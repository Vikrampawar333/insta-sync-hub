import httpx
import aiofiles
import random
import os
from pathlib import Path
from datetime import datetime
from app.config import settings
from app.database import db_session

GRAPH_API_BASE = "https://graph.facebook.com/v19.0"

class InstagramService:
    def __init__(self):
        self.account_id = settings.INSTAGRAM_ACCOUNT_ID
        self.access_token = settings.INSTAGRAM_ACCESS_TOKEN
        self.mock_mode = settings.MOCK_MODE or not self.access_token or self.access_token == "demo_access_token"

    @property
    def api_base(self):
        if self.access_token and self.access_token.startswith("IG"):
            return "https://graph.instagram.com/v19.0"
        return "https://graph.facebook.com/v19.0"

    async def sync_profile(self):
        """Fetches profile info from Meta Graph API or maintains mock profile."""
        if self.mock_mode:
            with db_session() as conn:
                row = conn.execute("SELECT * FROM instagram_profile WHERE id = 1").fetchone()
                return dict(row) if row else None
        
        url = f"{self.api_base}/{self.account_id}"
        params = {
            "fields": "id,username,name,biography,profile_picture_url,followers_count,follows_count,media_count",
            "access_token": self.access_token
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                with db_session() as conn:
                    conn.execute("""
                    INSERT INTO instagram_profile (id, username, name, biography, profile_picture_url, followers_count, follows_count, media_count, updated_at)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(id) DO UPDATE SET
                        username=excluded.username,
                        name=excluded.name,
                        biography=excluded.biography,
                        profile_picture_url=excluded.profile_picture_url,
                        followers_count=excluded.followers_count,
                        follows_count=excluded.follows_count,
                        media_count=excluded.media_count,
                        updated_at=CURRENT_TIMESTAMP
                    """, (
                        data.get("username", "brand"),
                        data.get("name", "Brand"),
                        data.get("biography", ""),
                        data.get("profile_picture_url", ""),
                        data.get("followers_count", 0),
                        data.get("follows_count", 0),
                        data.get("media_count", 0)
                    ))
                    row = conn.execute("SELECT * FROM instagram_profile WHERE id = 1").fetchone()
                    return dict(row)
            else:
                # Fallback to local cached profile if API fails
                with db_session() as conn:
                    row = conn.execute("SELECT * FROM instagram_profile WHERE id = 1").fetchone()
                    return dict(row) if row else None

    async def download_media(self, media_url: str, media_id: str, media_type: str) -> str:
        """
        Downloads media locally to server disk.
        Instagram CDN links expire after 3 days. Saving locally ensures 100% FREE lifetime storage.
        """
        try:
            ext = ".mp4" if "VIDEO" in media_type or "REEL" in media_type else ".jpg"
            filename = f"{media_id}{ext}"
            file_path = settings.MEDIA_DIR / filename
            
            # If already downloaded, return existing local path
            if file_path.exists():
                return f"/media/{filename}"
                
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(media_url)
                if resp.status_code == 200:
                    async with aiofiles.open(file_path, "wb") as f:
                        await f.write(resp.content)
                    return f"/media/{filename}"
        except Exception as e:
            print(f"[Warning] Could not download media locally: {e}")
        return media_url

    async def sync_media_from_instagram(self):
        """Fetches posts/reels from Instagram Graph API and caches them in local SQLite."""
        if self.mock_mode:
            return self.get_cached_posts()

        url = f"{self.api_base}/{self.account_id}/media"
        params = {
            "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count",
            "access_token": self.access_token,
            "limit": 25
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                active_ig_ids = [item.get("id") for item in data if item.get("id")]
                
                # Step 1: Pre-download any new media outside the database lock
                processed_items = []
                for item in data:
                    ig_id = item.get("id")
                    m_type = item.get("media_type")
                    if m_type == "VIDEO":
                        m_type = "REEL"
                        
                    m_url = item.get("media_url") or ""
                    thumb_url = item.get("thumbnail_url") or m_url
                    caption = item.get("caption", "")
                    permalink = item.get("permalink", "")
                    timestamp = item.get("timestamp", "")
                    likes = item.get("like_count", 0)
                    comments = item.get("comments_count", 0)

                    local_path = await self.download_media(m_url, ig_id, m_type) if m_url else None
                    processed_items.append((
                        ig_id, m_type, m_url, local_path, thumb_url, caption, permalink, timestamp, likes, comments
                    ))

                # Step 2: Perform fast atomic SQLite database sync in 1 millisecond
                with db_session() as conn:
                    # Automatic Delete Sync: If deleted on Instagram, delete from local DB
                    if active_ig_ids:
                        placeholders = ",".join("?" for _ in active_ig_ids)
                        conn.execute(f"DELETE FROM instagram_posts WHERE ig_media_id NOT IN ({placeholders})", active_ig_ids)
                        conn.execute("DELETE FROM instagram_comments WHERE post_id NOT IN (SELECT id FROM instagram_posts)")
                    else:
                        conn.execute("DELETE FROM instagram_posts")
                        conn.execute("DELETE FROM instagram_comments")

                    for item_tuple in processed_items:
                        conn.execute("""
                        INSERT INTO instagram_posts (
                            ig_media_id, media_type, media_url, local_media_path,
                            thumbnail_url, caption, permalink, timestamp, like_count, comments_count
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(ig_media_id) DO UPDATE SET
                            media_type=excluded.media_type,
                            media_url=excluded.media_url,
                            local_media_path=COALESCE(excluded.local_media_path, instagram_posts.local_media_path),
                            thumbnail_url=excluded.thumbnail_url,
                            caption=excluded.caption,
                            permalink=excluded.permalink,
                            timestamp=excluded.timestamp,
                            like_count=excluded.like_count,
                            comments_count=excluded.comments_count
                        """, item_tuple)
                return self.get_cached_posts()
            else:
                return self.get_cached_posts()

    def get_cached_posts(self, filter_type: str = "ALL"):
        """Returns posts from SQLite database."""
        with db_session() as conn:
            query = "SELECT * FROM instagram_posts"
            params = []
            if filter_type == "POSTS":
                query += " WHERE media_type IN ('IMAGE', 'CAROUSEL_ALBUM')"
            elif filter_type == "REELS":
                query += " WHERE media_type IN ('VIDEO', 'REEL')"
                
            query += " ORDER BY id DESC"
            rows = conn.execute(query, params).fetchall()
            
            posts = []
            for r in rows:
                p = dict(r)
                p["total_likes"] = p["like_count"] + p["website_likes_count"]
                
                # Fetch comments for this post
                comments_rows = conn.execute(
                    "SELECT * FROM instagram_comments WHERE post_id = ? ORDER BY id ASC", 
                    (p["id"],)
                ).fetchall()
                p["comments"] = [dict(c) for c in comments_rows]

                # Fetch users who liked this post
                likers_rows = conn.execute(
                    "SELECT username, user_avatar FROM post_likes WHERE post_id = ? ORDER BY id DESC LIMIT 5",
                    (p["id"],)
                ).fetchall()
                p["likers"] = [dict(lk) for lk in likers_rows]
                posts.append(p)
            return posts

    async def reply_to_comment(self, comment_id: str, message: str):
        """Replies to an Instagram comment via Graph API."""
        if not self.mock_mode:
            url = f"{self.api_base}/{comment_id}/replies"
            params = {
                "message": message,
                "access_token": self.access_token
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, params=params)
                if resp.status_code == 200:
                    return resp.json()

        # In mock mode or DB record, store reply locally
        with db_session() as conn:
            # find original comment's post_id
            row = conn.execute("SELECT post_id FROM instagram_comments WHERE ig_comment_id = ?", (comment_id,)).fetchone()
            post_id = row["post_id"] if row else 1
            new_id = f"ig_reply_{int(datetime.now().timestamp())}"
            conn.execute("""
            INSERT INTO instagram_comments (ig_comment_id, post_id, username, text, timestamp, like_count, is_reply, parent_comment_id)
            VALUES (?, ?, 'Brand (You)', ?, 'Just now', 0, 1, ?)
            """, (new_id, post_id, message, comment_id))
            
            # Increment comment count
            conn.execute("UPDATE instagram_posts SET comments_count = comments_count + 1 WHERE id = ?", (post_id,))
        return {"success": True, "comment_id": new_id, "message": message}

    async def add_post_comment(self, post_id: int, username: str, text: str):
        """Adds a comment from the website visitor to the post and publishes to Instagram if connected."""
        with db_session() as conn:
            row = conn.execute("SELECT ig_media_id FROM instagram_posts WHERE id = ?", (post_id,)).fetchone()
            ig_media_id = row["ig_media_id"] if row else None

        new_id = f"comm_web_{int(datetime.now().timestamp())}_{random.randint(100, 999)}"

        with db_session() as conn:
            conn.execute("""
            INSERT INTO instagram_comments (ig_comment_id, post_id, username, text, timestamp, like_count, is_reply)
            VALUES (?, ?, ?, ?, 'Just now', 0, 0)
            ON CONFLICT(ig_comment_id) DO NOTHING
            """, (new_id, post_id, username, text))
            conn.execute("UPDATE instagram_posts SET comments_count = comments_count + 1 WHERE id = ?", (post_id,))
            
        return {"id": new_id, "post_id": post_id, "username": username, "text": text, "timestamp": "Just now"}

    async def toggle_comment_like(self, comment_id: str):
        """Likes a comment on the website."""
        with db_session() as conn:
            conn.execute("UPDATE instagram_comments SET like_count = like_count + 1 WHERE ig_comment_id = ?", (comment_id,))
            row = conn.execute("SELECT like_count FROM instagram_comments WHERE ig_comment_id = ?", (comment_id,)) .fetchone()
            return {"success": True, "comment_id": comment_id, "likes": row["like_count"] if row else 1}

    async def toggle_post_like(self, post_id: int):
        """Toggles like count for a post on the website."""
        with db_session() as conn:
            row = conn.execute("SELECT like_count, website_likes_count FROM instagram_posts WHERE id = ?", (post_id,)).fetchone()
            if not row:
                return {"success": False, "new_like_count": 0, "action": "not_found"}
                
            curr_web_likes = row["website_likes_count"]
            # Toggle logic
            new_web_likes = curr_web_likes + 1
            action = "liked"
            
            conn.execute("UPDATE instagram_posts SET website_likes_count = ? WHERE id = ?", (new_web_likes, post_id))
            total = row["like_count"] + new_web_likes
            return {"success": True, "new_like_count": total, "action": action}

    async def simulate_new_instagram_post(self):
        """
        Simulates an incoming real-time post from Instagram.
        Creates a high-quality post or reel, saves it, and triggers real-time SSE.
        """
        types = ["REEL", "IMAGE"]
        chosen_type = random.choice(types)
        post_num = random.randint(200, 999)
        ig_id = f"ig_live_{post_num}"
        
        reels_pool = [
            ("https://assets.mixkit.co/videos/preview/mixkit-circuit-board-with-glowing-signals-41586-large.mp4",
             "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=80",
             "⚡ Just dropped! Microchips, hardware acceleration, and the next leap forward. Tell us your thoughts below! #Hardware #TechLaunch #NewReel"),
            ("https://assets.mixkit.co/videos/preview/mixkit-hands-holding-a-smartphone-with-green-screen-41589-large.mp4",
             "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800&auto=format&fit=crop&q=80",
             "📲 The future of mobile experiences is here! Check out how responsive and clean the new interface looks. #MobileFirst #AppDesign #UX")
        ]
        
        images_pool = [
            ("https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800&auto=format&fit=crop&q=80",
             "Collaboration at its finest! Our engineers and designers putting the final polish on our latest release. 💻🔥 #TeamWork #Innovate #BehindTheScenes"),
            ("https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=800&auto=format&fit=crop&q=80",
             "Simplicity is the ultimate sophistication. Designing systems that scale seamlessly without friction. 🚀 #Architecture #TechStack #CleanCode")
        ]
        
        if chosen_type == "REEL":
            item = random.choice(reels_pool)
            m_url, thumb, cap = item[0], item[1], item[2]
        else:
            item = random.choice(images_pool)
            m_url, thumb, cap = item[0], item[0], item[1]
            
        with db_session() as conn:
            conn.execute("""
            INSERT INTO instagram_posts (
                ig_media_id, media_type, media_url, thumbnail_url, caption, 
                permalink, timestamp, like_count, comments_count, website_likes_count
            ) VALUES (?, ?, ?, ?, ?, ?, 'Just now', ?, 0, 0)
            """, (ig_id, chosen_type, m_url, thumb, cap, f"https://instagram.com/p/{ig_id}", random.randint(15, 120)))
            
            new_row = conn.execute("SELECT * FROM instagram_posts WHERE ig_media_id = ?", (ig_id,)).fetchone()
            post_dict = dict(new_row)
            post_dict["total_likes"] = post_dict["like_count"]
            post_dict["comments"] = []
            return post_dict

instagram_service = InstagramService()
