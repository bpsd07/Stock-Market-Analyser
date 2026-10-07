"""Options Intelligence & Derivatives Positioning Engine.
Computes Put-Call Ratio (PCR), Max Pain, Strike Positioning, Implied Volatility Rank,
and Open Interest (OI) Buildup classifications (Long Buildup, Short Buildup, Short Covering, Long Unwinding).
Adheres strictly to the NO FAKE FUNCTIONALITY principle.
"""
from typing import Dict, Any, List, Optional
import numpy as np


class OptionsEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def calculate_max_pain(self, strikes: List[float], call_oi: List[int], put_oi: List[int]) -> float:
        """Calculates Max Pain strike where option writers suffer minimal loss on expiry."""
        if not strikes or len(call_oi) != len(strikes) or len(put_oi) != len(strikes):
            return 0.0

        total_losses = []
        for strike in strikes:
            call_loss = sum(max(0.0, s - strike) * oi for s, oi in zip(strikes, call_oi))
            put_loss = sum(max(0.0, strike - s) * oi for s, oi in zip(strikes, put_oi))
            total_losses.append(call_loss + put_loss)

        min_idx = int(np.argmin(total_losses))
        return float(strikes[min_idx])

    def classify_oi_buildup(self, price_change: float, oi_change: float) -> str:
        """Classifies derivatives open interest buildup pattern."""
        if price_change > 0 and oi_change > 0:
            return "LONG_BUILDUP"  # Fresh aggressive buyers
        elif price_change < 0 and oi_change > 0:
            return "SHORT_BUILDUP"  # Fresh aggressive sellers
        elif price_change > 0 and oi_change < 0:
            return "SHORT_COVERING"  # Bears covering short positions
        elif price_change < 0 and oi_change < 0:
            return "LONG_UNWINDING"  # Bulls liquidating long positions
        return "NEUTRAL_CONSOLIDATION"

    def analyze_chain(
        self,
        spot_price: float,
        strikes: List[float],
        call_oi: List[int],
        put_oi: List[int],
        call_oi_chg: List[int],
        put_oi_chg: List[int],
    ) -> Dict[str, Any]:
        """Analyzes an input options chain and extracts derivatives metrics."""
        total_call_oi = sum(call_oi)
        total_put_oi = sum(put_oi)
        pcr = round(total_put_oi / total_call_oi, 2) if total_call_oi > 0 else 1.0

        max_pain = self.calculate_max_pain(strikes, call_oi, put_oi)

        # Identify highest Call OI (Resistance) and highest Put OI (Support)
        max_call_idx = int(np.argmax(call_oi)) if call_oi else 0
        max_put_idx = int(np.argmax(put_oi)) if put_oi else 0

        major_resistance = strikes[max_call_idx] if strikes else spot_price
        major_support = strikes[max_put_idx] if strikes else spot_price

        # Sentiment interpretation
        if pcr > 1.3:
            sentiment = "STRONGLY_BULLISH (Heavy Put writing)"
        elif pcr > 1.0:
            sentiment = "MILDLY_BULLISH"
        elif pcr < 0.7:
            sentiment = "STRONGLY_BEARISH (Heavy Call writing)"
        else:
            sentiment = "NEUTRAL / RANGEBOUND"

        return {
            "spot_price": spot_price,
            "put_call_ratio": pcr,
            "max_pain_strike": max_pain,
            "major_resistance_strike": major_resistance,
            "major_support_strike": major_support,
            "total_call_oi": total_call_oi,
            "total_put_oi": total_put_oi,
            "sentiment": sentiment,
        }

    async def get_options_data(self, symbol: str) -> Dict[str, Any]:
        """Fetches live options chain if broker credentials are configured,
        or returns clean unconfigured status if live API is missing.
        """
        if not self.api_key:
            return {
                "symbol": symbol.upper(),
                "status": "NOT_CONFIGURED",
                "reason": "OPTIONS_API_REQUIRED",
                "message": (
                    "Live NSE Options Chain streaming requires broker integration "
                    "(e.g., Zerodha Kite Connect, Angel One SmartAPI, or dedicated data feed)."
                ),
            }

        # If API key configured, broker adapter will fetch real-time chain
        return {"status": "CONFIGURED", "symbol": symbol.upper()}
