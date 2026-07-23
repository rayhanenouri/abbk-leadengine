"""
User management routes - Admin only.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import User, UserRole
from app.schemas.auth import UserResponse
from app.schemas.user import UserCreate, UserUpdate, ApproveUserRequest, UpdateRoleRequest
from app.core.deps import get_db, require_role
from app.core.security import get_password_hash


router = APIRouter()


@router.get("/", response_model=list[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """
    Get all users (Admin only).

    Requires admin role. Returns list of all users in the system.
    """
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/pending", response_model=list[UserResponse])
async def get_pending_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """
    Get all pending users awaiting approval (Admin only).

    Requires admin role. Returns list of users with is_active=False.
    """
    result = await db.execute(select(User).where(User.is_active == False))
    pending_users = result.scalars().all()
    return pending_users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """
    Get a specific user by ID (Admin only).

    Requires admin role. Returns user details for the given ID.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """
    Create a new user (Admin only).

    Requires admin role. Creates a new user account with the provided details.
    Password is hashed before storage.

    Example request:
    ```json
    {
        "email": "manager@abbk.tn",
        "full_name": "Sales Manager",
        "password": "securepass123",
        "role": "manager",
        "permissions": {}
    }
    ```
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    # Create new user
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_pw=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=True,
        permissions=user_data.permissions or {},
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """
    Update a user (Admin only).

    Requires admin role. Updates user details. Only provided fields are updated.
    """
    # Fetch user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # Update fields
    if user_data.email is not None:
        # Check if new email already exists
        result = await db.execute(
            select(User).where(User.email == user_data.email, User.id != user_id)
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists",
            )
        user.email = user_data.email

    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    if user_data.password is not None:
        user.hashed_pw = get_password_hash(user_data.password)

    if user_data.role is not None:
        user.role = user_data.role

    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    if user_data.permissions is not None:
        user.permissions = user_data.permissions

    await db.commit()
    await db.refresh(user)

    return user


@router.put("/{user_id}/approve", response_model=UserResponse)
async def approve_user(
    user_id: int,
    approve_data: ApproveUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """
    Approve a pending user and assign role (Admin only).

    Requires admin role. Sets is_active=True and assigns the specified role.

    Example request:
    ```json
    {
        "role": "sales"
    }
    ```
    """
    # Fetch user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # Approve user
    user.is_active = True
    user.role = approve_data.role

    await db.commit()
    await db.refresh(user)

    return user


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role_data: UpdateRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """
    Update a user's role (Admin only).

    Requires admin role. Changes the user's role to the specified value.

    Example request:
    ```json
    {
        "role": "manager"
    }
    ```
    """
    # Prevent changing own role
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role",
        )

    # Fetch user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    user.role = role_data.role

    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """
    Delete a user (Admin only).

    Requires admin role. Permanently deletes a user account.
    Admins cannot delete themselves.
    """
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    # Fetch user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    await db.delete(user)
    await db.commit()

    return None
