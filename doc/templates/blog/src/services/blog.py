import json
import math
import re
from src.repositories.blog import PostRepository
from src.core.cache import redis_client
from src.schemas.blog import PostRead
from typing import Optional, List

class BlogService:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    async def get_post_detail(self, slug: str) -> Optional[PostRead]:
        # Try cache first
        cache_key = f"post:{slug}"
        cached = await redis_client.get(cache_key)
        if cached:
            return PostRead.model_validate_json(cached)
        
        # Fetch from DB
        post = await self.post_repo.get_by_slug(slug)
        if not post:
            return None
            
        post_data = PostRead.from_orm(post)
        
        # Calculate reading time (avg 200 words per minute)
        words = len(re.findall(r'\w+', post.content))
        post_data.reading_time = max(1, math.ceil(words / 200))
        
        # Get related posts
        related = await self.post_repo.get_related(post)
        post_data.related_posts = [PostRead.from_orm(r) for r in related]

        # Cache for 1 hour
        await redis_client.setex(cache_key, 3600, post_data.model_dump_json())
        return post_data

    async def list_posts(self, page: int = 1, size: int = 10, tag: str = None, author_id: int = None):
        posts, total = await self.post_repo.get_posts(page, size, tag, author_id)
        return [PostRead.from_orm(p) for p in posts], total

    async def create_post(self, data: 'PostCreate'):
        post = await self.post_repo.create(data.model_dump())
        return PostRead.from_orm(post)

    async def update_post(self, post_id: int, data: 'PostUpdate'):
        post = await self.post_repo.update(post_id, data.model_dump(exclude_unset=True))
        if post:
            # Clear cache
            await redis_client.delete(f"post:{post.slug}")
            return PostRead.from_orm(post)
        return None

    async def delete_post(self, post_id: int):
        post = await self.post_repo.get_by_id(post_id)
        if post:
            await redis_client.delete(f"post:{post.slug}")
        return await self.post_repo.delete(post_id)

    async def list_authors(self):
        from src.repositories.blog import AuthorRepository
        from src.core.models import Author
        author_repo = AuthorRepository(self.post_repo.db)
        from sqlalchemy import select
        result = await author_repo.db.execute(select(Author))
        authors = result.scalars().all()
        from src.schemas.blog import AuthorRead
        return [AuthorRead.from_orm(a) for a in authors]

    async def list_tags(self):
        from src.core.models import Tag
        from sqlalchemy import select
        result = await self.post_repo.db.execute(select(Tag))
        tags = result.scalars().all()
        from src.schemas.blog import TagRead
        return [TagRead.from_orm(t) for t in tags]

    async def get_author_profile(self, author_id: int):
        from src.repositories.blog import AuthorRepository
        author_repo = AuthorRepository(self.post_repo.db)
        author = await author_repo.get_by_id(author_id)
        if not author:
            return None
            
        from src.schemas.blog import AuthorRead
        return AuthorRead.from_orm(author)

    async def get_admin_stats(self):
        return await self.post_repo.get_stats()

    async def create_author(self, data: dict):
        from src.repositories.blog import AuthorRepository
        author_repo = AuthorRepository(self.post_repo.db)
        author = await author_repo.create(data)
        from src.schemas.blog import AuthorRead
        return AuthorRead.from_orm(author)

    async def update_author(self, author_id: int, data: dict):
        from src.repositories.blog import AuthorRepository
        author_repo = AuthorRepository(self.post_repo.db)
        author = await author_repo.update(author_id, data)
        if author:
            from src.schemas.blog import AuthorRead
            return AuthorRead.from_orm(author)
        return None

    async def delete_author(self, author_id: int):
        from src.repositories.blog import AuthorRepository
        author_repo = AuthorRepository(self.post_repo.db)
        return await author_repo.delete(author_id)

