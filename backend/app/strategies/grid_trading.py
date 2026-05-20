import pandas as pd
import numpy as np
from typing import List, Dict
from app.strategies.base_strategy import BaseStrategy


class GridTradingStrategy(BaseStrategy):
    """
    Controlled Grid Trading Strategy.
    
    Logic:
    - Creates a grid of buy and sell orders at fixed price intervals
    - Buys when price falls to grid level, sells when it rises
    - Profits from price oscillation within range
    
    Best used in: Sideways/ranging markets
    Risk level: Medium (controlled with upper/lower boundaries)
    """

    name = "Grid Trading"
    description = (
        "Places a grid of buy and sell orders at equal price intervals. "
        "Profits from price oscillation within a defined range. "
        "Risk-controlled with upper/lower boundaries."
    )
    category = "grid"
    risk_level = "medium"

    @staticmethod
    def default_parameters() -> dict:
        return {
            "grid_levels": 10,        # number of grid lines
            "grid_spacing_pct": 1.0,  # % spacing between grid levels
            "upper_range_pct": 10.0,  # % above current price for upper boundary
            "lower_range_pct": 10.0,  # % below current price for lower boundary
            "order_size_pct": 0.01,   # % of portfolio per grid order
            "stop_loss_pct": 0.15,    # overall grid stop loss
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Simplified grid signal generation for backtesting.
        In live trading this would maintain actual order book entries.
        """
        df = df.copy()
        spacing = self.parameters.get("grid_spacing_pct", 1.0) / 100
        stop_loss = self.parameters.get("stop_loss_pct", 0.15)

        df["signal"] = 0
        grid_center = None
        position_price = 0.0
        in_position = False

        for i in range(1, len(df)):
            price = df["close"].iloc[i]

            if not in_position:
                # Initialize grid around first entry
                grid_center = price
                df.iloc[i, df.columns.get_loc("signal")] = 1
                position_price = price
                in_position = True

            elif in_position and grid_center:
                pnl_pct = (price - position_price) / position_price

                # Hard stop loss
                if pnl_pct <= -stop_loss:
                    df.iloc[i, df.columns.get_loc("signal")] = -1
                    in_position = False
                    grid_center = None
                    continue

                # Sell at grid level above
                if price >= grid_center * (1 + spacing):
                    df.iloc[i, df.columns.get_loc("signal")] = -1
                    grid_center = price
                    in_position = False

                # Buy at grid level below
                elif price <= grid_center * (1 - spacing):
                    df.iloc[i, df.columns.get_loc("signal")] = 1
                    grid_center = price
                    position_price = (position_price + price) / 2

        return df

    @staticmethod
    def calculate_grid_levels(
        current_price: float,
        grid_levels: int,
        spacing_pct: float,
        upper_range_pct: float,
        lower_range_pct: float,
    ) -> Dict[str, List[float]]:
        """Calculate buy and sell grid price levels."""
        buy_levels = []
        sell_levels = []

        for i in range(1, grid_levels + 1):
            buy_price = current_price * (1 - (spacing_pct / 100) * i)
            sell_price = current_price * (1 + (spacing_pct / 100) * i)

            lower_bound = current_price * (1 - lower_range_pct / 100)
            upper_bound = current_price * (1 + upper_range_pct / 100)

            if buy_price >= lower_bound:
                buy_levels.append(round(buy_price, 8))
            if sell_price <= upper_bound:
                sell_levels.append(round(sell_price, 8))

        return {
            "buy_levels": sorted(buy_levels, reverse=True),
            "sell_levels": sorted(sell_levels),
            "upper_boundary": round(current_price * (1 + upper_range_pct / 100), 8),
            "lower_boundary": round(current_price * (1 - lower_range_pct / 100), 8),
        }
