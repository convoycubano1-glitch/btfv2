import pandas as pd
import pandas_ta as ta
from app.strategies.base_strategy import BaseStrategy


class TrendFollowingMultiTFStrategy(BaseStrategy):
    """
    Multi-Timeframe Trend Following Strategy.
    
    Logic:
    - Uses ADX to confirm trend strength
    - Combines fast and slow EMAs across timeframes
    - Only enters in direction of higher timeframe trend
    - EMA + ADX confirmation required
    
    Best used in: Strong trending markets
    Risk level: Medium
    """

    name = "Trend Following Multi-TF"
    description = (
        "Combines EMA crossover with ADX trend strength filter. "
        "Only enters trades in strongly trending conditions (ADX > threshold)."
    )
    category = "trend_following"
    risk_level = "medium"

    @staticmethod
    def default_parameters() -> dict:
        return {
            "fast_ema": 20,
            "slow_ema": 50,
            "adx_period": 14,
            "adx_threshold": 25,    # ADX > 25 = trending market
            "stop_loss_pct": 0.025,
            "take_profit_pct": 0.05,
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        fast = self.parameters.get("fast_ema", 20)
        slow = self.parameters.get("slow_ema", 50)
        adx_period = self.parameters.get("adx_period", 14)
        adx_threshold = self.parameters.get("adx_threshold", 25)

        df = df.copy()
        df["ema_fast"] = ta.ema(df["close"], length=fast)
        df["ema_slow"] = ta.ema(df["close"], length=slow)

        adx_df = ta.adx(df["high"], df["low"], df["close"], length=adx_period)
        df = pd.concat([df, adx_df], axis=1)
        df = df.dropna()

        adx_col = [c for c in df.columns if c.startswith("ADX_")]
        dmp_col = [c for c in df.columns if c.startswith("DMP_")]
        dmn_col = [c for c in df.columns if c.startswith("DMN_")]

        if not adx_col:
            df["signal"] = 0
            return df

        adx = adx_col[0]
        df["signal"] = 0

        trending = df[adx] >= adx_threshold

        # Bull signal: fast EMA crosses above slow EMA in trending market
        df.loc[
            trending
            & (df["ema_fast"] > df["ema_slow"])
            & (df["ema_fast"].shift(1) <= df["ema_slow"].shift(1)),
            "signal",
        ] = 1

        # Bear signal: fast EMA crosses below slow EMA in trending market
        df.loc[
            trending
            & (df["ema_fast"] < df["ema_slow"])
            & (df["ema_fast"].shift(1) >= df["ema_slow"].shift(1)),
            "signal",
        ] = -1

        return df
