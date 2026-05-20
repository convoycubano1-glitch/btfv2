"""
pandas_ta compatibility shim.
Provides the same API used by the strategy files using the `ta` library,
which is pure-Python and available on PyPI for Python 3.11.
"""
import pandas as pd
import ta as _ta


def ema(series: pd.Series, length: int = 20, **kwargs) -> pd.Series:
    return _ta.trend.ema_indicator(series, window=length)


def rsi(series: pd.Series, length: int = 14, **kwargs) -> pd.Series:
    return _ta.momentum.rsi(series, window=length)


def atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14, **kwargs) -> pd.Series:
    return _ta.volatility.average_true_range(high, low, close, window=length)


def macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    **kwargs,
) -> pd.DataFrame:
    macd_line = _ta.trend.macd(series, window_slow=slow, window_fast=fast, window_sign=signal)
    signal_line = _ta.trend.macd_signal(series, window_slow=slow, window_fast=fast, window_sign=signal)
    hist = _ta.trend.macd_diff(series, window_slow=slow, window_fast=fast, window_sign=signal)
    return pd.DataFrame(
        {
            f"MACD_{fast}_{slow}_{signal}": macd_line,
            f"MACDh_{fast}_{slow}_{signal}": hist,
            f"MACDs_{fast}_{slow}_{signal}": signal_line,
        }
    )


def bbands(
    series: pd.Series,
    length: int = 20,
    std: float = 2.0,
    **kwargs,
) -> pd.DataFrame:
    upper = _ta.volatility.bollinger_hband(series, window=length, window_dev=float(std))
    middle = _ta.volatility.bollinger_mavg(series, window=length)
    lower = _ta.volatility.bollinger_lband(series, window=length, window_dev=float(std))
    return pd.DataFrame(
        {
            f"BBL_{length}_{float(std)}": lower,
            f"BBM_{length}_{float(std)}": middle,
            f"BBU_{length}_{float(std)}": upper,
        }
    )


def adx(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    length: int = 14,
    **kwargs,
) -> pd.DataFrame:
    adx_val = _ta.trend.adx(high, low, close, window=length)
    return pd.DataFrame({f"ADX_{length}": adx_val})
