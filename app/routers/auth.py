from fastapi import APIRouter, HTTPException, status, Depends, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Dict
from ..schemas.auth import (
    UserRegister, 
    UserLogin, 
    Token, 
    UserResponse,
    PasswordResetRequest,
    PasswordResetConfirm
)
from ..utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    get_current_user
)
from ..database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.user import User as UserModel
from ..config import get_settings
from ..cache import get_redis
from redis.asyncio import Redis
from pydantic import EmailStr

router = APIRouter(
    prefix="/api/auth/v1",
    tags=["authentication"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication failed"},
        status.HTTP_403_FORBIDDEN: {"description": "Permission denied"}
    }
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/v1/login")

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Email already registered"}
    }
)
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

@router.post(
    "/login",
    response_model=Token,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials"}
    }
)
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

# Social Authentication Routes
@router.get(
    "/google/login",
    description="Initiate Google OAuth2 login flow"
)
async def google_login():
    settings = get_settings()
    return {
        "url": f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        "scope=openid%20email%20profile"
    }

@router.get(
    "/google/callback",
    response_model=Token,
    description="Handle Google OAuth2 callback"
)
async def google_callback(
    code: str,
    db: AsyncSession = Depends(get_db)
) -> Token:
    # Implementation for Google OAuth callback
    pass

@router.get(
    "/facebook/login",
    description="Initiate Facebook OAuth2 login flow"
)
async def facebook_login():
    settings = get_settings()
    return {
        "url": f"https://www.facebook.com/v12.0/dialog/oauth?"
        f"client_id={settings.FACEBOOK_CLIENT_ID}&"
        f"redirect_uri={settings.FACEBOOK_REDIRECT_URI}&"
        "scope=email"
    }

@router.get(
    "/facebook/callback",
    response_model=Token,
    description="Handle Facebook OAuth2 callback"
)
async def facebook_callback(
    code: str,
    db: AsyncSession = Depends(get_db)
) -> Token:
    # Implementation for Facebook OAuth callback
    pass

@router.post(
    "/password-reset/request",
    status_code=status.HTTP_202_ACCEPTED,
    description="Request a password reset email"
)
async def request_password_reset(
    email: EmailStr,
    db: AsyncSession = Depends(get_db)
):
    # Implement password reset request logic
    # 1. Verify email exists
    # 2. Generate reset token
    # 3. Send email with reset link
    return {"message": "If the email exists, a password reset link will be sent"}

@router.post(
    "/password-reset/confirm",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid or expired token"}
    }
)
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    # Implement password reset confirmation logic
    # 1. Verify token
    # 2. Update password
    await db.commit()
    return {"message": "Password successfully updated"}

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    description="Logout current user"
)
async def logout(
    response: Response,
    current_user: UserModel = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    # Implement logout logic
    # 1. Invalidate token in Redis
    # 2. Clear cookie if using cookie auth
    await redis.delete(f"user_session:{current_user.id}")
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}

@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Not authenticated"}
    }
)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_user)
) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name
    ) 