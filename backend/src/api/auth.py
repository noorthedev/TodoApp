"""Authentication API endpoints."""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.database import get_session
from src.models.user import User
from src.schemas.auth import AuthResponse, UserLogin, UserRegister, UserResponse
from src.utils.jwt import create_access_token
from src.utils.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    session: AsyncSession = Depends(get_session),
):
    """Register a new user.

    Args:
        user_data: User registration data (email and password)
        session: Database session

    Returns:
        AuthResponse with JWT token and user information

    Raises:
        HTTPException: If email already exists
    """
    logger.info(f"Registration attempt for email: {user_data.email}")

    # Check if email already exists
    result = await session.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        logger.warning(f"Registration failed - email already exists: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Hash password and create user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
    )
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    logger.info(f"User registered successfully: {new_user.email} (ID: {new_user.id})")

    # Generate JWT token
    # access_token = create_access_token(data={"sub": new_user.id})
    access_token = create_access_token(data={"sub": str(new_user.id)}) # str() add karein
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_session),
):
    """Login with email and password.

    Args:
        credentials: User login credentials (email and password)
        session: Database session

    Returns:
        AuthResponse with JWT token and user information

    Raises:
        HTTPException: If credentials are invalid
    """
    logger.info(f"Login attempt for email: {credentials.email}")

    # Find user by email
    result = await session.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Login failed - invalid credentials for email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"User logged in successfully: {user.email} (ID: {user.id})")

    # Generate JWT token
    # access_token = create_access_token(data={"sub": user.id})
    
    access_token = create_access_token(data={"sub": str(user.id)}) # str() add karein
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """Logout endpoint (informational only).
    
    JWT tokens are stateless, so logout is handled client-side by removing the token.
    This endpoint exists for API completeness and can be used for logging/analytics.
    
    Returns:
        Success message
    """
    return {"message": "Successfully logged out. Please remove the token from client storage."}
