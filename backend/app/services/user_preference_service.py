"""User preference service for managing notification and automation settings."""

import json
import logging
from typing import Optional, List
from datetime import time
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.user_preference import UserPreference
from app.models.user import User
from app.models.event import Event
from app.schemas.user_preference import UserPreferenceCreate, UserPreferenceUpdate

logger = logging.getLogger(__name__)


class UserPreferenceService:
    """Service for managing user notification preferences."""

    @staticmethod
    def get_or_create_preferences(
        db: Session,
        user_id: int,
        business_id: UUID
    ) -> UserPreference:
        """
        Get user preferences, create with defaults if doesn't exist.

        Args:
            db: Database session
            user_id: User ID
            business_id: Business UUID

        Returns:
            UserPreference instance
        """
        preferences = db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()

        if not preferences:
            logger.info(f"Creating default preferences for user {user_id}")
            preferences = UserPreference(
                user_id=user_id,
                business_id=business_id,
                notification_enabled=True,
                email_notifications_enabled=True,
                relevance_threshold=0.7,
                notification_categories=None,  # All categories
                notification_frequency="instant",
                assigned_clients_only=False,
                digest_time=time(9, 0, 0),  # 9:00 AM
                digest_day_of_week=0  # Monday
            )
            db.add(preferences)
            db.commit()
            db.refresh(preferences)

        return preferences

    @staticmethod
    def get_preferences(
        db: Session,
        user_id: int
    ) -> Optional[UserPreference]:
        """Get user preferences."""
        return db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()

    @staticmethod
    def update_preferences(
        db: Session,
        preference_id: UUID,
        updates: UserPreferenceUpdate
    ) -> Optional[UserPreference]:
        """
        Update user preferences by preference ID.

        Args:
            db: Database session
            preference_id: UserPreference UUID
            updates: UserPreferenceUpdate schema

        Returns:
            Updated UserPreference or None if not found
        """
        preferences = db.query(UserPreference).filter(
            UserPreference.id == preference_id
        ).first()

        if not preferences:
            logger.warning(f"No preferences found with ID {preference_id}")
            return None

        # Update only provided fields
        update_data = updates.model_dump(exclude_unset=True)

        # Handle notification_categories JSON serialization
        if "notification_categories" in update_data:
            categories = update_data["notification_categories"]
            if categories is not None:
                update_data["notification_categories"] = json.dumps(categories)

        for field, value in update_data.items():
            setattr(preferences, field, value)

        db.commit()
        db.refresh(preferences)

        logger.info(f"Updated preferences for user {preferences.user_id}")
        return preferences

    @staticmethod
    def reset_to_defaults(
        db: Session,
        user_id: int,
        business_id: UUID
    ) -> UserPreference:
        """Reset user preferences to defaults."""
        preferences = db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()

        if preferences:
            db.delete(preferences)
            db.commit()

        # Create new with defaults
        return UserPreferenceService.get_or_create_preferences(db, user_id, business_id)

    @staticmethod
    def should_notify_for_event(
        preferences: UserPreference,
        event: Event,
        user_assigned_to_client: bool = False
    ) -> bool:
        """
        Check if user should be notified about an event.

        Args:
            preferences: UserPreference instance
            event: Event instance
            user_assigned_to_client: Whether user is assigned to the client

        Returns:
            True if user should be notified
        """
        # Check if notifications enabled
        if not preferences.notification_enabled:
            return False

        # Check relevance threshold
        if event.relevance_score < preferences.relevance_threshold:
            return False

        # Check category filters
        if preferences.notification_categories:
            try:
                allowed_categories = json.loads(preferences.notification_categories)
                if event.category not in allowed_categories:
                    return False
            except (json.JSONDecodeError, TypeError):
                logger.error(f"Failed to parse notification_categories for user {preferences.user_id}")

        # Check assigned clients only
        if preferences.assigned_clients_only and not user_assigned_to_client:
            return False

        return True

    @staticmethod
    def get_users_to_notify(
        db: Session,
        business_id: UUID,
        event: Event
    ) -> List[User]:
        """
        Get list of users who should be notified about an event.

        Args:
            db: Database session
            business_id: Business UUID
            event: Event instance

        Returns:
            List of User instances to notify
        """
        # Get all active users in the business
        users = db.query(User).filter(
            User.business_id == business_id,
            User.is_active == True
        ).all()

        users_to_notify = []

        for user in users:
            # Get user preferences
            preferences = UserPreferenceService.get_or_create_preferences(
                db, user.id, business_id
            )

            # Check if instant notifications enabled
            if not preferences.should_send_instant_notifications:
                continue

            # Check if user is assigned to the client
            user_assigned = event.client.assigned_to_user_id == user.id

            # Check if should notify
            if UserPreferenceService.should_notify_for_event(
                preferences, event, user_assigned
            ):
                users_to_notify.append(user)

        logger.info(
            f"Found {len(users_to_notify)} users to notify for event {event.id}"
        )
        return users_to_notify

    @staticmethod
    def get_users_for_digest(
        db: Session,
        business_id: UUID,
        frequency: str,
        current_time: time = None,
        current_day: int = None
    ) -> List[tuple[User, UserPreference]]:
        """
        Get users who should receive digest emails.

        Args:
            db: Database session
            business_id: Business UUID
            frequency: "daily" or "weekly"
            current_time: Current time (for testing)
            current_day: Current day of week (for testing, 0=Monday)

        Returns:
            List of (User, UserPreference) tuples
        """
        if current_time is None:
            from datetime import datetime
            current_time = datetime.utcnow().time()

        if current_day is None:
            from datetime import datetime
            current_day = datetime.utcnow().weekday()

        # Query users with digest preferences
        query = db.query(User, UserPreference).join(
            UserPreference, User.id == UserPreference.user_id
        ).filter(
            User.business_id == business_id,
            User.is_active == True,
            UserPreference.notification_enabled == True,
            UserPreference.email_notifications_enabled == True,
            UserPreference.notification_frequency == frequency
        )

        results = query.all()

        # Filter by time/day
        users_for_digest = []
        for user, prefs in results:
            # Check digest time (within 1 hour window)
            if prefs.digest_time:
                time_diff = abs(
                    (current_time.hour * 60 + current_time.minute) -
                    (prefs.digest_time.hour * 60 + prefs.digest_time.minute)
                )
                if time_diff > 60:  # More than 1 hour difference
                    continue

            # For weekly, check day of week
            if frequency == "weekly":
                if prefs.digest_day_of_week != current_day:
                    continue

            users_for_digest.append((user, prefs))

        logger.info(
            f"Found {len(users_for_digest)} users for {frequency} digest"
        )
        return users_for_digest

    @staticmethod
    def get_preferences_by_user_id(
        db: Session,
        user_id: int
    ) -> Optional[UserPreference]:
        """Get user preferences by user ID."""
        return db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()

    @staticmethod
    def create_preferences(
        db: Session,
        preference_data: UserPreferenceCreate
    ) -> UserPreference:
        """
        Create new user preferences.

        Args:
            db: Database session
            preference_data: UserPreferenceCreate schema

        Returns:
            Created UserPreference instance
        """
        # Handle notification_categories JSON serialization
        categories_json = None
        if preference_data.notification_categories is not None:
            categories_json = json.dumps(preference_data.notification_categories)

        preferences = UserPreference(
            user_id=preference_data.user_id,
            business_id=preference_data.business_id,
            notification_enabled=preference_data.notification_enabled,
            email_notifications_enabled=preference_data.email_notifications_enabled,
            relevance_threshold=preference_data.relevance_threshold,
            notification_categories=categories_json,
            notification_frequency=preference_data.notification_frequency,
            assigned_clients_only=preference_data.assigned_clients_only,
            digest_time=preference_data.digest_time,
            digest_day_of_week=preference_data.digest_day_of_week
        )

        db.add(preferences)
        db.commit()
        db.refresh(preferences)

        logger.info(f"Created preferences for user {preference_data.user_id}")
        return preferences

    @staticmethod
    def delete_preferences(
        db: Session,
        preference_id: UUID,
        business_id: Optional[UUID] = None
    ) -> bool:
        """
        Delete user preferences.

        Args:
            db: Database session
            preference_id: UserPreference UUID
            business_id: Optional business ID for validation

        Returns:
            True if deleted, False if not found
        """
        query = db.query(UserPreference).filter(
            UserPreference.id == preference_id
        )

        if business_id:
            query = query.filter(UserPreference.business_id == business_id)

        preferences = query.first()
        if not preferences:
            return False

        db.delete(preferences)
        db.commit()

        logger.info(f"Deleted preferences {preference_id}")
        return True

    @staticmethod
    def parse_notification_categories(preferences: UserPreference) -> Optional[List[str]]:
        """Parse notification categories from JSON string."""
        if not preferences.notification_categories:
            return None

        try:
            return json.loads(preferences.notification_categories)
        except (json.JSONDecodeError, TypeError):
            logger.error(
                f"Failed to parse notification_categories for user {preferences.user_id}"
            )
            return None
