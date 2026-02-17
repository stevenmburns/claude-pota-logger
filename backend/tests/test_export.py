"""Integration tests for ADIF export endpoint."""

import uuid

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio

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


async def _get_session_id(client: AsyncClient) -> str:
    resp = await client.get("/api/hunt-sessions/today")
    return resp.json()["id"]


async def test_export_empty_session(client: AsyncClient):
    sid = await _get_session_id(client)
    resp = await client.get(f"/api/hunt-sessions/{sid}/export")
    assert resp.status_code == 200
    assert "application/octet-stream" in resp.headers["content-type"]
    content = resp.text
    assert "<EOH>" in content
    assert "<EOR>" not in content


async def test_export_with_qso(client: AsyncClient):
    sid = await _get_session_id(client)
    await client.post(f"/api/hunt-sessions/{sid}/qsos", json=QSO_DATA)

    resp = await client.get(f"/api/hunt-sessions/{sid}/export")
    assert resp.status_code == 200
    content = resp.text
    assert "<CALL:4>W1AW" in content
    assert "<SIG:4>POTA" in content
    assert "<SIG_INFO:6>K-0001" in content
    assert "<EOR>" in content


async def test_export_uses_operator_callsign(client: AsyncClient):
    await client.put("/api/settings", json={"operator_callsign": "KD2ABC"})
    sid = await _get_session_id(client)
    await client.post(f"/api/hunt-sessions/{sid}/qsos", json=QSO_DATA)

    resp = await client.get(f"/api/hunt-sessions/{sid}/export")
    assert "<STATION_CALLSIGN:6>KD2ABC" in resp.text


async def test_export_fallback_n0call(client: AsyncClient):
    """When no settings exist, operator defaults to empty string (auto-created)."""
    sid = await _get_session_id(client)
    await client.post(f"/api/hunt-sessions/{sid}/qsos", json=QSO_DATA)
    resp = await client.get(f"/api/hunt-sessions/{sid}/export")
    assert resp.status_code == 200


async def test_export_filename(client: AsyncClient):
    sid = await _get_session_id(client)
    resp = await client.get(f"/api/hunt-sessions/{sid}/export")
    assert "hunt_" in resp.headers.get("content-disposition", "")
    assert ".adi" in resp.headers.get("content-disposition", "")


async def test_export_session_not_found(client: AsyncClient):
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/api/hunt-sessions/{fake_id}/export")
    assert resp.status_code == 404
