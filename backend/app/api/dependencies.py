"""API dependencies for authentication and database sessions."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.core.security import decode_access_token
from app.services.user_service import UserService

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Authorization credentials (Bearer token)
        db: Database session

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    # Extract user_id from token
    user_id: Optional[int] = payload.get("sub")

    if user_id is None:
        raise credentials_exception

    # Get user from database
    user = UserService.get_user_by_id(db, user_id=int(user_id))

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get current active user.

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Current active user

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get current superuser.

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Current superuser

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


def get_system_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to require SYSTEM_ADMIN role.

    System admins have global access to the entire platform and can:
    - Manage all businesses
    - Create new businesses
    - Manage all users across all businesses
    - Access all data across all businesses

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Current user if they are a system admin

    Raises:
        HTTPException: If user is not a system admin
    """
    if not current_user.is_system_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System administrator privileges required",
        )
    return current_user


def get_business_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to require BUSINESS_ADMIN role or higher.

    Business admins can:
    - Manage users within their business
    - Manage business settings
    - Full CRUD on clients and events within their business
    - View and manage all data within their business

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Current user if they are a business admin or system admin

    Raises:
        HTTPException: If user is not a business admin or system admin
    """
    if not (current_user.is_business_admin or current_user.is_system_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Business administrator privileges required",
        )
    return current_user


def require_business_context(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to ensure user has a business context.

    Validates that the user is associated with a business.
    SYSTEM_ADMIN users are exempt from this requirement.

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Current user if they have a business context

    Raises:
        HTTPException: If user doesn't have a business_id (except system admins)
    """
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business",
        )
    return current_user
