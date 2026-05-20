from fastapi import APIRouter
from app.api.v1 import (
    auth, exchanges, bots, strategies,
    backtesting, trading, marketplace, signals,
    risk, reports, subscriptions, ai_assistant, websocket
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(exchanges.router, prefix="/exchanges", tags=["Exchanges"])
api_router.include_router(bots.router, prefix="/bots", tags=["Bots"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["Strategies"])
api_router.include_router(backtesting.router, prefix="/backtesting", tags=["Backtesting"])
api_router.include_router(trading.router, prefix="/trading", tags=["Trading"])
api_router.include_router(marketplace.router, prefix="/marketplace", tags=["Marketplace"])
api_router.include_router(signals.router, prefix="/signals", tags=["Signals"])
api_router.include_router(risk.router, prefix="/risk", tags=["Risk Management"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
api_router.include_router(ai_assistant.router, prefix="/ai", tags=["AI Assistant"])
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
