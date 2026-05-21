from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter
import logging

from app.core.config import settings
from app.core.database import create_tables
from app.core.redis_client import redis_client
from app.api.v1.router import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Rate limiter ──────────────────────────────────────────────────────────────────
# limiter is defined in app.core.limiter and shared with endpoint modules.


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────
    logger.info("Starting TradeBotHub Pro API...")
    await create_tables()
    await redis_client.connect()
    await _reset_stuck_backtests()
    logger.info("Database and Redis connected.")
    yield
    # ── Shutdown ─────────────────────────────────────
    await redis_client.disconnect()
    logger.info("TradeBotHub Pro API stopped.")


async def _reset_stuck_backtests():
    """Reset backtests stuck in RUNNING state (server restarted mid-execution)."""
    try:
        from app.models.backtest import Backtest, BacktestStatus
        from sqlalchemy import update
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                update(Backtest)
                .where(Backtest.status == BacktestStatus.RUNNING)
                .values(
                    status=BacktestStatus.FAILED,
                    error_message="Server restarted during execution. Please re-run.",
                )
            )
            if result.rowcount:
                logger.warning(f"Reset {result.rowcount} stuck backtest(s) to FAILED.")
            await db.commit()
    except Exception as e:
        logger.error(f"Could not reset stuck backtests: {e}")


app = FastAPI(
    title="TradeBotHub Pro",
    description=(
        "Professional SaaS Algorithmic Trading Platform. "
        "⚠️ This platform does not provide financial advice. "
        "All trading involves significant risk of loss."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── Rate limiting ─────────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ── Global exception handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "disclaimer": (
            "TradeBotHub Pro does not provide financial advice. "
            "All trading involves risk of loss."
        ),
    }
