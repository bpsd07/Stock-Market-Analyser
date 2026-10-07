"""Signal Fusion & NO-TRADE Engine.
Combines Technical, Momentum, Fundamental, Valuation, Macro, and Risk metrics
into an explainable, probabilistic decision score.
Enforces the mandatory NO-TRADE filter whenever edge is insufficient or risk is unquantified.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class SignalFusionEngine:
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        # Default configurable weights summing to 1.0
        self.weights = weights or {
            "technical": 0.20,
            "momentum": 0.15,
            "fundamental": 0.15,
            "valuation": 0.10,
            "macro": 0.10,
            "institutional": 0.10,
            "news_catalyst": 0.10,
            "risk_penalty": -0.10,
        }

    def evaluate_no_trade_conditions(
        self,
        symbol: str,
        technical_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        macro_data: Dict[str, Any],
        risk_reward_ratio: float,
    ) -> Optional[Dict[str, Any]]:
        """Evaluates whether trade must be aborted under the NO-TRADE protocol.
        Returns NO-TRADE reason dict if any condition is breached, else None.
        """
        ltp = technical_data.get("last_price", 0.0)
        volume = technical_data.get("volume", 0)
        vix = macro_data.get("india_vix", 14.0)
        regime = macro_data.get("regime", "")

        # 1. Zero or corrupt market data
        if ltp <= 0:
            return {
                "decision": "NO_TRADE",
                "reason": "MISSING_PRICE_DATA",
                "explanation": f"LTP for {symbol} is zero or corrupt. Cannot formulate risk-managed entry.",
            }

        # 2. Poor liquidity / penny stock filter
        if ltp < 10.0 or (volume > 0 and volume < 25000):
            return {
                "decision": "NO_TRADE",
                "reason": "ILLIQUID_INSTRUMENT",
                "explanation": f"{symbol} exhibits insufficient volume ({volume} shares) or penny status (< ₹10). High slippage risk.",
            }

        # 3. Inadequate Risk/Reward
        if risk_reward_ratio < 1.5:
            return {
                "decision": "NO_TRADE",
                "reason": "UNFAVORABLE_RISK_REWARD",
                "explanation": f"Risk/Reward ratio ({round(risk_reward_ratio, 2)}) is below the required 1:1.5 threshold.",
            }

        # 4. Extreme systemic volatility crisis
        if vix > 28.0 or "Crisis" in regime:
            return {
                "decision": "NO_TRADE",
                "reason": "EXTREME_MARKET_VOLATILITY",
                "explanation": f"India VIX is at {vix} (extreme crisis regime). Capital preservation mandate requires pausing fresh directional bets.",
            }

        return None

    def compute_signal(
        self,
        symbol: str,
        technical_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        macro_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calculates total fusion score and generates trade thesis or NO-TRADE."""
        ltp = technical_data.get("last_price", 0.0)
        rsi = technical_data.get("rsi_14", 50.0)
        vol_ratio = technical_data.get("volume_ratio", 1.0)
        is_stage_2 = technical_data.get("is_stage_2", False)
        triggers = technical_data.get("triggers", [])

        # Technical score (0 to 100)
        tech_score = 50.0
        if is_stage_2:
            tech_score += 25.0
        if triggers:
            tech_score += 20.0
        tech_score = min(100.0, tech_score)

        # Momentum score (0 to 100)
        mom_score = 50.0
        if 55 <= rsi <= 68:
            mom_score += 30.0
        elif rsi > 70:
            mom_score -= 10.0  # Overbought penalty
        if vol_ratio > 1.5:
            mom_score += 20.0
        mom_score = max(0.0, min(100.0, mom_score))

        # Fundamental score (0 to 100)
        roce = fundamental_data.get("roce_pct") or 15.0
        debt_equity = fundamental_data.get("debt_to_equity") or 0.5
        fund_score = 50.0
        if roce > 18.0:
            fund_score += 25.0
        if debt_equity < 0.5:
            fund_score += 25.0
        elif debt_equity > 1.5:
            fund_score -= 30.0
        fund_score = max(0.0, min(100.0, fund_score))

        # Valuation score (0 to 100)
        val_grade = fundamental_data.get("valuation_grade", "FAIRLY_VALUED")
        val_score = 80.0 if val_grade == "UNDERVALUED" else (55.0 if val_grade == "FAIRLY_VALUED" else 30.0)

        # Macro score (0 to 100)
        regime = macro_data.get("regime", "Neutral")
        macro_score = 75.0 if "Risk-on" in regime else (35.0 if "Risk-off" in regime else 50.0)

        # Risk score penalty (0 to 100)
        risk_penalty_score = 25.0
        if rsi > 72.0 or debt_equity > 1.5:
            risk_penalty_score += 30.0

        # Weighted calculation
        total_score = (
            tech_score * self.weights["technical"]
            + mom_score * self.weights["momentum"]
            + fund_score * self.weights["fundamental"]
            + val_score * self.weights["valuation"]
            + macro_score * self.weights["macro"]
            + 60.0 * self.weights["institutional"]
            + 60.0 * self.weights["news_catalyst"]
            - (risk_penalty_score * abs(self.weights["risk_penalty"]))
        )
        total_score = round(max(0.0, min(100.0, total_score)), 1)

        # Price targets
        stop_loss = round(ltp * 0.95, 2)
        target = round(ltp * 1.12, 2)
        risk = max(ltp - stop_loss, 0.5)
        reward = max(target - ltp, 1.0)
        rr_ratio = round(reward / risk, 2)

        # Evaluate NO-TRADE filter
        no_trade = self.evaluate_no_trade_conditions(
            symbol, technical_data, fundamental_data, macro_data, rr_ratio
        )
        if no_trade:
            return {
                "symbol": symbol.upper(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "direction": "NO_TRADE",
                "total_score": total_score,
                "confidence": "LOW",
                "no_trade_reason": no_trade["reason"],
                "explanation": no_trade["explanation"],
            }

        # Direction and confidence
        if total_score >= 68.0:
            direction = "BULLISH"
            confidence = "HIGH" if total_score >= 78.0 else "MEDIUM"
        elif total_score <= 35.0:
            direction = "BEARISH"
            confidence = "MEDIUM"
        else:
            direction = "NEUTRAL"
            confidence = "LOW"

        return {
            "symbol": symbol.upper(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "direction": direction,
            "total_score": total_score,
            "confidence": confidence,
            "time_horizon": "2 to 8 WEEKS (SWING)",
            "last_price": ltp,
            "entry_range": f"₹{round(ltp * 0.99, 2)} - ₹{round(ltp * 1.01, 2)}",
            "stop_loss": stop_loss,
            "target_1": round(ltp * 1.08, 2),
            "target_2": target,
            "risk_reward_ratio": rr_ratio,
            "invalidation_level": stop_loss,
            "score_breakdown": {
                "technical": round(tech_score, 1),
                "momentum": round(mom_score, 1),
                "fundamental": round(fund_score, 1),
                "valuation": round(val_score, 1),
                "macro": round(macro_score, 1),
                "risk_penalty": round(risk_penalty_score, 1),
            },
        }
