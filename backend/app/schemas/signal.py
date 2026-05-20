from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class SignalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    symbol: str
    signal_type: str
    timeframe: str
    entry_price: float
    stop_loss: float
    take_profit_1: Optional[float] = None
    take_profit_2: Optional[float] = None
    take_profit_3: Optional[float] = None
    is_free: bool = True
    price_usd: float = 0.0
    tags: list[str] = []
    expires_at: Optional[datetime] = None


class SignalResponse(BaseModel):
    id: uuid.UUID
    creator_id: uuid.UUID
    title: str
    description: Optional[str]
    symbol: str
    signal_type: str
    timeframe: str
    entry_price: float
    stop_loss: float
    take_profit_1: Optional[float]
    take_profit_2: Optional[float]
    take_profit_3: Optional[float]
    risk_reward_ratio: Optional[float]
    is_free: bool
    price_usd: float
    is_published: bool
    status: str
    subscribers_count: int
    hit_tp1: Optional[bool]
    hit_stop_loss: Optional[bool]
    final_pnl_pct: Optional[float]
    tags: list
    expires_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
