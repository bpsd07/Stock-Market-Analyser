"""AI Analyst Mesh & Multi-Agent Deliberation Endpoints."""
from fastapi import APIRouter, HTTPException
from backend.agents.analysts import AIAnalystMesh, ANALYST_ROLES
from backend.data.yahoo_provider import YahooFinanceProvider
from backend.fundamentals.fundamental_engine import FundamentalEngine
from backend.data.macro_provider import MacroProvider
from backend.indicators.technical import compute_technical_snapshot

router = APIRouter(prefix="/agents", tags=["AI Analysts"])
agent_mesh = AIAnalystMesh()
market_provider = YahooFinanceProvider()
fundamental_engine = FundamentalEngine()
macro_provider = MacroProvider()


@router.get("/roles")
async def get_analyst_roles():
    """List the 14 specialized AI analyst personas including the mandatory Bear Analyst."""
    return {"roles": ANALYST_ROLES}


@router.get("/analyze/{symbol}")
async def run_multi_agent_deliberation(symbol: str):
    """Executes multi-agent committee debate, Bear Analyst critique, and trade plan synthesis."""
    sym = symbol.upper()
    df = await market_provider.get_historical_candles(sym, period="1y", interval="1d")
    if df.empty or len(df) < 10:
        raise HTTPException(status_code=404, detail=f"Data unavailable for {sym}")

    enriched = compute_technical_snapshot(df)
    last = enriched.iloc[-1]

    tech_data = {
        "last_price": round(float(last["Close"]), 2),
        "rsi_14": round(float(last.get("RSI_14", 50.0)), 1),
        "volume": int(last["Volume"]),
        "volume_ratio": float(last.get("Vol_Ratio", 1.0)),
        "is_stage_2": float(last["Close"]) > float(last.get("SMA_50", 0.0)) > float(last.get("SMA_200", 0.0)),
    }

    fund_data = await fundamental_engine.get_fundamentals(sym)
    macro_data = await macro_provider.get_macro_dashboard()

    analysis = await agent_mesh.analyze_stock(
        symbol=sym,
        technical_data=tech_data,
        fundamental_data=fund_data,
        macro_data=macro_data,
    )
    return analysis
