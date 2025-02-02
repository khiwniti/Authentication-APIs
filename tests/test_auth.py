import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.utils.auth import get_password_hash

# Create a test database URL
TEST_DATABASE_URL = "postgresql://bitebase_admin:your_password@localhost:5432/test_db"

# Create a new engine and session for testing
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_client():
    # Create the FastAPI test client
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="module")
def db():
    # Create a new database session for testing
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Create the test database and tables
    from app.database import create_tables
    import asyncio

    asyncio.run(create_tables())
    yield
    # Optionally, drop the test database here

def test_register_user(test_client, db):
    # Test user registration
    response = test_client.post(
        "/_api/auth/v1/register",
        json={"email": "test@example.com", "password": "testpassword", "full_name": "Test User"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_login_user(test_client, db):
    # Test user login
    response = test_client.post(
        "/_api/auth/v1/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_user(test_client):
    # Test login with invalid credentials
    response = test_client.post(
        "/_api/auth/v1/login",
        data={"username": "invalid@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password" 