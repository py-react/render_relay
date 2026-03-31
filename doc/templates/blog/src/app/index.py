from render_relay import Request
from src.core.database import AsyncSessionLocal
from src.repositories.blog import PostRepository
from src.services.blog import BlogService
from src.schemas.blog import PostListResponse

async def index(request: Request):
    page = int(request.query_params.get("page", 1))
    tag = request.query_params.get("tag")

    async with AsyncSessionLocal() as db:
        repo = PostRepository(db)
        service = BlogService(repo)
        posts, total = await service.list_posts(page=page, tag=tag)
        
        return {
            "posts": [p.dict() for p in posts],
            "total": total,
            "page": page,
            "tag": tag
        }

