from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/spots", tags=["spots"])

FREQ_TO_BAND: dict[str, str] = {
    "1.8": "160m", "3.5": "80m", "5.3": "60m", "7": "40m",
    "10.1": "30m", "14": "20m", "18.1": "17m", "21": "15m",
    "24.9": "12m", "28": "10m", "50": "6m", "144": "2m",
}


def khz_to_band(khz: str) -> str:
    try:
        mhz = float(khz) / 1000
    except (ValueError, TypeError):
        return ""
    for start, band in FREQ_TO_BAND.items():
        f = float(start)
        if f <= mhz < f + 1:
            return band
    if 28 <= mhz < 30:
        return "10m"
    if 50 <= mhz < 54:
        return "6m"
    if 144 <= mhz < 148:
        return "2m"
    return ""


@router.get("")
async def get_active_spots(
    band: Optional[str] = Query(None),
    mode: Optional[str] = Query(None),
):
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.pota.app/spot/activator", timeout=10.0)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch spots")
    spots = resp.json()

    if band and band != "All":
        spots = [s for s in spots if khz_to_band(s.get("frequency", "")) == band]
    if mode and mode != "All":
        spots = [s for s in spots if s.get("mode", "").upper() == mode.upper()]

    return spots
