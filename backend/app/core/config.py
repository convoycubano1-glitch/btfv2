from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List
import secrets
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # ── App ───────────────────────────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    # REQUIRED in production — set via env var. Never let this auto-generate
    # because all JWTs are invalidated on every restart.
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ENCRYPTION_KEY: str = ""          # Fernet key for API key encryption
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── Frontend ──────────────────────────────────────────────────────────────
    FRONTEND_URL: str = "https://btfv2.netlify.app"

    # ── Clerk JWKS cache TTL (seconds) ────────────────────────────────────────
    JWKS_CACHE_TTL_SECONDS: int = 300  # 5 minutes

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://tradebothub:tradebothub_secret@localhost:5432/tradebothub"

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Stored as a comma-separated string to avoid pydantic-settings JSON parsing issues.
    # Use the allowed_origins property to get a list.
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def allowed_origins_list(self) -> List[str]:
        import json
        v = self.ALLOWED_ORIGINS.strip()
        if v.startswith("["):
            return json.loads(v)
        return [o.strip() for o in v.split(",") if o.strip()]

    # ── Supabase ──────────────────────────────────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # ── Stripe ────────────────────────────────────────────────────────────────
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_PRO: str = ""
    STRIPE_PRICE_ELITE: str = ""

    # ── OpenAI ────────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    # ── Risk defaults ─────────────────────────────────────────────────────────
    MAX_POSITION_SIZE_PCT: float = 0.05   # 5% of portfolio per trade
    MAX_DAILY_LOSS_PCT: float = 0.10      # 10% daily loss limit
    DEFAULT_STOP_LOSS_PCT: float = 0.02   # 2% stop loss

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

# ── Runtime validation warnings ───────────────────────────────────────────────
if settings.ENVIRONMENT == "production":
    if not settings.ENCRYPTION_KEY:
        raise RuntimeError(
            "ENCRYPTION_KEY env var is required in production. "
            "Generate with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
if settings.ENCRYPTION_KEY == "":
    logger.warning(
        "ENCRYPTION_KEY not set — exchange API keys cannot be saved/restored. "
        "Set ENCRYPTION_KEY env var before adding exchange connections."
    )
