import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Activation, QSO
from app.schemas import QSOCreate, QSOResponse

router = APIRouter(prefix="/api/activations/{activation_id}/qsos", tags=["qsos"])


async def _get_activation(activation_id: uuid.UUID, db: AsyncSession) -> Activation:
    result = await db.execute(
        select(Activation).where(Activation.id == activation_id)
    )
    activation = result.scalar_one_or_none()
    if not activation:
        raise HTTPException(status_code=404, detail="Activation not found")
    return activation


@router.post("", response_model=QSOResponse, status_code=201)
async def create_qso(
    activation_id: uuid.UUID, data: QSOCreate, db: AsyncSession = Depends(get_db)
):
    await _get_activation(activation_id, db)
    qso = QSO(activation_id=activation_id, **data.model_dump())
    db.add(qso)
    await db.commit()
    await db.refresh(qso)
    return qso


@router.get("", response_model=list[QSOResponse])
async def list_qsos(activation_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await _get_activation(activation_id, db)
    result = await db.execute(
        select(QSO).where(QSO.activation_id == activation_id).order_by(QSO.timestamp)
    )
    return result.scalars().all()


@router.delete("/{qso_id}", status_code=204)
async def delete_qso(
    activation_id: uuid.UUID, qso_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(QSO).where(QSO.id == qso_id, QSO.activation_id == activation_id)
    )
    qso = result.scalar_one_or_none()
    if not qso:
        raise HTTPException(status_code=404, detail="QSO not found")
    await db.delete(qso)
    await db.commit()
