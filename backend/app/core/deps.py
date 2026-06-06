"""
FastAPI dependencies for authentication and authorization.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.models import User
from app.core.security import decode_access_token


# HTTP Bearer token scheme for Swagger UI
security = HTTPBearer()


async def get_db() -> AsyncSession:
    """
    FastAPI dependency that yields a database session.
    Automatically commits on success, rolls back on error.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency to get the currently authenticated user.

    Extracts JWT token from Authorization header, verifies it,
    and returns the user from the database.

    Raises:
        HTTPException 401: If token is invalid or user not found
        HTTPException 403: If user account is inactive

    Usage:
        @app.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.email}
    """
    token = credentials.credentials

    # Decode and verify the JWT token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract email from token payload
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user


def require_role(*allowed_roles):
    """
    Dependency factory to require specific roles.

    Returns a dependency that checks if the current user has one of the allowed roles.
    Raises 403 Forbidden if the user's role is not in the allowed list.

    Args:
        *allowed_roles: Variable number of UserRole enum values

    Returns:
        FastAPI dependency function

    Usage:
        from app.models.models import UserRole

        # Single role
        @app.get("/admin-only")
        async def admin_route(user: User = Depends(require_role(UserRole.admin))):
            return {"message": "Admin only"}

        # Multiple roles
        @app.get("/staff-only")
        async def staff_route(user: User = Depends(require_role(UserRole.admin, UserRole.manager))):
            return {"message": "Admin or manager"}
    """
    from app.models.models import UserRole

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            allowed_role_names = [role.value for role in allowed_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role(s): {', '.join(allowed_role_names)}",
            )
        return current_user

    return role_checker


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require admin role (legacy - use require_role for more flexibility).

    Usage:
        @app.post("/admin-only")
        async def admin_route(admin: User = Depends(require_admin)):
            return {"message": "Admin access granted"}
    """
    from app.models.models import UserRole

    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
