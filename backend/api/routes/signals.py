"""Signal Fusion & NO-TRADE Decision Endpoints."""
from fastapi import APIRouter, HTTPException
from backend.signals.fusion_engine import SignalFusionEngine
from backend.data.yahoo_provider import YahooFinanceProvider
from backend.fundamentals.fundamental_engine import FundamentalEngine
from backend.data.macro_provider import MacroProvider
from backend.indicators.technical import compute_technical_snapshot
from backend.screening.screenipy_strategies import check_breakout, check_vcp, check_five_ema

router = APIRouter(prefix="/signals", tags=["Signal Fusion"])
fusion_engine = SignalFusionEngine()
market_provider = YahooFinanceProvider()
fundamental_engine = FundamentalEngine()
macro_provider = MacroProvider()


@router.get("/generate/{symbol}")
async def generate_fused_signal(symbol: str):
    """Calculates fused multi-factor signal or invokes mandatory NO-TRADE protocol."""
    sym = symbol.upper()
    df = await market_provider.get_historical_candles(sym, period="1y", interval="1d")
    if df.empty or len(df) < 20:
        raise HTTPException(status_code=404, detail=f"Data unavailable for {sym}")

    enriched = compute_technical_snapshot(df)
    last = enriched.iloc[-1]

    triggers = []
    bo = check_breakout(enriched)
    if bo:
        triggers.append(bo)
    vcp = check_vcp(enriched)
    if vcp:
        triggers.append(vcp)
    fem = check_five_ema(enriched)
    if fem:
        triggers.append(fem)

    tech_data = {
        "last_price": round(float(last["Close"]), 2),
        "rsi_14": round(float(last.get("RSI_14", 50.0)), 1),
        "volume": int(last["Volume"]),
        "volume_ratio": float(last.get("Vol_Ratio", 1.0)),
        "is_stage_2": float(last["Close"]) > float(last.get("SMA_50", 0.0)) > float(last.get("SMA_200", 0.0)),
        "triggers": triggers,
    }

    fund_data = await fundamental_engine.get_fundamentals(sym)
    macro_data = await macro_provider.get_macro_dashboard()

    signal = fusion_engine.compute_signal(
        symbol=sym,
        technical_data=tech_data,
        fundamental_data=fund_data,
        macro_data=macro_data,
    )
    return signal
