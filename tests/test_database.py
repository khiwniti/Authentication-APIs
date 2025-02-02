import pytest
from app.database import get_db
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

@pytest.mark.asyncio
async def test_create_user(db: AsyncSession):
    # Create a new user in the database
    new_user = User(email="db_test@example.com", password_hash="hashed_password", full_name="DB Test User")
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Verify the user was created
    result = await db.execute(select(User).where(User.email == "db_test@example.com"))
    user = result.scalars().first()
    assert user is not None
    assert user.email == "db_test@example.com"

@pytest.mark.asyncio
async def test_user_exists(db: AsyncSession):
    # Check if the user exists
    result = await db.execute(select(User).where(User.email == "db_test@example.com"))
    user = result.scalars().first()
    assert user is not None 