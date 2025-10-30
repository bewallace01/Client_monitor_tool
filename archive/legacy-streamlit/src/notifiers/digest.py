"""Digest and report generation for client monitoring."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Literal
from collections import defaultdict

from src.storage import SQLiteStorage
from src.models import EventCategory

logger = logging.getLogger(__name__)


class DigestGenerator:
    """Generate formatted reports and digests from monitoring data."""

    def __init__(self, storage: SQLiteStorage):
        """
        Initialize digest generator.

        Args:
            storage: SQLiteStorage instance for data access
        """
        self.storage = storage

    def generate_daily_digest(
        self,
        date_range: Optional[tuple[datetime, datetime]] = None,
        format: Literal["text", "markdown", "html"] = "markdown",
        title: str = "Daily Intelligence Digest"
    ) -> str:
        """
        Generate daily digest report.

        Args:
            date_range: Optional tuple of (start_date, end_date). Defaults to last 24 hours.
            format: Output format - "text", "markdown", or "html"
            title: Custom title for the report

        Returns:
            Formatted digest report string
        """
        if date_range is None:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=1)
            date_range = (start_date, end_date)
        else:
            start_date, end_date = date_range

        # Get events in date range
        all_events = self.storage.get_all_events()
        events = [
            e for e in all_events
            if start_date <= e.published_date <= end_date
        ]

        # Get all clients for reference
        clients = {c.id: c for c in self.storage.get_all_clients()}

        # Generate report data
        report_data = self._analyze_events(events, clients)

        # Format based on requested format
        if format == "html":
            return self._format_html(report_data, start_date, end_date, title)
        elif format == "text":
            return self._format_text(report_data, start_date, end_date, title)
        else:  # markdown
            return self._format_markdown(report_data, start_date, end_date, title)

    def generate_weekly_digest(
        self,
        format: Literal["text", "markdown", "html"] = "markdown"
    ) -> str:
        """
        Generate weekly summary report.

        Args:
            format: Output format - "text", "markdown", or "html"

        Returns:
            Formatted weekly digest report string
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)

        return self.generate_daily_digest(
            date_range=(start_date, end_date),
            format=format,
            title="Weekly Intelligence Summary"
        )

    def generate_client_report(
        self,
        client_id: str,
        days_back: int = 30,
        format: Literal["text", "markdown", "html"] = "markdown"
    ) -> str:
        """
        Generate report for a single client.

        Args:
            client_id: Client ID to generate report for
            days_back: Number of days to include in report
            format: Output format - "text", "markdown", or "html"

        Returns:
            Formatted client report string
        """
        client = self.storage.get_client(client_id)
        if not client:
            return f"Client {client_id} not found"

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)

        # Get events for this client
        all_events = self.storage.get_events_by_client(client_id)
        events = [
            e for e in all_events
            if start_date <= e.published_date <= end_date
        ]

        # Analyze events
        report_data = {
            "client": client,
            "total_events": len(events),
            "high_priority": len([e for e in events if e.relevance_score >= 0.7]),
            "by_category": self._group_by_category(events),
            "by_sentiment": self._group_by_sentiment(events),
            "recent_events": sorted(events, key=lambda e: e.published_date, reverse=True)[:10],
            "trending": self._calculate_trend(events)
        }

        # Format based on requested format
        if format == "html":
            return self._format_client_html(report_data, start_date, end_date)
        elif format == "text":
            return self._format_client_text(report_data, start_date, end_date)
        else:  # markdown
            return self._format_client_markdown(report_data, start_date, end_date)

    def _analyze_events(self, events: List, clients: Dict) -> Dict[str, Any]:
        """Analyze events and generate summary statistics."""
        # Group events by client
        by_client = defaultdict(list)
        for event in events:
            by_client[event.client_id].append(event)

        # High priority alerts
        high_priority = [e for e in events if e.relevance_score >= 0.7]

        # Event counts by type
        by_category = self._group_by_category(events)

        # Event counts by sentiment
        by_sentiment = self._group_by_sentiment(events)

        # Trending clients (most activity)
        trending = sorted(
            by_client.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:5]

        return {
            "total_events": len(events),
            "total_clients": len(by_client),
            "high_priority_count": len(high_priority),
            "high_priority_events": high_priority[:10],  # Top 10
            "by_client": by_client,
            "by_category": by_category,
            "by_sentiment": by_sentiment,
            "trending_clients": [
                (clients.get(cid), events) for cid, events in trending
            ],
            "clients": clients
        }

    def _group_by_category(self, events: List) -> Dict[str, int]:
        """Group events by event type."""
        by_category = defaultdict(int)
        for event in events:
            # Use event_type which has values like "funding", "acquisition", "leadership", etc.
            event_type = event.event_type if hasattr(event, 'event_type') else 'other'
            by_category[event_type] += 1
        return dict(by_category)

    def _group_by_sentiment(self, events: List) -> Dict[str, int]:
        """Group events by sentiment."""
        positive = len([e for e in events if e.sentiment == "positive"])
        neutral = len([e for e in events if e.sentiment == "neutral"])
        negative = len([e for e in events if e.sentiment == "negative"])
        return {"positive": positive, "neutral": neutral, "negative": negative}

    def _calculate_trend(self, events: List) -> str:
        """Calculate trend direction for events."""
        if len(events) < 2:
            return "stable"

        # Split into two halves
        mid = len(events) // 2
        sorted_events = sorted(events, key=lambda e: e.published_date)
        first_half = sorted_events[:mid]
        second_half = sorted_events[mid:]

        if len(second_half) > len(first_half) * 1.2:
            return "increasing"
        elif len(second_half) < len(first_half) * 0.8:
            return "decreasing"
        else:
            return "stable"

    def _format_markdown(self, data: Dict, start_date: datetime, end_date: datetime, title: str = "Daily Intelligence Digest") -> str:
        """Format report as Markdown."""
        md = f"""# {title}
**Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}

---

## 📊 Executive Summary

- **Total Events:** {data['total_events']}
- **Active Clients:** {data['total_clients']}
- **High-Priority Alerts:** {data['high_priority_count']}

---

## 🚨 High-Priority Alerts

"""
        if data['high_priority_events']:
            for event in data['high_priority_events']:
                client = data['clients'].get(event.client_id)
                client_name = client.name if client else "Unknown"
                sentiment_emoji = "📈" if event.sentiment_score > 0 else "📉" if event.sentiment_score < 0 else "➡️"
                md += f"""### {sentiment_emoji} {event.title}
- **Client:** {client_name}
- **Relevance:** {event.relevance_score:.0%}
- **Date:** {event.published_date.strftime('%Y-%m-%d %H:%M')}
- **Source:** [{event.source_name}]({event.source_url})

"""
        else:
            md += "*No high-priority alerts in this period.*\n\n"

        md += """---

## 📈 Events by Category

"""
        for category, count in sorted(data['by_category'].items(), key=lambda x: x[1], reverse=True):
            md += f"- **{category}:** {count} events\n"

        md += """
---

## 🔥 Trending Clients (Most Activity)

"""
        for client, events in data['trending_clients']:
            if client:
                md += f"- **{client.name}:** {len(events)} events\n"

        md += """
---

## 📋 Events by Client

"""
        for client_id, events in sorted(data['by_client'].items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            client = data['clients'].get(client_id)
            if client:
                md += f"""### {client.name}
- **Total Events:** {len(events)}
- **Avg Relevance:** {sum(e.relevance_score for e in events) / len(events):.0%}

"""
                for event in events[:3]:  # Top 3 events
                    md += f"  - {event.title}\n"
                md += "\n"

        return md

    def _format_text(self, data: Dict, start_date: datetime, end_date: datetime, title: str = "Daily Intelligence Digest") -> str:
        """Format report as plain text."""
        text = f"""{title.upper()}
Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}

{'=' * 60}

EXECUTIVE SUMMARY

Total Events: {data['total_events']}
Active Clients: {data['total_clients']}
High-Priority Alerts: {data['high_priority_count']}

{'=' * 60}

HIGH-PRIORITY ALERTS

"""
        if data['high_priority_events']:
            for i, event in enumerate(data['high_priority_events'], 1):
                client = data['clients'].get(event.client_id)
                client_name = client.name if client else "Unknown"
                text += f"""{i}. {event.title}
   Client: {client_name}
   Relevance: {event.relevance_score:.0%}
   Date: {event.published_date.strftime('%Y-%m-%d %H:%M')}
   Source: {event.source_url}

"""
        else:
            text += "No high-priority alerts in this period.\n\n"

        text += f"""{'=' * 60}

EVENTS BY CATEGORY

"""
        for category, count in sorted(data['by_category'].items(), key=lambda x: x[1], reverse=True):
            text += f"{category}: {count} events\n"

        text += f"""
{'=' * 60}

TRENDING CLIENTS (Most Activity)

"""
        for client, events in data['trending_clients']:
            if client:
                text += f"{client.name}: {len(events)} events\n"

        return text

    def _format_html(self, data: Dict, start_date: datetime, end_date: datetime, title: str = "Daily Intelligence Digest") -> str:
        """Format report as HTML."""
        # Prepare data for charts
        categories = list(data['by_category'].keys())
        category_counts = list(data['by_category'].values())

        sentiments = list(data['by_sentiment'].keys())
        sentiment_counts = list(data['by_sentiment'].values())

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 40px auto; padding: 0 20px; }}
        h1 {{ color: #1a1a1a; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #333; margin-top: 30px; border-left: 4px solid #4CAF50; padding-left: 10px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .stat {{ display: inline-block; margin-right: 30px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #4CAF50; }}
        .alert {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 10px 0; }}
        .client-section {{ margin: 20px 0; }}
        .event-list {{ list-style: none; padding-left: 0; }}
        .event-item {{ padding: 10px; margin: 5px 0; border-left: 3px solid #2196F3; }}
        .charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin: 30px 0; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        canvas {{ max-height: 300px; }}
    </style>
</head>
<body>
    <h1>📊 {title}</h1>
    <p><strong>Period:</strong> {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}</p>

    <div class="summary">
        <h2>Executive Summary</h2>
        <div class="stat">
            <div class="stat-value">{data['total_events']}</div>
            <div>Total Events</div>
        </div>
        <div class="stat">
            <div class="stat-value">{data['total_clients']}</div>
            <div>Active Clients</div>
        </div>
        <div class="stat">
            <div class="stat-value">{data['high_priority_count']}</div>
            <div>High-Priority Alerts</div>
        </div>
    </div>

    <h2>📊 Visual Analytics</h2>
    <div class="charts-grid">
        <div class="chart-container">
            <h3>Events by Type</h3>
            <canvas id="categoryChart"></canvas>
        </div>
        <div class="chart-container">
            <h3>Sentiment Distribution</h3>
            <canvas id="sentimentChart"></canvas>
        </div>
    </div>

    <h2>🚨 High-Priority Alerts</h2>
"""
        if data['high_priority_events']:
            for event in data['high_priority_events']:
                client = data['clients'].get(event.client_id)
                client_name = client.name if client else "Unknown"
                sentiment_emoji = "📈" if event.sentiment_score and event.sentiment_score > 0 else "📉" if event.sentiment_score and event.sentiment_score < 0 else "➡️"
                html += f"""
    <div class="alert">
        <h3>{sentiment_emoji} {event.title}</h3>
        <p><strong>Client:</strong> {client_name} | <strong>Relevance:</strong> {event.relevance_score:.0%}</p>
        <p><strong>Date:</strong> {event.published_date.strftime('%Y-%m-%d %H:%M')}</p>
        {f'<p><a href="{event.source_url}">View Source</a></p>' if event.source_url else ''}
    </div>
"""
        else:
            html += "<p><em>No high-priority alerts in this period.</em></p>"

        html += """
    <h2>📈 Events by Type</h2>
    <ul>
"""
        for event_type, count in sorted(data['by_category'].items(), key=lambda x: x[1], reverse=True):
            # Capitalize first letter for better display
            display_type = event_type.capitalize()
            html += f"        <li><strong>{display_type}:</strong> {count} events</li>\n"

        html += """
    </ul>

    <h2>🔥 Trending Clients</h2>
    <ul>
"""
        for client, events in data['trending_clients']:
            if client:
                html += f"        <li><strong>{client.name}:</strong> {len(events)} events</li>\n"

        html += f"""
    </ul>

    <script>
        // Events by Category Chart
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        new Chart(categoryCtx, {{
            type: 'bar',
            data: {{
                labels: {categories},
                datasets: [{{
                    label: 'Number of Events',
                    data: {category_counts},
                    backgroundColor: [
                        'rgba(76, 175, 80, 0.8)',
                        'rgba(33, 150, 243, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(156, 39, 176, 0.8)',
                        'rgba(255, 87, 34, 0.8)',
                        'rgba(0, 188, 212, 0.8)'
                    ],
                    borderColor: [
                        'rgba(76, 175, 80, 1)',
                        'rgba(33, 150, 243, 1)',
                        'rgba(255, 193, 7, 1)',
                        'rgba(156, 39, 176, 1)',
                        'rgba(255, 87, 34, 1)',
                        'rgba(0, 188, 212, 1)'
                    ],
                    borderWidth: 2,
                    borderRadius: 5
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: {{
                            size: 14,
                            weight: 'bold'
                        }},
                        bodyFont: {{
                            size: 13
                        }},
                        padding: 12,
                        displayColors: false,
                        callbacks: {{
                            label: function(context) {{
                                return context.parsed.y + ' events';
                            }}
                        }}
                    }},
                    datalabels: {{
                        anchor: 'end',
                        align: 'top',
                        color: '#333',
                        font: {{
                            weight: 'bold',
                            size: 12
                        }},
                        formatter: function(value) {{
                            return value;
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            stepSize: 1,
                            font: {{
                                size: 11
                            }}
                        }},
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.05)'
                        }}
                    }},
                    x: {{
                        ticks: {{
                            font: {{
                                size: 11,
                                weight: '500'
                            }}
                        }},
                        grid: {{
                            display: false
                        }}
                    }}
                }}
            }},
            plugins: [{{
                afterDatasetsDraw: function(chart) {{
                    const ctx = chart.ctx;
                    chart.data.datasets.forEach(function(dataset, i) {{
                        const meta = chart.getDatasetMeta(i);
                        meta.data.forEach(function(bar, index) {{
                            const data = dataset.data[index];
                            ctx.fillStyle = '#333';
                            ctx.font = 'bold 12px Arial';
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'bottom';
                            ctx.fillText(data, bar.x, bar.y - 5);
                        }});
                    }});
                }}
            }}]
        }});

        // Sentiment Chart
        const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
        new Chart(sentimentCtx, {{
            type: 'doughnut',
            data: {{
                labels: {sentiments},
                datasets: [{{
                    data: {sentiment_counts},
                    backgroundColor: [
                        'rgba(76, 175, 80, 0.85)',   // positive - green
                        'rgba(158, 158, 158, 0.85)', // neutral - gray
                        'rgba(244, 67, 54, 0.85)'    // negative - red
                    ],
                    borderColor: [
                        'rgba(76, 175, 80, 1)',
                        'rgba(158, 158, 158, 1)',
                        'rgba(244, 67, 54, 1)'
                    ],
                    borderWidth: 2,
                    hoverOffset: 10
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            padding: 15,
                            font: {{
                                size: 12,
                                weight: '500'
                            }},
                            generateLabels: function(chart) {{
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {{
                                    return data.labels.map((label, i) => {{
                                        const value = data.datasets[0].data[i];
                                        const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        return {{
                                            text: `${{label.charAt(0).toUpperCase() + label.slice(1)}}: ${{value}} (${{percentage}}%)`,
                                            fillStyle: data.datasets[0].backgroundColor[i],
                                            hidden: false,
                                            index: i
                                        }};
                                    }});
                                }}
                                return [];
                            }}
                        }}
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: {{
                            size: 14,
                            weight: 'bold'
                        }},
                        bodyFont: {{
                            size: 13
                        }},
                        padding: 12,
                        callbacks: {{
                            label: function(context) {{
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return label + ': ' + value + ' events (' + percentage + '%)';
                            }}
                        }}
                    }}
                }},
                layout: {{
                    padding: 10
                }}
            }},
            plugins: [{{
                afterDraw: function(chart) {{
                    const ctx = chart.ctx;
                    const centerX = (chart.chartArea.left + chart.chartArea.right) / 2;
                    const centerY = (chart.chartArea.top + chart.chartArea.bottom) / 2;

                    const total = chart.data.datasets[0].data.reduce((a, b) => a + b, 0);

                    ctx.save();
                    ctx.font = 'bold 16px Arial';
                    ctx.fillStyle = '#333';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(total, centerX, centerY - 8);

                    ctx.font = '11px Arial';
                    ctx.fillStyle = '#666';
                    ctx.fillText('Total Events', centerX, centerY + 10);
                    ctx.restore();
                }}
            }}]
        }});
    </script>
</body>
</html>
"""
        return html

    def _format_client_markdown(self, data: Dict, start_date: datetime, end_date: datetime) -> str:
        """Format client report as Markdown."""
        client = data['client']
        trend_emoji = "📈" if data['trending'] == "increasing" else "📉" if data['trending'] == "decreasing" else "➡️"

        md = f"""# Client Report: {client.name}
**Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}

---

## 📊 Summary

- **Total Events:** {data['total_events']}
- **High-Priority Events:** {data['high_priority']}
- **Trend:** {trend_emoji} {data['trending'].capitalize()}

---

## 📈 Events by Category

"""
        for category, count in sorted(data['by_category'].items(), key=lambda x: x[1], reverse=True):
            md += f"- **{category}:** {count}\n"

        md += """
---

## 😊 Sentiment Analysis

"""
        for sentiment, count in data['by_sentiment'].items():
            emoji = "😊" if sentiment == "positive" else "😐" if sentiment == "neutral" else "😟"
            md += f"- {emoji} **{sentiment.capitalize()}:** {count}\n"

        md += """
---

## 📰 Recent Events

"""
        for event in data['recent_events']:
            sentiment_emoji = "📈" if event.sentiment_score > 0 else "📉" if event.sentiment_score < 0 else "➡️"
            md += f"""### {sentiment_emoji} {event.title}
- **Relevance:** {event.relevance_score:.0%}
- **Date:** {event.published_date.strftime('%Y-%m-%d')}
- **Source:** [{event.source_name}]({event.source_url})

"""

        return md

    def _format_client_text(self, data: Dict, start_date: datetime, end_date: datetime) -> str:
        """Format client report as plain text."""
        client = data['client']

        text = f"""CLIENT REPORT: {client.name}
Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}

{'=' * 60}

SUMMARY

Total Events: {data['total_events']}
High-Priority Events: {data['high_priority']}
Trend: {data['trending'].capitalize()}

{'=' * 60}

EVENTS BY CATEGORY

"""
        for category, count in sorted(data['by_category'].items(), key=lambda x: x[1], reverse=True):
            text += f"{category}: {count}\n"

        text += f"""
{'=' * 60}

SENTIMENT ANALYSIS

"""
        for sentiment, count in data['by_sentiment'].items():
            text += f"{sentiment.capitalize()}: {count}\n"

        text += f"""
{'=' * 60}

RECENT EVENTS

"""
        for i, event in enumerate(data['recent_events'], 1):
            text += f"""{i}. {event.title}
   Relevance: {event.relevance_score:.0%}
   Date: {event.published_date.strftime('%Y-%m-%d')}
   Source: {event.source_url}

"""

        return text

    def _format_client_html(self, data: Dict, start_date: datetime, end_date: datetime) -> str:
        """Format client report as HTML."""
        client = data['client']
        trend_emoji = "📈" if data['trending'] == "increasing" else "📉" if data['trending'] == "decreasing" else "➡️"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Client Report: {client.name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }}
        h1 {{ color: #1a1a1a; border-bottom: 3px solid #2196F3; padding-bottom: 10px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .stat {{ margin: 10px 0; }}
        .event {{ border-left: 3px solid #2196F3; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>Client Report: {client.name}</h1>
    <p><strong>Period:</strong> {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}</p>

    <div class="summary">
        <h2>Summary</h2>
        <div class="stat"><strong>Total Events:</strong> {data['total_events']}</div>
        <div class="stat"><strong>High-Priority Events:</strong> {data['high_priority']}</div>
        <div class="stat"><strong>Trend:</strong> {trend_emoji} {data['trending'].capitalize()}</div>
    </div>

    <h2>Events by Category</h2>
    <ul>
"""
        for category, count in sorted(data['by_category'].items(), key=lambda x: x[1], reverse=True):
            html += f"        <li><strong>{category}:</strong> {count}</li>\n"

        html += """
    </ul>

    <h2>Recent Events</h2>
"""
        for event in data['recent_events']:
            sentiment_emoji = "📈" if event.sentiment_score > 0 else "📉" if event.sentiment_score < 0 else "➡️"
            html += f"""
    <div class="event">
        <h3>{sentiment_emoji} {event.title}</h3>
        <p><strong>Relevance:</strong> {event.relevance_score:.0%} | <strong>Date:</strong> {event.published_date.strftime('%Y-%m-%d')}</p>
        <p><a href="{event.source_url}">View Source</a></p>
    </div>
"""

        html += """
</body>
</html>
"""
        return html
