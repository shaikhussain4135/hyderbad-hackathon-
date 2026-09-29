"""Configuration management with secure secret masking."""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

# Load .env if present
if ENV_FILE.exists():
    load_dotenv(ENV_FILE, override=True)
else:
    load_dotenv(override=True)


def mask_secret(value: Optional[str], visible_chars: int = 4) -> str:
    """Mask sensitive string, showing only trailing characters or dots."""
    if not value or not value.strip():
        return "(not set)"
    clean = value.strip()
    if len(clean) <= visible_chars * 2:
        return "••••••••"
    return f"{clean[:visible_chars]}••••••••{clean[-visible_chars:]}"


class Config:
    """Application configuration container."""

    def __init__(self):
        self.reload()

    def reload(self):
        """Reload configuration from environment."""
        if ENV_FILE.exists():
            load_dotenv(ENV_FILE, override=True)

        self.hindsight_url: str = os.getenv("HINDSIGHT_URL", "http://localhost:8888").strip()
        self.hindsight_api_key: Optional[str] = os.getenv("HINDSIGHT_API_KEY", "").strip() or None

        self.database_url: Optional[str] = os.getenv("DATABASE_URL", "").strip() or None

        self.llm_provider: str = os.getenv("LLM_PROVIDER", "groq").strip().lower()
        self.llm_api_key: Optional[str] = os.getenv("LLM_API_KEY", "").strip() or None
        self.llm_model: str = os.getenv(
            "LLM_MODEL",
            "llama-3.3-70b-versatile" if self.llm_provider == "groq" else "gpt-4o-mini"
        ).strip()
        self.llm_base_url: Optional[str] = os.getenv("LLM_BASE_URL", "").strip() or None

        self.app_env: str = os.getenv("APP_ENV", "development").strip()
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").strip()

    def update_and_save(
        self,
        hindsight_url: Optional[str] = None,
        hindsight_api_key: Optional[str] = None,
        database_url: Optional[str] = None,
        llm_provider: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_base_url: Optional[str] = None,
    ):
        """Update runtime config and optionally persist to local .env file."""
        if hindsight_url is not None:
            self.hindsight_url = hindsight_url.strip()
            os.environ["HINDSIGHT_URL"] = self.hindsight_url
        if hindsight_api_key is not None:
            self.hindsight_api_key = hindsight_api_key.strip() or None
            if self.hindsight_api_key:
                os.environ["HINDSIGHT_API_KEY"] = self.hindsight_api_key
            elif "HINDSIGHT_API_KEY" in os.environ:
                del os.environ["HINDSIGHT_API_KEY"]

        if database_url is not None:
            self.database_url = database_url.strip() or None
            if self.database_url:
                os.environ["DATABASE_URL"] = self.database_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

        if llm_provider is not None:
            self.llm_provider = llm_provider.strip().lower()
            os.environ["LLM_PROVIDER"] = self.llm_provider
        if llm_api_key is not None:
            self.llm_api_key = llm_api_key.strip() or None
            if self.llm_api_key:
                os.environ["LLM_API_KEY"] = self.llm_api_key
            elif "LLM_API_KEY" in os.environ:
                del os.environ["LLM_API_KEY"]

        if llm_model is not None:
            self.llm_model = llm_model.strip()
            os.environ["LLM_MODEL"] = self.llm_model
        if llm_base_url is not None:
            self.llm_base_url = llm_base_url.strip() or None
            if self.llm_base_url:
                os.environ["LLM_BASE_URL"] = self.llm_base_url
            elif "LLM_BASE_URL" in os.environ:
                del os.environ["LLM_BASE_URL"]

        # Persist to local .env safely
        lines = [
            f"HINDSIGHT_URL={self.hindsight_url}",
            f"HINDSIGHT_API_KEY={self.hindsight_api_key or ''}",
            f"DATABASE_URL={self.database_url or ''}",
            f"LLM_PROVIDER={self.llm_provider}",
            f"LLM_API_KEY={self.llm_api_key or ''}",
            f"LLM_MODEL={self.llm_model}",
            f"LLM_BASE_URL={self.llm_base_url or ''}",
            f"APP_ENV={self.app_env}",
            f"LOG_LEVEL={self.log_level}",
        ]
        ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


config = Config()
