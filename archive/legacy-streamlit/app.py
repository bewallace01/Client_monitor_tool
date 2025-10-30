"""
Client Intelligence Monitor - Streamlit Dashboard
Main entry point for the web UI.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

from config import settings
from src.storage import Database, ClientRepository, EventRepository, SQLiteStorage
from src.models import EventCategory
from src.collectors import MockCollector
from src.ui.pages.models_test import render_models_test_page
from src.ui.pages.database import render_database_page
from src.ui.pages.collector_test import render_collector_test_page
from src.ui.pages.search_test import render_search_test_page
from src.ui.pages.clients import render_clients_page
from src.ui.pages.add_sample_clients import render_add_sample_clients_page
from src.ui.pages.events import render_events_page
from src.ui.pages.automation import render_automation_page
from src.ui.pages.notifications import render_notifications_page
from src.ui.pages.reports import render_reports_page
from src.ui.pages.insights import render_insights_page
from src.ui.pages.settings import render_settings_page
from src.ui.pages.system_test import render_system_test_page
from src.ui.pages.help import render_help_page
from src.scheduler.control import is_scheduler_running, start_scheduler, stop_scheduler
from src.scheduler.runner import get_scheduler_status
from src.ui.polish import inject_custom_css, render_page_header, render_empty_state
from src.ui.components import render_global_search
from src.debug_utils import initialize_debug_mode, render_debug_panel


# Page configuration
st.set_page_config(
    page_title="ClientIQ - Intelligence Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/client-monitor',
        'Report a bug': 'https://github.com/yourusername/client-monitor/issues',
        'About': '**ClientIQ** - Professional client intelligence monitoring platform'
    }
)


# Initialize legacy database (SQLAlchemy)
@st.cache_resource
def init_database():
    """Initialize legacy SQLAlchemy database and create tables."""
    db = Database()
    db.create_tables()
    return db


# Initialize new database (SQLite with DTOs)
@st.cache_resource
def init_new_database(_version="v6_timestamps"):  # Fixed created_at/updated_at requirement
    """Initialize new SQLite database with DTO storage."""
    storage = SQLiteStorage()
    storage.connect()

    # Always run initialize_database to ensure schema is up-to-date
    # It includes migration logic for existing databases
    try:
        storage.initialize_database()
    except Exception as e:
        st.error(f"Failed to initialize database: {e}")

    return storage


db = init_database()  # Legacy database
storage = init_new_database()  # New DTO-based database

# Inject professional UI polish
inject_custom_css()


def render_sidebar():
    """Render modern sidebar with navigation only."""
    with st.sidebar:
        # Modern Logo/Brand area with gradient
        st.markdown("""
        <style>
        /* Modern Navigation Styling */
        .nav-logo {
            text-align: center;
            padding: 2rem 0 1.5rem 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: -1rem -1rem 2rem -1rem;
            border-radius: 0 0 20px 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .nav-logo h1 {
            color: white;
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        .nav-logo p {
            color: rgba(255,255,255,0.9);
            font-size: 0.85rem;
            margin: 0.3rem 0 0 0;
            font-weight: 300;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        /* Navigation Section Header */
        .nav-header {
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: rgba(255,255,255,0.5);
            margin: 1.5rem 0 1rem 0;
            padding-left: 0.5rem;
        }

        /* Streamlit Radio Button Customization */

        /* Aggressively hide radio button circles - all possible selectors */
        section[data-testid="stSidebar"] input[type="radio"],
        section[data-testid="stSidebar"] [data-baseweb="radio"],
        .stRadio input[type="radio"],
        .stRadio [data-baseweb="radio"],
        [role="radiogroup"] input[type="radio"],
        [role="radiogroup"] [data-baseweb="radio"],
        input[type="radio"] {
            opacity: 0 !important;
            width: 0 !important;
            height: 0 !important;
            position: absolute !important;
            left: -9999px !important;
            visibility: hidden !important;
        }

        /* Hide the entire radio control wrapper */
        section[data-testid="stSidebar"] [data-baseweb="radio"],
        .stRadio [data-baseweb="radio"] {
            width: 0 !important;
            height: 0 !important;
            opacity: 0 !important;
            overflow: hidden !important;
            position: absolute !important;
            left: -9999px !important;
        }

        /* Radio group container */
        .stRadio [role="radiogroup"],
        section[data-testid="stSidebar"] [role="radiogroup"] {
            gap: 0.3rem !important;
            display: flex !important;
            flex-direction: column !important;
            width: 100% !important;
        }

        /* Individual radio button labels */
        .stRadio [role="radiogroup"] label,
        section[data-testid="stSidebar"] [role="radiogroup"] label {
            background: rgba(255,255,255,0.05) !important;
            border-radius: 10px !important;
            padding: 0.7rem 1rem !important;
            transition: all 0.2s ease !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            width: 100% !important;
            display: block !important;
            text-align: center !important;
            cursor: pointer !important;
            margin: 0 !important;
        }

        /* Hover state */
        .stRadio [role="radiogroup"] label:hover,
        section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(255,255,255,0.1) !important;
            border-color: rgba(255,255,255,0.2) !important;
            transform: translateX(3px) !important;
        }

        /* Selected state - darker box */
        .stRadio [role="radiogroup"] label[data-checked="true"],
        section[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] {
            background: rgba(0,0,0,0.4) !important;
            border-color: rgba(255,255,255,0.4) !important;
            box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3) !important;
            font-weight: 600 !important;
        }

        /* Center the text content */
        .stRadio [role="radiogroup"] label p,
        section[data-testid="stSidebar"] [role="radiogroup"] label p {
            text-align: center !important;
            width: 100% !important;
            margin: 0 !important;
        }

        /* Remove left padding from markdown container */
        .stRadio [role="radiogroup"] label div,
        section[data-testid="stSidebar"] [role="radiogroup"] label div {
            padding-left: 0 !important;
        }
        </style>

        <div class="nav-logo">
            <h1>📊 ClientIQ</h1>
            <p>Intelligence Monitor</p>
        </div>
        """, unsafe_allow_html=True)

        # Navigation header
        st.markdown('<div class="nav-header">🎯 Navigation</div>', unsafe_allow_html=True)

        # Navigation menu
        page = st.radio(
            "Select Page",
            ["📊 Dashboard", "🔍 Search", "👥 Clients", "📰 Events", "🤖 Automation", "📬 Notifications", "📈 Reports", "💡 Insights", "✨ Add Samples", "🔎 Search Test", "🧪 Collector Test", "🧪 Models Test", "🗄️ Database", "⚙️ Settings", "🧪 System Test", "📚 Help"],
            label_visibility="collapsed"
        )

        return {"page": page}


def render_dashboard():
    """Render main dashboard page."""
    # Professional header with subtitle
    render_page_header(
        "Client Intelligence Dashboard",
        "Real-time monitoring and insights for your key accounts",
        "📊"
    )

    # Filters section at top of dashboard
    with st.expander("🔍 Filters & Options", expanded=False):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Client filter
            with db.get_session() as session:
                clients = ClientRepository.get_all(session)
                client_options = ["All Clients"] + [c.name for c in clients]

            selected_client = st.selectbox("Client", client_options, key="dash_client_filter")

        with col2:
            # Date range filter
            date_range = st.slider(
                "Date Range (days)",
                min_value=7,
                max_value=90,
                value=30,
                step=7,
                key="dash_date_filter"
            )

        with col3:
            # Category filter
            categories = st.multiselect(
                "Event Categories",
                options=[c.value for c in EventCategory],
                default=[],
                key="dash_category_filter"
            )

        with col4:
            # Relevance filter
            min_relevance = st.slider(
                "Min Relevance Score",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.1,
                key="dash_relevance_filter"
            )

    # Create filters dict
    filters = {
        "selected_client": selected_client if selected_client != "All Clients" else None,
        "date_range": date_range,
        "categories": categories if categories else None,
        "min_relevance": min_relevance,
    }

    with db.get_session() as session:
        # Welcome banner for first-time users
        all_clients = ClientRepository.get_all(session, active_only=False)
        if len(all_clients) == 0:
            st.info("""
            👋 **Welcome to ClientIQ!** Get started by adding your first client and running a scan.

            **Quick Start:**
            1. Navigate to '👥 Clients' to add clients
            2. Return here and click '🔄 Run Scan Now'
            3. View and manage events in the timeline below
            """)
            st.divider()
        # Get metrics
        total_clients = len(ClientRepository.get_all(session, active_only=True))
        recent_events = EventRepository.get_recent(
            session,
            days=filters["date_range"],
            min_relevance=filters["min_relevance"]
        )
        unread_count = EventRepository.get_unread_count(session)

        # Top metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Active Clients", total_clients)

        with col2:
            st.metric("Recent Events", len(recent_events))

        with col3:
            st.metric("Unread Events", unread_count)

        with col4:
            high_priority = len([e for e in recent_events if e.relevance_score >= 0.8])
            st.metric("High Priority (>0.8)", high_priority)

        with col5:
            # Get last scan time from most recently checked client
            all_clients = ClientRepository.get_all(session, active_only=False)
            last_scan = max([c.last_checked_at for c in all_clients if c.last_checked_at], default=None)
            if last_scan:
                time_ago = datetime.utcnow() - last_scan
                if time_ago.days > 0:
                    scan_text = f"{time_ago.days}d ago"
                elif time_ago.seconds > 3600:
                    scan_text = f"{time_ago.seconds // 3600}h ago"
                else:
                    scan_text = f"{time_ago.seconds // 60}m ago"
            else:
                scan_text = "Never"
            st.metric("Last Scan", scan_text)

        st.divider()

        # Charts row 1
        col1, col2 = st.columns(2)

        with col1:
            # Events by type
            st.subheader("📊 Events by Type")
            if recent_events:
                type_counts = {}
                for event in recent_events:
                    # Use event_type if available, fallback to category
                    event_type = getattr(event, 'event_type', event.category)
                    type_counts[event_type] = type_counts.get(event_type, 0) + 1

                fig = px.bar(
                    x=list(type_counts.keys()),
                    y=list(type_counts.values()),
                    labels={"x": "Event Type", "y": "Count"},
                    color=list(type_counts.values()),
                    color_continuous_scale="blues"
                )
                fig.update_layout(showlegend=False, height=300, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No events found for the selected filters.")

        with col2:
            # Events over time
            st.subheader("📈 Events Timeline")
            if recent_events:
                event_dates = [e.event_date.date() for e in recent_events]
                date_counts = {}
                for date in event_dates:
                    date_counts[date] = date_counts.get(date, 0) + 1

                df_timeline = pd.DataFrame(
                    list(date_counts.items()),
                    columns=["Date", "Events"]
                ).sort_values("Date")

                fig = px.area(
                    df_timeline,
                    x="Date",
                    y="Events",
                    markers=True,
                    line_shape="spline"
                )
                fig.update_traces(fill='tozeroy', fillcolor='rgba(31, 119, 180, 0.2)')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No events found for the selected filters.")

        # Charts row 2
        col1, col2 = st.columns(2)

        with col1:
            # Sentiment distribution pie chart
            st.subheader("😊 Sentiment Distribution")
            if recent_events:
                sentiment_counts = {}
                for event in recent_events:
                    sentiment = getattr(event, 'sentiment', event.sentiment_label)
                    sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

                colors = {
                    'positive': '#28a745',
                    'neutral': '#ffc107',
                    'negative': '#dc3545'
                }
                color_list = [colors.get(s, '#6c757d') for s in sentiment_counts.keys()]

                fig = px.pie(
                    names=list(sentiment_counts.keys()),
                    values=list(sentiment_counts.values()),
                    color=list(sentiment_counts.keys()),
                    color_discrete_map=colors
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No events found for the selected filters.")

        with col2:
            # Relevance distribution
            st.subheader("🎯 Relevance Distribution")
            if recent_events:
                relevance_labels = [e.relevance_label for e in recent_events]
                relevance_counts = {}
                for label in relevance_labels:
                    relevance_counts[label] = relevance_counts.get(label, 0) + 1

                # Ensure proper order
                ordered_labels = ['high', 'medium', 'low']
                ordered_counts = [relevance_counts.get(label, 0) for label in ordered_labels]

                colors = ['#28a745', '#ffc107', '#dc3545']

                fig = go.Figure(data=[go.Bar(
                    x=ordered_labels,
                    y=ordered_counts,
                    marker_color=colors
                )])
                fig.update_layout(
                    height=300,
                    xaxis_title="Relevance",
                    yaxis_title="Count",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No events found for the selected filters.")

        st.divider()

        # Recent events feed with timeline view
        st.subheader("📰 Recent Events Timeline")

        if recent_events:
            # Add a quick filter for event types
            event_types = list(set([getattr(e, 'event_type', e.category) for e in recent_events]))
            selected_types = st.multiselect(
                "Filter by event type:",
                options=event_types,
                default=event_types,
                key="dashboard_event_filter"
            )

            # Filter events
            filtered_events = [
                e for e in recent_events
                if getattr(e, 'event_type', e.category) in selected_types
            ]

            for event in filtered_events[:15]:  # Show top 15
                client = ClientRepository.get_by_id(session, event.client_id)

                relevance_class = f"{event.relevance_label}-relevance"

                # Event type emoji mapping
                type_emoji = {
                    'funding': '💰',
                    'acquisition': '🤝',
                    'leadership': '👤',
                    'product': '🚀',
                    'partnership': '🤝',
                    'financial': '💵',
                    'award': '🏆',
                    'regulatory': '⚖️',
                    'news': '📰',
                    'other': '📌'
                }

                # Sentiment emoji mapping
                sentiment_emoji = {
                    'positive': '😊',
                    'neutral': '😐',
                    'negative': '😞'
                }

                event_type = getattr(event, 'event_type', event.category)
                sentiment = getattr(event, 'sentiment', event.sentiment_label)

                # Determine border color based on relevance
                border_colors = {
                    'high': '#10b981',
                    'medium': '#f59e0b',
                    'low': '#ef4444'
                }
                border_color = border_colors.get(relevance_class.replace('-relevance', ''), '#e0e0e0')

                # Badge colors
                badge_color_map = {
                    'funding': '#0d6efd',
                    'acquisition': '#6610f2',
                    'leadership': '#d63384',
                    'product': '#fd7e14',
                    'partnership': '#20c997',
                    'financial': '#198754',
                    'award': '#ffc107',
                    'regulatory': '#dc3545',
                    'news': '#6c757d',
                    'other': '#adb5bd'
                }
                badge_color = badge_color_map.get(event_type, '#6c757d')

                # Use st.container with border parameter (Streamlit native approach)
                with st.container(border=True):
                    # Badge row at top
                    st.markdown(f"""
                    <div style="margin-bottom: 0.75rem;">
                        <span style="background-color: {badge_color}; color: white; padding: 4px 12px;
                                     border-radius: 6px; font-size: 0.85em; font-weight: 500; margin-right: 10px;">
                            {type_emoji.get(event_type, '📌')} {event_type.upper()}
                        </span>
                        <span style="font-size: 1.3em;">
                            {sentiment_emoji.get(sentiment, '😐')}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                    # Add colored indicator bar
                    st.markdown(f"""
                    <div style="height: 4px; background-color: {border_color}; border-radius: 2px; margin-bottom: 1rem;"></div>
                    """, unsafe_allow_html=True)

                    # Main content columns
                    col1, col2, col3 = st.columns([6, 2, 2])

                    with col1:
                        st.markdown(f"**{event.title}**")
                        st.caption(f"🏢 {client.name if client else 'Unknown'} • 📅 {event.event_date.strftime('%Y-%m-%d')} • 📰 {event.source}")

                    with col2:
                        st.metric("Relevance", f"{event.relevance_score:.0%}")
                        if hasattr(event, 'sentiment_score') and event.sentiment_score is not None:
                            st.caption(f"Sentiment: {event.sentiment_score:+.2f}")

                    with col3:
                        if not event.is_read:
                            if st.button("✓ Mark Read", key=f"read_{event.id}", use_container_width=True):
                                EventRepository.mark_as_read(session, event.id)
                                st.rerun()
                        else:
                            st.caption("✅ Read")

                        # Star/Unstar toggle - always show button
                        if event.is_starred:
                            if st.button("⭐ Starred", key=f"unstar_{event.id}", use_container_width=True, type="primary"):
                                EventRepository.toggle_star(session, event.id)
                                st.rerun()
                        else:
                            if st.button("☆ Star", key=f"star_{event.id}", use_container_width=True):
                                EventRepository.toggle_star(session, event.id)
                                st.rerun()

                    # Expandable details
                    if event.description:
                        with st.expander("📖 Show details"):
                            st.write(event.description)
                            if event.url:
                                st.markdown(f"[🔗 Read full article]({event.url})")

                    # Add notes section
                    with st.expander("📝 Add/View Notes"):
                        notes = event.user_notes or ""
                        new_notes = st.text_area(
                            "Notes:",
                            value=notes,
                            key=f"notes_{event.id}",
                            height=100
                        )
                        if st.button("💾 Save Notes", key=f"save_notes_{event.id}"):
                            EventRepository.update_notes(session, event.id, new_notes)
                            st.success("Notes saved!")
                            st.rerun()
        else:
            # Professional empty state
            render_empty_state(
                icon="📭",
                title="No Events Found",
                description="Get started by adding clients and running your first scan to discover relevant business events."
            )

        st.divider()

        # Client Insights Section
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔥 Top Clients by Activity")
            # Get all active clients with event counts
            all_active_clients = ClientRepository.get_all(session, active_only=True)
            if all_active_clients:
                client_activity = []
                for client in all_active_clients:
                    client_events = EventRepository.get_by_client(session, client.id)
                    recent_events = [e for e in client_events if e.event_date >= (datetime.utcnow() - timedelta(days=filters["date_range"]))]
                    if len(recent_events) > 0:
                        client_activity.append((client, len(recent_events)))

                # Sort by event count
                client_activity.sort(key=lambda x: x[1], reverse=True)

                if client_activity:
                    for client, count in client_activity[:5]:  # Top 5
                        with st.container(border=True):
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                # Clickable client name
                                if st.button(f"📊 {client.name}", key=f"top_client_{client.id}", use_container_width=True):
                                    st.session_state.viewing_client_id = client.id
                                    st.session_state.page = "👥 Clients"
                                    st.rerun()
                            with col_b:
                                st.metric("Events", count)
                else:
                    st.info("No client activity in selected period")
            else:
                st.info("No active clients")

        with col2:
            st.subheader("⚠️ Clients Needing Attention")
            # Find clients with no recent events
            all_active_clients = ClientRepository.get_all(session, active_only=True)
            if all_active_clients:
                clients_needing_attention = []
                for client in all_active_clients:
                    client_events = EventRepository.get_by_client(session, client.id)
                    recent_events = [e for e in client_events if e.event_date >= (datetime.utcnow() - timedelta(days=30))]

                    if len(recent_events) == 0:
                        # Check last checked time
                        days_since_check = 999
                        if client.last_checked_at:
                            days_since_check = (datetime.utcnow() - client.last_checked_at).days

                        clients_needing_attention.append((client, days_since_check))

                # Sort by days since check
                clients_needing_attention.sort(key=lambda x: x[1], reverse=True)

                if clients_needing_attention:
                    for client, days in clients_needing_attention[:5]:  # Top 5
                        with st.container(border=True):
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                # Clickable client name
                                if st.button(f"⚠️ {client.name}", key=f"attention_client_{client.id}", use_container_width=True):
                                    st.session_state.viewing_client_id = client.id
                                    st.session_state.page = "👥 Clients"
                                    st.rerun()
                            with col_b:
                                if days == 999:
                                    st.caption("Never checked")
                                else:
                                    st.caption(f"{days}d ago")
                else:
                    st.success("All clients have recent activity!")
            else:
                st.info("No active clients")

        st.divider()

        # Client Overview Section
        st.subheader("👥 Client Overview")

        all_clients = ClientRepository.get_all(session, active_only=True)
        if all_clients:
            client_data = []
            for client in all_clients:
                # Get recent event for this client
                client_events = EventRepository.get_by_client(session, client.id)
                recent_client_events = [e for e in client_events if e.event_date >= (datetime.utcnow() - timedelta(days=filters["date_range"]))]

                last_event = max([e.event_date for e in client_events], default=None) if client_events else None
                event_count = len(recent_client_events)

                status_icon = "🟢" if client.is_active else "⚫"
                last_event_str = last_event.strftime("%Y-%m-%d") if last_event else "No events"

                client_data.append({
                    "Status": status_icon,
                    "Client": client.name,
                    "Industry": client.industry or "—",
                    "Last Event": last_event_str,
                    "Events (period)": event_count,
                    "Last Checked": client.last_checked_at.strftime("%Y-%m-%d %H:%M") if client.last_checked_at else "Never"
                })

            df_clients = pd.DataFrame(client_data)
            st.dataframe(df_clients, use_container_width=True, hide_index=True)
        else:
            st.info("No clients added yet. Go to '👥 Clients' to add your first client.")

        st.divider()

        # Quick Actions Section
        st.subheader("⚡ Quick Actions")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Run Scan Now", use_container_width=True, type="primary"):
                with st.spinner("Running monitoring scan..."):
                    import subprocess
                    result = subprocess.run(
                        ["python", "scripts/run_monitor.py", "--lookback-days", "7"],
                        cwd=str(project_root),
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        st.success("✅ Scan completed successfully!")

                        # Display output in an expandable section
                        with st.expander("📋 View Scan Results", expanded=True):
                            st.code(result.stdout, language=None)

                        # Add a rerun button instead of auto-rerun
                        if st.button("🔄 Refresh Dashboard", type="primary"):
                            st.rerun()
                    else:
                        st.error(f"❌ Scan failed: {result.stderr}")

        with col2:
            if st.button("➕ Add New Client", use_container_width=True):
                st.info("👈 Use the sidebar to navigate to '👥 Clients' page to add a new client")

        with col3:
            if st.button("📊 Generate Report", use_container_width=True):
                st.info("📝 Report generation coming soon!")


def render_search_page():
    """Render global search page."""
    render_page_header(
        "Global Search",
        "Search across all clients, events, and data",
        "🔍"
    )

    render_global_search(storage)


def main():
    """Main application entry point."""
    filters = render_sidebar()

    # Initialize debug mode after settings are available
    initialize_debug_mode()

    # Demo mode banner
    demo_mode = os.getenv("DEMO_MODE", "").lower() == "true"
    if demo_mode:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;
                    text-align: center; border: 2px solid rgba(255,255,255,0.3);">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🎭 DEMO MODE</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">
                You are viewing demo data. This is a demonstration environment with sample clients and events.
                To exit demo mode, unset the <code style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 4px;">DEMO_MODE</code> environment variable.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Route to appropriate page
    if filters["page"] == "📊 Dashboard":
        render_dashboard()
    elif filters["page"] == "🔍 Search":
        render_search_page()
    elif filters["page"] == "👥 Clients":
        render_clients_page()
    elif filters["page"] == "📰 Events":
        render_events_page()
    elif filters["page"] == "🤖 Automation":
        render_automation_page()
    elif filters["page"] == "📬 Notifications":
        render_notifications_page()
    elif filters["page"] == "📈 Reports":
        render_reports_page()
    elif filters["page"] == "💡 Insights":
        render_insights_page()
    elif filters["page"] == "✨ Add Samples":
        render_add_sample_clients_page()
    elif filters["page"] == "🔎 Search Test":
        render_search_test_page()
    elif filters["page"] == "🔍 Collector Test":
        render_collector_test_page()
    elif filters["page"] == "🧪 Models Test":
        render_models_test_page()
    elif filters["page"] == "🗄️ Database":
        render_database_page()
    elif filters["page"] == "⚙️ Settings":
        render_settings_page()
    elif filters["page"] == "🧪 System Test":
        render_system_test_page()
    elif filters["page"] == "📚 Help":
        render_help_page()

    # Render debug panel if debug mode is enabled
    render_debug_panel()


if __name__ == "__main__":
    main()
