"""Vectorized Technical Indicators Engine.
Pure-Python, Pandas, and NumPy implementation.
Zero C-extension compilation dependencies (no TA-Lib compiler issues on Windows).
Fast, vectorized, and unit-tested.
"""
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd


def calculate_sma(series: pd.Series, period: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=period, min_periods=period).mean()


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=period, adjust=False).mean()


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index (Wilder's smoothing)."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi.fillna(50.0)


def calculate_macd(
    series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Moving Average Convergence Divergence."""
    fast_ema = calculate_ema(series, fast)
    slow_ema = calculate_ema(series, slow)
    macd_line = fast_ema - slow_ema
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(
    series: pd.Series, period: int = 20, num_std: float = 2.0
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands (Middle, Upper, Lower)."""
    middle = calculate_sma(series, period)
    std = series.rolling(window=period).std()
    upper = middle + (std * num_std)
    lower = middle - (std * num_std)
    return middle, upper, lower


def calculate_atr(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
) -> pd.Series:
    """Average True Range."""
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    return atr


def calculate_supertrend(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 10, multiplier: float = 3.0
) -> Tuple[pd.Series, pd.Series]:
    """Supertrend indicator (Supertrend line, Direction: +1 Bullish, -1 Bearish)."""
    atr = calculate_atr(high, low, close, period)
    hl2 = (high + low) / 2.0
    upper_band = hl2 + (multiplier * atr)
    lower_band = hl2 - (multiplier * atr)

    supertrend = pd.Series(index=close.index, dtype=float)
    direction = pd.Series(index=close.index, dtype=int)

    # Iterative calculation for proper band tightening
    in_uptrend = True
    for i in range(len(close)):
        if i == 0:
            supertrend.iloc[i] = lower_band.iloc[i]
            direction.iloc[i] = 1
            continue

        curr_close = close.iloc[i]
        curr_upper = upper_band.iloc[i]
        curr_lower = lower_band.iloc[i]
        prev_supertrend = supertrend.iloc[i - 1]

        if in_uptrend:
            if curr_close < prev_supertrend:
                in_uptrend = False
                supertrend.iloc[i] = curr_upper
                direction.iloc[i] = -1
            else:
                supertrend.iloc[i] = max(curr_lower, prev_supertrend)
                direction.iloc[i] = 1
        else:
            if curr_close > prev_supertrend:
                in_uptrend = True
                supertrend.iloc[i] = curr_lower
                direction.iloc[i] = 1
            else:
                supertrend.iloc[i] = min(curr_upper, prev_supertrend)
                direction.iloc[i] = -1

    return supertrend, direction


def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """Volume Weighted Average Price."""
    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3.0
    vp = typical_price * df["Volume"]
    cum_vp = vp.cumsum()
    cum_vol = df["Volume"].cumsum()
    vwap = cum_vp / cum_vol.replace(0, np.nan)
    return vwap.ffill()


def compute_technical_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    """Enriches OHLCV DataFrame with complete suite of indicators."""
    if df.empty or len(df) < 5:
        return df

    data = df.copy()
    close = data["Close"]
    high = data["High"]
    low = data["Low"]
    volume = data["Volume"]

    # Moving averages
    data["SMA_20"] = calculate_sma(close, 20)
    data["SMA_50"] = calculate_sma(close, 50)
    data["SMA_200"] = calculate_sma(close, 200)

    data["EMA_9"] = calculate_ema(close, 9)
    data["EMA_21"] = calculate_ema(close, 21)
    data["EMA_50"] = calculate_ema(close, 50)
    data["EMA_200"] = calculate_ema(close, 200)

    # Volume moving average
    data["VolMA_20"] = volume.rolling(20).mean()
    data["Vol_Ratio"] = (volume / data["VolMA_20"].replace(0, np.nan)).round(2)

    # Momentum & Trend
    data["RSI_14"] = calculate_rsi(close, 14)
    macd, signal, hist = calculate_macd(close, 12, 26, 9)
    data["MACD"] = macd
    data["MACD_Signal"] = signal
    data["MACD_Hist"] = hist

    # Volatility
    bb_mid, bb_upper, bb_lower = calculate_bollinger_bands(close, 20, 2.0)
    data["BB_Middle"] = bb_mid
    data["BB_Upper"] = bb_upper
    data["BB_Lower"] = bb_lower
    data["ATR_14"] = calculate_atr(high, low, close, 14)

    return data
