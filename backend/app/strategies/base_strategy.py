from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd
import pandas_ta as ta


class BaseStrategy(ABC):
    """
    Abstract base class for all TradeBotHub Pro strategies.
    Each strategy receives a DataFrame of OHLCV data and returns signals.
    """

    name: str = "BaseStrategy"
    description: str = ""
    category: str = "general"
    risk_level: str = "medium"

    def __init__(self, parameters: dict = {}):
        self.parameters = {**self.default_parameters(), **parameters}

    @staticmethod
    def default_parameters() -> dict:
        return {}

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add indicator columns and a 'signal' column to df.
        signal: 1 = buy, -1 = sell, 0 = hold
        Returns the modified DataFrame.
        """
        pass

    def get_entry_signal(self, df: pd.DataFrame) -> int:
        """Returns the latest signal (-1, 0, 1)."""
        df = self.generate_signals(df)
        if df.empty:
            return 0
        return int(df["signal"].iloc[-1])

    def validate_parameters(self) -> tuple[bool, str]:
        return True, ""
