import pandas as pd
import pandas_ta as ta
from app.strategies.base_strategy import BaseStrategy


class SmartScalpingStrategy(BaseStrategy):
    """
    Smart Scalping Strategy.
    
    Logic:
    - Uses fast EMA + RSI combination for quick entries
    - Targets small profits (0.3-1%) with tight stop losses
    - Filters noise with ATR — only enters on sufficient volatility
    - Requires RSI and price alignment for confirmation
    
    Best used in: High-liquidity pairs (BTC, ETH) on lower timeframes (1m-15m)
    Risk level: High (due to frequency and leverage sensitivity)
    """

    name = "Smart Scalping"
    description = (
        "High-frequency short-term strategy combining EMA, RSI, and ATR. "
        "Targets small but frequent profits with strict risk management."
    )
    category = "scalping"
    risk_level = "high"

    @staticmethod
    def default_parameters() -> dict:
        return {
            "ema_period": 8,
            "rsi_period": 7,
            "rsi_oversold": 35,
            "rsi_overbought": 65,
            "atr_period": 7,
            "min_atr_pct": 0.001,   # ignore entries if ATR < 0.1% of price
            "stop_loss_pct": 0.005,  # 0.5% stop loss
            "take_profit_pct": 0.01, # 1% take profit
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        ema_period = self.parameters.get("ema_period", 8)
        rsi_period = self.parameters.get("rsi_period", 7)
        rsi_oversold = self.parameters.get("rsi_oversold", 35)
        rsi_overbought = self.parameters.get("rsi_overbought", 65)
        atr_period = self.parameters.get("atr_period", 7)
        min_atr_pct = self.parameters.get("min_atr_pct", 0.001)

        df = df.copy()
        df["ema"] = ta.ema(df["close"], length=ema_period)
        df["rsi"] = ta.rsi(df["close"], length=rsi_period)
        df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=atr_period)
        df = df.dropna()

        # ATR filter: only trade when volatility is sufficient
        df["atr_pct"] = df["atr"] / df["close"]
        sufficient_vol = df["atr_pct"] >= min_atr_pct

        df["signal"] = 0

        # Long: price above EMA + RSI oversold recovery + sufficient volatility
        df.loc[
            sufficient_vol
            & (df["close"] > df["ema"])
            & (df["rsi"] > rsi_oversold)
            & (df["rsi"].shift(1) <= rsi_oversold),
            "signal",
        ] = 1

        # Short: price below EMA + RSI overbought reversal + sufficient volatility
        df.loc[
            sufficient_vol
            & (df["close"] < df["ema"])
            & (df["rsi"] < rsi_overbought)
            & (df["rsi"].shift(1) >= rsi_overbought),
            "signal",
        ] = -1

        return df
