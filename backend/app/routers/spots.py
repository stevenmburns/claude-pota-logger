from datetime import date, timezone
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import HuntSession

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
    db: AsyncSession = Depends(get_db),
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

    # Build set of hunted (callsign, park, band) from today's QSOs
    hunted: set[tuple[str, str, str]] = set()
    today = date.today()
    result = await db.execute(
        select(HuntSession)
        .options(selectinload(HuntSession.qsos))
        .where(HuntSession.session_date == today)
    )
    session = result.scalar_one_or_none()
    if session:
        for qso in session.qsos:
            hunted.add((qso.callsign.upper(), qso.park_reference.upper(), qso.band.upper()))

    # Annotate each spot with hunted flag
    for spot in spots:
        spot_band = khz_to_band(spot.get("frequency", "")).upper()
        key = (
            spot.get("activator", "").upper(),
            spot.get("reference", "").upper(),
            spot_band,
        )
        spot["hunted"] = key in hunted

    return spots
