"""
Strategy Registry — maps strategy type keys to metadata and classes.
Used by the bot engine, backtesting, and API strategy list endpoint.
"""

from app.strategies.ema_crossover import EMACrossoverStrategy
from app.strategies.rsi_mean_reversion import RSIMeanReversionStrategy
from app.strategies.macd_momentum import MACDMomentumStrategy
from app.strategies.bollinger_bands import BollingerBandsStrategy
from app.strategies.breakout import BreakoutStrategy
from app.strategies.dca import SmartDCAStrategy
from app.strategies.grid_trading import GridTradingStrategy
from app.strategies.volatility_breakout import VolatilityBreakoutStrategy
from app.strategies.portfolio_rebalancing import PortfolioRebalancingStrategy
from app.strategies.arbitrage_monitor import ArbitrageMonitorStrategy
from app.strategies.trend_following import TrendFollowingMultiTFStrategy
from app.strategies.smart_scalping import SmartScalpingStrategy

STRATEGY_CLASSES = {
    "ema_crossover": EMACrossoverStrategy,
    "rsi_mean_reversion": RSIMeanReversionStrategy,
    "macd_momentum": MACDMomentumStrategy,
    "bollinger_bands": BollingerBandsStrategy,
    "breakout": BreakoutStrategy,
    "dca": SmartDCAStrategy,
    "grid_trading": GridTradingStrategy,
    "volatility_breakout": VolatilityBreakoutStrategy,
    "portfolio_rebalancing": PortfolioRebalancingStrategy,
    "arbitrage_monitor": ArbitrageMonitorStrategy,
    "trend_following": TrendFollowingMultiTFStrategy,
    "smart_scalping": SmartScalpingStrategy,
}

STRATEGY_REGISTRY = {
    "ema_crossover": {
        "name": "EMA Crossover",
        "description": "Golden/death cross using fast and slow EMA. Works best in trending markets.",
        "category": "Trend Following",
        "risk_level": "Low",
        "default_parameters": EMACrossoverStrategy.default_parameters(),
    },
    "rsi_mean_reversion": {
        "name": "RSI Mean Reversion",
        "description": "Buys oversold and sells overbought RSI conditions. Best in ranging markets.",
        "category": "Mean Reversion",
        "risk_level": "Medium",
        "default_parameters": RSIMeanReversionStrategy.default_parameters(),
    },
    "macd_momentum": {
        "name": "MACD Momentum",
        "description": "Trades MACD line crossovers for momentum-based entries.",
        "category": "Momentum",
        "risk_level": "Medium",
        "default_parameters": MACDMomentumStrategy.default_parameters(),
    },
    "bollinger_bands": {
        "name": "Bollinger Bands Reversal",
        "description": "Mean reversion strategy using Bollinger Band extremes.",
        "category": "Mean Reversion",
        "risk_level": "Medium",
        "default_parameters": BollingerBandsStrategy.default_parameters(),
    },
    "breakout": {
        "name": "Breakout Strategy",
        "description": "Trades breakouts above resistance and below support with ATR filter.",
        "category": "Breakout",
        "risk_level": "Medium",
        "default_parameters": BreakoutStrategy.default_parameters(),
    },
    "dca": {
        "name": "Smart DCA",
        "description": "Dollar-cost averaging with dynamic sizing on dips.",
        "category": "Accumulation",
        "risk_level": "Low",
        "default_parameters": SmartDCAStrategy.default_parameters(),
    },
    "grid_trading": {
        "name": "Grid Trading",
        "description": "Profits from price oscillation with automated grid orders.",
        "category": "Grid",
        "risk_level": "Medium",
        "default_parameters": GridTradingStrategy.default_parameters(),
    },
    "volatility_breakout": {
        "name": "Volatility Breakout",
        "description": "ATR-based entries on high-volatility explosive moves.",
        "category": "Breakout",
        "risk_level": "High",
        "default_parameters": VolatilityBreakoutStrategy.default_parameters(),
    },
    "portfolio_rebalancing": {
        "name": "Portfolio Rebalancing",
        "description": "Automatically rebalances multi-asset portfolio to target allocations.",
        "category": "Portfolio",
        "risk_level": "Low",
        "default_parameters": PortfolioRebalancingStrategy.default_parameters(),
    },
    "arbitrage_monitor": {
        "name": "Arbitrage Monitor",
        "description": "Monitors cross-exchange price discrepancies for arbitrage opportunities.",
        "category": "Arbitrage",
        "risk_level": "Low",
        "default_parameters": ArbitrageMonitorStrategy.default_parameters(),
    },
    "trend_following": {
        "name": "Trend Following Multi-TF",
        "description": "EMA crossover with ADX confirmation for strong trending markets.",
        "category": "Trend Following",
        "risk_level": "Medium",
        "default_parameters": TrendFollowingMultiTFStrategy.default_parameters(),
    },
    "smart_scalping": {
        "name": "Smart Scalping",
        "description": "High-frequency EMA + RSI + ATR scalping for liquid pairs.",
        "category": "Scalping",
        "risk_level": "High",
        "default_parameters": SmartScalpingStrategy.default_parameters(),
    },
}


def get_strategy(strategy_type: str, parameters: dict = {}):
    """Instantiate a strategy by type key."""
    cls = STRATEGY_CLASSES.get(strategy_type)
    if not cls:
        raise ValueError(f"Unknown strategy type: {strategy_type}")
    return cls(parameters)
