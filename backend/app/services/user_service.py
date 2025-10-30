"""User service layer for authentication and user management."""

from typing import Optional, List, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.schemas.auth import UserRegister, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    """Service for managing users."""

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get a user by username."""
        return db.query(User).filter(User.username == username.lower()).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get a user by email."""
        return db.query(User).filter(User.email == email.lower()).first()

    @staticmethod
    def create_user(db: Session, user_data: UserRegister) -> User:
        """
        Create a new user.

        Args:
            db: Database session
            user_data: User registration data

        Returns:
            Created user object
        """
        hashed_password = get_password_hash(user_data.password)

        db_user = User(
            username=user_data.username.lower(),
            email=user_data.email.lower(),
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
            role=user_data.role or UserRole.BASE_USER,
            business_id=user_data.business_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """
        Update a user's information.

        Args:
            db: Database session
            user_id: ID of user to update
            user_update: User update data

        Returns:
            Updated user object or None if not found
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None

        # Update only provided fields
        update_data = user_update.model_dump(exclude_unset=True)

        # Handle password separately
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            del update_data["password"]

        # Update email to lowercase if provided
        if "email" in update_data:
            update_data["email"] = update_data["email"].lower()

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db_user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by username and password.

        Args:
            db: Database session
            username: Username to authenticate
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = UserService.get_user_by_username(db, username)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        return user

    @staticmethod
    def change_password(
        db: Session, user_id: int, old_password: str, new_password: str
    ) -> bool:
        """
        Change a user's password.

        Args:
            db: Database session
            user_id: ID of user
            old_password: Current password
            new_password: New password

        Returns:
            True if password changed successfully, False otherwise
        """
        user = UserService.get_user_by_id(db, user_id)

        if not user:
            return False

        if not verify_password(old_password, user.hashed_password):
            return False

        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()

        db.commit()

        return True

    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> bool:
        """
        Deactivate a user account.

        Args:
            db: Database session
            user_id: ID of user to deactivate

        Returns:
            True if user deactivated, False if not found
        """
        user = UserService.get_user_by_id(db, user_id)

        if not user:
            return False

        user.is_active = False
        user.updated_at = datetime.utcnow()

        db.commit()

        return True

    @staticmethod
    def get_users_by_business(
        db: Session,
        business_id: UUID,
        skip: int = 0,
        limit: int = 50,
        is_active: Optional[bool] = None,
        role: Optional[UserRole] = None,
    ) -> Tuple[List[User], int]:
        """
        Get all users for a specific business with filtering.

        Args:
            db: Database session
            business_id: Business UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status
            role: Filter by role

        Returns:
            Tuple of (list of users, total count)
        """
        query = db.query(User).filter(User.business_id == business_id)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if role is not None:
            query = query.filter(User.role == role)

        total = query.count()
        users = query.offset(skip).limit(limit).all()

        return users, total

    @staticmethod
    def get_all_users(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        is_active: Optional[bool] = None,
        role: Optional[UserRole] = None,
        business_id: Optional[UUID] = None,
    ) -> Tuple[List[User], int]:
        """
        Get all users (SYSTEM_ADMIN only) with filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status
            role: Filter by role
            business_id: Filter by business

        Returns:
            Tuple of (list of users, total count)
        """
        query = db.query(User)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if role is not None:
            query = query.filter(User.role == role)

        if business_id is not None:
            query = query.filter(User.business_id == business_id)

        total = query.count()
        users = query.offset(skip).limit(limit).all()

        return users, total

    @staticmethod
    def update_user_role(
        db: Session,
        user_id: int,
        new_role: UserRole,
    ) -> Optional[User]:
        """
        Update a user's role.

        Args:
            db: Database session
            user_id: ID of user to update
            new_role: New role for the user

        Returns:
            Updated user or None if not found
        """
        user = UserService.get_user_by_id(db, user_id)

        if not user:
            return None

        user.role = new_role
        user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def update_user_business(
        db: Session,
        user_id: int,
        business_id: Optional[UUID],
    ) -> Optional[User]:
        """
        Update a user's business association.

        Args:
            db: Database session
            user_id: ID of user to update
            business_id: New business ID (None for system admins)

        Returns:
            Updated user or None if not found
        """
        user = UserService.get_user_by_id(db, user_id)

        if not user:
            return None

        user.business_id = business_id
        user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        Permanently delete a user.

        Args:
            db: Database session
            user_id: ID of user to delete

        Returns:
            True if user deleted, False if not found
        """
        user = UserService.get_user_by_id(db, user_id)

        if not user:
            return False

        db.delete(user)
        db.commit()

        return True
