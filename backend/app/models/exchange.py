import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class ExchangeStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


SUPPORTED_EXCHANGES = [
    "binance", "binanceus", "coinbase", "kraken", "bybit",
    "okx", "kucoin", "gate", "huobi", "bitfinex",
]


class ExchangeConnection(Base):
    __tablename__ = "exchange_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exchange_id = Column(String(50), nullable=False)    # e.g. "binance"
    label = Column(String(100), nullable=False)          # user-defined nickname
    encrypted_api_key = Column(Text, nullable=False)     # AES-256 encrypted
    encrypted_api_secret = Column(Text, nullable=False)  # AES-256 encrypted
    encrypted_passphrase = Column(Text, nullable=True)   # for exchanges that require it (e.g. OKX)
    is_testnet = Column(Boolean, default=True)
    allow_trading = Column(Boolean, default=True)
    # SECURITY: withdrawals NEVER allowed via platform
    allow_withdrawals = Column(Boolean, default=False, nullable=False)
    status = Column(SAEnum(ExchangeStatus), default=ExchangeStatus.INACTIVE)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="exchanges")
    bots = relationship("Bot", back_populates="exchange_connection")

    def __repr__(self):
        return f"<ExchangeConnection {self.exchange_id}:{self.label}>"
