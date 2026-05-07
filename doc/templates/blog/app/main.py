from fastapi import FastAPI
from src.core.database import engine, Base
# Import models to register them with Base.metadata
from src.core.models import Author, Post, Tag


def extend_app(app: FastAPI):
    pass

async def startup(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)