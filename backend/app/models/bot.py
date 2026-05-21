import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Float, Integer, JSON, Enum as SAEnum, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class BotStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class TradingMode(str, enum.Enum):
    PAPER = "paper"
    LIVE = "live"


class Bot(Base):
    __tablename__ = "bots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exchange_connection_id = Column(UUID(as_uuid=True), ForeignKey("exchange_connections.id"), nullable=True)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=True)

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    symbol = Column(String(20), nullable=False)       # e.g. "BTC/USDT"
    timeframe = Column(String(10), nullable=False)    # e.g. "1h"

    # Trading mode — paper by default for safety
    mode = Column(SAEnum(TradingMode), default=TradingMode.PAPER, nullable=False)
    status = Column(SAEnum(BotStatus), default=BotStatus.DRAFT)

    # Strategy parameters (JSON)
    parameters = Column(JSON, default=dict)

    # Risk settings
    max_position_size_pct = Column(Float, default=0.02)  # % of portfolio per trade
    stop_loss_pct = Column(Float, default=0.02)
    take_profit_pct = Column(Float, default=0.04)
    max_open_trades = Column(Integer, default=1)
    max_daily_loss_pct = Column(Float, default=0.05)

    # Performance metrics (denormalized for quick access)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    total_pnl_pct = Column(Float, default=0.0)

    last_run_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="bots")
    exchange_connection = relationship("ExchangeConnection", back_populates="bots")
    strategy = relationship("Strategy", back_populates="bots")
    trades = relationship("Trade", back_populates="bot")

    __table_args__ = (
        Index("ix_bots_user_id", "user_id"),
        Index("ix_bots_status", "status"),
        Index("ix_bots_user_status", "user_id", "status"),
    )

    def __repr__(self):
        return f"<Bot {self.name} [{self.status}]>"
