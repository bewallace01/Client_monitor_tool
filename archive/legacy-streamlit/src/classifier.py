"""Event classification module - categorizes events into types."""

import re
from typing import Dict, List, Tuple


def classify_event(title: str, summary: str = "") -> Tuple[str, float]:
    """
    Classify an event based on its title and summary.

    Args:
        title: Event title
        summary: Event summary/description

    Returns:
        Tuple of (event_type, confidence_score)

    Event types:
        - funding: Funding rounds, investments, capital raises
        - acquisition: Mergers, acquisitions, buyouts
        - leadership: Executive appointments, departures
        - product: Product launches, updates, features
        - partnership: Partnerships, collaborations, alliances
        - financial: Earnings, revenue, financial results
        - award: Awards, recognition, certifications
        - regulatory: Compliance, legal, regulatory changes
        - news: General news and announcements
    """
    text = f"{title} {summary}".lower()

    # Classification patterns with keywords and confidence weights
    patterns = {
        "funding": {
            "keywords": [
                "funding", "investment", "raised", "capital", "series a", "series b",
                "series c", "seed round", "venture", "financing", "fundraise",
                "investor", "backed by", "valuation", "round"
            ],
            "weight": 1.0
        },
        "acquisition": {
            "keywords": [
                "acquisition", "acquired", "merger", "buyout", "acquired by",
                "purchase", "bought", "takeover", "deal", "m&a"
            ],
            "weight": 1.0
        },
        "leadership": {
            "keywords": [
                "ceo", "cto", "cfo", "coo", "president", "appointed", "executive",
                "hire", "joins", "departure", "resigned", "named", "promoted",
                "leadership", "board", "director", "vice president"
            ],
            "weight": 0.9
        },
        "product": {
            "keywords": [
                "launch", "released", "announces", "unveils", "introduces",
                "new product", "feature", "update", "version", "platform",
                "solution", "beta", "preview", "available"
            ],
            "weight": 0.85
        },
        "partnership": {
            "keywords": [
                "partnership", "partner", "collaboration", "alliance", "team up",
                "joins forces", "agreement", "integrate", "integration",
                "works with", "collaborate"
            ],
            "weight": 0.9
        },
        "financial": {
            "keywords": [
                "earnings", "revenue", "profit", "quarterly", "financial results",
                "q1", "q2", "q3", "q4", "fy", "fiscal", "beats estimates",
                "misses estimates", "guidance", "eps", "ebitda"
            ],
            "weight": 1.0
        },
        "award": {
            "keywords": [
                "award", "wins", "recognition", "certified", "certification",
                "ranked", "named to", "best", "top", "leader", "excellence",
                "honor", "prize"
            ],
            "weight": 0.8
        },
        "regulatory": {
            "keywords": [
                "regulation", "compliance", "legal", "lawsuit", "court",
                "fine", "penalty", "investigation", "sec", "ftc", "fcc",
                "gdpr", "privacy", "data breach", "settlement"
            ],
            "weight": 0.95
        }
    }

    # Calculate scores for each category
    scores: Dict[str, float] = {}

    for event_type, config in patterns.items():
        keywords = config["keywords"]
        weight = config["weight"]

        # Count keyword matches
        matches = sum(1 for keyword in keywords if keyword in text)

        if matches > 0:
            # Calculate confidence based on number of matches and category weight
            # More matches = higher confidence
            confidence = min(1.0, (matches / len(keywords)) * 10) * weight
            scores[event_type] = confidence

    # If no matches found, classify as general news
    if not scores:
        return ("news", 0.5)

    # Return the category with highest confidence
    best_type = max(scores.items(), key=lambda x: x[1])
    return best_type


def classify_event_multi(title: str, summary: str = "", threshold: float = 0.3) -> List[Tuple[str, float]]:
    """
    Classify an event into multiple categories if applicable.

    Args:
        title: Event title
        summary: Event summary/description
        threshold: Minimum confidence threshold for including a category

    Returns:
        List of (event_type, confidence) tuples sorted by confidence (highest first)
    """
    text = f"{title} {summary}".lower()

    patterns = {
        "funding": {
            "keywords": [
                "funding", "investment", "raised", "capital", "series a", "series b",
                "series c", "seed round", "venture", "financing", "fundraise",
                "investor", "backed by", "valuation", "round"
            ],
            "weight": 1.0
        },
        "acquisition": {
            "keywords": [
                "acquisition", "acquired", "merger", "buyout", "acquired by",
                "purchase", "bought", "takeover", "deal", "m&a"
            ],
            "weight": 1.0
        },
        "leadership": {
            "keywords": [
                "ceo", "cto", "cfo", "coo", "president", "appointed", "executive",
                "hire", "joins", "departure", "resigned", "named", "promoted",
                "leadership", "board", "director", "vice president"
            ],
            "weight": 0.9
        },
        "product": {
            "keywords": [
                "launch", "released", "announces", "unveils", "introduces",
                "new product", "feature", "update", "version", "platform",
                "solution", "beta", "preview", "available"
            ],
            "weight": 0.85
        },
        "partnership": {
            "keywords": [
                "partnership", "partner", "collaboration", "alliance", "team up",
                "joins forces", "agreement", "integrate", "integration",
                "works with", "collaborate"
            ],
            "weight": 0.9
        },
        "financial": {
            "keywords": [
                "earnings", "revenue", "profit", "quarterly", "financial results",
                "q1", "q2", "q3", "q4", "fy", "fiscal", "beats estimates",
                "misses estimates", "guidance", "eps", "ebitda"
            ],
            "weight": 1.0
        },
        "award": {
            "keywords": [
                "award", "wins", "recognition", "certified", "certification",
                "ranked", "named to", "best", "top", "leader", "excellence",
                "honor", "prize"
            ],
            "weight": 0.8
        },
        "regulatory": {
            "keywords": [
                "regulation", "compliance", "legal", "lawsuit", "court",
                "fine", "penalty", "investigation", "sec", "ftc", "fcc",
                "gdpr", "privacy", "data breach", "settlement"
            ],
            "weight": 0.95
        }
    }

    scores: List[Tuple[str, float]] = []

    for event_type, config in patterns.items():
        keywords = config["keywords"]
        weight = config["weight"]

        matches = sum(1 for keyword in keywords if keyword in text)

        if matches > 0:
            confidence = min(1.0, (matches / len(keywords)) * 10) * weight
            if confidence >= threshold:
                scores.append((event_type, confidence))

    # Sort by confidence (highest first)
    scores.sort(key=lambda x: x[1], reverse=True)

    # If no matches found, return news category
    if not scores:
        return [("news", 0.5)]

    return scores


def extract_tags(title: str, summary: str = "", max_tags: int = 5) -> List[str]:
    """
    Extract relevant tags from event title and summary.

    Args:
        title: Event title
        summary: Event summary/description
        max_tags: Maximum number of tags to return

    Returns:
        List of extracted tags
    """
    text = f"{title} {summary}".lower()

    # Common important terms in business/tech news
    tag_patterns = {
        # Funding related
        r'\b(series [a-z])\b': 'series-funding',
        r'\b(seed round)\b': 'seed-funding',
        r'\b(venture capital|vc)\b': 'venture-capital',
        r'\b(ipo)\b': 'ipo',

        # Business types
        r'\b(startup|start-up)\b': 'startup',
        r'\b(enterprise)\b': 'enterprise',
        r'\b(saas)\b': 'saas',
        r'\b(ai|artificial intelligence)\b': 'ai',
        r'\b(machine learning|ml)\b': 'machine-learning',
        r'\b(cloud)\b': 'cloud',
        r'\b(blockchain)\b': 'blockchain',
        r'\b(crypto|cryptocurrency)\b': 'crypto',

        # Event types
        r'\b(merger|acquisition|m&a)\b': 'ma',
        r'\b(partnership)\b': 'partnership',
        r'\b(product launch)\b': 'product-launch',
        r'\b(expansion)\b': 'expansion',

        # Industries
        r'\b(fintech)\b': 'fintech',
        r'\b(healthtech|health tech)\b': 'healthtech',
        r'\b(edtech|education tech)\b': 'edtech',
        r'\b(e-commerce|ecommerce)\b': 'ecommerce',
        r'\b(cybersecurity)\b': 'cybersecurity',
    }

    tags = set()

    for pattern, tag in tag_patterns.items():
        if re.search(pattern, text):
            tags.add(tag)

    # Get event type as a tag
    event_type, _ = classify_event(title, summary)
    tags.add(event_type)

    # Convert to list and limit
    return list(tags)[:max_tags]
