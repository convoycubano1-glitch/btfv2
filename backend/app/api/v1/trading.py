from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.trade import Trade, TradeStatus
from app.models.bot import Bot, BotStatus
import uuid

router = APIRouter()


@router.get("/trades", response_model=list[dict])
async def get_trades(
    limit: int = 50,
    offset: int = 0,
    mode: str | None = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    query = select(Trade).where(Trade.user_id == uuid.UUID(user_id))
    if mode:
        query = query.where(Trade.mode == mode)
    query = query.order_by(desc(Trade.created_at)).limit(limit).offset(offset)
    result = await db.execute(query)
    trades = result.scalars().all()
    return [
        {
            "id": str(t.id),
            "symbol": t.symbol,
            "side": t.side,
            "mode": t.mode,
            "status": t.status,
            "entry_price": t.entry_price,
            "exit_price": t.exit_price,
            "quantity": t.quantity,
            "pnl": t.pnl,
            "pnl_pct": t.pnl_pct,
            "strategy_name": t.strategy_name,
            "opened_at": t.opened_at,
            "closed_at": t.closed_at,
        }
        for t in trades
    ]


@router.get("/active-bots", response_model=list[dict])
async def get_active_bots(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Bot).where(
            Bot.user_id == uuid.UUID(user_id),
            Bot.status == BotStatus.ACTIVE,
        )
    )
    bots = result.scalars().all()
    return [
        {
            "id": str(b.id),
            "name": b.name,
            "symbol": b.symbol,
            "mode": b.mode,
            "total_pnl": b.total_pnl,
            "total_trades": b.total_trades,
            "last_run_at": b.last_run_at,
        }
        for b in bots
    ]


@router.get("/portfolio-summary")
async def get_portfolio_summary(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Returns aggregated portfolio performance metrics."""
    from sqlalchemy import func

    # Aggregate trade metrics
    result = await db.execute(
        select(
            func.count(Trade.id).label("total_trades"),
            func.sum(Trade.pnl).label("total_pnl"),
            func.count(Trade.id).filter(Trade.pnl > 0).label("winning_trades"),
        ).where(
            Trade.user_id == uuid.UUID(user_id),
            Trade.status == TradeStatus.CLOSED,
        )
    )
    row = result.one()

    total_trades = row.total_trades or 0
    total_pnl = float(row.total_pnl or 0)
    winning_trades = row.winning_trades or 0
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    # Active bots count + aggregate PnL from bots
    bots_result = await db.execute(
        select(
            func.count(Bot.id).label("active_count"),
            func.coalesce(func.sum(Bot.total_pnl), 0).label("bots_pnl"),
        ).where(
            Bot.user_id == uuid.UUID(user_id),
            Bot.status == BotStatus.ACTIVE,
        )
    )
    bots_row = bots_result.one()
    active_bots = bots_row.active_count or 0

    # Approximate equity: trades PnL + assumed starting capital
    # In a full implementation this would query an equity_snapshots table
    ASSUMED_STARTING_CAPITAL = 10000.0
    total_equity = ASSUMED_STARTING_CAPITAL + total_pnl
    total_pnl_pct = (total_pnl / ASSUMED_STARTING_CAPITAL * 100) if ASSUMED_STARTING_CAPITAL > 0 else 0

    return {
        "total_trades": total_trades,
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl_pct, 2),
        "total_equity": round(total_equity, 2),
        "win_rate": round(win_rate, 2),
        "active_bots": active_bots,
        "disclaimer": "Past performance is not indicative of future results.",
    }
