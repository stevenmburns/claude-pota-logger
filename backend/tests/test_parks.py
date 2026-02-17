"""Tests for parks proxy endpoint (mocked POTA API)."""

import pytest
import respx
from httpx import AsyncClient, Response


pytestmark = pytest.mark.asyncio

PARK_DATA = {
    "reference": "K-0001",
    "name": "Acadia National Park",
    "locationDesc": "US-ME",
    "latitude": 44.35,
    "longitude": -68.21,
}


@respx.mock
async def test_get_park_success(client: AsyncClient):
    respx.get("https://api.pota.app/park/K-0001").mock(
        return_value=Response(200, json=PARK_DATA)
    )
    resp = await client.get("/api/parks/K-0001")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Acadia National Park"


@respx.mock
async def test_get_park_not_found(client: AsyncClient):
    respx.get("https://api.pota.app/park/K-9999").mock(
        return_value=Response(404)
    )
    resp = await client.get("/api/parks/K-9999")
    assert resp.status_code == 404


@respx.mock
async def test_get_park_api_error(client: AsyncClient):
    respx.get("https://api.pota.app/park/K-0001").mock(
        return_value=Response(500)
    )
    resp = await client.get("/api/parks/K-0001")
    assert resp.status_code == 404  # backend returns 404 for any non-200
