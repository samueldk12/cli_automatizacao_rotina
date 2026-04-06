"""
Authentication dependencies and role-based access checkers.

Provides:
    - get_current_user: Validate JWT access token, return User
    - require_role: Factory returning dependency that checks user role
    - get_db: Async database session dependency
    - log_audit: Helper to record audit log entries
"""

from datetime import datetime, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import async_session
from .models import AuditLog, User

# JWT configuration (imported from settings or env in production)
SECRET_KEY = "supersecretkey_change_in_production_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncSession:
    """Provide an async database session per request."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


def _decode_token(token: str, token_type: str = "access") -> dict:
    """Decode and validate a JWT token, returning its payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{token_type.title()} token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Validate the JWT access token and return the current user.

    Raises 401 if the token is invalid or the user does not exist/is inactive.
    """
    payload = _decode_token(token, "access")
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user.",
        )
    return user


def require_role(*roles: str):
    """
    Factory that returns a FastAPI dependency checking if the current user
    has one of the required roles.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role("admin"))])
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role(s): {', '.join(roles)}.",
            )
        return current_user

    return role_checker


async def log_audit(
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = None,
    request: Optional[Request] = None,
) -> None:
    """Record an audit log entry in the database."""
    client_ip = None
    if request:
        client_ip = request.client.host if request.client else None

    log_entry = AuditLog(
        user_id=user.id if user else None,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=client_ip,
    )
    db.add(log_entry)
    await db.commit()
