import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.adif import generate_adif
from app.database import get_db
from app.models import Activation

router = APIRouter(prefix="/api/activations/{activation_id}", tags=["export"])


@router.get("/export")
async def export_adif(activation_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Activation)
        .options(selectinload(Activation.qsos))
        .where(Activation.id == activation_id)
    )
    activation = result.scalar_one_or_none()
    if not activation:
        raise HTTPException(status_code=404, detail="Activation not found")

    adif_content = generate_adif(activation, activation.qsos)
    filename = f"{activation.park_reference}_{activation.start_time.strftime('%Y%m%d')}.adi"

    return Response(
        content=adif_content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
