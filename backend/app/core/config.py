"""
ORIONIS Core Configuration
"""
import os
from pathlib import Path
from functools import lru_cache
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


class Settings:
    """ORIONIS Configuration Settings"""
    
    def __init__(self):
        # App
        self.APP_NAME = "ORIONIS"
        self.APP_VERSION = "3.0.0"
        self.DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
        self.ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
        
        # API
        self.API_V1_PREFIX = "/api/v1"
        
        # Security
        self.SECRET_KEY = os.environ.get("SECRET_KEY", "orionis-secret-key-change-in-production")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.REFRESH_TOKEN_EXPIRE_DAYS = 7
        
        # Database - PostgreSQL
        self.POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
        self.POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", "5432"))
        self.POSTGRES_USER = os.environ.get("POSTGRES_USER", "orionis")
        self.POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "orionis")
        self.POSTGRES_DB = os.environ.get("POSTGRES_DB", "orionis_db")
        
        # MongoDB (legacy support)
        self.MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
        self.MONGO_DB_NAME = os.environ.get("DB_NAME", "test_database")
        
        # Redis
        self.REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
        self.REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
        self.REDIS_DB = 0
        
        # AI Models
        self.EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
        self.DEFAULT_CHAT_MODEL = "gpt-4o"
        self.DEFAULT_FAST_MODEL = "gpt-4o-mini"
        self.DEFAULT_VISION_MODEL = "gpt-4o"
        self.DEFAULT_VOICE_MODEL = "whisper-1"
        self.DEFAULT_TTS_MODEL = "tts-1"
        self.DEFAULT_IMAGE_MODEL = "gpt-image-1"
        
        # Storage
        self.STORAGE_TYPE = "local"
        self.STORAGE_PATH = "/app/storage"
        self.S3_BUCKET = os.environ.get("S3_BUCKET")
        self.S3_REGION = os.environ.get("S3_REGION")
        self.S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
        self.S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")
        
        # CORS
        self.CORS_ORIGINS = ["*"]
        
        # Rate Limiting
        self.RATE_LIMIT_PER_MINUTE = 60
        
        # Celery
        self.CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
        self.CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def DATABASE_URL_SYNC(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
