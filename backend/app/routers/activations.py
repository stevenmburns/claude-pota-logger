import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Activation
from app.schemas import ActivationCreate, ActivationDetail, ActivationResponse

router = APIRouter(prefix="/api/activations", tags=["activations"])


@router.post("", response_model=ActivationResponse, status_code=201)
async def create_activation(data: ActivationCreate, db: AsyncSession = Depends(get_db)):
    activation = Activation(**data.model_dump())
    db.add(activation)
    await db.commit()
    await db.refresh(activation)
    return activation


@router.get("", response_model=list[ActivationResponse])
async def list_activations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Activation).order_by(Activation.start_time.desc())
    )
    return result.scalars().all()


@router.get("/{activation_id}", response_model=ActivationDetail)
async def get_activation(activation_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Activation)
        .options(selectinload(Activation.qsos))
        .where(Activation.id == activation_id)
    )
    activation = result.scalar_one_or_none()
    if not activation:
        raise HTTPException(status_code=404, detail="Activation not found")
    return activation
