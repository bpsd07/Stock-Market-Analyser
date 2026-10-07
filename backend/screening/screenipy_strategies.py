"""Screeni-py Strategy Algorithms Port & Modernization.
Refactored into clean, pure-Python, deterministic functions.
Preserves high-value setups: VCP, 5 EMA, Volume Spread Analysis,
MA Confluence, NR4/NR7, and Momentum Breakouts.
"""
from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from backend.indicators.technical import compute_technical_snapshot


def check_vcp(df: pd.DataFrame, window: int = 3, pct_from_top: float = 4.0) -> Optional[Dict[str, Any]]:
    """Volatility Contraction Pattern (Mark Minervini VCP).
    Identifies successive contracting price waves near 52-week or multi-month highs.
    Ported directly from Screeni-py Screener.validateVCP.
    """
    if len(df) < 50:
        return None

    data = df.tail(120).copy().reset_index(drop=True)
    highs = data["High"].to_numpy()
    lows = data["Low"].to_numpy()

    # Find swing highs and swing lows using argrelextrema
    top_indices = list(argrelextrema(highs, np.greater_equal, order=window)[0])
    bot_indices = list(argrelextrema(lows, np.less_equal, order=window)[0])

    if len(top_indices) < 3 or len(bot_indices) < 2:
        return None

    top_prices = [highs[i] for i in top_indices[-4:]]
    highest_top = max(top_prices)

    # Check if swing tops are forming near the same resistance level (within pct_from_top)
    is_tight_ceiling = all(top >= highest_top * (1.0 - pct_from_top / 100.0) for top in top_prices)

    # Check if swing lows are contracting upwards (higher lows)
    bot_prices = [lows[i] for i in bot_indices[-3:]]
    is_higher_lows = all(bot_prices[i] >= bot_prices[i - 1] for i in range(1, len(bot_prices)))

    current_price = data["Close"].iloc[-1]

    if is_tight_ceiling and is_higher_lows and current_price < highest_top and current_price >= bot_prices[-1]:
        return {
            "strategy": "VCP_CONTRACTION",
            "breakout_level": round(float(highest_top), 2),
            "support_base": round(float(bot_prices[-1]), 2),
            "current_price": round(float(current_price), 2),
            "description": f"VCP contraction confirmed with higher lows. Pivot resistance at ₹{round(highest_top, 2)}.",
        }

    return None


def check_five_ema(df: pd.DataFrame, risk_reward: float = 3.0) -> Optional[Dict[str, Any]]:
    """5-EMA Strategy (Mean Reversion setup).
    Identifies stretched candles where Low/High is detached from the 5 EMA.
    Ported directly from Screeni-py Screener.monitorFiveEma.
    """
    if len(df) < 10:
        return None

    data = df.copy()
    data["EMA_5"] = data["Close"].ewm(span=5, adjust=False).mean()

    prev = data.iloc[-2]
    curr = data.iloc[-1]

    # Bullish Mean Reversion: Previous candle Low > 5EMA (stretched above), current candle crosses back
    # Or Bearish setup: Previous candle High < 5EMA (stretched below), current candle crosses back
    # In Indian retail intraday/swing:
    # 1. Bearish setup: Candle Low > 5 EMA (completely above 5EMA). When next candle breaks low -> SELL.
    if prev["Low"] > prev["EMA_5"] and (prev["Low"] - prev["EMA_5"]) > (prev["Close"] * 0.002):
        if curr["Close"] < prev["Low"] or curr["Low"] < prev["Low"]:
            sl = round(float(prev["High"]), 2)
            entry = round(float(prev["Low"]), 2)
            risk = max(sl - entry, 0.5)
            target = round(entry - (risk * risk_reward), 2)
            return {
                "strategy": "5_EMA_REVERSAL_SHORT",
                "direction": "BEARISH",
                "entry": entry,
                "stop_loss": sl,
                "target": target,
                "risk_reward": f"1:{risk_reward}",
                "description": f"5-EMA Short setup triggered below ₹{entry} with SL ₹{sl}.",
            }

    # 2. Bullish setup: Candle High < 5 EMA (completely below 5EMA). When next candle breaks high -> BUY.
    if prev["High"] < prev["EMA_5"] and (prev["EMA_5"] - prev["High"]) > (prev["Close"] * 0.002):
        if curr["Close"] > prev["High"] or curr["High"] > prev["High"]:
            sl = round(float(prev["Low"]), 2)
            entry = round(float(prev["High"]), 2)
            risk = max(entry - sl, 0.5)
            target = round(entry + (risk * risk_reward), 2)
            return {
                "strategy": "5_EMA_REVERSAL_BUY",
                "direction": "BULLISH",
                "entry": entry,
                "stop_loss": sl,
                "target": target,
                "risk_reward": f"1:{risk_reward}",
                "description": f"5-EMA Long setup triggered above ₹{entry} with SL ₹{sl}.",
            }

    return None


def check_volume_spread_analysis(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """Volume Spread Analysis (Supply Drought & Demand Rise).
    Ported from Screeni-py Screener.validateVolumeSpreadAnalysis.
    """
    if len(df) < 20:
        return None

    data = df.tail(5).copy()
    c0 = data.iloc[-1]  # Today
    c1 = data.iloc[-2]  # Yesterday

    vol_ma20 = df["Volume"].tail(20).mean()

    spread0 = abs(c0["Open"] - c0["Close"])
    spread1 = abs(c1["Open"] - c1["Close"])
    lower_wick0 = min(c0["Open"], c0["Close"]) - c0["Low"]

    # Supply Drought: Prior candle was down, current candle volume is exceptionally dry (< 75% of prior and < VolMA)
    # with narrow spread, demonstrating seller exhaustion.
    if (
        c1["Open"] >= c1["Close"]
        and c0["Volume"] < vol_ma20
        and c0["Volume"] <= c1["Volume"] * 0.75
        and spread0 <= spread1
    ):
        return {
            "strategy": "VSA_SUPPLY_DROUGHT",
            "type": "BULLISH_ABSORPTION",
            "description": "Supply Drought detected: Volume completely dried up on consolidation, signaling seller depletion.",
        }

    # Demand Rise: High volume absorption with expanding spread above prior close
    if c0["Volume"] > vol_ma20 * 1.5 and c0["Close"] > c1["Close"] and c0["Close"] > c0["Open"]:
        return {
            "strategy": "VSA_DEMAND_RISE",
            "type": "BULLISH_EXPANSION",
            "description": f"Demand Rise detected: Volume expanded to {round(c0['Volume'] / vol_ma20, 1)}x 20-day average on bullish close.",
        }

    return None


def check_narrow_range(df: pd.DataFrame, nr: int = 7) -> Optional[Dict[str, Any]]:
    """Narrow Range Bar (NR4 / NR7 contraction).
    Identifies when the current day's trading range is the smallest of the past N days.
    Ported from Screeni-py Screener.validateNarrowRange.
    """
    if len(df) < nr:
        return None

    recent = df.tail(nr).copy()
    ranges = (recent["High"] - recent["Low"]).to_list()
    current_range = ranges[-1]
    min_range = min(ranges)

    if current_range == min_range:
        current_close = df["Close"].iloc[-1]
        atr = (df["High"] - df["Low"]).tail(14).mean()
        return {
            "strategy": f"NR_{nr}",
            "type": "VOLATILITY_COMPRESSION",
            "current_range": round(float(current_range), 2),
            "atr_14": round(float(atr), 2),
            "description": f"NR{nr} detected: Tightest volatility range in {nr} trading sessions. Anticipate explosive directional breakout.",
        }

    return None


def check_breakout(df: pd.DataFrame, lookback: int = 50) -> Optional[Dict[str, Any]]:
    """Resistance Breakout with Volume Confirmation.
    Ported from Screeni-py Screener.findBreakout.
    """
    if len(df) < lookback + 1:
        return None

    prior = df.iloc[-lookback - 1 : -1]
    today = df.iloc[-1]

    highest_close = prior["Close"].max()
    highest_high = prior["High"].max()
    vol_ma20 = prior["Volume"].tail(20).mean()

    # Price breaking above 50-day highest close with > 1.5x volume expansion
    if today["Close"] > highest_close and today["Volume"] > vol_ma20 * 1.4:
        return {
            "strategy": "MOMENTUM_BREAKOUT",
            "breakout_price": round(float(highest_close), 2),
            "current_price": round(float(today["Close"]), 2),
            "volume_surge": round(float(today["Volume"] / vol_ma20), 2),
            "description": f"Breakout above {lookback}-day high (₹{round(highest_close, 2)}) with {round(today['Volume'] / vol_ma20, 1)}x volume surge.",
        }

    return None


def check_stage_two(df: pd.DataFrame) -> bool:
    """Stan Weinstein / Mark Minervini Stage 2 Uptrend Verification.
    Stock must be above 50 SMA and 200 SMA, with 50 SMA > 200 SMA,
    and trading at least 25% above 52-week low and within 25% of 52-week high.
    """
    if len(df) < 200:
        return False

    c = df["Close"].iloc[-1]
    sma50 = df["Close"].tail(50).mean()
    sma200 = df["Close"].tail(200).mean()
    yearly_low = df["Low"].tail(250).min() if len(df) >= 250 else df["Low"].min()
    yearly_high = df["High"].tail(250).max() if len(df) >= 250 else df["High"].max()

    return bool(
        c > sma50 > sma200
        and c >= yearly_low * 1.25
        and c >= yearly_high * 0.75
    )
