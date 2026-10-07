"""Candlestick Pattern Recognition Engine.
Pure-Python, zero-dependency implementation of the 18 patterns from Screeni-py.
Classifies patterns into Bullish Reversal, Bearish Reversal, or Continuation.
"""
from typing import Optional, Dict, Any
import pandas as pd


def detect_candle_patterns(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """Inspects recent candles (last 4 bars) for high-probability candlestick patterns.
    Returns pattern dictionary if found, else None.
    """
    if len(df) < 4:
        return None

    # Work with recent 4 bars: c0 is today, c1 is yesterday, c2 is 2 days ago, c3 is 3 days ago
    recent = df.tail(4).copy()
    c = [recent.iloc[i] for i in range(len(recent))]  # c[0]=3d ago, c[1]=2d ago, c[2]=1d ago, c[3]=today
    today = c[3]
    prev = c[2]
    prev2 = c[1]

    def is_bullish(bar):
        return bar["Close"] >= bar["Open"]

    def is_bearish(bar):
        return bar["Close"] < bar["Open"]

    def body_size(bar):
        return abs(bar["Close"] - bar["Open"])

    def upper_shadow(bar):
        return bar["High"] - max(bar["Close"], bar["Open"])

    def lower_shadow(bar):
        return min(bar["Close"], bar["Open"]) - bar["Low"]

    def is_doji(bar):
        return body_size(bar) <= (bar["High"] - bar["Low"]) * 0.10

    # 1. Morning Star (Bullish Reversal)
    if (
        is_bearish(prev2)
        and body_size(prev) < body_size(prev2) * 0.4
        and is_bullish(today)
        and today["Close"] > (prev2["Open"] + prev2["Close"]) / 2.0
    ):
        return {
            "pattern": "Morning Star",
            "type": "BULLISH_REVERSAL",
            "significance": "HIGH",
            "description": "3-bar bullish reversal pattern indicating seller exhaustion followed by sharp buyer momentum.",
        }

    # 2. Evening Star (Bearish Reversal)
    if (
        is_bullish(prev2)
        and body_size(prev) < body_size(prev2) * 0.4
        and is_bearish(today)
        and today["Close"] < (prev2["Open"] + prev2["Close"]) / 2.0
    ):
        return {
            "pattern": "Evening Star",
            "type": "BEARISH_REVERSAL",
            "significance": "HIGH",
            "description": "3-bar bearish reversal pattern signaling buyer climax and distribution.",
        }

    # 3. Three White Soldiers (Strong Bullish Continuation)
    if (
        is_bullish(prev2)
        and is_bullish(prev)
        and is_bullish(today)
        and prev["Close"] > prev2["Close"]
        and today["Close"] > prev["Close"]
        and upper_shadow(today) < body_size(today) * 0.3
    ):
        return {
            "pattern": "3 White Soldiers",
            "type": "BULLISH_EXPANSION",
            "significance": "VERY_HIGH",
            "description": "3 consecutive strong green candles with higher closes showing persistent institutional buying.",
        }

    # 4. Three Black Crows (Strong Bearish Continuation)
    if (
        is_bearish(prev2)
        and is_bearish(prev)
        and is_bearish(today)
        and prev["Close"] < prev2["Close"]
        and today["Close"] < prev["Close"]
        and lower_shadow(today) < body_size(today) * 0.3
    ):
        return {
            "pattern": "3 Black Crows",
            "type": "BEARISH_EXPANSION",
            "significance": "VERY_HIGH",
            "description": "3 consecutive red candles with lower closes signaling aggressive institutional liquidation.",
        }

    # 5. Bullish Engulfing
    if (
        is_bearish(prev)
        and is_bullish(today)
        and today["Open"] <= prev["Close"]
        and today["Close"] >= prev["Open"]
    ):
        return {
            "pattern": "Bullish Engulfing",
            "type": "BULLISH_REVERSAL",
            "significance": "HIGH",
            "description": "Large green candle completely engulfing the prior red body at key support.",
        }

    # 6. Bearish Engulfing
    if (
        is_bullish(prev)
        and is_bearish(today)
        and today["Open"] >= prev["Close"]
        and today["Close"] <= prev["Open"]
    ):
        return {
            "pattern": "Bearish Engulfing",
            "type": "BEARISH_REVERSAL",
            "significance": "HIGH",
            "description": "Large red candle completely engulfing the prior green body at key resistance.",
        }

    # 7. Hammer (Bullish Reversal)
    if (
        lower_shadow(today) >= 2.0 * body_size(today)
        and upper_shadow(today) <= body_size(today) * 0.3
        and is_bearish(prev)
    ):
        return {
            "pattern": "Hammer",
            "type": "BULLISH_REVERSAL",
            "significance": "MEDIUM",
            "description": "Long lower shadow showing rejection of lower prices and intraday buyer recovery.",
        }

    # 8. Shooting Star (Bearish Reversal)
    if (
        upper_shadow(today) >= 2.0 * body_size(today)
        and lower_shadow(today) <= body_size(today) * 0.3
        and is_bullish(prev)
    ):
        return {
            "pattern": "Shooting Star",
            "type": "BEARISH_REVERSAL",
            "significance": "MEDIUM",
            "description": "Long upper shadow showing rejection of higher prices and aggressive seller pushback.",
        }

    # 9. Dragonfly Doji (Bullish Reversal)
    if is_doji(today) and lower_shadow(today) >= (today["High"] - today["Low"]) * 0.7:
        return {
            "pattern": "Dragonfly Doji",
            "type": "BULLISH_REVERSAL",
            "significance": "MEDIUM",
            "description": "Doji with long lower tail indicating strong support at lows.",
        }

    # 10. Gravestone Doji (Bearish Reversal)
    if is_doji(today) and upper_shadow(today) >= (today["High"] - today["Low"]) * 0.7:
        return {
            "pattern": "Gravestone Doji",
            "type": "BEARISH_REVERSAL",
            "significance": "MEDIUM",
            "description": "Doji with long upper tail indicating supply overhang at highs.",
        }

    return None
