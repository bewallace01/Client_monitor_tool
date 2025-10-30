"""Business service layer for business logic."""

from typing import Optional, List, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.models import Business, AuditLog
from app.schemas import BusinessCreate, BusinessUpdate


class BusinessService:
    """Service for managing businesses."""

    @staticmethod
    def _create_audit_log(
        db: Session,
        business_id: UUID,
        user_id: int,
        action: str,
        table_name: str,
        record_id: UUID,
        changes: Optional[dict] = None
    ):
        """Helper method to create audit log entries."""
        from uuid import uuid4
        import json

        # Extract old/new values from changes dict
        old_values = {}
        new_values = {}
        changed_fields = []

        if changes:
            for field, value in changes.items():
                if isinstance(value, dict) and 'old' in value and 'new' in value:
                    old_values[field] = value['old']
                    new_values[field] = value['new']
                    changed_fields.append(field)
                else:
                    # Simple value (for CREATE/DELETE)
                    new_values[field] = value
                    changed_fields.append(field)

        audit_log = AuditLog(
            id=uuid4(),
            business_id=business_id,
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=str(record_id),
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            changed_fields=json.dumps(changed_fields) if changed_fields else None,
            created_at=datetime.utcnow()
        )
        db.add(audit_log)

    @staticmethod
    def get_businesses(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        industry: Optional[str] = None,
        is_active: Optional[bool] = None,
        subscription_tier: Optional[str] = None,
        sort_by: str = "updated_at",
        sort_desc: bool = True,
    ) -> Tuple[List[Business], int]:
        """
        Get list of businesses with filtering, sorting, and pagination.

        Returns tuple of (businesses, total_count).
        """
        query = db.query(Business)

        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Business.name.ilike(search_term),
                    Business.domain.ilike(search_term),
                    Business.industry.ilike(search_term),
                )
            )

        if industry:
            query = query.filter(Business.industry == industry)

        if is_active is not None:
            query = query.filter(Business.is_active == is_active)

        if subscription_tier:
            query = query.filter(Business.tier == subscription_tier)

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        sort_column = getattr(Business, sort_by, Business.updated_at)
        if sort_desc:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        businesses = query.offset(skip).limit(limit).all()

        return businesses, total

    @staticmethod
    def get_business(
        db: Session,
        business_id: UUID
    ) -> Optional[Business]:
        """Get a single business by ID."""
        return db.query(Business).filter(Business.id == business_id).first()

    @staticmethod
    def get_business_by_name(
        db: Session,
        name: str
    ) -> Optional[Business]:
        """Get a business by name."""
        return db.query(Business).filter(Business.name == name).first()

    @staticmethod
    def create_business(
        db: Session,
        business: BusinessCreate,
        user_id: int
    ) -> Business:
        """Create a new business."""
        from uuid import uuid4
        from pathlib import Path

        business_id = uuid4()
        db_business = Business(
            id=business_id,
            name=business.name,
            domain=business.domain,
            industry=business.industry,
            size=business.size,
            contact_email=business.contact_email,
            contact_phone=business.contact_phone,
            address=business.address,
            tier=business.subscription_tier,
            subscription_status=business.subscription_status,
            is_active=business.is_active if business.is_active is not None else True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(db_business)

        # Create audit log
        BusinessService._create_audit_log(
            db=db,
            business_id=business_id,
            user_id=user_id,
            action="CREATE",
            table_name="businesses",
            record_id=business_id,
            changes={"name": business.name}
        )

        db.commit()
        db.refresh(db_business)

        # Create API configuration file for the new business
        from app.services.api_config_service import APIConfigService
        try:
            config_file_path = APIConfigService.create_config_file(business_id, [])
            print(f"[INFO] Created API config file for business {business_id}: {config_file_path}")
        except Exception as e:
            print(f"[WARNING] Failed to create API config file for business {business_id}: {e}")

        return db_business

    @staticmethod
    def update_business(
        db: Session,
        business_id: UUID,
        business_update: BusinessUpdate,
        user_id: int
    ) -> Optional[Business]:
        """Update an existing business."""
        db_business = db.query(Business).filter(
            Business.id == business_id
        ).first()

        if not db_business:
            return None

        # Track changes for audit log
        update_data = business_update.model_dump(exclude_unset=True)
        changes = {}
        for field, value in update_data.items():
            # Map frontend field names to database field names
            db_field = field
            if field == "subscription_tier":
                db_field = "tier"

            old_value = getattr(db_business, db_field)
            if old_value != value:
                changes[db_field] = {"old": str(old_value), "new": str(value)}
                setattr(db_business, db_field, value)

        db_business.updated_at = datetime.utcnow()

        # Create audit log if there were changes
        if changes:
            BusinessService._create_audit_log(
                db=db,
                business_id=business_id,
                user_id=user_id,
                action="UPDATE",
                table_name="businesses",
                record_id=business_id,
                changes=changes
            )

        db.commit()
        db.refresh(db_business)
        return db_business

    @staticmethod
    def delete_business(
        db: Session,
        business_id: UUID,
        user_id: int
    ) -> bool:
        """
        Delete a business (permanently).

        Warning: This will cascade delete all associated users, clients, and events.

        Returns True if deleted, False if not found.
        """
        db_business = db.query(Business).filter(Business.id == business_id).first()

        if not db_business:
            return False

        # Create audit log before deletion
        BusinessService._create_audit_log(
            db=db,
            business_id=business_id,
            user_id=user_id,
            action="HARD_DELETE",
            table_name="businesses",
            record_id=business_id,
            changes={"name": db_business.name}
        )

        db.delete(db_business)
        db.commit()
        return True

    @staticmethod
    def activate_business(
        db: Session,
        business_id: UUID,
        user_id: int
    ) -> Optional[Business]:
        """Activate a business."""
        db_business = db.query(Business).filter(Business.id == business_id).first()

        if not db_business:
            return None

        if db_business.is_active:
            return db_business  # Already active

        db_business.is_active = True
        db_business.updated_at = datetime.utcnow()

        BusinessService._create_audit_log(
            db=db,
            business_id=business_id,
            user_id=user_id,
            action="ACTIVATE",
            table_name="businesses",
            record_id=business_id,
            changes={"is_active": {"old": "False", "new": "True"}}
        )

        db.commit()
        db.refresh(db_business)
        return db_business

    @staticmethod
    def deactivate_business(
        db: Session,
        business_id: UUID,
        user_id: int
    ) -> Optional[Business]:
        """Deactivate a business."""
        db_business = db.query(Business).filter(Business.id == business_id).first()

        if not db_business:
            return None

        if not db_business.is_active:
            return db_business  # Already inactive

        db_business.is_active = False
        db_business.updated_at = datetime.utcnow()

        BusinessService._create_audit_log(
            db=db,
            business_id=business_id,
            user_id=user_id,
            action="DEACTIVATE",
            table_name="businesses",
            record_id=business_id,
            changes={"is_active": {"old": "True", "new": "False"}}
        )

        db.commit()
        db.refresh(db_business)
        return db_business

    @staticmethod
    def get_all_industries(db: Session) -> List[str]:
        """Get list of all unique industries."""
        industries = db.query(Business.industry).filter(
            Business.industry.isnot(None)
        ).distinct().all()
        return [industry[0] for industry in industries]

    @staticmethod
    def get_all_tiers(db: Session) -> List[str]:
        """Get list of all unique tiers."""
        tiers = db.query(Business.tier).filter(
            Business.tier.isnot(None)
        ).distinct().all()
        return [tier[0] for tier in tiers]
