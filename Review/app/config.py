from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    DATABASE_PATH: str = "./movies.db"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 часа
    
    # OMDb API
    OMDB_API_KEY: str
    OMDB_API_URL: str = "http://www.omdbapi.com/"
    OMDB_TIMEOUT: int = 10
    OMDB_RETRIES: int = 3
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Admin (optional)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = None
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()