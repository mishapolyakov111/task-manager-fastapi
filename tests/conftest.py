import os

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+asyncpg://app:app@localhost:5432/tasks_test"
)
# app.config требует DATABASE_URL при импорте приложения
os.environ.setdefault("DATABASE_URL", TEST_DATABASE_URL)

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402

from app import models  # noqa: E402, F401
from app.db import Base, get_session  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def client(engine):
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE users, tasks RESTART IDENTITY CASCADE"))

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
async def user(client):
    response = await client.post(
        "/users", json={"email": "owner@example.com", "name": "Owner"}
    )
    return response.json()
