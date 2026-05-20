import pandas as pd
from typing import List
from app.strategies.base_strategy import BaseStrategy


class SmartDCAStrategy(BaseStrategy):
    """
    Smart Dollar-Cost Averaging (DCA) Strategy.
    
    Logic:
    - Places buy orders at regular intervals or on dips
    - Dynamically sizes entries based on price drop magnitude
    - Exits when total position reaches target profit
    
    Best used in: Long-term accumulation in bull/bear markets
    Risk level: Low-Medium
    """

    name = "Smart DCA"
    description = (
        "Dollar-cost averaging with dynamic position sizing. "
        "Increases position size on larger dips and exits at profit target."
    )
    category = "accumulation"
    risk_level = "low"

    @staticmethod
    def default_parameters() -> dict:
        return {
            "base_order_size_pct": 0.05,    # % of portfolio for base order
            "safety_order_size_pct": 0.10,  # % for subsequent orders
            "safety_order_deviation": 2.0,  # % price drop to trigger safety order
            "safety_order_volume_scale": 1.5,  # multiply each safety order
            "max_safety_orders": 5,
            "take_profit_pct": 3.0,  # target profit %
            "cooldown_bars": 10,     # bars to wait before new cycle
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        DCA logic: buy at regular intervals / dips, sell at profit target.
        Simplified signal generation for backtesting compatibility.
        """
        df = df.copy()
        deviation = self.parameters.get("safety_order_deviation", 2.0) / 100
        take_profit = self.parameters.get("take_profit_pct", 3.0) / 100
        max_orders = self.parameters.get("max_safety_orders", 5)
        cooldown = self.parameters.get("cooldown_bars", 10)

        df["signal"] = 0
        in_position = False
        entry_price = 0.0
        orders_count = 0
        last_exit_bar = -cooldown

        for i in range(1, len(df)):
            price = df["close"].iloc[i]

            if not in_position:
                if i - last_exit_bar >= cooldown:
                    df.iloc[i, df.columns.get_loc("signal")] = 1
                    entry_price = price
                    in_position = True
                    orders_count = 1

            elif in_position:
                avg_price = entry_price  # simplified: use first entry
                pnl_pct = (price - avg_price) / avg_price

                # Take profit
                if pnl_pct >= take_profit:
                    df.iloc[i, df.columns.get_loc("signal")] = -1
                    in_position = False
                    orders_count = 0
                    last_exit_bar = i

                # Safety order (additional DCA buy on dip)
                elif pnl_pct <= -deviation and orders_count < max_orders:
                    df.iloc[i, df.columns.get_loc("signal")] = 1  # additional buy
                    orders_count += 1
                    entry_price = (entry_price + price) / 2  # update avg

        return df


class DCAOrder:
    """Represents a single DCA order in a cycle."""
    def __init__(self, order_number: int, price: float, size: float):
        self.order_number = order_number
        self.price = price
        self.size = size
        self.total_cost = price * size
