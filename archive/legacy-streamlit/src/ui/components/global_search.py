"""
Global Search Component
Unified search across clients, events, and other entities.
"""

import streamlit as st
from typing import List, Dict, Any
from datetime import datetime


def search_clients(storage, query: str) -> List[Dict[str, Any]]:
    """
    Search clients by name, industry, or description.

    Args:
        storage: Storage instance
        query: Search query

    Returns:
        List of matching clients with metadata
    """
    if not query or len(query) < 2:
        return []

    query_lower = query.lower()
    all_clients = storage.get_all_clients()
    results = []

    for client in all_clients:
        # Search in name, industry, description
        searchable_text = " ".join([
            client.name or "",
            client.industry or "",
            client.description or "",
            " ".join(client.keywords or [])
        ]).lower()

        if query_lower in searchable_text:
            results.append({
                "type": "client",
                "id": client.id,
                "title": client.name,
                "subtitle": client.industry or "No industry",
                "description": client.description,
                "icon": "👥",
                "data": client
            })

    return results


def search_events(storage, query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search events by title, summary, or tags.

    Args:
        storage: Storage instance
        query: Search query
        limit: Maximum number of results

    Returns:
        List of matching events with metadata
    """
    if not query or len(query) < 2:
        return []

    query_lower = query.lower()
    all_events = storage.get_all_events()  # Get all events
    results = []

    for event in all_events:
        # Search in title, summary, tags
        searchable_text = " ".join([
            event.title or "",
            event.summary or "",
            event.event_type or "",
            " ".join(event.tags or [])
        ]).lower()

        if query_lower in searchable_text:
            # Get client name
            client = storage.get_client(event.client_id)
            client_name = client.name if client else "Unknown"

            # Get event age
            if hasattr(event, 'published_date'):
                event_date = event.published_date
            elif hasattr(event, 'event_date'):
                event_date = event.event_date
            else:
                event_date = datetime.now()

            days_ago = (datetime.now() - event_date).days

            results.append({
                "type": "event",
                "id": event.id,
                "title": event.title,
                "subtitle": f"{client_name} • {event.event_type.upper() if hasattr(event, 'event_type') else 'EVENT'}",
                "description": event.summary,
                "icon": get_event_icon(event.event_type if hasattr(event, 'event_type') else 'news'),
                "relevance": event.relevance_score if hasattr(event, 'relevance_score') else 0.5,
                "days_ago": days_ago,
                "data": event
            })

            if len(results) >= limit:
                break

    # Sort by relevance
    results.sort(key=lambda x: x.get('relevance', 0), reverse=True)

    return results


def get_event_icon(event_type: str) -> str:
    """Get icon for event type."""
    icon_map = {
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
    return icon_map.get(event_type.lower(), '📌')


def render_global_search(storage):
    """
    Render a global search interface.

    Args:
        storage: Storage instance
    """
    # Search input with icon
    col1, col2 = st.columns([10, 1])

    with col1:
        query = st.text_input(
            "🔍 Search clients, events, and more...",
            placeholder="Search for companies, events, keywords...",
            label_visibility="collapsed",
            key="global_search_input"
        )

    with col2:
        if st.button("🔍", key="global_search_button", help="Search"):
            pass  # Trigger search

    if query and len(query) >= 2:
        # Perform search
        with st.spinner("Searching..."):
            client_results = search_clients(storage, query)
            event_results = search_events(storage, query, limit=15)

            total_results = len(client_results) + len(event_results)

            if total_results == 0:
                st.info(f"No results found for '{query}'")
            else:
                st.success(f"Found {total_results} results for '{query}'")

                # Display results in tabs
                if client_results and event_results:
                    tab1, tab2 = st.tabs([
                        f"👥 Clients ({len(client_results)})",
                        f"📰 Events ({len(event_results)})"
                    ])

                    with tab1:
                        render_client_results(client_results)

                    with tab2:
                        render_event_results(event_results)

                elif client_results:
                    st.markdown("### 👥 Clients")
                    render_client_results(client_results)

                elif event_results:
                    st.markdown("### 📰 Events")
                    render_event_results(event_results)


def render_client_results(results: List[Dict[str, Any]]):
    """Render client search results."""
    for result in results:
        with st.container(border=True):
            col1, col2 = st.columns([8, 2])

            with col1:
                st.markdown(f"**{result['icon']} {result['title']}**")
                st.caption(result['subtitle'])
                if result['description']:
                    st.caption(result['description'][:100] + "..." if len(result['description']) > 100 else result['description'])

            with col2:
                if st.button("View", key=f"view_client_{result['id']}", use_container_width=True):
                    st.session_state['selected_client'] = result['id']
                    st.session_state['page'] = "👥 Clients"
                    st.rerun()


def render_event_results(results: List[Dict[str, Any]]):
    """Render event search results."""
    for result in results:
        # Relevance color
        if result['relevance'] >= 0.7:
            border_color = "#10b981"
        elif result['relevance'] >= 0.4:
            border_color = "#f59e0b"
        else:
            border_color = "#ef4444"

        with st.container(border=True):
            # Add colored indicator
            st.markdown(f"""
            <div style="height: 4px; background-color: {border_color}; border-radius: 2px; margin-bottom: 0.5rem;"></div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([8, 2])

            with col1:
                st.markdown(f"**{result['icon']} {result['title']}**")
                st.caption(result['subtitle'])
                if result['description']:
                    st.caption(result['description'][:150] + "..." if len(result['description']) > 150 else result['description'])

            with col2:
                st.metric("Relevance", f"{result['relevance']:.0%}")
                days_text = "Today" if result['days_ago'] == 0 else f"{result['days_ago']}d ago"
                st.caption(f"📅 {days_text}")


def render_quick_search(storage, placeholder: str = "Quick search..."):
    """
    Render a compact quick search bar.

    Args:
        storage: Storage instance
        placeholder: Placeholder text

    Returns:
        Search query or None
    """
    query = st.text_input(
        "🔍 Search",
        placeholder=placeholder,
        label_visibility="collapsed",
        key=f"quick_search_{placeholder}"
    )

    return query if query and len(query) >= 2 else None
