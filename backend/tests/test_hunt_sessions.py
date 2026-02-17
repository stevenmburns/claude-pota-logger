"""Integration tests for hunt session endpoints."""

import uuid

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


async def test_get_today_creates_session(client: AsyncClient):
    resp = await client.get("/api/hunt-sessions/today")
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert "session_date" in data
    assert data["qsos"] == []


async def test_get_today_is_idempotent(client: AsyncClient):
    resp1 = await client.get("/api/hunt-sessions/today")
    resp2 = await client.get("/api/hunt-sessions/today")
    assert resp1.json()["id"] == resp2.json()["id"]


async def test_list_sessions(client: AsyncClient):
    await client.get("/api/hunt-sessions/today")  # ensure at least one
    resp = await client.get("/api/hunt-sessions")
    assert resp.status_code == 200
    sessions = resp.json()
    assert len(sessions) >= 1


async def test_get_session_by_id(client: AsyncClient):
    today = await client.get("/api/hunt-sessions/today")
    session_id = today.json()["id"]

    resp = await client.get(f"/api/hunt-sessions/{session_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == session_id
    assert "qsos" in resp.json()


async def test_get_session_not_found(client: AsyncClient):
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/api/hunt-sessions/{fake_id}")
    assert resp.status_code == 404
