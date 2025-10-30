

# Database Management Guide

## Overview

The Client Intelligence Monitor now has a complete SQLite database layer with a visual management interface. You can **add clients, view them, add events, and query them - all through the UI without writing SQL!**

## Quick Start

### Step 1: Open the Dashboard

```bash
# If not already running
python -m streamlit run app.py
```

Open http://localhost:8501

### Step 2: Check Database Status

Look at the **sidebar** - you'll see:
```
📊 Database Status
Clients: 0
Events: 0
New Events: 0
```

### Step 3: Navigate to Database Page

Click **"🗄️ Database"** in the navigation menu.

## Database Page - 4 Tabs

### Tab 1: Database Status 📊

**What You See:**
- Database file path and size
- Tables created (clients, events, search_cache)
- Statistics dashboard
- Management buttons

**Actions:**
1. **Initialize Database** - Create tables (auto-runs on first startup)
2. **Reset Database** - Clear everything and start fresh
3. **Refresh Stats** - Update displayed statistics

**When to Use:**
- First time setup
- Check database health
- Clear all data for testing

### Tab 2: Clients 👥

**What You See:**
- Table of all clients with:
  - Name, Industry, Priority
  - Number of events per client
  - Last checked timestamp
  - Active status
- Client details viewer

**Add a Client:**
1. Click **"➕ Add Sample Client"**
2. A new client is created instantly
3. Table refreshes automatically

**View Client Details:**
1. Select client from dropdown
2. See full information:
   - Contact details
   - Keywords
   - Statistics
   - Events breakdown

**Example Workflow:**
```
1. Click "Add Sample Client" 3 times
2. You now have 3 sample clients
3. Select "Sample Co 1" from dropdown
4. View its statistics and details
```

### Tab 3: Events 📰

**What You See:**
- Event cards (expandable)
- Color-coded by type:
  - 🟢 Funding
  - 🔵 Acquisition
  - 🟡 Leadership
  - 🟣 Product
  - ⚪ News
- Relevance indicators (🟢🟡🔴)

**Filter Events:**
1. **By Client:** Select from dropdown
2. **By Date:** Use "Days Back" slider (1-90 days)
3. **By Relevance:** Set minimum score (0.0-1.0)

**View Event Details:**
1. Click on any event card to expand
2. See:
   - Full summary
   - Source link
   - Published date
   - Tags
   - Current status

**Update Event Status:**
1. Expand an event
2. Click one of:
   - "Mark Reviewed"
   - "Mark Actioned"
   - "Archive"
3. Status updates instantly

**Example Workflow:**
```
1. Filter by "Sample Co 1"
2. Set "Days Back" to 30
3. Set "Min Relevance" to 0.5
4. Expand a funding event
5. Click "Mark Reviewed"
6. Event status changes to "reviewed"
```

### Tab 4: Cache 💾

**What You See:**
- Cache statistics
- Cache validity rate
- Management actions

**Actions:**
1. **Clear Expired Cache** - Remove outdated entries
2. **Clear All Cache** - Delete everything
3. **Add Sample Cache** - Create test entry

**When to Use:**
- Free up space
- Test cache functionality
- Monitor cache performance

## Complete Walkthrough

### Scenario: Set Up and Test Database

**Step 1: Initialize Database**
```
1. Go to "Database Status" tab
2. Click "Initialize Database"
3. See success message
4. Tables are created
```

**Step 2: Add Clients**
```
1. Go to "Clients" tab
2. Click "Add Sample Client" 3 times
3. Table shows 3 clients
4. Sidebar shows "Clients: 3"
```

**Step 3: Add Events** (via Database Status)
```
Option A: Use setup script
- Run: python scripts/setup_db_new.py
- Answer 'y' to seed data
- 15 events created

Option B: Add manually (future feature)
- Use "Add Sample Event" button
```

**Step 4: View and Filter Events**
```
1. Go to "Events" tab
2. Select a client from filter
3. See events for that client
4. Expand an event to see details
```

**Step 5: Update Event Status**
```
1. Expand an event
2. Click "Mark Reviewed"
3. Event status changes
4. Click "Archive" to archive it
```

**Step 6: View Client Statistics**
```
1. Go to "Clients" tab
2. Select a client from dropdown
3. See:
   - Total events
   - Average relevance
   - Events by type
```

## Sidebar Database Status

The sidebar **always shows** current database stats:

```
📊 Database Status
Clients: 5          ← Active clients
Events: 15          ← Total events
New Events: 12      ← Events not reviewed

💾 Cache: 3/5 valid ← Cache entries
```

**Real-time Updates:**
- Add a client → Counter updates
- Add an event → Counter updates
- Mark event as reviewed → "New Events" decreases

## Common Tasks

### Task: Add a New Client

**Method 1: Via UI (Sample)**
```
1. Database page → Clients tab
2. Click "Add Sample Client"
3. Client created instantly
```

**Method 2: Via Script (Batch)**
```bash
python scripts/setup_db_new.py
# Follow prompts to add multiple clients
```

### Task: Find Events for a Client

```
1. Database page → Events tab
2. "Filter by Client" dropdown
3. Select client name
4. See all their events
```

### Task: Find High-Priority Events

```
1. Database page → Events tab
2. Set "Min Relevance" to 0.7
3. See only high-priority events (🟢)
```

### Task: Archive Old Events

```
1. Database page → Events tab
2. Set "Days Back" to 90
3. Expand old events
4. Click "Archive" on each
```

### Task: Reset Database

```
1. Database page → Database Status tab
2. Click "Reset Database"
3. Click again to confirm
4. All data cleared
5. Database recreated
```

### Task: Check Database Size

```
1. Database page → Database Status tab
2. Look at "File Size" metric
3. See size in MB
```

## Event Type Colors

| Color | Type | Example |
|-------|------|---------|
| 🟢 | Funding | "Company raises $50M Series B" |
| 🔵 | Acquisition | "Company acquires CompetitorCo" |
| 🟡 | Leadership | "Company appoints new CEO" |
| 🟣 | Product | "Company launches AI Platform" |
| ⚪ | News | "Company featured in TechCrunch" |
| ⚫ | Other | "Company announces partnership" |

## Relevance Indicators

| Indicator | Score Range | Meaning |
|-----------|-------------|---------|
| 🟢 | 0.7 - 1.0 | High relevance |
| 🟡 | 0.4 - 0.6 | Medium relevance |
| 🔴 | 0.0 - 0.3 | Low relevance |

## Status Workflow

```
new → reviewed → actioned → archived
 ↓        ↓         ↓          ↓
Just     You've    You've     Done/
found    seen it   acted      closed
```

## Tips & Tricks

### Tip 1: Quick Testing
```
1. Reset database
2. Add 3 sample clients
3. Run seed script for events
4. Test filtering and status updates
```

### Tip 2: Monitor Performance
```
1. Check database size regularly
2. Clear expired cache periodically
3. Archive old events
```

### Tip 3: Find Actionable Items
```
1. Events tab
2. Filter: "Min Relevance" = 0.7
3. Status: "new"
4. These need your attention!
```

### Tip 4: Client Health Check
```
1. Clients tab
2. Select each client
3. Check "Avg Relevance"
4. Low score? May need attention
```

## Troubleshooting

### Issue: "Database not initialized"

**Solution:**
```
1. Go to Database page
2. Database Status tab
3. Click "Initialize Database"
```

### Issue: No events showing

**Possible causes:**
1. No events in database
   - Solution: Run setup script to seed data
2. Filters too restrictive
   - Solution: Lower "Min Relevance" to 0.0
   - Solution: Increase "Days Back" to 90

### Issue: Can't see new client

**Solution:**
```
1. Check "Active" status in table
2. Look in sidebar - counter should update
3. Refresh page if needed
```

### Issue: Events not updating

**Solution:**
```
1. Database page → refresh tab
2. Or click any action button
3. Page auto-refreshes on changes
```

## Database Files

**Location:**
```
C:\Users\bwall\Desktop\Client Monitor\data\
└── client_intelligence.db
```

**Backup:**
```bash
# Copy database file
cp data/client_intelligence.db data/backup_YYYYMMDD.db
```

**Restore:**
```bash
# Replace with backup
cp data/backup_YYYYMMDD.db data/client_intelligence.db
```

## Integration with Other Pages

The database is integrated throughout the app:

**Dashboard Page:**
- Shows events from database
- Filters work with database queries

**Clients Page:**
- Displays clients from database
- Add clients through forms

**Events Page:**
- Shows events from database
- Advanced filtering

**Sidebar:**
- Always shows database stats
- Updates in real-time

## Next Steps

Now that the database is working:

1. ✅ **Add your real clients**
   - Use database page or forms
   - Add their keywords and details

2. ✅ **Collect events**
   - Set up collectors (Phase 3)
   - Events populate automatically

3. ✅ **Review and action**
   - Check new events daily
   - Mark as reviewed/actioned
   - Archive when done

4. ✅ **Monitor trends**
   - Check client statistics
   - Look at events by type
   - Track relevance scores

## Summary

**You now have:**
- ✅ Visual database management
- ✅ Add/view clients through UI
- ✅ Add/view events through UI
- ✅ Filter and search capabilities
- ✅ Status tracking workflow
- ✅ Real-time statistics
- ✅ No SQL required!

**Everything is visual and interactive!** 🎉

Open http://localhost:8501 and click "🗄️ Database" to start managing your data!
