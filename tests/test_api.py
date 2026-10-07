"""Integration tests for FastAPI endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.api.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ONLINE"


@pytest.mark.asyncio
async def test_system_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/system/status")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "OPERATIONAL"
        assert "memory_usage_mb" in data


@pytest.mark.asyncio
async def test_scanner_strategies():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/scanner/strategies")
        assert res.status_code == 200
        data = res.json()
        assert len(data["strategies"]) >= 5


@pytest.mark.asyncio
async def test_paper_trading_balance():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/paper/balance")
        assert res.status_code == 200
        data = res.json()
        assert data["mode"] == "PAPER_TRADING"
        assert data["cash_balance"] == 1000000.0
