"""
Streamlit page for testing data models.
Allows visual verification that DTOs work correctly.
"""

import streamlit as st
import json
from datetime import datetime
from src.models import ClientDTO, EventDTO, SearchCacheDTO
from src.models.utils import (
    format_datetime_ago,
    sentiment_score_to_label,
    relevance_score_to_label,
)


def render_models_test_page():
    """Render the models testing page."""
    st.title("🧪 Data Models Test Page")
    st.markdown("Generate and inspect sample data models to verify they work correctly.")

    st.divider()

    # Create three columns for the main buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🏢 Generate Sample Client", use_container_width=True, type="primary"):
            st.session_state.sample_client = ClientDTO.create_sample(
                name="Acme Corporation",
                priority="high"
            )

    with col2:
        if st.button("📰 Generate Sample Event", use_container_width=True, type="primary"):
            st.session_state.sample_event = EventDTO.create_sample(
                event_type="funding",
                relevance_score=0.85
            )

    with col3:
        if st.button("💾 Generate Sample Cache", use_container_width=True, type="primary"):
            st.session_state.sample_cache = SearchCacheDTO.create_sample(
                query="Acme Corporation funding",
                api_source="newsapi",
                ttl_hours=24
            )

    st.divider()

    # Display Client Sample
    if hasattr(st.session_state, 'sample_client'):
        st.subheader("🏢 Client Data Model")
        client = st.session_state.sample_client

        # Validate
        is_valid, error = client.validate()

        if is_valid:
            st.success("✅ Client model created and validated successfully!")
        else:
            st.error(f"❌ Validation failed: {error}")

        # Show in a nice card format
        with st.container():
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Name:** {client.name}")
                st.markdown(f"**Industry:** {client.industry}")
                st.markdown(f"**Domain:** {client.domain}")
                st.markdown(f"**Priority:** {client.priority.upper()}")

            with col2:
                st.metric("Keywords", len(client.keywords))
                st.metric("Active", "Yes" if client.is_active else "No")

            st.markdown(f"**Description:** {client.description}")
            st.markdown(f"**Account Owner:** {client.account_owner}")
            st.markdown(f"**Tier:** {client.tier}")
            st.markdown(f"**Monitoring Since:** {format_datetime_ago(client.monitoring_since)}")

            if client.keywords:
                st.markdown(f"**Keywords:** {', '.join(client.keywords)}")

        # Show raw JSON
        with st.expander("📄 View Raw JSON"):
            st.json(client.to_dict())

        # Show methods demo
        with st.expander("🔧 Test Methods"):
            st.code(f"client.to_dict() -> {len(client.to_dict())} fields")
            st.code(f"client.validate() -> {client.validate()}")
            st.code(f"client.to_json() -> {len(client.to_json())} characters")
            st.code(f"str(client) -> {str(client)}")

        st.divider()

    # Display Event Sample
    if hasattr(st.session_state, 'sample_event'):
        st.subheader("📰 Event Data Model")
        event = st.session_state.sample_event

        # Validate
        is_valid, error = event.validate()

        if is_valid:
            st.success("✅ Event model created and validated successfully!")
        else:
            st.error(f"❌ Validation failed: {error}")

        # Show in a nice card format
        with st.container():
            # Header row
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Event Type", event.event_type.replace("_", " ").title())

            with col2:
                relevance_label = event.get_relevance_label()
                relevance_color = {"high": "🟢", "medium": "🟡", "low": "🔴"}
                st.metric("Relevance", f"{relevance_color.get(relevance_label, '')} {relevance_label.title()}")

            with col3:
                sentiment_emoji = {"positive": "😊", "neutral": "😐", "negative": "😟"}
                st.metric("Sentiment", f"{sentiment_emoji.get(event.sentiment, '')} {event.sentiment.title()}")

            with col4:
                st.metric("Status", event.status.title())

            # Title and summary
            st.markdown(f"### {event.title}")
            st.markdown(f"**Summary:** {event.summary}")

            # Source info
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Source:** [{event.source_name}]({event.source_url})")
                st.markdown(f"**Published:** {format_datetime_ago(event.published_date)}")

            with col2:
                st.markdown(f"**Discovered:** {format_datetime_ago(event.discovered_date)}")
                st.markdown(f"**Relevance Score:** {event.relevance_score:.2%}")

            if event.tags:
                st.markdown(f"**Tags:** {', '.join(event.tags)}")

        # Test relevance checking
        with st.expander("🎯 Test Relevance Checking"):
            thresholds = [0.3, 0.5, 0.7, 0.9]
            st.markdown("**Test `is_relevant()` method:**")

            for threshold in thresholds:
                is_relevant = event.is_relevant(threshold)
                icon = "✅" if is_relevant else "❌"
                st.markdown(f"{icon} `event.is_relevant({threshold})` → {is_relevant}")

        # Test status changes
        with st.expander("🔄 Test Status Changes"):
            st.markdown("**Original Status:** " + event.status)

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Mark as Reviewed"):
                    event.mark_as_reviewed()
                    st.success(f"Status changed to: {event.status}")

            with col2:
                if st.button("Mark as Actioned"):
                    event.mark_as_actioned()
                    st.success(f"Status changed to: {event.status}")

            with col3:
                if st.button("Archive Event"):
                    event.archive()
                    st.success(f"Status changed to: {event.status}")

        # Show raw JSON
        with st.expander("📄 View Raw JSON"):
            st.json(event.to_dict())

        st.divider()

    # Display Cache Sample
    if hasattr(st.session_state, 'sample_cache'):
        st.subheader("💾 Search Cache Data Model")
        cache = st.session_state.sample_cache

        # Validate
        is_valid, error = cache.validate()

        if is_valid:
            st.success("✅ Cache model created and validated successfully!")
        else:
            st.error(f"❌ Validation failed: {error}")

        # Show in a nice card format
        with st.container():
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("API Source", cache.api_source)

            with col2:
                st.metric("Results", cache.result_count)

            with col3:
                status = "✅ Valid" if cache.is_valid() else "⏰ Expired"
                st.metric("Status", status)

            st.markdown(f"**Query:** `{cache.query}`")
            st.markdown(f"**Query Hash:** `{cache.query_hash[:16]}...`")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Cached:** {format_datetime_ago(cache.cached_at)}")
                st.markdown(f"**Cache Age:** {cache.get_cache_age()}")

            with col2:
                st.markdown(f"**Expires:** {cache.expires_at.strftime('%Y-%m-%d %H:%M')}")
                st.markdown(f"**Time Until Expiry:** {cache.time_until_expiry()}")

        # Test expiry checking
        with st.expander("⏰ Test Expiry Logic"):
            st.markdown("**Expiry Status:**")
            st.code(f"cache.is_expired() -> {cache.is_expired()}")
            st.code(f"cache.is_valid() -> {cache.is_valid()}")
            st.code(f"cache.time_until_expiry() -> {cache.time_until_expiry()}")
            st.code(f"cache.get_cache_age() -> {cache.get_cache_age()}")

            st.markdown("**Cache Management:**")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Extend Expiry (+24h)"):
                    cache.extend_expiry(hours=24)
                    st.success(f"Expiry extended! New expiry: {cache.expires_at}")

            with col2:
                if st.button("Refresh Cache"):
                    new_results = [{"title": "New result", "url": "https://example.com"}]
                    cache.refresh(new_results, ttl_hours=48)
                    st.success(f"Cache refreshed! New result count: {cache.result_count}")

        # Show cached results
        with st.expander("📊 View Cached Results"):
            if cache.results:
                for idx, result in enumerate(cache.results, 1):
                    st.markdown(f"**Result {idx}:**")
                    st.json(result)
            else:
                st.info("No cached results")

        # Show raw JSON
        with st.expander("📄 View Raw JSON"):
            st.json(cache.to_dict())

        st.divider()

    # Utility Functions Demo
    st.subheader("🛠️ Utility Functions Demo")

    with st.expander("🔧 Test Utility Functions"):
        from src.models.utils import (
            generate_uuid,
            normalize_relevance_score,
            normalize_sentiment_score,
        )

        st.markdown("**UUID Generation:**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate UUID"):
                uuid = generate_uuid()
                st.code(uuid)
        with col2:
            st.info("Each UUID is unique")

        st.markdown("**Score Normalization:**")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Relevance Score (0.0-1.0):**")
            test_values = [0.5, 1.5, -0.2, 0.85]
            for val in test_values:
                normalized = normalize_relevance_score(val)
                st.code(f"{val} → {normalized}")

        with col2:
            st.markdown("**Sentiment Score (-1.0 to 1.0):**")
            test_values = [0.5, 1.5, -0.8, -2.0]
            for val in test_values:
                normalized = normalize_sentiment_score(val)
                st.code(f"{val} → {normalized}")

        st.markdown("**Time Formatting:**")
        from datetime import timedelta
        now = datetime.utcnow()
        test_times = [
            now - timedelta(seconds=30),
            now - timedelta(minutes=5),
            now - timedelta(hours=2),
            now - timedelta(days=3),
            now - timedelta(days=45),
        ]

        for dt in test_times:
            formatted = format_datetime_ago(dt)
            st.code(f"{dt.isoformat()} → {formatted}")

    # Clear All Button
    st.divider()
    if st.button("🗑️ Clear All Samples", type="secondary"):
        if hasattr(st.session_state, 'sample_client'):
            del st.session_state.sample_client
        if hasattr(st.session_state, 'sample_event'):
            del st.session_state.sample_event
        if hasattr(st.session_state, 'sample_cache'):
            del st.session_state.sample_cache
        st.rerun()


if __name__ == "__main__":
    render_models_test_page()
