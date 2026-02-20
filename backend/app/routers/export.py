import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.adif import generate_adif
from app.database import get_db
from app.routers.hunt_sessions import get_hunt_session_or_404
from app.routers.settings import get_or_create_settings

router = APIRouter(prefix="/api/hunt-sessions/{session_id}", tags=["export"])


@router.get("/export")
async def export_adif(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    session = await get_hunt_session_or_404(session_id, db, load_qsos=True)

    settings = await get_or_create_settings(db)
    operator_callsign = settings.operator_callsign

    adif_content = generate_adif(operator_callsign, session.qsos)
    filename = f"hunt_{session.session_date.strftime('%Y%m%d')}.adi"

    return Response(
        content=adif_content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
