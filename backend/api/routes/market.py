"""Market Data & Overview Endpoints with Real-Time WebSocket Streaming."""
import asyncio
import json
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
from backend.data.yahoo_provider import YahooFinanceProvider
from backend.data.nse_provider import NSEProvider

router = APIRouter(prefix="/market", tags=["Market Data"])
market_provider = YahooFinanceProvider()
nse_provider = NSEProvider()


@router.get("/indices")
async def get_major_indices():
    """Fetch live quotes for major Indian benchmark indices."""
    indices = ["^NSEI", "^NSEBANK", "^BSESN", "^INDIAVIX"]
    quotes = {}
    for idx in indices:
        q = await market_provider.get_quote(idx)
        name = (
            "NIFTY 50" if idx == "^NSEI"
            else ("BANK NIFTY" if idx == "^NSEBANK"
            else ("SENSEX" if idx == "^BSESN"
            else "INDIA VIX"))
        )
        quotes[name] = q
    return {"indices": quotes}


@router.get("/quote/{symbol}")
async def get_stock_quote(symbol: str):
    """Fetch real-time quote for an equity symbol."""
    q = await market_provider.get_quote(symbol)
    if not q or q.get("last_price", 0) <= 0:
        raise HTTPException(status_code=404, detail=f"Quote not found for {symbol}")
    return q


@router.get("/symbols/{universe}")
async def get_universe_symbols(universe: str = "NIFTY_50"):
    """Fetch symbols belonging to index universe."""
    symbols = await nse_provider.fetch_index_symbols(universe)
    return {"universe": universe, "count": len(symbols), "symbols": symbols}


@router.websocket("/ws")
async def market_data_websocket(websocket: WebSocket):
    """Real-Time WebSocket Tick Stream.
    Pushes live ticks for major Indian indices and subscribed stock symbols every 1.5 seconds.
    Clients can subscribe via: {"action": "subscribe", "symbol": "RELIANCE"}
    """
    await websocket.accept()
    subscribed_symbols = set()

    async def listen_for_client_messages():
        try:
            while True:
                msg_text = await websocket.receive_text()
                try:
                    payload = json.loads(msg_text)
                    if payload.get("action") == "subscribe" and payload.get("symbol"):
                        subscribed_symbols.add(str(payload["symbol"]).strip().upper())
                    elif payload.get("action") == "unsubscribe" and payload.get("symbol"):
                        subscribed_symbols.discard(str(payload["symbol"]).strip().upper())
                except Exception:
                    pass
        except Exception:
            pass

    listen_task = asyncio.create_task(listen_for_client_messages())

    try:
        while True:
            indices_quotes = {}
            for idx in ["^NSEI", "^NSEBANK", "^BSESN", "^INDIAVIX"]:
                q = await market_provider.get_quote(idx)
                name = (
                    "NIFTY 50" if idx == "^NSEI"
                    else ("BANK NIFTY" if idx == "^NSEBANK"
                    else ("SENSEX" if idx == "^BSESN"
                    else "INDIA VIX"))
                )
                indices_quotes[name] = q

            stock_quotes = {}
            for sym in list(subscribed_symbols):
                sq = await market_provider.get_quote(sym)
                if sq.get("last_price", 0) > 0:
                    stock_quotes[sym] = sq

            payload = {
                "type": "TICK_UPDATE",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "indices": indices_quotes,
                "stocks": stock_quotes,
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1.5)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        listen_task.cancel()
