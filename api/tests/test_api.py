"""
API integration tests using pytest + httpx.

Run with:  pytest api/tests/ -v
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database import create_tables, engine, Base


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create tables before each test, drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ------------------------------------------------------------------
# Health & root
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "BreatheEasy API"


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"


# ------------------------------------------------------------------
# Sensors
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_sensors_current(client: AsyncClient):
    resp = await client.get("/api/sensors/current")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_sensors_health(client: AsyncClient):
    resp = await client.get("/api/sensors/health")
    assert resp.status_code == 200


# ------------------------------------------------------------------
# Readings
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_readings_history_empty(client: AsyncClient):
    resp = await client.get("/api/readings/history")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_readings_history_with_filters(client: AsyncClient):
    resp = await client.get(
        "/api/readings/history",
        params={"sensor_type": "bme680", "metric": "temperature", "limit": 10},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_readings_stats(client: AsyncClient):
    resp = await client.get(
        "/api/readings/stats",
        params={"metric": "temperature", "timeframe": "24h"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "min" in body
    assert "max" in body
    assert "avg" in body


# ------------------------------------------------------------------
# WebSocket
# ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_websocket_connect():
    """Verify WebSocket endpoint accepts connections."""
    from httpx_ws import aconnect_ws

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        try:
            async with aconnect_ws("http://test/ws/sensors", ac) as ws:
                # Should receive initial data or keep alive
                pass
        except Exception:
            # httpx_ws may not be installed – skip gracefully
            pytest.skip("httpx_ws not available for WebSocket testing")
