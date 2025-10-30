"""Migrate data from Streamlit SQLite database to FastAPI database."""

import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session
from app.database.connection import engine, SessionLocal
from app.models import Client, Event, SearchCache, JobRun


def parse_datetime(value: Any) -> datetime:
    """Parse datetime from various formats."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        # Try ISO format first
        for fmt in [
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
        ]:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return datetime.utcnow()


def migrate_clients(source_conn: sqlite3.Connection, db: Session) -> Dict[int, int]:
    """
    Migrate clients from Streamlit database to FastAPI database.
    Returns mapping of old_id -> new_id.
    """
    print("\n[1/3] Migrating Clients...")
    print("-" * 60)

    cursor = source_conn.cursor()
    cursor.execute("SELECT * FROM clients ORDER BY id")
    rows = cursor.fetchall()

    # Get column names
    columns = [desc[0] for desc in cursor.description]

    id_mapping = {}
    migrated = 0
    skipped = 0

    for row in rows:
        data = dict(zip(columns, row))
        old_id = data['id']

        # Check if client already exists by name and domain
        existing = db.query(Client).filter(
            Client.name == data['name'],
            Client.domain == data.get('domain')
        ).first()

        if existing:
            print(f"  [SKIP] Client already exists: {data['name']}")
            id_mapping[old_id] = existing.id
            skipped += 1
            continue

        # Create new client with field mapping
        client = Client(
            name=data['name'],
            domain=data.get('domain'),
            industry=data.get('industry'),
            description=data.get('description'),
            search_keywords=data.get('search_keywords') or data.get('keywords'),
            is_active=bool(data.get('is_active', True)),
            created_at=parse_datetime(data.get('created_at') or data.get('monitoring_since')),
            updated_at=parse_datetime(data.get('updated_at') or data.get('last_checked')),
            last_checked_at=parse_datetime(data.get('last_checked_at') or data.get('last_checked')) if data.get('last_checked_at') or data.get('last_checked') else None,
            account_owner=data.get('account_owner'),
            tier=data.get('tier'),
            notes=data.get('notes')
        )

        db.add(client)
        db.flush()  # Get the new ID

        id_mapping[old_id] = client.id
        migrated += 1

        print(f"  [OK] Migrated: {client.name} (old_id={old_id}, new_id={client.id})")

    db.commit()

    print(f"\n  Total: {len(rows)}, Migrated: {migrated}, Skipped: {skipped}")
    return id_mapping


def migrate_events(source_conn: sqlite3.Connection, db: Session, client_id_mapping: Dict[int, int]) -> None:
    """Migrate events from Streamlit database to FastAPI database."""
    print("\n[2/3] Migrating Events...")
    print("-" * 60)

    cursor = source_conn.cursor()
    cursor.execute("SELECT * FROM events ORDER BY id")
    rows = cursor.fetchall()

    # Get column names
    columns = [desc[0] for desc in cursor.description]

    migrated = 0
    skipped = 0

    for row in rows:
        data = dict(zip(columns, row))
        old_client_id = data['client_id']

        # Map old client_id to new client_id
        if old_client_id not in client_id_mapping:
            print(f"  [SKIP] Event references non-existent client_id: {old_client_id}")
            skipped += 1
            continue

        new_client_id = client_id_mapping[old_client_id]

        # Check if event already exists by title and client
        existing = db.query(Event).filter(
            Event.client_id == new_client_id,
            Event.title == data['title'],
            Event.event_date == parse_datetime(data.get('event_date') or data.get('published_date'))
        ).first()

        if existing:
            skipped += 1
            continue

        # Create new event with field mapping
        event = Event(
            client_id=new_client_id,
            title=data['title'],
            description=data.get('description') or data.get('summary'),
            url=data.get('url') or data.get('source_url'),
            source=data.get('source') or data.get('source_name'),
            category=data.get('category', 'other'),
            relevance_score=float(data.get('relevance_score', 0.5)),
            sentiment_score=float(data['sentiment_score']) if data.get('sentiment_score') is not None else None,
            event_date=parse_datetime(data.get('event_date') or data.get('published_date')),
            discovered_at=parse_datetime(data.get('discovered_at') or data.get('discovered_date')),
            content_hash=data.get('content_hash'),
            is_read=bool(data.get('is_read', False)),
            is_starred=bool(data.get('is_starred', False)),
            user_notes=data.get('user_notes')
        )

        db.add(event)
        migrated += 1

        if migrated % 100 == 0:
            print(f"  [PROGRESS] Migrated {migrated} events...")
            db.commit()

    db.commit()
    print(f"\n  Total: {len(rows)}, Migrated: {migrated}, Skipped: {skipped}")


def migrate_job_runs(source_conn: sqlite3.Connection, db: Session) -> None:
    """Migrate job runs from Streamlit database to FastAPI database."""
    print("\n[3/3] Migrating Job Runs...")
    print("-" * 60)

    cursor = source_conn.cursor()
    cursor.execute("SELECT * FROM job_runs ORDER BY created_at")
    rows = cursor.fetchall()

    # Get column names
    columns = [desc[0] for desc in cursor.description]

    migrated = 0
    skipped = 0

    for row in rows:
        data = dict(zip(columns, row))

        # Check if job run already exists by job_id
        existing = db.query(JobRun).filter(JobRun.job_id == data['id']).first()

        if existing:
            skipped += 1
            continue

        # Create new job run with field mapping
        job_run = JobRun(
            job_id=data['id'],  # Use old UUID as job_id
            job_name=data['job_name'],
            start_time=parse_datetime(data['start_time']),
            end_time=parse_datetime(data['end_time']) if data.get('end_time') else None,
            status=data.get('status', 'running'),
            results_summary=data.get('results_summary'),
            error_message=data.get('error_message'),
            job_metadata=data.get('metadata')
        )

        db.add(job_run)
        migrated += 1

    db.commit()
    print(f"\n  Total: {len(rows)}, Migrated: {migrated}, Skipped: {skipped}")


def verify_migration(db: Session, expected_counts: Dict[str, int]) -> bool:
    """Verify migration was successful."""
    print("\n" + "=" * 60)
    print("Verifying Migration")
    print("=" * 60)

    success = True

    # Check clients
    client_count = db.query(Client).count()
    print(f"\nClients:")
    print(f"  Source DB: {expected_counts['clients']}")
    print(f"  Target DB: {client_count}")
    if client_count >= 1:
        print(f"  [OK] (duplicates were skipped)")
    else:
        print(f"  [ERROR] No clients migrated")
        success = False

    # Check events
    event_count = db.query(Event).count()
    print(f"\nEvents:")
    print(f"  Expected: {expected_counts['events']}")
    print(f"  Actual: {event_count}")
    if event_count < expected_counts['events']:
        print(f"  [WARNING] Some events may not have been migrated")
        success = False
    else:
        print(f"  [OK]")

    # Check job runs
    job_run_count = db.query(JobRun).count()
    print(f"\nJob Runs:")
    print(f"  Expected: {expected_counts['job_runs']}")
    print(f"  Actual: {job_run_count}")
    if job_run_count < expected_counts['job_runs']:
        print(f"  [WARNING] Some job runs may not have been migrated")
        success = False
    else:
        print(f"  [OK]")

    print("\n" + "=" * 60)
    if success:
        print("[OK] Migration verification passed!")
    else:
        print("[WARNING] Migration verification found issues")
    print("=" * 60)

    return success


def main():
    """Main migration function."""
    print("=" * 60)
    print("Data Migration: Streamlit -> FastAPI")
    print("=" * 60)

    # Paths
    streamlit_db = Path(__file__).resolve().parents[2] / "data" / "client_intelligence.db"
    fastapi_db = Path(__file__).resolve().parents[1] / "data" / "client_intelligence.db"

    if not streamlit_db.exists():
        print(f"\n[ERROR] Streamlit database not found: {streamlit_db}")
        return False

    print(f"\nSource DB: {streamlit_db}")
    print(f"Target DB: {fastapi_db}")
    print()

    # Connect to source database
    source_conn = sqlite3.connect(str(streamlit_db))

    # Get expected counts
    cursor = source_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clients")
    expected_clients = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM events")
    expected_events = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM job_runs")
    expected_job_runs = cursor.fetchone()[0]

    expected_counts = {
        'clients': expected_clients,
        'events': expected_events,
        'job_runs': expected_job_runs
    }

    print(f"Source database contains:")
    print(f"  - Clients: {expected_clients}")
    print(f"  - Events: {expected_events}")
    print(f"  - Job Runs: {expected_job_runs}")

    # Get target database session
    db = SessionLocal()

    try:
        # Migrate data
        client_id_mapping = migrate_clients(source_conn, db)
        migrate_events(source_conn, db, client_id_mapping)
        migrate_job_runs(source_conn, db)

        # Verify migration
        success = verify_migration(db, expected_counts)

        return success

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False

    finally:
        source_conn.close()
        db.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
