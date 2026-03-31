from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Brahma Blog"
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/blog"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "super-secret-key"
    
    class Config:
        env_file = ".env"

settings = Settings()
