"""Unit tests for Indian statutory transaction costs."""
import pytest
from backend.backtesting.indian_tax_model import IndianTransactionCostCalculator


def test_indian_tax_delivery_costs():
    calc = IndianTransactionCostCalculator()
    # Buy 100 shares @ ₹1000 = ₹1,00,000 turnover
    # Sell 100 shares @ ₹1100 = ₹1,10,000 turnover
    costs = calc.calculate_trade_costs(buy_price=1000.0, sell_price=1100.0, quantity=100, is_delivery=True)

    # STT: 0.1% on buy (₹100) + 0.1% on sell (₹110) = ₹210
    assert costs["stt"] == 210.0
    # Stamp duty: 0.015% on buy side only (₹1,00,000 * 0.00015 = ₹15)
    assert costs["stamp_duty"] == 15.0
    # Brokerage: ₹20 buy + ₹20 sell = ₹40
    assert costs["brokerage"] == 40.0
    # Frictional costs must be strictly positive
    assert costs["total_frictional_cost"] > 300.0
