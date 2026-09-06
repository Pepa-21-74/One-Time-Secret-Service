import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from main import app
from database import get_db
from models.models import Base
from services.rate_limiter import security_protection
from sqlalchemy.pool import NullPool

TEST_DATABASE_URL = os.getenv("DATABASE_URL_TEST")
test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def clean_state():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    security_protection._attempts_state.clear()  

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def make_client(client_ip: str = "1.2.3.4") -> AsyncClient:

    transport = ASGITransport(app=app, client=(client_ip, 12345))
    return AsyncClient(transport=transport, base_url="http://test")