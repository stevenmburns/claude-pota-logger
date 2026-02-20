from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import HuntSession

router = APIRouter(prefix="/api/spots", tags=["spots"])

BAND_RANGES: list[tuple[float, float, str]] = [
    (1800, 2000, "160m"),
    (3500, 4000, "80m"),
    (5330, 5406, "60m"),
    (7000, 7300, "40m"),
    (10100, 10150, "30m"),
    (14000, 14350, "20m"),
    (18068, 18168, "17m"),
    (21000, 21450, "15m"),
    (24890, 24990, "12m"),
    (28000, 30000, "10m"),
    (50000, 54000, "6m"),
    (144000, 148000, "2m"),
]


def khz_to_band(khz: str) -> str:
    try:
        freq = float(khz)
    except (ValueError, TypeError):
        return ""
    for low, high, band in BAND_RANGES:
        if low <= freq < high:
            return band
    return ""


@router.get("")
async def get_active_spots(
    request: Request,
    band: Optional[str] = Query(None),
    mode: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    client = request.app.state.http_client
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
    today = datetime.now(timezone.utc).date()
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
