from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Emotional Voice Chat"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    DATABASE_URL: str
    REDIS_URL: str
    
    OPENAI_API_KEY: str = "mock"
    INDEXTTS_BASE_URL: str = "http://mock-indextts"
    
    # Security & Compliance
    DAILY_VOICE_LIMIT: int = 50
    MAX_AUDIO_DURATION_SEC: int = 60

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
