"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8889
    DEBUG: bool = True
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://10.40.1.65:5173",
        "http://10.40.1.65:5174",
        "http://10.40.1.65:5175",
        "http://10.40.1.65:5176",
        "http://10.40.1.65:5177",
        "https://microfrontends.alpha-grep.com",
    ]
    
    # Authentication
    ACCESS_VERIFY_TOKEN_URL: str = "http://localhost:3000/user/verifyToken"
    DEV_MODE: bool = False  # Set to True to bypass authentication for development
    DEV_USER_EMAIL: str = "dev@example.com"
    DEV_USER_ROLE: str = "ADMIN"
    
    # Data storage
    DATA_DIR: str = "data"
    TOOLS_FILE: str = "tools.json"
    
    # Database (password special characters need URL encoding: @ becomes %40)
    DATABASE_URL: str = "postgresql+asyncpg://one_rw:ONEAG%402025@10.40.1.56:5432/one_ag"
    
    # Confluence Integration (for document crawling)
    CONFLUENCE_EMAIL: str = ""  # Your Confluence email
    CONFLUENCE_API_TOKEN: str = ""  # Confluence API token
    
    class Config:
        env_file = ".env"


_settings = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


settings = get_settings()
