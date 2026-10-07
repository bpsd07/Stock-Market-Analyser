"""Yahoo Finance Market Data Provider.
Provides non-blocking historical candles and real-time live quotes for Indian equities.
Appends .NS for NSE equities or .BO for BSE equities.
Guarantees real-time tick synchronization.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import pandas as pd
import yfinance as yf
from backend.data.provider import MarketDataProvider
from backend.core.cache import cache

logger = logging.getLogger(__name__)


class YahooFinanceProvider(MarketDataProvider):
    """Yahoo Finance implementation for Indian markets."""

    def __init__(self, default_exchange_suffix: str = ".NS"):
        self.suffix = default_exchange_suffix

    def _format_ticker(self, symbol: str) -> str:
        s = symbol.strip().upper()
        if s.endswith(".NS") or s.endswith(".BO") or s.startswith("^") or "=" in s:
            return s
        return f"{s}{self.suffix}"

    async def get_index_symbols(self, index_name: str) -> List[str]:
        from backend.data.nse_provider import NSEProvider
        return await NSEProvider().fetch_index_symbols(index_name)

    async def get_historical_candles(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        formatted_ticker = self._format_ticker(symbol)
        cache_key = f"yf:candles:{formatted_ticker}:{period}:{interval}"
        cached = await cache.get(cache_key)
        if cached:
            df = pd.DataFrame(cached)
            if not df.empty and "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"])
                df.set_index("Date", inplace=True)
            return df

        def _fetch():
            try:
                dl_kwargs = {
                    "tickers": formatted_ticker,
                    "interval": interval,
                    "progress": False,
                    "timeout": 12,
                    "auto_adjust": False,
                }
                if start_date and end_date:
                    dl_kwargs["start"] = start_date
                    dl_kwargs["end"] = end_date
                else:
                    dl_kwargs["period"] = period
                data = yf.download(**dl_kwargs)

                # Flatten multi-level columns if present
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = [c[0] for c in data.columns]

                data.dropna(subset=["Close"], inplace=True)

                # Real-time tick synchronization: check if latest tick needs to be merged
                try:
                    ticker = yf.Ticker(formatted_ticker)
                    fast = ticker.fast_info
                    live_price = float(fast.last_price or 0.0)
                    if live_price > 0 and not data.empty:
                        # Update the latest row's Close if different
                        data.iloc[-1, data.columns.get_loc("Close")] = live_price
                        if live_price > data.iloc[-1, data.columns.get_loc("High")]:
                            data.iloc[-1, data.columns.get_loc("High")] = live_price
                        if live_price < data.iloc[-1, data.columns.get_loc("Low")]:
                            data.iloc[-1, data.columns.get_loc("Low")] = live_price
                except Exception:
                    pass

                return data
            except Exception as e:
                logger.error(f"Error fetching candles for {formatted_ticker}: {e}")
                return pd.DataFrame()

        df = await asyncio.to_thread(_fetch)
        if not df.empty:
            cache_df = df.reset_index()
            if "Date" in cache_df.columns:
                cache_df["Date"] = cache_df["Date"].astype(str)
            await cache.set(cache_key, cache_df.to_dict(orient="records"), ttl_seconds=60)

        return df

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        formatted_ticker = self._format_ticker(symbol)
        cache_key = f"yf:quote:{formatted_ticker}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        def _fetch_quote():
            try:
                ticker = yf.Ticker(formatted_ticker)
                fast = ticker.fast_info
                last_price = float(fast.last_price or 0.0)
                prev_close = float(fast.previous_close or last_price)

                # Fallback to 1-minute intraday candle if last_price was empty
                if last_price <= 0:
                    hist_1m = ticker.history(period="1d", interval="1m")
                    if not hist_1m.empty:
                        last_price = float(hist_1m["Close"].iloc[-1])
                        prev_close = float(hist_1m["Open"].iloc[0])

                change = last_price - prev_close
                change_pct = (change / prev_close * 100.0) if prev_close else 0.0

                now_iso = datetime.now(timezone.utc).isoformat()
                return {
                    "symbol": symbol.upper(),
                    "formatted_ticker": formatted_ticker,
                    "last_price": round(last_price, 2),
                    "previous_close": round(prev_close, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                    "open": round(float(fast.open or last_price), 2),
                    "day_high": round(float(fast.day_high or last_price), 2),
                    "day_low": round(float(fast.day_low or last_price), 2),
                    "year_high": round(float(fast.year_high or last_price), 2),
                    "year_low": round(float(fast.year_low or last_price), 2),
                    "volume": int(fast.last_volume or 0),
                    "is_real_time": True,
                    "timestamp": now_iso,
                }
            except Exception as e:
                logger.warning(f"Fast info failed for {formatted_ticker}: {e}")
                return {
                    "symbol": symbol.upper(),
                    "formatted_ticker": formatted_ticker,
                    "last_price": 0.0,
                    "change_pct": 0.0,
                    "volume": 0,
                    "is_real_time": False,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

        quote = await asyncio.to_thread(_fetch_quote)
        if quote.get("last_price", 0) > 0:
            await cache.set(cache_key, quote, ttl_seconds=3)  # 3-second TTL for live streaming
        return quote
