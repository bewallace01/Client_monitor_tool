"""Verify data migration was successful with detailed spot checks."""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models import Client, Event, JobRun


def verify_migration():
    """Verify the data migration was successful."""
    print("=" * 60)
    print("Data Migration Verification")
    print("=" * 60)
    print()

    db = SessionLocal()

    try:
        # Count records
        client_count = db.query(Client).count()
        event_count = db.query(Event).count()
        job_run_count = db.query(JobRun).count()

        print("Record Counts:")
        print(f"  Clients: {client_count}")
        print(f"  Events: {event_count}")
        print(f"  Job Runs: {job_run_count}")
        print()

        # Check client data integrity
        print("Client Data Sample (first 5):")
        print("-" * 60)
        clients = db.query(Client).limit(5).all()
        for client in clients:
            print(f"  ID: {client.id}")
            print(f"  Name: {client.name}")
            print(f"  Domain: {client.domain}")
            print(f"  Industry: {client.industry}")
            print(f"  Active: {client.is_active}")
            print(f"  Tier: {client.tier}")
            print()

        # Check event data integrity
        print("Event Data Sample (first 5):")
        print("-" * 60)
        events = db.query(Event).limit(5).all()
        for event in events:
            print(f"  ID: {event.id}")
            print(f"  Client ID: {event.client_id}")
            print(f"  Title: {event.title[:50]}...")
            print(f"  Category: {event.category}")
            print(f"  Relevance: {event.relevance_score}")
            print(f"  Sentiment: {event.sentiment_score}")
            print(f"  Read: {event.is_read}")
            print()

        # Check job run data integrity
        print("Job Run Data Sample (first 5):")
        print("-" * 60)
        job_runs = db.query(JobRun).order_by(JobRun.start_time.desc()).limit(5).all()
        for job_run in job_runs:
            print(f"  ID: {job_run.id}")
            print(f"  Job ID: {job_run.job_id}")
            print(f"  Job Name: {job_run.job_name}")
            print(f"  Status: {job_run.status}")
            print(f"  Start: {job_run.start_time}")
            print(f"  End: {job_run.end_time}")
            if job_run.results_summary:
                summary = job_run.results_summary[:70] + "..." if len(job_run.results_summary) > 70 else job_run.results_summary
                print(f"  Summary: {summary}")
            print()

        # Check relationships
        print("Relationship Verification:")
        print("-" * 60)
        client_with_events = db.query(Client).join(Event).first()
        if client_with_events:
            events_for_client = db.query(Event).filter(Event.client_id == client_with_events.id).count()
            print(f"  Client: {client_with_events.name}")
            print(f"  Events: {events_for_client}")
            print(f"  [OK] Client-Event relationship works")
        else:
            print(f"  [WARNING] No clients with events found")
        print()

        # Check data distribution
        print("Data Distribution:")
        print("-" * 60)
        active_clients = db.query(Client).filter(Client.is_active == True).count()
        inactive_clients = client_count - active_clients
        print(f"  Active Clients: {active_clients}")
        print(f"  Inactive Clients: {inactive_clients}")

        read_events = db.query(Event).filter(Event.is_read == True).count()
        unread_events = event_count - read_events
        print(f"  Read Events: {read_events}")
        print(f"  Unread Events: {unread_events}")

        starred_events = db.query(Event).filter(Event.is_starred == True).count()
        print(f"  Starred Events: {starred_events}")
        print()

        # Check event categories
        from sqlalchemy import func
        print("Events by Category:")
        print("-" * 60)
        categories = db.query(
            Event.category,
            func.count(Event.id)
        ).group_by(Event.category).all()
        for category, count in categories:
            print(f"  {category}: {count}")
        print()

        # Check job statuses
        print("Job Runs by Status:")
        print("-" * 60)
        statuses = db.query(
            JobRun.status,
            func.count(JobRun.id)
        ).group_by(JobRun.status).all()
        for status, count in statuses:
            print(f"  {status}: {count}")
        print()

        print("=" * 60)
        print("[OK] Migration verification complete!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[ERROR] Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = verify_migration()
    sys.exit(0 if success else 1)
