import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Framework Required
    NAME: str = "app"
    VERSION: str = "1.0"
    PACKAGE_MANAGER: str = "npm"
    DEBUG: bool = True
    PORT: str = "8000"
    HOST: str = "0.0.0.0"
    PYTHONDONTWRITEBYTECODE: str = ""
    CWD: str = os.path.dirname(os.path.abspath(__file__))
    TYPESCRIPT:bool = False
    TAILWIND:bool = True
    STATIC_SITE:bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:example@localhost:5432/blog"
    
    # Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "super-secret-key"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Export framework required constants
NAME = settings.NAME
VERSION = settings.VERSION
PACKAGE_MANAGER = settings.PACKAGE_MANAGER
DEBUG = settings.DEBUG
PORT = settings.PORT
HOST = settings.HOST
PYTHONDONTWRITEBYTECODE = settings.PYTHONDONTWRITEBYTECODE
CWD = settings.CWD
TYPESCRIPT=settings.TYPESCRIPT
TAILWIND=settings.TAILWIND
STATIC_SITE=settings.STATIC_SITE

