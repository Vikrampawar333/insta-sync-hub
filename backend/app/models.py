from pydantic import BaseModel, Field
from typing import Optional, List

class CommentItem(BaseModel):
    id: int
    ig_comment_id: str
    post_id: int
    username: str
    text: str
    timestamp: Optional[str] = None
    like_count: int = 0
    is_reply: bool = False
    parent_comment_id: Optional[str] = None

class CommentCreate(BaseModel):
    text: str
    username: Optional[str] = "Website Visitor"
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    full_name: str
    avatar_url: Optional[str] = None

class UserLikeRequest(BaseModel):
    username: str
    user_avatar: Optional[str] = None

class PostItem(BaseModel):
    id: int
    ig_media_id: str
    media_type: str # IMAGE, VIDEO, REEL, CAROUSEL_ALBUM
    media_url: str
    local_media_path: Optional[str] = None
    thumbnail_url: Optional[str] = None
    caption: Optional[str] = None
    permalink: Optional[str] = None
    timestamp: Optional[str] = None
    like_count: int = 0
    comments_count: int = 0
    website_likes_count: int = 0
    total_likes: int = 0
    comments: Optional[List[CommentItem]] = []

class ProfileData(BaseModel):
    id: int = 1
    username: str
    name: Optional[str] = None
    biography: Optional[str] = None
    profile_picture_url: Optional[str] = None
    followers_count: int = 0
    follows_count: int = 0
    media_count: int = 0

class CommunityCommentItem(BaseModel):
    id: int
    community_post_id: int
    author_name: str
    content: str
    created_at: str

class CommunityPostItem(BaseModel):
    id: int
    author_name: str
    author_avatar: Optional[str] = None
    content: str
    media_url: Optional[str] = None
    likes_count: int = 0
    comments_count: int = 0
    created_at: str

class CommunityPostCreate(BaseModel):
    author_name: str
    content: str
    media_url: Optional[str] = None

class LikeResponse(BaseModel):
    success: bool
    new_like_count: int
    action: str # "liked" or "unliked"
