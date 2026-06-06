"""
User management routes - Admin only.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import User, UserRole
from app.schemas.auth import UserResponse
from app.core.deps import get_db, require_role


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
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    return user
