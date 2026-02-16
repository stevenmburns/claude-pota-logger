import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/spots", tags=["spots"])


@router.get("")
async def get_active_spots():
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.pota.app/spot/activator", timeout=10.0)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch spots")
    return resp.json()
