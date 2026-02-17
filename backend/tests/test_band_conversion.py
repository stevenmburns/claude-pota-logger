"""Unit tests for kHz-to-band conversion in spots router."""

import pytest

from app.routers.spots import khz_to_band


class TestKhzToBand:
    """Test frequency (kHz string) to amateur band conversion."""

    @pytest.mark.parametrize(
        "khz, expected",
        [
            ("1800", "160m"),
            ("1850", "160m"),
            ("3500", "80m"),
            ("3573", "80m"),
            ("5330", "60m"),
            ("7000", "40m"),
            ("7074", "40m"),
            ("10100", "30m"),
            ("10136", "30m"),
            ("14000", "20m"),
            ("14074", "20m"),
            ("18100", "17m"),
            ("18100", "17m"),
            ("21000", "15m"),
            ("21074", "15m"),
            ("24900", "12m"),
            ("24915", "12m"),
            ("28000", "10m"),
            ("28074", "10m"),
            ("29600", "10m"),
            ("50000", "6m"),
            ("50313", "6m"),
            ("52525", "6m"),
            ("144000", "2m"),
            ("145000", "2m"),
            ("146520", "2m"),
        ],
    )
    def test_standard_frequencies(self, khz, expected):
        assert khz_to_band(khz) == expected

    def test_out_of_range_low(self):
        assert khz_to_band("500") == ""

    def test_out_of_range_high(self):
        assert khz_to_band("440000") == ""

    def test_between_bands(self):
        # 30 MHz is between 10m (28-30) — actually still 10m
        # 31 MHz should be out of range
        assert khz_to_band("31000") == ""

    def test_invalid_string(self):
        assert khz_to_band("abc") == ""

    def test_empty_string(self):
        assert khz_to_band("") == ""

    def test_none_value(self):
        assert khz_to_band(None) == ""

    def test_10m_upper_edge(self):
        """29999 kHz should still be 10m."""
        assert khz_to_band("29999") == "10m"

    def test_6m_upper_edge(self):
        """53999 kHz should still be 6m."""
        assert khz_to_band("53999") == "6m"

    def test_2m_upper_edge(self):
        """147999 kHz should still be 2m."""
        assert khz_to_band("147999") == "2m"

    def test_just_above_2m(self):
        """148000 kHz is above 2m."""
        assert khz_to_band("148000") == ""
