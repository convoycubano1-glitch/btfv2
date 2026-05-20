import pandas as pd
import pandas_ta as ta
from app.strategies.base_strategy import BaseStrategy


class VolatilityBreakoutStrategy(BaseStrategy):
    """
    Volatility Breakout Strategy.
    
    Logic:
    - Measures volatility using ATR
    - BUY when price moves > ATR multiplier above open
    - SELL when price moves > ATR multiplier below open
    - Rides explosive moves fueled by volatility expansion
    
    Best used in: High-volatility markets with clear catalysts
    Risk level: High
    """

    name = "Volatility Breakout"
    description = (
        "Uses ATR to measure volatility and enter trades when price "
        "makes a significant intrabar move. Designed to capture explosive moves."
    )
    category = "breakout"
    risk_level = "high"

    @staticmethod
    def default_parameters() -> dict:
        return {
            "atr_period": 14,
            "atr_multiplier": 1.5,    # entry when price > open + ATR * multiplier
            "stop_atr_multiplier": 1.0,
            "stop_loss_pct": 0.03,
            "take_profit_pct": 0.06,
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        atr_period = self.parameters.get("atr_period", 14)
        atr_mult = self.parameters.get("atr_multiplier", 1.5)

        df = df.copy()
        df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=atr_period)
        df = df.dropna()

        df["upper_breakout"] = df["open"] + df["atr"] * atr_mult
        df["lower_breakout"] = df["open"] - df["atr"] * atr_mult

        df["signal"] = 0
        df.loc[df["close"] > df["upper_breakout"], "signal"] = 1
        df.loc[df["close"] < df["lower_breakout"], "signal"] = -1

        return df
