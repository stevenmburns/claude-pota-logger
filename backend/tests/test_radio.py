"""Tests for POST /api/radio/set-frequency (flrig XML-RPC proxy)."""

import xmlrpc.client
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_set_frequency_success(client: AsyncClient):
    with patch("xmlrpc.client.ServerProxy") as mock_proxy_cls:
        mock_proxy = MagicMock()
        mock_proxy_cls.return_value = mock_proxy

        resp = await client.post(
            "/api/radio/set-frequency", json={"frequency_khz": "14074.0"}
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["frequency_hz"] == 14074000
    freq_arg = mock_proxy.rig.set_vfo.call_args.args[0]
    assert isinstance(freq_arg, float), "flrig requires a double (float), not int"
    assert freq_arg == 14074000.0


async def test_set_frequency_integer_conversion(client: AsyncClient):
    """Verifies kHz → Hz conversion for non-integer kHz values."""
    with patch("xmlrpc.client.ServerProxy") as mock_proxy_cls:
        mock_proxy = MagicMock()
        mock_proxy_cls.return_value = mock_proxy

        resp = await client.post(
            "/api/radio/set-frequency", json={"frequency_khz": "7074.5"}
        )

    assert resp.status_code == 200
    assert resp.json()["frequency_hz"] == 7074500
    freq_arg = mock_proxy.rig.set_vfo.call_args.args[0]
    assert isinstance(freq_arg, float), "flrig requires a double (float), not int"
    assert freq_arg == 7074500.0


async def test_set_frequency_xml_rpc_fault(client: AsyncClient):
    """XML-RPC faults from flrig (e.g. type error) return 502, not 500."""
    with patch("xmlrpc.client.ServerProxy") as mock_proxy_cls:
        mock_proxy = MagicMock()
        mock_proxy.rig.set_vfo.side_effect = xmlrpc.client.Fault(-1, "type error")
        mock_proxy_cls.return_value = mock_proxy

        resp = await client.post(
            "/api/radio/set-frequency", json={"frequency_khz": "14074.0"}
        )

    assert resp.status_code == 502
    assert "type error" in resp.json()["detail"]


async def test_set_frequency_flrig_unreachable(client: AsyncClient):
    with patch("xmlrpc.client.ServerProxy") as mock_proxy_cls:
        mock_proxy = MagicMock()
        mock_proxy.rig.set_vfo.side_effect = ConnectionRefusedError("Connection refused")
        mock_proxy_cls.return_value = mock_proxy

        resp = await client.post(
            "/api/radio/set-frequency", json={"frequency_khz": "14074.0"}
        )

    assert resp.status_code == 503
    assert "flrig unreachable" in resp.json()["detail"]


async def test_set_frequency_os_error(client: AsyncClient):
    """OSError (e.g. network unreachable) also returns 503."""
    with patch("xmlrpc.client.ServerProxy") as mock_proxy_cls:
        mock_proxy = MagicMock()
        mock_proxy.rig.set_vfo.side_effect = OSError("Network unreachable")
        mock_proxy_cls.return_value = mock_proxy

        resp = await client.post(
            "/api/radio/set-frequency", json={"frequency_khz": "21074.0"}
        )

    assert resp.status_code == 503
    assert "flrig unreachable" in resp.json()["detail"]


async def test_set_frequency_uses_settings_host_port(client: AsyncClient):
    """Verifies that saved flrig host/port from Settings are used."""
    # Save custom settings
    await client.put(
        "/api/settings",
        json={"operator_callsign": "W1AW", "flrig_host": "192.168.1.10", "flrig_port": 54321},
    )

    with patch("xmlrpc.client.ServerProxy") as mock_proxy_cls:
        mock_proxy = MagicMock()
        mock_proxy_cls.return_value = mock_proxy

        resp = await client.post(
            "/api/radio/set-frequency", json={"frequency_khz": "14025.0"}
        )

    assert resp.status_code == 200
    mock_proxy_cls.assert_called_once_with("http://192.168.1.10:54321")
    mock_proxy.rig.set_vfo.assert_called_once_with(14025000.0)
