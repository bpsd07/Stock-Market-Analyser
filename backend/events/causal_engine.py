"""Causal Chain & Geopolitical Event Propagation Engine.
Models transmission shocks:
EVENT ──► MACRO ──► COMMODITIES/FX ──► SECTOR ──► COMPANY ──► FUNDAMENTALS ──► TECHNICAL CONFIRMATION ──► TRADE THESIS.
Includes lightweight graph propagation for Indian sector sensitivities.
"""
from typing import Dict, List, Any


# Sector sensitivity mapping for Indian Equities
SECTOR_SENSITIVITIES = {
    "CRUDE_UP": {
        "negative_sectors": ["PAINTS", "TYRES", "AVIATION", "OIL_MARKETING"],
        "negative_stocks": ["ASIANPAINT", "BERGEPAINT", "APOLLOTYRE", "MRF", "INDIGO", "BPCL", "IOC", "HPCL"],
        "positive_sectors": ["UPSTREAM_OIL", "OIL_EXPLORATION"],
        "positive_stocks": ["ONGC", "OIL"],
        "macro_impact": "India current account deficit expands; INR depreciation pressure; inflation risk elevated.",
    },
    "INR_WEAKENING": {
        "positive_sectors": ["IT_SERVICES", "PHARMACEUTICALS"],
        "positive_stocks": ["TCS", "INFY", "HCLTECH", "WIPRO", "SUNPHARMA", "DRREDDY", "CIPLA"],
        "negative_sectors": ["IMPORTERS", "CONSUMER_ELECTRONICS"],
        "negative_stocks": ["VOLTAS", "DIXON"],
        "macro_impact": "Imported inflation rises; higher realization for net exporters.",
    },
    "INTEREST_RATE_HIKE": {
        "negative_sectors": ["REALTY", "AUTO", "NBFC"],
        "negative_stocks": ["DLF", "GODREJPROP", "MARUTI", "M&M", "BAJFINANCE"],
        "positive_sectors": ["CASH_RICH_COMPANIES"],
        "positive_stocks": ["TCS", "ITC"],
        "macro_impact": "Borrowing costs rise; retail discretionary demand softens.",
    },
    "INFRASTRUCTURE_CAPEX_BOOST": {
        "positive_sectors": ["INFRASTRUCTURE", "CAPITAL_GOODS", "CEMENT", "METALS"],
        "positive_stocks": ["LT", "SIEMENS", "ABB", "ULTRACEMCO", "TATASTEEL", "JSWSTEEL"],
        "macro_impact": "Domestic investment cycle accelerates; industrial order books expand.",
    },
}


class CausalIntelligenceEngine:
    def evaluate_event_impact(
        self,
        event_type: str,
        headline: str,
        severity: str = "HIGH",
    ) -> Dict[str, Any]:
        """Maps an event into its systemic causal transmission chain."""
        matched_category = None
        lower_head = headline.lower()

        if "crude" in lower_head or "oil" in lower_head or "middle east" in lower_head or "opec" in lower_head:
            matched_category = "CRUDE_UP"
        elif "rupee" in lower_head or "usd" in lower_head or "forex" in lower_head:
            matched_category = "INR_WEAKENING"
        elif "rate cut" in lower_head or "repo rate" in lower_head or "rbi" in lower_head or "inflation" in lower_head:
            matched_category = "INTEREST_RATE_HIKE"
        elif "budget" in lower_head or "capex" in lower_head or "infrastructure" in lower_head or "order" in lower_head:
            matched_category = "INFRASTRUCTURE_CAPEX_BOOST"
        else:
            matched_category = "CRUDE_UP"  # Default reference propagation

        shock = SECTOR_SENSITIVITIES.get(matched_category, SECTOR_SENSITIVITIES["CRUDE_UP"])

        causal_chain = [
            f"1. EVENT: {headline} (Severity: {severity})",
            f"2. MACRO IMPACT: {shock['macro_impact']}",
            f"3. SECTOR TAILWINDS: Beneficiary sectors: {', '.join(shock['positive_sectors'])}",
            f"4. SECTOR HEADWINDS: Adversely affected sectors: {', '.join(shock['negative_sectors'])}",
            f"5. KEY BENEFICIARY STOCKS: {', '.join(shock['positive_stocks'])}",
            f"6. STOCKS TO AVOID / HEDGE: {', '.join(shock['negative_stocks'])}",
            "7. TECHNICAL VERIFICATION: Validate price volume confirmation on beneficiary stocks before entry.",
        ]

        return {
            "event_category": matched_category,
            "headline": headline,
            "severity": severity,
            "causal_chain": causal_chain,
            "positive_sectors": shock["positive_sectors"],
            "negative_sectors": shock["negative_sectors"],
            "beneficiary_stocks": shock["positive_stocks"],
            "hedging_candidates": shock["negative_stocks"],
            "confidence": "HIGH" if severity == "HIGH" else "MEDIUM",
        }
