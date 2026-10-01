import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse
from app.config import settings
from app.database import init_db, db_session, get_or_create_user, toggle_user_post_like, get_post_likers
from app.instagram_service import instagram_service
from app.webhook_handler import router as webhook_router, event_listeners, broadcast_event
from app.models import (
    CommentCreate, CommunityPostCreate, LikeResponse, 
    ProfileData, PostItem, CommunityPostItem, UserLogin, UserLikeRequest
)
try:
    from app.pdf_generator import generate_insta_theory_pdf
except ImportError:
    generate_insta_theory_pdf = None



FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

async def periodic_instagram_sync():
    """Background worker that continuously syncs additions & deletions from Instagram."""
    while True:
        try:
            await asyncio.sleep(15)  # Auto-check Instagram every 15 seconds for instant upload/delete sync
            if not settings.MOCK_MODE and settings.INSTAGRAM_ACCESS_TOKEN:
                posts = await instagram_service.sync_media_from_instagram()
                broadcast_event("sync_completed", {"posts_count": len(posts)})
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Periodic Auto-Sync] Notice: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database
    init_db()
    print("[Startup] SQLite Database ready (100% Free & Local).")
    
    # Generate the Theory Guide PDF on startup
    pdf_path = Path(__file__).resolve().parent.parent.parent / "InstaSync_Hub_Theory_Guide.pdf"
    if generate_insta_theory_pdf:
        try:
            generate_insta_theory_pdf(str(pdf_path))
            print(f"[Startup] PDF Guide generated: {pdf_path}")
        except Exception as e:
            print(f"[Startup] PDF Generation notice: {e}")

    sync_task = asyncio.create_task(periodic_instagram_sync())
    yield
    sync_task.cancel()
    print("[Shutdown] Cleaning up connections.")

app = FastAPI(
    title="Instagram Live Sync & Community Hub API",
    description="Universal 100% Free Backend for syncing Instagram Posts/Reels to any website in real-time.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware: Allows any company website domain to connect seamlessly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/widget") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Mount Local Media Directory (100% Free Local Media Storage)
app.mount("/media", StaticFiles(directory=str(settings.MEDIA_DIR)), name="media")

# Mount Frontend static files for widget distribution
if FRONTEND_DIR.exists():
    app.mount("/widget", StaticFiles(directory=str(FRONTEND_DIR)), name="widget")

# Include Webhook Router
app.include_router(webhook_router)

# ----------------- Core API Endpoints -----------------

@app.get("/api/health")
async def health_check():
    """Health status and configuration check."""
    return {
        "status": "healthy",
        "mock_mode": settings.MOCK_MODE,
        "database": "SQLite Local (Active)",
        "media_storage": "Local Disk (Active)",
        "cost": "₹0 (100% Free)"
    }

@app.get("/api/profile")
async def get_profile():
    """Returns Instagram account profile info."""
    profile = await instagram_service.sync_profile()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.get("/api/posts")
async def get_posts(filter: str = Query("ALL", pattern="^(ALL|POSTS|REELS)$")):
    """
    Returns cached posts and reels from local database.
    Filter: ALL, POSTS, REELS.
    """
    posts = instagram_service.get_cached_posts(filter_type=filter)
    return {
        "count": len(posts),
        "filter": filter,
        "posts": posts
    }

@app.get("/api/posts/{post_id}")
async def get_post_detail(post_id: int):
    """Returns single post with all its comments."""
    posts = instagram_service.get_cached_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.post("/api/posts/{post_id}/comments")
async def add_post_comment(post_id: int, payload: CommentCreate):
    """Adds a comment from the website visitor to the post."""
    result = await instagram_service.add_post_comment(
        post_id=post_id,
        username=payload.username or "Website Visitor",
        text=payload.text
    )
    broadcast_event("new_comment", {"post_id": post_id, "comment": result})
    return {"success": True, "comment": result}

@app.post("/api/comments/{comment_id}/reply")
async def reply_to_instagram_comment(comment_id: str, payload: CommentCreate):
    """Replies directly to an Instagram comment via Meta Graph API."""
    result = await instagram_service.reply_to_comment(
        comment_id=comment_id,
        message=payload.text
    )
    broadcast_event("comment_replied", {"comment_id": comment_id, "reply": result})
    return result

@app.post("/api/auth/login")
async def login_user(payload: UserLogin):
    """Logs in or registers a website visitor."""
    user = get_or_create_user(payload.username, payload.full_name, payload.avatar_url)
    return {"success": True, "user": user}

@app.post("/api/posts/{post_id}/user-like")
async def user_like_post(post_id: int, payload: UserLikeRequest):
    """Likes or unlikes a post on behalf of a specific logged-in user."""
    result = toggle_user_post_like(post_id, payload.username, payload.user_avatar)
    broadcast_event("post_liked", {"post_id": post_id, "data": result})
    return result

@app.post("/api/posts/{post_id}/like")
async def toggle_post_like(post_id: int):
    """Likes/unlikes an Instagram post on the website."""
    result = await instagram_service.toggle_post_like(post_id=post_id)
    broadcast_event("post_liked", {"post_id": post_id, "new_count": result.get("new_like_count")})
    return result

@app.post("/api/comments/{comment_id}/like")
async def toggle_comment_like(comment_id: str):
    """Likes a comment on the website."""
    return await instagram_service.toggle_comment_like(comment_id=comment_id)

# ----------------- Separate Website Community Feed -----------------

@app.get("/api/community/posts")
async def get_community_posts():
    """Returns website's own separate community feed posts."""
    with db_session() as conn:
        rows = conn.execute("SELECT * FROM community_posts ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

@app.post("/api/community/posts")
async def create_community_post(payload: CommunityPostCreate):
    """Creates a post directly on the website's separate community feed."""
    avatar = f"https://api.dicebear.com/7.x/bottts/svg?seed={payload.author_name}"
    with db_session() as conn:
        cursor = conn.execute("""
        INSERT INTO community_posts (author_name, author_avatar, content, media_url, likes_count, comments_count)
        VALUES (?, ?, ?, ?, 0, 0)
        """, (payload.author_name, avatar, payload.content, payload.media_url))
        new_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM community_posts WHERE id = ?", (new_id,)).fetchone()
        post_dict = dict(row)
        broadcast_event("new_community_post", post_dict)
        return post_dict

@app.post("/api/community/posts/{post_id}/like")
async def like_community_post(post_id: int):
    """Likes a post on the website community feed."""
    with db_session() as conn:
        conn.execute("UPDATE community_posts SET likes_count = likes_count + 1 WHERE id = ?", (post_id,))
        row = conn.execute("SELECT likes_count FROM community_posts WHERE id = ?", (post_id,)).fetchone()
        new_likes = row["likes_count"] if row else 0
        broadcast_event("community_post_liked", {"id": post_id, "likes_count": new_likes})
        return {"success": True, "likes_count": new_likes}

# ----------------- Real-Time Live Sync & SSE Stream -----------------

@app.post("/api/sync/trigger")
async def trigger_manual_sync():
    """Forces an immediate sync with Instagram Graph API."""
    posts = await instagram_service.sync_media_from_instagram()
    profile = await instagram_service.sync_profile()
    broadcast_event("sync_completed", {"posts_count": len(posts)})
    return {"success": True, "synced_posts": len(posts), "profile": profile}

@app.post("/api/simulate/new-post")
async def simulate_instant_post():
    """
    Simulates a live Instagram post or reel upload.
    Allows instant demonstration of real-time sync without waiting for Instagram.
    """
    new_post = await instagram_service.simulate_new_instagram_post()
    broadcast_event("new_post", new_post)
    return {"success": True, "message": "Simulated Instagram post broadcasted!", "post": new_post}

@app.get("/api/stream")
async def stream_live_events(request: Request):
    """
    Server-Sent Events (SSE) Stream.
    Pushes instant real-time updates to browser when Instagram post is uploaded.
    100% Free, zero WebSocket server or paid push notification service required!
    """
    queue = asyncio.Queue()
    event_listeners.append(queue)

    async def event_generator():
        try:
            # Send initial connected ping
            yield "data: {\"event\": \"connected\", \"message\": \"Live Instagram sync listener active\"}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=20.0)
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    # Keep-alive heartbeat ping every 20 seconds
                    yield "data: {\"event\": \"ping\"}\n\n"
        finally:
            if queue in event_listeners:
                event_listeners.remove(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# ----------------- Frontend Demo Route -----------------

@app.get("/")
async def serve_demo():
    """Serves the interactive demo & integration test suite."""
    demo_file = FRONTEND_DIR / "index.html"
    if demo_file.exists():
        return FileResponse(
            demo_file,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return {"message": "Instagram Live Sync Hub Backend is running!"}

@app.get("/manual")
async def serve_project_manual():
    """Serves the complete printable project manual and documentation."""
    manual_file = Path(__file__).resolve().parent.parent.parent / "PROJECT_MANUAL.html"
    if manual_file.exists():
        return FileResponse(manual_file)
    raise HTTPException(status_code=404, detail="Manual not found")

@app.get("/theory")
async def serve_theory_manual():
    """Serves the comprehensive Theory & Concept Manual."""
    theory_file = Path(__file__).resolve().parent.parent.parent / "THEORY_MANUAL.html"
    if theory_file.exists():
        return FileResponse(theory_file)
    raise HTTPException(status_code=404, detail="Theory manual not found")

@app.get("/download-pdf")
async def download_theory_pdf():
    """Directly downloads the generated InstaSync Hub Theory Guide PDF."""
    pdf_path = Path(__file__).resolve().parent.parent.parent / "InstaSync_Hub_Theory_Guide.pdf"
    if not pdf_path.exists():
        generate_insta_theory_pdf(str(pdf_path))
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="InstaSync_Hub_Theory_Guide.pdf",
        headers={"Content-Disposition": "attachment; filename=InstaSync_Hub_Theory_Guide.pdf"}
    )



