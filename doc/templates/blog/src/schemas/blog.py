from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class TagBase(BaseModel):
    name: str

class TagRead(TagBase):
    id: int
    class Config:
        from_attributes = True

class AuthorBase(BaseModel):
    name: str
    bio: Optional[str] = None
    avatar: Optional[str] = None

class AuthorRead(AuthorBase):
    id: int
    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str
    slug: str
    content: str
    excerpt: Optional[str] = None

class PostCreate(PostBase):
    author_id: int
    tag_ids: List[int] = []

class PostUpdate(PostBase):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    author_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None

class PostRead(PostBase):
    id: int
    published_at: datetime
    views: int
    author: AuthorRead
    tags: List[TagRead]
    reading_time: Optional[int] = 0
    related_posts: Optional[List['PostRead']] = []
    
    class Config:
        from_attributes = True

class PostListResponse(BaseModel):
    items: List[PostRead]
    total: int
    page: int
    size: int

PostRead.model_rebuild()

