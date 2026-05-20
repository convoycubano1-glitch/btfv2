from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.backtest import Backtest, BacktestStatus
from app.schemas.backtesting import BacktestCreate, BacktestResponse, BacktestDetailResponse
from app.services.backtesting_engine import run_backtest
import uuid

router = APIRouter()


@router.post("/", response_model=BacktestResponse, status_code=202)
async def create_backtest(
    payload: BacktestCreate,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    backtest = Backtest(
        user_id=uuid.UUID(user_id),
        name=payload.name,
        symbol=payload.symbol,
        timeframe=payload.timeframe,
        strategy_type=payload.strategy_type,
        parameters=payload.parameters,
        start_date=payload.start_date,
        end_date=payload.end_date,
        initial_capital=payload.initial_capital,
        status=BacktestStatus.PENDING,
    )
    db.add(backtest)
    await db.commit()
    await db.refresh(backtest)

    # Run in background
    background_tasks.add_task(run_backtest, str(backtest.id))

    return BacktestResponse.model_validate(backtest)


@router.get("/", response_model=list[BacktestResponse])
async def list_backtests(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Backtest).where(Backtest.user_id == uuid.UUID(user_id))
        .order_by(Backtest.created_at.desc())
    )
    return [BacktestResponse.model_validate(b) for b in result.scalars().all()]


@router.get("/{backtest_id}", response_model=BacktestDetailResponse)
async def get_backtest(
    backtest_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Backtest).where(
            Backtest.id == backtest_id,
            Backtest.user_id == uuid.UUID(user_id),
        )
    )
    bt = result.scalar_one_or_none()
    if not bt:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return BacktestDetailResponse.model_validate(bt)


@router.delete("/{backtest_id}", status_code=204)
async def delete_backtest(
    backtest_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Backtest).where(
            Backtest.id == backtest_id,
            Backtest.user_id == uuid.UUID(user_id),
        )
    )
    bt = result.scalar_one_or_none()
    if not bt:
        raise HTTPException(status_code=404, detail="Backtest not found")
    await db.delete(bt)
    await db.commit()
