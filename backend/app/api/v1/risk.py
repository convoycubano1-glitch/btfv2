from fastapi import APIRouter, Depends
from app.core.security import get_current_user_id
from app.services.risk_manager import RiskManager

router = APIRouter()


@router.post("/validate-bot")
async def validate_bot_risk(
    payload: dict,
    user_id: str = Depends(get_current_user_id),
):
    """Validate risk parameters before activating a bot."""
    result = RiskManager.validate_bot_risk(payload)
    return result


@router.get("/guidelines")
async def get_risk_guidelines():
    """Return platform risk management guidelines."""
    return {
        "guidelines": RiskManager.get_risk_guidelines(),
        "disclaimer": "These are guidelines only, not financial advice.",
    }


@router.post("/position-size")
async def calculate_position_size(
    payload: dict,
    user_id: str = Depends(get_current_user_id),
):
    """Calculate recommended position size based on account size and risk tolerance."""
    account_size = payload.get("account_size", 10000)
    risk_pct = payload.get("risk_pct", 1.0)
    entry_price = payload.get("entry_price")
    stop_loss = payload.get("stop_loss")

    if not entry_price or not stop_loss:
        return {"error": "entry_price and stop_loss are required"}

    result = RiskManager.calculate_position_size(
        account_size=account_size,
        risk_pct=risk_pct,
        entry_price=entry_price,
        stop_loss=stop_loss,
    )
    return {
        **result,
        "disclaimer": "Position sizing is for educational purposes only.",
    }
