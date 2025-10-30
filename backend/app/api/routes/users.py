"""User management API endpoints."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User, UserRole
from app.schemas.auth import UserResponse, UserUpdate, UserRegister
from app.services.user_service import UserService
from app.api.dependencies import (
    get_current_user,
    get_business_admin,
    get_system_admin,
    require_business_context,
)

router = APIRouter(prefix="/users", tags=["users"])


# Schema for paginated user list response
class UserListResponse:
    """Response schema for paginated user list."""

    def __init__(self, users: List[User], total: int, skip: int, limit: int):
        self.total = total
        self.page = (skip // limit) + 1 if limit > 0 else 1
        self.page_size = limit
        self.total_pages = (total + limit - 1) // limit if limit > 0 else 1
        self.items = [UserResponse.model_validate(user) for user in users]


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's profile.

    Returns the authenticated user's information.
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current user's profile.

    Users can update their own information (email, full_name, password).
    Cannot change role or business_id through this endpoint.
    """
    # Remove fields users shouldn't be able to change themselves
    update_data = user_update.model_dump(exclude_unset=True)
    update_data.pop("role", None)
    update_data.pop("business_id", None)
    update_data.pop("is_active", None)
    update_data.pop("is_superuser", None)

    # Create a new UserUpdate with filtered data
    filtered_update = UserUpdate(**update_data)

    updated_user = UserService.update_user(db, current_user.id, filtered_update)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(updated_user)


@router.get("", response_model=dict)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = None,
    role: Optional[UserRole] = None,
    business_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List users with filtering and pagination.

    - SYSTEM_ADMIN: Can see all users across all businesses
    - BUSINESS_ADMIN: Can only see users within their business
    - BASE_USER: Cannot access this endpoint

    Query parameters:
    - skip: Number of records to skip
    - limit: Maximum number of records to return
    - is_active: Filter by active status
    - role: Filter by role
    - business_id: Filter by business (SYSTEM_ADMIN only)
    """
    # BASE_USER cannot list users
    if not (current_user.is_business_admin or current_user.is_system_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to list users",
        )

    # SYSTEM_ADMIN can see all users
    if current_user.is_system_admin:
        users, total = UserService.get_all_users(
            db=db,
            skip=skip,
            limit=limit,
            is_active=is_active,
            role=role,
            business_id=business_id,
        )
    # BUSINESS_ADMIN can only see users in their business
    else:
        if not current_user.business_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business administrator must be associated with a business",
            )

        users, total = UserService.get_users_by_business(
            db=db,
            business_id=current_user.business_id,
            skip=skip,
            limit=limit,
            is_active=is_active,
            role=role,
        )

    response = UserListResponse(users, total, skip, limit)
    return {
        "total": response.total,
        "page": response.page,
        "page_size": response.page_size,
        "total_pages": response.total_pages,
        "items": response.items,
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific user by ID.

    - SYSTEM_ADMIN: Can view any user
    - BUSINESS_ADMIN: Can only view users within their business
    - BASE_USER: Can only view themselves
    """
    user = UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # BASE_USER can only view themselves
    if not (current_user.is_business_admin or current_user.is_system_admin):
        if user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view this user",
            )
    # BUSINESS_ADMIN can only view users in their business
    elif current_user.is_business_admin and not current_user.is_system_admin:
        if user.business_id != current_user.business_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view users from other businesses",
            )

    return UserResponse.model_validate(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserRegister,
    current_user: User = Depends(get_business_admin),
    db: Session = Depends(get_db),
):
    """
    Create a new user.

    Requires BUSINESS_ADMIN or SYSTEM_ADMIN role.

    - BUSINESS_ADMIN: Can only create users within their business
    - SYSTEM_ADMIN: Can create users for any business
    """
    # Check if username already exists
    existing_user = UserService.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    existing_email = UserService.get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # BUSINESS_ADMIN can only create users in their business
    if current_user.is_business_admin and not current_user.is_system_admin:
        if not current_user.business_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business administrator must be associated with a business",
            )

        # Force business_id to match admin's business
        user_data.business_id = current_user.business_id

        # BUSINESS_ADMIN cannot create SYSTEM_ADMIN users
        if user_data.role == UserRole.SYSTEM_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Business administrators cannot create system administrators",
            )

    # SYSTEM_ADMIN can create users for any business
    # but must specify business_id for non-SYSTEM_ADMIN users
    if current_user.is_system_admin:
        if user_data.role != UserRole.SYSTEM_ADMIN and not user_data.business_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="business_id required for non-system administrator users",
            )

    new_user = UserService.create_user(db, user_data)
    return UserResponse.model_validate(new_user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_business_admin),
    db: Session = Depends(get_db),
):
    """
    Update a user's information.

    Requires BUSINESS_ADMIN or SYSTEM_ADMIN role.

    - BUSINESS_ADMIN: Can only update users within their business, cannot change role or business_id
    - SYSTEM_ADMIN: Can update any user, including role and business_id
    """
    user = UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # BUSINESS_ADMIN restrictions
    if current_user.is_business_admin and not current_user.is_system_admin:
        # Can only update users in their business
        if user.business_id != current_user.business_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update users from other businesses",
            )

        # Cannot change role or business_id
        update_data = user_update.model_dump(exclude_unset=True)
        if "role" in update_data or "business_id" in update_data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Business administrators cannot change user roles or business associations",
            )

    updated_user = UserService.update_user(db, user_id, user_update)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(updated_user)


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    new_role: UserRole,
    current_user: User = Depends(get_system_admin),
    db: Session = Depends(get_db),
):
    """
    Update a user's role.

    Requires SYSTEM_ADMIN role.
    Only system administrators can change user roles.
    """
    user = UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent users from demoting themselves
    if user.id == current_user.id and new_role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot demote yourself from system administrator",
        )

    updated_user = UserService.update_user_role(db, user_id, new_role)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(updated_user)


@router.put("/{user_id}/business", response_model=UserResponse)
async def update_user_business(
    user_id: int,
    business_id: Optional[UUID],
    current_user: User = Depends(get_system_admin),
    db: Session = Depends(get_db),
):
    """
    Update a user's business association.

    Requires SYSTEM_ADMIN role.
    Only system administrators can change business associations.
    """
    user = UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Only SYSTEM_ADMIN users can have null business_id
    if business_id is None and user.role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only system administrators can have null business_id",
        )

    updated_user = UserService.update_user_business(db, user_id, business_id)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(updated_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_business_admin),
    db: Session = Depends(get_db),
):
    """
    Delete a user.

    Requires BUSINESS_ADMIN or SYSTEM_ADMIN role.

    - BUSINESS_ADMIN: Can only delete users within their business
    - SYSTEM_ADMIN: Can delete any user

    Note: Users cannot delete themselves.
    """
    # Cannot delete yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    user = UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # BUSINESS_ADMIN can only delete users in their business
    if current_user.is_business_admin and not current_user.is_system_admin:
        if user.business_id != current_user.business_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete users from other businesses",
            )

        # BUSINESS_ADMIN cannot delete SYSTEM_ADMIN users
        if user.role == UserRole.SYSTEM_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Business administrators cannot delete system administrators",
            )

    success = UserService.delete_user(db, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return None


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_business_admin),
    db: Session = Depends(get_db),
):
    """
    Deactivate a user account.

    Requires BUSINESS_ADMIN or SYSTEM_ADMIN role.

    - BUSINESS_ADMIN: Can only deactivate users within their business
    - SYSTEM_ADMIN: Can deactivate any user

    Note: Users cannot deactivate themselves.
    """
    # Cannot deactivate yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )

    user = UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # BUSINESS_ADMIN can only deactivate users in their business
    if current_user.is_business_admin and not current_user.is_system_admin:
        if user.business_id != current_user.business_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot deactivate users from other businesses",
            )

    success = UserService.deactivate_user(db, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    deactivated_user = UserService.get_user_by_id(db, user_id)
    return UserResponse.model_validate(deactivated_user)
