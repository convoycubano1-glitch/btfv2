import stripe
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

PLAN_PRICE_MAP = {
    "pro": settings.STRIPE_PRICE_PRO,
    "elite": settings.STRIPE_PRICE_ELITE,
}


class StripeService:
    async def create_checkout_session(
        self,
        user_id: str,
        email: str,
        plan: str,
    ) -> str:
        """Create a Stripe Checkout session and return the URL."""
        price_id = PLAN_PRICE_MAP.get(plan)
        if not price_id:
            raise ValueError(f"Invalid plan: {plan}")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            customer_email=email,
            client_reference_id=user_id,
            metadata={"user_id": user_id, "plan": plan},
            success_url="http://localhost:3000/subscription?success=true",
            cancel_url="http://localhost:3000/subscription?cancelled=true",
        )
        return session.url

    async def cancel_subscription(self, stripe_subscription_id: str):
        """Cancel a Stripe subscription at period end."""
        stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=True,
        )

    def construct_webhook_event(self, payload: bytes, sig_header: str):
        """Verify and construct a Stripe webhook event."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except stripe.error.SignatureVerificationError:
            logger.warning("Invalid Stripe webhook signature")
            return None

    async def handle_webhook_event(self, event: dict, db):
        """Process Stripe webhook events to update subscription status."""
        from sqlalchemy import select
        from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
        from datetime import datetime, timezone

        event_type = event["type"]
        data = event["data"]["object"]

        if event_type == "checkout.session.completed":
            user_id = data["metadata"].get("user_id")
            plan = data["metadata"].get("plan", "pro")
            stripe_customer_id = data.get("customer")
            stripe_sub_id = data.get("subscription")

            if user_id:
                import uuid
                result = await db.execute(
                    select(Subscription).where(Subscription.user_id == uuid.UUID(user_id))
                )
                sub = result.scalar_one_or_none()
                if sub:
                    sub.plan = SubscriptionPlan(plan)
                    sub.status = SubscriptionStatus.ACTIVE
                    sub.stripe_customer_id = stripe_customer_id
                    sub.stripe_subscription_id = stripe_sub_id
                await db.commit()
                logger.info(f"Subscription activated: user={user_id} plan={plan}")

        elif event_type == "customer.subscription.deleted":
            stripe_sub_id = data["id"]
            result = await db.execute(
                select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub_id)
            )
            sub = result.scalar_one_or_none()
            if sub:
                sub.plan = SubscriptionPlan.FREE
                sub.status = SubscriptionStatus.EXPIRED
                sub.stripe_subscription_id = None
                await db.commit()
                logger.info(f"Subscription cancelled: stripe_sub={stripe_sub_id}")
