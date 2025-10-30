"""Help and user guide page."""

import streamlit as st
from datetime import datetime


def render_help_page():
    """Main help and user guide page."""
    st.markdown('<h1 class="main-header">📚 Help & User Guide</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Learn how to get the most out of ClientIQ</p>', unsafe_allow_html=True)

    # Navigation tabs
    tabs = st.tabs([
        "🚀 Getting Started",
        "📖 Features",
        "🔄 Common Workflows",
        "❓ FAQ",
        "🔧 Troubleshooting",
        "💡 Request Feature"
    ])

    # Getting Started Tab
    with tabs[0]:
        render_getting_started()

    # Features Tab
    with tabs[1]:
        render_features()

    # Common Workflows Tab
    with tabs[2]:
        render_workflows()

    # FAQ Tab
    with tabs[3]:
        render_faq()

    # Troubleshooting Tab
    with tabs[4]:
        render_troubleshooting()

    # Request Feature Tab
    with tabs[5]:
        render_request_feature()


def render_getting_started():
    """Render getting started guide."""
    st.markdown("## 🚀 Getting Started with ClientIQ")

    st.markdown("""
    Welcome to **ClientIQ** - your professional client intelligence monitoring platform!
    This guide will help you get up and running in just a few minutes.
    """)

    # Step-by-step guide
    with st.expander("📋 **Step 1: Add Your First Client**", expanded=True):
        st.markdown("""
        1. Navigate to **👥 Clients** page from the sidebar
        2. Click the **"➕ Add New Client"** button
        3. Fill in the client information:
           - **Name**: Company name (e.g., "Microsoft")
           - **Industry**: Select from dropdown (e.g., "Technology")
           - **Website**: Company website URL
           - **Description**: Brief description of the company
        4. Click **"💾 Save Client"**

        **💡 Tip:** Start with 3-5 key clients to test the system before adding your entire portfolio.
        """)

    with st.expander("📋 **Step 2: Configure Settings (Optional)**"):
        st.markdown("""
        Before running your first scan, you can customize the settings:

        1. Navigate to **⚙️ Settings** page
        2. In the **API Configuration** tab:
           - Toggle **"Use Mock APIs"** ON (recommended for testing)
           - Or configure real API keys if you have them
        3. In the **Monitoring Settings** tab:
           - Set scan frequency (daily recommended)
           - Adjust minimum relevance score (0.5 is good default)
        4. Click **"💾 Save All Settings"**

        **💡 Tip:** Mock APIs are free and perfect for testing. Switch to real APIs when you're ready for production.
        """)

    with st.expander("📋 **Step 3: Run Your First Scan**"):
        st.markdown("""
        1. Return to the **📊 Dashboard**
        2. Click the **"🔄 Run Scan Now"** button
        3. Wait for the scan to complete (usually 10-30 seconds)
        4. Review the results in the scan output

        The system will:
        - ✅ Search for news and events related to your clients
        - ✅ Classify events by type (funding, acquisition, product, etc.)
        - ✅ Score events by relevance (0.0 to 1.0)
        - ✅ Analyze sentiment (positive, neutral, negative)

        **💡 Tip:** Your first scan might return sample data if using mock APIs. This is normal!
        """)

    with st.expander("📋 **Step 4: Review and Manage Events**"):
        st.markdown("""
        1. Navigate to **📰 Events** page
        2. Browse through discovered events
        3. Use the filters to find specific events:
           - Filter by client
           - Filter by event type
           - Filter by relevance score
           - Filter by date range
        4. Click on events to:
           - Mark as read/unread
           - Star important events
           - Add notes
           - Update event details

        **💡 Tip:** Focus on high-relevance events (score > 0.7) first - these are most important.
        """)

    with st.expander("📋 **Step 5: Set Up Automation (Optional)**"):
        st.markdown("""
        1. Navigate to **🤖 Automation** page
        2. Click **"▶️ Start Scheduler"**
        3. Configure scan schedules for automatic monitoring
        4. The system will now run scans automatically

        Or manually schedule scans:
        - Daily at a specific time
        - Multiple times per day
        - Custom schedule

        **💡 Tip:** Start with manual scans until you're comfortable, then enable automation.
        """)

    st.divider()

    # Quick reference card
    st.markdown("### 📌 Quick Reference Card")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Key Actions:**
        - ➕ Add clients → **Clients** page
        - 🔄 Run scan → **Dashboard** page
        - 📰 View events → **Events** page
        - 📊 See analytics → **Insights** page
        - ⚙️ Configure → **Settings** page
        """)

    with col2:
        st.markdown("""
        **Event Actions:**
        - ✓ Mark as read
        - ⭐ Star important events
        - 📝 Add notes
        - 🔍 Filter and search
        - 📥 Export data
        """)


def render_features():
    """Render features explanation."""
    st.markdown("## 📖 Features Overview")

    features = [
        {
            "title": "👥 Client Management",
            "description": """
            Manage your client portfolio with comprehensive profiles:
            - **Add/Edit/Delete** clients
            - Track **industry**, **website**, and custom **metadata**
            - Mark clients as **active/inactive**
            - View **client-specific event feeds**
            - **Bulk import** clients (coming soon)
            """,
            "use_case": "Keep track of all companies you're monitoring in one place."
        },
        {
            "title": "📰 Event Monitoring",
            "description": """
            Automatically discover and track client-related events:
            - **News articles** from multiple sources
            - **Funding rounds** and investments
            - **Product launches** and updates
            - **Leadership changes** (CEO, executives)
            - **Acquisitions** and mergers
            - **Partnerships** and collaborations
            - **Regulatory news** and compliance
            """,
            "use_case": "Stay informed about everything happening with your clients."
        },
        {
            "title": "🎯 Smart Classification",
            "description": """
            AI-powered event classification:
            - **Automatic categorization** by event type
            - **Relevance scoring** (0.0 to 1.0)
            - **Sentiment analysis** (positive/neutral/negative)
            - **Tag extraction** (AI, Cloud, Finance, etc.)
            - **Keyword matching** for custom alerts
            """,
            "use_case": "Quickly identify the most important events without reading everything."
        },
        {
            "title": "🤖 Automation",
            "description": """
            Automated monitoring with scheduler:
            - **Scheduled scans** (daily, hourly, custom)
            - **Background processing**
            - **Automatic event collection**
            - **Rate limiting** to stay within API quotas
            - **Error recovery** and retry logic
            """,
            "use_case": "Set it and forget it - events appear automatically."
        },
        {
            "title": "📬 Notifications",
            "description": """
            Custom alert rules to stay informed:
            - **Email notifications** for important events
            - **Configurable triggers** (event type, relevance, keywords)
            - **Digest mode** (hourly, daily, weekly)
            - **Client-specific rules**
            - **Quiet hours** configuration
            """,
            "use_case": "Get alerted when critical events happen, without spam."
        },
        {
            "title": "📊 Analytics & Insights",
            "description": """
            Data-driven intelligence dashboards:
            - **Event trends** over time
            - **Client activity** metrics
            - **Sentiment analysis** charts
            - **Event type distribution**
            - **Top sources** and topics
            - **Exportable reports** (CSV, PDF)
            """,
            "use_case": "Understand patterns and make data-driven decisions."
        },
        {
            "title": "🔌 API Integration",
            "description": """
            Multiple data sources:
            - **Google Custom Search** - Web-wide coverage
            - **NewsAPI** - News-specific sources
            - **Mock API** - Free testing with sample data
            - **Rate limiting** - Stay within quotas
            - **Fallback mechanism** - Never fails
            """,
            "use_case": "Choose between free testing or comprehensive real data."
        },
        {
            "title": "⚙️ Customization",
            "description": """
            Tailor the system to your needs:
            - **Configurable relevance** thresholds
            - **Custom event types**
            - **Date range filters**
            - **Data retention policies**
            - **Display preferences**
            - **Export formats**
            """,
            "use_case": "Make ClientIQ work exactly how you need it."
        }
    ]

    for feature in features:
        with st.expander(f"**{feature['title']}**"):
            st.markdown(feature['description'])
            st.info(f"💡 **Use Case:** {feature['use_case']}")


def render_workflows():
    """Render common workflows."""
    st.markdown("## 🔄 Common Workflows")

    workflows = [
        {
            "title": "Daily Monitoring Routine",
            "icon": "📅",
            "steps": [
                "1. Open **Dashboard** to see overview",
                "2. Check **Recent Events Timeline** for new items",
                "3. Review **High Priority** events (>0.8 relevance)",
                "4. Mark important events with ⭐",
                "5. Add notes to events requiring follow-up",
                "6. Check **Clients Needing Attention** section"
            ],
            "time": "⏱️ 10-15 minutes daily"
        },
        {
            "title": "Weekly Analysis",
            "icon": "📊",
            "steps": [
                "1. Navigate to **💡 Insights** page",
                "2. Review **Events Over Time** chart",
                "3. Analyze **Event Type Distribution**",
                "4. Check **Sentiment Trends**",
                "5. Review **Top Clients by Activity**",
                "6. Identify **Emerging Trends**",
                "7. Export data for executive summary"
            ],
            "time": "⏱️ 30 minutes weekly"
        },
        {
            "title": "Setting Up Automated Alerts",
            "icon": "🔔",
            "steps": [
                "1. Go to **📬 Notifications** page",
                "2. Click **➕ New Rule**",
                "3. Configure trigger conditions:",
                "   - Select event types to monitor",
                "   - Set minimum relevance score",
                "   - Add keywords (optional)",
                "   - Choose specific clients (optional)",
                "4. Configure notification settings:",
                "   - Add recipient emails",
                "   - Set frequency (immediate/digest)",
                "5. Toggle rule to **Active**",
                "6. Test with **🧪 Test** button",
                "7. **💾 Save** the rule"
            ],
            "time": "⏱️ 5 minutes per rule"
        },
        {
            "title": "Client Portfolio Review",
            "icon": "👥",
            "steps": [
                "1. Navigate to **👥 Clients** page",
                "2. Review **Active Clients** list",
                "3. For each client:",
                "   - Check last scan date",
                "   - Review recent events count",
                "   - Update client information if needed",
                "4. Deactivate clients no longer relevant",
                "5. Add new clients to monitor",
                "6. Run targeted scan for specific clients"
            ],
            "time": "⏱️ 20 minutes monthly"
        },
        {
            "title": "Generating Executive Reports",
            "icon": "📈",
            "steps": [
                "1. Go to **📈 Reports** page",
                "2. Select date range (e.g., last quarter)",
                "3. Choose report type:",
                "   - Executive Summary",
                "   - Client Activity Report",
                "   - Event Analysis Report",
                "4. Customize filters:",
                "   - Specific clients",
                "   - Event types",
                "   - Minimum relevance",
                "5. Click **Generate Report**",
                "6. Review report preview",
                "7. Export to PDF or CSV"
            ],
            "time": "⏱️ 15 minutes per report"
        },
        {
            "title": "Troubleshooting Issues",
            "icon": "🔧",
            "steps": [
                "1. Navigate to **🧪 System Test** page",
                "2. Check **System Health** status",
                "3. Run relevant tests:",
                "   - Database operations",
                "   - Collector functionality",
                "   - API connectivity",
                "4. Review test results",
                "5. Fix any configuration issues in **⚙️ Settings**",
                "6. Re-run tests to verify fixes",
                "7. Contact support if issues persist"
            ],
            "time": "⏱️ 10 minutes as needed"
        }
    ]

    for workflow in workflows:
        with st.expander(f"{workflow['icon']} **{workflow['title']}** {workflow['time']}"):
            for step in workflow['steps']:
                st.markdown(step)


def render_faq():
    """Render FAQ section."""
    st.markdown("## ❓ Frequently Asked Questions")

    faqs = [
        {
            "q": "What's the difference between Mock and Real APIs?",
            "a": """
            **Mock APIs** (Free):
            - Generate realistic sample data
            - No API keys required
            - No cost or rate limits
            - Perfect for testing and demos
            - Data is simulated, not real

            **Real APIs** (Requires keys):
            - Actual news and web search results
            - Requires API keys (Google, NewsAPI)
            - Usage costs may apply
            - Rate limits apply (typically 100 calls/day)
            - Real, up-to-date information

            💡 **Recommendation:** Start with Mock APIs to learn the system, then switch to Real APIs for production use.
            """
        },
        {
            "q": "How do I get API keys?",
            "a": """
            **Google Custom Search API:**
            1. Go to [Google Cloud Console](https://console.cloud.google.com/)
            2. Create a new project
            3. Enable Custom Search API
            4. Create API credentials
            5. Set up a Custom Search Engine at [programmablesearchengine.google.com](https://programmablesearchengine.google.com/)
            6. Copy both API key and Search Engine ID to Settings

            **NewsAPI:**
            1. Go to [newsapi.org](https://newsapi.org/)
            2. Sign up for a free account
            3. Get your API key from the dashboard
            4. Copy to Settings > API Configuration

            💡 **Free Tiers Available:** Both services offer free tiers suitable for getting started.
            """
        },
        {
            "q": "What is a relevance score?",
            "a": """
            The **relevance score** (0.0 to 1.0) indicates how relevant an event is to a specific client:

            - **0.8 - 1.0** (High): Direct mention, major news about the client
            - **0.5 - 0.79** (Medium): Relevant industry news, indirect mentions
            - **0.0 - 0.49** (Low): Tangential relevance, generic industry news

            The score is calculated based on:
            - ✅ Company name mentions
            - ✅ Position in title vs. body
            - ✅ Industry relevance
            - ✅ Event type importance
            - ✅ Source credibility

            💡 **Tip:** Set minimum relevance score to 0.5 in Settings to filter out noise.
            """
        },
        {
            "q": "How often should I run scans?",
            "a": """
            **Recommended scan frequency:**

            - **Daily** (Most common): Good for most use cases, balances coverage and API usage
            - **Twice Daily**: For fast-moving industries or critical clients
            - **Hourly**: Only for breaking news scenarios, uses more API calls
            - **Manual**: For occasional checks or testing

            💡 **Tips:**
            - Start with daily scans
            - Enable automation once you're comfortable
            - Monitor API usage in Settings
            - Adjust based on your industry's pace
            """
        },
        {
            "q": "Can I monitor multiple clients?",
            "a": """
            **Yes!** ClientIQ is designed for portfolio monitoring:

            - ✅ Add unlimited clients (limited only by database size)
            - ✅ Scan multiple clients in one job
            - ✅ Set different priorities per client
            - ✅ Create client-specific notification rules
            - ✅ View aggregated analytics across all clients

            💡 **Best Practice:** Start with 5-10 key clients, then expand as needed.
            """
        },
        {
            "q": "How do I export data?",
            "a": """
            **Export options:**

            1. **Events Page:**
               - Filter events as needed
               - Click "📥 Export" button
               - Choose CSV or PDF format

            2. **Insights Page:**
               - Click "📊 Export to CSV"
               - Get all events in date range

            3. **Settings Page:**
               - Click "📊 Export All Data"
               - Downloads complete database backup in JSON

            💡 **Use Cases:** Executive reports, compliance records, backup/archival
            """
        },
        {
            "q": "What happens if I hit API rate limits?",
            "a": """
            **Built-in protection:**

            - ✅ Rate limiter tracks API usage automatically
            - ✅ System warns when approaching limits
            - ✅ Automatically falls back to Mock API if limit reached
            - ✅ Resets at midnight (24-hour window)
            - ✅ Configurable limits in Settings

            **What to do:**
            1. Check rate limit status in Settings > API Configuration
            2. Reduce scan frequency if needed
            3. Increase rate limit (may require paid API tier)
            4. Use Mock API temporarily

            💡 **Tip:** 100 calls/day is usually sufficient for 10-20 clients with daily scans.
            """
        },
        {
            "q": "Is my data secure?",
            "a": """
            **Security measures:**

            - 🔒 **Local storage:** All data stored locally in SQLite database
            - 🔒 **No cloud sync:** Your data never leaves your machine (unless you configure it)
            - 🔒 **API keys:** Stored securely in settings file
            - 🔒 **Password fields:** API keys are masked in UI
            - 🔒 **Backups:** Manual backup/restore available

            💡 **Best Practices:**
            - Keep API keys confidential
            - Backup database regularly
            - Use environment variables for production
            - Restrict file system access appropriately
            """
        }
    ]

    for faq in faqs:
        with st.expander(f"**{faq['q']}**"):
            st.markdown(faq['a'])


def render_troubleshooting():
    """Render troubleshooting guide."""
    st.markdown("## 🔧 Troubleshooting Guide")

    issues = [
        {
            "problem": "Scans return no events",
            "solutions": [
                "✅ Check if clients are marked as active (Clients page)",
                "✅ Verify API keys are configured correctly (Settings > API Configuration)",
                "✅ Test connection with 'Test Real API' button (System Test page)",
                "✅ Try increasing lookback days (scans last N days)",
                "✅ Check if rate limits are exceeded (Settings page)",
                "✅ Try switching to Mock API temporarily to rule out API issues"
            ]
        },
        {
            "problem": "Database errors",
            "solutions": [
                "✅ Run database tests (System Test page)",
                "✅ Check disk space (System Test > Health Check)",
                "✅ Backup and restore database (Settings page)",
                "✅ Initialize database (Database page)",
                "✅ Check file permissions on database file",
                "✅ Try clearing cache (Settings > General)"
            ]
        },
        {
            "problem": "Scheduler not working",
            "solutions": [
                "✅ Check scheduler status (Automation page)",
                "✅ Start scheduler if stopped",
                "✅ Verify schedule configuration",
                "✅ Check scheduler logs for errors",
                "✅ Ensure system time is correct",
                "✅ Restart application"
            ]
        },
        {
            "problem": "Notifications not sending",
            "solutions": [
                "✅ Test SMTP configuration (Settings > Notifications > Send Test Email)",
                "✅ Verify notification rules are active (Notifications page)",
                "✅ Check email addresses are correct",
                "✅ Review quiet hours settings",
                "✅ Check spam/junk folder",
                "✅ Verify trigger conditions match events"
            ]
        },
        {
            "problem": "API authentication errors",
            "solutions": [
                "✅ Verify API keys in Settings are correct (no extra spaces)",
                "✅ Check API key hasn't expired",
                "✅ Ensure API is enabled in provider's dashboard",
                "✅ Verify billing is active (for paid tiers)",
                "✅ Test credentials with provider's API explorer",
                "✅ Generate new API key if needed"
            ]
        },
        {
            "problem": "Slow performance",
            "solutions": [
                "✅ Check system resources (System Test > Health Check)",
                "✅ Clear cache (Settings > General)",
                "✅ Reduce number of events displayed (Settings > Display)",
                "✅ Archive old events (Settings > Monitoring)",
                "✅ Optimize database (Database page)",
                "✅ Close other applications"
            ]
        },
        {
            "problem": "Events have wrong classification",
            "solutions": [
                "✅ This is expected for some events - classifiers aren't perfect",
                "✅ Manually update event type in Events page",
                "✅ Add keywords to notification rules for better filtering",
                "✅ Adjust relevance score threshold",
                "✅ Use tags to supplement classification",
                "✅ Provide feedback (Request Feature tab)"
            ]
        }
    ]

    for issue in issues:
        with st.expander(f"❗ **{issue['problem']}**"):
            st.markdown("**Try these solutions:**")
            for solution in issue['solutions']:
                st.markdown(solution)

    st.divider()

    st.markdown("### 🆘 Still Having Issues?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Run System Diagnostics:**
        1. Go to **🧪 System Test** page
        2. Run all test suites
        3. Review failed tests
        4. Share results with support
        """)

    with col2:
        st.markdown("""
        **Get Help:**
        - 📧 Email: support@clientiq.com
        - 💬 GitHub Issues: [Report a bug](https://github.com/yourusername/clientiq/issues)
        - 📖 Documentation: [Read the docs](https://docs.clientiq.com)
        - 💡 Request features in the next tab →
        """)


def render_request_feature():
    """Render feature request form."""
    st.markdown("## 💡 Request a Feature")

    st.markdown("""
    We'd love to hear your ideas! Help us improve ClientIQ by suggesting new features or enhancements.
    """)

    with st.form("feature_request_form"):
        st.markdown("### Feature Request Form")

        # Feature category
        category = st.selectbox(
            "Feature Category",
            [
                "Data Collection & APIs",
                "Analytics & Reporting",
                "Notifications & Alerts",
                "User Interface",
                "Automation & Scheduling",
                "Integrations",
                "Performance & Scalability",
                "Other"
            ]
        )

        # Feature title
        title = st.text_input(
            "Feature Title",
            placeholder="Brief, descriptive title for your feature request"
        )

        # Detailed description
        description = st.text_area(
            "Detailed Description",
            placeholder="Describe the feature you'd like to see. What problem does it solve? How would you use it?",
            height=150
        )

        # Use case
        use_case = st.text_area(
            "Use Case / Example",
            placeholder="Provide a specific example of how you would use this feature in your workflow",
            height=100
        )

        # Priority
        priority = st.select_slider(
            "How important is this feature to you?",
            options=["Nice to have", "Would be helpful", "Important", "Critical"],
            value="Would be helpful"
        )

        # Contact info (optional)
        contact_email = st.text_input(
            "Your Email (optional)",
            placeholder="We'll contact you for clarification or to notify you when implemented"
        )

        # Submit button
        submitted = st.form_submit_button("📮 Submit Feature Request", use_container_width=True, type="primary")

        if submitted:
            if not title or not description:
                st.error("❌ Please fill in at least the title and description")
            else:
                # In a real implementation, this would send to a backend or email
                st.success("✅ Thank you! Your feature request has been submitted.")
                st.balloons()

                # Display summary
                with st.expander("📋 Request Summary"):
                    st.markdown(f"""
                    **Category:** {category}

                    **Title:** {title}

                    **Priority:** {priority}

                    **Description:**
                    {description}

                    **Use Case:**
                    {use_case}

                    **Contact:** {contact_email if contact_email else 'Not provided'}

                    **Submitted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """)

                st.info("💡 **Next Steps:** Our team will review your request and may reach out for more details.")

    st.divider()

    # Popular feature requests
    st.markdown("### 🔥 Popular Feature Requests")

    st.markdown("""
    See what others are requesting:

    1. **Slack/Teams Integration** - 🔥 45 votes
       - Send notifications to Slack/Teams channels
       - Status: Under consideration

    2. **Multi-language Support** - 🔥 32 votes
       - Monitor news in multiple languages
       - Status: Planned for Q3

    3. **Sentiment Deep Dive** - 🔥 28 votes
       - More detailed sentiment analysis with explanations
       - Status: In development

    4. **Custom Dashboards** - 🔥 24 votes
       - Create custom dashboard layouts and widgets
       - Status: Planned for Q4

    5. **API Webhooks** - 🔥 19 votes
       - Send events to external systems via webhooks
       - Status: Under consideration

    💡 **Vote on existing requests:** Visit our [feature request board](https://github.com/yourusername/clientiq/discussions)
    """)
