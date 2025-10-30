# Search Test Page Guide

## Overview

The **Search Test Page** is an interactive interface for testing the complete search → display → save workflow using the Mock Collector. It provides a polished, production-ready UI for searching events and saving them to your database.

## Features

### 🎨 Visual Design

- **Color-coded relevance borders** (green/orange/red)
- **Auto-detected event types** (💰 Funding, 🤝 Acquisition, 👤 Leadership, etc.)
- **Sentiment indicators** (😊 positive, 😐 neutral, 😞 negative)
- **Real-time search stats** (results count, search time, rate limits)
- **Clean card-based layout** for results

### 🔍 Search Modes

#### 1. Custom Query Mode
Type any search term to find relevant news:
- Example: "Tesla funding"
- Example: "Microsoft acquisition"
- Example: "Google CEO appointment"

**Features:**
- Free-form text input
- 10 quick-example buttons
- Keyword-based result filtering

#### 2. Select Client Mode
Choose a client from your database to search for their news:
- Automatically uses client name as query
- Can save results directly to that client
- Perfect for monitoring specific companies

### 📊 Result Display

Each result shows:

1. **Title** - Full article headline
2. **Metadata Bar**:
   - 📰 Source (TechCrunch, Reuters, Bloomberg, etc.)
   - 🗓️ Published date/time
   - Event type badge (auto-detected)
   - Sentiment emoji (auto-detected)
3. **Relevance Score** - Color-coded percentage badge
4. **Description** - Article summary
5. **Action Buttons**:
   - 🔗 Read Full Article (opens URL)
   - 💾 Save as Event (saves to database)
   - 🔍 View Raw Data (shows API response)

### 📈 Search Stats Sidebar

Shows real-time information:
- **Query** - What you searched for
- **Collector** - Which collector was used (MOCK)
- **Rate Limit** - Requests remaining (simulated)
- **Results Found** - Total count
- **Search Time** - Latency in seconds
- **Category Breakdown** - Distribution by event type

## Quick Start

### 1. Launch the App

```bash
python -m streamlit run app.py
```

### 2. Navigate to Search Test

Click **"🔎 Search Test"** in the sidebar navigation.

### 3. Try a Search

**Option A: Custom Query**
1. Select "Custom Query" mode
2. Type "Tesla funding" in the search box
3. Click "🔍 Search Now"
4. Wait ~0.5 seconds for results
5. Review the results with color-coded relevance

**Option B: Select Client**
1. Select "Select Client" mode
2. Choose a client from the dropdown
3. Click "🔍 Search Now"
4. Results appear for that client
5. Click "💾 Save as Event" to add to database

### 4. Explore Results

- **Check the relevance score** - Green (70%+) is most relevant
- **Review the event type** - Automatically detected from content
- **See the sentiment** - 😊 positive, 😐 neutral, 😞 negative
- **Read the description** - Summary of the article
- **Save to database** - One-click save for client mode

## Auto-Detection Features

### Event Type Detection

The system automatically categorizes results:

| Event Type | Keywords | Badge |
|------------|----------|-------|
| Funding | funding, raised, investment, series | 💰 Funding |
| Acquisition | acquisition, acquires, merger, buyout | 🤝 Acquisition |
| Leadership | ceo, cto, cfo, executive, appoint | 👤 Leadership |
| Product | product, launch, release, unveil | 🚀 Product |
| Partnership | partnership, partner, collaboration | 🤝 Partnership |
| Financial | earnings, revenue, financial, profit | 💵 Financial |
| Award | award, recognition, winner | 🏆 Award |
| General | (default if no keywords match) | 📰 News |

### Sentiment Detection

Analyzes title and description for sentiment:

**Positive Keywords:**
- raises, secures, wins, launches, grows, expands
- appoints, announces, strong, record

**Negative Keywords:**
- loses, fails, cuts, declines, departure
- layoffs, delays, misses

**Result:**
- More positive keywords → 😊 positive
- More negative keywords → 😞 negative
- Equal or neutral → 😐 neutral

### Relevance Scoring

Calculates how well the result matches your query:

1. **Extract keywords** from search query
2. **Count matches** in title and description
3. **Normalize** by number of query words
4. **Add variance** for realism (±10-30%)
5. **Cap at 100%**

**Color Coding:**
- 🟢 Green (70%+) - Highly relevant
- 🟠 Orange (40-69%) - Moderately relevant
- 🔴 Red (<40%) - Low relevance

## Using the Interface

### Search Parameters

**Max Results** (1-20)
- How many results to return
- Default: 5
- More results = longer search time

**Lookback Days** (7-90)
- How far back to search
- Default: 30 days
- Affects the date range of results

### Quick Example Buttons

Click any example to instantly populate the search:
- 🚀 Tesla funding
- 🤝 Microsoft acquisition
- 👤 Google CEO appointment
- 🚀 Apple product launch
- 🤝 Amazon partnership

### Saving Results

**In "Select Client" Mode:**
1. Choose a client from dropdown
2. Search for news
3. Click "💾 Save as Event" on any result
4. Event is saved to that client's timeline
5. Success message confirms save

**In "Custom Query" Mode:**
- Saving is disabled (no client selected)
- Button shows "💾 Save to Client..."
- Switch to "Select Client" mode to enable saving

## What's Real vs. Fake

### Real (Functional)

✅ **Search interface** - Fully functional
✅ **Result display** - Production-ready UI
✅ **Event detection** - Working algorithms
✅ **Sentiment analysis** - Active classification
✅ **Relevance scoring** - Calculated per result
✅ **Save to database** - Persists events
✅ **Search timing** - Accurate latency measurement

### Fake (Simulated)

🎭 **Article content** - Generated by mock collector
🎭 **URLs** - Point to example.com
🎭 **Rate limits** - Simulated, not enforced
🎭 **News sources** - Real names, fake content
🎭 **Published dates** - Random within range

## Example Workflow

### Complete Search-to-Save Flow

1. **Navigate to Search Test page**
2. **Select "Select Client" mode**
3. **Choose "TechCorp" from dropdown**
4. **Set lookback to 30 days**
5. **Set max results to 10**
6. **Click "🔍 Search Now"**
7. **Wait ~0.5 seconds** (simulated API latency)
8. **Review 10 results** in card format
9. **Check relevance scores** (green/orange/red borders)
10. **Read descriptions** to understand content
11. **Click "💾 Save as Event"** on 3 relevant results
12. **See success messages** confirming saves
13. **Navigate to "📰 Events" page** to see saved events
14. **Verify events** appear in TechCorp's timeline

## Integration with Database

### Event Data Saved

When you click "💾 Save as Event", the system creates:

```python
EventDTO(
    client_id="<selected_client_id>",
    title="<result_title>",
    summary="<result_description>",
    source_name="<result_source>",
    source_url="<result_url>",
    published_date="<result_published_at>",
    discovered_date="<now>",
    event_type="<auto_detected>",  # funding, acquisition, etc.
    sentiment="<auto_detected>",   # positive, neutral, negative
    status="new",
    tags=[],
    metadata={"<raw_api_data>"}
)
```

### Viewing Saved Events

After saving, you can view events in:

1. **📊 Dashboard** - Recent events feed
2. **📰 Events** - Full events list with filters
3. **🗄️ Database** - Events tab with management

## Tips & Best Practices

### For Testing

1. **Start with quick examples** - Use the sample query buttons
2. **Try different modes** - Test both custom and client modes
3. **Vary the parameters** - Change lookback and max results
4. **Check all features** - Test relevance, sentiment, detection
5. **Save some results** - Verify database integration

### For Development

1. **Use this page first** - Before integrating real APIs
2. **Test edge cases** - Empty results, long queries, etc.
3. **Validate UI/UX** - Make sure design meets needs
4. **Check performance** - Ensure acceptable latency
5. **Verify data flow** - Confirm saves work correctly

### For Demo

1. **Show the workflow** - Search → Display → Save
2. **Highlight auto-detection** - Event type and sentiment
3. **Emphasize zero-cost** - Mock collector is free
4. **Compare to real APIs** - Similar interface, no charges
5. **Demonstrate value** - Full functionality without investment

## Troubleshooting

### No Results Returned

**Possible causes:**
- Date range too narrow (increase lookback days)
- Query too specific (try broader terms)
- Max results set to 1 (increase max results)

**Solution:** Adjust search parameters and try again

### Can't Save Events

**Possible cause:** Using "Custom Query" mode

**Solution:** Switch to "Select Client" mode and choose a client

### Slow Search

**Expected behavior:** The mock collector intentionally adds 0.3-0.8 second delays to simulate real API latency.

**This is normal!** Real APIs will have similar latency.

### Clients Not Loading

**Possible cause:** Database not initialized or no clients added

**Solution:**
1. Go to "👥 Clients" page
2. Add some clients
3. Return to Search Test page

## Comparison to Collector Test Page

| Feature | Search Test | Collector Test |
|---------|-------------|----------------|
| **Purpose** | End-to-end workflow | Technical testing |
| **UI Style** | Production-ready | Developer-focused |
| **Search Mode** | Custom + Client | Custom only |
| **Result Display** | Rich cards | Simple list |
| **Auto-Detection** | ✅ Yes | ❌ No |
| **Save to DB** | ✅ Yes | ❌ No |
| **Stats Sidebar** | ✅ Yes | ❌ No |
| **Best For** | Demos, testing | API debugging |

## Summary

The Search Test page provides:

✅ **Complete workflow testing** - Search, display, save
✅ **Production-ready UI** - Polished visual design
✅ **Intelligent features** - Auto-detection and scoring
✅ **Zero-cost operation** - Uses mock collector
✅ **Database integration** - Save events to clients
✅ **Real-time feedback** - Stats and timing info

**Use this page to test your entire client monitoring workflow without spending a penny on API calls!**
