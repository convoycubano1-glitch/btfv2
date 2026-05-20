import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Float, Integer, JSON, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ELITE = "elite"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    EXPIRED = "expired"


PLAN_LIMITS = {
    SubscriptionPlan.FREE: {
        "max_bots": 1,
        "max_exchanges": 1,
        "live_trading": False,
        "backtesting": True,
        "marketplace": False,
        "ai_assistant": False,
        "signals_per_month": 0,
    },
    SubscriptionPlan.PRO: {
        "max_bots": 5,
        "max_exchanges": 3,
        "live_trading": True,
        "backtesting": True,
        "marketplace": True,
        "ai_assistant": False,
        "signals_per_month": 10,
    },
    SubscriptionPlan.ELITE: {
        "max_bots": -1,   # unlimited
        "max_exchanges": -1,
        "live_trading": True,
        "backtesting": True,
        "marketplace": True,
        "ai_assistant": True,
        "signals_per_month": -1,
    },
}


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    plan = Column(SAEnum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    status = Column(SAEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)

    # Stripe
    stripe_customer_id = Column(String(255), nullable=True, unique=True)
    stripe_subscription_id = Column(String(255), nullable=True, unique=True)

    # Billing
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="subscription")

    def get_limits(self) -> dict:
        return PLAN_LIMITS.get(self.plan, PLAN_LIMITS[SubscriptionPlan.FREE])

    def __repr__(self):
        return f"<Subscription {self.plan} [{self.status}]>"
