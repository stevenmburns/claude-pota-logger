import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import QSO
from app.routers.hunt_sessions import get_hunt_session_or_404
from app.schemas import QSOCreate, QSOResponse

router = APIRouter(prefix="/api/hunt-sessions/{session_id}/qsos", tags=["qsos"])


@router.post("", response_model=QSOResponse, status_code=201)
async def create_qso(
    session_id: uuid.UUID, data: QSOCreate, db: AsyncSession = Depends(get_db)
):
    await get_hunt_session_or_404(session_id, db)
    qso = QSO(hunt_session_id=session_id, **data.model_dump())
    db.add(qso)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Already logged {data.callsign.upper()} at {data.park_reference.upper()} on {data.band}",
        )
    await db.refresh(qso)
    return qso


@router.get("", response_model=list[QSOResponse])
async def list_qsos(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await get_hunt_session_or_404(session_id, db)
    result = await db.execute(
        select(QSO).where(QSO.hunt_session_id == session_id).order_by(QSO.timestamp)
    )
    return result.scalars().all()


@router.delete("/{qso_id}", status_code=204)
async def delete_qso(
    session_id: uuid.UUID, qso_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(QSO).where(QSO.id == qso_id, QSO.hunt_session_id == session_id)
    )
    qso = result.scalar_one_or_none()
    if not qso:
        raise HTTPException(status_code=404, detail="QSO not found")
    await db.delete(qso)
    await db.commit()
