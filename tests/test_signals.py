"""Unit tests for signal fusion and NO-TRADE protocol."""
import pytest
from backend.signals.fusion_engine import SignalFusionEngine


def test_no_trade_on_zero_price():
    engine = SignalFusionEngine()
    result = engine.compute_signal(
        symbol="TESTSTOCK",
        technical_data={"last_price": 0.0, "volume": 0},
        fundamental_data={},
        macro_data={"regime": "Neutral"},
    )
    assert result["direction"] == "NO_TRADE"
    assert result["no_trade_reason"] == "MISSING_PRICE_DATA"


def test_no_trade_on_penny_stock():
    engine = SignalFusionEngine()
    result = engine.compute_signal(
        symbol="PENNY",
        technical_data={"last_price": 4.5, "volume": 1000},
        fundamental_data={},
        macro_data={"regime": "Neutral"},
    )
    assert result["direction"] == "NO_TRADE"
    assert result["no_trade_reason"] == "ILLIQUID_INSTRUMENT"


def test_bullish_signal_generation():
    engine = SignalFusionEngine()
    result = engine.compute_signal(
        symbol="GOODSTOCK",
        technical_data={"last_price": 500.0, "volume": 500000, "volume_ratio": 2.2, "rsi_14": 62.0, "is_stage_2": True, "triggers": [{"strategy": "VCP"}]},
        fundamental_data={"roce_pct": 24.0, "debt_to_equity": 0.2, "valuation_grade": "FAIRLY_VALUED"},
        macro_data={"regime": "Risk-on / Expansion", "india_vix": 13.5},
    )
    assert result["direction"] == "BULLISH"
    assert result["total_score"] >= 65.0
    assert result["risk_reward_ratio"] >= 2.0
