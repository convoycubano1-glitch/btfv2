import pandas as pd
import pandas_ta as ta
from app.strategies.base_strategy import BaseStrategy


class RSIMeanReversionStrategy(BaseStrategy):
    """
    RSI Mean Reversion Strategy.
    
    Logic:
    - BUY when RSI drops below oversold level and starts recovering
    - SELL when RSI rises above overbought level and starts declining
    
    Best used in: Range-bound / sideways markets
    Risk level: Medium
    """

    name = "RSI Mean Reversion"
    description = (
        "Uses the Relative Strength Index to identify overbought and oversold conditions. "
        "Buys when RSI is oversold (< 30) and sells when overbought (> 70)."
    )
    category = "mean_reversion"
    risk_level = "medium"

    @staticmethod
    def default_parameters() -> dict:
        return {
            "rsi_period": 14,
            "oversold": 30,
            "overbought": 70,
            "stop_loss_pct": 0.025,
            "take_profit_pct": 0.05,
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        period = self.parameters.get("rsi_period", 14)
        oversold = self.parameters.get("oversold", 30)
        overbought = self.parameters.get("overbought", 70)

        df = df.copy()
        df["rsi"] = ta.rsi(df["close"], length=period)
        df = df.dropna()

        df["signal"] = 0
        # Buy: RSI crosses above oversold from below
        df.loc[(df["rsi"] > oversold) & (df["rsi"].shift(1) <= oversold), "signal"] = 1
        # Sell: RSI crosses below overbought from above
        df.loc[(df["rsi"] < overbought) & (df["rsi"].shift(1) >= overbought), "signal"] = -1
        return df
