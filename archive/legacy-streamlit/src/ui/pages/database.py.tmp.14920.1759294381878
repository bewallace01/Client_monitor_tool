"""
Database management UI page for Client Intelligence Monitor.
Provides visual interface for viewing and managing the SQLite database.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.storage import SQLiteStorage
from src.models import ClientDTO, EventDTO
from src.models.utils import generate_uuid, format_datetime_ago


# Initialize storage
@st.cache_resource
def get_storage():
    """Get or create storage instance."""
    storage = SQLiteStorage()
    storage.connect()
    return storage


def render_database_page():
    """Render the database management page."""
    st.title("🗄️ Database Management")
    st.markdown("View and manage the SQLite database for Client Intelligence Monitor")

    storage = get_storage()

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Database Status",
        "👥 Clients",
        "📰 Events",
        "💾 Cache"
    ])

    with tab1:
        render_status_tab(storage)

    with tab2:
        render_clients_tab(storage)

    with tab3:
        render_events_tab(storage)

    with tab4:
        render_cache_tab(storage)


# ==================== Tab 1: Database Status ====================

def render_status_tab(storage: SQLiteStorage):
    """Render database status tab."""
    st.subheader("Database Status")

    # Get database info
    db_info = storage.get_database_info()
    stats = storage.get_statistics()

    # Database info
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📁 Database File")
        st.code(db_info["path"])
        st.metric("File Size", f"{db_info['size_mb']} MB")
        st.metric("Exists", "Yes" if db_info["exists"] else "No")

    with col2:
        st.markdown("### 📊 Tables")
        if db_info["tables"]:
            for table in db_info["tables"]:
                st.markdown(f"- `{table}`")
        else:
            st.info("No tables found")

    st.divider()

    # Statistics
    st.markdown("### 📈 Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Active Clients", stats.get("active_clients", 0))

    with col2:
        st.metric("Total Events", stats.get("total_events", 0))

    with col3:
        st.metric("New Events", stats.get("new_events", 0))

    with col4:
        st.metric("Cache Entries", stats.get("total_cache_entries", 0))

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Events (Last 7 Days)", stats.get("events_last_7_days", 0))

    with col2:
        st.metric("Valid Cache Entries", stats.get("valid_cache_entries", 0))

    st.divider()

    # Management actions
    st.markdown("### ⚙️ Database Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔧 Initialize Database", use_container_width=True):
            try:
                storage.initialize_database()
                st.success("Database initialized successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error initializing database: {e}")

    with col2:
        if st.button("🗑️ Reset Database", use_container_width=True, type="secondary"):
            if st.session_state.get("confirm_reset"):
                try:
                    storage.drop_all_tables()
                    storage.initialize_database()
                    st.success("Database reset successfully!")
                    st.session_state.confirm_reset = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error resetting database: {e}")
            else:
                st.session_state.confirm_reset = True
                st.warning("Click again to confirm reset")

    with col3:
        if st.button("🔄 Refresh Stats", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()


# ==================== Tab 2: Clients ====================

def render_clients_tab(storage: SQLiteStorage):
    """Render clients management tab."""
    st.subheader("Client Management")

    # Get all clients
    clients = storage.get_all_clients(active_only=False)

    # Add sample client button
    col1, col2 = st.columns([3, 1])

    with col2:
        if st.button("➕ Add Sample Client", use_container_width=True):
            sample_client = ClientDTO.create_sample(
                name=f"Sample Co {len(clients) + 1}",
                priority="medium"
            )
            try:
                storage.create_client(sample_client)
                st.success(f"Added client: {sample_client.name}")
                st.rerun()
            except Exception as e:
                st.error(f"Error adding client: {e}")

    st.markdown(f"**Total Clients:** {len(clients)}")

    if not clients:
        st.info("No clients in database. Click 'Add Sample Client' to get started!")
        return

    # Prepare data for table
    client_data = []
    for client in clients:
        # Get event count for this client
        client_stats = storage.get_client_statistics(client.id)

        client_data.append({
            "Name": client.name,
            "Industry": client.industry or "-",
            "Priority": client.priority.upper(),
            "# Events": client_stats.get("total_events", 0),
            "Last Checked": format_datetime_ago(client.last_checked) if client.last_checked else "Never",
            "Active": "✅" if client.is_active else "❌",
            "ID": client.id,
        })

    # Display table
    df = pd.DataFrame(client_data)

    # Color-code priority
    def highlight_priority(row):
        if row["Priority"] == "HIGH":
            return ['background-color: #90EE90'] * len(row)
        elif row["Priority"] == "MEDIUM":
            return ['background-color: #FFFFE0'] * len(row)
        else:
            return ['background-color: #FFB6C1'] * len(row)

    st.dataframe(
        df.drop(columns=["ID"]),
        use_container_width=True,
        hide_index=True,
    )

    # Client details section
    st.divider()
    st.markdown("### 🔍 Client Details")

    selected_client_name = st.selectbox(
        "Select a client to view details",
        options=[c.name for c in clients]
    )

    if selected_client_name:
        client = next(c for c in clients if c.name == selected_client_name)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Name:** {client.name}")
            st.markdown(f"**Industry:** {client.industry}")
            st.markdown(f"**Priority:** {client.priority.upper()}")
            st.markdown(f"**Domain:** {client.domain}")

        with col2:
            st.markdown(f"**Account Owner:** {client.account_owner or 'N/A'}")
            st.markdown(f"**Tier:** {client.tier or 'N/A'}")
            st.markdown(f"**Monitoring Since:** {format_datetime_ago(client.monitoring_since)}")
            st.markdown(f"**Last Checked:** {format_datetime_ago(client.last_checked) if client.last_checked else 'Never'}")

        if client.description:
            st.markdown(f"**Description:** {client.description}")

        if client.keywords:
            st.markdown(f"**Keywords:** {', '.join(client.keywords)}")

        # Show client statistics
        st.markdown("#### Statistics")
        client_stats = storage.get_client_statistics(client.id)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Events", client_stats.get("total_events", 0))

        with col2:
            avg_rel = client_stats.get("average_relevance", 0)
            st.metric("Avg Relevance", f"{avg_rel:.0%}")

        with col3:
            new_count = client_stats.get("events_by_status", {}).get("new", 0)
            st.metric("New Events", new_count)

        # Events by type
        if client_stats.get("events_by_type"):
            st.markdown("**Events by Type:**")
            events_by_type = client_stats["events_by_type"]
            for event_type, count in events_by_type.items():
                st.markdown(f"- {event_type}: {count}")


# ==================== Tab 3: Events ====================

def render_events_tab(storage: SQLiteStorage):
    """Render events management tab."""
    st.subheader("Event Management")

    # Get all clients for filter
    clients = storage.get_all_clients()
    client_options = ["All Clients"] + [c.name for c in clients]

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_client = st.selectbox("Filter by Client", client_options)

    with col2:
        days_back = st.slider("Days Back", 1, 90, 30)

    with col3:
        min_relevance = st.slider("Min Relevance", 0.0, 1.0, 0.0, 0.1)

    # Get events
    if selected_client == "All Clients":
        events = storage.get_recent_events(days=days_back, min_relevance=min_relevance, limit=100)
    else:
        client = next(c for c in clients if c.name == selected_client)
        events = storage.get_events_by_client(client.id, limit=100)
        events = [e for e in events if e.relevance_score >= min_relevance]

    st.markdown(f"**Showing {len(events)} events**")

    if not events:
        st.info("No events match your filters.")
        return

    # Event type colors
    event_colors = {
        "funding": "🟢",
        "acquisition": "🔵",
        "leadership": "🟡",
        "product": "🟣",
        "news": "⚪",
        "other": "⚫",
    }

    # Display events as cards
    for event in events[:20]:  # Limit to 20 for performance
        # Get client name
        client = storage.get_client(event.client_id)
        client_name = client.name if client else "Unknown"

        color_icon = event_colors.get(event.event_type, "⚪")
        relevance_color = "🟢" if event.relevance_score >= 0.7 else "🟡" if event.relevance_score >= 0.4 else "🔴"

        with st.expander(f"{color_icon} {relevance_color} **{event.title}**"):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"**Type:** {event.event_type}")

            with col2:
                st.markdown(f"**Client:** {client_name}")

            with col3:
                st.markdown(f"**Relevance:** {event.relevance_score:.0%}")

            with col4:
                st.markdown(f"**Sentiment:** {event.sentiment}")

            st.markdown(f"**Summary:** {event.summary}")
            st.markdown(f"**Source:** [{event.source_name}]({event.source_url})")
            st.markdown(f"**Published:** {format_datetime_ago(event.published_date)}")
            st.markdown(f"**Status:** {event.status}")

            if event.tags:
                st.markdown(f"**Tags:** {', '.join(event.tags)}")

            # Status update buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Mark Reviewed", key=f"review_{event.id}"):
                    storage.update_event(event.id, {"status": "reviewed"})
                    st.success("Status updated!")
                    st.rerun()

            with col2:
                if st.button("Mark Actioned", key=f"action_{event.id}"):
                    storage.update_event(event.id, {"status": "actioned"})
                    st.success("Status updated!")
                    st.rerun()

            with col3:
                if st.button("Archive", key=f"archive_{event.id}"):
                    storage.update_event(event.id, {"status": "archived"})
                    st.success("Archived!")
                    st.rerun()


# ==================== Tab 4: Cache ====================

def render_cache_tab(storage: SQLiteStorage):
    """Render cache management tab."""
    st.subheader("Cache Management")

    # Get cache stats
    stats = storage.get_statistics()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Cache Entries", stats.get("total_cache_entries", 0))

    with col2:
        st.metric("Valid Entries", stats.get("valid_cache_entries", 0))

    with col3:
        expired = stats.get("total_cache_entries", 0) - stats.get("valid_cache_entries", 0)
        st.metric("Expired Entries", expired)

    st.divider()

    # Cache management actions
    st.markdown("### ⚙️ Cache Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🧹 Clear Expired Cache", use_container_width=True):
            try:
                count = storage.delete_expired_cache()
                st.success(f"Deleted {count} expired entries")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    with col2:
        if st.button("🗑️ Clear All Cache", use_container_width=True, type="secondary"):
            if st.session_state.get("confirm_clear_cache"):
                try:
                    count = storage.clear_all_cache()
                    st.success(f"Cleared {count} cache entries")
                    st.session_state.confirm_clear_cache = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.session_state.confirm_clear_cache = True
                st.warning("Click again to confirm")

    with col3:
        if st.button("➕ Add Sample Cache", use_container_width=True):
            from src.models import SearchCacheDTO
            cache = SearchCacheDTO.create_sample(
                query=f"Test Query {datetime.now().strftime('%H:%M:%S')}",
                api_source="mock",
                ttl_hours=24
            )
            try:
                storage.create_cache(cache)
                st.success("Added sample cache entry")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()

    # Display cache entries
    st.markdown("### 💾 Cache Entries")

    # Note: We can't easily retrieve all cache entries with current interface
    # Let's add a note about this
    st.info("Cache entries are stored efficiently but not all are displayed here. Use the statistics above to monitor cache usage.")

    # Show cache hit rate (if we track this)
    st.markdown("### 📊 Cache Performance")

    col1, col2 = st.columns(2)

    with col1:
        total = stats.get("total_cache_entries", 0)
        valid = stats.get("valid_cache_entries", 0)
        hit_rate = (valid / total * 100) if total > 0 else 0
        st.metric("Cache Validity Rate", f"{hit_rate:.1f}%")

    with col2:
        st.metric("Storage Efficiency", "Good" if hit_rate > 50 else "Review")


if __name__ == "__main__":
    render_database_page()
