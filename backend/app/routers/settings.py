from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Settings
from app.schemas import SettingsCreate, SettingsResponse

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
async def get_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Settings))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = Settings(operator_callsign="")
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.put("", response_model=SettingsResponse)
async def update_settings(data: SettingsCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Settings))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = Settings(
            operator_callsign=data.operator_callsign,
            flrig_host=data.flrig_host,
            flrig_port=data.flrig_port,
        )
        db.add(settings)
    else:
        settings.operator_callsign = data.operator_callsign
        settings.flrig_host = data.flrig_host
        settings.flrig_port = data.flrig_port
    await db.commit()
    await db.refresh(settings)
    return settings
