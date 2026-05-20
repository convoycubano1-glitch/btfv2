from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.trade import Trade, TradeStatus, TradeMode
from app.models.bot import Bot
import uuid

router = APIRouter()


@router.get("/performance")
async def get_performance_report(
    period: str = "30d",
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    period_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = period_map.get(period, 30)
    since = now - timedelta(days=days)

    result = await db.execute(
        select(Trade).where(
            Trade.user_id == uuid.UUID(user_id),
            Trade.status == TradeStatus.CLOSED,
            Trade.created_at >= since,
        ).order_by(Trade.closed_at)
    )
    trades = result.scalars().all()

    if not trades:
        return {"message": "No trades in this period", "period": period, "trades": []}

    total_pnl = sum(t.pnl or 0 for t in trades)
    winning = [t for t in trades if (t.pnl or 0) > 0]
    losing = [t for t in trades if (t.pnl or 0) <= 0]
    win_rate = len(winning) / len(trades) * 100

    avg_win = sum(t.pnl for t in winning) / len(winning) if winning else 0
    avg_loss = sum(t.pnl for t in losing) / len(losing) if losing else 0
    profit_factor = abs(sum(t.pnl for t in winning) / sum(t.pnl for t in losing)) if losing and sum(t.pnl for t in losing) != 0 else 0

    # Equity curve
    equity = 10000.0
    equity_curve = []
    for t in trades:
        equity += (t.pnl or 0)
        equity_curve.append({
            "date": t.closed_at.isoformat() if t.closed_at else None,
            "equity": round(equity, 2),
            "pnl": round(t.pnl or 0, 2),
        })

    return {
        "period": period,
        "total_trades": len(trades),
        "winning_trades": len(winning),
        "losing_trades": len(losing),
        "win_rate": round(win_rate, 2),
        "total_pnl": round(total_pnl, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "profit_factor": round(profit_factor, 2),
        "equity_curve": equity_curve,
        "disclaimer": "Past performance is not indicative of future results.",
    }


@router.get("/trades-by-strategy")
async def trades_by_strategy(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            Trade.strategy_name,
            func.count(Trade.id).label("count"),
            func.sum(Trade.pnl).label("total_pnl"),
        ).where(
            Trade.user_id == uuid.UUID(user_id),
            Trade.status == TradeStatus.CLOSED,
        ).group_by(Trade.strategy_name)
    )
    rows = result.all()
    return [
        {"strategy": r.strategy_name, "trades": r.count, "total_pnl": round(float(r.total_pnl or 0), 2)}
        for r in rows
    ]
