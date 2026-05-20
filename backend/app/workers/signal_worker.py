import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


async def run_signal_monitor():
    """Monitors active signals, checks if TP/SL levels have been hit, updates status."""
    from app.core.database import AsyncSessionLocal
    from app.models.signal import Signal, SignalStatus
    from app.services.exchange_service import ExchangeService
    from sqlalchemy import select
    import ccxt.async_support as ccxt

    logger.info("Signal worker started.")

    while True:
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Signal).where(
                        Signal.is_published == True,
                        Signal.status == SignalStatus.ACTIVE,
                    )
                )
                active_signals = result.scalars().all()
                logger.debug(f"Monitoring {len(active_signals)} active signals")

                # Batch fetch prices for unique symbols
                symbols = list({s.symbol for s in active_signals})
                prices = {}

                exchange = ccxt.binance({"enableRateLimit": True})
                try:
                    for symbol in symbols:
                        try:
                            ticker = await exchange.fetch_ticker(symbol)
                            prices[symbol] = ticker["last"]
                        except Exception:
                            pass
                finally:
                    await exchange.close()

                # Check each signal
                for signal in active_signals:
                    price = prices.get(signal.symbol)
                    if price is None:
                        continue

                    updated = False

                    # Check TP1
                    if signal.take_profit_1 and not signal.hit_tp1:
                        if (signal.signal_type == "buy" and price >= signal.take_profit_1) or \
                           (signal.signal_type == "sell" and price <= signal.take_profit_1):
                            signal.hit_tp1 = True
                            updated = True
                            logger.info(f"Signal {signal.id}: TP1 hit at {price}")

                    # Check TP2
                    if signal.take_profit_2 and not signal.hit_tp2 and signal.hit_tp1:
                        if (signal.signal_type == "buy" and price >= signal.take_profit_2) or \
                           (signal.signal_type == "sell" and price <= signal.take_profit_2):
                            signal.hit_tp2 = True
                            updated = True

                    # Check Stop Loss
                    if signal.stop_loss and not signal.hit_stop_loss:
                        if (signal.signal_type == "buy" and price <= signal.stop_loss) or \
                           (signal.signal_type == "sell" and price >= signal.stop_loss):
                            signal.hit_stop_loss = True
                            signal.status = SignalStatus.EXPIRED
                            updated = True

                            # Calculate final PnL
                            if signal.entry_price:
                                if signal.signal_type == "buy":
                                    signal.final_pnl_pct = ((price - signal.entry_price) / signal.entry_price) * 100
                                else:
                                    signal.final_pnl_pct = ((signal.entry_price - price) / signal.entry_price) * 100

                            logger.info(f"Signal {signal.id}: Stop loss hit at {price}")

                    # Expire signals past their expiry date
                    if signal.expires_at and signal.expires_at <= datetime.now(timezone.utc):
                        signal.status = SignalStatus.EXPIRED
                        updated = True

                    if updated:
                        await db.commit()

        except Exception as e:
            logger.error(f"Signal worker error: {e}", exc_info=True)

        await asyncio.sleep(120)  # Run every 2 minutes


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_signal_monitor())
