import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.adif import generate_adif
from app.database import get_db
from app.models import HuntSession, Settings

router = APIRouter(prefix="/api/hunt-sessions/{session_id}", tags=["export"])


@router.get("/export")
async def export_adif(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(HuntSession)
        .options(selectinload(HuntSession.qsos))
        .where(HuntSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Hunt session not found")

    settings_result = await db.execute(select(Settings))
    settings = settings_result.scalar_one_or_none()
    operator_callsign = settings.operator_callsign if settings else "N0CALL"

    adif_content = generate_adif(operator_callsign, session.qsos)
    filename = f"hunt_{session.session_date.strftime('%Y%m%d')}.adi"

    return Response(
        content=adif_content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
