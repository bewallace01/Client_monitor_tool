"""Search Test Page - Interactive search interface with mock data."""

import streamlit as st
from datetime import datetime, timedelta
import time
from typing import Optional

from src.collectors import get_collector
from src.storage import SQLiteStorage
from src.models import EventCategory
from src.models.client_dto import ClientDTO
from src.models.event_dto import EventDTO


# Sample queries for quick testing
SAMPLE_QUERIES = [
    "Tesla funding",
    "Microsoft acquisition",
    "Google CEO appointment",
    "Apple product launch",
    "Amazon partnership",
    "Meta earnings report",
    "Netflix product update",
    "Salesforce leadership change",
    "OpenAI funding round",
    "SpaceX launch announcement",
]


def get_sentiment_emoji(sentiment: str) -> str:
    """Get emoji for sentiment."""
    sentiment_map = {
        "positive": "😊",
        "neutral": "😐",
        "negative": "😞",
    }
    return sentiment_map.get(sentiment.lower(), "😐")


def get_relevance_color(score: float) -> str:
    """Get color for relevance score."""
    if score >= 0.7:
        return "green"
    elif score >= 0.4:
        return "orange"
    else:
        return "red"


def detect_event_type(title: str, description: str) -> str:
    """Auto-detect event type from title and description."""
    text = f"{title} {description}".lower()

    if any(word in text for word in ["funding", "raised", "investment", "series"]):
        return "💰 Funding"
    elif any(word in text for word in ["acquisition", "acquires", "merger", "buyout"]):
        return "🤝 Acquisition"
    elif any(word in text for word in ["ceo", "cto", "cfo", "executive", "appoint"]):
        return "👤 Leadership"
    elif any(word in text for word in ["product", "launch", "release", "unveil"]):
        return "🚀 Product"
    elif any(word in text for word in ["partnership", "partner", "collaboration"]):
        return "🤝 Partnership"
    elif any(word in text for word in ["earnings", "revenue", "financial", "profit"]):
        return "💵 Financial"
    elif any(word in text for word in ["award", "recognition", "winner"]):
        return "🏆 Award"
    else:
        return "📰 News"


def detect_sentiment(title: str, description: str) -> str:
    """Auto-detect sentiment from title and description."""
    text = f"{title} {description}".lower()

    positive_words = ["raises", "secures", "wins", "launches", "grows", "expands", "appoints", "announces", "strong", "record"]
    negative_words = ["loses", "fails", "cuts", "declines", "departure", "layoffs", "delays", "misses"]

    positive_count = sum(1 for word in positive_words if word in text)
    negative_count = sum(1 for word in negative_words if word in text)

    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"


def calculate_relevance_score(query: str, title: str, description: str) -> float:
    """Calculate simple relevance score based on keyword matching."""
    query_words = set(query.lower().split())
    text = f"{title} {description}".lower()

    # Count how many query words appear in the text
    matches = sum(1 for word in query_words if word in text and len(word) > 2)

    # Normalize by number of query words
    if len(query_words) > 0:
        score = min(matches / len(query_words), 1.0)
        # Add some randomness to make it realistic
        import random
        score = min(score + random.uniform(0.1, 0.3), 1.0)
        return round(score, 2)

    return 0.5


def save_result_as_event(result, client_id: str, storage: SQLiteStorage):
    """Save a search result as an event in the database."""
    try:
        import uuid

        # Detect event type and sentiment
        event_type = detect_event_type(result.title, result.description or "")
        sentiment = detect_sentiment(result.title, result.description or "")

        # Map event type emoji to event_type string
        event_type_map = {
            "💰 Funding": "funding",
            "🤝 Acquisition": "acquisition",
            "👤 Leadership": "leadership",
            "🚀 Product": "product",
            "🤝 Partnership": "product",  # Map to closest match
            "💵 Financial": "news",
            "🏆 Award": "other",
            "📰 News": "news",
        }
        event_type_str = event_type_map.get(event_type, "other")

        # Create event DTO
        event = EventDTO(
            id=str(uuid.uuid4()),  # Generate new UUID
            client_id=client_id,
            title=result.title,
            summary=result.description,
            source_name=result.source,
            source_url=result.url,
            published_date=result.published_at if result.published_at else datetime.utcnow(),  # Use datetime object
            discovered_date=datetime.utcnow(),  # Use datetime object
            event_type=event_type_str,
            sentiment=sentiment,
            status="new",
            tags=[],
            metadata=result.raw_data or {},
        )

        # Save to database
        storage.create_event(event)
        return True, "Event saved successfully!"

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return False, f"Failed to save event: {str(e)}\n{error_details}"


def render_search_test_page():
    """Render the search test page."""
    st.markdown('<h1 class="main-header">🔍 Search Test</h1>', unsafe_allow_html=True)

    st.write("""
    Test the complete search workflow: search → display → save. Uses the **Mock Collector**
    to generate realistic fake results instantly at zero cost.
    """)

    # Initialize collector and storage
    collector = get_collector()
    storage = SQLiteStorage()
    storage.connect()

    st.divider()

    # Search Interface
    st.subheader("🔎 Search Interface")

    # Two-column layout for search controls
    col1, col2 = st.columns([3, 1])

    with col1:
        # Query input mode selection
        search_mode = st.radio(
            "Search Mode",
            ["Custom Query", "Select Client"],
            horizontal=True,
            label_visibility="collapsed"
        )

    with col2:
        max_results = st.number_input(
            "Max Results",
            min_value=1,
            max_value=20,
            value=5,
            step=1
        )

    # Query input based on mode
    if search_mode == "Custom Query":
        query = st.text_input(
            "Enter search query",
            placeholder="e.g., Acme Corp funding, Tesla acquisition, Microsoft CEO",
            help="Type any company name or event type"
        )

        # Sample queries as buttons
        st.caption("💡 **Quick Examples:**")
        cols = st.columns(5)
        for i, sample in enumerate(SAMPLE_QUERIES[:5]):
            with cols[i]:
                if st.button(sample, key=f"sample_{i}", use_container_width=True):
                    query = sample
                    st.rerun()

        selected_client_id = None

    else:  # Select Client mode
        try:
            clients = storage.get_all_clients()
            if clients:
                client_options = {f"{c.name} ({c.industry or 'N/A'})": c for c in clients}
                selected_name = st.selectbox(
                    "Select Client",
                    options=list(client_options.keys()),
                    help="Search for news about this client"
                )
                selected_client = client_options[selected_name]
                query = selected_client.name
                selected_client_id = selected_client.id
            else:
                st.warning("⚠️ No clients in database. Go to Clients page to add some, or use Custom Query mode.")
                query = ""
                selected_client_id = None
        except Exception as e:
            st.error(f"Failed to load clients: {e}")
            query = ""
            selected_client_id = None

    # Date range
    col1, col2 = st.columns(2)
    with col1:
        lookback_days = st.slider(
            "Lookback Days",
            min_value=7,
            max_value=90,
            value=30,
            step=7,
            help="How far back to search"
        )

    with col2:
        st.metric("Collector", collector.collector_name.upper(), "Zero Cost")

    # Search button
    search_clicked = st.button("🔍 Search Now", type="primary", use_container_width=True)

    st.divider()

    # Initialize session state for search results
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'search_query' not in st.session_state:
        st.session_state.search_query = None
    if 'search_time' not in st.session_state:
        st.session_state.search_time = None
    if 'selected_client_for_results' not in st.session_state:
        st.session_state.selected_client_for_results = None

    # Perform search
    if search_clicked:
        if not query or not query.strip():
            st.warning("⚠️ Please enter a search query")
            return

        # Create two-column layout for results and stats
        results_col, stats_col = st.columns([2, 1])

        with stats_col:
            st.subheader("📊 Search Stats")

            # Show loading stats first
            stats_container = st.container()
            with stats_container:
                st.metric("Query", f'"{query}"')
                st.metric("Collector", collector.collector_name.upper())

                # Rate limit status
                rate_limit = collector.get_rate_limit_status()
                st.metric(
                    "Rate Limit",
                    f"{rate_limit['remaining']}/{rate_limit['limit']}",
                    help="Simulated rate limit (not real)"
                )

        with results_col:
            # Loading spinner
            with st.spinner(f"🔍 Searching for: **{query}**... (simulating API latency)"):
                start_time = time.time()

                # Calculate date range
                to_date = datetime.utcnow()
                from_date = to_date - timedelta(days=lookback_days)

                # Perform search
                try:
                    results = collector.search(
                        query=query,
                        from_date=from_date,
                        to_date=to_date,
                        max_results=max_results
                    )

                    search_time = time.time() - start_time

                    # Store results in session state
                    st.session_state.search_results = results
                    st.session_state.search_query = query
                    st.session_state.search_time = search_time
                    if search_mode == "Select Client" and selected_client_id:
                        st.session_state.selected_client_for_results = selected_client

                except Exception as e:
                    st.error(f"❌ Search failed: {e}")
                    import traceback
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())
                    return

    # Display results from session state (persists across button clicks)
    if st.session_state.search_results is not None:
        results = st.session_state.search_results
        query = st.session_state.search_query
        search_time = st.session_state.search_time
        selected_client = st.session_state.selected_client_for_results

        # Create two-column layout for results and stats
        results_col, stats_col = st.columns([2, 1])

        with stats_col:
            st.subheader("📊 Search Stats")
            st.metric("Query", f'"{query}"')
            st.metric("Collector", collector.collector_name.upper())

            # Rate limit status
            rate_limit = collector.get_rate_limit_status()
            st.metric(
                "Rate Limit",
                f"{rate_limit['remaining']}/{rate_limit['limit']}",
                help="Simulated rate limit (not real)"
            )

            st.metric("Results Found", len(results))
            st.metric("Search Time", f"{search_time:.2f}s")

            if results:
                # Category breakdown
                st.caption("**Categories Found:**")
                categories = {}
                for result in results:
                    cat = detect_event_type(result.title, result.description or "")
                    categories[cat] = categories.get(cat, 0) + 1

                for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"{cat}: {count}")

        with results_col:
            if not results:
                st.info("🔍 No results found. Try a different query or increase the lookback period.")
                return

            # Display results
            st.success(f"✅ Found **{len(results)}** results in **{search_time:.2f}** seconds")

            st.subheader(f"📰 Search Results ({len(results)})")

            for i, result in enumerate(results, 1):
                # Calculate metrics for this result
                relevance_score = calculate_relevance_score(
                    query,
                    result.title,
                    result.description or ""
                )
                event_type = detect_event_type(result.title, result.description or "")
                sentiment = detect_sentiment(result.title, result.description or "")
                sentiment_emoji = get_sentiment_emoji(sentiment)
                relevance_color = get_relevance_color(relevance_score)

                # Result card
                with st.container():
                    # Use colored border based on relevance
                    border_style = f"border-left: 4px solid {relevance_color};"
                    st.markdown(
                        f'<div style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; {border_style} margin-bottom: 1rem;">',
                        unsafe_allow_html=True
                    )

                    # Title with number
                    st.markdown(f"### {i}. {result.title}")

                    # Metadata row
                    meta_col1, meta_col2, meta_col3, meta_col4 = st.columns([2, 2, 1, 1])

                    with meta_col1:
                        st.caption(f"📰 **Source:** {result.source}")

                    with meta_col2:
                        date_str = result.published_at.strftime("%Y-%m-%d %H:%M") if result.published_at else "Unknown"
                        st.caption(f"🗓️ **Published:** {date_str}")

                    with meta_col3:
                        st.caption(f"**Type:** {event_type}")

                    with meta_col4:
                        st.caption(f"**Mood:** {sentiment_emoji}")

                    # Relevance score badge
                    st.markdown(
                        f'<span style="background-color: {relevance_color}; color: white; padding: 0.2rem 0.6rem; '
                        f'border-radius: 0.3rem; font-size: 0.85rem; font-weight: bold;">'
                        f'Relevance: {int(relevance_score * 100)}%</span>',
                        unsafe_allow_html=True
                    )

                    st.write("")  # Spacing

                    # Description
                    if result.description:
                        st.write(result.description)

                    # Action row
                    action_col1, action_col2, action_col3 = st.columns([2, 2, 2])

                    with action_col1:
                        if result.url:
                            st.markdown(f"[🔗 Read Full Article]({result.url})")

                    with action_col2:
                        # Initialize session state for saved events
                        if 'saved_events' not in st.session_state:
                            st.session_state.saved_events = {}

                        result_key = f"{i}_{hash(result.title)}"

                        # Check if this event was already saved
                        if result_key in st.session_state.saved_events:
                            # Show green "Saved" button
                            saved_client_name = st.session_state.saved_events[result_key]
                            st.button(
                                f"✅ Saved to {saved_client_name}",
                                key=f"saved_{result_key}",
                                use_container_width=True,
                                type="primary",
                                disabled=True
                            )
                        else:
                            # Save button logic
                            if selected_client_id and search_mode == "Select Client":
                                # In Select Client mode with client selected
                                save_key = f"save_{result_key}"
                                if st.button(f"💾 Save as Event", key=save_key, use_container_width=True):
                                    success, message = save_result_as_event(result, selected_client_id, storage)
                                    if success:
                                        # Mark as saved in session state
                                        st.session_state.saved_events[result_key] = selected_client.name
                                        st.success(f"✅ Saved to {selected_client.name}!")
                                    else:
                                        st.error(message)
                            else:
                                # In Custom Query mode - use popover for client selection
                                with st.popover("💾 Save to Client...", use_container_width=True):
                                    try:
                                        all_clients = storage.get_all_clients()
                                        if all_clients:
                                            st.write("**Select a client to save this event:**")

                                            # Create a form to handle the save
                                            with st.form(key=f"save_form_{result_key}"):
                                                client_names = [c.name for c in all_clients]
                                                selected_client_name = st.selectbox(
                                                    "Client:",
                                                    options=client_names,
                                                    key=f"client_select_{result_key}"
                                                )

                                                submitted = st.form_submit_button("✅ Save Event", use_container_width=True)

                                                if submitted:
                                                    # Find the client DTO
                                                    selected_client_dto = next(c for c in all_clients if c.name == selected_client_name)
                                                    success, message = save_result_as_event(result, selected_client_dto.id, storage)
                                                    if success:
                                                        st.session_state.saved_events[result_key] = selected_client_name
                                                        st.success(f"✅ Saved to {selected_client_name}!")
                                                        st.rerun()
                                                    else:
                                                        st.error(message)
                                        else:
                                            st.warning("⚠️ No clients available. Go to the Clients page to add some first.")
                                    except Exception as e:
                                        st.error(f"Failed to load clients: {e}")

                    with action_col3:
                        # View raw data
                        if result.raw_data:
                            with st.expander("🔍 Raw Data"):
                                st.json(result.raw_data)

                    st.markdown('</div>', unsafe_allow_html=True)

            # Summary table at the end
            st.divider()
            st.subheader("📊 Results Summary")

            import pandas as pd
            summary_data = []
            for result in results:
                relevance = calculate_relevance_score(query, result.title, result.description or "")
                event_type = detect_event_type(result.title, result.description or "")
                sentiment = detect_sentiment(result.title, result.description or "")

                summary_data.append({
                    "Title": result.title[:50] + "..." if len(result.title) > 50 else result.title,
                    "Source": result.source,
                    "Date": result.published_at.strftime("%Y-%m-%d") if result.published_at else "N/A",
                    "Type": event_type,
                    "Sentiment": sentiment,
                    "Relevance": f"{int(relevance * 100)}%",
                })

            df = pd.DataFrame(summary_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # Instructions section
    st.divider()
    st.subheader("💡 How to Use")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Search Modes:**

        1. **Custom Query** - Type any search term
           - Good for: Testing different keywords
           - Example: "Tesla funding", "Apple CEO"

        2. **Select Client** - Choose from your clients
           - Good for: Finding news for specific clients
           - Can save results directly to that client

        **Tips:**
        - Use specific keywords for better results
        - Try different lookback periods (7-90 days)
        - Check the event type and sentiment auto-detection
        """)

    with col2:
        st.markdown("""
        **Result Features:**

        - **Color-coded relevance** (green/orange/red border)
        - **Auto-detected event type** (Funding, Acquisition, etc.)
        - **Sentiment indicators** (😊 positive, 😐 neutral, 😞 negative)
        - **Relevance score** based on keyword matching
        - **One-click save** to client events

        **What's Fake:**
        - Article content (generated by mock collector)
        - URLs (point to example.com)
        - Rate limits (simulated, not enforced)
        """)

    st.info("""
    **🎯 This is a complete workflow test!** You can search, review results, and save events to your database -
    all without spending a penny on API calls. Perfect for development and testing!
    """)
