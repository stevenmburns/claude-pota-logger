from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.models import Base
from app.database import get_db

TEST_DATABASE_URL = "sqlite+aiosqlite://"


@pytest.fixture()
async def _test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture()
async def client(_test_engine) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client with dependency-overridden database session."""
    from app.main import app as _app

    session_factory = async_sessionmaker(
        _test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def _override_get_db():
        async with session_factory() as session:
            yield session

    @asynccontextmanager
    async def _test_lifespan(app):
        yield

    _app.router.lifespan_context = _test_lifespan
    _app.dependency_overrides[get_db] = _override_get_db

    async with httpx.AsyncClient() as http_client:
        _app.state.http_client = http_client
        transport = ASGITransport(app=_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    _app.dependency_overrides.clear()
