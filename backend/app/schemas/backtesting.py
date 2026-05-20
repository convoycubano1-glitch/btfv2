from pydantic import BaseModel, field_validator
from typing import Optional, Any
from datetime import datetime
import uuid


class BacktestCreate(BaseModel):
    name: str
    symbol: str
    timeframe: str
    strategy_type: str
    parameters: dict[str, Any] = {}
    start_date: datetime
    end_date: datetime
    initial_capital: float = 10000.0

    @field_validator("initial_capital")
    @classmethod
    def positive_capital(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Initial capital must be positive")
        return v

    @field_validator("symbol")
    @classmethod
    def valid_symbol(cls, v: str) -> str:
        if "/" not in v:
            raise ValueError("Symbol must be in format BASE/QUOTE e.g. BTC/USDT")
        return v.upper()


class BacktestResponse(BaseModel):
    id: uuid.UUID
    name: str
    symbol: str
    timeframe: str
    strategy_type: str
    parameters: dict
    start_date: datetime
    end_date: datetime
    initial_capital: float
    status: str
    final_equity: Optional[float]
    total_return_pct: Optional[float]
    annualized_return_pct: Optional[float]
    max_drawdown_pct: Optional[float]
    sharpe_ratio: Optional[float]
    sortino_ratio: Optional[float]
    win_rate_pct: Optional[float]
    total_trades: Optional[int]
    winning_trades: Optional[int]
    losing_trades: Optional[int]
    profit_factor: Optional[float]
    expectancy: Optional[float]
    error_message: Optional[str]
    duration_seconds: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class BacktestDetailResponse(BacktestResponse):
    trade_log: Optional[list]
    equity_curve: Optional[list]
