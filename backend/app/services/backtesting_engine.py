import pandas as pd
import numpy as np
import pandas_ta as ta
from datetime import datetime, timezone
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def run_backtest(backtest_id: str):
    """
    Background task to run a backtest.
    Fetches data via CCXT and runs the selected strategy.
    """
    import asyncio
    from app.core.database import AsyncSessionLocal
    from app.models.backtest import Backtest, BacktestStatus
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Backtest).where(Backtest.id == backtest_id))
        backtest = result.scalar_one_or_none()
        if not backtest:
            return

        backtest.status = BacktestStatus.RUNNING
        await db.commit()

        start_time = datetime.now(timezone.utc)
        try:
            engine = BacktestEngine(
                symbol=backtest.symbol,
                timeframe=backtest.timeframe,
                strategy_type=backtest.strategy_type,
                parameters=backtest.parameters,
                start_date=backtest.start_date,
                end_date=backtest.end_date,
                initial_capital=backtest.initial_capital,
            )
            results = await engine.run()

            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()

            # Update backtest record
            backtest.status = BacktestStatus.COMPLETED
            backtest.final_equity = results["final_equity"]
            backtest.total_return_pct = results["total_return_pct"]
            backtest.annualized_return_pct = results["annualized_return_pct"]
            backtest.max_drawdown_pct = results["max_drawdown_pct"]
            backtest.sharpe_ratio = results["sharpe_ratio"]
            backtest.sortino_ratio = results["sortino_ratio"]
            backtest.win_rate_pct = results["win_rate_pct"]
            backtest.total_trades = results["total_trades"]
            backtest.winning_trades = results["winning_trades"]
            backtest.losing_trades = results["losing_trades"]
            backtest.avg_win_pct = results["avg_win_pct"]
            backtest.avg_loss_pct = results["avg_loss_pct"]
            backtest.profit_factor = results["profit_factor"]
            backtest.expectancy = results["expectancy"]
            backtest.trade_log = results["trade_log"]
            backtest.equity_curve = results["equity_curve"]
            backtest.duration_seconds = duration
            backtest.completed_at = end_time

        except Exception as e:
            logger.error(f"Backtest {backtest_id} failed: {e}", exc_info=True)
            backtest.status = BacktestStatus.FAILED
            backtest.error_message = str(e)

        await db.commit()


class BacktestEngine:
    """
    Vectorized backtesting engine using pandas.
    Simulates strategy on historical OHLCV data.
    """

    def __init__(
        self,
        symbol: str,
        timeframe: str,
        strategy_type: str,
        parameters: dict,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 10000.0,
    ):
        self.symbol = symbol
        self.timeframe = timeframe
        self.strategy_type = strategy_type
        self.parameters = parameters
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital

    async def _fetch_data(self) -> pd.DataFrame:
        """Fetch OHLCV data from exchange (Binance by default for backtesting)."""
        import ccxt.async_support as ccxt
        exchange = ccxt.binance({"enableRateLimit": True})
        try:
            since = int(self.start_date.timestamp() * 1000)
            all_candles = []
            while True:
                candles = await exchange.fetch_ohlcv(
                    self.symbol, self.timeframe, since=since, limit=1000
                )
                if not candles:
                    break
                all_candles.extend(candles)
                last_ts = candles[-1][0]
                end_ts = int(self.end_date.timestamp() * 1000)
                if last_ts >= end_ts or len(candles) < 1000:
                    break
                since = last_ts + 1
        finally:
            await exchange.close()

        if not all_candles:
            raise ValueError(f"No data found for {self.symbol} {self.timeframe}")

        df = pd.DataFrame(
            all_candles, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df = df.set_index("timestamp")
        end_ts = pd.Timestamp(self.end_date, tz="UTC")
        df = df[df.index <= end_ts]
        return df

    async def run(self) -> dict[str, Any]:
        """Run the full backtest and return performance metrics."""
        df = await self._fetch_data()
        df = self._add_indicators(df)
        df = self._generate_signals(df)
        return self._calculate_metrics(df)

    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators based on strategy type."""
        params = self.parameters

        if self.strategy_type == "ema_crossover":
            fast = params.get("fast_ema", 9)
            slow = params.get("slow_ema", 21)
            df["ema_fast"] = ta.ema(df["close"], length=fast)
            df["ema_slow"] = ta.ema(df["close"], length=slow)

        elif self.strategy_type == "rsi_mean_reversion":
            period = params.get("rsi_period", 14)
            df["rsi"] = ta.rsi(df["close"], length=period)

        elif self.strategy_type == "macd_momentum":
            fast = params.get("fast", 12)
            slow = params.get("slow", 26)
            signal = params.get("signal", 9)
            macd = ta.macd(df["close"], fast=fast, slow=slow, signal=signal)
            df = pd.concat([df, macd], axis=1)

        elif self.strategy_type == "bollinger_bands":
            period = params.get("period", 20)
            std = params.get("std_dev", 2.0)
            bb = ta.bbands(df["close"], length=period, std=std)
            df = pd.concat([df, bb], axis=1)

        elif self.strategy_type in ("breakout", "volatility_breakout"):
            period = params.get("period", 20)
            df["highest_high"] = df["high"].rolling(period).max()
            df["lowest_low"] = df["low"].rolling(period).min()
            df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=14)

        elif self.strategy_type == "trend_following":
            df["ema_fast"] = ta.ema(df["close"], length=params.get("fast_ema", 20))
            df["ema_slow"] = ta.ema(df["close"], length=params.get("slow_ema", 50))
            df["adx"] = ta.adx(df["high"], df["low"], df["close"], length=14)["ADX_14"]

        elif self.strategy_type == "smart_scalping":
            df["ema"] = ta.ema(df["close"], length=params.get("ema", 8))
            df["rsi"] = ta.rsi(df["close"], length=params.get("rsi_period", 7))
            df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=7)

        return df.dropna()

    def _generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate BUY/SELL signals (1 = buy, -1 = sell, 0 = hold)."""
        df["signal"] = 0
        params = self.parameters

        if self.strategy_type == "ema_crossover":
            df.loc[
                (df["ema_fast"] > df["ema_slow"]) & (df["ema_fast"].shift(1) <= df["ema_slow"].shift(1)),
                "signal",
            ] = 1
            df.loc[
                (df["ema_fast"] < df["ema_slow"]) & (df["ema_fast"].shift(1) >= df["ema_slow"].shift(1)),
                "signal",
            ] = -1

        elif self.strategy_type == "rsi_mean_reversion":
            oversold = params.get("oversold", 30)
            overbought = params.get("overbought", 70)
            df.loc[(df["rsi"] < oversold) & (df["rsi"].shift(1) >= oversold), "signal"] = 1
            df.loc[(df["rsi"] > overbought) & (df["rsi"].shift(1) <= overbought), "signal"] = -1

        elif self.strategy_type == "macd_momentum":
            macd_col = [c for c in df.columns if c.startswith("MACD_")]
            signal_col = [c for c in df.columns if c.startswith("MACDs_")]
            if macd_col and signal_col:
                df.loc[
                    (df[macd_col[0]] > df[signal_col[0]]) & (df[macd_col[0]].shift(1) <= df[signal_col[0]].shift(1)),
                    "signal",
                ] = 1
                df.loc[
                    (df[macd_col[0]] < df[signal_col[0]]) & (df[macd_col[0]].shift(1) >= df[signal_col[0]].shift(1)),
                    "signal",
                ] = -1

        elif self.strategy_type == "bollinger_bands":
            lower_col = [c for c in df.columns if c.startswith("BBL_")]
            upper_col = [c for c in df.columns if c.startswith("BBU_")]
            if lower_col and upper_col:
                df.loc[df["close"] < df[lower_col[0]], "signal"] = 1
                df.loc[df["close"] > df[upper_col[0]], "signal"] = -1

        elif self.strategy_type == "breakout":
            df.loc[df["close"] > df["highest_high"].shift(1), "signal"] = 1
            df.loc[df["close"] < df["lowest_low"].shift(1), "signal"] = -1

        return df

    def _calculate_metrics(self, df: pd.DataFrame) -> dict[str, Any]:
        """Simulate trades and calculate performance metrics."""
        capital = self.initial_capital
        position = 0.0
        entry_price = 0.0
        trades = []
        equity_curve = []

        stop_loss_pct = self.parameters.get("stop_loss_pct", 0.02)
        take_profit_pct = self.parameters.get("take_profit_pct", 0.04)

        for idx, row in df.iterrows():
            price = row["close"]

            # Check stop loss / take profit
            if position > 0:
                pnl_pct = (price - entry_price) / entry_price
                if pnl_pct <= -stop_loss_pct or pnl_pct >= take_profit_pct:
                    pnl = position * price - position * entry_price
                    capital += position * price
                    trades.append({
                        "entry": entry_price,
                        "exit": price,
                        "pnl": round(pnl, 2),
                        "pnl_pct": round(pnl_pct * 100, 2),
                        "reason": "stop_loss" if pnl_pct <= -stop_loss_pct else "take_profit",
                        "close_time": str(idx),
                    })
                    position = 0.0
                    entry_price = 0.0

            # Entry signal
            if row["signal"] == 1 and position == 0 and capital > 0:
                position_size = capital * 0.95  # Use 95% of capital
                position = position_size / price
                entry_price = price
                capital -= position_size

            elif row["signal"] == -1 and position > 0:
                pnl = position * price - position * entry_price
                pnl_pct = (price - entry_price) / entry_price
                capital += position * price
                trades.append({
                    "entry": entry_price,
                    "exit": price,
                    "pnl": round(pnl, 2),
                    "pnl_pct": round(pnl_pct * 100, 2),
                    "reason": "signal",
                    "close_time": str(idx),
                })
                position = 0.0
                entry_price = 0.0

            current_equity = capital + (position * price if position > 0 else 0)
            equity_curve.append({"date": str(idx), "equity": round(current_equity, 2)})

        # Final metrics
        final_equity = capital + (position * df["close"].iloc[-1] if position > 0 else 0)
        total_return_pct = (final_equity - self.initial_capital) / self.initial_capital * 100

        # Annualize
        days = (self.end_date - self.start_date).days or 1
        annualized = ((1 + total_return_pct / 100) ** (365 / days) - 1) * 100

        winning = [t for t in trades if t["pnl"] > 0]
        losing = [t for t in trades if t["pnl"] <= 0]

        win_rate = len(winning) / len(trades) * 100 if trades else 0
        avg_win = np.mean([t["pnl_pct"] for t in winning]) if winning else 0
        avg_loss = np.mean([t["pnl_pct"] for t in losing]) if losing else 0

        gross_profit = sum(t["pnl"] for t in winning)
        gross_loss = abs(sum(t["pnl"] for t in losing))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Max drawdown
        equities = [e["equity"] for e in equity_curve]
        max_dd = 0.0
        peak = self.initial_capital
        for eq in equities:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak * 100
            if dd > max_dd:
                max_dd = dd

        # Sharpe ratio (simplified)
        returns = pd.Series(equities).pct_change().dropna()
        sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        downside = returns[returns < 0]
        sortino = (returns.mean() / downside.std() * np.sqrt(252)) if len(downside) > 0 and downside.std() > 0 else 0

        expectancy = (win_rate / 100 * avg_win) + ((1 - win_rate / 100) * avg_loss)

        return {
            "final_equity": round(final_equity, 2),
            "total_return_pct": round(total_return_pct, 2),
            "annualized_return_pct": round(annualized, 2),
            "max_drawdown_pct": round(max_dd, 2),
            "sharpe_ratio": round(float(sharpe), 3),
            "sortino_ratio": round(float(sortino), 3),
            "win_rate_pct": round(win_rate, 2),
            "total_trades": len(trades),
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "avg_win_pct": round(float(avg_win), 2),
            "avg_loss_pct": round(float(avg_loss), 2),
            "profit_factor": round(profit_factor, 2),
            "expectancy": round(float(expectancy), 2),
            "trade_log": trades[-200:],   # last 200 trades
            "equity_curve": equity_curve[-1000:],  # last 1000 points
        }
