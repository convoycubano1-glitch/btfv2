import asyncio
import logging
from datetime import datetime, timezone
import pandas as pd

logger = logging.getLogger(__name__)


async def run_all_active_bots():
    """Main bot worker loop — executes all active bots on schedule."""
    from app.core.database import AsyncSessionLocal
    from app.models.bot import Bot, BotStatus, TradingMode
    from app.models.user import User
    from app.models.exchange import ExchangeConnection
    from sqlalchemy import select
    from app.core.security import decrypt_api_key

    logger.info("Bot worker started.")

    while True:
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Bot).where(Bot.status == BotStatus.ACTIVE)
                )
                active_bots = result.scalars().all()
                logger.info(f"Running {len(active_bots)} active bots...")

                for bot in active_bots:
                    try:
                        await execute_bot(bot, db)
                    except Exception as e:
                        logger.error(f"Bot {bot.id} error: {e}", exc_info=True)
                        bot.status = BotStatus.ERROR
                        bot.error_message = str(e)
                        await db.commit()

        except Exception as e:
            logger.error(f"Bot worker cycle error: {e}", exc_info=True)

        await asyncio.sleep(60)  # Run every minute


async def execute_bot(bot, db):
    """Execute a single bot iteration."""
    from app.models.exchange import ExchangeConnection
    from app.models.trade import Trade, TradeSide, TradeMode, TradeStatus
    from app.models.user import User
    from app.services.exchange_service import ExchangeService
    from app.services.risk_manager import RiskManager
    from app.strategies.registry import get_strategy
    from app.core.security import decrypt_api_key
    from app.core.websocket_manager import ws_manager
    from sqlalchemy import select
    import json

    logger.debug(f"Executing bot {bot.name} [{bot.mode}]")

    # Check user emergency stop
    user_result = await db.execute(select(User).where(User.id == bot.user_id))
    user = user_result.scalar_one_or_none()
    if user and user.emergency_stop_active:
        bot.status = "paused"
        await db.commit()
        return

    # Get strategy
    strategy = get_strategy(
        bot.strategy.strategy_type.value if bot.strategy else "ema_crossover",
        bot.parameters,
    )

    if bot.mode == TradingMode.LIVE:
        if not bot.exchange_connection_id:
            return

        conn_result = await db.execute(
            select(ExchangeConnection).where(ExchangeConnection.id == bot.exchange_connection_id)
        )
        conn = conn_result.scalar_one_or_none()
        if not conn:
            return

        exchange_service = ExchangeService(
            exchange_id=conn.exchange_id,
            api_key=decrypt_api_key(conn.encrypted_api_key),
            api_secret=decrypt_api_key(conn.encrypted_api_secret),
            passphrase=decrypt_api_key(conn.encrypted_passphrase) if conn.encrypted_passphrase else None,
            testnet=conn.is_testnet,
        )
    else:
        exchange_service = None

    # Fetch OHLCV data
    if exchange_service:
        candles = await exchange_service.fetch_ohlcv(bot.symbol, bot.timeframe, limit=200)
    else:
        # Paper trading: use public data
        from app.services.exchange_service import ExchangeService as ES
        import ccxt.async_support as ccxt
        exchange = ccxt.binance({"enableRateLimit": True})
        try:
            raw = await exchange.fetch_ohlcv(bot.symbol, bot.timeframe, limit=200)
            candles = [{"timestamp": c[0], "open": c[1], "high": c[2], "low": c[3], "close": c[4], "volume": c[5]} for c in raw]
        finally:
            await exchange.close()

    if not candles:
        return

    df = pd.DataFrame(candles)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df = df.set_index("timestamp")

    # Generate signal
    signal = strategy.get_entry_signal(df)
    current_price = float(df["close"].iloc[-1])

    # Open trades count check
    from sqlalchemy import func
    open_trades_count = await db.scalar(
        db.query(func.count(Trade.id)).where(
            Trade.bot_id == bot.id,
            Trade.status == TradeStatus.OPEN,
        )
    ) or 0

    if signal == 1 and open_trades_count < bot.max_open_trades:
        # Risk check
        risk_check = RiskManager.validate_bot_risk({
            "max_position_size_pct": bot.max_position_size_pct,
            "stop_loss_pct": bot.stop_loss_pct,
            "max_daily_loss_pct": bot.max_daily_loss_pct,
            "max_open_trades": bot.max_open_trades,
        })
        if not risk_check["passed"]:
            logger.warning(f"Bot {bot.name} failed risk check: {risk_check['reason']}")
            return

        # Place order
        trade = Trade(
            user_id=bot.user_id,
            bot_id=bot.id,
            exchange_connection_id=bot.exchange_connection_id,
            symbol=bot.symbol,
            side=TradeSide.BUY,
            mode=TradeMode.LIVE if bot.mode == TradingMode.LIVE else TradeMode.PAPER,
            status=TradeStatus.OPEN,
            entry_price=current_price,
            quantity=0.001,  # Would calculate based on position size
            stop_loss=current_price * (1 - bot.stop_loss_pct),
            take_profit=current_price * (1 + bot.take_profit_pct),
            strategy_name=bot.strategy.strategy_type.value if bot.strategy else "unknown",
            opened_at=datetime.now(timezone.utc),
        )
        db.add(trade)
        bot.total_trades += 1
        bot.last_run_at = datetime.now(timezone.utc)
        await db.commit()

        logger.info(f"Bot {bot.name}: BUY {bot.symbol} @ {current_price}")

        # Notify via WebSocket
        await ws_manager.send_to_user(str(bot.user_id), {
            "type": "trade_opened",
            "bot_name": bot.name,
            "symbol": bot.symbol,
            "price": current_price,
            "mode": bot.mode.value,
        })

    bot.last_run_at = datetime.now(timezone.utc)
    await db.commit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_all_active_bots())
