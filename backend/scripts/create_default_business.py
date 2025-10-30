"""Create default business for data migration.

This script creates a default business that will be used during the data import process.
All existing clients and events will be associated with this business.
"""

import sys
import uuid
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.core.config import settings
from app.models import Business

# Default business details
DEFAULT_BUSINESS_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEFAULT_BUSINESS_NAME = "Default Organization"


def create_default_business():
    """Create the default business for data migration."""
    print("=" * 80)
    print("CREATE DEFAULT BUSINESS")
    print("=" * 80)
    print()

    # Create engine and session
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if settings.USE_SQLITE else {}
    )
    db = Session(engine)

    try:
        # Check if business already exists
        existing = db.query(Business).filter(Business.id == DEFAULT_BUSINESS_ID).first()
        if existing:
            print(f"[INFO] Default business already exists: {existing.name}")
            print(f"       ID: {existing.id}")
            print(f"       Active: {existing.is_active}")
            print()
            return existing

        # Create new business
        business = Business(
            id=DEFAULT_BUSINESS_ID,
            name=DEFAULT_BUSINESS_NAME,
            domain=None,
            industry=None,
            tier="enterprise",
            is_active=True,
            sso_enabled=False,
            sso_provider=None,
            sso_config=None,
            sso_domain=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(business)
        db.commit()
        db.refresh(business)

        print("[SUCCESS] Created default business:")
        print(f"          Name: {business.name}")
        print(f"          ID: {business.id}")
        print(f"          Tier: {business.tier}")
        print(f"          Active: {business.is_active}")
        print()
        print("This business will be used for all existing data during migration.")
        print()

        return business

    except Exception as e:
        print()
        print("[ERROR] Failed to create default business:")
        print(f"        {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    create_default_business()
