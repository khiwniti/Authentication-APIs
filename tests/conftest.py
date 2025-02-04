import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_db  # Adjust the import based on your structure
from fastapi.testclient import TestClient
from app.main import app  # Ensure this imports ALL routes
import os
import asyncio
from typing import AsyncGenerator

# Set testing environment
os.environ["TESTING"] = "true"

# Test database URL - use your actual test database credentials
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://bitebase_admin:IzP2g4zdgkanxMDWekSO9RR6BzcBoRMA@dpg-cu2bn7t2ng1s73fv71q0-a.oregon-postgres.render.com/bitebasedb_test"
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    yield engine
    await engine.dispose()

@pytest.fixture
async def db():
    """Async database session fixture."""
    engine = create_async_engine(TEST_DATABASE_URL)
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    await engine.dispose()

@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
async def authenticated_user(test_client):
    # Create a test user and get authentication token
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    
    login_response = test_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    assert login_response.status_code == 200
    return login_response.json() 