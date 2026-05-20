from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import uuid


class ExchangeConnectionCreate(BaseModel):
    exchange_id: str
    label: str
    api_key: str
    api_secret: str
    passphrase: Optional[str] = None
    is_testnet: bool = True

    @field_validator("exchange_id")
    @classmethod
    def valid_exchange(cls, v: str) -> str:
        from app.models.exchange import SUPPORTED_EXCHANGES
        if v not in SUPPORTED_EXCHANGES:
            raise ValueError(f"Unsupported exchange. Supported: {SUPPORTED_EXCHANGES}")
        return v

    @field_validator("api_key", "api_secret")
    @classmethod
    def non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("API key and secret cannot be empty")
        return v.strip()


class ExchangeConnectionResponse(BaseModel):
    id: uuid.UUID
    exchange_id: str
    label: str
    is_testnet: bool
    allow_trading: bool
    allow_withdrawals: bool
    status: str
    last_verified_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ExchangeConnectionUpdate(BaseModel):
    label: Optional[str] = None
    is_testnet: Optional[bool] = None
    allow_trading: Optional[bool] = None
