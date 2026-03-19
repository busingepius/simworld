import pytest
import os
from pydantic import ValidationError
from core.config import Settings

def test_settings_missing_required_vars(monkeypatch):
    # Clear out any environment variables that might be set
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    
    with pytest.raises(ValidationError):
        Settings(_env_file=None)

def test_settings_valid(monkeypatch):
    # Set required environment variables
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("NEO4J_USER", "neo4j")
    monkeypatch.setenv("NEO4J_PASSWORD", "testpass")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("ZEP_API_KEY", "zep-key")
    monkeypatch.setenv("JWT_SECRET_KEY", "jwt-secret")
    
    settings = Settings(_env_file=None)
    assert settings.DATABASE_URL == "postgresql+asyncpg://test:test@localhost:5432/test"
    assert settings.LLM_MODEL_NAME == "gpt-4o"
    assert settings.STORAGE_BACKEND == "local"
    assert settings.MAX_LLM_CALLS_PER_RUN == 10000
