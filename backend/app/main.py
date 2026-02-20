from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import Base
from app.routers import export, hunt_sessions, parks, qsos, radio, settings, spots


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with httpx.AsyncClient() as client:
        app.state.http_client = client
        yield


app = FastAPI(title="POTA Logger", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hunt_sessions.router)
app.include_router(qsos.router)
app.include_router(export.router)
app.include_router(settings.router)
app.include_router(parks.router)
app.include_router(spots.router)
app.include_router(radio.router)
