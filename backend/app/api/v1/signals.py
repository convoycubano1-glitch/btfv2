from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.signal import Signal, SignalStatus
from app.schemas.signal import SignalCreate, SignalResponse
import uuid

router = APIRouter()


@router.get("/my", response_model=list[SignalResponse])
async def my_signals(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Signal).where(Signal.creator_id == uuid.UUID(user_id))
        .order_by(Signal.created_at.desc())
    )
    return [SignalResponse.model_validate(s) for s in result.scalars().all()]


@router.post("/", response_model=SignalResponse, status_code=201)
async def create_signal(
    payload: SignalCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Check subscription for paid signals
    if not payload.is_free:
        from app.models.subscription import Subscription, SubscriptionPlan
        sub_result = await db.execute(
            select(Subscription).where(Subscription.user_id == uuid.UUID(user_id))
        )
        subscription = sub_result.scalar_one_or_none()
        if not subscription or subscription.plan == SubscriptionPlan.FREE:
            raise HTTPException(
                status_code=403,
                detail="Selling signals requires a Pro or Elite subscription.",
            )

    # Calculate risk/reward ratio
    rr = None
    if payload.take_profit_1 and payload.stop_loss:
        risk = abs(payload.entry_price - payload.stop_loss)
        reward = abs(payload.take_profit_1 - payload.entry_price)
        rr = round(reward / risk, 2) if risk > 0 else None

    signal = Signal(
        creator_id=uuid.UUID(user_id),
        title=payload.title,
        description=payload.description,
        symbol=payload.symbol.upper(),
        signal_type=payload.signal_type,
        timeframe=payload.timeframe,
        entry_price=payload.entry_price,
        stop_loss=payload.stop_loss,
        take_profit_1=payload.take_profit_1,
        take_profit_2=payload.take_profit_2,
        take_profit_3=payload.take_profit_3,
        risk_reward_ratio=rr,
        is_free=payload.is_free,
        price_usd=payload.price_usd if not payload.is_free else 0.0,
        tags=payload.tags,
        expires_at=payload.expires_at,
    )
    db.add(signal)
    await db.commit()
    await db.refresh(signal)
    return SignalResponse.model_validate(signal)


@router.patch("/{signal_id}/publish", response_model=SignalResponse)
async def publish_signal(
    signal_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Signal).where(Signal.id == signal_id, Signal.creator_id == uuid.UUID(user_id))
    )
    signal = result.scalar_one_or_none()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    signal.is_published = True
    await db.commit()
    await db.refresh(signal)
    return SignalResponse.model_validate(signal)


@router.delete("/{signal_id}", status_code=204)
async def delete_signal(
    signal_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Signal).where(Signal.id == signal_id, Signal.creator_id == uuid.UUID(user_id))
    )
    signal = result.scalar_one_or_none()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    await db.delete(signal)
    await db.commit()
