"""Collector Test Page - Test news/event collection without paid APIs."""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from src.collectors import get_collector, list_available_collectors


def render_collector_test_page():
    """Render the collector testing page."""
    st.markdown('<h1 class="main-header">🔍 Collector Test Page</h1>', unsafe_allow_html=True)

    st.write("""
    Test the news collector to see how it works before integrating with your client monitoring.
    Currently using the **Mock Collector** which generates realistic fake data at zero cost.
    """)

    # Show available collectors
    with st.expander("📋 Available Collectors", expanded=False):
        collectors = list_available_collectors()

        for name, info in collectors.items():
            status = "✅ Available" if info["available"] else "🚧 Coming Soon"
            requires_key = "🔑 Requires API Key" if info["requires_api_key"] else "🆓 Free"

            st.markdown(f"""
            **{name.upper()}**
            - Status: {status}
            - {requires_key}
            - {info["description"]}
            """)

    st.divider()

    # Initialize collector
    try:
        collector = get_collector()
        st.success(f"✅ Collector initialized: **{collector.collector_name}**")

        # Show rate limit status
        rate_limit = collector.get_rate_limit_status()
        if rate_limit.get("enabled"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Rate Limit", rate_limit.get("limit", "N/A"))
            col2.metric("Remaining", rate_limit.get("remaining", "N/A"))
            reset_time = rate_limit.get("reset_at")
            if reset_time:
                col3.metric("Resets At", reset_time.strftime("%H:%M:%S") if isinstance(reset_time, datetime) else str(reset_time))

    except Exception as e:
        st.error(f"Failed to initialize collector: {e}")
        return

    st.divider()

    # Search interface
    st.subheader("🔎 Test Search")

    col1, col2 = st.columns([2, 1])

    with col1:
        search_query = st.text_input(
            "Search Query",
            placeholder="e.g., Acme Corp funding, TechStartup acquisition, CompanyX CEO",
            help="Try keywords like: funding, acquisition, CEO, product, partnership"
        )

    with col2:
        lookback_days = st.number_input(
            "Lookback Days",
            min_value=7,
            max_value=90,
            value=30,
            step=7,
            help="How many days back to search"
        )

    max_results = st.slider(
        "Max Results",
        min_value=5,
        max_value=50,
        value=10,
        step=5
    )

    # Example queries
    st.caption("💡 **Try these queries:**")
    example_col1, example_col2, example_col3 = st.columns(3)

    with example_col1:
        if st.button("🚀 TechCorp funding"):
            search_query = "TechCorp funding"

    with example_col2:
        if st.button("🤝 Acme Corp acquisition"):
            search_query = "Acme Corp acquisition"

    with example_col3:
        if st.button("👤 StartupXYZ CEO"):
            search_query = "StartupXYZ CEO"

    st.divider()

    # Run search
    if st.button("🔍 Run Search", type="primary", use_container_width=True):
        if not search_query:
            st.warning("Please enter a search query")
            return

        with st.spinner(f"Searching for: **{search_query}** (this may take 0.5-1 second to simulate API latency)..."):
            try:
                # Calculate date range
                to_date = datetime.utcnow()
                from_date = to_date - timedelta(days=lookback_days)

                # Perform search
                start_time = datetime.utcnow()
                results = collector.search(
                    query=search_query,
                    from_date=from_date,
                    to_date=to_date,
                    max_results=max_results
                )
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()

                st.success(f"✅ Found **{len(results)}** results in **{duration:.2f}** seconds")

                # Update rate limit display
                rate_limit = collector.get_rate_limit_status()
                if rate_limit.get("enabled"):
                    st.info(f"📊 Rate limit: {rate_limit['remaining']}/{rate_limit['limit']} requests remaining")

                if results:
                    st.divider()
                    st.subheader(f"📰 Search Results ({len(results)})")

                    # Display results
                    for i, result in enumerate(results, 1):
                        with st.container():
                            st.markdown(f"### {i}. {result.title}")

                            col1, col2, col3 = st.columns([2, 1, 1])

                            with col1:
                                st.caption(f"🗓️ **Published:** {result.published_at.strftime('%Y-%m-%d %H:%M')}")

                            with col2:
                                st.caption(f"📰 **Source:** {result.source}")

                            with col3:
                                category = result.raw_data.get("category", "unknown") if result.raw_data else "unknown"
                                st.caption(f"🏷️ **Category:** {category}")

                            if result.description:
                                st.write(result.description)

                            if result.url:
                                st.markdown(f"[🔗 Read more]({result.url})")

                            # Show raw data in expander
                            if result.raw_data:
                                with st.expander("🔍 View Raw Data"):
                                    st.json(result.raw_data)

                            st.divider()

                    # Results summary table
                    st.subheader("📊 Results Summary")

                    summary_data = []
                    for result in results:
                        summary_data.append({
                            "Title": result.title[:60] + "..." if len(result.title) > 60 else result.title,
                            "Source": result.source,
                            "Published": result.published_at.strftime("%Y-%m-%d"),
                            "Category": result.raw_data.get("category", "N/A") if result.raw_data else "N/A",
                        })

                    df = pd.DataFrame(summary_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)

                else:
                    st.info("No results found for this query")

            except Exception as e:
                st.error(f"Search failed: {e}")
                import traceback
                with st.expander("🐛 Error Details"):
                    st.code(traceback.format_exc())

    # Instructions for integration
    st.divider()
    st.subheader("🔗 Integration Guide")

    st.markdown("""
    ### How to use the collector in your code:

    ```python
    from src.collectors import get_collector

    # Get collector (automatically uses mock by default)
    collector = get_collector()

    # Search for events
    results = collector.search(
        query="TechCorp",
        from_date=datetime.utcnow() - timedelta(days=30),
        max_results=10
    )

    # Get company-specific news
    results = collector.get_company_news(
        company_name="Acme Corp",
        max_results=20
    )

    # Check rate limits
    status = collector.get_rate_limit_status()
    print(f"Remaining: {status['remaining']}/{status['limit']}")
    ```

    ### Keywords that influence results:
    - **funding, investment, raised, series** → Funding announcements
    - **acquisition, merger, buyout** → Acquisition news
    - **CEO, CTO, leadership, executive** → Leadership changes
    - **product, launch, release** → Product announcements
    - **partnership, collaboration** → Partnership news
    - **earnings, revenue, financial** → Financial results
    - **award, recognition** → Awards and recognition

    ### Switching to real APIs:
    Set the `APP_MODE` or `COLLECTOR_TYPE` environment variable:
    ```bash
    export APP_MODE=newsapi  # Use NewsAPI (when implemented)
    export APP_MODE=mock     # Use mock data (default)
    ```
    """)
