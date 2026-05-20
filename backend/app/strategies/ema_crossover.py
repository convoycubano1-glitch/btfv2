import pandas as pd
import pandas_ta as ta
from app.strategies.base_strategy import BaseStrategy


class EMACrossoverStrategy(BaseStrategy):
    """
    EMA Crossover Strategy.
    
    Logic:
    - BUY when fast EMA crosses above slow EMA (golden cross)
    - SELL when fast EMA crosses below slow EMA (death cross)
    
    Best used in: Trending markets
    Risk level: Low-Medium
    """

    name = "EMA Crossover"
    description = (
        "Generates buy signals when the fast EMA crosses above the slow EMA "
        "and sell signals when it crosses below. Works best in trending markets."
    )
    category = "trend_following"
    risk_level = "low"

    @staticmethod
    def default_parameters() -> dict:
        return {
            "fast_ema": 9,
            "slow_ema": 21,
            "stop_loss_pct": 0.02,
            "take_profit_pct": 0.04,
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        fast = self.parameters.get("fast_ema", 9)
        slow = self.parameters.get("slow_ema", 21)

        df = df.copy()
        df["ema_fast"] = ta.ema(df["close"], length=fast)
        df["ema_slow"] = ta.ema(df["close"], length=slow)
        df = df.dropna()

        df["signal"] = 0
        df.loc[
            (df["ema_fast"] > df["ema_slow"]) & (df["ema_fast"].shift(1) <= df["ema_slow"].shift(1)),
            "signal",
        ] = 1
        df.loc[
            (df["ema_fast"] < df["ema_slow"]) & (df["ema_fast"].shift(1) >= df["ema_slow"].shift(1)),
            "signal",
        ] = -1
        return df
