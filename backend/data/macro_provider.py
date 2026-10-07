"""Macroeconomic & Global Market Intelligence Provider.
Monitors Indian and global benchmark indices, commodities, currencies, interest rates,
and classifies the prevailing macroeconomic regime.
"""
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
import yfinance as yf
from backend.core.cache import cache

logger = logging.getLogger(__name__)

MACRO_TICKERS = {
    "NIFTY_50": "^NSEI",
    "BANK_NIFTY": "^NSEBANK",
    "SENSEX": "^BSESN",
    "INDIA_VIX": "^INDIAVIX",
    "USD_INR": "INR=X",
    "BRENT_CRUDE": "BZ=F",
    "WTI_CRUDE": "CL=F",
    "GOLD": "GC=F",
    "US_10Y_YIELD": "^TNX",
    "SP500": "^GSPC",
    "NASDAQ": "^IXIC",
    "NIKKEI_225": "^N225",
    "HANG_SENG": "^HSI",
}


class MacroProvider:
    """Fetches macro indicators and classifies market regime."""

    async def get_macro_dashboard(self) -> Dict[str, Any]:
        cache_key = "macro:dashboard:summary"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        def _fetch_macro():
            results = {}
            for name, ticker_symbol in MACRO_TICKERS.items():
                try:
                    t = yf.Ticker(ticker_symbol)
                    fast = t.fast_info
                    price = float(fast.last_price or 0.0)
                    prev = float(fast.previous_close or price)
                    chg_pct = round(((price - prev) / prev * 100.0), 2) if prev else 0.0
                    results[name] = {
                        "symbol": ticker_symbol,
                        "value": round(price, 2),
                        "change_pct": chg_pct,
                    }
                except Exception as e:
                    logger.debug(f"Failed to fetch macro ticker {name}: {e}")
                    results[name] = {"symbol": ticker_symbol, "value": 0.0, "change_pct": 0.0}
            return results

        data = await asyncio.to_thread(_fetch_macro)

        # Classify regime based on VIX, Crude, USD/INR, and Nifty momentum
        vix = data.get("INDIA_VIX", {}).get("value", 14.0)
        crude_pct = data.get("BRENT_CRUDE", {}).get("change_pct", 0.0)
        nifty_pct = data.get("NIFTY_50", {}).get("change_pct", 0.0)
        usdinr_pct = data.get("USD_INR", {}).get("change_pct", 0.0)

        # Quantitative regime determination
        if vix > 22.0 or (nifty_pct < -1.5 and crude_pct > 3.0):
            regime = "Crisis / Extreme Risk-Off"
            risk_appetite = "DEFENSIVE"
        elif vix > 17.0 or nifty_pct < -0.8:
            regime = "Risk-off / High Volatility"
            risk_appetite = "CAUTIOUS"
        elif crude_pct > 2.5 and usdinr_pct > 0.3:
            regime = "Inflationary / Rupee Pressure"
            risk_appetite = "SELECTIVE"
        elif vix < 14.0 and nifty_pct > 0.4:
            regime = "Risk-on / Bullish Expansion"
            risk_appetite = "AGGRESSIVE"
        else:
            regime = "Neutral / Sideways Rangebound"
            risk_appetite = "MODERATE"

        output = {
            "timestamp": datetime.utcnow().isoformat(),
            "regime": regime,
            "risk_appetite": risk_appetite,
            "india_vix": vix,
            "indicators": data,
            "policy_rates": {
                "rbi_repo_rate": 6.50,
                "rbi_stance": "Withdrawal of accommodation",
                "us_fed_funds_rate": "5.25 - 5.50",
                "india_10y_gsec_yield": 7.08,
            },
            "summary": (
                f"Market is in '{regime}' regime. India VIX is at {vix}. "
                f"Risk appetite characterized as {risk_appetite}."
            ),
        }

        await cache.set(cache_key, output, ttl_seconds=300)
        return output
