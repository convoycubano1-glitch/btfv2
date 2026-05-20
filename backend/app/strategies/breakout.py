import pandas as pd
import pandas_ta as ta
from app.strategies.base_strategy import BaseStrategy


class BreakoutStrategy(BaseStrategy):
    """
    Support/Resistance Breakout Strategy.
    
    Logic:
    - BUY when price breaks above N-period high (resistance breakout)
    - SELL when price breaks below N-period low (support breakdown)
    - Uses ATR for dynamic stop placement
    
    Best used in: Trending markets with clear structure
    Risk level: Medium-High
    """

    name = "Breakout Strategy"
    description = (
        "Identifies key support and resistance levels and enters trades "
        "on confirmed breakouts. Uses ATR to filter out false breakouts."
    )
    category = "breakout"
    risk_level = "medium"

    @staticmethod
    def default_parameters() -> dict:
        return {
            "period": 20,
            "atr_period": 14,
            "atr_filter": 1.0,     # price must move > atr_filter * ATR above resistance
            "stop_loss_pct": 0.02,
            "take_profit_pct": 0.06,
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        period = self.parameters.get("period", 20)
        atr_period = self.parameters.get("atr_period", 14)
        atr_filter = self.parameters.get("atr_filter", 1.0)

        df = df.copy()
        df["highest_high"] = df["high"].rolling(period).max()
        df["lowest_low"] = df["low"].rolling(period).min()
        df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=atr_period)
        df = df.dropna()

        df["signal"] = 0
        # Bullish breakout: close > previous N-period high + ATR filter
        df.loc[
            df["close"] > (df["highest_high"].shift(1) + df["atr"] * atr_filter),
            "signal",
        ] = 1
        # Bearish breakdown: close < previous N-period low
        df.loc[
            df["close"] < (df["lowest_low"].shift(1) - df["atr"] * atr_filter),
            "signal",
        ] = -1
        return df
