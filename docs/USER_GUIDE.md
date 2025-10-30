# Client Intelligence Monitor - User Guide

Complete guide to using the Client Intelligence Monitor application.

## Table of Contents

1. [What is Client Intelligence Monitor?](#what-is-client-intelligence-monitor)
2. [Installation](#installation)
3. [First Time Setup](#first-time-setup)
4. [Adding Your First Client](#adding-your-first-client)
5. [Running Your First Scan](#running-your-first-scan)
6. [Understanding the Dashboard](#understanding-the-dashboard)
7. [Working with Events](#working-with-events)
8. [Creating Reports](#creating-reports)
9. [Setting Up Automation](#setting-up-automation)
10. [Tips and Tricks](#tips-and-tricks)
11. [FAQ](#faq)

---

## What is Client Intelligence Monitor?

Client Intelligence Monitor is a powerful tool that helps businesses stay informed about their clients by automatically collecting and analyzing news, events, and updates. Think of it as your personal news assistant that:

- **Monitors** your clients for important news and events
- **Classifies** events by type (funding, acquisitions, products, etc.)
- **Scores** events by relevance to your business
- **Alerts** you to important developments
- **Tracks** trends and insights across your portfolio

### Key Features

✅ **Automated Monitoring**: Continuously scans for client news
✅ **Smart Classification**: Automatically categorizes events
✅ **Relevance Scoring**: Prioritizes important information
✅ **Beautiful Dashboard**: Visualize trends and insights
✅ **Email Notifications**: Get alerted to critical events
✅ **Export Reports**: Share insights with your team
✅ **Demo Mode**: Try it with sample data first

### Who Should Use This?

- **Account Managers**: Stay informed about client activities
- **Sales Teams**: Track prospect news and engagement opportunities
- **Customer Success**: Monitor client health indicators
- **Business Development**: Identify partnership opportunities
- **Analysts**: Track market trends and competitive intelligence

---

## Installation

### System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.8 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Storage**: 500MB available space
- **Internet**: Required for news collection

### Step 1: Install Python

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. ✅ **Important**: Check "Add Python to PATH"
4. Click "Install Now"
5. Verify: Open Command Prompt and type `python --version`

**macOS:**
```bash
# Using Homebrew
brew install python3

# Verify installation
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip

# Verify installation
python3 --version
```

### Step 2: Download the Application

**Option A: Download ZIP**
1. Download the application ZIP file
2. Extract to your desired location (e.g., `C:\Client Monitor`)
3. Navigate to the folder in terminal/command prompt

**Option B: Clone from Git**
```bash
git clone <repository-url>
cd client-monitor
```

### Step 3: Install Dependencies

Open terminal/command prompt in the application folder:

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
pip list
```

This will install:
- Streamlit (web interface)
- SQLite (database)
- Requests (API calls)
- And other dependencies

### Step 4: Verify Installation

```bash
# Test the installation
python -m streamlit run app.py

# You should see:
# "You can now view your Streamlit app in your browser."
```

If successful, the application will open in your browser at `http://localhost:8501`

---

## First Time Setup

### Launch the Application

```bash
# Navigate to the application folder
cd "C:\Users\YourName\Client Monitor"

# Start the application
python -m streamlit run app.py
```

The application will open automatically in your default browser.

### Try Demo Mode First (Recommended)

Before adding your own data, try demo mode:

1. **Enable Demo Mode**:
   - Create a file named `.env` in the application folder
   - Add: `DEMO_MODE=true`
   - Save and restart the application

2. **Explore Demo Data**:
   - Dashboard shows sample clients and events
   - Try all features with realistic data
   - See how everything works before committing real data

3. **Disable Demo Mode** when ready:
   - Change `.env` to: `DEMO_MODE=false`
   - Or delete the `.env` file
   - Restart the application

### Configure Settings

1. Navigate to **⚙️ Settings** in the sidebar

2. **General Tab**:
   - Set application mode (Development/Production)
   - Verify database path

3. **API Configuration Tab**:
   - Leave "Use Mock APIs" enabled for now (no cost!)
   - Later: Add real API keys (see API Setup Guide)

4. **Monitoring Tab**:
   - Set default scan time (e.g., 9:00 AM)
   - Set scan frequency (daily recommended)
   - Set minimum relevance score (0.5 recommended)

5. **Notifications Tab** (Optional):
   - Configure SMTP settings for email alerts
   - Set quiet hours

6. **Display Tab**:
   - Set events per page
   - Choose date format
   - Select timezone

7. Click **💾 Save All Settings** at the bottom

---

## Adding Your First Client

### From the Clients Page

1. Click **👥 Clients** in the sidebar

2. Click **➕ Add New Client** button

3. Fill in the form:

   **Required Fields:**
   - **Name**: Company name (e.g., "Acme Corporation")
   - **Industry**: Select from dropdown (e.g., "Technology")

   **Optional Fields:**
   - **Description**: Brief description of the company
   - **Domain**: Website (e.g., "acme.com")
   - **Priority**: low/medium/high (affects scanning)
   - **Tier**: Enterprise/Growth/Startup
   - **Account Owner**: Your name or team member
   - **Keywords**: Add relevant keywords for better matching

4. Click **Add Client**

5. ✅ Client appears in the list!

### Understanding Client Fields

**Name** - The official company name. This is used in news searches, so use the name they're known by publicly.

**Industry** - Helps classify relevant news. Choose the closest match:
- Technology
- Financial Services
- Healthcare
- Manufacturing
- Retail
- Professional Services
- Other

**Priority** - Affects how often the client is scanned:
- **High**: Scanned more frequently, all news captured
- **Medium**: Standard scanning frequency
- **Low**: Less frequent scans, only high-relevance news

**Keywords** - Additional terms to search for:
- Product names
- Executive names
- Alternative company names
- Industry terms
- Example: ["enterprise software", "cloud computing", "John Smith CEO"]

### Best Practices

✅ **Start with 5-10 clients** to test the system
✅ **Use accurate names** as they appear in news
✅ **Add specific keywords** for better results
✅ **Set realistic priorities** (not everything can be high!)
✅ **Include website domains** for better matching

---

## Running Your First Scan

### Manual Scan

1. Go to **🔍 Monitor** page

2. Click **🔄 Scan All Clients** button

3. Watch the progress:
   - Scanning status for each client
   - Events discovered
   - Processing time

4. When complete:
   - View summary statistics
   - Check new events found
   - Review any errors

### Scanning a Single Client

1. Go to **👥 Clients** page

2. Click **View** on the client you want to scan

3. In the client details, click **🔍 Scan for Events**

4. Review the events found

### Understanding Scan Results

**Events Found**: Total number of news items discovered

**New Events**: Events not previously seen

**High Relevance**: Events scored ≥ 0.7 (most important)

**Event Types**: Breakdown by category (funding, product, etc.)

### What Happens During a Scan?

1. **Search**: The system searches for news about the client
2. **Collect**: News articles are collected from various sources
3. **Classify**: Each event is categorized (funding, partnership, etc.)
4. **Score**: Relevance is calculated based on multiple factors
5. **Store**: Events are saved to the database
6. **Deduplicate**: Duplicate events are filtered out
7. **Notify**: Alerts are sent based on your notification rules

---

## Understanding the Dashboard

### 📊 Dashboard Overview

The dashboard is your command center. It shows:

**Top Metrics** (at a glance):
- Total Clients
- Active Monitoring
- Total Events
- High Relevance Events
- Events This Week
- Average Relevance

**Event Timeline**
- Visual timeline of events over the past 30 days
- See activity spikes and patterns
- Hover for details

**Events by Type**
- Pie chart showing distribution
- Funding, Acquisitions, Products, Partnerships, etc.

**Top Clients by Activity**
- Bar chart of most active clients
- Helps identify which clients have the most news

**Recent High-Relevance Events**
- List of important events from the past 7 days
- Quick access to what matters most

### Interpreting the Data

**Relevance Score (0-1.0)**:
- **0.8-1.0**: Critical - Review immediately
- **0.6-0.8**: Important - Review soon
- **0.4-0.6**: Moderate - Review when time permits
- **0.2-0.4**: Low - Optional review
- **0.0-0.2**: Very Low - Can likely ignore

**Event Types**:
- **💰 Funding**: Investment rounds, capital raises
- **🤝 Acquisition**: M&A activity, acquisitions
- **👤 Leadership**: C-level changes, hires
- **🚀 Product**: New products, launches, updates
- **🤝 Partnership**: Strategic partnerships, alliances
- **💵 Financial**: Earnings, financial results
- **🏆 Award**: Awards, recognitions, rankings
- **⚖️ Regulatory**: Compliance, regulations
- **📰 News**: General news, press releases

**Sentiment**:
- **Positive**: Good news (earnings, awards, growth)
- **Neutral**: Informational (appointments, announcements)
- **Negative**: Challenges (lawsuits, losses, layoffs)

---

## Working with Events

### Viewing Events

**All Events Page** (📰 Events):
1. Shows all collected events
2. Filter by:
   - Client
   - Event Type
   - Date Range
   - Relevance Score
   - Status
3. Search by keywords
4. Sort by date or relevance

**Client-Specific Events**:
1. Go to **👥 Clients**
2. Click **View** on a client
3. See only that client's events

### Event Details

Click on any event to see:
- **Full Title and Summary**
- **Source and URL**: Click to read the full article
- **Classification**: Event type and confidence
- **Relevance Score**: Why it matters
- **Sentiment Analysis**: Positive/Neutral/Negative
- **Tags**: Automatically generated keywords
- **Discovery Info**: When and how it was found

### Managing Events

**Mark as Read**:
- Change status to "reviewed"
- Helps track which events you've seen

**Add Notes**:
- Add your own comments
- Document follow-up actions
- Share context with team

**Change Status**:
- **New**: Just discovered
- **Reviewed**: You've read it
- **Archived**: No longer relevant
- **Flagged**: Needs attention

**Export Events**:
1. Apply filters to find events you want
2. Click **Export** button
3. Choose format (CSV or JSON)
4. Save to your computer

### Event Actions

**Share Event**:
- Copy URL to share with team
- Export single event
- Email directly (if configured)

**Follow Up**:
- Add to your CRM
- Schedule meeting
- Send to client

**Track**:
- Monitor for updates
- Set reminder
- Add to report

---

## Creating Reports

### Quick Reports

**Dashboard Report**:
1. Navigate to **📊 Dashboard**
2. Take a screenshot or use browser print (Ctrl+P)
3. Save as PDF

**Client Report**:
1. Go to **👥 Clients**
2. Click **View** on a client
3. See client-specific statistics
4. Export events for that client

### Custom Reports

**Event Export**:
1. Go to **📰 Events**
2. Apply filters:
   - Select date range (e.g., last 30 days)
   - Choose event types
   - Set minimum relevance
3. Click **📥 Export**
4. Open in Excel/Google Sheets for analysis

**Insights Report**:
1. Go to **📈 Insights**
2. View trends and patterns
3. Export charts and data
4. Create presentation

### Report Best Practices

✅ **Weekly Summary**: Export high-relevance events from past week
✅ **Monthly Review**: Trends and patterns across all clients
✅ **Client-Specific**: When preparing for client meetings
✅ **Quarterly Analysis**: Long-term trends and insights
✅ **Executive Summary**: Top 10 most important events

---

## Setting Up Automation

### Scheduled Scans

**Enable Automatic Scanning**:

1. Go to **⚙️ Settings** → **Monitoring Tab**

2. Configure:
   - **Scan Time**: When to run (e.g., 9:00 AM)
   - **Frequency**: daily/twice daily
   - **Batch Size**: How many clients per scan

3. Click **💾 Save All Settings**

4. Verify automation is running:
   - Check **🔍 Monitor** page
   - View scan history
   - Check for recent scans

### Email Notifications

**Set Up Email Alerts**:

1. Go to **⚙️ Settings** → **Notifications Tab**

2. Configure SMTP:
   - **Server**: smtp.gmail.com (for Gmail)
   - **Port**: 587
   - **Username**: your-email@gmail.com
   - **Password**: App-specific password
   - **Use TLS**: ✅ Enabled

3. Click **📧 Send Test Email** to verify

4. Set up notification rules (see Notification Rules below)

### Notification Rules

**Create a Rule**:

1. Go to **🔔 Notifications** page

2. Click **➕ Add Rule**

3. Configure:
   - **Name**: "High Priority Funding Events"
   - **Event Types**: Select "Funding"
   - **Min Relevance**: 0.8
   - **Clients**: Select specific clients or "All"
   - **Keywords**: Optional additional filters
   - **Recipients**: Email addresses
   - **Frequency**: immediate/daily digest/weekly

4. Click **Save Rule**

5. **Activate** the rule

**Example Rules**:

```
Rule 1: Critical Alerts
- Event Types: Funding, Acquisition, Leadership
- Min Relevance: 0.9
- Frequency: Immediate
- Recipients: team@company.com

Rule 2: Daily Digest
- Event Types: All
- Min Relevance: 0.6
- Frequency: Daily (9 AM)
- Recipients: managers@company.com

Rule 3: Client-Specific
- Clients: VIP Client 1, VIP Client 2
- Event Types: All
- Min Relevance: 0.5
- Frequency: Immediate
- Recipients: account-manager@company.com
```

---

## Tips and Tricks

### Optimization Tips

**Performance**:
- Start with 10-20 clients, scale gradually
- Use "High" priority sparingly
- Keep keywords specific and relevant
- Archive old events regularly

**Accuracy**:
- Use official company names in news
- Add product/brand names as keywords
- Review and refine relevance scores
- Provide feedback on classifications

**Workflow**:
- Check dashboard daily (5 minutes)
- Review high-relevance events immediately
- Process moderate-relevance weekly
- Archive low-relevance monthly

### Keyboard Shortcuts

- `Ctrl+K`: Quick search (when implemented)
- `Ctrl+/`: Show help
- `Ctrl+R`: Refresh page
- `Ctrl+P`: Print/Save as PDF

### Search Tips

**In Global Search** (🔍 Search):
- Use quotes for exact phrases: `"Series A funding"`
- Use AND for multiple terms: `acquisition AND technology`
- Search by company name, event type, or keywords
- Minimum 2 characters required

**Advanced Filters**:
- Combine multiple filters for precision
- Use date range for specific periods
- Sort by relevance to find important items
- Save common searches for quick access

### Data Management

**Backup Your Data**:
1. Go to **⚙️ Settings** → **General Tab**
2. Click **💾 Backup Database**
3. Save the .db file somewhere safe
4. Do this weekly or before major changes

**Clean Up Old Data**:
1. Go to **📰 Events**
2. Filter by old dates (e.g., > 1 year)
3. Archive irrelevant events
4. Keeps database performant

**Export for Analysis**:
1. Export events to CSV
2. Open in Excel/Google Sheets
3. Create pivot tables
4. Generate custom charts

---

## FAQ

### General Questions

**Q: Is my data secure?**
A: Yes! All data is stored locally on your computer in a SQLite database. Nothing is sent to external servers except for news collection APIs (which only send search queries, not your data).

**Q: Does this work offline?**
A: The interface works offline, but collecting news requires internet. You can view existing data without internet.

**Q: How much does it cost?**
A: The application is free! API costs depend on usage:
- Mock APIs: $0 (for testing)
- Google Custom Search: 100 free queries/day, then ~$5/1000 queries
- NewsAPI: Free tier available, paid plans from $449/month

**Q: Can multiple people use it?**
A: Currently single-user. For multi-user, deploy on a server and share the URL.

### Technical Questions

**Q: Which database does it use?**
A: SQLite - a lightweight, file-based database included with Python. No separate installation needed!

**Q: Can I import existing clients?**
A: Yes! Create a CSV with columns: name, industry, domain, priority. Then import via scripts/import.py (see Developer Guide).

**Q: How do I update the application?**
A: Download the new version, replace files (keep your .db database), run `pip install -r requirements.txt` again.

**Q: What if a scan fails?**
A: Check the error message. Common issues:
- Network connection
- API rate limits
- Invalid API keys (if using real APIs)

### Usage Questions

**Q: How many clients can I monitor?**
A: Recommended 50-100 clients for optimal performance. Can handle more, but scans take longer.

**Q: How often should I run scans?**
A: Daily for most use cases. Twice daily for high-priority clients. Weekly for low-priority.

**Q: What if I get too many irrelevant events?**
A: 1) Increase minimum relevance score in settings
   2) Refine client keywords
   3) Use more specific industry categories
   4) Review and flag irrelevant events to improve scoring

**Q: Can I customize event types?**
A: Currently predefined types. Custom types require code changes (see Developer Guide).

**Q: How do I share reports with my team?**
A: 1) Export to CSV and share file
   2) Take screenshots of dashboard
   3) Print to PDF
   4) Deploy on shared server for direct access

### Troubleshooting

**Q: Application won't start**
```bash
# Check Python installation
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Try running directly
streamlit run app.py
```

**Q: Database errors**
```bash
# Backup and reset database
python scripts/reset_database.py

# Or manually delete client_intelligence.db and restart
```

**Q: API errors**
- Verify API keys are correct
- Check rate limits haven't been exceeded
- Test with Mock APIs first
- See logs for detailed error messages

**Q: Slow performance**
- Archive old events
- Reduce number of active clients
- Increase scan frequency (less frequent = faster)
- Check database size (backup and optimize if > 100MB)

---

## Getting Help

### Resources

- **Documentation**: Check `docs/` folder for detailed guides
- **Examples**: See `docs/EXAMPLES.md` for common scenarios
- **API Setup**: See `docs/API_SETUP.md` for API configuration
- **Developer Guide**: See `docs/DEVELOPER_GUIDE.md` for technical details

### Support

- **GitHub Issues**: Report bugs and request features
- **Email**: support@example.com
- **Community**: Join our Slack/Discord

### Contributing

We welcome contributions! See `docs/DEVELOPER_GUIDE.md` for:
- Setting up development environment
- Code style guidelines
- How to submit pull requests
- Feature request process

---

**Last Updated**: 2025-10-15
**Version**: 1.0.0
**Need Help?** Check the FAQ above or refer to other documentation in the `docs/` folder.
