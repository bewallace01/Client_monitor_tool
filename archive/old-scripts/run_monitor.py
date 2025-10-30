"""Main monitoring script to collect and process events for all clients."""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.storage import SQLiteStorage
from src.collectors.factory import get_collector
from src.processors.event_classifier import classify_event
from src.processors.relevance_scorer import update_event_relevance
from src.processors.deduplicator import filter_duplicates
from src.models.event_dto import EventDTO


def generate_search_queries(client_name: str) -> List[str]:
    """
    Generate search queries for a client.

    Args:
        client_name: Name of the client

    Returns:
        List of search queries
    """
    # Base queries
    queries = [
        client_name,  # Just the name
        f"{client_name} funding",
        f"{client_name} acquisition",
        f"{client_name} partnership",
        f"{client_name} product launch",
    ]

    return queries


def run_monitoring(
    lookback_days: int = 7,
    min_relevance_score: float = 0.6,
    max_results_per_query: int = 10
):
    """
    Run the monitoring process for all active clients.

    Args:
        lookback_days: How many days back to search
        min_relevance_score: Minimum relevance score to save events
        max_results_per_query: Max results per search query
    """
    print("=" * 60)
    print("CLIENT INTELLIGENCE MONITOR - Starting Scan")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Lookback: {lookback_days} days")
    print(f"Min Relevance: {min_relevance_score}")
    print("-" * 60)

    # Initialize storage and collector
    storage = SQLiteStorage()
    storage.connect()
    collector = get_collector()

    # Get all active clients
    clients = storage.get_all_clients()
    active_clients = [c for c in clients if c.is_active]

    print(f"\n[CLIENTS] Found {len(active_clients)} active clients to monitor\n")

    # Track statistics
    total_searched = 0
    total_found = 0
    total_new = 0
    total_duplicates = 0
    total_low_relevance = 0

    # Process each client
    for i, client in enumerate(active_clients, 1):
        print(f"\n[{i}/{len(active_clients)}] Processing: {client.name}")
        print("-" * 40)

        # Generate queries
        queries = generate_search_queries(client.name)
        print(f"  [SEARCH] Searching with {len(queries)} queries...")

        # Get existing events for deduplication
        existing_events = storage.get_events_by_client(client.id)

        # Collect results from all queries
        all_results = []
        for query in queries:
            try:
                results = collector.search(
                    query=query,
                    from_date=datetime.utcnow() - timedelta(days=lookback_days),
                    max_results=max_results_per_query
                )
                all_results.extend(results)
                total_searched += 1
            except Exception as e:
                print(f"  [ERROR] Error searching '{query}': {e}")

        print(f"  [RESULTS] Found {len(all_results)} raw results")
        total_found += len(all_results)

        # Process results
        new_events = []
        for result in all_results:
            # Classify event
            event = classify_event(result, client)

            # Calculate relevance
            event = update_event_relevance(event, client)

            # Check if meets relevance threshold
            if event.relevance_score >= min_relevance_score:
                new_events.append(event)
            else:
                total_low_relevance += 1

        # Filter duplicates
        unique_events = filter_duplicates(new_events, existing_events)
        duplicates_found = len(new_events) - len(unique_events)
        total_duplicates += duplicates_found

        print(f"  [SAVED] New events: {len(unique_events)} (filtered {duplicates_found} duplicates)")

        # Save events
        for event in unique_events:
            try:
                storage.create_event(event)
                total_new += 1
            except Exception as e:
                print(f"  [ERROR] Error saving event: {e}")

        # Update client last_checked
        try:
            storage.update_client(client.id, {
                'last_checked': datetime.utcnow()
            })
        except Exception as e:
            print(f"  [WARNING] Error updating client: {e}")

    # Print summary
    print("\n" + "=" * 60)
    print("SCAN COMPLETE - Summary")
    print("=" * 60)
    print(f"[OK] Clients monitored: {len(active_clients)}")
    print(f"[SEARCH] Queries executed: {total_searched}")
    print(f"[RESULTS] Raw results found: {total_found}")
    print(f"[NEW] New events saved: {total_new}")
    print(f"[SKIP] Duplicates filtered: {total_duplicates}")
    print(f"[SKIP] Low relevance filtered: {total_low_relevance}")
    print("=" * 60)

    # Show rate limit status if available
    if hasattr(collector, 'get_rate_limit_status'):
        rate_limit = collector.get_rate_limit_status()
        print(f"\n[RATE_LIMIT] Status:")
        print(f"  - Limit: {rate_limit.get('limit', 'N/A')}")
        print(f"  - Remaining: {rate_limit.get('remaining', 'N/A')}")
        print(f"  - Resets at: {rate_limit.get('reset_at', 'N/A')}")

    print(f"\n[DONE] Scan completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run client intelligence monitoring")
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=7,
        help="Number of days to look back (default: 7)"
    )
    parser.add_argument(
        "--min-relevance",
        type=float,
        default=0.6,
        help="Minimum relevance score to save events (default: 0.6)"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Max results per query (default: 10)"
    )

    args = parser.parse_args()

    run_monitoring(
        lookback_days=args.lookback_days,
        min_relevance_score=args.min_relevance,
        max_results_per_query=args.max_results
    )
