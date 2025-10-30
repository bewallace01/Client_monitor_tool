"""Mock collector for development and testing (zero-cost)."""

import random
import time
from datetime import datetime, timedelta
from typing import List, Optional
from .base import BaseCollector, CollectorResult
from src.models import EventCategory


class MockCollector(BaseCollector):
    """
    Mock collector that generates realistic fake news data.
    Perfect for development and testing without API costs.
    Simulates realistic API latency and rate limiting.
    """

    # Sample news templates for different event categories
    TEMPLATES = {
        EventCategory.FUNDING: [
            "{company} raises ${amount}M in Series {series} funding",
            "{company} secures ${amount}M investment led by {investor}",
            "{company} closes ${amount}M funding round to expand operations",
            "Venture capital firm invests ${amount}M in {company}",
        ],
        EventCategory.ACQUISITION: [
            "{company} acquires {target} for ${amount}M",
            "{company} announces acquisition of {target}",
            "{company} completes merger with {target}",
            "{acquirer} to acquire {company} in ${amount}M deal",
        ],
        EventCategory.LEADERSHIP_CHANGE: [
            "{company} appoints {name} as new CEO",
            "{name} joins {company} as Chief Technology Officer",
            "{company} announces departure of CFO {name}",
            "{company} names {name} to Board of Directors",
        ],
        EventCategory.PRODUCT_LAUNCH: [
            "{company} launches {product} to transform {industry}",
            "{company} unveils new {product} platform",
            "{company} releases {product} with AI capabilities",
            "{company} announces {product} beta program",
        ],
        EventCategory.PARTNERSHIP: [
            "{company} partners with {partner} on {initiative}",
            "{company} and {partner} announce strategic partnership",
            "{company} collaborates with {partner} to deliver {solution}",
            "{partner} selects {company} as technology partner",
        ],
        EventCategory.FINANCIAL_RESULTS: [
            "{company} reports {direction} Q{quarter} revenue of ${amount}M",
            "{company} exceeds earnings expectations in Q{quarter}",
            "{company} announces {direction} quarterly results",
            "{company} revenue grows {percent}% year-over-year",
        ],
        EventCategory.AWARD: [
            "{company} named best {category} by {organization}",
            "{company} wins {award} for innovation",
            "{organization} recognizes {company} for {achievement}",
            "{company} receives industry award for {category}",
        ],
        EventCategory.REGULATORY: [
            "{company} receives regulatory approval for {product}",
            "{company} files for regulatory compliance in {location}",
            "Regulators approve {company}'s {initiative}",
            "{company} faces regulatory review for {issue}",
            "{company} complies with new {regulation} regulations",
        ],
        EventCategory.OTHER: [
            "{company} makes announcement about {topic}",
            "{company} updates on {initiative}",
            "Latest news from {company} regarding {topic}",
            "{company} shares update on business operations",
        ],
    }

    SOURCES = [
        "TechCrunch", "Reuters", "Bloomberg", "The Wall Street Journal",
        "Business Wire", "VentureBeat", "Forbes", "CNBC", "Financial Times",
        "The Information"
    ]

    INVESTORS = ["Sequoia Capital", "Andreessen Horowitz", "Accel", "Benchmark", "Tiger Global"]
    NAMES = ["Sarah Chen", "Michael Rodriguez", "Emily Thompson", "David Kim", "Jessica Martinez", "Robert Taylor"]
    PRODUCTS = ["AI Platform", "Cloud Solution", "Analytics Suite", "Mobile App", "Data Platform"]
    PARTNERS = ["Microsoft", "Google Cloud", "AWS", "Salesforce", "SAP"]
    ORGANIZATIONS = ["Gartner", "Forrester", "IDC", "G2"]

    def __init__(self, seed: int = None):
        """
        Initialize mock collector.

        Args:
            seed: Random seed for reproducible results
        """
        if seed is not None:
            random.seed(seed)

        # Rate limiting tracking
        self._requests_made = 0
        self._request_limit = 100
        self._reset_time = datetime.utcnow() + timedelta(hours=1)

    @property
    def collector_name(self) -> str:
        return "mock"

    @property
    def is_mock(self) -> bool:
        return True

    def get_rate_limit_status(self) -> dict:
        """
        Get current rate limit status for this collector.

        Returns:
            Dictionary with rate limit information
        """
        return {
            "limit": self._request_limit,
            "remaining": self._request_limit - self._requests_made,
            "reset_at": self._reset_time,
            "enabled": True,
        }

    def _simulate_latency(self):
        """Simulate realistic API latency (0.3-0.8 seconds)."""
        delay = random.uniform(0.3, 0.8)
        time.sleep(delay)

    def _increment_request_count(self):
        """Track API request count for rate limiting."""
        self._requests_made += 1
        if self._requests_made >= self._request_limit:
            self._requests_made = 0
            self._reset_time = datetime.utcnow() + timedelta(hours=1)

    def _determine_categories_from_query(self, query: str) -> List[EventCategory]:
        """Determine which event categories to prioritize based on query keywords."""
        query_lower = query.lower()
        categories = []

        # Check for keywords and map to categories
        if any(word in query_lower for word in ["funding", "investment", "raised", "series", "venture"]):
            categories.append(EventCategory.FUNDING)

        if any(word in query_lower for word in ["acquisition", "acquires", "acquired", "merger", "buy", "buyout"]):
            categories.append(EventCategory.ACQUISITION)

        if any(word in query_lower for word in ["ceo", "cto", "cfo", "leadership", "executive", "appoint", "hire"]):
            categories.append(EventCategory.LEADERSHIP_CHANGE)

        if any(word in query_lower for word in ["product", "launch", "release", "unveil", "feature"]):
            categories.append(EventCategory.PRODUCT_LAUNCH)

        if any(word in query_lower for word in ["partnership", "partner", "collaboration", "alliance"]):
            categories.append(EventCategory.PARTNERSHIP)

        if any(word in query_lower for word in ["earnings", "revenue", "profit", "financial", "quarterly"]):
            categories.append(EventCategory.FINANCIAL_RESULTS)

        if any(word in query_lower for word in ["award", "recognition", "winner", "best"]):
            categories.append(EventCategory.AWARD)

        # If no specific keywords, include all categories
        if not categories:
            categories = list(EventCategory)

        return categories

    def search(
        self,
        query: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        max_results: int = 20,
    ) -> List[CollectorResult]:
        """Generate mock search results with keyword-based relevance."""
        # Simulate realistic API latency
        self._simulate_latency()
        self._increment_request_count()

        # Determine relevant categories from query
        relevant_categories = self._determine_categories_from_query(query)

        return self._generate_results(query, from_date, to_date, max_results, relevant_categories)

    def get_company_news(
        self,
        company_name: str,
        from_date: Optional[datetime] = None,
        max_results: int = 20,
    ) -> List[CollectorResult]:
        """Generate mock company news."""
        # Simulate realistic API latency
        self._simulate_latency()
        self._increment_request_count()

        return self._generate_results(company_name, from_date, max_results=max_results)

    def _generate_results(
        self,
        company_name: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        max_results: int = 20,
        preferred_categories: Optional[List[EventCategory]] = None,
    ) -> List[CollectorResult]:
        """Generate mock results for a company."""
        if to_date is None:
            to_date = datetime.utcnow()
        if from_date is None:
            from_date = to_date - timedelta(days=30)

        # Generate 5-10 random events
        num_results = random.randint(5, min(10, max_results))
        results = []

        # If preferred categories are provided, use them more often (70% of the time)
        available_categories = list(self.TEMPLATES.keys())

        for _ in range(num_results):
            # Choose category based on preferences
            if preferred_categories and random.random() < 0.7:
                category = random.choice(preferred_categories)
            else:
                category = random.choice(available_categories)

            template = random.choice(self.TEMPLATES[category])

            # Fill in template variables
            title = template.format(
                company=company_name,
                amount=random.randint(5, 500),
                series=random.choice(['A', 'B', 'C', 'D']),
                investor=random.choice(self.INVESTORS),
                target=f"{random.choice(['Tech', 'Data', 'Cloud', 'AI'])}Corp",
                acquirer=random.choice(['Global Tech Inc', 'Enterprise Solutions']),
                name=random.choice(self.NAMES),
                product=random.choice(self.PRODUCTS),
                partner=random.choice(self.PARTNERS),
                industry=random.choice(['enterprise software', 'healthcare', 'finance']),
                initiative=random.choice(['digital transformation', 'cloud migration']),
                solution=random.choice(['innovative solutions', 'next-gen technology']),
                direction=random.choice(['strong', 'record']),
                quarter=random.randint(1, 4),
                percent=random.randint(15, 95),
                category=random.choice(['Workplace Software', 'Innovation']),
                organization=random.choice(self.ORGANIZATIONS),
                award=random.choice(['Innovation Award', 'Excellence Award']),
                achievement=random.choice(['customer success', 'product innovation']),
                # New variables for REGULATORY and OTHER
                location=random.choice(['North America', 'Europe', 'Asia Pacific']),
                issue=random.choice(['data privacy', 'security compliance', 'antitrust']),
                regulation=random.choice(['GDPR', 'CCPA', 'SOC 2', 'ISO 27001']),
                topic=random.choice(['operations', 'strategy', 'expansion', 'innovation']),
            )

            # Generate realistic description
            description = self._generate_description(company_name, category, title)

            # Random date within range
            days_diff = (to_date - from_date).days
            random_days = random.randint(0, max(1, days_diff))
            published_at = from_date + timedelta(days=random_days)

            results.append(CollectorResult(
                title=title,
                description=description,
                url=f"https://news.example.com/article/{random.randint(1000, 9999)}",
                source=random.choice(self.SOURCES),
                published_at=published_at,
                raw_data={"category": category.value, "mock": True}
            ))

        # Sort by date descending
        results.sort(key=lambda x: x.published_at, reverse=True)
        return results

    def _generate_description(self, company_name: str, category: EventCategory, title: str) -> str:
        """Generate a realistic description based on category."""
        descriptions = {
            EventCategory.FUNDING: f"{company_name} announced today that it has secured significant funding to accelerate growth and expand its market presence. The investment will be used to enhance product development and scale operations.",
            EventCategory.ACQUISITION: f"In a move to strengthen its market position, {company_name} has completed a strategic acquisition. The deal is expected to create synergies and expand the company's capabilities.",
            EventCategory.LEADERSHIP_CHANGE: f"{company_name} today announced a key leadership appointment as part of its continued growth strategy. The new executive brings extensive industry experience and will drive strategic initiatives.",
            EventCategory.PRODUCT_LAUNCH: f"{company_name} unveiled its latest innovation, designed to address evolving customer needs. The new offering leverages cutting-edge technology and is now available to customers.",
            EventCategory.PARTNERSHIP: f"{company_name} has entered into a strategic partnership to deliver enhanced value to customers. The collaboration combines complementary strengths and expertise.",
            EventCategory.FINANCIAL_RESULTS: f"{company_name} reported its latest quarterly financial results, demonstrating continued business momentum. The company cited strong customer demand and operational execution.",
            EventCategory.AWARD: f"{company_name} has been recognized for its excellence and innovation in the industry. The award reflects the company's commitment to delivering exceptional value.",
            EventCategory.REGULATORY: f"{company_name} is navigating regulatory requirements and compliance matters. The company is working closely with authorities to ensure full adherence to applicable regulations.",
            EventCategory.OTHER: f"{company_name} made an announcement today regarding company operations and strategic initiatives. Further details are available through official company channels.",
        }
        return descriptions.get(category, f"Latest news about {company_name}. {title}")
