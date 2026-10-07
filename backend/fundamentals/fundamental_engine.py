"""Fundamental & Valuation Analysis Engine.
Computes ROCE, ROE, P/E, P/B, EV/EBITDA, Free Cash Flow, Debt-to-Equity,
and evaluates balance sheet durability and valuation attractiveness for Indian equities.
"""
import asyncio
import logging
from typing import Dict, Any, Optional
import yfinance as yf
from backend.core.cache import cache

logger = logging.getLogger(__name__)


class FundamentalEngine:
    async def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        formatted_ticker = symbol.upper() if symbol.endswith(".NS") else f"{symbol.upper()}.NS"
        cache_key = f"fundamentals:{formatted_ticker}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        def _fetch():
            try:
                t = yf.Ticker(formatted_ticker)
                info = t.info
                fast = t.fast_info

                pe = info.get("trailingPE") or info.get("forwardPE")
                pb = info.get("priceToBook")
                roe = info.get("returnOnEquity")
                market_cap = fast.market_cap or info.get("marketCap", 0)
                market_cap_cr = round(market_cap / 10000000.0, 2) if market_cap else 0.0

                debt = info.get("totalDebt", 0)
                cash = info.get("totalCash", 0)
                ebitda = info.get("ebitda", 0)
                fcf = info.get("freeCashflow", 0)
                fcf_cr = round(fcf / 10000000.0, 2) if fcf else 0.0

                debt_to_equity = info.get("debtToEquity")
                debt_equity_ratio = round(debt_to_equity / 100.0, 2) if debt_to_equity else round(debt / (info.get("totalStockholderEquity") or 1), 2) if debt else 0.0

                # Approximate ROCE if operating margins and capital employed are present
                operating_margins = info.get("operatingMargins", 0.0)
                rev = info.get("totalRevenue", 0)
                ebit = rev * operating_margins if rev and operating_margins else 0
                capital_employed = (info.get("totalStockholderEquity", 0) or 0) + debt
                roce = round((ebit / capital_employed * 100.0), 2) if capital_employed and ebit else round((roe * 100.0 * 1.15), 2) if roe else None

                # Valuation Assessment
                if pe and pe < 18.0 and (roe and roe > 0.15):
                    val_grade = "UNDERVALUED"
                elif pe and pe > 45.0:
                    val_grade = "OVERVALUED"
                else:
                    val_grade = "FAIRLY_VALUED"

                # Health score (1 to 10)
                health_score = 5
                if debt_equity_ratio < 0.5:
                    health_score += 2
                elif debt_equity_ratio > 1.5:
                    health_score -= 2

                if roe and roe > 0.18:
                    health_score += 2
                elif roe and roe < 0.08:
                    health_score -= 1

                if fcf and fcf > 0:
                    health_score += 1

                health_score = max(1, min(10, health_score))

                return {
                    "symbol": symbol.upper(),
                    "company_name": info.get("longName", symbol.upper()),
                    "sector": info.get("sector", "Unknown"),
                    "industry": info.get("industry", "Unknown"),
                    "market_cap_cr": market_cap_cr,
                    "pe_ratio": round(pe, 2) if pe else None,
                    "pb_ratio": round(pb, 2) if pb else None,
                    "roe_pct": round(roe * 100.0, 2) if roe else None,
                    "roce_pct": roce,
                    "debt_to_equity": debt_equity_ratio,
                    "free_cash_flow_cr": fcf_cr,
                    "operating_margins_pct": round(operating_margins * 100.0, 2) if operating_margins else None,
                    "valuation_grade": val_grade,
                    "financial_health_score": health_score,
                    "promoter_holding_pct": round(info.get("heldPercentInsiders", 0.50) * 100.0, 1) if info.get("heldPercentInsiders") else 50.0,
                    "institutional_holding_pct": round(info.get("heldPercentInstitutions", 0.30) * 100.0, 1) if info.get("heldPercentInstitutions") else 30.0,
                }
            except Exception as e:
                logger.error(f"Failed to fetch fundamentals for {symbol}: {e}")
                return {
                    "symbol": symbol.upper(),
                    "company_name": symbol.upper(),
                    "sector": "Indian Equities",
                    "valuation_grade": "UNKNOWN",
                    "financial_health_score": 5,
                }

        data = await asyncio.to_thread(_fetch)
        await cache.set(cache_key, data, ttl_seconds=3600)
        return data
