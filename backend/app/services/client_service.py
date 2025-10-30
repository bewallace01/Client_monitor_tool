"""Client service layer for business logic."""

from typing import Optional, List, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.models import Client, AuditLog, User
from app.schemas import ClientCreate, ClientUpdate


class ClientService:
    """Service for managing clients."""

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
    def get_clients(
        db: Session,
        business_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        industry: Optional[str] = None,
        is_active: Optional[bool] = None,
        tier: Optional[str] = None,
        sort_by: str = "updated_at",
        sort_desc: bool = True,
        include_deleted: bool = False,
    ) -> Tuple[List[Client], int]:
        """
        Get list of clients with filtering, sorting, and pagination.

        If business_id is None, returns all clients (for system admins).
        Returns tuple of (clients, total_count).
        """
        query = db.query(Client)

        # Filter by business_id if provided (None means all clients for system admin)
        if business_id is not None:
            query = query.filter(Client.business_id == business_id)

        # Soft delete filter
        if not include_deleted:
            query = query.filter(Client.is_deleted == False)

        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Client.name.ilike(search_term),
                    Client.domain.ilike(search_term),
                    Client.description.ilike(search_term),
                    Client.search_keywords.ilike(search_term),
                )
            )

        if industry:
            query = query.filter(Client.industry == industry)

        if is_active is not None:
            query = query.filter(Client.is_active == is_active)

        if tier:
            query = query.filter(Client.tier == tier)

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        sort_column = getattr(Client, sort_by, Client.updated_at)
        if sort_desc:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        clients = query.offset(skip).limit(limit).all()

        return clients, total

    @staticmethod
    def get_client(
        db: Session,
        client_id: UUID,
        business_id: Optional[UUID] = None,
        include_deleted: bool = False
    ) -> Optional[Client]:
        """Get a single client by ID. If business_id is None, searches all clients (for system admins)."""
        query = db.query(Client).filter(Client.id == client_id)

        # Filter by business_id only if provided (not None for system admin)
        if business_id is not None:
            query = query.filter(Client.business_id == business_id)

        if not include_deleted:
            query = query.filter(Client.is_deleted == False)

        return query.first()

    @staticmethod
    def get_client_by_name(
        db: Session,
        name: str,
        business_id: Optional[UUID] = None,
        include_deleted: bool = False
    ) -> Optional[Client]:
        """Get a client by name. If business_id is None, searches all clients (for system admins)."""
        query = db.query(Client).filter(Client.name == name)

        # Filter by business_id only if provided (not None for system admin)
        if business_id is not None:
            query = query.filter(Client.business_id == business_id)

        if not include_deleted:
            query = query.filter(Client.is_deleted == False)

        return query.first()

    @staticmethod
    def create_client(
        db: Session,
        client: ClientCreate,
        business_id: UUID,
        user_id: int
    ) -> Client:
        """Create a new client."""
        from uuid import uuid4

        client_id = uuid4()
        db_client = Client(
            id=client_id,
            business_id=business_id,
            name=client.name,
            domain=client.domain,
            industry=client.industry,
            description=client.description,
            company_size=client.company_size,
            revenue_range=client.revenue_range,
            headquarters_location=client.headquarters_location,
            founded_year=client.founded_year,
            search_keywords=client.search_keywords,
            monitoring_frequency=client.monitoring_frequency or "daily",
            is_active=client.is_active if client.is_active is not None else True,
            assigned_to_user_id=client.assigned_to_user_id,
            tier=client.tier,
            health_score=client.health_score,
            notes=client.notes,
            created_by_user_id=user_id,
            is_deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(db_client)

        # Create audit log
        ClientService._create_audit_log(
            db=db,
            business_id=business_id,
            user_id=user_id,
            action="CREATE",
            table_name="clients",
            record_id=client_id,
            changes={"name": client.name}
        )

        db.commit()
        db.refresh(db_client)
        return db_client

    @staticmethod
    def update_client(
        db: Session,
        client_id: UUID,
        business_id: UUID,
        client_update: ClientUpdate,
        user_id: int
    ) -> Optional[Client]:
        """Update an existing client."""
        db_client = db.query(Client).filter(
            Client.id == client_id,
            Client.business_id == business_id,
            Client.is_deleted == False
        ).first()

        if not db_client:
            return None

        # Track changes for audit log
        update_data = client_update.model_dump(exclude_unset=True)
        changes = {}
        for field, value in update_data.items():
            old_value = getattr(db_client, field)
            if old_value != value:
                changes[field] = {"old": str(old_value), "new": str(value)}
                setattr(db_client, field, value)

        db_client.updated_at = datetime.utcnow()

        # Create audit log if there were changes
        if changes:
            ClientService._create_audit_log(
                db=db,
                business_id=business_id,
                user_id=user_id,
                action="UPDATE",
                table_name="clients",
                record_id=client_id,
                changes=changes
            )

        db.commit()
        db.refresh(db_client)
        return db_client

    @staticmethod
    def delete_client(
        db: Session,
        client_id: UUID,
        business_id: UUID,
        user_id: int,
        hard_delete: bool = False,
        is_system_admin: bool = False
    ) -> bool:
        """
        Delete a client (soft delete by default).

        Args:
            db: Database session
            client_id: UUID of client to delete
            business_id: UUID of business for authorization (can be None for system admin)
            user_id: User performing the deletion
            hard_delete: If True, permanently delete; if False, soft delete (default)
            is_system_admin: If True, bypass business_id check

        Returns True if deleted, False if not found.
        """
        # System admins can delete any client
        if is_system_admin:
            db_client = db.query(Client).filter(Client.id == client_id).first()
        else:
            db_client = db.query(Client).filter(
                Client.id == client_id,
                Client.business_id == business_id
            ).first()

        if not db_client:
            return False

        # Use client's business_id for audit log if business_id is None (system admin)
        audit_business_id = business_id or db_client.business_id

        if hard_delete:
            # Permanent deletion
            db.delete(db_client)
            ClientService._create_audit_log(
                db=db,
                business_id=audit_business_id,
                user_id=user_id,
                action="HARD_DELETE",
                table_name="clients",
                record_id=client_id,
                changes={"name": db_client.name}
            )
        else:
            # Soft delete
            if db_client.is_deleted:
                return False  # Already deleted

            db_client.is_deleted = True
            db_client.deleted_at = datetime.utcnow()
            db_client.deleted_by_user_id = user_id

            ClientService._create_audit_log(
                db=db,
                business_id=audit_business_id,
                user_id=user_id,
                action="DELETE",
                table_name="clients",
                record_id=client_id,
                changes={"name": db_client.name}
            )

        db.commit()
        return True

    @staticmethod
    def restore_client(
        db: Session,
        client_id: UUID,
        business_id: UUID,
        user_id: int
    ) -> Optional[Client]:
        """
        Restore a soft-deleted client.

        Returns the restored client or None if not found.
        """
        db_client = db.query(Client).filter(
            Client.id == client_id,
            Client.business_id == business_id,
            Client.is_deleted == True
        ).first()

        if not db_client:
            return None

        db_client.is_deleted = False
        db_client.deleted_at = None
        db_client.deleted_by_user_id = None
        db_client.updated_at = datetime.utcnow()

        ClientService._create_audit_log(
            db=db,
            business_id=business_id,
            user_id=user_id,
            action="RESTORE",
            table_name="clients",
            record_id=client_id,
            changes={"name": db_client.name}
        )

        db.commit()
        db.refresh(db_client)
        return db_client

    @staticmethod
    def get_client_stats(db: Session, business_id: UUID) -> dict:
        """Get statistics about clients for a specific business."""
        base_query = db.query(Client).filter(
            Client.business_id == business_id,
            Client.is_deleted == False
        )

        total_clients = base_query.count()
        active_clients = base_query.filter(Client.is_active == True).count()
        inactive_clients = total_clients - active_clients

        # Clients by tier
        tier_stats = (
            base_query.filter(Client.tier.isnot(None))
            .with_entities(Client.tier, func.count(Client.id))
            .group_by(Client.tier)
            .all()
        )
        clients_by_tier = {tier: count for tier, count in tier_stats}

        # Clients by industry
        industry_stats = (
            base_query.filter(Client.industry.isnot(None))
            .with_entities(Client.industry, func.count(Client.id))
            .group_by(Client.industry)
            .all()
        )
        clients_by_industry = {industry: count for industry, count in industry_stats}

        return {
            "total_clients": total_clients,
            "active_clients": active_clients,
            "inactive_clients": inactive_clients,
            "clients_by_tier": clients_by_tier,
            "clients_by_industry": clients_by_industry,
        }

    @staticmethod
    def get_all_industries(db: Session, business_id: Optional[UUID] = None) -> List[str]:
        """Get list of all unique industries for a specific business (or all if None)."""
        query = db.query(Client.industry).filter(
            Client.is_deleted == False,
            Client.industry.isnot(None)
        )

        # Filter by business_id only if provided (not None for system admin)
        if business_id is not None:
            query = query.filter(Client.business_id == business_id)

        industries = query.distinct().all()
        return [industry[0] for industry in industries]

    @staticmethod
    def get_all_tiers(db: Session, business_id: Optional[UUID] = None) -> List[str]:
        """Get list of all unique tiers for a specific business (or all if None)."""
        query = db.query(Client.tier).filter(
            Client.is_deleted == False,
            Client.tier.isnot(None)
        )

        # Filter by business_id only if provided (not None for system admin)
        if business_id is not None:
            query = query.filter(Client.business_id == business_id)

        tiers = query.distinct().all()
        return [tier[0] for tier in tiers]
