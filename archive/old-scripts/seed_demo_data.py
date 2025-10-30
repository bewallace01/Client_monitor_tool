#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed realistic demo data for Client Intelligence Monitor.

Creates:
- 15-20 sample clients across various industries
- 50-100 sample events distributed over the last 30 days
- Realistic event types, relevance scores, and metadata
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random
import uuid

# Set UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage import SQLiteStorage
from src.models.client_dto import ClientDTO
from src.models.event_dto import EventDTO


# Sample company data with realistic details
SAMPLE_COMPANIES = [
    {
        "name": "Acme Corporation",
        "industry": "Technology",
        "domain": "acme.com",
        "description": "Leading enterprise software provider specializing in cloud solutions",
        "tier": "Enterprise",
        "account_owner": "Sarah Johnson",
        "keywords": ["enterprise software", "cloud computing", "SaaS"]
    },
    {
        "name": "TechVista Solutions",
        "industry": "Technology",
        "domain": "techvista.io",
        "description": "AI-powered analytics platform for business intelligence",
        "tier": "Growth",
        "account_owner": "Michael Chen",
        "keywords": ["artificial intelligence", "analytics", "business intelligence"]
    },
    {
        "name": "GlobalFinance Group",
        "industry": "Financial Services",
        "domain": "globalfinance.com",
        "description": "International financial services and investment management",
        "tier": "Enterprise",
        "account_owner": "Sarah Johnson",
        "keywords": ["fintech", "investment", "financial services"]
    },
    {
        "name": "HealthTech Innovations",
        "industry": "Healthcare",
        "domain": "healthtechinnovations.com",
        "description": "Medical device manufacturer and healthcare technology provider",
        "tier": "Mid-Market",
        "account_owner": "David Martinez",
        "keywords": ["medical devices", "healthcare", "telemedicine"]
    },
    {
        "name": "RetailMax Inc",
        "industry": "Retail",
        "domain": "retailmax.com",
        "description": "E-commerce platform and retail technology solutions",
        "tier": "Growth",
        "account_owner": "Emily Rodriguez",
        "keywords": ["e-commerce", "retail", "omnichannel"]
    },
    {
        "name": "CloudNine Infrastructure",
        "industry": "Technology",
        "domain": "cloudnine.cloud",
        "description": "Cloud infrastructure and DevOps automation platform",
        "tier": "Enterprise",
        "account_owner": "Michael Chen",
        "keywords": ["cloud infrastructure", "DevOps", "automation"]
    },
    {
        "name": "DataDrive Analytics",
        "industry": "Technology",
        "domain": "datadrive.ai",
        "description": "Big data analytics and machine learning platform",
        "tier": "Growth",
        "account_owner": "Sarah Johnson",
        "keywords": ["big data", "machine learning", "data analytics"]
    },
    {
        "name": "SecureNet Cyber",
        "industry": "Cybersecurity",
        "domain": "securenet.security",
        "description": "Enterprise cybersecurity solutions and threat intelligence",
        "tier": "Mid-Market",
        "account_owner": "David Martinez",
        "keywords": ["cybersecurity", "threat detection", "network security"]
    },
    {
        "name": "GreenEnergy Solutions",
        "industry": "Energy",
        "domain": "greenenergy.earth",
        "description": "Renewable energy technology and sustainability consulting",
        "tier": "Mid-Market",
        "account_owner": "Emily Rodriguez",
        "keywords": ["renewable energy", "sustainability", "clean tech"]
    },
    {
        "name": "EduTech Learning",
        "industry": "Education",
        "domain": "edutech.edu",
        "description": "Online learning platform and educational technology",
        "tier": "Growth",
        "account_owner": "Michael Chen",
        "keywords": ["edtech", "online learning", "education technology"]
    },
    {
        "name": "FinanceFirst Bank",
        "industry": "Financial Services",
        "domain": "financefirst.bank",
        "description": "Digital banking and financial technology services",
        "tier": "Enterprise",
        "account_owner": "Sarah Johnson",
        "keywords": ["digital banking", "fintech", "mobile banking"]
    },
    {
        "name": "MediaStream Networks",
        "industry": "Media & Entertainment",
        "domain": "mediastream.tv",
        "description": "Streaming media platform and content delivery network",
        "tier": "Growth",
        "account_owner": "David Martinez",
        "keywords": ["streaming", "media", "content delivery"]
    },
    {
        "name": "AutoTech Innovations",
        "industry": "Automotive",
        "domain": "autotech.auto",
        "description": "Automotive technology and autonomous vehicle systems",
        "tier": "Mid-Market",
        "account_owner": "Emily Rodriguez",
        "keywords": ["autonomous vehicles", "automotive", "electric vehicles"]
    },
    {
        "name": "FoodTech Ventures",
        "industry": "Food & Beverage",
        "domain": "foodtech.com",
        "description": "Food technology and restaurant management software",
        "tier": "Growth",
        "account_owner": "Michael Chen",
        "keywords": ["food tech", "restaurant technology", "delivery"]
    },
    {
        "name": "PropTech Realty",
        "industry": "Real Estate",
        "domain": "proptech.properties",
        "description": "Real estate technology and property management platform",
        "tier": "Mid-Market",
        "account_owner": "Sarah Johnson",
        "keywords": ["real estate", "property management", "prop tech"]
    },
    {
        "name": "LogisticsPro",
        "industry": "Logistics",
        "domain": "logisticspro.shipping",
        "description": "Supply chain management and logistics optimization",
        "tier": "Enterprise",
        "account_owner": "David Martinez",
        "keywords": ["logistics", "supply chain", "shipping"]
    },
    {
        "name": "TravelTech Global",
        "industry": "Travel & Hospitality",
        "domain": "traveltech.travel",
        "description": "Travel booking platform and hospitality technology",
        "tier": "Growth",
        "account_owner": "Emily Rodriguez",
        "keywords": ["travel", "hospitality", "booking platform"]
    },
    {
        "name": "InsureTech Solutions",
        "industry": "Insurance",
        "domain": "insuretech.insure",
        "description": "Insurance technology and risk management platform",
        "tier": "Mid-Market",
        "account_owner": "Michael Chen",
        "keywords": ["insurtech", "insurance", "risk management"]
    },
    {
        "name": "BioTech Pharma",
        "industry": "Biotechnology",
        "domain": "biotech-pharma.bio",
        "description": "Biotechnology research and pharmaceutical development",
        "tier": "Enterprise",
        "account_owner": "Sarah Johnson",
        "keywords": ["biotechnology", "pharmaceutical", "drug development"]
    },
    {
        "name": "SportsTech Arena",
        "industry": "Sports & Fitness",
        "domain": "sportstech.fitness",
        "description": "Sports technology and fitness tracking platform",
        "tier": "Growth",
        "account_owner": "David Martinez",
        "keywords": ["sports tech", "fitness", "wearables"]
    }
]


# Event templates organized by type
EVENT_TEMPLATES = {
    "funding": [
        {
            "title": "{company} raises ${amount}M in Series {round} funding",
            "summary": "{company} announced today it has raised ${amount} million in Series {round} funding led by {investor}. The funds will be used to {purpose}.",
            "amounts": [10, 15, 20, 25, 30, 50, 75, 100, 150],
            "rounds": ["A", "B", "C", "D"],
            "investors": ["Sequoia Capital", "Andreessen Horowitz", "Tiger Global", "Accel Partners", "Benchmark Capital"],
            "purposes": ["expand operations", "accelerate product development", "enter new markets", "scale the team", "enhance technology infrastructure"]
        },
        {
            "title": "{company} secures ${amount}M seed round",
            "summary": "{company} has successfully closed a ${amount} million seed funding round from {investor}. The startup plans to {purpose}.",
            "amounts": [2, 3, 5, 7, 10, 12],
            "rounds": ["Seed"],
            "investors": ["Y Combinator", "500 Startups", "Techstars", "First Round Capital"],
            "purposes": ["build initial product", "hire key team members", "validate market fit", "launch beta program"]
        }
    ],
    "acquisition": [
        {
            "title": "{company} acquires {target} for ${amount}M",
            "summary": "{company} today announced the acquisition of {target} for ${amount} million. The deal is expected to {benefit}.",
            "amounts": [50, 100, 200, 350, 500, 750, 1000],
            "targets": ["TechStartup", "InnovateCo", "DataSolutions", "CloudVentures", "AI Labs", "SecureApp"],
            "benefits": ["expand market presence", "enhance product capabilities", "accelerate growth", "strengthen competitive position"]
        },
        {
            "title": "{company} to merge with {target}",
            "summary": "{company} and {target} announced plans to merge in a deal valued at ${amount} million. The combined entity will {benefit}.",
            "amounts": [200, 500, 1000, 2000],
            "targets": ["CompetitorCo", "MarketLeader", "IndustryPlayer", "TechGiant"],
            "benefits": ["create market leader", "unlock synergies", "expand global reach", "drive innovation"]
        }
    ],
    "leadership": [
        {
            "title": "{company} appoints {name} as new {role}",
            "summary": "{company} today announced the appointment of {name} as {role}. {name} brings {experience} years of experience from {previous}.",
            "names": ["John Smith", "Sarah Williams", "Michael Brown", "Jennifer Davis", "Robert Johnson", "Emily Chen"],
            "roles": ["CEO", "CTO", "CFO", "COO", "VP of Engineering", "Chief Product Officer"],
            "experience": [15, 20, 25, 30],
            "previous": ["Google", "Amazon", "Microsoft", "Apple", "Facebook", "Tesla", "Netflix"]
        },
        {
            "title": "{company} {role} {name} steps down",
            "summary": "{company} announced that {role} {name} will be stepping down after {years} years with the company. A search for a replacement is underway.",
            "names": ["David Miller", "Lisa Anderson", "James Wilson", "Maria Garcia", "Thomas Moore"],
            "roles": ["CEO", "President", "CFO", "CTO"],
            "years": [5, 7, 10, 12, 15]
        }
    ],
    "product": [
        {
            "title": "{company} launches {product}",
            "summary": "{company} today unveiled {product}, a revolutionary {category} solution. The product features {feature} and is designed to {benefit}.",
            "products": ["AI Platform", "Cloud Solution", "Mobile App", "Analytics Dashboard", "Security Suite", "Developer Tools"],
            "categories": ["enterprise", "consumer", "developer", "business intelligence", "cybersecurity"],
            "features": ["advanced AI capabilities", "real-time analytics", "seamless integration", "enhanced security"],
            "benefits": ["improve efficiency", "reduce costs", "enhance productivity", "streamline operations"]
        },
        {
            "title": "{company} releases version {version} with major updates",
            "summary": "{company} announced the release of version {version}, featuring {feature}. The update includes {improvement}.",
            "versions": ["2.0", "3.0", "4.0", "5.0"],
            "features": ["redesigned interface", "new AI features", "enhanced performance", "improved security"],
            "improvements": ["faster processing", "better user experience", "additional integrations", "mobile optimization"]
        }
    ],
    "partnership": [
        {
            "title": "{company} partners with {partner} to {goal}",
            "summary": "{company} and {partner} today announced a strategic partnership to {goal}. The collaboration will {benefit}.",
            "partners": ["Microsoft", "AWS", "Google Cloud", "Salesforce", "Oracle", "IBM", "SAP"],
            "goals": ["expand market reach", "develop new solutions", "enhance capabilities", "serve enterprise customers"],
            "benefits": ["deliver better value", "accelerate innovation", "improve customer experience", "create new opportunities"]
        }
    ],
    "financial": [
        {
            "title": "{company} reports {direction} Q{quarter} earnings",
            "summary": "{company} today reported {direction} earnings for Q{quarter}, with revenue of ${revenue}M. The company {performance}.",
            "directions": ["strong", "record", "improved"],
            "quarters": [1, 2, 3, 4],
            "revenues": [50, 75, 100, 150, 200, 250, 300, 500],
            "performances": ["exceeded analyst expectations", "showed solid growth", "demonstrated strong momentum", "delivered robust results"]
        }
    ],
    "award": [
        {
            "title": "{company} named {award}",
            "summary": "{company} has been recognized as {award} by {organization}. The award highlights {achievement}.",
            "awards": ["Leader in the Gartner Magic Quadrant", "Top Workplace", "Best Place to Work", "Innovation Leader", "Fastest Growing Company"],
            "organizations": ["Gartner", "Forbes", "Fortune", "Inc. Magazine", "Deloitte"],
            "achievements": ["industry leadership", "innovation excellence", "workplace culture", "rapid growth", "customer satisfaction"]
        }
    ],
    "regulatory": [
        {
            "title": "{company} achieves {certification} certification",
            "summary": "{company} announced it has achieved {certification} certification, demonstrating commitment to {area}.",
            "certifications": ["ISO 27001", "SOC 2 Type II", "GDPR compliance", "HIPAA compliance"],
            "areas": ["data security", "privacy protection", "compliance standards", "information security"]
        }
    ]
}


def generate_event_from_template(company: ClientDTO, event_type: str, days_ago: int) -> EventDTO:
    """Generate a realistic event from templates."""
    templates = EVENT_TEMPLATES.get(event_type, [])
    if not templates:
        return None

    template = random.choice(templates)

    # Generate title and summary
    title = template["title"]
    summary = template["summary"]

    # Replace placeholders
    replacements = {"company": company.name}

    for key, values in template.items():
        if key not in ["title", "summary"] and isinstance(values, list):
            replacements[key] = random.choice(values)

    # Format strings with replacements
    for key, value in replacements.items():
        title = title.replace(f"{{{key}}}", str(value))
        summary = summary.replace(f"{{{key}}}", str(value))

    # Calculate event date
    event_date = datetime.now() - timedelta(days=days_ago)

    # Calculate relevance score based on event type and recency
    base_scores = {
        "funding": 0.85,
        "acquisition": 0.90,
        "leadership": 0.70,
        "product": 0.75,
        "partnership": 0.80,
        "financial": 0.85,
        "award": 0.60,
        "regulatory": 0.75
    }

    base_score = base_scores.get(event_type, 0.70)
    recency_boost = max(0, (30 - days_ago) / 30 * 0.15)  # Up to 0.15 boost for recent events
    relevance_score = min(0.99, base_score + recency_boost + random.uniform(-0.05, 0.05))

    # Sentiment score
    sentiment_scores = {
        "funding": 0.8,
        "acquisition": 0.7,
        "leadership": 0.5,
        "product": 0.8,
        "partnership": 0.75,
        "financial": 0.7,
        "award": 0.9,
        "regulatory": 0.6
    }
    sentiment_score = sentiment_scores.get(event_type, 0.5) + random.uniform(-0.1, 0.1)

    # Map sentiment score to sentiment label
    if sentiment_score > 0.6:
        sentiment = "positive"
    elif sentiment_score < 0.4:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    # Map status based on age
    if days_ago > 7:
        status = random.choice(["reviewed", "actioned", "archived"])
    else:
        status = "new"

    return EventDTO(
        id=str(uuid.uuid4()),
        client_id=company.id,
        event_type=event_type,
        title=title,
        summary=summary,
        source_url=f"https://news.example.com/{event_type}/{uuid.uuid4()}",
        source_name="Demo Data",
        published_date=event_date,
        discovered_date=datetime.now(),
        relevance_score=round(relevance_score, 2),
        sentiment=sentiment,
        status=status,
        tags=[event_type, company.industry or "business"]
    )


def seed_demo_data(num_clients: int = 18, num_events: int = 75):
    """
    Seed the database with realistic demo data.

    Args:
        num_clients: Number of clients to create (default 18, max 20)
        num_events: Number of events to create (default 75)
    """
    print("🌱 Seeding demo data for Client Intelligence Monitor...")
    print(f"   Creating {num_clients} clients and ~{num_events} events")
    print()

    storage = SQLiteStorage()
    storage.connect()

    # Create clients
    print("📊 Creating clients...")
    clients = []
    num_clients = min(num_clients, len(SAMPLE_COMPANIES))

    for i in range(num_clients):
        company_data = SAMPLE_COMPANIES[i]

        client = ClientDTO(
            id=f"demo_{company_data['name'].lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}",
            name=company_data["name"],
            industry=company_data["industry"],
            domain=company_data["domain"],
            description=company_data["description"],
            tier=company_data["tier"],
            account_owner=company_data["account_owner"],
            keywords=company_data["keywords"],
            is_active=True,
            priority="high" if company_data["tier"] == "Enterprise" else "medium"
        )

        storage.create_client(client)
        clients.append(client)
        print(f"   ✓ {client.name} ({client.industry})")

    print(f"\n✅ Created {len(clients)} clients")
    print()

    # Create events distributed across clients and time
    print("📰 Creating events...")

    # Event type distribution (realistic)
    event_type_weights = {
        "product": 0.25,      # 25% product launches/updates
        "partnership": 0.20,  # 20% partnerships
        "funding": 0.15,      # 15% funding news
        "leadership": 0.15,   # 15% leadership changes
        "financial": 0.10,    # 10% financial results
        "acquisition": 0.08,  # 8% acquisitions
        "award": 0.05,        # 5% awards
        "regulatory": 0.02    # 2% regulatory
    }

    event_types = list(event_type_weights.keys())
    weights = list(event_type_weights.values())

    events_created = 0
    target_events_per_client = num_events // len(clients)

    for client in clients:
        # Each client gets 3-6 events
        num_client_events = random.randint(
            max(2, target_events_per_client - 2),
            min(8, target_events_per_client + 2)
        )

        for _ in range(num_client_events):
            # Select event type based on weights
            event_type = random.choices(event_types, weights=weights)[0]

            # Distribute events over last 30 days
            days_ago = random.randint(0, 30)

            event = generate_event_from_template(client, event_type, days_ago)
            if event:
                storage.create_event(event)
                events_created += 1

                if events_created % 10 == 0:
                    print(f"   Created {events_created} events...")

    print(f"\n✅ Created {events_created} events")
    print()

    # Print summary
    stats = storage.get_statistics()
    print("=" * 60)
    print("📈 Demo Data Summary:")
    print(f"   Total Clients: {stats.get('total_clients', 0)}")
    print(f"   Active Clients: {stats.get('active_clients', 0)}")
    print(f"   Total Events: {stats.get('total_events', 0)}")
    print(f"   Unread Events: {stats.get('unread_events', 0)}")
    print("=" * 60)
    print()
    print("✨ Demo data seeding complete!")
    print()
    print("💡 Tip: Set DEMO_MODE=true in your environment to show demo banner")
    print()


def clear_demo_data():
    """Clear all demo data (clients and events with 'demo_' prefix)."""
    print("🗑️  Clearing demo data...")

    storage = SQLiteStorage()
    storage.connect()

    all_clients = storage.get_all_clients()
    deleted_count = 0

    for client in all_clients:
        if client.id.startswith('demo_'):
            storage.delete_client(client.id)
            deleted_count += 1

    print(f"✅ Deleted {deleted_count} demo clients and their events")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed demo data for Client Intelligence Monitor")
    parser.add_argument("--clients", type=int, default=18, help="Number of clients to create (max 20)")
    parser.add_argument("--events", type=int, default=75, help="Target number of events to create")
    parser.add_argument("--clear", action="store_true", help="Clear existing demo data")

    args = parser.parse_args()

    if args.clear:
        clear_demo_data()
    else:
        seed_demo_data(num_clients=args.clients, num_events=args.events)
