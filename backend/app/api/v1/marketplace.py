from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.signal import Signal, SignalStatus, SignalSubscription
from app.schemas.signal import SignalCreate, SignalResponse
import uuid

router = APIRouter()


@router.get("/", response_model=list[SignalResponse])
async def list_marketplace_signals(
    symbol: str | None = Query(None),
    free_only: bool = Query(False),
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Public marketplace — browse all published signals."""
    query = select(Signal).where(
        Signal.is_published == True,
        Signal.status == SignalStatus.ACTIVE,
    )
    if symbol:
        query = query.where(Signal.symbol == symbol.upper())
    if free_only:
        query = query.where(Signal.is_free == True)
    query = query.order_by(Signal.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return [SignalResponse.model_validate(s) for s in result.scalars().all()]


@router.get("/{signal_id}", response_model=SignalResponse)
async def get_signal(signal_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Signal).where(Signal.id == signal_id, Signal.is_published == True)
    )
    signal = result.scalar_one_or_none()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return SignalResponse.model_validate(signal)


@router.post("/{signal_id}/subscribe", response_model=dict)
async def subscribe_to_signal(
    signal_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Subscribe to receive a signal (free or paid)."""
    result = await db.execute(
        select(Signal).where(Signal.id == signal_id, Signal.is_published == True)
    )
    signal = result.scalar_one_or_none()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    # Check if already subscribed
    existing = await db.execute(
        select(SignalSubscription).where(
            SignalSubscription.subscriber_id == uuid.UUID(user_id),
            SignalSubscription.provider_id == signal.creator_id,
            SignalSubscription.is_active == True,
        )
    )
    if existing.scalar_one_or_none():
        return {"message": "Already subscribed", "success": False}

    if not signal.is_free:
        return {
            "message": "Paid signal — initiate Stripe checkout",
            "signal_id": str(signal_id),
            "price_usd": signal.price_usd,
            "requires_payment": True,
        }

    sub = SignalSubscription(
        subscriber_id=uuid.UUID(user_id),
        provider_id=signal.creator_id,
    )
    db.add(sub)
    signal.subscribers_count += 1
    await db.commit()
    return {"message": "Subscribed successfully", "success": True}
