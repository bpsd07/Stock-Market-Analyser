"""Stock Deep Dive & Research Endpoints."""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from backend.data.yahoo_provider import YahooFinanceProvider
from backend.indicators.technical import compute_technical_snapshot
from backend.fundamentals.fundamental_engine import FundamentalEngine
from backend.screening.candle_patterns import detect_candle_patterns
from backend.screening.screenipy_strategies import check_vcp, check_five_ema, check_breakout

router = APIRouter(prefix="/stocks", tags=["Stock Research"])
market_provider = YahooFinanceProvider()
fundamental_engine = FundamentalEngine()


@router.get("/{symbol}/deep-dive")
async def get_stock_deep_dive(symbol: str):
    """Provides complete 360-degree analytics: price, technical indicators, candlestick patterns, and fundamentals."""
    sym = symbol.upper()
    df = await market_provider.get_historical_candles(sym, period="1y", interval="1d")

    if df.empty or len(df) < 10:
        raise HTTPException(status_code=404, detail=f"Stock data unavailable for {sym}")

    enriched = compute_technical_snapshot(df)
    last = enriched.iloc[-1]
    prev = enriched.iloc[-2]

    # Fetch 0-latency live quote
    live_quote = await market_provider.get_quote(sym)
    if live_quote.get("last_price", 0) > 0:
        ltp = float(live_quote["last_price"])
        chg = float(live_quote["change_pct"])
    else:
        ltp = float(last["Close"])
        prev_close = float(prev["Close"])
        chg = round(((ltp - prev_close) / prev_close * 100.0), 2)

    tech_snapshot = {
        "last_price": round(ltp, 2),
        "change_pct": chg,
        "is_real_time": live_quote.get("is_real_time", True),
        "volume": int(last["Volume"]),
        "volume_ratio": float(last.get("Vol_Ratio", 1.0)),
        "rsi_14": round(float(last.get("RSI_14", 50.0)), 1),
        "sma_20": round(float(last.get("SMA_20", 0.0)), 2),
        "sma_50": round(float(last.get("SMA_50", 0.0)), 2),
        "sma_200": round(float(last.get("SMA_200", 0.0)), 2),
        "ema_9": round(float(last.get("EMA_9", 0.0)), 2),
        "ema_21": round(float(last.get("EMA_21", 0.0)), 2),
        "macd": round(float(last.get("MACD", 0.0)), 2),
        "macd_signal": round(float(last.get("MACD_Signal", 0.0)), 2),
        "bb_upper": round(float(last.get("BB_Upper", 0.0)), 2),
        "bb_lower": round(float(last.get("BB_Lower", 0.0)), 2),
        "atr_14": round(float(last.get("ATR_14", 0.0)), 2),
    }

    # Candlestick pattern detection
    pattern = detect_candle_patterns(enriched)

    # Strategy signals
    triggers = []
    bo = check_breakout(enriched)
    if bo:
        triggers.append(bo)
    vcp = check_vcp(enriched)
    if vcp:
        triggers.append(vcp)
    fem = check_five_ema(enriched)
    if fem:
        triggers.append(fem)

    # Fundamentals
    fund = await fundamental_engine.get_fundamentals(sym)

    # Candlestick chart payload (last 60 bars)
    chart_bars = []
    for dt, row in enriched.tail(60).iterrows():
        chart_bars.append({
            "time": str(dt)[:10],
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]),
        })

    return {
        "symbol": sym,
        "technical": tech_snapshot,
        "candlestick_pattern": pattern,
        "technical_triggers": triggers,
        "fundamentals": fund,
        "chart_candles": chart_bars,
    }
