"""Application configuration module."""
from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache
import os
import json


class Settings(BaseSettings):
    """Centralized configuration for AI Tutor Backend."""

    # ─────────────── Application Metadata ───────────────
    APP_NAME: str = "AI Tutor Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # ─────────────── Server ───────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ─────────────── Database ───────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/ai_tutor.db"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0

    # ─────────────── Redis Cache ───────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ─────────────── OpenAI / LLM ───────────────
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_TEMPERATURE: float = 0.7

    # ─────────────── Hugging Face ───────────────
    HF_TOKEN: Optional[str] = os.getenv("HF_TOKEN")  # ✅ Added this line

    # ─────────────── Ollama ───────────────
    OLLAMA_HOST: str = "http://localhost:11434"

    # ─────────────── Pinecone Vector Store ───────────────
    PINECONE_API_KEY: Optional[str] = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: Optional[str] = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: str = "ai-tutor-content"

    # ─────────────── Local Chroma fallback ───────────────
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"

    # ─────────────── Authentication / JWT ───────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")  # ✅ Fixed typo (was JSECRET_KEY)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─────────────── CORS Settings ───────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    @property
    def cors_origin_list(self) -> List[str]:
        """Parse JSON list from env if provided."""
        try:
            if isinstance(self.CORS_ORIGINS, str):
                return json.loads(self.CORS_ORIGINS)
        except json.JSONDecodeError:
            pass
        return self.CORS_ORIGINS

    # ─────────────── Logging ───────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = "./data/logs/app.log"

    # ─────────────── LangChain / Agents ───────────────
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_ENDPOINT: Optional[str] = None
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "ai-tutor"

    # ─────────────── Agent Config ───────────────
    MAX_ITERATIONS: int = 10
    AGENT_TIMEOUT: int = 30

    # ─────────────── Content Settings ───────────────
    CONTENT_CHUNK_SIZE: int = 1000
    CONTENT_CHUNK_OVERLAP: int = 200
    MAX_QUIZ_QUESTIONS: int = 10

    # ─────────────── Performance ───────────────
    BATCH_SIZE: int = 32
    MAX_CONCURRENT_REQUESTS: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "forbid"  # ✅ Keep this strict mode now that HF_TOKEN is defined


@lru_cache()
def get_settings() -> Settings:
    """Return a cached global settings instance."""
    return Settings()


# Global settings importable across the app
settings = get_settings()
