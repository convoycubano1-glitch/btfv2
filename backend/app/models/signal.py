import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Float, Integer, JSON, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class SignalType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class SignalStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Signal(Base):
    __tablename__ = "signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Signal details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    symbol = Column(String(20), nullable=False)
    signal_type = Column(SAEnum(SignalType), nullable=False)
    timeframe = Column(String(10), nullable=False)

    # Price targets
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit_1 = Column(Float, nullable=True)
    take_profit_2 = Column(Float, nullable=True)
    take_profit_3 = Column(Float, nullable=True)
    risk_reward_ratio = Column(Float, nullable=True)

    # Marketplace
    is_free = Column(Boolean, default=True)
    price_usd = Column(Float, default=0.0)
    is_published = Column(Boolean, default=False)
    status = Column(SAEnum(SignalStatus), default=SignalStatus.ACTIVE)

    # Performance tracking
    subscribers_count = Column(Integer, default=0)
    hit_tp1 = Column(Boolean, nullable=True)
    hit_tp2 = Column(Boolean, nullable=True)
    hit_stop_loss = Column(Boolean, nullable=True)
    final_pnl_pct = Column(Float, nullable=True)

    # Metadata
    tags = Column(JSON, default=list)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    creator = relationship("User", back_populates="signals")

    def __repr__(self):
        return f"<Signal {self.symbol} {self.signal_type}>"


class SignalSubscription(Base):
    """Users who subscribe to a signal provider."""
    __tablename__ = "signal_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    stripe_subscription_id = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
