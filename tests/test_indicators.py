"""Unit tests for pure-python technical indicators."""
import numpy as np
import pandas as pd
import pytest
from backend.indicators.technical import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    compute_technical_snapshot,
)


@pytest.fixture
def sample_ohlcv():
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=100)
    prices = 1000.0 + np.cumsum(np.random.randn(100) * 15.0)
    highs = prices + np.abs(np.random.randn(100) * 10.0)
    lows = prices - np.abs(np.random.randn(100) * 10.0)
    opens = prices + np.random.randn(100) * 5.0
    volumes = np.random.randint(50000, 500000, size=100)

    return pd.DataFrame({
        "Open": opens,
        "High": highs,
        "Low": lows,
        "Close": prices,
        "Volume": volumes,
    }, index=dates)


def test_sma_calculation(sample_ohlcv):
    sma20 = calculate_sma(sample_ohlcv["Close"], 20)
    assert len(sma20) == 100
    assert pd.isna(sma20.iloc[18])
    assert not pd.isna(sma20.iloc[19])
    assert round(sma20.iloc[19], 2) == round(sample_ohlcv["Close"].iloc[:20].mean(), 2)


def test_rsi_bounds(sample_ohlcv):
    rsi = calculate_rsi(sample_ohlcv["Close"], 14)
    assert len(rsi) == 100
    assert (rsi >= 0.0).all() and (rsi <= 100.0).all()


def test_macd_relationship(sample_ohlcv):
    macd, signal, hist = calculate_macd(sample_ohlcv["Close"], 12, 26, 9)
    assert len(macd) == 100
    # Hist must equal macd - signal
    np.testing.assert_allclose(hist.dropna(), (macd - signal).dropna(), atol=1e-5)


def test_bollinger_bands_ordering(sample_ohlcv):
    mid, upper, lower = calculate_bollinger_bands(sample_ohlcv["Close"], 20, 2.0)
    valid_idx = ~pd.isna(upper)
    assert (upper[valid_idx] >= mid[valid_idx]).all()
    assert (mid[valid_idx] >= lower[valid_idx]).all()


def test_atr_positive(sample_ohlcv):
    atr = calculate_atr(sample_ohlcv["High"], sample_ohlcv["Low"], sample_ohlcv["Close"], 14)
    valid_atr = atr.dropna()
    assert (valid_atr > 0.0).all()


def test_compute_technical_snapshot(sample_ohlcv):
    enriched = compute_technical_snapshot(sample_ohlcv)
    expected_cols = ["SMA_20", "SMA_50", "EMA_9", "RSI_14", "MACD", "ATR_14", "Vol_Ratio"]
    for col in expected_cols:
        assert col in enriched.columns
