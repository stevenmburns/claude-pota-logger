import uuid
from datetime import date, timezone, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import attributes, selectinload

from app.database import get_db
from app.models import HuntSession
from app.schemas import HuntSessionDetail, HuntSessionResponse

router = APIRouter(prefix="/api/hunt-sessions", tags=["hunt-sessions"])


async def get_hunt_session_or_404(
    session_id: uuid.UUID,
    db: AsyncSession,
    load_qsos: bool = False,
) -> HuntSession:
    stmt = select(HuntSession).where(HuntSession.id == session_id)
    if load_qsos:
        stmt = stmt.options(selectinload(HuntSession.qsos))
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Hunt session not found")
    return session


@router.get("/today", response_model=HuntSessionDetail)
async def get_today_session(db: AsyncSession = Depends(get_db)):
    today = datetime.now(timezone.utc).date()
    result = await db.execute(
        select(HuntSession)
        .options(selectinload(HuntSession.qsos))
        .where(HuntSession.session_date == today)
    )
    session = result.scalar_one_or_none()
    if not session:
        session = HuntSession(session_date=today)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        attributes.set_committed_value(session, "qsos", [])
    return session


@router.get("", response_model=list[HuntSessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(HuntSession).order_by(HuntSession.session_date.desc())
    )
    return result.scalars().all()


@router.get("/{session_id}", response_model=HuntSessionDetail)
async def get_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await get_hunt_session_or_404(session_id, db, load_qsos=True)
