"""User preference API endpoints."""

import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.dependencies import get_current_active_user as get_current_user
from app.models.user import User
from app.schemas.user_preference import (
    UserPreferenceResponse,
    UserPreferenceUpdate,
    UserPreferenceCreate
)
from app.services.user_preference_service import UserPreferenceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user-preferences", tags=["User Preferences"])


@router.get("/me", response_model=UserPreferenceResponse)
def get_my_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's notification preferences.

    Creates default preferences if none exist.
    """
    try:
        preferences = UserPreferenceService.get_or_create_preferences(
            db=db,
            user_id=current_user.id,
            business_id=current_user.business_id
        )

        return preferences

    except Exception as e:
        logger.error(f"Error fetching user preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user preferences"
        )


@router.put("/me", response_model=UserPreferenceResponse)
def update_my_preferences(
    updates: UserPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's notification preferences.
    """
    try:
        # Get or create preferences first
        preferences = UserPreferenceService.get_or_create_preferences(
            db=db,
            user_id=current_user.id,
            business_id=current_user.business_id
        )

        # Update preferences
        updated_preferences = UserPreferenceService.update_preferences(
            db=db,
            preference_id=preferences.id,
            updates=updates
        )

        if not updated_preferences:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preferences not found"
            )

        logger.info(f"Updated preferences for user {current_user.id}")
        return updated_preferences

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user preferences"
        )


@router.get("/{user_id}", response_model=UserPreferenceResponse)
def get_user_preferences(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get preferences for a specific user (admin only).

    Regular users can only access their own preferences via /me endpoint.
    """
    # Check if user is admin or accessing their own preferences
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access other users' preferences"
        )

    try:
        preferences = UserPreferenceService.get_preferences_by_user_id(
            db=db,
            user_id=user_id
        )

        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preferences not found for this user"
            )

        # Verify same business
        if preferences.business_id != current_user.business_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access preferences from another business"
            )

        return preferences

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user preferences"
        )


@router.post("/", response_model=UserPreferenceResponse)
def create_preferences(
    preference_data: UserPreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create preferences for a user (admin only).

    Regular users get default preferences created automatically.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create preferences for other users"
        )

    # Ensure business_id matches current user's business
    if preference_data.business_id != current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create preferences for users in other businesses"
        )

    try:
        preferences = UserPreferenceService.create_preferences(
            db=db,
            preference_data=preference_data
        )

        logger.info(f"Admin {current_user.id} created preferences for user {preference_data.user_id}")
        return preferences

    except Exception as e:
        logger.error(f"Error creating user preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user preferences"
        )


@router.delete("/{preference_id}")
def delete_preferences(
    preference_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete user preferences (admin only).

    This will reset preferences to defaults on next access.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete preferences"
        )

    try:
        success = UserPreferenceService.delete_preferences(
            db=db,
            preference_id=preference_id,
            business_id=current_user.business_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preferences not found"
            )

        logger.info(f"Admin {current_user.id} deleted preferences {preference_id}")
        return {"message": "Preferences deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user preferences"
        )
