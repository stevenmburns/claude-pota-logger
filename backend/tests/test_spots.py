"""Tests for spots endpoint (mocked POTA API + DB for hunted flag)."""

import pytest
import respx
from httpx import AsyncClient, Response


pytestmark = pytest.mark.asyncio

SPOTS_DATA = [
    {
        "activator": "W1AW",
        "reference": "K-0001",
        "frequency": "14074",
        "mode": "FT8",
        "spotTime": "2025-06-15T18:30:00Z",
        "locationDesc": "US-ME",
        "name": "Acadia National Park",
    },
    {
        "activator": "K3LR",
        "reference": "K-0002",
        "frequency": "7074",
        "mode": "FT8",
        "spotTime": "2025-06-15T18:35:00Z",
        "locationDesc": "US-PA",
        "name": "Allegheny National Forest",
    },
    {
        "activator": "N5J",
        "reference": "K-0003",
        "frequency": "21074",
        "mode": "CW",
        "spotTime": "2025-06-15T18:40:00Z",
        "locationDesc": "US-TX",
        "name": "Big Thicket National Preserve",
    },
]

QSO_DATA = {
    "park_reference": "K-0001",
    "callsign": "W1AW",
    "frequency": 14.074,
    "band": "20m",
    "mode": "FT8",
    "rst_sent": "59",
    "rst_received": "59",
    "timestamp": "2025-06-15T18:30:00Z",
}


@respx.mock
async def test_get_spots_returns_list(client: AsyncClient):
    respx.get("https://api.pota.app/spot/activator").mock(
        return_value=Response(200, json=SPOTS_DATA)
    )
    resp = await client.get("/api/spots")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


@respx.mock
async def test_spots_have_hunted_flag(client: AsyncClient):
    respx.get("https://api.pota.app/spot/activator").mock(
        return_value=Response(200, json=SPOTS_DATA)
    )
    resp = await client.get("/api/spots")
    for spot in resp.json():
        assert "hunted" in spot


@respx.mock
async def test_spots_hunted_after_logging_qso(client: AsyncClient):
    """Spot should be marked hunted if we've logged a matching QSO today."""
    session_resp = await client.get("/api/hunt-sessions/today")
    sid = session_resp.json()["id"]
    await client.post(f"/api/hunt-sessions/{sid}/qsos", json=QSO_DATA)

    respx.get("https://api.pota.app/spot/activator").mock(
        return_value=Response(200, json=SPOTS_DATA)
    )
    resp = await client.get("/api/spots")
    spots = resp.json()

    w1aw_spot = next(s for s in spots if s["activator"] == "W1AW")
    assert w1aw_spot["hunted"] is True

    k3lr_spot = next(s for s in spots if s["activator"] == "K3LR")
    assert k3lr_spot["hunted"] is False


@respx.mock
async def test_spots_filter_by_band(client: AsyncClient):
    respx.get("https://api.pota.app/spot/activator").mock(
        return_value=Response(200, json=SPOTS_DATA)
    )
    resp = await client.get("/api/spots", params={"band": "20m"})
    spots = resp.json()
    assert len(spots) == 1
    assert spots[0]["activator"] == "W1AW"


@respx.mock
async def test_spots_filter_by_mode(client: AsyncClient):
    respx.get("https://api.pota.app/spot/activator").mock(
        return_value=Response(200, json=SPOTS_DATA)
    )
    resp = await client.get("/api/spots", params={"mode": "CW"})
    spots = resp.json()
    assert len(spots) == 1
    assert spots[0]["activator"] == "N5J"


@respx.mock
async def test_spots_filter_all_passes_everything(client: AsyncClient):
    respx.get("https://api.pota.app/spot/activator").mock(
        return_value=Response(200, json=SPOTS_DATA)
    )
    resp = await client.get("/api/spots", params={"band": "All", "mode": "All"})
    assert len(resp.json()) == 3


@respx.mock
async def test_spots_api_failure(client: AsyncClient):
    respx.get("https://api.pota.app/spot/activator").mock(
        return_value=Response(500)
    )
    resp = await client.get("/api/spots")
    assert resp.status_code == 502


@respx.mock
async def test_spots_empty_list(client: AsyncClient):
    respx.get("https://api.pota.app/spot/activator").mock(
        return_value=Response(200, json=[])
    )
    resp = await client.get("/api/spots")
    assert resp.status_code == 200
    assert resp.json() == []
