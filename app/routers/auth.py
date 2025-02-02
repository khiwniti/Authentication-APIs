from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Dict
from ..schemas.auth import UserRegister, UserLogin, Token, UserResponse
from ..utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
)
from ..database import get_db  # You'll need to implement this
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.user import User as UserModel  # Correct import for User model

router = APIRouter(prefix="/_api/auth/v1")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/_api/auth/v1/login")

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    # Check if user exists
    existing_user = await db.execute(
        select(UserModel).where(UserModel.email == user_data.email)
    )
    if existing_user.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = UserModel(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)  # Refresh to get the new user's ID

    return UserResponse(id=new_user.id, email=new_user.email, full_name=new_user.full_name)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Token:
    # Verify user credentials
    result = await db.execute(
        select(UserModel).where(UserModel.email == form_data.username)
    )
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/login/google")
async def google_login():
    # Implement Google OAuth2 login initiation
    return {"url": "Google OAuth URL"}

@router.get("/login/google/callback")
async def google_callback(code: str):
    # Implement Google OAuth2 callback handling
    return {"access_token": "google_oauth_token"}

@router.get("/login/facebook")
async def facebook_login():
    # Implement Facebook OAuth2 login initiation
    return {"url": "Facebook OAuth URL"}

@router.get("/login/facebook/callback")
async def facebook_callback(code: str):
    # Implement Facebook OAuth2 callback handling
    return {"access_token": "facebook_oauth_token"} 