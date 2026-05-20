import pandas as pd
import pandas_ta as ta
from app.strategies.base_strategy import BaseStrategy


class MACDMomentumStrategy(BaseStrategy):
    """
    MACD Momentum Strategy.
    
    Logic:
    - BUY when MACD line crosses above signal line (bullish crossover)
    - SELL when MACD line crosses below signal line (bearish crossover)
    - Optional: Filter with histogram above/below zero
    
    Best used in: Trending and momentum markets
    Risk level: Medium
    """

    name = "MACD Momentum"
    description = (
        "Uses the MACD indicator to identify momentum shifts. "
        "Enters long on bullish MACD crossover and exits on bearish crossover."
    )
    category = "momentum"
    risk_level = "medium"

    @staticmethod
    def default_parameters() -> dict:
        return {
            "fast": 12,
            "slow": 26,
            "signal": 9,
            "zero_filter": False,    # Only trade when histogram > 0
            "stop_loss_pct": 0.02,
            "take_profit_pct": 0.05,
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        fast = self.parameters.get("fast", 12)
        slow = self.parameters.get("slow", 26)
        signal_period = self.parameters.get("signal", 9)
        zero_filter = self.parameters.get("zero_filter", False)

        df = df.copy()
        macd = ta.macd(df["close"], fast=fast, slow=slow, signal=signal_period)
        df = pd.concat([df, macd], axis=1)
        df = df.dropna()

        macd_col = f"MACD_{fast}_{slow}_{signal_period}"
        signal_col = f"MACDs_{fast}_{slow}_{signal_period}"
        hist_col = f"MACDh_{fast}_{slow}_{signal_period}"

        if macd_col not in df.columns:
            # Fallback to first MACD columns
            macd_cols = [c for c in df.columns if c.startswith("MACD_") and not c.startswith("MACDs_") and not c.startswith("MACDh_")]
            signal_cols = [c for c in df.columns if c.startswith("MACDs_")]
            hist_cols = [c for c in df.columns if c.startswith("MACDh_")]
            if not macd_cols:
                df["signal"] = 0
                return df
            macd_col, signal_col = macd_cols[0], signal_cols[0]
            hist_col = hist_cols[0] if hist_cols else None

        df["signal"] = 0

        buy_cond = (df[macd_col] > df[signal_col]) & (df[macd_col].shift(1) <= df[signal_col].shift(1))
        sell_cond = (df[macd_col] < df[signal_col]) & (df[macd_col].shift(1) >= df[signal_col].shift(1))

        if zero_filter and hist_col and hist_col in df.columns:
            buy_cond = buy_cond & (df[hist_col] > 0)
            sell_cond = sell_cond & (df[hist_col] < 0)

        df.loc[buy_cond, "signal"] = 1
        df.loc[sell_cond, "signal"] = -1
        return df
