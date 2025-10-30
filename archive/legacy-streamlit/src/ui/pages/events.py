"""Comprehensive event management interface - the main workspace for client intelligence."""

import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
from collections import defaultdict
import re

from src.storage import SQLiteStorage
from src.models.event_dto import EventDTO


# Event type icons and colors
EVENT_TYPE_CONFIG = {
    "funding": {"icon": "💰", "color": "#10b981", "label": "Funding"},
    "acquisition": {"icon": "🤝", "color": "#3b82f6", "label": "Acquisition"},
    "leadership": {"icon": "👔", "color": "#8b5cf6", "label": "Leadership"},
    "product": {"icon": "🚀", "color": "#f59e0b", "label": "Product"},
    "partnership": {"icon": "🔗", "color": "#06b6d4", "label": "Partnership"},
    "financial": {"icon": "📊", "color": "#14b8a6", "label": "Financial"},
    "award": {"icon": "🏆", "color": "#fbbf24", "label": "Award"},
    "regulatory": {"icon": "⚖️", "color": "#ef4444", "label": "Regulatory"},
    "news": {"icon": "📰", "color": "#6366f1", "label": "News"},
    "other": {"icon": "📌", "color": "#6b7280", "label": "Other"},
}

SENTIMENT_CONFIG = {
    "positive": {"emoji": "😊", "color": "#10b981"},
    "neutral": {"emoji": "😐", "color": "#6b7280"},
    "negative": {"emoji": "😟", "color": "#ef4444"},
}


def highlight_search_text(text: str, search_term: str) -> str:
    """Highlight search term in text."""
    if not search_term or not text:
        return text

    pattern = re.compile(f"({re.escape(search_term)})", re.IGNORECASE)
    return pattern.sub(r"**\1**", text)


def get_related_events(event: EventDTO, all_events: List[EventDTO], limit: int = 5) -> List[EventDTO]:
    """Find related events (same client or similar type)."""
    related = []

    # Same client events
    same_client = [e for e in all_events
                   if e.client_id == event.client_id and e.id != event.id]
    related.extend(same_client[:3])

    # Similar type events
    if len(related) < limit:
        same_type = [e for e in all_events
                    if e.event_type == event.event_type
                    and e.id != event.id
                    and e.client_id != event.client_id]
        needed = limit - len(related)
        related.extend(same_type[:needed])

    return related[:limit]


def render_event_detail_modal(event: EventDTO, client_name: str, storage: SQLiteStorage, all_events: List[EventDTO]):
    """Render full-screen event detail modal."""
    config = EVENT_TYPE_CONFIG.get(event.event_type, EVENT_TYPE_CONFIG["other"])
    sentiment_config = SENTIMENT_CONFIG.get(event.sentiment, SENTIMENT_CONFIG["neutral"])

    # Close button
    if st.button("✕ Close", key="close_detail"):
        del st.session_state.viewing_event_id
        st.rerun()

    st.markdown("---")

    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"## {event.title}")
        st.caption(f"**{client_name}** · {config['icon']} {config['label']} · {event.published_date.strftime('%B %d, %Y')}")

    with col2:
        # Relevance badge
        if event.relevance_score >= 0.7:
            relevance_color = "#10b981"
            relevance_label = "High"
        elif event.relevance_score >= 0.4:
            relevance_color = "#f59e0b"
            relevance_label = "Medium"
        else:
            relevance_color = "#6b7280"
            relevance_label = "Low"

        st.markdown(f"""
        <div style="text-align: right;">
            <div style="background-color: {relevance_color}; color: white;
                        padding: 8px 16px; border-radius: 16px; font-weight: 600;
                        display: inline-block; margin-bottom: 8px;">
                {relevance_label} Relevance<br/>
                {event.relevance_score:.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        # Summary
        st.subheader("📄 Summary")
        if event.summary:
            st.write(event.summary)
        else:
            st.info("No summary available")

        st.divider()

        # Metadata
        st.subheader("ℹ️ Details")
        meta_col1, meta_col2, meta_col3 = st.columns(3)

        with meta_col1:
            st.write(f"**Sentiment:** {sentiment_config['emoji']} {event.sentiment.capitalize()}")
            if event.sentiment_score:
                st.caption(f"Score: {event.sentiment_score:.2f}")

        with meta_col2:
            status_icons = {"new": "🆕", "reviewed": "👁️", "actioned": "✅", "archived": "📦"}
            st.write(f"**Status:** {status_icons.get(event.status, '📌')} {event.status.capitalize()}")

        with meta_col3:
            if event.source_name:
                st.write(f"**Source:** {event.source_name}")

        if event.source_url:
            st.markdown(f"[🔗 View Original Source]({event.source_url})")

        # Tags
        st.divider()
        st.subheader("🏷️ Tags")

        # Display existing tags
        if event.tags:
            tag_cols = st.columns(min(len(event.tags), 5))
            for idx, tag in enumerate(event.tags):
                with tag_cols[idx % 5]:
                    st.markdown(f"`{tag}`")

        # Add new tag
        new_tag_col1, new_tag_col2 = st.columns([3, 1])
        with new_tag_col1:
            new_tag = st.text_input("Add tag", key=f"new_tag_{event.id}", label_visibility="collapsed",
                                   placeholder="Enter new tag...")
        with new_tag_col2:
            if st.button("➕ Add", key=f"add_tag_{event.id}") and new_tag:
                updated_tags = list(event.tags) if event.tags else []
                if new_tag not in updated_tags:
                    updated_tags.append(new_tag)
                    storage.update_event(event.id, {"tags": updated_tags})
                    st.success(f"Tag '{new_tag}' added!")
                    st.rerun()

        # Notes
        st.divider()
        st.subheader("📝 Notes")
        notes = st.text_area(
            "Event notes",
            value=event.user_notes or "",
            height=150,
            key=f"detail_notes_{event.id}",
            placeholder="Add your notes here...",
            label_visibility="collapsed"
        )
        if st.button("💾 Save Notes", key=f"save_detail_notes_{event.id}", type="primary"):
            storage.update_event(event.id, {"user_notes": notes})
            st.success("✅ Notes saved!")
            st.rerun()

    with col2:
        # Quick actions
        st.subheader("⚡ Quick Actions")

        if event.status != "reviewed":
            if st.button("👁️ Mark as Reviewed", key=f"detail_review_{event.id}", use_container_width=True):
                storage.update_event(event.id, {"status": "reviewed"})
                st.rerun()

        if event.status != "actioned":
            if st.button("✅ Mark as Actioned", key=f"detail_action_{event.id}", use_container_width=True):
                storage.update_event(event.id, {"status": "actioned"})
                st.rerun()

        if event.status != "archived":
            if st.button("📦 Archive", key=f"detail_archive_{event.id}", use_container_width=True):
                storage.update_event(event.id, {"status": "archived"})
                st.rerun()

        if st.button("🗑️ Delete Event", key=f"detail_delete_{event.id}", type="secondary", use_container_width=True):
            st.session_state.confirm_delete_detail = True

        if st.session_state.get("confirm_delete_detail", False):
            st.warning("⚠️ Delete event?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes", key=f"yes_delete_detail_{event.id}", type="primary"):
                    storage.delete_event(event.id)
                    del st.session_state.viewing_event_id
                    if "confirm_delete_detail" in st.session_state:
                        del st.session_state.confirm_delete_detail
                    st.rerun()
            with col2:
                if st.button("No", key=f"no_delete_detail_{event.id}"):
                    del st.session_state.confirm_delete_detail
                    st.rerun()

        st.divider()

        # Related events
        st.subheader("🔗 Related Events")
        related = get_related_events(event, all_events)

        if related:
            for rel_event in related:
                rel_client = storage.get_client(rel_event.client_id)
                rel_client_name = rel_client.name if rel_client else "Unknown"
                rel_config = EVENT_TYPE_CONFIG.get(rel_event.event_type, EVENT_TYPE_CONFIG["other"])

                with st.expander(f"{rel_config['icon']} {rel_client_name}", expanded=False):
                    st.caption(rel_event.title[:80] + "..." if len(rel_event.title) > 80 else rel_event.title)
                    if st.button("View", key=f"view_related_{rel_event.id}"):
                        st.session_state.viewing_event_id = rel_event.id
                        st.rerun()
        else:
            st.info("No related events found")


def render_quick_stats(events: List[EventDTO]):
    """Render quick stats bar at the top."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📊 Total Events", len(events))

    with col2:
        new_count = len([e for e in events if e.status == "new"])
        st.metric("🆕 New", new_count)

    with col3:
        if events:
            avg_relevance = sum(e.relevance_score for e in events) / len(events)
            st.metric("⭐ Avg Relevance", f"{avg_relevance:.2f}")
        else:
            st.metric("⭐ Avg Relevance", "—")

    with col4:
        if events:
            type_counts = defaultdict(int)
            for e in events:
                type_counts[e.event_type] += 1
            most_common = max(type_counts.items(), key=lambda x: x[1])
            config = EVENT_TYPE_CONFIG.get(most_common[0], EVENT_TYPE_CONFIG["other"])
            st.metric("🔥 Most Common", f"{config['icon']} {config['label']}")
        else:
            st.metric("🔥 Most Common", "—")


def render_bulk_actions(selected_event_ids: List[str], storage: SQLiteStorage):
    """Render bulk actions UI."""
    if not selected_event_ids:
        return

    st.markdown(f"**{len(selected_event_ids)} event(s) selected**")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        bulk_action = st.selectbox(
            "Bulk Action",
            ["Choose action...", "Mark as Reviewed", "Mark as Actioned", "Archive All", "Delete All", "Export Selected"],
            key="bulk_action_select"
        )

    with col2:
        if st.button("▶ Apply", disabled=bulk_action == "Choose action...", type="primary", use_container_width=True):
            st.session_state.confirm_bulk_action = bulk_action

    with col3:
        if st.button("✕ Clear Selection", use_container_width=True):
            st.session_state.selected_events = []
            st.rerun()

    # Confirmation for bulk actions
    if st.session_state.get("confirm_bulk_action"):
        action = st.session_state.confirm_bulk_action

        if action == "Export Selected":
            # Export immediately without confirmation
            events_to_export = []
            for event_id in selected_event_ids:
                event = storage.get_event(event_id)
                if event:
                    client = storage.get_client(event.client_id)
                    events_to_export.append({
                        "Client": client.name if client else "Unknown",
                        "Title": event.title,
                        "Type": event.event_type,
                        "Date": event.published_date.strftime("%Y-%m-%d"),
                        "Relevance": event.relevance_score,
                        "Sentiment": event.sentiment,
                        "Status": event.status,
                        "Summary": event.summary or "",
                        "Notes": event.user_notes or "",
                    })

            df = pd.DataFrame(events_to_export)
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"events_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            del st.session_state.confirm_bulk_action
        else:
            # Show confirmation for destructive actions
            st.warning(f"⚠️ Confirm: **{action}** for {len(selected_event_ids)} events?")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Confirm", key="confirm_bulk", type="primary", use_container_width=True):
                    for event_id in selected_event_ids:
                        if action == "Mark as Reviewed":
                            storage.update_event(event_id, {"status": "reviewed"})
                        elif action == "Mark as Actioned":
                            storage.update_event(event_id, {"status": "actioned"})
                        elif action == "Archive All":
                            storage.update_event(event_id, {"status": "archived"})
                        elif action == "Delete All":
                            storage.delete_event(event_id)

                    st.session_state.selected_events = []
                    del st.session_state.confirm_bulk_action
                    st.success(f"✅ {action} completed!")
                    st.rerun()

            with col2:
                if st.button("❌ Cancel", key="cancel_bulk", use_container_width=True):
                    del st.session_state.confirm_bulk_action
                    st.rerun()


def render_filters_sidebar(storage: SQLiteStorage) -> Dict[str, Any]:
    """Render filters in sidebar."""
    st.sidebar.markdown("### 🔍 Filters")

    # Search
    search_term = st.sidebar.text_input(
        "🔎 Search",
        placeholder="Search titles and summaries...",
        key="event_search"
    )

    st.sidebar.divider()

    # Date range
    st.sidebar.markdown("**Date Range**")
    date_preset = st.sidebar.radio(
        "Quick select",
        ["Today", "Last 7 days", "Last 30 days", "Last 90 days", "All time"],
        index=1,
        label_visibility="collapsed"
    )

    if date_preset == "Today":
        from_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_preset == "Last 7 days":
        from_date = datetime.utcnow() - timedelta(days=7)
    elif date_preset == "Last 30 days":
        from_date = datetime.utcnow() - timedelta(days=30)
    elif date_preset == "Last 90 days":
        from_date = datetime.utcnow() - timedelta(days=90)
    else:
        from_date = None

    st.sidebar.divider()

    # Client filter
    all_clients = storage.get_all_clients()
    client_options = ["All Clients"] + [c.name for c in all_clients]
    selected_clients = st.sidebar.multiselect(
        "📊 Clients",
        options=client_options,
        default=["All Clients"]
    )

    # Event type filter
    event_type_labels = [f"{config['icon']} {config['label']}"
                         for config in EVENT_TYPE_CONFIG.values()]
    selected_event_types = st.sidebar.multiselect(
        "🏷️ Event Types",
        options=["All Types"] + event_type_labels,
        default=["All Types"]
    )

    # Sentiment filter
    sentiment_options = [f"{config['emoji']} {sentiment.capitalize()}"
                        for sentiment, config in SENTIMENT_CONFIG.items()]
    selected_sentiments = st.sidebar.multiselect(
        "😊 Sentiment",
        options=["All Sentiments"] + sentiment_options,
        default=["All Sentiments"]
    )

    # Status filter
    status_options = ["New", "Reviewed", "Actioned", "Archived"]
    selected_statuses = st.sidebar.multiselect(
        "📋 Status",
        options=["All Statuses"] + status_options,
        default=["All Statuses"]
    )

    # Relevance score
    st.sidebar.markdown("**Relevance Score**")
    min_relevance = st.sidebar.slider(
        "Minimum relevance",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1,
        label_visibility="collapsed"
    )

    st.sidebar.divider()

    # Action buttons
    if st.sidebar.button("🔄 Clear Filters", use_container_width=True):
        # Clear filter-related session state
        for key in list(st.session_state.keys()):
            if 'event_search' in key or 'selected_events' in key:
                del st.session_state[key]
        st.rerun()

    return {
        "search_term": search_term,
        "from_date": from_date,
        "selected_clients": selected_clients,
        "selected_event_types": selected_event_types,
        "selected_sentiments": selected_sentiments,
        "selected_statuses": selected_statuses,
        "min_relevance": min_relevance,
    }


def apply_filters(events: List[EventDTO], filters: Dict[str, Any], storage: SQLiteStorage) -> List[EventDTO]:
    """Apply all filters to events list."""
    filtered = events.copy()

    # Search filter
    if filters["search_term"]:
        search_lower = filters["search_term"].lower()
        filtered = [e for e in filtered
                   if (search_lower in e.title.lower()) or
                      (e.summary and search_lower in e.summary.lower())]

    # Date filter
    if filters["from_date"]:
        filtered = [e for e in filtered if e.discovered_date >= filters["from_date"]]

    # Client filter
    if "All Clients" not in filters["selected_clients"] and filters["selected_clients"]:
        client_ids = []
        for client_name in filters["selected_clients"]:
            clients = [c for c in storage.get_all_clients() if c.name == client_name]
            if clients:
                client_ids.append(clients[0].id)
        filtered = [e for e in filtered if e.client_id in client_ids]

    # Event type filter
    if "All Types" not in filters["selected_event_types"] and filters["selected_event_types"]:
        selected_types = []
        for label in filters["selected_event_types"]:
            for event_type, config in EVENT_TYPE_CONFIG.items():
                if config["label"] in label:
                    selected_types.append(event_type)
        filtered = [e for e in filtered if e.event_type in selected_types]

    # Sentiment filter
    if "All Sentiments" not in filters["selected_sentiments"] and filters["selected_sentiments"]:
        selected_sentiments = []
        for label in filters["selected_sentiments"]:
            for sentiment in SENTIMENT_CONFIG.keys():
                if sentiment.capitalize() in label:
                    selected_sentiments.append(sentiment)
        filtered = [e for e in filtered if e.sentiment in selected_sentiments]

    # Status filter
    if "All Statuses" not in filters["selected_statuses"] and filters["selected_statuses"]:
        status_map = {"New": "new", "Reviewed": "reviewed", "Actioned": "actioned", "Archived": "archived"}
        selected_statuses = [status_map[s] for s in filters["selected_statuses"]]
        filtered = [e for e in filtered if e.status in selected_statuses]

    # Relevance filter
    filtered = [e for e in filtered if e.relevance_score >= filters["min_relevance"]]

    return filtered


def render_event_card_compact(event: EventDTO, client_name: str, storage: SQLiteStorage,
                              search_term: str = "", show_checkbox: bool = True):
    """Render a compact event card for list view."""
    config = EVENT_TYPE_CONFIG.get(event.event_type, EVENT_TYPE_CONFIG["other"])
    sentiment_config = SENTIMENT_CONFIG.get(event.sentiment, SENTIMENT_CONFIG["neutral"])

    # Relevance color
    if event.relevance_score >= 0.7:
        relevance_color = "#10b981"
    elif event.relevance_score >= 0.4:
        relevance_color = "#f59e0b"
    else:
        relevance_color = "#6b7280"

    with st.container(border=True):
        # Header row with checkbox
        header_cols = st.columns([0.3, 3, 1, 1]) if show_checkbox else st.columns([3, 1, 1])

        col_idx = 0
        if show_checkbox:
            with header_cols[col_idx]:
                selected = st.checkbox(
                    "Select",
                    key=f"select_{event.id}",
                    value=event.id in st.session_state.get("selected_events", []),
                    label_visibility="collapsed"
                )
                if selected and event.id not in st.session_state.get("selected_events", []):
                    if "selected_events" not in st.session_state:
                        st.session_state.selected_events = []
                    st.session_state.selected_events.append(event.id)
                elif not selected and event.id in st.session_state.get("selected_events", []):
                    st.session_state.selected_events.remove(event.id)
            col_idx = 1

        with header_cols[col_idx]:
            st.markdown(f"**{client_name}** · {config['icon']} {config['label']}")

        with header_cols[col_idx + 1]:
            days_ago = (datetime.utcnow() - event.published_date).days
            if days_ago == 0:
                date_str = "Today"
            elif days_ago == 1:
                date_str = "Yesterday"
            else:
                date_str = f"{days_ago}d ago"
            st.caption(date_str)

        with header_cols[col_idx + 2]:
            st.markdown(f"""
            <div style="text-align: right;">
                <span style="background-color: {relevance_color}; color: white;
                             padding: 2px 8px; border-radius: 10px; font-size: 0.75em;">
                    {event.relevance_score:.2f}
                </span>
            </div>
            """, unsafe_allow_html=True)

        # Title (clickable to open detail)
        title_text = highlight_search_text(event.title, search_term)
        if st.button(f"{title_text}", key=f"title_{event.id}", use_container_width=True):
            st.session_state.viewing_event_id = event.id
            st.rerun()

        # Summary preview
        if event.summary:
            summary_preview = event.summary[:150] + "..." if len(event.summary) > 150 else event.summary
            summary_text = highlight_search_text(summary_preview, search_term)
            st.caption(summary_text)

        # Metadata row
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.write(f"{sentiment_config['emoji']} {event.sentiment.capitalize()}")

        with col2:
            status_icons = {"new": "🆕", "reviewed": "👁️", "actioned": "✅", "archived": "📦"}
            st.write(f"{status_icons.get(event.status, '📌')} {event.status.capitalize()}")

        with col3:
            if event.source_name:
                st.caption(f"📰 {event.source_name}")

        with col4:
            if event.user_notes:
                st.caption("📝 Has notes")

        # Tags
        if event.tags:
            st.markdown(" ".join([f"`{tag}`" for tag in event.tags[:5]]))

        # Quick actions
        action_cols = st.columns(5)

        with action_cols[0]:
            if event.status != "reviewed" and st.button("✓ Reviewed", key=f"review_{event.id}", use_container_width=True):
                storage.update_event(event.id, {"status": "reviewed"})
                st.rerun()

        with action_cols[1]:
            if event.status != "actioned" and st.button("✓ Actioned", key=f"action_{event.id}", use_container_width=True):
                storage.update_event(event.id, {"status": "actioned"})
                st.rerun()

        with action_cols[2]:
            if event.status != "archived" and st.button("📦 Archive", key=f"archive_{event.id}", use_container_width=True):
                storage.update_event(event.id, {"status": "archived"})
                st.rerun()

        with action_cols[3]:
            if event.source_url:
                st.link_button("🔗 Source", event.source_url, use_container_width=True)

        with action_cols[4]:
            if st.button("ℹ️ Details", key=f"details_{event.id}", use_container_width=True):
                st.session_state.viewing_event_id = event.id
                st.rerun()


def render_list_view(events: List[EventDTO], storage: SQLiteStorage, search_term: str = ""):
    """Render events in list view with checkboxes."""
    if not events:
        st.info("📭 No events found matching your filters")
        return

    # Sort options
    col1, col2 = st.columns([3, 1])
    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["Relevance (High to Low)", "Date (Newest First)", "Date (Oldest First)", "Client Name"],
            label_visibility="collapsed"
        )

    # Sort events
    if sort_by == "Relevance (High to Low)":
        events_sorted = sorted(events, key=lambda e: e.relevance_score, reverse=True)
    elif sort_by == "Date (Newest First)":
        events_sorted = sorted(events, key=lambda e: e.published_date, reverse=True)
    elif sort_by == "Date (Oldest First)":
        events_sorted = sorted(events, key=lambda e: e.published_date)
    else:  # Client Name
        events_sorted = sorted(events, key=lambda e: storage.get_client(e.client_id).name if storage.get_client(e.client_id) else "")

    # Initialize selected_events in session state
    if "selected_events" not in st.session_state:
        st.session_state.selected_events = []

    # Bulk actions bar
    render_bulk_actions(st.session_state.selected_events, storage)

    st.divider()

    # Pagination
    items_per_page = 20
    total_pages = (len(events_sorted) + items_per_page - 1) // items_per_page

    if "events_page" not in st.session_state:
        st.session_state.events_page = 1

    start_idx = (st.session_state.events_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(events_sorted))

    # Render events
    for event in events_sorted[start_idx:end_idx]:
        client = storage.get_client(event.client_id)
        client_name = client.name if client else "Unknown Client"
        render_event_card_compact(event, client_name, storage, search_term, show_checkbox=True)

    # Pagination controls
    if total_pages > 1:
        st.divider()
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("◀ Previous", disabled=st.session_state.events_page == 1):
                st.session_state.events_page -= 1
                st.rerun()

        with col2:
            st.markdown(f"<div style='text-align: center;'>Page {st.session_state.events_page} of {total_pages}</div>",
                       unsafe_allow_html=True)

        with col3:
            if st.button("Next ▶", disabled=st.session_state.events_page == total_pages):
                st.session_state.events_page += 1
                st.rerun()


def render_timeline_view(events: List[EventDTO], storage: SQLiteStorage):
    """Render events in timeline view."""
    if not events:
        st.info("📭 No events found matching your filters")
        return

    # Group by date
    events_by_date = defaultdict(list)
    for event in sorted(events, key=lambda e: e.published_date, reverse=True):
        date_key = event.published_date.strftime("%Y-%m-%d")
        events_by_date[date_key].append(event)

    # Render timeline
    for date_str, date_events in events_by_date.items():
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        days_ago = (datetime.utcnow() - date_obj).days

        if days_ago == 0:
            date_label = "Today"
        elif days_ago == 1:
            date_label = "Yesterday"
        else:
            date_label = date_obj.strftime("%B %d, %Y")

        st.markdown(f"### 📅 {date_label}")
        st.caption(f"{len(date_events)} event(s)")

        for event in date_events:
            client = storage.get_client(event.client_id)
            client_name = client.name if client else "Unknown Client"
            render_event_card_compact(event, client_name, storage, show_checkbox=False)

        st.divider()


def render_table_view(events: List[EventDTO], storage: SQLiteStorage):
    """Render events in table view."""
    if not events:
        st.info("📭 No events found matching your filters")
        return

    # Prepare data
    data = []
    for event in events:
        client = storage.get_client(event.client_id)
        client_name = client.name if client else "Unknown"

        config = EVENT_TYPE_CONFIG.get(event.event_type, EVENT_TYPE_CONFIG["other"])

        data.append({
            "Client": client_name,
            "Title": event.title[:60] + "..." if len(event.title) > 60 else event.title,
            "Type": f"{config['icon']} {config['label']}",
            "Date": event.published_date.strftime("%Y-%m-%d"),
            "Relevance": event.relevance_score,
            "Sentiment": event.sentiment.capitalize(),
            "Status": event.status.capitalize(),
            "Source": event.source_name or "—",
        })

    df = pd.DataFrame(data)

    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Relevance": st.column_config.ProgressColumn(
                "Relevance",
                min_value=0.0,
                max_value=1.0,
            ),
        }
    )

    # Export button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Export to CSV",
        data=csv,
        file_name=f"events_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )


def render_analytics_view(events: List[EventDTO], storage: SQLiteStorage):
    """Render analytics and charts."""
    if not events:
        st.info("📭 No events found matching your filters")
        return

    # Summary metrics (duplicates quick stats, but with more detail)
    st.subheader("📊 Overview")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Events", len(events))

    with col2:
        new_count = len([e for e in events if e.status == "new"])
        reviewed_count = len([e for e in events if e.status == "reviewed"])
        st.metric("New / Reviewed", f"{new_count} / {reviewed_count}")

    with col3:
        avg_relevance = sum(e.relevance_score for e in events) / len(events)
        st.metric("Avg Relevance", f"{avg_relevance:.2f}")

    with col4:
        unique_clients = len(set(e.client_id for e in events))
        st.metric("Unique Clients", unique_clients)

    with col5:
        positive_count = len([e for e in events if e.sentiment == "positive"])
        positive_pct = (positive_count / len(events)) * 100
        st.metric("Positive Sentiment", f"{positive_pct:.0f}%")

    st.divider()

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Events by Type")
        type_counts = defaultdict(int)
        for event in events:
            type_counts[event.event_type] += 1

        type_data = pd.DataFrame([
            {"Type": EVENT_TYPE_CONFIG.get(t, EVENT_TYPE_CONFIG["other"])["label"], "Count": c}
            for t, c in type_counts.items()
        ])
        st.bar_chart(type_data.set_index("Type"))

    with col2:
        st.subheader("😊 Sentiment Distribution")
        sentiment_counts = defaultdict(int)
        for event in events:
            sentiment_counts[event.sentiment] += 1

        sentiment_data = pd.DataFrame([
            {"Sentiment": s.capitalize(), "Count": c}
            for s, c in sentiment_counts.items()
        ])
        st.bar_chart(sentiment_data.set_index("Sentiment"))

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Top Clients by Events")
        client_counts = defaultdict(int)
        for event in events:
            client = storage.get_client(event.client_id)
            if client:
                client_counts[client.name] += 1

        top_clients = sorted(client_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        client_data = pd.DataFrame(top_clients, columns=["Client", "Events"])
        st.bar_chart(client_data.set_index("Client"))

    with col2:
        st.subheader("📰 Top Sources")
        source_counts = defaultdict(int)
        for event in events:
            if event.source_name:
                source_counts[event.source_name] += 1

        top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        if top_sources:
            source_data = pd.DataFrame(top_sources, columns=["Source", "Events"])
            st.bar_chart(source_data.set_index("Source"))
        else:
            st.info("No source data available")

    st.divider()

    # Relevance distribution
    st.subheader("📈 Relevance Score Distribution")
    relevance_buckets = {"0.0-0.3": 0, "0.3-0.5": 0, "0.5-0.7": 0, "0.7-1.0": 0}
    for event in events:
        if event.relevance_score < 0.3:
            relevance_buckets["0.0-0.3"] += 1
        elif event.relevance_score < 0.5:
            relevance_buckets["0.3-0.5"] += 1
        elif event.relevance_score < 0.7:
            relevance_buckets["0.5-0.7"] += 1
        else:
            relevance_buckets["0.7-1.0"] += 1

    relevance_data = pd.DataFrame([
        {"Range": k, "Count": v}
        for k, v in relevance_buckets.items()
    ])
    st.bar_chart(relevance_data.set_index("Range"))


def render_events_page():
    """Main events page - the primary workspace for client intelligence."""
    # Initialize storage
    storage = SQLiteStorage()
    storage.connect()

    # Check if viewing event detail
    if st.session_state.get("viewing_event_id"):
        event = storage.get_event(st.session_state.viewing_event_id)
        if event:
            client = storage.get_client(event.client_id)
            client_name = client.name if client else "Unknown Client"
            all_events = storage.get_all_events()
            render_event_detail_modal(event, client_name, storage, all_events)
            return
        else:
            # Event not found, clear the state
            del st.session_state.viewing_event_id

    # Normal page view
    st.markdown('<h1 class="main-header">Event Intelligence</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your workspace for reviewing and managing client events</p>', unsafe_allow_html=True)

    # Render filters in sidebar
    filters = render_filters_sidebar(storage)

    # Get all events
    all_events = storage.get_all_events()

    # Apply filters
    filtered_events = apply_filters(all_events, filters, storage)

    # Quick stats
    render_quick_stats(filtered_events)

    st.divider()

    # View selector
    view_mode = st.radio(
        "View Mode",
        ["📋 List", "📅 Timeline", "📊 Table", "📈 Analytics"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.divider()

    # Render selected view
    if view_mode == "📋 List":
        render_list_view(filtered_events, storage, filters.get("search_term", ""))
    elif view_mode == "📅 Timeline":
        render_timeline_view(filtered_events, storage)
    elif view_mode == "📊 Table":
        render_table_view(filtered_events, storage)
    else:  # Analytics
        render_analytics_view(filtered_events, storage)
