"""NSE India Data Provider.
Fetches official index constituent CSVs and symbol directories directly from
archives.nseindia.com with caching and fallback.
Reuses and hardens Screeni-py's validated NSE URL definitions.
"""
import io
import csv
import logging
from typing import List, Dict, Optional
import httpx
import pandas as pd
from backend.core.cache import cache

logger = logging.getLogger(__name__)

NSE_INDEX_URLS = {
    "NIFTY_50": "https://archives.nseindia.com/content/indices/ind_nifty50list.csv",
    "NIFTY_NEXT_50": "https://archives.nseindia.com/content/indices/ind_niftynext50list.csv",
    "NIFTY_100": "https://archives.nseindia.com/content/indices/ind_nifty100list.csv",
    "NIFTY_200": "https://archives.nseindia.com/content/indices/ind_nifty200list.csv",
    "NIFTY_500": "https://archives.nseindia.com/content/indices/ind_nifty500list.csv",
    "NIFTY_MIDCAP_50": "https://archives.nseindia.com/content/indices/ind_niftymidcap50list.csv",
    "NIFTY_MIDCAP_100": "https://archives.nseindia.com/content/indices/ind_niftymidcap100list.csv",
    "NIFTY_MIDCAP_150": "https://archives.nseindia.com/content/indices/ind_niftymidcap150list.csv",
    "NIFTY_SMALLCAP_50": "https://archives.nseindia.com/content/indices/ind_niftysmallcap50list.csv",
    "NIFTY_SMALLCAP_100": "https://archives.nseindia.com/content/indices/ind_niftysmallcap100list.csv",
    "NIFTY_SMALLCAP_250": "https://archives.nseindia.com/content/indices/ind_niftysmallcap250list.csv",
    "ALL_EQUITIES": "https://archives.nseindia.com/content/equities/EQUITY_L.csv",
}

# Reliable fallback symbols for Nifty 50 in case of network unavailability
FALLBACK_NIFTY_50 = [
    "RELIANCE", "TCS", "HDFCBANK", "BHARTIARTL", "ICICIBANK", "INFY", "ITC",
    "HINDUNILVR", "LT", "SBIN", "BAJFINANCE", "HCLTECH", "M&M", "SUNPHARMA",
    "KOTAKBANK", "MARUTI", "AXISBANK", "TITAN", "ULTRACEMCO", "NTPC", "TATAMOTORS",
    "ONGC", "POWERGRID", "ADANIENT", "ADANIPORTS", "COALINDIA", "BAJAJFINSV",
    "TATASTEEL", "ASIANPAINT", "JSWSTEEL", "SIEMENS", "BEL", "NESTLEIND",
    "GRASIM", "TECHM", "WIPRO", "HINDALCO", "BPCL", "HEROMOTOCO", "EICHERMOT",
    "DIVISLAB", "CIPLA", "APOLLOHOSP", "DRREDDY", "BRITANNIA", "TATACONSUM",
    "SBILIFE", "HDFCLIFE", "SHRIRAMFIN", "INDUSINDBK"
]


class NSEProvider:
    """Manages official NSE symbol universe retrieval."""

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    async def fetch_index_symbols(self, index_key: str = "NIFTY_50") -> List[str]:
        cache_key = f"nse:symbols:{index_key.upper()}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        normalized_key = index_key.upper().replace(" ", "_").replace("-", "_")
        url = NSE_INDEX_URLS.get(normalized_key)

        if not url:
            # Check default
            url = NSE_INDEX_URLS["NIFTY_50"]

        try:
            async with httpx.AsyncClient(timeout=15.0, headers=self.headers, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    df = pd.read_csv(io.StringIO(response.text))
                    # Standard NSE CSV column name is 'Symbol' or 'SYMBOL'
                    symbol_col = next((c for c in df.columns if c.upper() == "SYMBOL"), None)
                    if symbol_col:
                        symbols = [str(s).strip().upper() for s in df[symbol_col].dropna().tolist()]
                        if symbols:
                            await cache.set(cache_key, symbols, ttl_seconds=86400)  # 24 hour TTL
                            logger.info(f"Fetched {len(symbols)} symbols for {index_key} from NSE archives.")
                            return symbols
        except Exception as e:
            logger.warning(f"Error fetching symbols from NSE URL {url}: {e}. Using fallback.")

        # If fetching fails, return fallback
        if "50" in normalized_key:
            return FALLBACK_NIFTY_50
        return FALLBACK_NIFTY_50[:20]
