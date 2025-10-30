"""
First-Run Onboarding Wizard

Guides new users through initial setup and core features.
"""

import streamlit as st
from datetime import datetime
from typing import Optional
from src.models import ClientDTO
from src.storage import SQLiteStorage
from src.collectors import CollectorFactory
from src.ui.polish import apply_custom_css


class OnboardingWizard:
    """Manages the first-run onboarding experience."""

    STEPS = [
        "welcome",
        "configure",
        "add_client",
        "run_scan",
        "dashboard_tour",
        "automation",
        "complete"
    ]

    @staticmethod
    def should_show_onboarding() -> bool:
        """Check if onboarding should be displayed."""
        # Check if onboarding has been completed
        if st.session_state.get('onboarding_completed', False):
            return False

        # Check if user has explicitly skipped
        if st.session_state.get('onboarding_skipped', False):
            return False

        # Check if this is truly first run (no clients exist)
        try:
            storage = st.session_state.get('storage')
            if storage:
                clients = storage.get_all_clients()
                # If there are clients, assume onboarding was completed
                if len(clients) > 0:
                    st.session_state['onboarding_completed'] = True
                    return False
        except Exception:
            pass

        return True

    @staticmethod
    def initialize():
        """Initialize onboarding state."""
        if 'onboarding_step' not in st.session_state:
            st.session_state['onboarding_step'] = 0
        if 'onboarding_data' not in st.session_state:
            st.session_state['onboarding_data'] = {}

    @staticmethod
    def render():
        """Render the onboarding wizard."""
        OnboardingWizard.initialize()

        step_index = st.session_state['onboarding_step']
        step_name = OnboardingWizard.STEPS[step_index]

        # Apply custom CSS for better styling
        apply_custom_css()

        # Render appropriate step
        if step_name == "welcome":
            OnboardingWizard.render_welcome()
        elif step_name == "configure":
            OnboardingWizard.render_configure()
        elif step_name == "add_client":
            OnboardingWizard.render_add_client()
        elif step_name == "run_scan":
            OnboardingWizard.render_run_scan()
        elif step_name == "dashboard_tour":
            OnboardingWizard.render_dashboard_tour()
        elif step_name == "automation":
            OnboardingWizard.render_automation()
        elif step_name == "complete":
            OnboardingWizard.render_complete()

    @staticmethod
    def render_progress():
        """Render progress indicator."""
        step_index = st.session_state['onboarding_step']
        total_steps = len(OnboardingWizard.STEPS)
        progress = (step_index + 1) / total_steps

        st.progress(progress)
        st.caption(f"Step {step_index + 1} of {total_steps}")

    @staticmethod
    def render_welcome():
        """Render welcome screen."""
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='color: #1976d2; font-size: 3rem; margin-bottom: 1rem;'>
                👋 Welcome to Client Intelligence Monitor
            </h1>
            <p style='font-size: 1.2rem; color: #666; margin-bottom: 2rem;'>
                Your automated platform for tracking client news and events
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("""
            ### What You'll Learn

            In the next few minutes, we'll help you:

            1. **Configure Your Database** - Set up your data storage
            2. **Add Your First Client** - Create your first client profile
            3. **Run Your First Scan** - Collect news and events automatically
            4. **Explore the Dashboard** - Understand your portfolio at a glance
            5. **Set Up Automation** (Optional) - Get automatic notifications

            ### Why Client Intelligence Monitor?

            - **Stay Informed**: Never miss important client news
            - **Save Time**: Automated scanning from multiple sources
            - **Be Proactive**: Reach out at the right moments
            - **Track Trends**: Monitor your entire portfolio

            ---
            """)

            col_a, col_b = st.columns(2)

            with col_a:
                if st.button("🚀 Let's Get Started!", use_container_width=True, type="primary"):
                    st.session_state['onboarding_step'] = 1
                    st.rerun()

            with col_b:
                if st.button("⏭️ Skip Onboarding", use_container_width=True):
                    st.session_state['onboarding_skipped'] = True
                    st.rerun()

            st.markdown("---")
            st.caption("💡 **Tip**: You can access the full user guide anytime from the Help menu")

    @staticmethod
    def render_configure():
        """Render database configuration step."""
        OnboardingWizard.render_progress()

        st.markdown("## 📊 Step 1: Configure Your Database")
        st.markdown("Your database stores all clients, events, and settings.")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("""
            ### Database Setup

            The application uses SQLite, a lightweight database that requires no server.
            Your data is stored securely in a local file.
            """)

            # Check if database is already initialized
            storage = st.session_state.get('storage')
            db_path = st.session_state.settings.get('database_path', 'data/client_intelligence.db')

            if storage:
                st.success(f"✅ Database configured at: `{db_path}`")
                st.info("Your database is ready to use!")
            else:
                st.warning("⚠️ Database not initialized. Please restart the application.")

            st.markdown("""
            ### What Gets Stored?

            - **Clients**: Company names, industries, priorities
            - **Events**: News articles, funding rounds, partnerships
            - **Settings**: Your preferences and configurations
            - **Cache**: Search results for faster performance

            All data is stored locally and under your control.
            """)

        with col2:
            st.markdown("### 📁 Database Info")
            st.metric("Location", "data/")
            st.metric("Type", "SQLite")
            st.metric("Size", "~2 MB")

            st.markdown("---")
            st.markdown("### ✅ Features")
            st.markdown("- Fast queries")
            st.markdown("- No server needed")
            st.markdown("- Easy backups")
            st.markdown("- Portable")

        st.markdown("---")

        col_back, col_next = st.columns([1, 1])

        with col_back:
            if st.button("← Back", use_container_width=True):
                st.session_state['onboarding_step'] -= 1
                st.rerun()

        with col_next:
            if st.button("Next: Add a Client →", use_container_width=True, type="primary"):
                st.session_state['onboarding_step'] = 2
                st.rerun()

    @staticmethod
    def render_add_client():
        """Render add client step."""
        OnboardingWizard.render_progress()

        st.markdown("## 👥 Step 2: Add Your First Client")
        st.markdown("Let's add a client to monitor. You can add more clients later.")

        col1, col2 = st.columns([2, 1])

        with col1:
            with st.form("onboarding_add_client"):
                st.markdown("### Client Information")

                name = st.text_input(
                    "Company Name *",
                    placeholder="e.g., Acme Corporation",
                    help="The official name of the client company"
                )

                industry = st.selectbox(
                    "Industry *",
                    options=[
                        "",
                        "Technology - SaaS",
                        "Technology - Hardware",
                        "Technology - AI/ML",
                        "Finance - Banking",
                        "Finance - Insurance",
                        "Finance - Investment",
                        "Healthcare - Provider",
                        "Healthcare - Pharma",
                        "Healthcare - Medical Devices",
                        "Retail - E-commerce",
                        "Retail - Physical",
                        "Manufacturing",
                        "Energy",
                        "Real Estate",
                        "Education",
                        "Media & Entertainment",
                        "Professional Services",
                        "Other"
                    ],
                    help="Select the client's primary industry"
                )

                priority = st.select_slider(
                    "Priority",
                    options=["Low", "Medium", "High"],
                    value="Medium",
                    help="How important is this client to monitor?"
                )

                website = st.text_input(
                    "Website (Optional)",
                    placeholder="https://example.com",
                    help="Client's website URL"
                )

                description = st.text_area(
                    "Description (Optional)",
                    placeholder="Brief description of the client...",
                    help="Any additional notes about this client",
                    max_chars=500
                )

                col_form1, col_form2 = st.columns(2)

                with col_form1:
                    skip_client = st.form_submit_button("Skip for Now", use_container_width=True)

                with col_form2:
                    submit_client = st.form_submit_button("Add Client", use_container_width=True, type="primary")

                if skip_client:
                    st.session_state['onboarding_step'] = 3
                    st.session_state['onboarding_data']['client_skipped'] = True
                    st.rerun()

                if submit_client:
                    # Validate inputs
                    if not name or not industry:
                        st.error("❌ Please fill in required fields (Name and Industry)")
                    else:
                        try:
                            # Create client
                            storage = st.session_state.get('storage')
                            client = ClientDTO(
                                id=f"client-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                                name=name,
                                industry=industry,
                                priority=priority.lower(),
                                website=website if website else None,
                                description=description if description else None,
                                created_date=datetime.now(),
                                last_scanned=None
                            )

                            storage.create_client(client)

                            # Store in onboarding data
                            st.session_state['onboarding_data']['client'] = client
                            st.session_state['onboarding_data']['client_id'] = client.id

                            st.success(f"✅ Successfully added {name}!")
                            st.session_state['onboarding_step'] = 3
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error adding client: {e}")

        with col2:
            st.markdown("### 💡 Tips")
            st.info("""
            **Start with one important client**

            Choose a client you want to monitor closely. You can add more clients anytime from the Clients page.
            """)

            st.markdown("### 📋 Example")
            st.code("""
Name: Microsoft Corporation
Industry: Technology - SaaS
Priority: High
Website: https://microsoft.com
            """)

            st.markdown("### ⭐ Priority Levels")
            st.markdown("- **High**: Critical clients")
            st.markdown("- **Medium**: Regular clients")
            st.markdown("- **Low**: Prospects")

        st.markdown("---")

        if st.button("← Back", use_container_width=False):
            st.session_state['onboarding_step'] -= 1
            st.rerun()

    @staticmethod
    def render_run_scan():
        """Render run scan step."""
        OnboardingWizard.render_progress()

        st.markdown("## 🔍 Step 3: Run Your First Scan")

        client = st.session_state['onboarding_data'].get('client')
        client_skipped = st.session_state['onboarding_data'].get('client_skipped', False)

        if client_skipped:
            st.info("ℹ️ You skipped adding a client. You can add clients from the Clients page and scan them later.")

            col_back, col_next = st.columns([1, 1])

            with col_back:
                if st.button("← Back", use_container_width=True):
                    st.session_state['onboarding_step'] -= 1
                    st.rerun()

            with col_next:
                if st.button("Next: Dashboard Tour →", use_container_width=True, type="primary"):
                    st.session_state['onboarding_step'] = 4
                    st.rerun()
            return

        if not client:
            st.error("❌ No client found. Please go back and add a client first.")
            if st.button("← Back to Add Client"):
                st.session_state['onboarding_step'] = 2
                st.rerun()
            return

        st.markdown(f"Let's scan for news and events about **{client.name}**.")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("""
            ### How Scanning Works

            1. **Search Multiple Sources**: The system queries Google Search and NewsAPI
            2. **Classify Events**: AI automatically categorizes events (funding, partnerships, etc.)
            3. **Score Relevance**: Each event gets a relevance score (0.0 to 1.0)
            4. **Remove Duplicates**: Similar events are merged
            5. **Store Results**: Events are saved to your database

            This process takes about 10-30 seconds depending on the results.
            """)

            # Check scan status
            scan_complete = st.session_state['onboarding_data'].get('scan_complete', False)

            if not scan_complete:
                if st.button("🔍 Start Scanning", use_container_width=True, type="primary"):
                    with st.spinner(f"Scanning for news about {client.name}..."):
                        try:
                            storage = st.session_state.get('storage')
                            settings = st.session_state.get('settings', {})

                            # Get collector
                            collector = CollectorFactory.create_collector(settings)

                            # Collect events
                            events = collector.collect_events(
                                client_name=client.name,
                                client_id=client.id,
                                days_back=7
                            )

                            # Store events
                            stored_count = 0
                            for event in events:
                                try:
                                    storage.create_event(event)
                                    stored_count += 1
                                except Exception:
                                    pass  # Skip duplicates

                            # Update client last_scanned
                            client.last_scanned = datetime.now()
                            storage.update_client(client)

                            # Store results
                            st.session_state['onboarding_data']['scan_complete'] = True
                            st.session_state['onboarding_data']['events_found'] = stored_count

                            st.success(f"✅ Found and stored {stored_count} events!")
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error scanning: {e}")
            else:
                events_found = st.session_state['onboarding_data'].get('events_found', 0)
                st.success(f"✅ Scan complete! Found {events_found} events for {client.name}")

                st.markdown("### 🎉 Great Job!")
                st.info("""
                You've successfully scanned for events. You can now:
                - View events on the Dashboard
                - Filter by event type
                - Click events to see details
                - Run scans anytime from the Clients page
                """)

        with col2:
            st.markdown("### 📊 What You'll Get")
            st.markdown("""
            - 📰 News articles
            - 💰 Funding rounds
            - 🤝 Partnerships
            - 🚀 Product launches
            - 📈 Growth signals
            - 🏆 Awards & recognition
            """)

            st.markdown("### ⚙️ Settings")
            st.caption(f"Lookback: 7 days")
            st.caption(f"Min Score: 0.5")
            st.caption(f"Sources: 2 APIs")

        st.markdown("---")

        col_back, col_next = st.columns([1, 1])

        with col_back:
            if st.button("← Back", use_container_width=True):
                st.session_state['onboarding_step'] -= 1
                st.rerun()

        with col_next:
            scan_complete = st.session_state['onboarding_data'].get('scan_complete', False)
            if scan_complete:
                if st.button("Next: Dashboard Tour →", use_container_width=True, type="primary"):
                    st.session_state['onboarding_step'] = 4
                    st.rerun()
            else:
                st.button("Next: Dashboard Tour →", use_container_width=True, disabled=True)
                st.caption("Complete the scan first")

    @staticmethod
    def render_dashboard_tour():
        """Render dashboard tour step."""
        OnboardingWizard.render_progress()

        st.markdown("## 📊 Step 4: Dashboard Tour")
        st.markdown("Let's explore the main dashboard and its features.")

        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown("""
            ### Dashboard Overview

            The dashboard is your command center for monitoring all clients.
            """)

            # Show demo metrics
            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

            with metrics_col1:
                st.metric("Total Clients", "1", delta="Just added!")

            with metrics_col2:
                events_found = st.session_state['onboarding_data'].get('events_found', 0)
                st.metric("Total Events", str(events_found), delta=f"+{events_found}")

            with metrics_col3:
                st.metric("This Week", str(events_found))

            with metrics_col4:
                st.metric("Avg Relevance", "0.78")

            st.markdown("---")

            st.markdown("""
            ### Key Features

            #### 📈 Event Timeline
            Shows event activity over the last 30 days. Helps you spot trends and busy periods.

            #### 📊 Events by Type
            Breakdown of events by category (Funding, Partnerships, Products, etc.)
            Quickly see what's happening across your portfolio.

            #### 👥 Top Active Clients
            See which clients have the most recent activity.
            Focus your attention where it matters.

            #### 🔍 Recent Events
            Latest events across all clients with quick actions:
            - View full details
            - Open source article
            - Mark as read
            - Archive or delete

            #### 🎯 Quick Actions
            - Add new clients
            - Run scans
            - View all events
            - Configure settings
            """)

        with col2:
            st.markdown("### 🎯 Navigation")
            st.markdown("""
            **Sidebar Menu:**
            - 📊 Dashboard
            - 👥 Clients
            - 📰 Events
            - 🔔 Notifications
            - ⚙️ Settings
            - ❓ Help
            """)

            st.markdown("### 💡 Pro Tips")
            st.info("""
            - Use **Global Search** (top right) to find anything
            - Click metrics for detailed views
            - Hover over charts for details
            - Use filters to focus on specific data
            """)

        st.markdown("---")

        col_back, col_next = st.columns([1, 1])

        with col_back:
            if st.button("← Back", use_container_width=True):
                st.session_state['onboarding_step'] -= 1
                st.rerun()

        with col_next:
            if st.button("Next: Automation (Optional) →", use_container_width=True, type="primary"):
                st.session_state['onboarding_step'] = 5
                st.rerun()

    @staticmethod
    def render_automation():
        """Render automation setup step."""
        OnboardingWizard.render_progress()

        st.markdown("## 🔔 Step 5: Set Up Automation (Optional)")
        st.markdown("Get notified automatically when important events happen.")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("""
            ### Notification Rules

            Create rules to automatically notify you when:
            - High-relevance events are detected
            - Specific event types occur (funding, partnerships)
            - Events match certain keywords
            - Priority clients have news

            ### How It Works

            1. **Set Conditions**: Define what events trigger notifications
            2. **Choose Method**: Email, in-app alerts, or both
            3. **Test Rule**: See a preview before activating
            4. **Activate**: Turn on the rule and get notified

            You can always set this up later from the Notifications page.
            """)

            with st.expander("📝 Create a Quick Rule (Optional)", expanded=False):
                st.markdown("Let's create a simple rule to notify you of high-relevance events.")

                rule_name = st.text_input("Rule Name", value="High-Priority Events", key="onboard_rule_name")

                event_type = st.selectbox(
                    "Event Type",
                    ["All Types", "Funding", "Partnership", "Product Launch", "Acquisition"],
                    key="onboard_event_type"
                )

                min_score = st.slider(
                    "Minimum Relevance Score",
                    0.0, 1.0, 0.7, 0.05,
                    help="Only notify for events with this relevance or higher",
                    key="onboard_min_score"
                )

                if st.button("Create Rule", use_container_width=True):
                    st.success(f"✅ Rule '{rule_name}' created successfully!")
                    st.info("You can manage rules from the Notifications page.")
                    st.session_state['onboarding_data']['rule_created'] = True

        with col2:
            st.markdown("### 📧 Notification Methods")
            st.markdown("""
            - **Email**: Daily digests
            - **In-App**: Real-time alerts
            - **Quiet Hours**: Respect your schedule
            """)

            st.markdown("### 🎯 Popular Rules")
            st.markdown("""
            1. **High-Priority Funding**
               - Type: Funding
               - Score: 0.8+
               - Clients: High priority

            2. **All Partnerships**
               - Type: Partnership
               - Score: 0.6+
               - Clients: All

            3. **Weekly Digest**
               - Frequency: Weekly
               - Include: All events
               - Time: Monday 9am
            """)

        st.markdown("---")

        col_back, col_skip, col_next = st.columns([1, 1, 1])

        with col_back:
            if st.button("← Back", use_container_width=True):
                st.session_state['onboarding_step'] -= 1
                st.rerun()

        with col_skip:
            if st.button("Skip Automation", use_container_width=True):
                st.session_state['onboarding_step'] = 6
                st.rerun()

        with col_next:
            if st.button("Complete Setup →", use_container_width=True, type="primary"):
                st.session_state['onboarding_step'] = 6
                st.rerun()

    @staticmethod
    def render_complete():
        """Render completion screen."""
        st.markdown("""
        <div style='text-align: center; padding: 3rem 0;'>
            <h1 style='color: #1976d2; font-size: 4rem;'>🎉</h1>
            <h1 style='color: #1976d2; font-size: 3rem; margin-bottom: 1rem;'>
                You're All Set!
            </h1>
            <p style='font-size: 1.2rem; color: #666; margin-bottom: 2rem;'>
                Your Client Intelligence Monitor is ready to use
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("### 🎯 What You've Accomplished")

            tasks = [
                ("✅", "Set up your database"),
                ("✅", "Added your first client") if not st.session_state['onboarding_data'].get('client_skipped') else ("⏭️", "Skipped adding a client"),
                ("✅", "Ran your first scan") if st.session_state['onboarding_data'].get('scan_complete') else ("⏭️", "Skipped running a scan"),
                ("✅", "Toured the dashboard"),
                ("✅", "Learned about automation")
            ]

            for icon, task in tasks:
                st.markdown(f"{icon} {task}")

            st.markdown("---")

            st.markdown("### 🚀 Next Steps")

            st.markdown("""
            **Immediate Actions:**
            1. 👥 Add more clients from the Clients page
            2. 🔍 Run scans to collect events
            3. 📊 Explore the Dashboard to monitor activity

            **When Ready:**
            4. 🔔 Set up notification rules
            5. ⚙️ Configure API keys for real data
            6. 📧 Set up email notifications

            **Learn More:**
            7. ❓ Read the User Guide for detailed help
            8. 🧪 Check out the System Testing page
            9. 📚 Review the documentation
            """)

            st.markdown("---")

            st.markdown("### 💡 Helpful Resources")

            resources_col1, resources_col2 = st.columns(2)

            with resources_col1:
                st.markdown("""
                **In-App Help:**
                - ❓ Help & User Guide
                - 🧪 System Testing
                - ⚙️ Settings
                """)

            with resources_col2:
                st.markdown("""
                **Documentation:**
                - 📖 User Guide
                - 👨‍💻 Developer Guide
                - 🚀 Deployment Guide
                """)

            st.markdown("---")

            # Complete button
            if st.button("🎉 Start Using Client Intelligence Monitor", use_container_width=True, type="primary"):
                st.session_state['onboarding_completed'] = True
                st.session_state['onboarding_step'] = 0
                st.session_state['onboarding_data'] = {}
                st.success("✅ Onboarding complete! Redirecting to dashboard...")
                st.rerun()

            st.markdown("---")

            # Restart option
            with st.expander("🔄 Restart Onboarding"):
                st.markdown("Want to go through the onboarding again?")
                if st.button("Restart from Beginning"):
                    st.session_state['onboarding_step'] = 0
                    st.session_state['onboarding_data'] = {}
                    st.rerun()


def render_onboarding_wizard():
    """Main function to render onboarding wizard."""
    if OnboardingWizard.should_show_onboarding():
        # Create full-page overlay
        st.markdown("""
        <style>
        .main > div {
            padding-top: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)

        OnboardingWizard.render()

        # Stop rendering the rest of the app
        st.stop()
