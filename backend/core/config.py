from typing import Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str

    # Cache / Queue
    REDIS_URL: str

    # LLM (OpenAI-compatible)
    LLM_API_KEY: str
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL_NAME: str = "gpt-4o"

    # Agent memory
    ZEP_API_KEY: str

    # Auth
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 60

    # Storage
    STORAGE_BACKEND: Literal["local", "s3"] = "local"
    STORAGE_PATH: str = "./uploads"
    AWS_BUCKET: Optional[str] = None
    AWS_REGION: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # Cost controls
    MAX_LLM_CALLS_PER_RUN: int = 10000
    MAX_AGENTS_STARTER: int = 1000
    MAX_AGENTS_PRO: int = 100000
    MAX_AGENTS_ENTERPRISE: int = 1000000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
