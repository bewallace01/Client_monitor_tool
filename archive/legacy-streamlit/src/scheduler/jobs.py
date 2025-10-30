"""Scheduled job definitions for automated monitoring."""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from src.storage import SQLiteStorage
from src.collectors.factory import get_collector
from src.processors.event_classifier import classify_event
from src.processors.relevance_scorer import update_event_relevance
from src.processors.deduplicator import filter_duplicates
from src.models.job_run import JobRun

logger = logging.getLogger(__name__)


def daily_scan_job(storage: SQLiteStorage, client_filter: Optional[List[str]] = None, job_name: str = "daily_scan") -> JobRun:
    """
    Run monitoring scan for active clients.

    Args:
        storage: SQLiteStorage instance
        client_filter: Optional list of client names to scan. If None, scans all active clients.
        job_name: Name for the job run (e.g., "daily_scan", "quick_scan", "targeted_scan")

    Returns:
        JobRun object with execution results
    """
    job_run = JobRun(
        id=str(uuid.uuid4()),
        job_name=job_name,
        start_time=datetime.utcnow(),
    )

    try:
        logger.info(f"Starting {job_name} job...")
        storage.create_job_run(job_run)

        # Get all active clients
        clients = storage.get_all_clients()
        active_clients = [c for c in clients if c.is_active]

        # Apply filter if provided
        if client_filter:
            active_clients = [c for c in active_clients if c.name in client_filter]

        # Track statistics
        total_clients = len(active_clients)
        total_events_found = 0
        total_new_events = 0
        clients_processed = 0

        # Get collector
        collector = get_collector()

        for client in active_clients:
            try:
                # Generate search query
                query = client.name

                # Search for events
                results = collector.search(
                    query=query,
                    from_date=datetime.utcnow() - timedelta(days=1),
                    max_results=10
                )

                total_events_found += len(results)

                # Get existing events for deduplication
                existing_events = storage.get_events_by_client(client.id)

                # Process and save new events
                for result in results:
                    event = classify_event(result, client)
                    event = update_event_relevance(event, client)

                    # Check if event already exists
                    unique_events = filter_duplicates([event], existing_events)

                    if unique_events:
                        storage.create_event(event)
                        total_new_events += 1

                # Update client last checked
                storage.update_client(client.id, {
                    'last_checked': datetime.utcnow()
                })

                clients_processed += 1

            except Exception as e:
                logger.error(f"Error processing client {client.name}: {e}")

        # Mark job as completed
        results_summary = (
            f"Processed {clients_processed}/{total_clients} clients. "
            f"Found {total_events_found} events, {total_new_events} new."
        )
        job_run.mark_completed(results_summary)
        job_run.metadata = {
            "total_clients": total_clients,
            "clients_processed": clients_processed,
            "total_events_found": total_events_found,
            "total_new_events": total_new_events,
        }

        logger.info(f"Daily scan completed: {results_summary}")

    except Exception as e:
        error_msg = f"Daily scan failed: {str(e)}"
        logger.error(error_msg)
        job_run.mark_failed(error_msg)

    finally:
        storage.update_job_run(job_run)

    return job_run


def weekly_report_job(storage: SQLiteStorage) -> JobRun:
    """
    Generate weekly summary report.

    Returns:
        JobRun object with execution results
    """
    job_run = JobRun(
        id=str(uuid.uuid4()),
        job_name="weekly_report",
        start_time=datetime.utcnow(),
    )

    try:
        logger.info("Starting weekly report job...")
        storage.create_job_run(job_run)

        # Get events from last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        all_events = storage.get_all_events()
        weekly_events = [e for e in all_events if e.discovered_date >= week_ago]

        # Get all clients
        clients = storage.get_all_clients()
        active_clients = [c for c in clients if c.is_active]

        # Calculate statistics
        total_events = len(weekly_events)
        new_events = len([e for e in weekly_events if e.status == "new"])
        high_relevance = len([e for e in weekly_events if e.relevance_score >= 0.7])

        # Events by client
        events_by_client = {}
        for client in active_clients:
            client_events = [e for e in weekly_events if e.client_id == client.id]
            if client_events:
                events_by_client[client.name] = len(client_events)

        # Top 5 clients by events
        top_clients = sorted(events_by_client.items(), key=lambda x: x[1], reverse=True)[:5]

        # Build report summary
        report_lines = [
            f"Weekly Report ({week_ago.strftime('%Y-%m-%d')} to {datetime.utcnow().strftime('%Y-%m-%d')})",
            f"Total Events: {total_events}",
            f"New Events: {new_events}",
            f"High Relevance: {high_relevance}",
            f"Active Clients: {len(active_clients)}",
            "",
            "Top Clients by Events:",
        ]

        for client_name, count in top_clients:
            report_lines.append(f"  - {client_name}: {count} events")

        results_summary = "\n".join(report_lines)

        job_run.mark_completed(results_summary)
        job_run.metadata = {
            "total_events": total_events,
            "new_events": new_events,
            "high_relevance": high_relevance,
            "active_clients": len(active_clients),
            "top_clients": dict(top_clients),
        }

        logger.info(f"Weekly report generated: {total_events} events")

    except Exception as e:
        error_msg = f"Weekly report failed: {str(e)}"
        logger.error(error_msg)
        job_run.mark_failed(error_msg)

    finally:
        storage.update_job_run(job_run)

    return job_run


def cache_cleanup_job(storage: SQLiteStorage) -> JobRun:
    """
    Remove expired cache entries.

    Returns:
        JobRun object with execution results
    """
    job_run = JobRun(
        id=str(uuid.uuid4()),
        job_name="cache_cleanup",
        start_time=datetime.utcnow(),
    )

    try:
        logger.info("Starting cache cleanup job...")
        storage.create_job_run(job_run)

        # Delete expired cache entries
        deleted_count = storage.delete_expired_cache()

        results_summary = f"Cleaned up {deleted_count} expired cache entries"
        job_run.mark_completed(results_summary)
        job_run.metadata = {
            "deleted_count": deleted_count,
        }

        logger.info(results_summary)

    except Exception as e:
        error_msg = f"Cache cleanup failed: {str(e)}"
        logger.error(error_msg)
        job_run.mark_failed(error_msg)

    finally:
        storage.update_job_run(job_run)

    return job_run


# Job registry for easy access
JOBS = {
    "daily_scan": daily_scan_job,
    "weekly_report": weekly_report_job,
    "cache_cleanup": cache_cleanup_job,
}


def run_job(job_name: str, storage: SQLiteStorage) -> JobRun:
    """
    Run a job by name.

    Args:
        job_name: Name of the job to run
        storage: Storage instance

    Returns:
        JobRun object with results

    Raises:
        ValueError: If job name is not recognized
    """
    if job_name not in JOBS:
        raise ValueError(f"Unknown job: {job_name}")

    return JOBS[job_name](storage)
