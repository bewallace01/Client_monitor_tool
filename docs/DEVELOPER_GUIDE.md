# Client Intelligence Monitor - Developer Guide

Technical documentation for developers working on the Client Intelligence Monitor.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Data Flow](#data-flow)
4. [Core Components](#core-components)
5. [Adding New Features](#adding-new-features)
6. [Database Schema](#database-schema)
7. [API Reference](#api-reference)
8. [Contributing Guidelines](#contributing-guidelines)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI Layer                      │
│  (app.py + src/ui/pages/ + src/ui/components/)             │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                   Business Logic Layer                       │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐     │
│  │ Collectors  │  │  Processors  │  │   Scheduler   │     │
│  └─────────────┘  └──────────────┘  └───────────────┘     │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                    Data Access Layer                         │
│              src/storage/sqlite_store.py                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                      SQLite Database                         │
│              data/client_intelligence.db                     │
└─────────────────────────────────────────────────────────────┘
```

### Design Patterns

**1. Repository Pattern** (Storage Layer)
- `BaseStorage` interface defines contract
- `SQLiteStorage` implements concrete persistence
- Easy to swap database backends

**2. Factory Pattern** (Collectors)
- `CollectorFactory` creates appropriate collector
- Falls back to mock on API failures
- Extensible for new data sources

**3. DTO Pattern** (Data Models)
- `ClientDTO`, `EventDTO` for data transfer
- Validation built-in
- Separates domain models from persistence

**4. Strategy Pattern** (Processors)
- Classifier, Scorer, Deduplicator are interchangeable
- Can implement different algorithms
- Testable in isolation

---

## Project Structure

```
client-monitor/
│
├── app.py                      # Main Streamlit application entry point
├── config/
│   └── settings.py            # Application configuration (Pydantic)
│
├── src/                       # Source code
│   ├── models/                # Data Transfer Objects
│   │   ├── __init__.py
│   │   ├── client.py         # ClientDTO
│   │   ├── event.py          # EventDTO
│   │   └── cache.py          # SearchCacheDTO
│   │
│   ├── storage/               # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py           # BaseStorage interface
│   │   └── sqlite_store.py   # SQLite implementation
│   │
│   ├── collectors/            # News collection
│   │   ├── __init__.py
│   │   ├── base_collector.py # Base collector interface
│   │   ├── mock_collector.py # Mock API for testing
│   │   ├── google_collector.py # Google Custom Search
│   │   ├── news_collector.py # NewsAPI
│   │   └── factory.py        # Collector factory
│   │
│   ├── ui/                    # User interface
│   │   ├── pages/            # Streamlit pages
│   │   │   ├── dashboard.py
│   │   │   ├── clients.py
│   │   │   ├── events.py
│   │   │   ├── monitor.py
│   │   │   ├── insights.py
│   │   │   ├── notifications.py
│   │   │   ├── settings.py
│   │   │   ├── system_test.py
│   │   │   └── help.py
│   │   │
│   │   ├── components/        # Reusable UI components
│   │   │   ├── __init__.py
│   │   │   └── global_search.py
│   │   │
│   │   └── polish.py         # UI polish and design system
│   │
│   ├── classifier.py          # Event classification
│   ├── scorer.py             # Relevance scoring
│   ├── deduplicator.py       # Event deduplication
│   └── rate_limiter.py       # API rate limiting
│
├── scripts/                   # Utility scripts
│   ├── seed_demo_data.py     # Generate demo data
│   └── reset_database.py     # Database reset utility
│
├── tests/                     # Test suite
│   ├── conftest.py           # Pytest fixtures
│   ├── fixtures/             # Test data
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
│
├── data/                      # Data directory (generated)
│   └── client_intelligence.db # SQLite database
│
├── docs/                      # Documentation
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   ├── DEPLOYMENT.md
│   ├── API_SETUP.md
│   └── TESTING.md
│
└── requirements.txt           # Python dependencies
```

### Key Files Explained

**app.py** - Main entry point
- Initializes Streamlit
- Handles navigation
- Loads pages dynamically

**config/settings.py** - Configuration
- Uses Pydantic for validation
- Environment variable support
- Type-safe settings

**src/models/** - Data models
- DTOs for data transfer
- Validation logic
- Serialization methods

**src/storage/** - Persistence
- Abstract interface + concrete implementation
- Transaction management
- Query optimization

**src/ui/** - User interface
- Streamlit pages and components
- Design system (polish.py)
- Reusable UI elements

---

## Data Flow

### Event Collection Flow

```
1. User triggers scan or scheduler runs
              │
              ▼
2. CollectorFactory creates appropriate collector
              │
              ▼
3. Collector searches for news (API or Mock)
              │
              ▼
4. Raw results are returned
              │
              ▼
5. Classifier categorizes each event
              │
              ▼
6. Scorer calculates relevance
              │
              ▼
7. Deduplicator filters duplicates
              │
              ▼
8. EventDTO objects created
              │
              ▼
9. Storage layer persists to database
              │
              ▼
10. Notification rules evaluated
              │
              ▼
11. Alerts sent (if rules match)
```

### Request Flow (User Interaction)

```
User clicks button → Streamlit event → Python function
                                            │
                                            ▼
                                    Business logic executes
                                            │
                                            ▼
                                    Storage layer accessed
                                            │
                                            ▼
                                    Database query/update
                                            │
                                            ▼
                                    Results returned
                                            │
                                            ▼
                                    UI updated via st.rerun()
```

---

## Core Components

### 1. Models (DTOs)

**ClientDTO** (`src/models/client.py`)

```python
@dataclass
class ClientDTO:
    """Client data transfer object."""
    id: str
    name: str
    industry: str
    priority: Literal['low', 'medium', 'high']
    keywords: List[str]
    monitoring_since: datetime
    # ... other fields

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Validate client data."""
        if not self.name:
            return False, "Name is required"
        if self.priority not in ['low', 'medium', 'high']:
            return False, "Invalid priority"
        return True, None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        # Implementation

    @classmethod
    def from_dict(cls, data: Dict) -> 'ClientDTO':
        """Create from dictionary."""
        # Implementation
```

**EventDTO** (`src/models/event.py`)

```python
@dataclass
class EventDTO:
    """Event data transfer object."""
    id: str
    client_id: str
    event_type: str
    title: str
    summary: str
    source_url: str
    source_name: str
    published_date: datetime
    discovered_date: datetime
    relevance_score: float  # 0.0 to 1.0
    sentiment: Literal['positive', 'neutral', 'negative']
    # ... other fields
```

### 2. Storage Layer

**Base Interface** (`src/storage/base.py`)

```python
class BaseStorage(ABC):
    """Abstract base class for storage implementations."""

    @abstractmethod
    def connect(self) -> None:
        """Establish connection."""
        pass

    @abstractmethod
    def create_client(self, client: ClientDTO) -> ClientDTO:
        """Create a new client."""
        pass

    @abstractmethod
    def get_client(self, client_id: str) -> Optional[ClientDTO]:
        """Retrieve client by ID."""
        pass

    # ... other CRUD methods
```

**SQLite Implementation** (`src/storage/sqlite_store.py`)

Key features:
- Context manager for connections
- Transaction support
- Prepared statements for security
- Schema migration support
- Cascade deletes

Example usage:
```python
storage = SQLiteStorage()
storage.connect()
storage.initialize_database()

# Create client
client = ClientDTO(...)
created = storage.create_client(client)

# Query
all_clients = storage.get_all_clients()
```

### 3. Collectors

**Factory Pattern** (`src/collectors/factory.py`)

```python
class CollectorFactory:
    """Factory for creating collector instances."""

    @staticmethod
    def create_collector(use_mock: bool = True, **config):
        """
        Create appropriate collector based on configuration.

        Args:
            use_mock: Use mock collector for testing
            **config: Configuration for real collectors

        Returns:
            Collector instance

        Falls back to mock collector if real collector fails.
        """
        if use_mock:
            return MockCollector()

        try:
            # Try to create real collector
            if config.get('collector_type') == 'google':
                return GoogleCollector(**config)
            elif config.get('collector_type') == 'news':
                return NewsCollector(**config)
        except Exception as e:
            logger.warning(f"Falling back to mock: {e}")
            return MockCollector()
```

**Mock Collector** (`src/collectors/mock_collector.py`)

- Zero-cost testing
- Realistic response structure
- Predictable results
- No API keys required

### 4. Processors

**Classifier** (`src/classifier.py`)

```python
def classify_event(title: str, summary: str = "") -> Tuple[str, float]:
    """
    Classify event based on title and summary.

    Args:
        title: Event title
        summary: Event summary (optional)

    Returns:
        Tuple of (event_type, confidence)
            event_type: funding, acquisition, leadership, etc.
            confidence: 0.0 to 1.0

    Uses keyword-based classification with weighted scoring.
    """
    # Implementation
```

Event types:
- funding
- acquisition
- leadership
- product
- partnership
- financial
- award
- regulatory
- news

**Scorer** (`src/scorer.py`)

```python
def calculate_relevance_score(
    event_title: str,
    event_summary: str,
    event_type: str,
    client_name: str,
    client_industry: Optional[str] = None,
    event_date: Optional[datetime] = None,
    sentiment: str = "neutral"
) -> float:
    """
    Calculate relevance score (0.0 to 1.0).

    Factors:
    - Text relevance (0-40 points)
    - Event type importance (0-30 points)
    - Recency (0-20 points)
    - Sentiment (0-10 points)

    Returns normalized score 0.0 to 1.0.
    """
    # Implementation
```

**Deduplicator** (`src/deduplicator.py`)

```python
class EventDeduplicator:
    """Identifies and removes duplicate events."""

    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize deduplicator.

        Args:
            similarity_threshold: Threshold for duplicate detection
                                  (0.0 to 1.0, higher = stricter)
        """
        self.similarity_threshold = similarity_threshold

    def find_duplicates(self, events: List[EventDTO]) -> List[Tuple[str, str]]:
        """Find duplicate event pairs."""
        # Implementation

    def remove_duplicates(self, events: List[EventDTO]) -> List[EventDTO]:
        """Remove duplicates, keeping highest relevance."""
        # Implementation
```

---

## Adding New Features

### Adding a New Event Type

1. **Update Classifier** (`src/classifier.py`):

```python
EVENT_TYPE_KEYWORDS = {
    # ... existing types
    'new_type': {
        'keywords': ['keyword1', 'keyword2'],
        'weight': 1.0
    }
}
```

2. **Update Scorer** (`src/scorer.py`):

```python
EVENT_TYPE_WEIGHTS = {
    # ... existing types
    'new_type': 0.8  # Importance weight
}
```

3. **Update UI** (`src/ui/polish.py`):

```python
def get_event_type_badge(event_type: str) -> str:
    """Get colored badge for event type."""
    badges = {
        # ... existing types
        'new_type': '<span style="...">🆕 NEW TYPE</span>'
    }
    return badges.get(event_type, badges['news'])
```

### Adding a New Collector

1. **Create Collector Class** (`src/collectors/new_collector.py`):

```python
from .base_collector import BaseCollector

class NewAPICollector(BaseCollector):
    """Collector for NewAPI service."""

    def __init__(self, api_key: str, **config):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://api.newapi.com"

    def search(self, query: str, **params) -> List[Dict]:
        """
        Search for news articles.

        Args:
            query: Search query
            **params: Additional parameters

        Returns:
            List of search results in standard format:
            [
                {
                    'title': str,
                    'url': str,
                    'snippet': str,
                    'source': str,
                    'published_date': str (ISO format)
                },
                ...
            ]
        """
        # Implementation
        response = requests.get(
            f"{self.base_url}/search",
            params={'q': query, 'apiKey': self.api_key}
        )
        return self._parse_response(response.json())

    def _parse_response(self, data: Dict) -> List[Dict]:
        """Parse API response into standard format."""
        results = []
        for item in data.get('items', []):
            results.append({
                'title': item['title'],
                'url': item['link'],
                'snippet': item['snippet'],
                'source': item.get('source', 'Unknown'),
                'published_date': item.get('date', '')
            })
        return results
```

2. **Update Factory** (`src/collectors/factory.py`):

```python
from .new_collector import NewAPICollector

class CollectorFactory:
    @staticmethod
    def create_collector(use_mock: bool = True, **config):
        if use_mock:
            return MockCollector()

        try:
            collector_type = config.get('collector_type')

            if collector_type == 'newapi':
                return NewAPICollector(
                    api_key=config.get('newapi_key'),
                    **config
                )
            # ... existing collectors

        except Exception as e:
            logger.warning(f"Falling back to mock: {e}")
            return MockCollector()
```

3. **Add Settings UI** (`src/ui/pages/settings.py`):

Add configuration fields in the API Configuration tab.

### Adding a New UI Page

1. **Create Page File** (`src/ui/pages/new_page.py`):

```python
"""New feature page."""

import streamlit as st
from src.storage import SQLiteStorage

def render_new_page():
    """Render the new feature page."""
    st.markdown('<h1 class="main-header">🆕 New Feature</h1>',
                unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Description of feature</p>',
                unsafe_allow_html=True)

    # Your page logic
    storage = SQLiteStorage()
    storage.connect()

    # ... implementation

if __name__ == "__main__":
    render_new_page()
```

2. **Add to Navigation** (`app.py`):

```python
# Add to page mapping
pages = {
    # ... existing pages
    "🆕 New Feature": "src.ui.pages.new_page"
}

# Add to sidebar navigation
if page == "🆕 New Feature":
    from src.ui.pages import new_page
    new_page.render_new_page()
```

---

## Database Schema

### Tables

**clients**
```sql
CREATE TABLE clients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    industry TEXT,
    priority TEXT NOT NULL DEFAULT 'medium',
    keywords TEXT,  -- JSON array
    monitoring_since TEXT NOT NULL,
    last_checked TEXT,
    metadata TEXT,  -- JSON object
    domain TEXT,
    description TEXT,
    account_owner TEXT,
    tier TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**events**
```sql
CREATE TABLE events (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    source_url TEXT,
    source_name TEXT,
    published_date TEXT NOT NULL,
    discovered_date TEXT NOT NULL,
    relevance_score REAL NOT NULL DEFAULT 0.5,
    sentiment TEXT NOT NULL DEFAULT 'neutral',
    sentiment_score REAL,
    status TEXT NOT NULL DEFAULT 'new',
    tags TEXT,  -- JSON array
    user_notes TEXT,
    metadata TEXT,  -- JSON object
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);
```

**search_cache**
```sql
CREATE TABLE search_cache (
    query_hash TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    api_source TEXT NOT NULL,
    results TEXT NOT NULL,  -- JSON array
    result_count INTEGER NOT NULL DEFAULT 0,
    cached_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    metadata TEXT  -- JSON object
);
```

**notification_rules**
```sql
CREATE TABLE notification_rules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    event_types TEXT,  -- JSON array
    min_relevance_score REAL NOT NULL DEFAULT 0.7,
    client_ids TEXT,  -- JSON array
    keywords TEXT,  -- JSON array
    frequency TEXT NOT NULL DEFAULT 'immediate',
    recipient_emails TEXT,  -- JSON array
    notification_type TEXT NOT NULL DEFAULT 'email',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_triggered TEXT,
    trigger_count INTEGER NOT NULL DEFAULT 0
);
```

### Indices

```sql
-- Client indices
CREATE INDEX idx_clients_name ON clients(name);
CREATE INDEX idx_clients_priority ON clients(priority);
CREATE INDEX idx_clients_active ON clients(is_active);

-- Event indices
CREATE INDEX idx_events_client ON events(client_id);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_published ON events(published_date DESC);
CREATE INDEX idx_events_relevance ON events(relevance_score DESC);
CREATE INDEX idx_events_status ON events(status);
```

---

## API Reference

### Storage API

See `src/storage/base.py` for complete interface.

**Common Operations:**

```python
# Initialize
storage = SQLiteStorage()
storage.connect()
storage.initialize_database()

# Create
client = storage.create_client(client_dto)
event = storage.create_event(event_dto)

# Read
client = storage.get_client(client_id)
events = storage.get_events_by_client(client_id)
recent = storage.get_recent_events(days=7)

# Update
updated_client = storage.update_client(client_id, {
    'priority': 'high',
    'tier': 'Enterprise'
})

# Delete
success = storage.delete_client(client_id)  # Cascades to events

# Search
clients = storage.search_clients("technology")
events = storage.search_events("funding")

# Statistics
stats = storage.get_statistics()
client_stats = storage.get_client_statistics(client_id)
```

### Collector API

```python
# Create collector
collector = CollectorFactory.create_collector(
    use_mock=False,
    collector_type='google',
    api_key='your-key'
)

# Search
results = collector.search("Company Name news")
# Returns: List[Dict] with keys: title, url, snippet, source, published_date
```

### Processor API

```python
# Classify event
event_type, confidence = classify_event(
    "Company raises $10M",
    "Full article text..."
)

# Calculate relevance
score = calculate_relevance_score(
    event_title="...",
    event_summary="...",
    event_type="funding",
    client_name="Company",
    client_industry="Technology",
    event_date=datetime.now(),
    sentiment="positive"
)

# Deduplicate
deduplicator = EventDeduplicator(similarity_threshold=0.85)
unique_events = deduplicator.remove_duplicates(event_list)
```

---

## Contributing Guidelines

### Setting Up Development Environment

```bash
# Clone repository
git clone <repo-url>
cd client-monitor

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run tests
pytest

# Start application
streamlit run app.py
```

### Code Style

**Python Code Style:**
- Follow PEP 8
- Use type hints
- Docstrings for all public functions/classes
- Maximum line length: 100 characters

**Example:**
```python
def process_event(
    event: EventDTO,
    client: ClientDTO,
    threshold: float = 0.5
) -> Optional[EventDTO]:
    """
    Process an event for a specific client.

    Args:
        event: Event to process
        client: Associated client
        threshold: Minimum relevance threshold

    Returns:
        Processed event if relevant, None otherwise

    Raises:
        ValueError: If event or client is invalid
    """
    # Implementation
```

### Testing Requirements

- Write tests for new features
- Maintain 80%+ coverage
- All tests must pass before merge
- Include both unit and integration tests

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/unit/test_models.py
```

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run Tests**
   ```bash
   pytest
   ```

4. **Commit**
   ```bash
   git add .
   git commit -m "Add: feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **PR Checklist**
   - [ ] Tests pass
   - [ ] Code follows style guide
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)
   - [ ] Reviewed by maintainer

### Commit Message Format

```
Type: Brief description

Detailed description of changes.

Fixes #123
```

Types:
- `Add:` New feature
- `Fix:` Bug fix
- `Update:` Improve existing feature
- `Refactor:` Code refactoring
- `Docs:` Documentation
- `Test:` Add/update tests
- `Style:` Code style changes

---

## Additional Resources

- **Testing Guide**: `docs/TESTING.md`
- **Deployment Guide**: `docs/DEPLOYMENT.md`
- **API Setup Guide**: `docs/API_SETUP.md`
- **User Guide**: `docs/USER_GUIDE.md`

---

**Last Updated**: 2025-10-15
**Version**: 1.0.0
