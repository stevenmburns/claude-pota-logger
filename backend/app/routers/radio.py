import asyncio
import xmlrpc.client

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Settings

router = APIRouter(prefix="/api/radio", tags=["radio"])


class SetFrequencyRequest(BaseModel):
    frequency_khz: float


@router.post("/set-frequency")
async def set_frequency(data: SetFrequencyRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Settings))
    settings = result.scalar_one_or_none()
    host = settings.flrig_host if settings else "localhost"
    port = settings.flrig_port if settings else 12345

    freq_hz = data.frequency_khz * 1000

    def call_flrig():
        proxy = xmlrpc.client.ServerProxy(f"http://{host}:{port}")
        proxy.rig.set_vfo(freq_hz)

    try:
        await asyncio.to_thread(call_flrig)
    except xmlrpc.client.Fault as e:
        raise HTTPException(status_code=502, detail=f"flrig XML-RPC fault: {e.faultString}")
    except (ConnectionRefusedError, OSError) as e:
        raise HTTPException(status_code=503, detail=f"flrig unreachable: {e}")

    return {"status": "ok", "frequency_hz": freq_hz}
