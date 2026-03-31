from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from src.core.models import Post, Author, Tag
from typing import List, Optional

class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_posts(self, page: int = 1, size: int = 10, tag: str = None, author_id: int = None) -> (List[Post], int):
        query = select(Post).order_by(Post.published_at.desc())
        if tag:
            query = query.join(Post.tags).filter(Tag.name == tag)
        if author_id:
            query = query.filter(Post.author_id == author_id)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Paginate
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def get_stats(self):
        posts_count = await self.db.execute(select(func.count(Post.id)))
        authors_count = await self.db.execute(select(func.count(Author.id)))
        views_count = await self.db.execute(select(func.sum(Post.views)))
        
        return {
            "total_posts": posts_count.scalar() or 0,
            "total_authors": authors_count.scalar() or 0,
            "total_views": views_count.scalar() or 0
        }

    async def get_by_slug(self, slug: str) -> Optional[Post]:
        result = await self.db.execute(select(Post).filter(Post.slug == slug))
        return result.scalar_one_or_none()

    async def get_related(self, post: Post, limit: int = 3) -> List[Post]:
        tag_ids = [t.id for t in post.tags]
        if not tag_ids:
            return []
        query = select(Post).join(Post.tags).filter(
            Tag.id.in_(tag_ids),
            Post.id != post.id
        ).distinct().limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def increment_views(self, post_id: int):
        await self.db.execute(
            Post.__table__.update().where(Post.id == post_id).values(views=Post.views + 1)
        )
        await self.db.commit()

    async def create(self, data: dict) -> Post:
        tag_ids = data.pop("tag_ids", [])
        post = Post(**data)
        if tag_ids:
            tags = await self.db.execute(select(Tag).filter(Tag.id.in_(tag_ids)))
            post.tags = tags.scalars().all()
        
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def update(self, post_id: int, data: dict) -> Optional[Post]:
        result = await self.db.execute(select(Post).filter(Post.id == post_id))
        post = result.scalar_one_or_none()
        if not post:
            return None
            
        tag_ids = data.pop("tag_ids", None)
        for key, value in data.items():
            if value is not None:
                setattr(post, key, value)
                
        if tag_ids is not None:
            tags = await self.db.execute(select(Tag).filter(Tag.id.in_(tag_ids)))
            post.tags = tags.scalars().all()
            
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def delete(self, post_id: int) -> bool:
        result = await self.db.execute(select(Post).filter(Post.id == post_id))
        post = result.scalar_one_or_none()
        if not post:
            return False
        await self.db.delete(post)
        await self.db.commit()
        return True

    async def get_by_id(self, post_id: int) -> Optional[Post]:
        result = await self.db.execute(select(Post).filter(Post.id == post_id))
        return result.scalar_one_or_none()

class AuthorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, author_id: int) -> Optional[Author]:
        result = await self.db.execute(select(Author).filter(Author.id == author_id))
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> Author:
        author = Author(**data)
        self.db.add(author)
        await self.db.commit()
        await self.db.refresh(author)
        return author

    async def update(self, author_id: int, data: dict) -> Optional[Author]:
        result = await self.db.execute(select(Author).filter(Author.id == author_id))
        author = result.scalar_one_or_none()
        if not author:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(author, key, value)
        await self.db.commit()
        await self.db.refresh(author)
        return author

    async def delete(self, author_id: int) -> bool:
        result = await self.db.execute(select(Author).filter(Author.id == author_id))
        author = result.scalar_one_or_none()
        if not author:
            return False
        await self.db.delete(author)
        await self.db.commit()
        return True

