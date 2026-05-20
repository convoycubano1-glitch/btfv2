from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus, PLAN_LIMITS
from app.services.stripe_service import StripeService
import uuid

router = APIRouter()


@router.get("/my", response_model=dict)
async def get_my_subscription(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == uuid.UUID(user_id))
    )
    sub = result.scalar_one_or_none()
    if not sub:
        return {"plan": "free", "status": "active", "limits": PLAN_LIMITS[SubscriptionPlan.FREE]}
    return {
        "id": str(sub.id),
        "plan": sub.plan,
        "status": sub.status,
        "current_period_end": sub.current_period_end,
        "cancel_at_period_end": sub.cancel_at_period_end,
        "limits": sub.get_limits(),
    }


@router.post("/checkout")
async def create_checkout_session(
    plan: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if plan not in ("pro", "elite"):
        raise HTTPException(status_code=400, detail="Invalid plan. Choose 'pro' or 'elite'")

    from app.models.user import User
    user_result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stripe_service = StripeService()
    session_url = await stripe_service.create_checkout_session(
        user_id=str(user.id),
        email=user.email,
        plan=plan,
    )
    return {"checkout_url": session_url}


@router.post("/cancel")
async def cancel_subscription(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == uuid.UUID(user_id))
    )
    sub = result.scalar_one_or_none()
    if not sub or not sub.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="No active subscription found")

    stripe_service = StripeService()
    await stripe_service.cancel_subscription(sub.stripe_subscription_id)
    sub.cancel_at_period_end = True
    await db.commit()
    return {"message": "Subscription will be cancelled at end of billing period"}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    stripe_service = StripeService()
    event = stripe_service.construct_webhook_event(payload, sig_header)
    if not event:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    await stripe_service.handle_webhook_event(event, db)
    return {"received": True}
