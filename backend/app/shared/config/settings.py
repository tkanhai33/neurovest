from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[4]
ENV_FILE = ROOT_DIR / ".env"


class Settings(BaseSettings):
    app_env: str = "local"
    app_name: str = "NeuroVest"
    database_url: str

    broker_enabled: bool = False
    live_trading_enabled: bool = False
    canary_trading_enabled: bool = False

    ollama_base_url: str = "http://localhost:11434"
    ollama_default_chat_model: str = "qwen3:8b"
    ollama_coder_model: str = "qwen2.5-coder:14b"
    ollama_heavy_coder_model: str = "qwen3-coder:30b"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
