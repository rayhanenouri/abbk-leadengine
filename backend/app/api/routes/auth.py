"""
Authentication routes: login, registration, and user profile.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.auth import LoginRequest, Token, UserResponse
from app.models.models import User
from app.core.deps import get_db, get_current_user
from app.core.security import verify_password, create_access_token


router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    OAuth2 compatible token login.

    Accepts email and password, verifies credentials against database,
    and returns a JWT access token.

    Example request:
    ```json
    {
        "email": "admin@abbk.tn",
        "password": "admin123"
    }
    ```

    Returns:
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "bearer"
    }
    ```
    """
    # Fetch user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalars().first()

    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.hashed_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    # Create JWT token with user email as subject
    access_token = create_access_token(data={"sub": user.email})

    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get the currently authenticated user's profile.

    Requires: Valid JWT token in Authorization header

    Example:
    ```
    Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
    ```

    Returns the user's profile excluding the password hash.
    """
    return current_user
