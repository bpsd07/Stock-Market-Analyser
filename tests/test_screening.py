"""Unit tests for screening algorithms and candlestick patterns."""
import pandas as pd
import numpy as np
import pytest
from backend.screening.candle_patterns import detect_candle_patterns
from backend.screening.screenipy_strategies import check_narrow_range, check_breakout, check_five_ema


def test_nr7_detection():
    # Construct 7 bars where the 7th has the tightest range
    data = []
    for i in range(6):
        data.append({"Open": 100, "High": 110, "Low": 90, "Close": 105, "Volume": 100000})  # Range = 20
    # 7th bar with range = 4
    data.append({"Open": 102, "High": 104, "Low": 100, "Close": 103, "Volume": 50000})

    df = pd.DataFrame(data)
    nr = check_narrow_range(df, nr=7)
    assert nr is not None
    assert nr["strategy"] == "NR_7"
    assert nr["current_range"] == 4.0


def test_bullish_engulfing():
    # Day 1: Red bar
    # Day 2: Large Green bar engulfing Day 1
    bars = [
        {"Open": 100, "High": 105, "Low": 95, "Close": 100, "Volume": 100000},
        {"Open": 100, "High": 105, "Low": 95, "Close": 100, "Volume": 100000},
        {"Open": 105, "High": 106, "Low": 98, "Close": 99, "Volume": 100000},   # Red candle (Open 105, Close 99)
        {"Open": 98, "High": 110, "Low": 97, "Close": 108, "Volume": 250000},   # Green engulfing (Open 98, Close 108)
    ]
    df = pd.DataFrame(bars)
    res = detect_candle_patterns(df)
    assert res is not None
    assert res["pattern"] == "Bullish Engulfing"
    assert res["type"] == "BULLISH_REVERSAL"
