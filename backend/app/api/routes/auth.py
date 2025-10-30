"""Authentication API endpoints."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.auth import (
    Token,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
    PasswordChange,
)
from app.services.user_service import UserService
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.api.dependencies import get_current_user, get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account.

    - **username**: Unique username (3-50 characters, alphanumeric + underscores)
    - **email**: Valid email address
    - **password**: Password (minimum 6 characters)
    - **full_name**: Optional full name

    Returns the created user object (excluding password).
    """
    # Check if username already exists
    existing_user = UserService.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )

    # Check if email already exists
    existing_email = UserService.get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create new user
    user = UserService.create_user(db, user_data)

    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.

    - **username**: Username
    - **password**: Password

    Returns JWT access token for subsequent authenticated requests.
    """
    # Authenticate user
    user = UserService.authenticate_user(db, credentials.username, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires,
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role.value,
        business_id=user.business_id,
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user's information.

    Requires valid JWT token in Authorization header.
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update current user's information.

    - **email**: New email address (optional)
    - **full_name**: New full name (optional)
    - **password**: New password (optional)

    Only provided fields will be updated.
    """
    # If email is being updated, check it's not already in use
    if user_update.email and user_update.email.lower() != current_user.email:
        existing_email = UserService.get_user_by_email(db, user_update.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use",
            )

    # Update user
    updated_user = UserService.update_user(db, current_user.id, user_update)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(updated_user)


@router.post("/change-password", response_model=dict)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Change current user's password.

    - **old_password**: Current password
    - **new_password**: New password (minimum 6 characters)

    Requires valid current password.
    """
    success = UserService.change_password(
        db,
        current_user.id,
        password_data.old_password,
        password_data.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    return {"message": "Password changed successfully"}


@router.post("/logout", response_model=dict)
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user.

    Note: With JWT tokens, actual logout is handled client-side by
    removing the token. This endpoint is here for API completeness
    and could be extended to implement token blacklisting.
    """
    return {"message": "Logged out successfully"}
