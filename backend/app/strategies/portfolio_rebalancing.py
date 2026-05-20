import pandas as pd
from typing import Dict, List
from app.strategies.base_strategy import BaseStrategy


class PortfolioRebalancingStrategy(BaseStrategy):
    """
    Portfolio Rebalancing Strategy.
    
    Logic:
    - Maintains target allocation percentages across multiple assets
    - Rebalances when any asset drifts beyond a threshold
    - Systematic, emotion-free portfolio management
    
    Best used in: Multi-asset portfolios
    Risk level: Low
    """

    name = "Portfolio Rebalancing"
    description = (
        "Automatically rebalances a multi-asset portfolio to target allocations. "
        "Sells overweight assets and buys underweight ones."
    )
    category = "portfolio"
    risk_level = "low"

    @staticmethod
    def default_parameters() -> dict:
        return {
            "target_allocations": {
                "BTC/USDT": 0.40,
                "ETH/USDT": 0.30,
                "BNB/USDT": 0.15,
                "SOL/USDT": 0.15,
            },
            "rebalance_threshold_pct": 5.0,   # rebalance if drift > 5%
            "rebalance_frequency": "weekly",   # or "threshold"
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        For single-asset backtesting, simplified to buy-and-hold with periodic rebalance.
        Real implementation uses multi-asset portfolio manager.
        """
        df = df.copy()
        df["signal"] = 0
        # Buy on first bar, hold — rebalancing is handled by portfolio manager
        if len(df) > 0:
            df.iloc[0, df.columns.get_loc("signal")] = 1
        return df

    @staticmethod
    def calculate_rebalance_trades(
        current_balances: Dict[str, float],
        target_allocations: Dict[str, float],
        prices: Dict[str, float],
        threshold_pct: float = 5.0,
    ) -> List[Dict]:
        """
        Calculate required trades to rebalance a portfolio.
        
        Returns list of {"symbol": str, "action": "buy"|"sell", "amount_usd": float}
        """
        total_value = sum(
            current_balances.get(sym, 0) * prices.get(sym, 0)
            for sym in target_allocations
        )
        if total_value == 0:
            return []

        trades = []
        for symbol, target_pct in target_allocations.items():
            current_value = current_balances.get(symbol, 0) * prices.get(symbol, 1)
            current_pct = (current_value / total_value) * 100
            target_value = total_value * target_pct

            drift = abs(current_pct - target_pct * 100)
            if drift >= threshold_pct:
                diff_usd = target_value - current_value
                trades.append({
                    "symbol": symbol,
                    "action": "buy" if diff_usd > 0 else "sell",
                    "amount_usd": abs(diff_usd),
                    "current_pct": round(current_pct, 2),
                    "target_pct": round(target_pct * 100, 2),
                    "drift_pct": round(drift, 2),
                })
        return trades
