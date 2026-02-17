import sqlite3
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import String, TypeDecorator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.models import Base
from app.database import get_db

# ---------------------------------------------------------------------------
# Make SQLite understand Python uuid.UUID objects at the driver level
# ---------------------------------------------------------------------------
sqlite3.register_adapter(uuid.UUID, lambda u: str(u))
sqlite3.register_converter("UUID", lambda b: uuid.UUID(b.decode()))


# ---------------------------------------------------------------------------
# TypeDecorator that stores UUIDs as strings in SQLite but accepts uuid.UUID
# objects in queries (converts both directions)
# ---------------------------------------------------------------------------
class SQLiteUUID(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return str(value)  # keep as string to match what app returns
        return value


# ---------------------------------------------------------------------------
# Patch PostgreSQL UUID columns to use our SQLite-friendly type
# ---------------------------------------------------------------------------

def _patch_uuid_columns():
    for table in Base.metadata.tables.values():
        for col in table.columns:
            if hasattr(col.type, "__class__") and col.type.__class__.__name__ == "UUID":
                col.type = SQLiteUUID()


_patch_uuid_columns()

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

    transport = ASGITransport(app=_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    _app.dependency_overrides.clear()
