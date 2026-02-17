"""Unit tests for ADIF generation (no database needed)."""

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock
from decimal import Decimal

from app.adif import _adif_field, generate_adif


def _make_qso(**overrides):
    """Create a mock QSO object with sensible defaults."""
    qso = MagicMock()
    qso.callsign = overrides.get("callsign", "W1AW")
    qso.park_reference = overrides.get("park_reference", "K-0001")
    qso.timestamp = overrides.get(
        "timestamp", datetime(2025, 6, 15, 18, 30, 0, tzinfo=timezone.utc)
    )
    qso.band = overrides.get("band", "20m")
    qso.frequency = overrides.get("frequency", Decimal("14.0740"))
    qso.mode = overrides.get("mode", "SSB")
    qso.rst_sent = overrides.get("rst_sent", "59")
    qso.rst_received = overrides.get("rst_received", "59")
    return qso


class TestAdifField:
    def test_basic_field(self):
        assert _adif_field("CALL", "W1AW") == "<CALL:4>W1AW"

    def test_empty_value(self):
        assert _adif_field("CALL", "") == "<CALL:0>"

    def test_length_matches_value(self):
        result = _adif_field("STATION_CALLSIGN", "KD2ABC")
        assert result == "<STATION_CALLSIGN:6>KD2ABC"


class TestGenerateAdif:
    def test_header_present(self):
        adif = generate_adif("W1AW", [])
        assert "<ADIF_VER:5>3.1.4" in adif
        assert "<PROGRAMID:11>POTA Logger" in adif
        assert "<PROGRAMVERSION:3>1.0" in adif
        assert "<EOH>" in adif

    def test_empty_qso_list(self):
        adif = generate_adif("W1AW", [])
        assert "<EOR>" not in adif

    def test_single_qso_record(self):
        qso = _make_qso()
        adif = generate_adif("KD2ABC", [qso])

        assert "<STATION_CALLSIGN:6>KD2ABC" in adif
        assert "<CALL:4>W1AW" in adif
        assert "<SIG:4>POTA" in adif
        assert "<SIG_INFO:6>K-0001" in adif
        assert "<QSO_DATE:8>20250615" in adif
        assert "<TIME_ON:6>183000" in adif
        assert "<BAND:3>20m" in adif
        assert "<MODE:3>SSB" in adif
        assert "<RST_SENT:2>59" in adif
        assert "<RST_RCVD:2>59" in adif
        assert "<EOR>" in adif

    def test_callsign_uppercased(self):
        qso = _make_qso(callsign="w1aw")
        adif = generate_adif("kd2abc", [qso])
        assert "<STATION_CALLSIGN:6>KD2ABC" in adif
        assert "<CALL:4>W1AW" in adif

    def test_park_reference_uppercased(self):
        qso = _make_qso(park_reference="k-0001")
        adif = generate_adif("W1AW", [qso])
        assert "<SIG_INFO:6>K-0001" in adif

    def test_band_lowercased(self):
        qso = _make_qso(band="20M")
        adif = generate_adif("W1AW", [qso])
        assert "<BAND:3>20m" in adif

    def test_mode_uppercased(self):
        qso = _make_qso(mode="cw")
        adif = generate_adif("W1AW", [qso])
        assert "<MODE:2>CW" in adif

    def test_frequency_four_decimal_places(self):
        qso = _make_qso(frequency=Decimal("14.074"))
        adif = generate_adif("W1AW", [qso])
        assert "<FREQ:7>14.0740" in adif

    def test_frequency_integer_value(self):
        qso = _make_qso(frequency=Decimal("7"))
        adif = generate_adif("W1AW", [qso])
        assert "<FREQ:6>7.0000" in adif

    def test_multiple_qsos(self):
        qsos = [_make_qso(callsign="W1AW"), _make_qso(callsign="K3LR")]
        adif = generate_adif("N0CALL", qsos)
        assert adif.count("<EOR>") == 2
        assert "<CALL:4>W1AW" in adif
        assert "<CALL:4>K3LR" in adif
