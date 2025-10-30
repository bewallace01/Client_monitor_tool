"""
Seed script to populate database with sample clients and events.
Run this to get started quickly with demo data.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timedelta
import random
from src.storage import Database, ClientRepository, EventRepository
from src.collectors import MockCollector
from src.models import EventCategory


def create_sample_clients(session):
    """Create sample client companies."""
    sample_clients = [
        {
            "name": "Salesforce",
            "domain": "salesforce.com",
            "industry": "Enterprise SaaS",
            "description": "Cloud-based CRM platform",
            "account_owner": "You",
            "tier": "Enterprise",
        },
        {
            "name": "Zoom",
            "domain": "zoom.us",
            "industry": "Communication",
            "description": "Video conferencing platform",
            "account_owner": "You",
            "tier": "Enterprise",
        },
        {
            "name": "Shopify",
            "domain": "shopify.com",
            "industry": "E-commerce",
            "description": "E-commerce platform for online stores",
            "account_owner": "You",
            "tier": "Mid-Market",
        },
        {
            "name": "Atlassian",
            "domain": "atlassian.com",
            "industry": "Developer Tools",
            "description": "Collaboration and productivity software",
            "account_owner": "You",
            "tier": "Enterprise",
        },
        {
            "name": "Stripe",
            "domain": "stripe.com",
            "industry": "FinTech",
            "description": "Payment processing platform",
            "account_owner": "You",
            "tier": "Enterprise",
        },
    ]

    clients = []
    for client_data in sample_clients:
        client = ClientRepository.create(session, **client_data)
        clients.append(client)
        print(f"[OK] Created client: {client.name}")

    return clients


def create_sample_events(session, clients):
    """Create sample events using MockCollector."""
    collector = MockCollector(seed=42)  # Fixed seed for reproducible data

    total_events = 0

    for client in clients:
        # Get mock news for this client
        results = collector.get_company_news(
            company_name=client.name,
            from_date=datetime.utcnow() - timedelta(days=30),
            max_results=10
        )

        for result in results:
            # Determine category from mock data
            category = result.raw_data.get("category", EventCategory.OTHER.value)

            # Generate relevance score (mock: high for important categories)
            if category in [EventCategory.FUNDING.value, EventCategory.ACQUISITION.value]:
                relevance_score = random.uniform(0.7, 1.0)
            elif category in [EventCategory.LEADERSHIP_CHANGE.value, EventCategory.PRODUCT_LAUNCH.value]:
                relevance_score = random.uniform(0.5, 0.8)
            else:
                relevance_score = random.uniform(0.3, 0.6)

            # Generate sentiment score
            sentiment_score = random.uniform(-0.3, 0.8)  # Mostly positive news

            # Create event
            event = EventRepository.create(
                session,
                client_id=client.id,
                title=result.title,
                description=result.description,
                url=result.url,
                source=result.source,
                category=category,
                relevance_score=relevance_score,
                sentiment_score=sentiment_score,
                event_date=result.published_at,
                is_read=random.choice([True, False]),  # Some already read
            )
            total_events += 1

        # Update client's last_checked_at
        ClientRepository.mark_as_checked(session, client.id)

        print(f"[OK] Created {len(results)} events for {client.name}")

    return total_events


def main():
    """Main seed function."""
    print("Seeding database with sample data...\n")

    # Initialize database
    db = Database()
    db.create_tables()

    with db.get_session() as session:
        # Check if data already exists
        existing_clients = ClientRepository.get_all(session, active_only=False)
        if existing_clients:
            print("[WARNING] Database already contains clients.")
            response = input("Do you want to continue and add more data? (y/n): ")
            if response.lower() != 'y':
                print("[CANCELLED] Seed cancelled.")
                return

        # Create sample data
        print("\nCreating sample clients...")
        clients = create_sample_clients(session)

        print(f"\nCreating sample events...")
        total_events = create_sample_events(session, clients)

    print(f"\n[SUCCESS] Seed complete!")
    print(f"   Created {len(clients)} clients")
    print(f"   Created {total_events} events")
    print(f"\nRun 'streamlit run app.py' to view the dashboard!")


if __name__ == "__main__":
    main()
