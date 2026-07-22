"""
FastAPI dependencies for authentication and role-based access control (RBAC).
"""
import uuid
from typing import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_token
from app.models.enums import UserRole
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_uuid = uuid.UUID(str(user_id))
    except ValueError as exc:
        raise credentials_exception from exc

    user = await User.get(user_uuid)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_roles(*allowed_roles: Iterable[UserRole]):
    """
    Usage: Depends(require_roles(UserRole.OFFICER, UserRole.ADMIN))
    Raises 403 if the current user's role isn't in the allowed set.
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Role '{current_user.role.value}' is not permitted "
                    "to access this resource"
                ),
            )
        return current_user

    return role_checker
