from fastapi import Request
from src.core.database import AsyncSessionLocal
from src.repositories.blog import PostRepository
from src.services.blog import BlogService

async def index(request: Request, id: int):
    page = int(request.query_params.get("page", 1))
    
    async with AsyncSessionLocal() as db:
        repo = PostRepository(db)
        service = BlogService(repo)
        
        author = await service.get_author_profile(id)
        if not author:
            return {"error": "Author not found"}, 404
            
        posts, total = await service.list_posts(page=page, author_id=id)
        
        return {
            "author": author.dict(),
            "posts": [p.dict() for p in posts],
            "total": total,
            "page": page
        }
