"""Stock Scanner Endpoints."""
from fastapi import APIRouter, Query
from typing import Dict, Any, List
from backend.screening.screener_engine import ScreenerEngine

router = APIRouter(prefix="/scanner", tags=["Stock Scanner"])
screener_engine = ScreenerEngine()


@router.get("/strategies")
async def get_available_strategies():
    """List supported screening setups."""
    return {
        "strategies": [
            {"id": "ALL", "name": "All Technical Triggers"},
            {"id": "MOMENTUM_BREAKOUT", "name": "50-Day High Breakout with Volume Surge"},
            {"id": "VCP_CONTRACTION", "name": "Volatility Contraction Pattern (Minervini VCP)"},
            {"id": "5_EMA_REVERSAL_BUY", "name": "5-EMA Mean Reversion Long"},
            {"id": "5_EMA_REVERSAL_SHORT", "name": "5-EMA Mean Reversion Short"},
            {"id": "VSA_SUPPLY_DROUGHT", "name": "Volume Spread Analysis: Supply Drought"},
            {"id": "VSA_DEMAND_RISE", "name": "Volume Spread Analysis: Demand Rise"},
            {"id": "NR_7", "name": "Narrow Range 7 (NR7) Compression"},
        ]
    }


@router.get("/run")
async def run_screening_scan(
    universe: str = Query("NIFTY_50", description="NIFTY_50 | NIFTY_100 | NIFTY_500"),
    strategy: str = Query("ALL", description="Target strategy code"),
    limit: int = Query(30, description="Max symbols to screen"),
):
    """Executes high-performance screening scan."""
    results = await screener_engine.run_scan(universe=universe, strategy=strategy, max_symbols=limit)
    return {
        "universe": universe,
        "strategy": strategy,
        "matches_count": len(results),
        "results": results,
    }
