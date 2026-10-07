"""Quantitative Backtesting Endpoints."""
from fastapi import APIRouter, HTTPException, Query
from backend.backtesting.engine import BacktestEngine
from backend.data.yahoo_provider import YahooFinanceProvider

router = APIRouter(prefix="/backtest", tags=["Backtesting"])
backtester = BacktestEngine(initial_capital=1000000.0)
market_provider = YahooFinanceProvider()


@router.get("/run")
async def run_backtest_simulation(
    symbol: str = Query("RELIANCE", description="Stock symbol to backtest"),
    strategy: str = Query("MOMENTUM_BREAKOUT", description="MOMENTUM_BREAKOUT | EMA_CROSSOVER | RSI_PULLBACK"),
    period: str = Query("2y", description="Historical period: 1y | 2y | 5y"),
):
    """Executes backtest with Indian statutory charges and slippage deduction."""
    sym = symbol.upper()
    df = await market_provider.get_historical_candles(sym, period=period, interval="1d")
    if df.empty or len(df) < 60:
        raise HTTPException(status_code=400, detail=f"Insufficient history for {sym}")

    result = backtester.run_strategy_backtest(df, strategy_name=strategy)
    result["symbol"] = sym
    return result
