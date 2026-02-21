"""Integration tests for QSO CRUD endpoints."""

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
}


async def _get_session_id(client: AsyncClient) -> str:
    resp = await client.get("/api/hunt-sessions/today")
    return resp.json()["id"]


async def test_create_qso(client: AsyncClient):
    sid = await _get_session_id(client)
    resp = await client.post(f"/api/hunt-sessions/{sid}/qsos", json=QSO_DATA)
    assert resp.status_code == 201
    data = resp.json()
    assert data["callsign"] == "W1AW"
    assert data["park_reference"] == "K-0001"
    assert data["band"] == "20m"


async def test_qso_timestamp_is_utc(client: AsyncClient):
    """Timestamp returned in response must carry UTC timezone so browsers parse it correctly."""
    sid = await _get_session_id(client)
    resp = await client.post(f"/api/hunt-sessions/{sid}/qsos", json=QSO_DATA)
    assert resp.status_code == 201
    ts = resp.json()["timestamp"]
    # Must end with Z or +00:00 so JavaScript new Date() treats it as UTC
    assert ts.endswith("Z") or ts.endswith("+00:00"), f"timestamp lacks UTC indicator: {ts}"


async def test_duplicate_qso_returns_409(client: AsyncClient):
    sid = await _get_session_id(client)
    await client.post(f"/api/hunt-sessions/{sid}/qsos", json=QSO_DATA)
    resp = await client.post(f"/api/hunt-sessions/{sid}/qsos", json=QSO_DATA)
    assert resp.status_code == 409


async def test_same_callsign_different_band_allowed(client: AsyncClient):
    sid = await _get_session_id(client)
    await client.post(f"/api/hunt-sessions/{sid}/qsos", json=QSO_DATA)

    data_40m = {**QSO_DATA, "band": "40m", "frequency": 7.074}
    resp = await client.post(f"/api/hunt-sessions/{sid}/qsos", json=data_40m)
    assert resp.status_code == 201


async def test_same_callsign_different_park_allowed(client: AsyncClient):
    sid = await _get_session_id(client)
    await client.post(f"/api/hunt-sessions/{sid}/qsos", json=QSO_DATA)

    data_other_park = {**QSO_DATA, "park_reference": "K-0002"}
    resp = await client.post(f"/api/hunt-sessions/{sid}/qsos", json=data_other_park)
    assert resp.status_code == 201


async def test_list_qsos(client: AsyncClient):
    sid = await _get_session_id(client)
    await client.post(f"/api/hunt-sessions/{sid}/qsos", json=QSO_DATA)

    resp = await client.get(f"/api/hunt-sessions/{sid}/qsos")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_delete_qso(client: AsyncClient):
    sid = await _get_session_id(client)
    create_resp = await client.post(f"/api/hunt-sessions/{sid}/qsos", json=QSO_DATA)
    qso_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/hunt-sessions/{sid}/qsos/{qso_id}")
    assert del_resp.status_code == 204

    # Verify it's gone
    list_resp = await client.get(f"/api/hunt-sessions/{sid}/qsos")
    ids = [q["id"] for q in list_resp.json()]
    assert qso_id not in ids


async def test_delete_qso_not_found(client: AsyncClient):
    sid = await _get_session_id(client)
    fake_id = str(uuid.uuid4())
    resp = await client.delete(f"/api/hunt-sessions/{sid}/qsos/{fake_id}")
    assert resp.status_code == 404


async def test_create_qso_session_not_found(client: AsyncClient):
    fake_id = str(uuid.uuid4())
    resp = await client.post(f"/api/hunt-sessions/{fake_id}/qsos", json=QSO_DATA)
    assert resp.status_code == 404
