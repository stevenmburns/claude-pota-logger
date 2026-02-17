"""Integration tests for settings endpoints."""

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


async def test_get_settings_creates_default(client: AsyncClient):
    resp = await client.get("/api/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert data["operator_callsign"] == ""


async def test_get_settings_idempotent(client: AsyncClient):
    resp1 = await client.get("/api/settings")
    resp2 = await client.get("/api/settings")
    assert resp1.json()["id"] == resp2.json()["id"]


async def test_put_settings_update(client: AsyncClient):
    await client.get("/api/settings")  # ensure exists
    resp = await client.put("/api/settings", json={"operator_callsign": "KD2ABC"})
    assert resp.status_code == 200
    assert resp.json()["operator_callsign"] == "KD2ABC"


async def test_put_settings_creates_if_missing(client: AsyncClient):
    resp = await client.put("/api/settings", json={"operator_callsign": "W1AW"})
    assert resp.status_code == 200
    assert resp.json()["operator_callsign"] == "W1AW"
