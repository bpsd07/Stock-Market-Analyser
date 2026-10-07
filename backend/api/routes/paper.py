"""Paper Trading & Execution Endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from backend.execution.broker_adapter import PaperTradingBroker

router = APIRouter(prefix="/paper", tags=["Paper Trading"])

# Singleton in-memory paper trading broker for session
paper_broker = PaperTradingBroker(initial_capital=1000000.0)


class OrderRequest(BaseModel):
    symbol: str
    side: str = Field(description="BUY | SELL")
    quantity: int = Field(gt=0)
    order_type: str = Field(default="MARKET", description="MARKET | LIMIT | SL")
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    target: Optional[float] = None


@router.get("/balance")
async def get_paper_balance():
    """Fetch virtual account balance, equity, and MTM returns."""
    return await paper_broker.get_balance()


@router.get("/positions")
async def get_paper_positions():
    """Fetch virtual portfolio open positions."""
    return {"positions": await paper_broker.get_positions()}


@router.get("/orders")
async def get_paper_orders():
    """Fetch virtual order history."""
    return {"orders": await paper_broker.get_orders()}


@router.post("/order")
async def place_paper_order(req: OrderRequest):
    """Place a simulated paper trading order with tax and margin validation."""
    order = await paper_broker.place_order(
        symbol=req.symbol,
        side=req.side,
        quantity=req.quantity,
        order_type=req.order_type,
        price=req.price,
        stop_loss=req.stop_loss,
        target=req.target,
    )
    if order.get("status") == "REJECTED":
        raise HTTPException(status_code=400, detail=order.get("reason"))
    return order
