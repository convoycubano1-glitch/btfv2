import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer, JSON, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class TradeStatus(str, enum.Enum):
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TradeSide(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class TradeMode(str, enum.Enum):
    PAPER = "paper"
    LIVE = "live"


class Trade(Base):
    __tablename__ = "trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    bot_id = Column(UUID(as_uuid=True), ForeignKey("bots.id"), nullable=True)
    exchange_connection_id = Column(UUID(as_uuid=True), ForeignKey("exchange_connections.id"), nullable=True)

    # Exchange order details
    exchange_order_id = Column(String(100), nullable=True)
    symbol = Column(String(20), nullable=False)
    side = Column(SAEnum(TradeSide), nullable=False)
    mode = Column(SAEnum(TradeMode), default=TradeMode.PAPER)
    status = Column(SAEnum(TradeStatus), default=TradeStatus.PENDING)

    # Pricing
    entry_price = Column(Float, nullable=True)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=False)
    notional_value = Column(Float, nullable=True)

    # Risk levels
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)

    # P&L
    pnl = Column(Float, nullable=True)
    pnl_pct = Column(Float, nullable=True)
    fees = Column(Float, default=0.0)

    # Strategy that triggered this trade
    strategy_name = Column(String(100), nullable=True)
    signal_data = Column(JSON, nullable=True)

    # Timestamps
    opened_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="trades")
    bot = relationship("Bot", back_populates="trades")

    def __repr__(self):
        return f"<Trade {self.symbol} {self.side} [{self.status}]>"
