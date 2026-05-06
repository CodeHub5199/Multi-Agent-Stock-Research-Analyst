"""
api/config.py
-------------
Centralised settings loaded from environment variables (.env supported via python-dotenv).
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Groq
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"

    # Tavily (news agent)
    tavily_api_key: str = ""

    # Pipeline
    default_depth: str = "standard"   # standard | deep

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
