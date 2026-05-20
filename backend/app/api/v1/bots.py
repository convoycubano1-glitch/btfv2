from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.bot import Bot, BotStatus, TradingMode
from app.models.user import User
from app.schemas.bot import BotCreate, BotResponse, BotUpdate
from app.services.risk_manager import RiskManager
import uuid

router = APIRouter()


async def _get_user_bot(bot_id: uuid.UUID, user_id: str, db: AsyncSession) -> Bot:
    result = await db.execute(
        select(Bot).where(Bot.id == bot_id, Bot.user_id == uuid.UUID(user_id))
    )
    bot = result.scalar_one_or_none()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot


@router.get("/", response_model=list[BotResponse])
async def list_bots(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Bot).where(Bot.user_id == uuid.UUID(user_id)))
    return [BotResponse.model_validate(b) for b in result.scalars().all()]


@router.post("/", response_model=BotResponse, status_code=201)
async def create_bot(
    payload: BotCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Check subscription limits
    from app.models.subscription import Subscription
    sub_result = await db.execute(select(Subscription).where(Subscription.user_id == uuid.UUID(user_id)))
    subscription = sub_result.scalar_one_or_none()
    if subscription:
        limits = subscription.get_limits()
        if limits["max_bots"] != -1:
            bot_count_result = await db.execute(select(Bot).where(Bot.user_id == uuid.UUID(user_id)))
            current_bots = len(bot_count_result.scalars().all())
            if current_bots >= limits["max_bots"]:
                raise HTTPException(
                    status_code=403,
                    detail=f"Bot limit reached ({limits['max_bots']}). Upgrade your plan.",
                )
        if payload.mode == "live" and not limits["live_trading"]:
            raise HTTPException(
                status_code=403,
                detail="Live trading requires a Pro or Elite subscription.",
            )

    # Safety: default to paper trading
    if payload.mode == "live":
        # Validate risk before going live
        risk_check = RiskManager.validate_bot_risk(payload.model_dump())
        if not risk_check["passed"]:
            raise HTTPException(
                status_code=400,
                detail=f"Risk validation failed: {risk_check['reason']}",
            )

    bot = Bot(
        user_id=uuid.UUID(user_id),
        name=payload.name,
        description=payload.description,
        exchange_connection_id=payload.exchange_connection_id,
        strategy_id=payload.strategy_id,
        symbol=payload.symbol,
        timeframe=payload.timeframe,
        mode=TradingMode(payload.mode),
        parameters=payload.parameters,
        max_position_size_pct=payload.max_position_size_pct,
        stop_loss_pct=payload.stop_loss_pct,
        take_profit_pct=payload.take_profit_pct,
        max_open_trades=payload.max_open_trades,
        max_daily_loss_pct=payload.max_daily_loss_pct,
    )
    db.add(bot)
    await db.commit()
    await db.refresh(bot)
    return BotResponse.model_validate(bot)


@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(
    bot_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    bot = await _get_user_bot(bot_id, user_id, db)
    return BotResponse.model_validate(bot)


@router.patch("/{bot_id}", response_model=BotResponse)
async def update_bot(
    bot_id: uuid.UUID,
    payload: BotUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    bot = await _get_user_bot(bot_id, user_id, db)
    if bot.status == BotStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Cannot update a running bot. Pause it first.")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(bot, field, value)
    await db.commit()
    await db.refresh(bot)
    return BotResponse.model_validate(bot)


@router.delete("/{bot_id}", status_code=204)
async def delete_bot(
    bot_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    bot = await _get_user_bot(bot_id, user_id, db)
    if bot.status == BotStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Stop the bot before deleting.")
    await db.delete(bot)
    await db.commit()


@router.post("/{bot_id}/start", response_model=BotResponse)
async def start_bot(
    bot_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    bot = await _get_user_bot(bot_id, user_id, db)

    # Check emergency stop
    user_result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = user_result.scalar_one_or_none()
    if user and user.emergency_stop_active:
        raise HTTPException(status_code=403, detail="Emergency stop is active. Resume it first.")

    if bot.status == BotStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Bot is already running")

    # Live trading requires exchange connection
    if bot.mode == TradingMode.LIVE and not bot.exchange_connection_id:
        raise HTTPException(status_code=400, detail="Live trading requires an exchange connection")

    bot.status = BotStatus.ACTIVE
    bot.error_message = None
    await db.commit()
    await db.refresh(bot)
    return BotResponse.model_validate(bot)


@router.post("/{bot_id}/pause", response_model=BotResponse)
async def pause_bot(
    bot_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    bot = await _get_user_bot(bot_id, user_id, db)
    bot.status = BotStatus.PAUSED
    await db.commit()
    await db.refresh(bot)
    return BotResponse.model_validate(bot)


@router.post("/{bot_id}/stop", response_model=BotResponse)
async def stop_bot(
    bot_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    bot = await _get_user_bot(bot_id, user_id, db)
    bot.status = BotStatus.STOPPED
    await db.commit()
    await db.refresh(bot)
    return BotResponse.model_validate(bot)
