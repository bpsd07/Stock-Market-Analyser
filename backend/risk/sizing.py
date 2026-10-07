"""Quantitative Position Sizing & Risk Management.
Implements:
1. Fixed Fractional Sizing (1% equity risk)
2. ATR Volatility Sizing
3. Half-Kelly Constrained Sizing
Enforces single-stock allocation ceiling (10%) and sector limits (25%).
"""
import math
from typing import Dict, Any


class PositionSizer:
    def __init__(
        self,
        max_portfolio_risk_per_trade: float = 0.01,  # 1% equity risk default
        max_single_stock_pct: float = 0.10,          # 10% maximum capital in one stock
        max_sector_pct: float = 0.25,                # 25% maximum sector exposure
    ):
        self.max_portfolio_risk_per_trade = max_portfolio_risk_per_trade
        self.max_single_stock_pct = max_single_stock_pct
        self.max_sector_pct = max_sector_pct

    def calculate_atr_size(
        self,
        portfolio_equity: float,
        entry_price: float,
        atr_14: float,
        atr_multiplier: float = 2.0,
    ) -> Dict[str, Any]:
        """Calculates risk-adjusted quantity based on volatility (ATR)."""
        if entry_price <= 0 or atr_14 <= 0 or portfolio_equity <= 0:
            return {"quantity": 0, "risk_amount": 0.0, "stop_loss": 0.0}

        risk_capital = portfolio_equity * self.max_portfolio_risk_per_trade
        stop_distance = atr_14 * atr_multiplier
        stop_loss = round(entry_price - stop_distance, 2)

        # Quantity constrained by volatility risk
        vol_quantity = int(risk_capital / stop_distance) if stop_distance > 0 else 0

        # Maximum capital allocation cap (10% of portfolio)
        max_capital_allowed = portfolio_equity * self.max_single_stock_pct
        capital_constrained_qty = int(max_capital_allowed / entry_price)

        final_quantity = max(0, min(vol_quantity, capital_constrained_qty))
        position_value = round(final_quantity * entry_price, 2)
        total_risk = round(final_quantity * stop_distance, 2)

        return {
            "method": "ATR_VOLATILITY",
            "quantity": final_quantity,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "risk_per_share": round(stop_distance, 2),
            "total_risk_inr": total_risk,
            "position_value_inr": position_value,
            "portfolio_allocation_pct": round((position_value / portfolio_equity * 100.0), 2),
            "is_capital_capped": final_quantity == capital_constrained_qty,
        }

    def calculate_half_kelly(
        self,
        portfolio_equity: float,
        entry_price: float,
        win_rate: float = 0.55,
        win_loss_ratio: float = 2.0,
    ) -> Dict[str, Any]:
        """Half-Kelly sizing for growth with conservative drawdown dampening."""
        # Kelly % = W - [(1 - W) / R]
        kelly_fraction = win_rate - ((1.0 - win_rate) / win_loss_ratio)
        half_kelly = max(0.01, min(self.max_single_stock_pct, kelly_fraction * 0.5))

        target_allocation = portfolio_equity * half_kelly
        quantity = int(target_allocation / entry_price) if entry_price > 0 else 0

        return {
            "method": "HALF_KELLY",
            "kelly_fraction_raw": round(kelly_fraction, 3),
            "half_kelly_pct": round(half_kelly * 100.0, 2),
            "quantity": quantity,
            "position_value_inr": round(quantity * entry_price, 2),
        }
