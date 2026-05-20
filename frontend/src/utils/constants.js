export const EXCHANGES = [
  { id: 'binance', name: 'Binance', logo: '🟡' },
  { id: 'binanceus', name: 'Binance US', logo: '🟡' },
  { id: 'coinbase', name: 'Coinbase Advanced', logo: '🔵' },
  { id: 'kraken', name: 'Kraken', logo: '🟣' },
  { id: 'bybit', name: 'Bybit', logo: '🟠' },
  { id: 'okx', name: 'OKX', logo: '⚫' },
  { id: 'kucoin', name: 'KuCoin', logo: '🟢' },
  { id: 'gate', name: 'Gate.io', logo: '🔷' },
  { id: 'huobi', name: 'HTX (Huobi)', logo: '🔴' },
  { id: 'bitfinex', name: 'Bitfinex', logo: '🟤' },
]

export const TIMEFRAMES = [
  { value: '1m', label: '1 Minute' },
  { value: '3m', label: '3 Minutes' },
  { value: '5m', label: '5 Minutes' },
  { value: '15m', label: '15 Minutes' },
  { value: '30m', label: '30 Minutes' },
  { value: '1h', label: '1 Hour' },
  { value: '4h', label: '4 Hours' },
  { value: '1d', label: '1 Day' },
  { value: '1w', label: '1 Week' },
]

export const STRATEGY_TYPES = [
  { value: 'ema_crossover', label: 'EMA Crossover', category: 'Trend', risk: 'Low' },
  { value: 'rsi_mean_reversion', label: 'RSI Mean Reversion', category: 'Mean Reversion', risk: 'Medium' },
  { value: 'macd_momentum', label: 'MACD Momentum', category: 'Momentum', risk: 'Medium' },
  { value: 'bollinger_bands', label: 'Bollinger Bands Reversal', category: 'Mean Reversion', risk: 'Medium' },
  { value: 'breakout', label: 'Breakout Strategy', category: 'Breakout', risk: 'High' },
  { value: 'dca', label: 'DCA (Dollar-Cost Averaging)', category: 'Investment', risk: 'Low' },
  { value: 'grid_trading', label: 'Grid Trading', category: 'Neutral', risk: 'Medium' },
  { value: 'volatility_breakout', label: 'Volatility Breakout', category: 'Breakout', risk: 'High' },
  { value: 'portfolio_rebalancing', label: 'Portfolio Rebalancing', category: 'Investment', risk: 'Low' },
  { value: 'arbitrage_monitor', label: 'Arbitrage Monitor', category: 'Arbitrage', risk: 'Low' },
  { value: 'trend_following', label: 'Trend Following Multi-TF', category: 'Trend', risk: 'Medium' },
  { value: 'smart_scalping', label: 'Smart Scalping', category: 'Scalping', risk: 'High' },
  { value: 'custom', label: 'Custom Strategy', category: 'Custom', risk: 'Variable' },
]

export const PLAN_FEATURES = {
  free: {
    name: 'Free',
    price: 0,
    bots: 1,
    backtests: 5,
    live_trading: false,
    signals: false,
    ai_assistant: false,
    color: 'text-gray-400',
  },
  pro: {
    name: 'Pro',
    price: 49,
    bots: 5,
    backtests: 50,
    live_trading: true,
    signals: true,
    ai_assistant: true,
    color: 'text-brand-400',
  },
  elite: {
    name: 'Elite',
    price: 149,
    bots: -1,  // unlimited
    backtests: -1,
    live_trading: true,
    signals: true,
    ai_assistant: true,
    color: 'text-purple-400',
  },
}

export const POPULAR_PAIRS = [
  'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT',
  'ADA/USDT', 'XRP/USDT', 'DOGE/USDT', 'MATIC/USDT',
  'AVAX/USDT', 'DOT/USDT',
]

export const RISK_LEVELS = {
  low: { label: 'Low', class: 'badge-green' },
  medium: { label: 'Medium', class: 'badge-yellow' },
  high: { label: 'High', class: 'badge-red' },
}
