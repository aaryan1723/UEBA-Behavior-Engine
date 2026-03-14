"""
Application Settings

Centralized configuration management using Pydantic.

Loads environment variables and exposes them as typed settings.

Author: Aryan Patel
"""

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    MCP_HOST: str
    MCP_PORT: int
    MCP_PROTOCOL: str
    MCP_STATEFUL: bool

    MCP_SERVER_NAME: str = "Cognisec-UEBA-Intelligence-MCP"

    class Config:
        env_file = ENV_FILE
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """
    Returns cached settings instance
    """

    return Settings()