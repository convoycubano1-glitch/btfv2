import pandas as pd
from typing import Dict, List, Optional
from app.strategies.base_strategy import BaseStrategy


class ArbitrageMonitorStrategy(BaseStrategy):
    """
    Cross-Exchange Arbitrage Monitor.
    
    Logic:
    - Monitors the same asset price across multiple exchanges
    - Alerts when spread > threshold (accounting for fees)
    - NOTE: Execution requires accounts on multiple exchanges
    - This strategy MONITORS opportunities — it does not auto-execute
    
    Best used in: High-liquidity assets on multiple exchanges
    Risk level: Low-Medium (execution risk exists)
    """

    name = "Arbitrage Monitor"
    description = (
        "Monitors price discrepancies across exchanges and alerts when "
        "profitable arbitrage opportunities arise. Accounts for trading fees."
    )
    category = "arbitrage"
    risk_level = "low"

    @staticmethod
    def default_parameters() -> dict:
        return {
            "min_profit_pct": 0.3,     # minimum profit after fees
            "taker_fee_pct": 0.1,      # typical taker fee
            "exchanges": ["binance", "kraken", "coinbase"],
            "symbols": ["BTC/USDT", "ETH/USDT"],
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Single-exchange backtesting mode: monitors simulated spread.
        In live mode, this runs as a multi-exchange monitor.
        """
        df = df.copy()
        df["signal"] = 0
        return df

    @staticmethod
    def calculate_arbitrage_opportunity(
        buy_exchange: str,
        buy_price: float,
        sell_exchange: str,
        sell_price: float,
        taker_fee_pct: float = 0.1,
        min_profit_pct: float = 0.3,
    ) -> Optional[Dict]:
        """
        Calculate if an arbitrage opportunity is profitable.
        Returns opportunity details if profitable, None otherwise.
        """
        # Total fees: buy side + sell side
        total_fee_pct = taker_fee_pct * 2

        gross_spread_pct = ((sell_price - buy_price) / buy_price) * 100
        net_profit_pct = gross_spread_pct - total_fee_pct

        if net_profit_pct < min_profit_pct:
            return None

        return {
            "buy_exchange": buy_exchange,
            "buy_price": buy_price,
            "sell_exchange": sell_exchange,
            "sell_price": sell_price,
            "gross_spread_pct": round(gross_spread_pct, 4),
            "fees_pct": round(total_fee_pct, 4),
            "net_profit_pct": round(net_profit_pct, 4),
            "is_profitable": True,
            "disclaimer": (
                "Arbitrage carries execution risk. Prices may change before orders fill. "
                "This is not financial advice."
            ),
        }

    @staticmethod
    async def scan_opportunities(
        symbols: List[str],
        exchanges: List[str],
        min_profit_pct: float = 0.3,
        taker_fee_pct: float = 0.1,
    ) -> List[Dict]:
        """Scan multiple exchanges for arbitrage opportunities."""
        from app.services.exchange_service import ExchangeService
        import asyncio

        opportunities = []

        for symbol in symbols:
            prices = {}
            tasks = [
                ExchangeService.get_public_ticker(exchange, symbol)
                for exchange in exchanges
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for exchange, result in zip(exchanges, results):
                if not isinstance(result, Exception) and "last" in result and result["last"]:
                    prices[exchange] = float(result["last"])

            # Find best buy/sell pair
            if len(prices) < 2:
                continue

            exchange_list = list(prices.items())
            for i in range(len(exchange_list)):
                for j in range(len(exchange_list)):
                    if i == j:
                        continue
                    buy_ex, buy_price = exchange_list[i]
                    sell_ex, sell_price = exchange_list[j]
                    if buy_price < sell_price:
                        opp = ArbitrageMonitorStrategy.calculate_arbitrage_opportunity(
                            buy_ex, buy_price, sell_ex, sell_price, taker_fee_pct, min_profit_pct
                        )
                        if opp:
                            opp["symbol"] = symbol
                            opportunities.append(opp)

        return opportunities
