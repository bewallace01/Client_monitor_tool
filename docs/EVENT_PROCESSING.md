# Event Processing & Dashboard Guide

## Overview

The Client Intelligence Monitor now includes complete event processing logic and an enhanced visual dashboard to automatically classify, score, and display client events.

## Architecture

### 1. Event Processors (`src/processors/`)

#### Event Classifier (`event_classifier.py`)
**Purpose**: Automatically classify search results into structured events

**Features**:
- **Event Type Detection**: Uses keyword matching to identify event types:
  - 💰 Funding: "raise", "funding", "Series A/B/C", "investment"
  - 🤝 Acquisition: "acquire", "acquisition", "merger", "buys"
  - 👤 Leadership: "CEO", "CTO", "executive", "appoint", "hire"
  - 🚀 Product: "launch", "release", "unveils", "announces"
  - 🤝 Partnership: "partner", "collaboration", "alliance"
  - 💵 Financial: "earnings", "revenue", "quarterly", "profit"
  - 🏆 Award: "award", "wins", "recognition"
  - ⚖️ Regulatory: "regulatory", "compliance", "approval"

- **Sentiment Detection**: Analyzes keywords to determine sentiment:
  - **Positive**: "growth", "success", "wins", "expansion", "strong"
  - **Negative**: "layoff", "decline", "loss", "fails", "lawsuit"
  - **Neutral**: Equal or no sentiment keywords

- **Sentiment Scoring**: Returns score from -1.0 (very negative) to +1.0 (very positive)

**Usage**:
```python
from src.processors import classify_event
from src.collectors.base import CollectorResult
from src.models.client_dto import ClientDTO

event = classify_event(search_result, client)
# Returns EventDTO with event_type, sentiment, and sentiment_score
```

#### Relevance Scorer (`relevance_scorer.py`)
**Purpose**: Calculate how relevant an event is to a client

**Scoring Factors**:
1. **Client name in title**: +0.4
2. **Client name in summary**: +0.2
3. **Reputable source**: +0.2 (TechCrunch, Reuters, Bloomberg, etc.)
4. **Recent event** (< 7 days): +0.1
5. **High-value event type** (funding/acquisition/partnership): +0.1

**Maximum Score**: 1.0

**Usage**:
```python
from src.processors import calculate_relevance, update_event_relevance

# Get score and explanation
score, explanation = calculate_relevance(event, client)

# Or update event in-place
event = update_event_relevance(event, client)
```

#### Deduplicator (`deduplicator.py`)
**Purpose**: Filter out duplicate events

**Detection Methods**:
1. **URL exact match**: If same source URL, it's a duplicate
2. **Title similarity**: If title similarity > 85%, it's a duplicate

**Usage**:
```python
from src.processors import is_duplicate, filter_duplicates

# Check single event
is_dup = is_duplicate(new_event, existing_events)

# Filter list of events
unique_events = filter_duplicates(new_events, existing_events)
```

### 2. Monitoring Script (`scripts/run_monitor.py`)

**Purpose**: Main script to collect and process events for all clients

**Process Flow**:
1. Load all active clients from database
2. For each client:
   - Generate search queries (name + keywords)
   - Search using collector
   - Classify each result → EventDTO
   - Score relevance
   - Filter duplicates
   - Save events with score ≥ 0.6
   - Update client.last_checked_at
3. Print summary statistics

**Usage**:
```bash
# Basic usage
python scripts/run_monitor.py

# Custom parameters
python scripts/run_monitor.py --lookback-days 14 --min-relevance 0.7 --max-results 20

# Help
python scripts/run_monitor.py --help
```

**Parameters**:
- `--lookback-days`: How many days to search back (default: 7)
- `--min-relevance`: Minimum score to save (default: 0.6)
- `--max-results`: Max results per query (default: 10)

**Sample Output**:
```
============================================================
CLIENT INTELLIGENCE MONITOR - Starting Scan
============================================================
Time: 2025-10-01 15:30:45
Lookback: 7 days
Min Relevance: 0.6
------------------------------------------------------------

📊 Found 5 active clients to monitor

[1/5] Processing: TechCorp
----------------------------------------
  🔍 Searching with 5 queries...
  📰 Found 45 raw results
  ✅ New events: 8 (filtered 3 duplicates)

[2/5] Processing: DataInc
----------------------------------------
  🔍 Searching with 5 queries...
  📰 Found 32 raw results
  ✅ New events: 5 (filtered 1 duplicates)

...

============================================================
SCAN COMPLETE - Summary
============================================================
✅ Clients monitored: 5
🔍 Queries executed: 25
📰 Raw results found: 180
🆕 New events saved: 34
🔄 Duplicates filtered: 12
📉 Low relevance filtered: 134
============================================================

✨ Scan completed at 2025-10-01 15:35:12
```

## Enhanced Dashboard

### Visual Improvements

#### 1. Top Metrics Row
- **Active Clients**: Total monitored clients
- **Recent Events**: Events in date range
- **Unread Events**: Events not yet reviewed
- **High Priority**: Events with relevance ≥ 0.7

#### 2. Charts Section

**Row 1**:
- **📊 Events by Type**: Bar chart showing distribution by event type
- **📈 Events Timeline**: Area chart showing events over time

**Row 2**:
- **😊 Sentiment Distribution**: Pie chart with color coding:
  - 🟢 Green: Positive
  - 🟡 Yellow: Neutral
  - 🔴 Red: Negative
- **🎯 Relevance Distribution**: Bar chart showing high/medium/low relevance

#### 3. Enhanced Event Cards

Each event card now shows:

**Header**:
- Event type badge with emoji and color
- Sentiment emoji (😊/😐/😞)

**Body**:
- Event title
- Client name, date, source
- Relevance score
- Sentiment score

**Actions**:
- ✓ Mark Read button
- ⭐ Star button
- 📖 Show details (expandable)
- 📝 Add/View Notes (expandable)

**Event Type Colors**:
- 🔵 Funding: Blue
- 🟣 Acquisition: Purple
- 🔴 Leadership: Pink
- 🟠 Product: Orange
- 🟢 Partnership: Green
- 🟢 Financial: Dark green
- 🟡 Award: Yellow
- 🔴 Regulatory: Red
- ⚫ News/Other: Gray

#### 4. Event Filtering

Quick multiselect filter to show/hide event types in the timeline.

## Complete Workflow Example

### 1. Add Clients
```python
# Via UI: Go to "👥 Clients" page and add your clients
# Or via code:
from src.storage import SQLiteStorage
from src.models.client_dto import ClientDTO

storage = SQLiteStorage()
storage.connect()

client = ClientDTO(
    id="uuid-here",
    name="TechCorp",
    industry="SaaS",
    is_active=True
)
storage.create_client(client)
```

### 2. Run Monitoring
```bash
python scripts/run_monitor.py --lookback-days 30
```

This will:
- Search for "TechCorp", "TechCorp funding", "TechCorp acquisition", etc.
- Classify results into events
- Score relevance
- Filter duplicates
- Save high-relevance events

### 3. View Dashboard
Open the Streamlit app and go to "📊 Dashboard":
- See charts showing event distribution
- Review timeline of recent events
- Mark events as read
- Star important events
- Add notes for follow-up

### 4. Advanced Usage

**Custom Event Processing**:
```python
from src.collectors.factory import get_collector
from src.processors import classify_event, update_event_relevance, is_duplicate
from src.storage import SQLiteStorage

# Get collector and storage
collector = get_collector()
storage = SQLiteStorage()
storage.connect()

# Get client
client = storage.get_client_by_name("TechCorp")

# Search
results = collector.search("TechCorp acquisition", max_results=10)

# Process each result
for result in results:
    # Classify
    event = classify_event(result, client)

    # Score relevance
    event = update_event_relevance(event, client)

    # Check duplicates
    existing = storage.get_client_events(client.id)
    if not is_duplicate(event, existing):
        # Save
        if event.relevance_score >= 0.6:
            storage.create_event(event)
```

## Configuration

### Reputable Sources
Edit `src/processors/relevance_scorer.py` to add/remove sources:
```python
REPUTABLE_SOURCES = [
    "TechCrunch", "Reuters", "Bloomberg",
    "The Wall Street Journal", "Financial Times",
    # Add more...
]
```

### Event Type Keywords
Edit `src/processors/event_classifier.py` to customize:
```python
EVENT_TYPE_KEYWORDS = {
    "funding": ["raise", "funding", "series a", ...],
    # Add more keywords...
}
```

### Sentiment Keywords
Edit `src/processors/event_classifier.py`:
```python
POSITIVE_KEYWORDS = ["growth", "success", "wins", ...]
NEGATIVE_KEYWORDS = ["layoff", "decline", "loss", ...]
```

## Best Practices

1. **Run monitoring regularly**: Set up a cron job or scheduled task
   ```bash
   # Every 6 hours
   0 */6 * * * cd /path/to/monitor && python scripts/run_monitor.py
   ```

2. **Adjust relevance threshold**: Start with 0.6, adjust based on results
   - Too many low-quality events? Increase to 0.7 or 0.8
   - Missing important events? Decrease to 0.5

3. **Review and refine**: Check the dashboard daily
   - Mark events as read to track progress
   - Star important events for follow-up
   - Add notes for context

4. **Customize for your industry**: Add industry-specific keywords to classifiers

5. **Monitor rate limits**: Check collector rate limit status in monitoring output

## Troubleshooting

### No events found
- Check if clients are active: `client.is_active = True`
- Lower minimum relevance score
- Increase lookback days
- Verify collector is working

### Too many irrelevant events
- Increase minimum relevance score (0.7 or 0.8)
- Customize relevance scoring factors
- Add negative keywords to filter out noise

### Duplicates not being filtered
- Check if URLs are present in results
- Adjust title similarity threshold in deduplicator
- Review existing events in database

### Dashboard not showing data
- Verify events exist: Check "📰 Events" page
- Check date range filter in sidebar
- Verify relevance filter allows your events through

## Next Steps

1. **Add real collectors**: Replace MockCollector with NewsAPI, Bing, etc.
2. **Implement scheduling**: Use APScheduler for automated monitoring
3. **Add email alerts**: Notify on high-priority events
4. **Export reports**: Generate weekly/monthly summaries
5. **ML-based relevance**: Train model on user feedback
