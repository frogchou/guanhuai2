import os
import logging
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine absolute path to .env file in project root
# Path: backend/app/core/config.py -> ... -> project_root/.env
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
env_path = os.path.join(project_root, ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Emotional Voice Chat"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    DATABASE_URL: str
    REDIS_URL: str
    
    OPENAI_API_KEY: str = "mock"
    INDEXTTS_BASE_URL: str = "http://192.168.2.252:8000"
    
    # Security & Compliance
    DAILY_VOICE_LIMIT: int = 50
    MAX_AUDIO_DURATION_SEC: int = 60

    model_config = SettingsConfigDict(
        env_file=[".env", env_path], 
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

# Logging check
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("config")

if os.path.exists(env_path):
    logger.info(f"✅ Loaded .env file from: {env_path}")
elif os.path.exists(".env"):
    logger.info("✅ Loaded .env file from current directory")
else:
    logger.warning(f"⚠️  WARNING: .env file NOT found at {env_path} or current directory. Using defaults/env vars.")

