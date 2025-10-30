"""Mock API service for testing and fallback when real APIs aren't configured.

This service provides realistic-looking fake data for:
- Search results (Google/Serper)
- News articles (NewsAPI)
- CRM data (Salesforce/HubSpot)
- AI classification and insights

Used primarily by system admins for testing and as graceful fallback.
"""

import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID


class MockAPIService:
    """Mock API responses for system admin testing and missing APIs."""

    # Sample data pools
    TECH_KEYWORDS = [
        "artificial intelligence", "machine learning", "cloud computing",
        "cybersecurity", "blockchain", "digital transformation",
        "automation", "data analytics", "API integration", "SaaS platform"
    ]

    NEWS_SOURCES = [
        "TechCrunch", "Reuters", "Bloomberg", "The Wall Street Journal",
        "Forbes", "Business Insider", "VentureBeat", "Wired"
    ]

    EVENT_CATEGORIES = [
        "funding", "acquisition", "leadership_change", "product_launch",
        "partnership", "financial_results", "award", "expansion"
    ]

    FUNDING_ROUNDS = ["Seed", "Series A", "Series B", "Series C", "Series D"]

    EXECUTIVE_TITLES = [
        "CEO", "CTO", "CFO", "COO", "CMO", "VP of Engineering",
        "VP of Sales", "Chief Data Officer", "Head of Product"
    ]

    SAMPLE_NAMES = [
        "Jennifer Martinez", "Michael Chen", "Sarah Johnson", "David Kim",
        "Emily Rodriguez", "James Anderson", "Lisa Thompson", "Robert Lee",
        "Maria Garcia", "William Brown"
    ]

    @staticmethod
    def mock_search_results(
        client_name: str,
        keywords: List[str] = None,
        num_results: int = 10
    ) -> Dict[str, Any]:
        """
        Generate fake Google Search-like results.

        Args:
            client_name: Name of the client being searched
            keywords: Optional search keywords
            num_results: Number of results to generate

        Returns:
            Dict with search results in Google Custom Search API format
        """
        if keywords is None:
            keywords = [random.choice(MockAPIService.TECH_KEYWORDS)]

        results = []
        base_date = datetime.utcnow()

        for i in range(num_results):
            # Create realistic URLs
            domain = client_name.lower().replace(" ", "").replace(",", "")[:15]
            url_paths = ["press", "news", "blog", "media", "announcements"]
            url = f"https://www.{domain}.com/{random.choice(url_paths)}/article-{random.randint(100, 999)}"

            # Generate realistic snippets based on random event type
            event_type = random.choice(MockAPIService.EVENT_CATEGORIES)
            snippet = MockAPIService._generate_snippet(client_name, event_type)

            # Random date within last 30 days
            days_ago = random.randint(1, 30)
            published_date = base_date - timedelta(days=days_ago)

            result = {
                "kind": "customsearch#result",
                "title": MockAPIService._generate_title(client_name, event_type),
                "htmlTitle": MockAPIService._generate_title(client_name, event_type),
                "link": url,
                "displayLink": f"{domain}.com",
                "snippet": snippet,
                "htmlSnippet": snippet,
                "formattedUrl": url,
                "htmlFormattedUrl": url,
                "pagemap": {
                    "metatags": [{
                        "og:type": "article",
                        "article:published_time": published_date.isoformat()
                    }]
                }
            }
            results.append(result)

        return {
            "kind": "customsearch#search",
            "url": {
                "type": "application/json",
                "template": "https://www.googleapis.com/customsearch/v1"
            },
            "queries": {
                "request": [{
                    "title": "Google Custom Search - " + client_name,
                    "totalResults": str(num_results * 10),
                    "searchTerms": client_name + " " + " ".join(keywords),
                    "count": num_results,
                    "startIndex": 1
                }]
            },
            "searchInformation": {
                "searchTime": round(random.uniform(0.1, 0.5), 2),
                "formattedSearchTime": "0.25",
                "totalResults": str(num_results * 10)
            },
            "items": results
        }

    @staticmethod
    def _generate_title(client_name: str, event_type: str) -> str:
        """Generate realistic article title based on event type."""
        titles = {
            "funding": [
                f"{client_name} Raises ${random.randint(5, 100)}M in {random.choice(MockAPIService.FUNDING_ROUNDS)} Funding",
                f"{client_name} Secures Major Investment to Accelerate Growth",
                f"Venture Capital Firm Invests in {client_name}"
            ],
            "acquisition": [
                f"{client_name} Acquires Tech Startup to Expand Platform",
                f"Breaking: {client_name} Announces Strategic Acquisition",
                f"{client_name} Completes Acquisition of Industry Leader"
            ],
            "leadership_change": [
                f"{client_name} Appoints New {random.choice(MockAPIService.EXECUTIVE_TITLES)}",
                f"{random.choice(MockAPIService.SAMPLE_NAMES)} Joins {client_name} as {random.choice(MockAPIService.EXECUTIVE_TITLES)}",
                f"Leadership Update: {client_name} Announces Executive Transition"
            ],
            "product_launch": [
                f"{client_name} Launches Innovative New Platform",
                f"{client_name} Unveils Next-Generation Solution",
                f"New Product Release: {client_name} Enters New Market"
            ],
            "partnership": [
                f"{client_name} Partners with Global Enterprise",
                f"{client_name} and Industry Leader Announce Strategic Partnership",
                f"Collaboration: {client_name} Teams Up for Innovation"
            ],
            "financial_results": [
                f"{client_name} Reports Strong Q{random.randint(1, 4)} Results",
                f"{client_name} Revenue Grows {random.randint(20, 200)}% Year-Over-Year",
                f"{client_name} Achieves Profitability Milestone"
            ],
            "award": [
                f"{client_name} Named Best in Industry by Leading Publication",
                f"{client_name} Wins Innovation Award",
                f"Recognition: {client_name} Ranked Top Solution Provider"
            ],
            "expansion": [
                f"{client_name} Opens New Office in Major City",
                f"{client_name} Expands to International Markets",
                f"{client_name} Announces Hiring Surge to Support Growth"
            ]
        }

        return random.choice(titles.get(event_type, [f"{client_name} Company News Update"]))

    @staticmethod
    def _generate_snippet(client_name: str, event_type: str) -> str:
        """Generate realistic article snippet based on event type."""
        snippets = {
            "funding": f"{client_name} today announced it has raised a significant funding round led by prominent venture capital firms. The company plans to use the funds to accelerate product development and expand its market presence...",
            "acquisition": f"{client_name} has completed the acquisition of a complementary technology company, strengthening its position in the market. The acquisition will enable {client_name} to offer enhanced capabilities to its customers...",
            "leadership_change": f"{client_name} announced today that {random.choice(MockAPIService.SAMPLE_NAMES)} will join the company as {random.choice(MockAPIService.EXECUTIVE_TITLES)}. With over 20 years of experience, the new executive brings deep industry expertise...",
            "product_launch": f"{client_name} unveiled its latest product offering, designed to address key market challenges. The new solution incorporates advanced {random.choice(MockAPIService.TECH_KEYWORDS)} capabilities...",
            "partnership": f"{client_name} today announced a strategic partnership aimed at delivering innovative solutions to customers. The collaboration combines {client_name}'s expertise with its partner's market reach...",
            "financial_results": f"{client_name} reported strong financial results, with revenue growth exceeding expectations. The company attributed its success to strong customer demand and successful product adoption...",
            "award": f"{client_name} has been recognized as a leader in its industry, receiving a prestigious award for innovation and customer satisfaction. The recognition highlights the company's commitment to excellence...",
            "expansion": f"{client_name} announced plans to expand its operations, including new office locations and significant headcount growth. The expansion reflects strong market demand for the company's solutions..."
        }

        return snippets.get(event_type, f"{client_name} continues to make strides in the industry with recent developments and strategic initiatives aimed at driving growth and innovation...")

    @staticmethod
    def mock_news_results(
        client_name: str,
        num_articles: int = 10
    ) -> Dict[str, Any]:
        """
        Generate fake NewsAPI-like results.

        Args:
            client_name: Name of the client being searched
            num_articles: Number of articles to generate

        Returns:
            Dict with news articles in NewsAPI format
        """
        articles = []
        base_date = datetime.utcnow()

        for i in range(num_articles):
            event_type = random.choice(MockAPIService.EVENT_CATEGORIES)
            days_ago = random.randint(1, 30)
            published_date = base_date - timedelta(days=days_ago)

            article = {
                "source": {
                    "id": None,
                    "name": random.choice(MockAPIService.NEWS_SOURCES)
                },
                "author": random.choice(MockAPIService.SAMPLE_NAMES),
                "title": MockAPIService._generate_title(client_name, event_type),
                "description": MockAPIService._generate_snippet(client_name, event_type),
                "url": f"https://news.example.com/article/{random.randint(1000, 9999)}",
                "urlToImage": f"https://via.placeholder.com/400x200?text={client_name.replace(' ', '+')}",
                "publishedAt": published_date.isoformat() + "Z",
                "content": MockAPIService._generate_snippet(client_name, event_type) + " [+1000 chars]"
            }
            articles.append(article)

        return {
            "status": "ok",
            "totalResults": num_articles * 3,
            "articles": articles
        }

    @staticmethod
    def mock_crm_data(client_id: UUID, client_name: str) -> Dict[str, Any]:
        """
        Generate fake CRM enrichment data (Salesforce/HubSpot style).

        Args:
            client_id: UUID of the client
            client_name: Name of the client

        Returns:
            Dict with standardized CRM data
        """
        # Generate consistent but random data based on client_id
        seed = int(str(client_id).replace("-", "")[:8], 16)
        random.seed(seed)

        health_score = round(random.uniform(30, 95), 1)
        arr = random.choice([50000, 100000, 250000, 500000, 1000000, 2500000, 5000000])
        employees = random.choice([50, 100, 250, 500, 1000, 2500, 5000, 10000])

        # Generate contacts
        num_contacts = random.randint(2, 5)
        contacts = []
        for i in range(num_contacts):
            contacts.append({
                "name": random.choice(MockAPIService.SAMPLE_NAMES),
                "title": random.choice(MockAPIService.EXECUTIVE_TITLES),
                "email": f"{random.choice(MockAPIService.SAMPLE_NAMES).lower().replace(' ', '.')}@{client_name.lower().replace(' ', '')}.com",
                "phone": f"+1 ({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
                "is_primary": i == 0
            })

        # Last interaction
        days_since_interaction = random.randint(1, 60)
        last_interaction = datetime.utcnow() - timedelta(days=days_since_interaction)

        crm_data = {
            "account_id": f"SF-{random.randint(10000, 99999)}",
            "account_name": client_name,
            "health_score": health_score,
            "health_status": "Healthy" if health_score >= 70 else "At Risk" if health_score >= 50 else "Critical",
            "annual_revenue": arr,
            "annual_revenue_formatted": f"${arr:,}",
            "employee_count": employees,
            "industry": random.choice(["Technology", "Financial Services", "Healthcare", "Retail", "Manufacturing"]),
            "account_owner": {
                "name": random.choice(MockAPIService.SAMPLE_NAMES),
                "email": "csm@yourcompany.com"
            },
            "contacts": contacts,
            "last_interaction": {
                "date": last_interaction.isoformat(),
                "type": random.choice(["Email", "Phone Call", "Meeting", "Support Ticket"]),
                "summary": f"Discussed {random.choice(['product roadmap', 'contract renewal', 'feature request', 'support issue', 'expansion opportunity'])}"
            },
            "open_opportunities": random.randint(0, 3),
            "open_cases": random.randint(0, 5),
            "contract_end_date": (datetime.utcnow() + timedelta(days=random.randint(30, 730))).isoformat(),
            "lifecycle_stage": random.choice(["Customer", "Expansion", "Renewal", "At Risk"]),
            "products_purchased": random.sample([
                "Enterprise Plan", "Professional Services", "Premium Support",
                "API Access", "Advanced Analytics", "Custom Integration"
            ], k=random.randint(1, 3)),
            "nps_score": random.randint(6, 10),
            "churn_risk": round(random.uniform(0.05, 0.30), 2) if health_score < 70 else round(random.uniform(0.01, 0.10), 2)
        }

        # Reset random seed
        random.seed()

        return crm_data

    @staticmethod
    def mock_ai_classification(raw_data: Dict[str, Any], client_name: str) -> Dict[str, Any]:
        """
        Generate fake AI event classification using rule-based logic.

        Args:
            raw_data: Raw data from search/news API
            client_name: Name of the client

        Returns:
            Dict with event classification data
        """
        # Extract title and content from raw data
        # Check for normalized format FIRST (this is what's actually being passed)
        if "title" in raw_data and "items" not in raw_data and "articles" not in raw_data:
            # Normalized format (from extract_results_for_storage)
            title = raw_data.get("title", f"{client_name} Update")
            description = raw_data.get("description", "") or raw_data.get("content", "")
        elif "items" in raw_data:  # Google Search format (raw)
            title = raw_data["items"][0].get("title", f"{client_name} Update") if raw_data.get("items") else f"{client_name} Update"
            description = raw_data["items"][0].get("snippet", "") if raw_data.get("items") else ""
        elif "articles" in raw_data:  # NewsAPI format (raw)
            title = raw_data["articles"][0].get("title", f"{client_name} Update") if raw_data.get("articles") else f"{client_name} Update"
            description = raw_data["articles"][0].get("description", "") if raw_data.get("articles") else ""
        else:
            title = f"{client_name} Company Update"
            description = "Recent company developments and news."

        # Rule-based category detection
        title_lower = title.lower()
        description_lower = description.lower()

        category = "other"
        relevance_score = 0.5
        sentiment_score = 0.0

        # Category detection
        if any(word in title_lower for word in ["raises", "funding", "investment", "capital"]):
            category = "funding"
            relevance_score = 0.9
            sentiment_score = 0.7
        elif any(word in title_lower for word in ["acquires", "acquisition", "merger"]):
            category = "acquisition"
            relevance_score = 0.85
            sentiment_score = 0.6
        elif any(word in title_lower for word in ["ceo", "cto", "appoints", "joins", "leadership"]):
            category = "leadership_change"
            relevance_score = 0.75
            sentiment_score = 0.5
        elif any(word in title_lower for word in ["launch", "unveils", "releases", "introduces"]):
            category = "product_launch"
            relevance_score = 0.8
            sentiment_score = 0.6
        elif any(word in title_lower for word in ["partner", "collaboration", "alliance"]):
            category = "partnership"
            relevance_score = 0.7
            sentiment_score = 0.5
        elif any(word in title_lower for word in ["revenue", "earnings", "results", "financial"]):
            category = "financial_results"
            relevance_score = 0.75
            sentiment_score = 0.4
        elif any(word in title_lower for word in ["award", "wins", "recognition", "ranked"]):
            category = "award"
            relevance_score = 0.65
            sentiment_score = 0.8

        # Sentiment adjustments
        if any(word in description_lower for word in ["strong", "growth", "success", "innovative", "leading"]):
            sentiment_score += 0.2
        if any(word in description_lower for word in ["challenge", "decline", "loss", "issue"]):
            sentiment_score -= 0.3

        # Clamp values
        relevance_score = max(0.1, min(1.0, relevance_score + random.uniform(-0.05, 0.05)))
        sentiment_score = max(-1.0, min(1.0, sentiment_score + random.uniform(-0.1, 0.1)))
        confidence_score = round(random.uniform(0.7, 0.95), 2)

        return {
            "title": title[:500],
            "description": description[:2000] if description else title,
            "category": category,
            "subcategory": None,
            "relevance_score": round(relevance_score, 2),
            "sentiment_score": round(sentiment_score, 2),
            "confidence_score": confidence_score,
            "event_date": datetime.utcnow().isoformat(),
            "tags": MockAPIService._generate_tags(category)
        }

    @staticmethod
    def _generate_tags(category: str) -> List[str]:
        """Generate relevant tags based on category."""
        tag_map = {
            "funding": ["investment", "venture capital", "growth"],
            "acquisition": ["M&A", "strategic", "expansion"],
            "leadership_change": ["executive", "management", "hiring"],
            "product_launch": ["innovation", "product", "release"],
            "partnership": ["collaboration", "strategic", "alliance"],
            "financial_results": ["earnings", "performance", "metrics"],
            "award": ["recognition", "achievement", "industry leader"],
            "expansion": ["growth", "market expansion", "scaling"]
        }
        return tag_map.get(category, ["company news", "update"])

    @staticmethod
    def mock_ai_insights(
        event_data: Dict[str, Any],
        crm_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate fake AI-powered insights and recommendations.

        Args:
            event_data: Classified event data
            crm_data: Optional CRM enrichment data

        Returns:
            Dict with insights and recommendations
        """
        category = event_data.get("category", "other")
        relevance = event_data.get("relevance_score", 0.5)
        sentiment = event_data.get("sentiment_score", 0.0)

        # Generate insights based on category and CRM data
        insights = []
        recommended_actions = []
        risk_assessment = "Low Risk"
        urgency_level = "Normal"

        if category == "funding":
            insights.append("Client secured significant funding, indicating strong investor confidence and growth trajectory.")
            insights.append("New capital may enable expansion of team, technology, and market presence.")
            recommended_actions.append("Schedule congratulatory call to discuss how our solutions can support their growth")
            recommended_actions.append("Explore upsell opportunities for enterprise features")
            if crm_data and crm_data.get("health_score", 100) < 70:
                recommended_actions.append("Proactively address any outstanding concerns before their expansion phase")
            urgency_level = "High"

        elif category == "acquisition":
            insights.append("Acquisition may signal strategic shift or market consolidation strategy.")
            insights.append("Integration phase could present both opportunities and risks for existing partnerships.")
            recommended_actions.append("Reach out to understand integration plans and timeline")
            recommended_actions.append("Ensure key stakeholders in acquired company are aware of our value")
            recommended_actions.append("Monitor for any changes in budget or priorities")
            risk_assessment = "Medium Risk"
            urgency_level = "High"

        elif category == "leadership_change":
            insights.append("Leadership transition may influence strategic priorities and vendor relationships.")
            if crm_data:
                insights.append("Ensure continuity of relationship during transition period.")
            recommended_actions.append("Schedule introduction meeting with new executive")
            recommended_actions.append("Share success stories and ROI documentation")
            recommended_actions.append("Reconfirm strategic alignment and priorities")
            risk_assessment = "Medium Risk"
            urgency_level = "High"

        elif category == "product_launch":
            insights.append("New product launch indicates innovation focus and potential for complementary integrations.")
            recommended_actions.append("Explore integration opportunities with their new product")
            recommended_actions.append("Feature client's launch in customer success story")
            urgency_level = "Normal"

        elif category == "partnership":
            insights.append("Strategic partnership could expand their market reach and customer base.")
            if crm_data:
                insights.append("Partnership may increase their reliance on scalable infrastructure solutions.")
            recommended_actions.append("Congratulate on partnership and discuss scalability needs")
            recommended_actions.append("Position solutions as enabler for partnership success")

        elif category == "financial_results":
            if sentiment > 0:
                insights.append("Strong financial performance indicates healthy business and potential for expansion.")
                recommended_actions.append("Explore expansion and upsell opportunities")
            else:
                insights.append("Financial challenges may impact budget and renewal decisions.")
                recommended_actions.append("Proactively demonstrate ROI and cost savings")
                recommended_actions.append("Offer flexible payment terms if appropriate")
                risk_assessment = "Medium Risk"
                urgency_level = "High"

        elif category == "award":
            insights.append("Industry recognition demonstrates market leadership and credibility.")
            recommended_actions.append("Congratulate on award and request joint marketing opportunity")
            recommended_actions.append("Feature in case study highlighting mutual success")

        # Add CRM-based insights if available
        if crm_data:
            health_score = crm_data.get("health_score", 100)
            if health_score < 50:
                insights.append(f"⚠️ CRITICAL: Account health score is {health_score}. Immediate attention required.")
                recommended_actions.insert(0, "Schedule urgent check-in call with account owner and executive sponsor")
                risk_assessment = "High Risk"
                urgency_level = "Critical"
            elif health_score < 70:
                insights.append(f"⚠️ Account health score is {health_score}. Monitor closely.")
                recommended_actions.append("Schedule proactive health check meeting")
                risk_assessment = "Medium Risk"

            # Contract renewal insights
            contract_end = crm_data.get("contract_end_date")
            if contract_end:
                try:
                    end_date = datetime.fromisoformat(contract_end.replace("Z", "+00:00"))
                    days_until_renewal = (end_date - datetime.utcnow()).days
                    if days_until_renewal < 90:
                        insights.append(f"Contract renewal due in {days_until_renewal} days.")
                        recommended_actions.insert(0, "Initiate renewal conversation immediately")
                        urgency_level = "High"
                except:
                    pass

        # Default insights if none generated
        if not insights:
            insights.append("Stay informed about client developments to maintain strong relationship.")
            recommended_actions.append("Monitor for follow-up news and developments")

        return {
            "insights": insights,
            "recommended_actions": recommended_actions,
            "risk_assessment": risk_assessment,
            "urgency_level": urgency_level,
            "generated_at": datetime.utcnow().isoformat(),
            "confidence": "Mock Data - For Testing Only"
        }

    @staticmethod
    def generate_content_hash(content: str) -> str:
        """Generate a hash for content deduplication."""
        return hashlib.sha256(content.encode()).hexdigest()