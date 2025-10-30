"""Import legacy data from JSON export into new UUID-based database.

This script imports the data exported in Step 5.2.1 into the new UUID-based database structure.
It handles:
- Creating admin user with SYSTEM_ADMIN role
- Importing clients with UUID generation
- Importing events with UUID generation
- Creating EventUserInteraction records for read/starred events
- Importing job runs
- Linking all data to default business

Usage:
    python scripts/import_legacy_data.py
"""

import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import (
    Business, User, Client, Event, EventUserInteraction, JobRun,
    SearchCache, UserRole
)

# Default business ID from create_default_business.py
DEFAULT_BUSINESS_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def load_export_data() -> dict:
    """Load the exported JSON data."""
    print("[INFO] Looking for export file...")
    export_dir = Path(__file__).parent.parent / "data" / "exports"

    # Find the most recent export file
    export_files = list(export_dir.glob("database_export_*.json"))
    if not export_files:
        print("[ERROR] No export file found in", export_dir)
        sys.exit(1)

    latest_export = max(export_files, key=lambda p: p.stat().st_mtime)
    print(f"[INFO] Found export file: {latest_export.name}")

    with open(latest_export, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"[INFO] Export date: {data['export_metadata']['export_date']}")
    print(f"[INFO] Record counts:")
    for key, count in data['record_counts'].items():
        print(f"       - {key}: {count:,}")
    print()

    return data


def create_or_update_admin_user(db: Session) -> User:
    """Create or update admin user with SYSTEM_ADMIN role."""
    print("[INFO] Creating/updating admin user...")

    # Check if admin user exists
    admin = db.query(User).filter(User.username == ADMIN_USERNAME).first()

    if admin:
        print(f"[INFO] Admin user exists (ID: {admin.id}), updating role...")
        admin.role = UserRole.SYSTEM_ADMIN
        admin.is_superuser = True
        admin.business_id = None  # System admins are not tied to a business
        admin.updated_at = datetime.utcnow()
    else:
        print(f"[INFO] Creating new admin user...")
        admin = User(
            username=ADMIN_USERNAME,
            email="admin@system.local",
            full_name="System Administrator",
            hashed_password=get_password_hash(ADMIN_PASSWORD),
            is_active=True,
            is_superuser=True,
            role=UserRole.SYSTEM_ADMIN,
            business_id=None,
            sso_enabled=False,
            password_reset_required=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(admin)

    db.commit()
    db.refresh(admin)

    print(f"[SUCCESS] Admin user ready:")
    print(f"          Username: {admin.username}")
    print(f"          ID: {admin.id}")
    print(f"          Role: {admin.role}")
    print()

    return admin


def import_clients(db: Session, clients_data: List[dict], business_id: uuid.UUID, admin_user_id: int) -> Dict[int, uuid.UUID]:
    """Import clients and return mapping of old ID to new UUID."""
    print(f"[INFO] Importing {len(clients_data)} clients...")

    id_mapping = {}
    imported_count = 0

    for old_client in clients_data:
        try:
            # Generate new UUID
            new_uuid = uuid.uuid4()
            old_id = old_client['id']

            # Parse dates
            created_at = datetime.fromisoformat(old_client['created_at'])
            updated_at = datetime.fromisoformat(old_client['updated_at'])
            last_checked_at = datetime.fromisoformat(old_client['last_checked_at']) if old_client.get('last_checked_at') else None

            # Create new client with UUID
            client = Client(
                id=new_uuid,
                business_id=business_id,
                name=old_client['name'],
                domain=old_client.get('domain'),
                industry=old_client.get('industry'),
                description=old_client.get('description'),
                search_keywords=old_client.get('search_keywords'),
                monitoring_frequency="daily",
                is_active=old_client['is_active'],
                created_at=created_at,
                updated_at=updated_at,
                last_checked_at=last_checked_at,
                tier=old_client.get('tier'),
                notes=old_client.get('notes'),
                created_by_user_id=admin_user_id,
                is_deleted=False,
            )

            db.add(client)
            id_mapping[old_id] = new_uuid
            imported_count += 1

            if imported_count % 10 == 0:
                print(f"       Imported {imported_count} clients...")

        except Exception as e:
            print(f"[ERROR] Failed to import client '{old_client.get('name', 'Unknown')}': {e}")
            continue

    db.commit()
    print(f"[SUCCESS] Imported {imported_count} clients")
    print()

    return id_mapping


def import_events(
    db: Session,
    events_data: List[dict],
    business_id: uuid.UUID,
    admin_user_id: int,
    client_id_mapping: Dict[int, uuid.UUID]
) -> Dict[int, uuid.UUID]:
    """Import events and return mapping of old ID to new UUID."""
    print(f"[INFO] Importing {len(events_data)} events...")

    id_mapping = {}
    imported_count = 0
    skipped_count = 0

    for old_event in events_data:
        try:
            # Map old client_id to new UUID
            old_client_id = old_event['client_id']
            if old_client_id not in client_id_mapping:
                print(f"[WARN] Event '{old_event.get('title', 'Unknown')}' references unknown client ID {old_client_id}, skipping")
                skipped_count += 1
                continue

            new_client_uuid = client_id_mapping[old_client_id]

            # Generate new UUID for event
            new_uuid = uuid.uuid4()
            old_id = old_event['id']

            # Parse dates
            event_date = datetime.fromisoformat(old_event['event_date'])
            discovered_at = datetime.fromisoformat(old_event['discovered_at'])

            # Create new event with UUID
            event = Event(
                id=new_uuid,
                business_id=business_id,
                client_id=new_client_uuid,
                title=old_event['title'],
                description=old_event.get('description'),
                url=old_event.get('url'),
                source=old_event.get('source'),
                category=old_event['category'],
                relevance_score=old_event['relevance_score'],
                sentiment_score=old_event.get('sentiment_score'),
                event_date=event_date,
                discovered_at=discovered_at,
                content_hash=old_event.get('content_hash'),
                is_read=old_event.get('is_read', False),
                is_starred=old_event.get('is_starred', False),
                user_notes=old_event.get('user_notes'),
                created_by_user_id=admin_user_id,
                is_deleted=False,
            )

            db.add(event)
            id_mapping[old_id] = new_uuid
            imported_count += 1

            if imported_count % 100 == 0:
                print(f"       Imported {imported_count} events...")

        except Exception as e:
            print(f"[ERROR] Failed to import event '{old_event.get('title', 'Unknown')}': {e}")
            skipped_count += 1
            continue

    db.commit()
    print(f"[SUCCESS] Imported {imported_count} events")
    if skipped_count > 0:
        print(f"[WARN] Skipped {skipped_count} events")
    print()

    return id_mapping


def create_event_interactions(
    db: Session,
    events_data: List[dict],
    admin_user_id: int,
    event_id_mapping: Dict[int, uuid.UUID]
):
    """Create EventUserInteraction records for read/starred events."""
    print("[INFO] Creating EventUserInteraction records...")

    interaction_count = 0

    for old_event in events_data:
        old_id = old_event['id']
        if old_id not in event_id_mapping:
            continue

        new_uuid = event_id_mapping[old_id]
        is_read = old_event.get('is_read', False)
        is_starred = old_event.get('is_starred', False)
        user_notes = old_event.get('user_notes')

        # Only create interaction if there's something to track
        if is_read or is_starred or user_notes:
            interaction = EventUserInteraction(
                id=uuid.uuid4(),
                event_id=new_uuid,
                user_id=admin_user_id,
                is_read=is_read,
                read_at=datetime.utcnow() if is_read else None,
                is_starred=is_starred,
                starred_at=datetime.utcnow() if is_starred else None,
                user_notes=user_notes,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(interaction)
            interaction_count += 1

    db.commit()
    print(f"[SUCCESS] Created {interaction_count} EventUserInteraction records")
    print()


def import_job_runs(db: Session, job_runs_data: List[dict]):
    """Import job runs with UUID generation."""
    print(f"[INFO] Importing {len(job_runs_data)} job runs...")

    imported_count = 0

    for old_job_run in job_runs_data:
        try:
            # Parse dates
            started_at = datetime.fromisoformat(old_job_run['started_at'])
            completed_at = datetime.fromisoformat(old_job_run['completed_at']) if old_job_run.get('completed_at') else None

            # Create new job run with UUID
            job_run = JobRun(
                id=uuid.uuid4(),
                job_id=old_job_run['job_id'],
                job_type=old_job_run['job_type'],
                started_at=started_at,
                completed_at=completed_at,
                status=old_job_run['status'],
                events_found=old_job_run.get('events_found', 0),
                events_new=old_job_run.get('events_new', 0),
                clients_processed=old_job_run.get('clients_processed', 0),
                error_message=old_job_run.get('error_message'),
                job_metadata=old_job_run.get('job_metadata'),
            )

            db.add(job_run)
            imported_count += 1

        except Exception as e:
            print(f"[ERROR] Failed to import job run: {e}")
            continue

    db.commit()
    print(f"[SUCCESS] Imported {imported_count} job runs")
    print()


def verify_data_integrity(db: Session, export_data: dict):
    """Verify imported data matches export counts."""
    print("=" * 80)
    print("DATA INTEGRITY VERIFICATION")
    print("=" * 80)
    print()

    # Count imported records
    client_count = db.query(Client).filter(Client.is_deleted == False).count()
    event_count = db.query(Event).filter(Event.is_deleted == False).count()
    job_run_count = db.query(JobRun).count()
    user_count = db.query(User).count()
    interaction_count = db.query(EventUserInteraction).count()

    # Expected counts
    expected_clients = export_data['record_counts']['clients']
    expected_events = export_data['record_counts']['events']
    expected_job_runs = export_data['record_counts']['job_runs']

    print("Record Counts:")
    print(f"  Clients:      {client_count:,} / {expected_clients:,} expected", "[OK]" if client_count == expected_clients else "[FAIL]")
    print(f"  Events:       {event_count:,} / {expected_events:,} expected", "[OK]" if event_count == expected_events else "[FAIL]")
    print(f"  Job Runs:     {job_run_count:,} / {expected_job_runs:,} expected", "[OK]" if job_run_count == expected_job_runs else "[FAIL]")
    print(f"  Users:        {user_count:,}")
    print(f"  Interactions: {interaction_count:,}")
    print()

    # Verify business assignments
    clients_with_business = db.query(Client).filter(Client.business_id == DEFAULT_BUSINESS_ID).count()
    events_with_business = db.query(Event).filter(Event.business_id == DEFAULT_BUSINESS_ID).count()

    print("Business Assignments:")
    print(f"  Clients with business_id: {clients_with_business:,} / {client_count:,}", "[OK]" if clients_with_business == client_count else "[FAIL]")
    print(f"  Events with business_id:  {events_with_business:,} / {event_count:,}", "[OK]" if events_with_business == event_count else "[FAIL]")
    print()

    # Verify relationships
    events_with_valid_client = db.query(Event).join(Client, Event.client_id == Client.id).count()
    print("Relationships:")
    print(f"  Events with valid client: {events_with_valid_client:,} / {event_count:,}", "[OK]" if events_with_valid_client == event_count else "[FAIL]")
    print()

    success = (
        client_count == expected_clients and
        event_count == expected_events and
        job_run_count == expected_job_runs and
        clients_with_business == client_count and
        events_with_business == event_count and
        events_with_valid_client == event_count
    )

    if success:
        print("[SUCCESS] Data integrity verified! All checks passed.")
    else:
        print("[WARNING] Some integrity checks failed. Please review the data.")
    print()

    return success


def main():
    """Main import function."""
    print("=" * 80)
    print("LEGACY DATA IMPORT SCRIPT")
    print("=" * 80)
    print()

    # Load export data
    export_data = load_export_data()

    # Create database connection
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if settings.USE_SQLITE else {}
    )
    db = Session(engine)

    try:
        # Verify default business exists
        business = db.query(Business).filter(Business.id == DEFAULT_BUSINESS_ID).first()
        if not business:
            print("[ERROR] Default business not found. Run create_default_business.py first.")
            sys.exit(1)

        print(f"[INFO] Using business: {business.name} ({business.id})")
        print()

        # Create/update admin user
        admin = create_or_update_admin_user(db)

        # Import clients
        client_id_mapping = import_clients(
            db,
            export_data['data']['clients'],
            DEFAULT_BUSINESS_ID,
            admin.id
        )

        # Import events
        event_id_mapping = import_events(
            db,
            export_data['data']['events'],
            DEFAULT_BUSINESS_ID,
            admin.id,
            client_id_mapping
        )

        # Create event interactions
        create_event_interactions(
            db,
            export_data['data']['events'],
            admin.id,
            event_id_mapping
        )

        # Import job runs
        import_job_runs(db, export_data['data']['job_runs'])

        # Verify data integrity
        success = verify_data_integrity(db, export_data)

        if success:
            print("=" * 80)
            print("IMPORT COMPLETE")
            print("=" * 80)
            print()
            print("Next steps:")
            print("  1. Start the backend server to verify the API works")
            print("  2. Login with admin/admin123")
            print("  3. Verify clients and events are visible")
            print()
        else:
            print("=" * 80)
            print("IMPORT COMPLETED WITH WARNINGS")
            print("=" * 80)
            print()
            print("Please review the warnings above and verify the data manually.")
            print()

    except Exception as e:
        print()
        print("=" * 80)
        print("IMPORT FAILED")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
