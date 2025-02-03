import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_db  # Adjust the import based on your structure
from fastapi.testclient import TestClient
from app.main import app  # Ensure this imports ALL routes

DATABASE_URL = "postgresql+asyncpg://bitebase_admin:your_password@localhost:5432/test_db"

@pytest.fixture(scope="session")
def db_engine():
    engine = create_async_engine(DATABASE_URL)
    yield engine
    engine.dispose()

@pytest.fixture
async def db(db_engine):
    async with db_engine.connect() as conn:
        await conn.begin()
        AsyncTestingSession = sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False
        )
        session = AsyncTestingSession()
        yield session
        await session.close()
        await conn.rollback()

@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client 