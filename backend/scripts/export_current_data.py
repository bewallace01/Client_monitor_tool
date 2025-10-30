"""
Export current database data to JSON files for migration.

This script exports all data from the current database before the UUID migration.
It creates backups of:
- Clients
- Events
- Job Runs
- Users
- Search Cache

Usage:
    python scripts/export_current_data.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, MetaData, Table
from app.core.config import settings

# Import directly from database URL to avoid model relationship issues
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if settings.USE_SQLITE else {})
metadata = MetaData()
metadata.reflect(bind=engine)


def serialize_datetime(obj: Any) -> str:
    """Serialize datetime objects to ISO format."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def export_clients(connection) -> List[Dict]:
    """Export all clients to dict format."""
    clients_table = metadata.tables.get('clients')
    if clients_table is None:
        print("[WARN] Clients table not found")
        return []

    result = connection.execute(clients_table.select())

    client_list = []
    for row in result:
        client_dict = dict(row._mapping)
        # Convert datetime objects to ISO format
        for key, value in client_dict.items():
            if isinstance(value, datetime):
                client_dict[key] = value.isoformat()
        client_list.append(client_dict)

    print(f"[OK] Exported {len(client_list)} clients")
    return client_list


def export_events(connection) -> List[Dict]:
    """Export all events to dict format."""
    events_table = metadata.tables.get('events')
    if events_table is None:
        print("[WARN] Events table not found")
        return []

    result = connection.execute(events_table.select())

    event_list = []
    for row in result:
        event_dict = dict(row._mapping)
        # Convert datetime objects to ISO format
        for key, value in event_dict.items():
            if isinstance(value, datetime):
                event_dict[key] = value.isoformat()
        event_list.append(event_dict)

    print(f"[OK] Exported {len(event_list)} events")
    return event_list


def export_job_runs(connection) -> List[Dict]:
    """Export all job runs to dict format."""
    job_runs_table = metadata.tables.get('job_runs')
    if job_runs_table is None:
        print("[WARN] Job runs table not found")
        return []

    result = connection.execute(job_runs_table.select())

    job_run_list = []
    for row in result:
        job_run_dict = dict(row._mapping)
        # Convert datetime objects to ISO format
        for key, value in job_run_dict.items():
            if isinstance(value, datetime):
                job_run_dict[key] = value.isoformat()
        job_run_list.append(job_run_dict)

    print(f"[OK] Exported {len(job_run_list)} job runs")
    return job_run_list


def export_users(connection) -> List[Dict]:
    """Export all users to dict format."""
    users_table = metadata.tables.get('users')
    if users_table is None:
        print("[WARN] Users table not found")
        return []

    result = connection.execute(users_table.select())

    user_list = []
    for row in result:
        user_dict = dict(row._mapping)
        # Convert datetime objects to ISO format
        for key, value in user_dict.items():
            if isinstance(value, datetime):
                user_dict[key] = value.isoformat()
        user_list.append(user_dict)

    print(f"[OK] Exported {len(user_list)} users")
    return user_list


def export_search_cache(connection) -> List[Dict]:
    """Export all search cache entries to dict format."""
    try:
        search_cache_table = metadata.tables.get('search_cache')
        if search_cache_table is None:
            print("[WARN] Search cache table not found")
            return []

        result = connection.execute(search_cache_table.select())

        cache_list = []
        for row in result:
            cache_dict = dict(row._mapping)
            # Convert datetime objects to ISO format
            for key, value in cache_dict.items():
                if isinstance(value, datetime):
                    cache_dict[key] = value.isoformat()
            cache_list.append(cache_dict)

        print(f"[OK] Exported {len(cache_list)} search cache entries")
        return cache_list
    except Exception as e:
        print(f"[WARN] Could not export search cache: {e}")
        return []


def main():
    """Main export function."""
    print("=" * 80)
    print("DATABASE EXPORT SCRIPT")
    print("=" * 80)
    print()
    print("This will export all data from the current database to JSON files.")
    print()

    # Create exports directory
    export_dir = Path(__file__).parent.parent / "data" / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    # Create database connection
    connection = engine.connect()

    try:
        # Export all data
        print("Starting export...")
        print()

        clients = export_clients(connection)
        events = export_events(connection)
        job_runs = export_job_runs(connection)
        users = export_users(connection)
        search_cache = export_search_cache(connection)

        # Create combined export
        export_data = {
            "export_metadata": {
                "export_date": datetime.utcnow().isoformat(),
                "database_type": "SQLite",
                "export_version": "1.0",
            },
            "record_counts": {
                "clients": len(clients),
                "events": len(events),
                "job_runs": len(job_runs),
                "users": len(users),
                "search_cache": len(search_cache),
            },
            "data": {
                "clients": clients,
                "events": events,
                "job_runs": job_runs,
                "users": users,
                "search_cache": search_cache,
            }
        }

        # Save combined export
        combined_file = export_dir / f"database_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print()
        print("=" * 80)
        print("EXPORT COMPLETE")
        print("=" * 80)
        print()
        print(f"Combined export: {combined_file}")
        print()
        print("Summary:")
        print(f"  • Clients:      {len(clients):,}")
        print(f"  • Events:       {len(events):,}")
        print(f"  • Job Runs:     {len(job_runs):,}")
        print(f"  • Users:        {len(users):,}")
        print(f"  • Search Cache: {len(search_cache):,}")
        print()

        # Also save individual files for easier inspection
        individual_files = {
            "clients_backup.json": clients,
            "events_backup.json": events,
            "job_runs_backup.json": job_runs,
            "users_backup.json": users,
            "search_cache_backup.json": search_cache,
        }

        for filename, data in individual_files.items():
            filepath = export_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        print("Individual backup files created:")
        for filename in individual_files.keys():
            print(f"  • {filename}")
        print()

        # Calculate total file size
        total_size = sum(f.stat().st_size for f in export_dir.glob("*.json"))
        print(f"Total export size: {total_size / 1024 / 1024:.2f} MB")
        print()

        print("[SUCCESS] Export completed successfully!")
        print()
        print("Next steps:")
        print("  1. Backup the database file: backend/data/client_intelligence.db")
        print("  2. Verify the exported JSON files are valid")
        print("  3. Proceed with database migration")
        print()

    except Exception as e:
        print()
        print("=" * 80)
        print("EXPORT FAILED")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
