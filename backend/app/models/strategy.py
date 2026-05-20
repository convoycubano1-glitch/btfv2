import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class StrategyType(str, enum.Enum):
    EMA_CROSSOVER = "ema_crossover"
    RSI_MEAN_REVERSION = "rsi_mean_reversion"
    MACD_MOMENTUM = "macd_momentum"
    BOLLINGER_BANDS = "bollinger_bands"
    BREAKOUT = "breakout"
    DCA = "dca"
    GRID_TRADING = "grid_trading"
    VOLATILITY_BREAKOUT = "volatility_breakout"
    PORTFOLIO_REBALANCING = "portfolio_rebalancing"
    ARBITRAGE_MONITOR = "arbitrage_monitor"
    TREND_FOLLOWING = "trend_following"
    SMART_SCALPING = "smart_scalping"
    CUSTOM = "custom"


class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    strategy_type = Column(SAEnum(StrategyType), nullable=False)

    # Default parameters for this strategy
    default_parameters = Column(JSON, default=dict)

    # Custom code (for custom strategies)
    custom_code = Column(Text, nullable=True)

    is_public = Column(Boolean, default=False)
    is_built_in = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="strategies")
    bots = relationship("Bot", back_populates="strategy")
    backtests = relationship("Backtest", back_populates="strategy")

    def __repr__(self):
        return f"<Strategy {self.name} [{self.strategy_type}]>"
