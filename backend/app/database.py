import sqlite3
from datetime import datetime
from contextlib import contextmanager
from app.config import settings

def get_db():
    conn = sqlite3.connect(str(settings.DB_PATH), timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def db_session():
    conn = sqlite3.connect(str(settings.DB_PATH), timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initializes SQLite database schema (100% Free & Local)."""
    with db_session() as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
        cursor = conn.cursor()
        
        # 1. Instagram Profile Cache
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS instagram_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            username TEXT NOT NULL,
            name TEXT,
            biography TEXT,
            profile_picture_url TEXT,
            followers_count INTEGER DEFAULT 0,
            follows_count INTEGER DEFAULT 0,
            media_count INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 2. Instagram Posts & Reels Cache
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS instagram_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ig_media_id TEXT UNIQUE NOT NULL,
            media_type TEXT NOT NULL, /* IMAGE, VIDEO, REEL, CAROUSEL_ALBUM */
            media_url TEXT NOT NULL,
            local_media_path TEXT,
            thumbnail_url TEXT,
            caption TEXT,
            permalink TEXT,
            timestamp TEXT,
            like_count INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            website_likes_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 3. Instagram Comments Cache
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS instagram_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ig_comment_id TEXT UNIQUE NOT NULL,
            post_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp TEXT,
            like_count INTEGER DEFAULT 0,
            is_reply BOOLEAN DEFAULT 0,
            parent_comment_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(post_id) REFERENCES instagram_posts(id) ON DELETE CASCADE
        );
        """)
        
        # 4. Website Separate Community Feed Posts
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS community_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_name TEXT NOT NULL,
            author_avatar TEXT,
            content TEXT NOT NULL,
            media_url TEXT,
            likes_count INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 5. Community Comments
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS community_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            community_post_id INTEGER NOT NULL,
            author_name TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(community_post_id) REFERENCES community_posts(id) ON DELETE CASCADE
        );
        """)

        # 6. Registered Website Users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            avatar_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 7. Post Likes by Specific Users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            user_avatar TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(post_id, username)
        );
        """)

        # 8. Comment Likes by Specific Users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS comment_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comment_id TEXT NOT NULL,
            username TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(comment_id, username)
        );
        """)
        
        # Check if initial data needs seeding
        cursor.execute("SELECT COUNT(*) as count FROM instagram_profile")
        if cursor.fetchone()["count"] == 0:
            seed_initial_data(cursor)

def seed_initial_data(cursor):
    """Seed initial realistic demo data so the app looks stunning immediately."""
    cursor.execute("""
    INSERT INTO instagram_profile (id, username, name, biography, profile_picture_url, followers_count, follows_count, media_count)
    VALUES (
        1,
        'yourbrand.official',
        'Your Brand Official',
        'Official Digital Brand Hub ✨ Innovations, Behind the Scenes, and Community Stories. Connect with us daily!',
        'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=200&auto=format&fit=crop&q=80',
        124800,
        342,
        86
    );
    """)
    
    # Seed sample Instagram Posts & Reels
    sample_posts = [
        (
            'ig_post_101',
            'REEL',
            'https://assets.mixkit.co/videos/preview/mixkit-futuristic-robotic-arm-working-in-a-laboratory-41584-large.mp4',
            None,
            'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&auto=format&fit=crop&q=80',
            '🚀 Redefining the next era of automation. Here is a sneak peek into our lab innovation sprint! What feature do you want next? #TechInnovation #AI #Automation #Future',
            'https://instagram.com/p/sample1',
            datetime.now().isoformat(),
            4520,
            128,
            34
        ),
        (
            'ig_post_102',
            'IMAGE',
            'https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=800&auto=format&fit=crop&q=80',
            None,
            'https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=800&auto=format&fit=crop&q=80',
            'Big milestone today! Grateful to every creator, developer, and team member driving this mission forward. Together we grow 🌱✨ #Milestone #Community #WorkCulture',
            'https://instagram.com/p/sample2',
            datetime.now().isoformat(),
            3210,
            64,
            19
        ),
        (
            'ig_post_103',
            'REEL',
            'https://assets.mixkit.co/videos/preview/mixkit-hands-typing-on-a-laptop-keyboard-in-a-dark-room-43224-large.mp4',
            None,
            'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=80',
            '3 clean coding tips every developer needs in 2026! 💡 Save this reel for your next sprint review. #WebDev #CodingTips #Developers #TechTricks',
            'https://instagram.com/p/sample3',
            datetime.now().isoformat(),
            8940,
            312,
            91
        ),
        (
            'ig_post_104',
            'IMAGE',
            'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=800&auto=format&fit=crop&q=80',
            None,
            'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=800&auto=format&fit=crop&q=80',
            'Designing with speed and precision. Here is how our UI design system handles multi-platform responsiveness. Drop a 💜 if you love dark-mode UI! #DesignSystem #UIUX',
            'https://instagram.com/p/sample4',
            datetime.now().isoformat(),
            2890,
            45,
            12
        )
    ]
    
    for post in sample_posts:
        cursor.execute("""
        INSERT INTO instagram_posts (ig_media_id, media_type, media_url, local_media_path, thumbnail_url, caption, permalink, timestamp, like_count, comments_count, website_likes_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, post)
        
    # Sample comments for post 1
    sample_comments = [
        ('ig_comm_1', 1, 'arjun_coder', 'Insane tech! Is the API open-source or hosted on private cloud?', '2 hours ago', 14, 0, None),
        ('ig_comm_2', 1, 'priya.design', 'The UI transition looks super smooth! Great work team ❤️', '1 hour ago', 8, 0, None),
        ('ig_comm_3', 1, 'vikram_dev', 'Awesome! Can we integrate this directly into existing websites?', '30 mins ago', 22, 0, None),
    ]
    for c in sample_comments:
        cursor.execute("""
        INSERT INTO instagram_comments (ig_comment_id, post_id, username, text, timestamp, like_count, is_reply, parent_comment_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, c)
        
    # Sample Community Feed posts (Separate website social feed)
    sample_community = [
        ('Rohit Sharma', 'https://api.dicebear.com/7.x/bottts/svg?seed=Rohit', 'Just deployed our new website feature using FastAPI! The speed is incredible 🔥', None, 15, 2),
        ('Ayesha Khan', 'https://api.dicebear.com/7.x/bottts/svg?seed=Ayesha', 'Welcome everyone to our new community feed! Share your feedback, ideas, and questions right here.', 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=600&auto=format&fit=crop&q=80', 28, 5)
    ]
    for cp in sample_community:
        cursor.execute("""
        INSERT INTO community_posts (author_name, author_avatar, content, media_url, likes_count, comments_count)
        VALUES (?, ?, ?, ?, ?, ?)
        """, cp)

def get_or_create_user(username: str, full_name: str, avatar_url: str = None) -> dict:
    """Creates or updates a registered visitor profile."""
    cleaned_user = username.strip().lstrip("@").lower()
    if not avatar_url:
        avatar_url = f"https://api.dicebear.com/7.x/bottts/svg?seed={cleaned_user}"
    with db_session() as conn:
        conn.execute("""
        INSERT INTO users (username, full_name, avatar_url)
        VALUES (?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            full_name=excluded.full_name,
            avatar_url=COALESCE(excluded.avatar_url, users.avatar_url)
        """, (cleaned_user, full_name, avatar_url))
        row = conn.execute("SELECT * FROM users WHERE username = ?", (cleaned_user,)).fetchone()
        return dict(row)

def toggle_user_post_like(post_id: int, username: str, user_avatar: str = None) -> dict:
    """Tracks likes per user and returns updated likers."""
    cleaned_user = username.strip().lstrip("@").lower()
    with db_session() as conn:
        existing = conn.execute("SELECT * FROM post_likes WHERE post_id = ? AND username = ?", (post_id, cleaned_user)).fetchone()
        if existing:
            conn.execute("DELETE FROM post_likes WHERE post_id = ? AND username = ?", (post_id, cleaned_user))
            action = "unliked"
        else:
            conn.execute("""
            INSERT INTO post_likes (post_id, username, user_avatar)
            VALUES (?, ?, ?)
            """, (post_id, cleaned_user, user_avatar))
            action = "liked"
        
        user_likes_cnt = conn.execute("SELECT COUNT(*) as cnt FROM post_likes WHERE post_id = ?", (post_id,)).fetchone()["cnt"]
        conn.execute("UPDATE instagram_posts SET website_likes_count = ? WHERE id = ?", (user_likes_cnt, post_id))
        
        likers_rows = conn.execute("SELECT username, user_avatar FROM post_likes WHERE post_id = ? ORDER BY id DESC LIMIT 5", (post_id,)).fetchall()
        likers = [dict(r) for r in likers_rows]
        
        post_row = conn.execute("SELECT like_count, website_likes_count FROM instagram_posts WHERE id = ?", (post_id,)).fetchone()
        total_likes = (post_row["like_count"] or 0) + (post_row["website_likes_count"] or 0) if post_row else user_likes_cnt
        
        return {
            "success": True,
            "action": action,
            "user_liked": action == "liked",
            "total_likes": total_likes,
            "likers": likers
        }

def get_post_likers(post_id: int) -> list:
    """Returns all users who liked a post."""
    with db_session() as conn:
        rows = conn.execute("SELECT username, user_avatar FROM post_likes WHERE post_id = ? ORDER BY id DESC LIMIT 10", (post_id,)).fetchall()
        return [dict(r) for r in rows]
