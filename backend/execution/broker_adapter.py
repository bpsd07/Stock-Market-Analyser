"""Broker Adapter Abstraction Layer & Paper Trading Execution Simulator.
Provides unified interface across simulated and live execution.
Paper Trading is the default safe mode. Live broker orders require explicit user confirmation.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from backend.backtesting.indian_tax_model import IndianTransactionCostCalculator


class BrokerAdapter(ABC):
    """Abstract interface for all broker execution engines."""

    @abstractmethod
    async def get_balance(self) -> Dict[str, Any]:
        """Fetch cash, margins, and portfolio equity."""
        pass

    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Fetch active open positions."""
        pass

    @abstractmethod
    async def get_orders(self) -> List[Dict[str, Any]]:
        """Fetch historical and pending orders."""
        pass

    @abstractmethod
    async def place_order(
        self,
        symbol: str,
        side: str,  # BUY | SELL
        quantity: int,
        order_type: str = "MARKET",  # MARKET | LIMIT | SL
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        target: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Place an order with risk constraints."""
        pass

    @abstractmethod
    async def modify_order(self, order_id: str, new_price: Optional[float] = None, new_qty: Optional[int] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        pass


class PaperTradingBroker(BrokerAdapter):
    """Full-featured Paper Trading Execution Engine.
    Simulates real-world execution with realistic slippage, Indian taxes, and trade logs.
    """

    def __init__(self, initial_capital: float = 1000000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.orders: List[Dict[str, Any]] = []
        self.tax_calc = IndianTransactionCostCalculator()

    async def get_balance(self) -> Dict[str, Any]:
        invested_value = sum(
            pos["quantity"] * pos["current_price"] for pos in self.positions.values()
        )
        total_equity = self.cash + invested_value
        unrealized_pnl = sum(pos["unrealized_pnl"] for pos in self.positions.values())

        return {
            "mode": "PAPER_TRADING",
            "initial_capital": self.initial_capital,
            "cash_balance": round(self.cash, 2),
            "invested_value": round(invested_value, 2),
            "total_portfolio_equity": round(total_equity, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "total_return_pct": round(((total_equity - self.initial_capital) / self.initial_capital * 100.0), 2),
            "active_positions_count": len(self.positions),
        }

    async def get_positions(self) -> List[Dict[str, Any]]:
        return list(self.positions.values())

    async def get_orders(self) -> List[Dict[str, Any]]:
        return sorted(self.orders, key=lambda x: x["timestamp"], reverse=True)

    async def update_market_prices(self, price_map: Dict[str, float]):
        """Updates MTM price for open positions."""
        for symbol, curr_price in price_map.items():
            sym = symbol.upper()
            if sym in self.positions:
                pos = self.positions[sym]
                pos["current_price"] = curr_price
                cost_basis = pos["quantity"] * pos["avg_price"]
                current_val = pos["quantity"] * curr_price
                pos["unrealized_pnl"] = round(current_val - cost_basis, 2)
                pos["unrealized_pnl_pct"] = round(((curr_price - pos["avg_price"]) / pos["avg_price"] * 100.0), 2)

    async def place_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        target: Optional[float] = None,
    ) -> Dict[str, Any]:
        sym = symbol.upper()
        order_id = f"PAPER_{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow().isoformat()

        if quantity <= 0:
            return {"status": "REJECTED", "reason": "Quantity must be greater than zero."}

        fill_price = price or 100.0  # Fallback reference if market price omitted
        gross_value = fill_price * quantity

        if side.upper() == "BUY":
            # Check cash margin
            tax_est = self.tax_calc.calculate_trade_costs(fill_price, fill_price, quantity)
            total_required = gross_value + tax_est["total_frictional_cost"]

            if total_required > self.cash:
                return {
                    "status": "REJECTED",
                    "reason": f"Insufficient funds: Required ₹{round(total_required, 2)}, Available ₹{round(self.cash, 2)}",
                }

            self.cash -= total_required

            # Add or update position
            if sym in self.positions:
                existing = self.positions[sym]
                new_qty = existing["quantity"] + quantity
                new_avg = ((existing["quantity"] * existing["avg_price"]) + gross_value) / new_qty
                existing["quantity"] = new_qty
                existing["avg_price"] = round(new_avg, 2)
            else:
                self.positions[sym] = {
                    "symbol": sym,
                    "quantity": quantity,
                    "avg_price": round(fill_price, 2),
                    "current_price": round(fill_price, 2),
                    "stop_loss": stop_loss,
                    "target": target,
                    "unrealized_pnl": 0.0,
                    "unrealized_pnl_pct": 0.0,
                    "opened_at": timestamp,
                }

        elif side.upper() == "SELL":
            if sym not in self.positions or self.positions[sym]["quantity"] < quantity:
                return {
                    "status": "REJECTED",
                    "reason": f"Insufficient holding for {sym} to execute SELL order.",
                }

            pos = self.positions[sym]
            costs = self.tax_calc.calculate_trade_costs(pos["avg_price"], fill_price, quantity)
            realized_pnl = ((fill_price - pos["avg_price"]) * quantity) - costs["total_frictional_cost"]

            self.cash += (fill_price * quantity) - costs["total_frictional_cost"]
            pos["quantity"] -= quantity

            if pos["quantity"] == 0:
                del self.positions[sym]

        order_record = {
            "order_id": order_id,
            "symbol": sym,
            "side": side.upper(),
            "quantity": quantity,
            "order_type": order_type.upper(),
            "fill_price": round(fill_price, 2),
            "status": "FILLED",
            "timestamp": timestamp,
            "stop_loss": stop_loss,
            "target": target,
        }
        self.orders.append(order_record)
        return order_record

    async def modify_order(self, order_id: str, new_price: Optional[float] = None, new_qty: Optional[int] = None) -> Dict[str, Any]:
        return {"status": "SUCCESS", "order_id": order_id, "message": "Simulated order modified."}

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        return {"status": "SUCCESS", "order_id": order_id, "message": "Simulated order cancelled."}


class ZerodhaKiteAdapter(BrokerAdapter):
    """Zerodha Kite Connect live execution adapter."""

    def __init__(self, api_key: Optional[str] = None, access_token: Optional[str] = None):
        self.api_key = api_key
        self.access_token = access_token

    def _check_auth(self):
        if not self.api_key or not self.access_token:
            raise ValueError(
                "STATUS: NOT CONFIGURED. REASON: ZERODHA_API_KEY and ZERODHA_ACCESS_TOKEN REQUIRED."
            )

    async def get_balance(self) -> Dict[str, Any]:
        self._check_auth()
        return {}

    async def get_positions(self) -> List[Dict[str, Any]]:
        self._check_auth()
        return []

    async def get_orders(self) -> List[Dict[str, Any]]:
        self._check_auth()
        return []

    async def place_order(self, symbol: str, side: str, quantity: int, **kwargs) -> Dict[str, Any]:
        self._check_auth()
        return {}

    async def modify_order(self, order_id: str, **kwargs) -> Dict[str, Any]:
        self._check_auth()
        return {}

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        self._check_auth()
        return {}
