"""Macro & Geopolitical Intelligence Endpoints."""
from fastapi import APIRouter
from backend.data.macro_provider import MacroProvider
from backend.events.causal_engine import CausalIntelligenceEngine

router = APIRouter(prefix="/macro", tags=["Macro Intelligence"])
macro_provider = MacroProvider()
causal_engine = CausalIntelligenceEngine()


@router.get("/dashboard")
async def get_macro_dashboard():
    """Fetch global & Indian macro indicators and market regime."""
    return await macro_provider.get_macro_dashboard()


@router.get("/causal-chain")
async def get_causal_shock_chain(headline: str = "Middle East Escalation - Crude Spikes 10%"):
    """Generates the systemic transmission chain for a geopolitical/macro shock."""
    return causal_engine.evaluate_event_impact(
        event_type="GEOPOLITICAL", headline=headline, severity="HIGH"
    )
