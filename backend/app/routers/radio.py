import asyncio
import xmlrpc.client

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.settings import get_or_create_settings

router = APIRouter(prefix="/api/radio", tags=["radio"])


class SetFrequencyRequest(BaseModel):
    frequency_khz: float


@router.post("/set-frequency")
async def set_frequency(data: SetFrequencyRequest, db: AsyncSession = Depends(get_db)):
    settings = await get_or_create_settings(db)
    host = settings.flrig_host
    port = settings.flrig_port

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
