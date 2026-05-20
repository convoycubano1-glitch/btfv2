from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.strategy import Strategy, StrategyType
from app.strategies.registry import STRATEGY_REGISTRY
import uuid

router = APIRouter()


@router.get("/built-in", response_model=list[dict])
async def list_built_in_strategies():
    """List all 12 built-in strategies with descriptions and default parameters."""
    return [
        {
            "type": key,
            "name": meta["name"],
            "description": meta["description"],
            "category": meta["category"],
            "default_parameters": meta["default_parameters"],
            "risk_level": meta["risk_level"],
        }
        for key, meta in STRATEGY_REGISTRY.items()
    ]


@router.get("/my", response_model=list[dict])
async def list_my_strategies(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Strategy).where(Strategy.user_id == uuid.UUID(user_id))
    )
    strategies = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "description": s.description,
            "strategy_type": s.strategy_type,
            "default_parameters": s.default_parameters,
            "is_public": s.is_public,
            "created_at": s.created_at,
        }
        for s in strategies
    ]


@router.post("/", response_model=dict, status_code=201)
async def create_custom_strategy(
    payload: dict,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    strategy = Strategy(
        user_id=uuid.UUID(user_id),
        name=payload.get("name", "Custom Strategy"),
        description=payload.get("description"),
        strategy_type=StrategyType.CUSTOM,
        default_parameters=payload.get("parameters", {}),
        is_public=payload.get("is_public", False),
    )
    db.add(strategy)
    await db.commit()
    await db.refresh(strategy)
    return {"id": str(strategy.id), "name": strategy.name, "status": "created"}
