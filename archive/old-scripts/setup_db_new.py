"""
Database setup script for the new SQLite storage layer.
Initializes database and optionally seeds with sample data.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timedelta
import random
from src.storage import SQLiteStorage
from src.models import ClientDTO, EventDTO, SearchCacheDTO
from src.models.utils import generate_uuid


def initialize_database(storage: SQLiteStorage):
    """Initialize database schema."""
    print("Initializing database...")
    storage.initialize_database()
    print("[OK] Database schema created")


def seed_clients(storage: SQLiteStorage, count: int = 5) -> list[ClientDTO]:
    """Seed database with sample clients."""
    print(f"\nSeeding {count} sample clients...")

    sample_data = [
        {
            "name": "TechVentures Inc",
            "industry": "Enterprise SaaS",
            "priority": "high",
            "tier": "Enterprise",
            "description": "Leading provider of enterprise workflow automation solutions",
        },
        {
            "name": "DataFlow Systems",
            "industry": "Data Analytics",
            "priority": "high",
            "tier": "Enterprise",
            "description": "Real-time data analytics platform for Fortune 500 companies",
        },
        {
            "name": "CloudScale Solutions",
            "industry": "Cloud Infrastructure",
            "priority": "medium",
            "tier": "Mid-Market",
            "description": "Cloud infrastructure management and optimization platform",
        },
        {
            "name": "SecureNet Corp",
            "industry": "Cybersecurity",
            "priority": "high",
            "tier": "Enterprise",
            "description": "Enterprise cybersecurity and threat detection platform",
        },
        {
            "name": "MobileFirst Technologies",
            "industry": "Mobile Development",
            "priority": "medium",
            "tier": "Mid-Market",
            "description": "Mobile app development and deployment platform",
        },
    ]

    clients = []
    for data in sample_data[:count]:
        client = ClientDTO(
            id=generate_uuid(),
            name=data["name"],
            industry=data["industry"],
            priority=data["priority"],
            keywords=["enterprise", "cloud", "AI", "platform"],
            monitoring_since=datetime.utcnow() - timedelta(days=random.randint(30, 180)),
            last_checked=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
            metadata={
                "company_size": random.choice(["100-500", "500-1000", "1000+"]),
                "funding_stage": random.choice(["Series B", "Series C", "Series D"]),
            },
            domain=f"{data['name'].lower().replace(' ', '')}.com",
            description=data["description"],
            account_owner="Sample CS Manager",
            tier=data["tier"],
            is_active=True,
        )

        storage.create_client(client)
        clients.append(client)
        print(f"  [OK] Created client: {client.name}")

    return clients


def seed_events(storage: SQLiteStorage, clients: list[ClientDTO], events_per_client: int = 3):
    """Seed database with sample events."""
    total_events = len(clients) * events_per_client
    print(f"\nSeeding {total_events} sample events...")

    event_templates = [
        {
            "type": "funding",
            "titles": [
                "{company} raises ${amount}M in Series {series} funding round",
                "{company} secures ${amount}M to expand global operations",
                "Investment round nets {company} ${amount}M for product development",
            ],
            "summary": "{company} announced today that it has secured ${amount}M in funding. The investment will be used to accelerate product development, expand into new markets, and scale the engineering team.",
        },
        {
            "type": "product",
            "titles": [
                "{company} launches new {product} platform with AI capabilities",
                "{company} unveils {product} to revolutionize {industry}",
                "{company} releases {product} beta to select customers",
            ],
            "summary": "{company} has launched {product}, a new platform designed to transform how enterprises operate. The solution leverages cutting-edge technology and is now available to customers.",
        },
        {
            "type": "partnership",
            "titles": [
                "{company} partners with {partner} on strategic initiative",
                "{company} and {partner} announce collaboration",
                "{company} teams up with {partner} to deliver innovation",
            ],
            "summary": "{company} has entered into a strategic partnership with {partner}. The collaboration will combine complementary strengths to deliver enhanced value to customers across multiple industries.",
        },
        {
            "type": "leadership",
            "titles": [
                "{company} appoints {person} as new {role}",
                "{person} joins {company} as {role}",
                "{company} announces {role} transition with {person}",
            ],
            "summary": "{company} announced today that {person} has joined the company as {role}. The appointment reflects the company's continued growth and commitment to expanding its leadership team.",
        },
        {
            "type": "acquisition",
            "titles": [
                "{company} acquires {target} for ${amount}M",
                "{company} completes acquisition of {target}",
                "{company} expands portfolio with {target} acquisition",
            ],
            "summary": "{company} has completed the acquisition of {target} for ${amount}M. The deal strengthens the company's position in the market and expands its technology capabilities.",
        },
    ]

    partners = ["Microsoft", "Google Cloud", "AWS", "Salesforce", "Oracle"]
    people = ["Sarah Chen", "Michael Rodriguez", "Emily Thompson", "David Kim"]
    roles = ["Chief Technology Officer", "VP of Engineering", "Chief Product Officer"]
    products = ["AI Platform", "Analytics Suite", "Cloud Solution", "Mobile App"]

    event_count = 0
    for client in clients:
        for _ in range(events_per_client):
            template = random.choice(event_templates)
            title_template = random.choice(template["titles"])

            # Generate title
            title = title_template.format(
                company=client.name,
                amount=random.randint(10, 150),
                series=random.choice(["B", "C", "D"]),
                product=random.choice(products),
                industry=client.industry,
                partner=random.choice(partners),
                person=random.choice(people),
                role=random.choice(roles),
                target=random.choice(["TechStart", "DataCo", "CloudTech"]),
            )

            # Generate summary
            summary = template["summary"].format(
                company=client.name,
                amount=random.randint(10, 150),
                product=random.choice(products),
                partner=random.choice(partners),
                person=random.choice(people),
                role=random.choice(roles),
                target=random.choice(["TechStart", "DataCo", "CloudTech"]),
            )

            # Generate event
            days_ago = random.randint(1, 30)
            event = EventDTO(
                id=generate_uuid(),
                client_id=client.id,
                event_type=template["type"],
                title=title,
                summary=summary,
                source_url=f"https://techcrunch.com/article/{generate_uuid()[:8]}",
                source_name=random.choice(["TechCrunch", "Reuters", "Bloomberg", "The Information"]),
                published_date=datetime.utcnow() - timedelta(days=days_ago),
                discovered_date=datetime.utcnow() - timedelta(days=days_ago, hours=-2),
                relevance_score=random.uniform(0.4, 1.0),
                sentiment="positive" if random.random() > 0.3 else "neutral",
                sentiment_score=random.uniform(0.2, 0.9),
                status=random.choice(["new", "new", "new", "reviewed"]),  # Most are new
                tags=random.sample(["AI", "cloud", "enterprise", "innovation", "growth"], k=2),
                user_notes=None,
                metadata={"word_count": random.randint(300, 800)},
            )

            storage.create_event(event)
            event_count += 1

    print(f"  [OK] Created {event_count} events")


def seed_cache(storage: SQLiteStorage, count: int = 3):
    """Seed database with sample cache entries."""
    print(f"\nSeeding {count} sample cache entries...")

    queries = [
        "TechVentures funding",
        "DataFlow product launch",
        "CloudScale partnership",
    ]

    for i, query in enumerate(queries[:count]):
        cache = SearchCacheDTO.create_sample(
            query=query,
            api_source="mock",
            ttl_hours=24
        )
        storage.create_cache(cache)
        print(f"  [OK] Created cache entry: {query}")


def print_summary(storage: SQLiteStorage):
    """Print database summary."""
    print("\n" + "=" * 60)
    print("DATABASE SETUP COMPLETE")
    print("=" * 60)

    stats = storage.get_statistics()
    db_info = storage.get_database_info()

    print(f"\nDatabase: {db_info['path']}")
    print(f"Size: {db_info['size_mb']} MB")
    print(f"Tables: {', '.join(db_info['tables'])}")

    print(f"\nRecords:")
    print(f"  - Active Clients: {stats['active_clients']}")
    print(f"  - Total Events: {stats['total_events']}")
    print(f"  - New Events: {stats['new_events']}")
    print(f"  - Cache Entries: {stats['total_cache_entries']}")

    print(f"\n[SUCCESS] Database is ready to use!")
    print(f"\nNext steps:")
    print(f"  1. View database: Navigate to 'Database' page in the dashboard")
    print(f"  2. Test storage: python scripts/test_db.py")
    print(f"  3. Use in app: The storage layer is ready for integration")


def main():
    """Main setup function."""
    print("Client Intelligence Monitor - Database Setup")
    print("=" * 60)

    # Create storage instance
    storage = SQLiteStorage()
    storage.connect()

    try:
        # Check if database already exists
        db_info = storage.get_database_info()
        if db_info["exists"] and db_info["tables"]:
            print(f"\n[WARNING] Database already exists: {db_info['path']}")
            response = input("Do you want to reset the database? (y/n): ")
            if response.lower() == 'y':
                print("\n[WARNING] Dropping all tables...")
                storage.drop_all_tables()
                print("[OK] Tables dropped")
            else:
                print("[CANCELLED] Setup cancelled")
                return

        # Initialize database
        initialize_database(storage)

        # Ask about seeding
        response = input("\nDo you want to seed with sample data? (y/n): ")
        if response.lower() == 'y':
            # Seed clients
            clients = seed_clients(storage, count=5)

            # Seed events
            seed_events(storage, clients, events_per_client=3)

            # Seed cache
            seed_cache(storage, count=3)

        # Print summary
        print_summary(storage)

    finally:
        storage.disconnect()


if __name__ == "__main__":
    main()
