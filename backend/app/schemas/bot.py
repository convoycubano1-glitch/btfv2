from pydantic import BaseModel, field_validator
from typing import Optional, Any
from datetime import datetime
import uuid


class BotCreate(BaseModel):
    name: str
    description: Optional[str] = None
    exchange_connection_id: Optional[uuid.UUID] = None
    strategy_id: Optional[uuid.UUID] = None
    symbol: str
    timeframe: str
    mode: str = "paper"
    parameters: dict[str, Any] = {}
    max_position_size_pct: float = 0.02
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.04
    max_open_trades: int = 1
    max_daily_loss_pct: float = 0.05

    @field_validator("mode")
    @classmethod
    def valid_mode(cls, v: str) -> str:
        if v not in ("paper", "live"):
            raise ValueError("mode must be 'paper' or 'live'")
        return v

    @field_validator("symbol")
    @classmethod
    def valid_symbol(cls, v: str) -> str:
        if "/" not in v:
            raise ValueError("Symbol must be in format BASE/QUOTE e.g. BTC/USDT")
        return v.upper()


class BotResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    symbol: str
    timeframe: str
    mode: str
    status: str
    parameters: dict
    max_position_size_pct: float
    stop_loss_pct: float
    take_profit_pct: float
    max_open_trades: int
    total_trades: int
    winning_trades: int
    total_pnl: float
    total_pnl_pct: float
    last_run_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class BotUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[dict[str, Any]] = None
    max_position_size_pct: Optional[float] = None
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None
    max_open_trades: Optional[int] = None
    max_daily_loss_pct: Optional[float] = None
