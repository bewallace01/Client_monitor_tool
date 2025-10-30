# Scripts Directory

Utility scripts for Client Intelligence Monitor.

## Demo Data Seeder

### `seed_demo_data.py`

Creates realistic demo data for demonstration purposes.

**Features:**
- 15-20 sample clients across various industries
- 50-100 sample events distributed over the last 30 days
- Realistic event types, relevance scores, and metadata
- Events distributed by type: funding, acquisitions, leadership changes, product launches, etc.

### Usage

**Seed demo data (default: 18 clients, ~75 events):**
```bash
python scripts/seed_demo_data.py
```

**Customize the amount of data:**
```bash
# Create 15 clients with ~50 events
python scripts/seed_demo_data.py --clients 15 --events 50

# Create 20 clients (maximum) with ~100 events
python scripts/seed_demo_data.py --clients 20 --events 100
```

**Clear existing demo data:**
```bash
python scripts/seed_demo_data.py --clear
```

### Demo Mode

To enable the demo mode banner in the UI:

**Windows:**
```cmd
set DEMO_MODE=true
python -m streamlit run app.py
```

**Linux/Mac:**
```bash
export DEMO_MODE=true
python -m streamlit run app.py
```

**One-liner:**
```bash
DEMO_MODE=true python -m streamlit run app.py
```

### Data Structure

**Sample Companies:**
- 20 pre-configured companies across 10+ industries
- Realistic company details (domain, description, tier, account owner)
- Industry keywords for accurate event matching

**Event Types Distribution:**
- Product launches/updates: 25%
- Partnerships: 20%
- Funding news: 15%
- Leadership changes: 15%
- Financial results: 10%
- Acquisitions: 8%
- Awards/recognition: 5%
- Regulatory/compliance: 2%

**Event Details:**
- Realistic titles and summaries generated from templates
- Relevance scores: 0.60-0.99 (based on event type and recency)
- Sentiment scores with appropriate emotional valence
- Events distributed over last 30 days
- Some events marked as read (older events more likely)
- 10% chance of being starred

### Examples

**Quick demo setup:**
```bash
# 1. Seed demo data
python scripts/seed_demo_data.py

# 2. Start in demo mode
set DEMO_MODE=true
python -m streamlit run app.py
```

**Large demo dataset:**
```bash
# Create maximum demo data for presentations
python scripts/seed_demo_data.py --clients 20 --events 100
```

**Reset demo environment:**
```bash
# Clear demo data and start fresh
python scripts/seed_demo_data.py --clear
python scripts/seed_demo_data.py --clients 18 --events 75
```

### Notes

- All demo data is prefixed with `demo_` in the database
- Demo clients and events can be safely deleted without affecting production data
- The seeder uses realistic company names and event templates
- Events are automatically distributed across clients and time periods
- Relevance and sentiment scores are calculated based on event type
