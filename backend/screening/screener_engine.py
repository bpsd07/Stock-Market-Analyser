"""High-Performance Async Stock Screener Engine.
Replaces Screeni-py's serial 50-stock loop with a concurrent, cached scanning pipeline.
Supports all Indian market universes (NIFTY 50, NIFTY 100, NIFTY 500, F&O).
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from backend.data.yahoo_provider import YahooFinanceProvider
from backend.data.nse_provider import NSEProvider
from backend.indicators.technical import compute_technical_snapshot
from backend.screening.candle_patterns import detect_candle_patterns
from backend.screening.screenipy_strategies import (
    check_vcp,
    check_five_ema,
    check_volume_spread_analysis,
    check_narrow_range,
    check_breakout,
    check_stage_two,
)
from backend.core.cache import cache

logger = logging.getLogger(__name__)


class ScreenerEngine:
    def __init__(self):
        self.market_data = YahooFinanceProvider()
        self.nse_data = NSEProvider()

    async def scan_symbol(self, symbol: str, strategy: str = "ALL") -> Optional[Dict[str, Any]]:
        """Analyzes a single stock and evaluates against screening rules."""
        try:
            df = await self.market_data.get_historical_candles(symbol, period="1y", interval="1d")
            if df.empty or len(df) < 30:
                return None

            enriched = compute_technical_snapshot(df)
            last_row = enriched.iloc[-1]
            prev_row = enriched.iloc[-2]

            ltp = float(last_row["Close"])
            prev_close = float(prev_row["Close"])
            change_pct = round(((ltp - prev_close) / prev_close) * 100.0, 2)
            volume = int(last_row["Volume"])
            vol_ratio = float(last_row.get("Vol_Ratio", 1.0))
            rsi = float(last_row.get("RSI_14", 50.0))

            matched_strategies = []

            # 1. Breakout check
            bo = check_breakout(enriched)
            if bo:
                matched_strategies.append(bo)

            # 2. VCP check
            vcp = check_vcp(enriched)
            if vcp:
                matched_strategies.append(vcp)

            # 3. 5-EMA setup
            five_ema = check_five_ema(enriched)
            if five_ema:
                matched_strategies.append(five_ema)

            # 4. Volume Spread Analysis (Supply Drought / Demand Rise)
            vsa = check_volume_spread_analysis(enriched)
            if vsa:
                matched_strategies.append(vsa)

            # 5. Narrow Range (NR7)
            nr7 = check_narrow_range(enriched, nr=7)
            if nr7:
                matched_strategies.append(nr7)

            # 6. Candlestick patterns
            cp = detect_candle_patterns(enriched)
            if cp:
                matched_strategies.append(cp)

            # 7. Stage 2 verification
            is_stage_2 = check_stage_two(enriched)

            # Filter by requested strategy if specified
            if strategy != "ALL":
                has_target = any(
                    s.get("strategy") == strategy or s.get("pattern") == strategy
                    for s in matched_strategies
                )
                if not has_target:
                    return None
            elif not matched_strategies and not is_stage_2:
                # If ALL requested, return only stocks that triggered at least one setup
                return None

            return {
                "symbol": symbol.upper(),
                "last_price": round(ltp, 2),
                "change_pct": change_pct,
                "volume": volume,
                "volume_ratio": vol_ratio,
                "rsi_14": round(rsi, 1),
                "is_stage_2": is_stage_2,
                "sma_50": round(float(last_row.get("SMA_50", 0.0)), 2),
                "sma_200": round(float(last_row.get("SMA_200", 0.0)), 2),
                "triggers": matched_strategies,
                "primary_trigger": matched_strategies[0]["strategy"] if matched_strategies and "strategy" in matched_strategies[0] else (matched_strategies[0]["pattern"] if matched_strategies else "STAGE_2_UPTREND"),
            }
        except Exception as e:
            logger.debug(f"Error screening symbol {symbol}: {e}")
            return None

    async def run_scan(
        self,
        universe: str = "NIFTY_50",
        strategy: str = "ALL",
        max_symbols: int = 50,
    ) -> List[Dict[str, Any]]:
        """Scans universe with controlled concurrency and caching."""
        cache_key = f"screener:scan:{universe}:{strategy}:{max_symbols}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        symbols = await self.nse_data.fetch_index_symbols(universe)
        target_symbols = symbols[:max_symbols]

        # Scan concurrently using asyncio.gather with Semaphore to avoid rate limit spikes
        semaphore = asyncio.Semaphore(8)

        async def _bounded_scan(sym):
            async with semaphore:
                return await self.scan_symbol(sym, strategy)

        tasks = [_bounded_scan(sym) for sym in target_symbols]
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        results = [
            r for r in raw_results if r and not isinstance(r, Exception)
        ]

        # Sort by volume ratio and absolute change percentage
        results.sort(key=lambda x: (len(x["triggers"]), x["volume_ratio"]), reverse=True)

        await cache.set(cache_key, results, ttl_seconds=300)
        return results
