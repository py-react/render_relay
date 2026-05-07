import asyncio
from src.core.database import AsyncSessionLocal, engine
from src.core.models import Base, Author, Post, Tag

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Create Author
        me = Author(
            name="Arjuna", 
            bio="Lead Architect. Focusing on high-voltage system design using RenderRelay.",
            avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=Arjuna"
        )
        db.add(me)
        
        # Create Tags
        tags = [Tag(name=n) for n in ["Backend", "React", "Architecture", "Networking"]]
        db.add_all(tags)
        
        # Create Posts
        p1 = Post(
            title="The Architect's Guide to RenderRelay",
            slug="architects-guide-to-render_relay",
            content="<p>RenderRelay represents the shift from <b>monolithic complexity</b> to <b>modular elegance</b>...</p>",
            excerpt="A deep dive into the core philosophy and technical decisions behind the RenderRelay system.",
            author=me,
            tags=[tags[0], tags[2]]
        )
        db.add(p1)
        
        await db.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed())

