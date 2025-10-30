# Quick Start Guide 🚀

Get your Client Intelligence Monitor up and running in 3 steps!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Streamlit (web UI)
- SQLAlchemy (database)
- Plotly (charts)
- Pandas (data handling)
- All other dependencies

## Step 2: Seed Sample Data

```bash
python scripts/seed_data.py
```

This creates:
- 5 sample clients (Salesforce, Zoom, Shopify, Atlassian, Stripe)
- 30-40 mock events (funding, acquisitions, product launches, etc.)
- All data is stored in `data/client_intelligence.db` (auto-created)

## Step 3: Launch Dashboard

```bash
streamlit run app.py
```

The dashboard opens automatically at: **http://localhost:8501**

## What You'll See

### Dashboard Page (📊)
- Overview metrics (clients, events, high priority items)
- Events by category chart
- Events timeline chart
- Recent events feed with relevance scores

### Clients Page (👥)
- View all your clients
- Add new clients with custom metadata
- See event counts per client

### Events Page (📰)
- Browse all events with filtering
- Filter by client, date range, category, relevance

### Settings Page (⚙️)
- View system configuration
- Check database stats

## Optional: Verify Setup

Before seeding data, you can test the installation:

```bash
python scripts/test_setup.py
```

This runs tests to verify:
- All modules import correctly
- Database can be created
- Mock collector generates data
- Repository operations work

## Troubleshooting

**Issue: "No module named 'X'"**
- Solution: Run `pip install -r requirements.txt`

**Issue: Dashboard won't start**
- Solution: Make sure Streamlit is installed: `pip install streamlit`

**Issue: No data showing in dashboard**
- Solution: Run the seed script: `python scripts/seed_data.py`

**Issue: Permission error on Windows**
- Solution: Run terminal as Administrator or use a virtual environment

## Next Steps

Once you're up and running:

1. **Add your real clients** via the "👥 Clients" page
2. **Explore the filters** in the sidebar
3. **Mark events as read** to track what you've reviewed
4. **Customize settings** in `config/settings.py`

## Virtual Environment (Recommended)

For a clean installation:

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

**Need Help?** Check the main README.md for full documentation.
