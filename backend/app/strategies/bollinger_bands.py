import pandas as pd
import pandas_ta as ta
from app.strategies.base_strategy import BaseStrategy


class BollingerBandsStrategy(BaseStrategy):
    """
    Bollinger Bands Reversal Strategy.
    
    Logic:
    - BUY when price touches/crosses below lower band (mean reversion)
    - SELL when price touches/crosses above upper band
    - Optional: Squeeze detection for breakout entries
    
    Best used in: Ranging/sideways markets
    Risk level: Medium
    """

    name = "Bollinger Bands Reversal"
    description = (
        "Uses Bollinger Bands to identify price extremes. "
        "Buys at the lower band and sells at the upper band, "
        "trading the reversion to the mean."
    )
    category = "mean_reversion"
    risk_level = "medium"

    @staticmethod
    def default_parameters() -> dict:
        return {
            "period": 20,
            "std_dev": 2.0,
            "stop_loss_pct": 0.02,
            "take_profit_pct": 0.03,
            "use_squeeze": False,
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        period = self.parameters.get("period", 20)
        std_dev = self.parameters.get("std_dev", 2.0)
        use_squeeze = self.parameters.get("use_squeeze", False)

        df = df.copy()
        bb = ta.bbands(df["close"], length=period, std=std_dev)
        df = pd.concat([df, bb], axis=1)
        df = df.dropna()

        lower_col = [c for c in df.columns if c.startswith("BBL_")]
        upper_col = [c for c in df.columns if c.startswith("BBU_")]
        mid_col = [c for c in df.columns if c.startswith("BBM_")]

        if not lower_col or not upper_col:
            df["signal"] = 0
            return df

        lower, upper = lower_col[0], upper_col[0]

        df["signal"] = 0
        # Buy when price crosses below lower band
        df.loc[(df["close"] < df[lower]) & (df["close"].shift(1) >= df[lower].shift(1)), "signal"] = 1
        # Sell when price crosses above upper band
        df.loc[(df["close"] > df[upper]) & (df["close"].shift(1) <= df[upper].shift(1)), "signal"] = -1

        return df


class BollingerBandsBreakoutStrategy(BaseStrategy):
    """
    Bollinger Bands Breakout (Squeeze) Strategy.
    Trades the breakout after a Bollinger Band squeeze.
    """

    name = "Bollinger Bands Breakout"
    description = "Identifies Bollinger Band squeezes and trades the subsequent breakout."
    category = "breakout"
    risk_level = "medium"

    @staticmethod
    def default_parameters() -> dict:
        return {
            "period": 20,
            "std_dev": 2.0,
            "squeeze_threshold": 0.1,
            "stop_loss_pct": 0.025,
            "take_profit_pct": 0.05,
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        period = self.parameters.get("period", 20)
        std_dev = self.parameters.get("std_dev", 2.0)

        df = df.copy()
        bb = ta.bbands(df["close"], length=period, std=std_dev)
        df = pd.concat([df, bb], axis=1)
        df = df.dropna()

        upper_col = [c for c in df.columns if c.startswith("BBU_")]
        lower_col = [c for c in df.columns if c.startswith("BBL_")]
        width_col = [c for c in df.columns if c.startswith("BBB_")]

        if not upper_col:
            df["signal"] = 0
            return df

        upper, lower = upper_col[0], lower_col[0]

        df["signal"] = 0
        # Breakout above upper band
        df.loc[(df["close"] > df[upper]) & (df["close"].shift(1) <= df[upper].shift(1)), "signal"] = 1
        # Breakout below lower band
        df.loc[(df["close"] < df[lower]) & (df["close"].shift(1) >= df[lower].shift(1)), "signal"] = -1
        return df
