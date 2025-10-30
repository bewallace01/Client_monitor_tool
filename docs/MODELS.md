# Data Models Documentation

## Overview

The Client Intelligence Monitor uses a **dual-model architecture**:

1. **ORM Models** (SQLAlchemy) - For database persistence
2. **DTO Models** (Dataclasses) - For business logic and data transfer

This separation provides flexibility and allows the business logic to work independently of the database.

## Architecture

```
┌─────────────────────┐         ┌──────────────────────┐
│   ORM Models        │         │   DTO Models         │
│   (Database)        │ ◄────► │   (Business Logic)   │
├─────────────────────┤         ├──────────────────────┤
│ • Client            │         │ • ClientDTO          │
│ • Event             │         │ • EventDTO           │
│ • SearchCache       │         │ • SearchCacheDTO     │
└─────────────────────┘         └──────────────────────┘
         │                                │
         └────────────┬───────────────────┘
                      │
              ┌───────▼────────┐
              │  Utils Module  │
              │  (Converters)  │
              └────────────────┘
```

---

## 1. ClientDTO

**Purpose**: Represents a client company being monitored.

### Fields

```python
@dataclass
class ClientDTO:
    id: str                              # UUID
    name: str                            # Company name
    industry: Optional[str]              # Industry/sector
    priority: Literal["high", "medium", "low"]
    keywords: List[str]                  # Search keywords
    monitoring_since: datetime           # When monitoring started
    last_checked: Optional[datetime]     # Last check timestamp
    metadata: Dict[str, Any]             # Additional data

    # Optional CS fields
    domain: Optional[str]                # Website domain
    description: Optional[str]           # Company description
    account_owner: Optional[str]         # CS manager
    tier: Optional[str]                  # Account tier
    is_active: bool                      # Monitoring status
```

### Methods

| Method | Description |
|--------|-------------|
| `to_dict()` | Convert to dictionary |
| `from_dict(data)` | Create from dictionary |
| `validate()` | Validate data, returns (bool, error_msg) |
| `to_json()` | Convert to JSON string |
| `from_json(json_str)` | Create from JSON string |
| `create_sample(name, priority)` | Factory method for testing |

### Example Usage

```python
from src.models import ClientDTO

# Create a new client
client = ClientDTO(
    id=str(uuid.uuid4()),
    name="Acme Corp",
    industry="SaaS",
    priority="high",
    keywords=["enterprise", "cloud", "AI"],
    monitoring_since=datetime.utcnow(),
)

# Validate
is_valid, error = client.validate()
if not is_valid:
    print(f"Validation error: {error}")

# Create sample for testing
sample = ClientDTO.create_sample(name="TestCo", priority="medium")

# Convert to JSON
json_str = client.to_json()

# Recreate from JSON
client2 = ClientDTO.from_json(json_str)
```

---

## 2. EventDTO

**Purpose**: Represents a business event for a client.

### Fields

```python
@dataclass
class EventDTO:
    id: str                                      # UUID
    client_id: str                               # Client UUID
    event_type: Literal["funding", "acquisition", "leadership", "product", "news", "other"]
    title: str                                   # Event title
    summary: Optional[str]                       # Event description
    source_url: Optional[str]                    # Article URL
    source_name: Optional[str]                   # Source (e.g., "TechCrunch")
    published_date: datetime                     # When event occurred
    discovered_date: datetime                    # When we found it
    relevance_score: float                       # 0.0 to 1.0
    sentiment: Literal["positive", "neutral", "negative"]
    status: Literal["new", "reviewed", "actioned", "archived"]
    tags: List[str]                              # Custom tags
    user_notes: Optional[str]                    # User comments

    # Additional fields
    sentiment_score: Optional[float]             # -1.0 to 1.0 (granular)
    metadata: Dict[str, Any]                     # Extra data
```

### Methods

| Method | Description |
|--------|-------------|
| `to_dict()` | Convert to dictionary |
| `from_dict(data)` | Create from dictionary |
| `validate()` | Validate data |
| `is_relevant(threshold)` | Check if meets relevance threshold |
| `get_relevance_label()` | Get "high", "medium", or "low" |
| `get_sentiment_emoji()` | Get emoji for sentiment |
| `mark_as_reviewed()` | Change status to reviewed |
| `mark_as_actioned()` | Change status to actioned |
| `archive()` | Change status to archived |
| `to_json()` | Convert to JSON string |
| `from_json(json_str)` | Create from JSON |
| `create_sample(...)` | Factory method for testing |

### Example Usage

```python
from src.models import EventDTO

# Create an event
event = EventDTO(
    id=str(uuid.uuid4()),
    client_id=client.id,
    event_type="funding",
    title="Acme Corp raises $50M Series B",
    summary="Acme Corp announced...",
    source_url="https://techcrunch.com/...",
    source_name="TechCrunch",
    published_date=datetime.utcnow(),
    discovered_date=datetime.utcnow(),
    relevance_score=0.85,
    sentiment="positive",
    status="new",
    tags=["funding", "series-b"],
)

# Check relevance
if event.is_relevant(threshold=0.7):
    print(f"High relevance: {event.get_relevance_label()}")

# Update status
event.mark_as_reviewed()
event.mark_as_actioned()

# Create sample
sample = EventDTO.create_sample(
    client_id=client.id,
    event_type="product",
    relevance_score=0.9
)
```

---

## 3. SearchCacheDTO

**Purpose**: Cache search results to reduce API calls.

### Fields

```python
@dataclass
class SearchCacheDTO:
    query: str                          # Search query
    api_source: str                     # API name (e.g., "newsapi")
    results: List[Dict[str, Any]]       # Cached results
    cached_at: datetime                 # Cache timestamp
    expires_at: datetime                # Expiry timestamp

    # Optional fields
    result_count: int                   # Number of results
    query_hash: Optional[str]           # SHA256 hash
    metadata: Dict[str, Any]            # Extra data
```

### Methods

| Method | Description |
|--------|-------------|
| `to_dict()` | Convert to dictionary |
| `from_dict(data)` | Create from dictionary |
| `validate()` | Validate data |
| `is_expired()` | Check if cache expired |
| `is_valid()` | Check if cache still valid |
| `time_until_expiry()` | Get time remaining |
| `get_cache_age()` | Get age of cache |
| `refresh(results, ttl)` | Update with new results |
| `extend_expiry(hours)` | Extend expiry time |
| `to_json()` | Convert to JSON |
| `from_json(json_str)` | Create from JSON |
| `create_sample(...)` | Factory method for testing |

### Example Usage

```python
from src.models import SearchCacheDTO
from datetime import timedelta

# Create cache entry
cache = SearchCacheDTO(
    query="Acme Corp funding",
    api_source="newsapi",
    results=[{"title": "...", "url": "..."}],
    cached_at=datetime.utcnow(),
    expires_at=datetime.utcnow() + timedelta(hours=24),
)

# Check if still valid
if cache.is_valid():
    print(f"Cache valid for {cache.time_until_expiry()}")
    return cache.results
else:
    # Fetch new results...
    cache.refresh(new_results, ttl_hours=48)

# Check age
print(f"Cache age: {cache.get_cache_age()}")

# Create sample
sample = SearchCacheDTO.create_sample(
    query="TestCo",
    api_source="mock",
    ttl_hours=12
)
```

---

## Utility Functions

Located in `src/models/utils.py`

### Converters

```python
from src.models.utils import (
    orm_to_client_dto,
    orm_to_event_dto,
    orm_to_cache_dto,
)

# Convert ORM to DTO
client_dto = orm_to_client_dto(orm_client)
event_dto = orm_to_event_dto(orm_event)
cache_dto = orm_to_cache_dto(orm_cache)
```

### Validators

```python
from src.models.utils import (
    validate_priority,
    validate_event_type,
    validate_sentiment,
    validate_status,
)

# Validate values
is_valid = validate_priority("high")  # True
is_valid = validate_event_type("funding")  # True
```

### Normalizers

```python
from src.models.utils import (
    normalize_relevance_score,
    normalize_sentiment_score,
)

# Normalize scores
score = normalize_relevance_score(1.5)  # Returns 1.0
score = normalize_sentiment_score(-2.0)  # Returns -1.0
```

### Formatters

```python
from src.models.utils import (
    sentiment_score_to_label,
    relevance_score_to_label,
    format_datetime_ago,
)

# Convert scores to labels
label = sentiment_score_to_label(0.7)  # "positive"
label = relevance_score_to_label(0.8)  # "high"

# Format time
ago = format_datetime_ago(some_datetime)  # "2 hours ago"
```

### Helpers

```python
from src.models.utils import (
    generate_uuid,
    calculate_cache_expiry,
    is_cache_expired,
)

# Generate UUID
new_id = generate_uuid()

# Calculate expiry
expires_at = calculate_cache_expiry(ttl_hours=24)

# Check if expired
expired = is_cache_expired(expires_at)
```

---

## Testing

Run the model tests:

```bash
python scripts/test_models.py
```

This tests:
- All DTO creation and validation
- Conversion methods (to_dict, from_dict, to_json, from_json)
- Sample factory methods
- Utility functions
- Error handling

---

## Best Practices

### 1. Use DTOs for Business Logic

```python
# ✅ Good - Use DTOs in business logic
def process_event(event: EventDTO) -> bool:
    if event.is_relevant(0.7):
        event.mark_as_actioned()
        return True
    return False
```

### 2. Use ORM for Database Operations

```python
# ✅ Good - Use ORM for database
with db.get_session() as session:
    orm_client = ClientRepository.get_by_id(session, client_id)
    # Convert to DTO for processing
    dto = orm_to_client_dto(orm_client)
```

### 3. Always Validate

```python
# ✅ Good - Always validate before saving
client = ClientDTO(...)
is_valid, error = client.validate()
if not is_valid:
    raise ValueError(f"Invalid client: {error}")
```

### 4. Use Factory Methods for Testing

```python
# ✅ Good - Use create_sample() in tests
def test_something():
    client = ClientDTO.create_sample(name="TestCo")
    event = EventDTO.create_sample(client_id=client.id)
    assert event.is_relevant(0.5)
```

---

## Model Comparison

| Feature | ORM Model | DTO Model |
|---------|-----------|-----------|
| **Purpose** | Database persistence | Business logic |
| **ID Type** | int (auto-increment) | str (UUID) |
| **Dependencies** | SQLAlchemy | Pure Python |
| **Serialization** | Manual | Built-in (dataclass) |
| **Validation** | Database constraints | Explicit methods |
| **Testing** | Requires database | Standalone |

---

## Migration Guide

If you have existing ORM usage, convert to DTOs:

```python
# Before (ORM-only)
client = ClientRepository.get_by_id(session, 1)
if client.name:
    process_client(client)

# After (with DTOs)
orm_client = ClientRepository.get_by_id(session, 1)
client_dto = orm_to_client_dto(orm_client)
if client_dto.validate()[0]:
    process_client(client_dto)
```

---

## Future Enhancements

Planned improvements:

- [ ] Pydantic models for API validation
- [ ] JSON Schema generation
- [ ] Automatic DTO ↔ ORM synchronization
- [ ] Event sourcing support
- [ ] Audit trail fields
- [ ] Soft delete support

---

## Questions?

See:
- `scripts/test_models.py` - Working examples
- `src/models/utils.py` - Utility functions
- `src/models/*_dto.py` - Model implementations
