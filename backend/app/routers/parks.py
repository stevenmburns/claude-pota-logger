from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/api/parks", tags=["parks"])


@router.get("/{park_ref}")
async def get_park(park_ref: str, request: Request):
    client = request.app.state.http_client
    resp = await client.get(f"https://api.pota.app/park/{park_ref}", timeout=5.0)
    if resp.status_code != 200:
        raise HTTPException(status_code=404, detail="Park not found")
    return resp.json()
