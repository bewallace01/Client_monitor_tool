# Mock Collector Guide

## Overview

The **Mock Collector** is a zero-cost event collection system that generates realistic fake news data for testing and development. It simulates the behavior of real news APIs without requiring API keys or incurring any costs.

## Features

✅ **Keyword-Based Search** - Returns relevant results based on query keywords
✅ **Realistic Latency** - Simulates API delays (0.3-0.8 seconds)
✅ **Rate Limiting** - Tracks request counts (100 requests per hour)
✅ **10 News Sources** - TechCrunch, Reuters, Bloomberg, WSJ, Forbes, etc.
✅ **7 Event Categories** - Funding, Acquisition, Leadership, Product, Partnership, Financial, Award
✅ **Varied Data** - Random amounts, dates, names, and descriptions

## Quick Start

### Using the UI

1. **Open the Streamlit app**:
   ```bash
   python -m streamlit run app.py
   ```

2. **Navigate to "🔍 Collector Test" page** in the sidebar

3. **Enter a search query** and click "Run Search"

4. **Try example queries**:
   - "TechCorp funding" → Returns funding announcements
   - "Acme Corp acquisition" → Returns acquisition news
   - "StartupXYZ CEO" → Returns leadership changes
   - "CompanyABC product launch" → Returns product announcements

### Using in Code

```python
from src.collectors import get_collector
from datetime import datetime, timedelta

# Initialize collector (automatically uses mock by default)
collector = get_collector()

# Search for events
results = collector.search(
    query="Acme Corp funding",
    from_date=datetime.utcnow() - timedelta(days=30),
    max_results=10
)

# Display results
for result in results:
    print(f"Title: {result.title}")
    print(f"Source: {result.source}")
    print(f"Published: {result.published_at}")
    print(f"URL: {result.url}")
    print()

# Check rate limit
status = collector.get_rate_limit_status()
print(f"Rate limit: {status['remaining']}/{status['limit']}")
```

## Keyword-Based Results

The mock collector intelligently returns relevant results based on keywords in your query:

| Keywords | Event Type | Example Results |
|----------|-----------|----------------|
| funding, investment, raised, series, venture | **Funding** | "TechCorp raises $50M in Series B funding" |
| acquisition, acquires, merger, buy, buyout | **Acquisition** | "Acme Corp acquires DataCorp for $100M" |
| CEO, CTO, CFO, leadership, executive, appoint | **Leadership** | "StartupXYZ appoints Sarah Chen as new CEO" |
| product, launch, release, unveil, feature | **Product** | "CompanyABC launches AI Platform" |
| partnership, partner, collaboration, alliance | **Partnership** | "TechCorp partners with Microsoft" |
| earnings, revenue, profit, financial, quarterly | **Financial** | "Acme Corp reports strong Q3 revenue" |
| award, recognition, winner, best | **Award** | "StartupXYZ named best SaaS by Gartner" |

If no keywords match, the collector returns a mix of all event types.

## Architecture

### Components

1. **BaseCollector** (`src/collectors/base.py`)
   - Abstract base class defining the collector interface
   - Methods: `search()`, `get_company_news()`, `get_rate_limit_status()`
   - Returns: `CollectorResult` objects

2. **MockCollector** (`src/collectors/mock_collector.py`)
   - Implements `BaseCollector`
   - Generates realistic fake data
   - Simulates API latency (0.3-0.8 seconds)
   - Tracks rate limits (100 requests/hour)

3. **Collector Factory** (`src/collectors/factory.py`)
   - Creates appropriate collector based on environment
   - Checks `APP_MODE` or `COLLECTOR_TYPE` env variable
   - Defaults to `MockCollector`

4. **Collector Test Page** (`src/ui/pages/collector_test.py`)
   - Interactive UI for testing searches
   - Shows rate limits and latency
   - Displays results with category breakdown

### Data Flow

```
User Query
    ↓
Collector Factory → MockCollector
    ↓
Keyword Detection → Category Selection
    ↓
Template Selection → Data Generation
    ↓
Simulated Latency (0.3-0.8s)
    ↓
CollectorResult Objects
```

## Configuration

### Environment Variables

```bash
# Use mock collector (default)
export APP_MODE=mock

# Use real NewsAPI (when implemented)
export APP_MODE=newsapi

# Alternative variable name
export COLLECTOR_TYPE=mock
```

### Available Collectors

Check available collectors programmatically:

```python
from src.collectors import list_available_collectors

collectors = list_available_collectors()
for name, info in collectors.items():
    print(f"{name}: {info['description']}")
    print(f"  Available: {info['available']}")
    print(f"  Requires API Key: {info['requires_api_key']}")
```

## Testing

### Run the Test Script

```bash
python test_collector.py
```

This will:
1. Initialize the collector
2. Check rate limit status
3. Test searches with different keywords
4. Display sample results
5. Verify response times

Expected output:
```
============================================================
Testing Mock Collector
============================================================

1. Initializing collector...
   [OK] Collector: mock
   [OK] Is Mock: True

2. Checking rate limit status...
   [OK] Limit: 100
   [OK] Remaining: 100

3. Testing search: 'TechCorp funding'
   [OK] Found 5 results in 0.36 seconds

4. Final rate limit check...
   [OK] Remaining: 96/100

============================================================
[PASS] All tests passed!
============================================================
```

## API Reference

### `get_collector(collector_type: Optional[str] = None) -> BaseCollector`

Get a collector instance.

**Parameters:**
- `collector_type` (optional): Override collector type ("mock", "newsapi", etc.)

**Returns:** `BaseCollector` instance

**Example:**
```python
collector = get_collector()  # Uses default (mock)
collector = get_collector("mock")  # Explicitly use mock
```

### `collector.search(query, from_date, to_date, max_results) -> List[CollectorResult]`

Search for news/events matching the query.

**Parameters:**
- `query` (str): Search query string
- `from_date` (datetime, optional): Start date for search
- `to_date` (datetime, optional): End date for search
- `max_results` (int): Maximum number of results (default: 20)

**Returns:** List of `CollectorResult` objects

**Example:**
```python
results = collector.search(
    query="Acme Corp",
    from_date=datetime.utcnow() - timedelta(days=30),
    max_results=10
)
```

### `collector.get_company_news(company_name, from_date, max_results) -> List[CollectorResult]`

Get news specifically about a company.

**Parameters:**
- `company_name` (str): Name of the company
- `from_date` (datetime, optional): Start date for search
- `max_results` (int): Maximum number of results (default: 20)

**Returns:** List of `CollectorResult` objects

**Example:**
```python
results = collector.get_company_news(
    company_name="Acme Corp",
    max_results=20
)
```

### `collector.get_rate_limit_status() -> dict`

Get current rate limit status.

**Returns:** Dictionary with keys:
- `limit` (int): Total requests allowed per time window
- `remaining` (int): Requests remaining in current window
- `reset_at` (datetime): When the limit resets
- `enabled` (bool): Whether rate limiting is enabled

**Example:**
```python
status = collector.get_rate_limit_status()
print(f"{status['remaining']}/{status['limit']} requests remaining")
```

### `CollectorResult`

Data class representing a news/event result.

**Attributes:**
- `title` (str): Title of the article
- `description` (str, optional): Article description/summary
- `url` (str, optional): URL to full article
- `source` (str): News source name
- `published_at` (datetime): Publication date/time
- `raw_data` (dict, optional): Original API response

## Customization

### Adding New Event Templates

Edit `src/collectors/mock_collector.py`:

```python
TEMPLATES = {
    EventCategory.FUNDING: [
        "{company} raises ${amount}M in Series {series} funding",
        # Add your template here
    ],
    # Add new category
    EventCategory.NEW_TYPE: [
        "Your template here: {company} does {action}",
    ],
}
```

### Adding New Keywords

Add keyword mappings in `_determine_categories_from_query()`:

```python
if any(word in query_lower for word in ["your", "keywords", "here"]):
    categories.append(EventCategory.YOUR_CATEGORY)
```

### Adjusting Latency

Change the delay range in `_simulate_latency()`:

```python
def _simulate_latency(self):
    delay = random.uniform(0.5, 1.5)  # Changed from 0.3-0.8
    time.sleep(delay)
```

## Future Enhancements

When real API collectors are implemented, they will:

1. **Implement the same `BaseCollector` interface**
2. **Be created through the same factory**
3. **Return the same `CollectorResult` format**
4. **Allow seamless switching via environment variable**

Example future usage:

```bash
# Switch to real NewsAPI
export APP_MODE=newsapi
export NEWSAPI_KEY=your_api_key_here

# Code stays the same!
collector = get_collector()  # Now uses NewsAPI
results = collector.search("Acme Corp")
```

## Troubleshooting

### Issue: Collector not found

**Solution:** Make sure you're importing from the correct module:
```python
from src.collectors import get_collector  # Correct
```

### Issue: No results returned

**Solution:** Check that your date range is valid:
```python
from_date = datetime.utcnow() - timedelta(days=30)  # Valid
from_date = datetime.utcnow() + timedelta(days=30)  # Invalid (future date)
```

### Issue: Slow response times

**Expected:** The mock collector intentionally adds 0.3-0.8 second delays to simulate real API latency. This is by design.

## Summary

The Mock Collector provides a complete, zero-cost solution for testing event collection:

- ✅ No API keys required
- ✅ No rate limits (simulated only)
- ✅ No costs
- ✅ Realistic behavior
- ✅ Keyword-aware results
- ✅ Full UI testing page
- ✅ Easy to extend

Use it to develop and test your client monitoring system before integrating real APIs!
