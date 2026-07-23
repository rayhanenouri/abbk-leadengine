"""
Authentication routes: login, registration, and user profile.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.auth import LoginRequest, Token, UserResponse, SignupRequest
from app.models.models import User, UserRole
from app.core.deps import get_db, get_current_user
from app.core.security import verify_password, create_access_token, get_password_hash


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


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    signup_data: SignupRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    User self-registration endpoint.

    Creates a new account with role='viewer' and is_active=False (pending admin approval).

    Example request:
    ```json
    {
        "email": "user@company.com",
        "full_name": "John Doe",
        "password": "securepass123",
        "company_role": "Sales Engineer"
    }
    ```

    Returns the created user profile.
    User cannot login until admin approves the account.
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == signup_data.email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists",
        )

    # Create new user with viewer role and inactive status
    new_user = User(
        email=signup_data.email,
        full_name=signup_data.full_name,
        hashed_pw=get_password_hash(signup_data.password),
        role=UserRole.viewer,
        is_active=False,  # Requires admin approval
        permissions={
            "company_role": signup_data.company_role  # Store their company role info
        },
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


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
