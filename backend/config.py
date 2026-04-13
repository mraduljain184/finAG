"""
finAG — Configuration
Loads environment variables and exposes typed settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

class Settings:
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")

    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    REPORT_CACHE_TTL: int = int(os.getenv("REPORT_CACHE_TTL", "86400"))

    @property
    def llm_provider(self) -> str:
        if self.ANTHROPIC_API_KEY:
            return "anthropic"
        elif self.OPENAI_API_KEY:
            return "openai"
        return "none"

settings = Settings()