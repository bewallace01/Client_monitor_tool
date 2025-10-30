"""Analytics service layer for dashboard metrics and reporting."""

from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy import func, and_, case, or_
from sqlalchemy.orm import Session

from app.models import Client, Event, EventUserInteraction
from app.schemas.analytics import (
    ClientActivityMetrics,
    SentimentDistribution,
    CategoryDistribution,
    TimeSeriesDataPoint,
    TrendData,
    RelevanceMetrics,
)


class AnalyticsService:
    """Service for analytics and dashboard metrics."""

    @staticmethod
    def get_dashboard_summary(db: Session, business_id: Optional[UUID] = None, user_id: Optional[int] = None) -> dict:
        """
        Get complete dashboard summary with all key metrics for a specific business.

        Args:
            db: Database session
            business_id: UUID of the business (None for system admins to see all)
            user_id: Optional user ID for per-user event stats

        Returns comprehensive metrics for the dashboard overview.
        """
        # Client metrics (filtered by business and excluding deleted)
        client_query = db.query(Client).filter(Client.is_deleted == False)
        if business_id is not None:
            client_query = client_query.filter(Client.business_id == business_id)
        total_clients = client_query.count()
        active_clients = client_query.filter(Client.is_active == True).count()

        # Clients by tier
        tier_stats = (
            client_query
            .filter(Client.tier.isnot(None))
            .with_entities(Client.tier, func.count(Client.id))
            .group_by(Client.tier)
            .all()
        )
        clients_by_tier = {tier: count for tier, count in tier_stats}

        # Clients by industry
        industry_stats = (
            client_query
            .filter(Client.industry.isnot(None))
            .with_entities(Client.industry, func.count(Client.id))
            .group_by(Client.industry)
            .all()
        )
        clients_by_industry = {industry: count for industry, count in industry_stats}

        # Event metrics (filtered by business and excluding deleted)
        event_query = db.query(Event).filter(Event.is_deleted == False)
        if business_id is not None:
            event_query = event_query.filter(Event.business_id == business_id)
        total_events = event_query.count()

        # Per-user read/starred stats (if user_id provided)
        if user_id:
            # Count events NOT marked as read by this user
            unread_events = event_query.outerjoin(
                EventUserInteraction,
                and_(
                    EventUserInteraction.event_id == Event.id,
                    EventUserInteraction.user_id == user_id
                )
            ).filter(
                or_(
                    EventUserInteraction.is_read == False,
                    EventUserInteraction.id.is_(None)
                )
            ).count()

            # Count events starred by this user
            starred_query = db.query(EventUserInteraction).join(Event).filter(
                Event.is_deleted == False,
                EventUserInteraction.user_id == user_id,
                EventUserInteraction.is_starred == True
            )
            if business_id is not None:
                starred_query = starred_query.filter(Event.business_id == business_id)
            starred_events = starred_query.count()
        else:
            # Without user_id, all events are "unread", none starred
            unread_events = total_events
            starred_events = 0

        # Recent events
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_events = event_query.filter(Event.event_date >= seven_days_ago).count()

        # Events by category
        category_stats = (
            event_query
            .with_entities(Event.category, func.count(Event.id))
            .group_by(Event.category)
            .all()
        )
        events_by_category = {category: count for category, count in category_stats}

        # Sentiment distribution
        sentiment_dist = AnalyticsService._calculate_sentiment_distribution(db, business_id)

        # Time-based metrics
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        events_today = event_query.filter(Event.event_date >= today_start).count()

        week_start = datetime.utcnow() - timedelta(days=7)
        events_this_week = event_query.filter(Event.event_date >= week_start).count()

        month_start = datetime.utcnow() - timedelta(days=30)
        events_this_month = event_query.filter(Event.event_date >= month_start).count()

        # Relevance metrics
        avg_relevance = event_query.with_entities(func.avg(Event.relevance_score)).scalar() or 0.0
        high_relevance_events = event_query.filter(Event.relevance_score >= 0.7).count()

        return {
            "total_clients": total_clients,
            "active_clients": active_clients,
            "clients_by_tier": clients_by_tier,
            "clients_by_industry": clients_by_industry,
            "total_events": total_events,
            "unread_events": unread_events,
            "starred_events": starred_events,
            "recent_events": recent_events,
            "events_by_category": events_by_category,
            "sentiment_distribution": sentiment_dist,
            "events_today": events_today,
            "events_this_week": events_this_week,
            "events_this_month": events_this_month,
            "avg_relevance_score": round(avg_relevance, 3),
            "high_relevance_events": high_relevance_events,
        }

    @staticmethod
    def get_top_clients_by_activity(
        db: Session, business_id: Optional[UUID] = None, user_id: Optional[int] = None, limit: int = 10, days: int = 30
    ) -> Tuple[List[dict], int]:
        """
        Get top clients by event activity.

        If business_id is None, returns top clients across all businesses (system admins).
        Returns clients sorted by number of events in the specified period.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        # Subquery for recent events count
        recent_events_query = db.query(
            Event.client_id,
            func.count(Event.id).label('recent_count')
        ).filter(
            Event.is_deleted == False,
            Event.event_date >= seven_days_ago
        )
        if business_id is not None:
            recent_events_query = recent_events_query.filter(Event.business_id == business_id)

        recent_events_subq = recent_events_query.group_by(Event.client_id).subquery()

        # Main query
        query = db.query(
            Client.id,
            Client.name,
            func.count(Event.id).label('total_events'),
            func.coalesce(recent_events_subq.c.recent_count, 0).label('recent_events'),
            func.max(Event.event_date).label('last_event_date'),
            func.avg(Event.relevance_score).label('avg_relevance'),
        ).join(Event, Client.id == Event.client_id).filter(
            Client.is_deleted == False,
            Event.is_deleted == False
        )

        if business_id is not None:
            query = query.filter(Client.business_id == business_id)

        query = query.outerjoin(
            recent_events_subq, Client.id == recent_events_subq.c.client_id
        ).group_by(
            Client.id, Client.name, recent_events_subq.c.recent_count
        ).order_by(func.count(Event.id).desc()).limit(limit)

        results = query.all()

        clients = []
        for row in results:
            # If user_id provided, calculate unread count for this client
            if user_id:
                unread_query = db.query(Event).outerjoin(
                    EventUserInteraction,
                    and_(
                        EventUserInteraction.event_id == Event.id,
                        EventUserInteraction.user_id == user_id
                    )
                ).filter(
                    Event.client_id == row[0],
                    Event.is_deleted == False,
                    or_(
                        EventUserInteraction.is_read == False,
                        EventUserInteraction.id.is_(None)
                    )
                )
                if business_id is not None:
                    unread_query = unread_query.filter(Event.business_id == business_id)
                unread_count = unread_query.count()
            else:
                unread_count = row[2]  # All events are unread without user_id

            clients.append({
                "client_id": row[0],
                "client_name": row[1],
                "total_events": row[2],
                "unread_events": unread_count,
                "recent_events": row[3],
                "last_event_date": row[4],
                "avg_relevance_score": round(row[5] if row[5] else 0.0, 3),
            })

        return clients, days

    @staticmethod
    def get_event_timeline(
        db: Session, business_id: Optional[UUID] = None, days: int = 30, group_by: str = "day"
    ) -> Tuple[List[dict], int, str, str]:
        """
        Get event timeline data.

        If business_id is None, returns timeline for all events (system admins).
        Returns time series data of events grouped by day or week.
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Query events in date range with business filtering
        query = db.query(
            func.date(Event.event_date).label('date'),
            func.count(Event.id).label('count')
        ).filter(
            Event.is_deleted == False,
            Event.event_date >= start_date,
            Event.event_date <= end_date
        )

        if business_id is not None:
            query = query.filter(Event.business_id == business_id)

        events = query.group_by(func.date(Event.event_date)).order_by(func.date(Event.event_date)).all()

        # Build complete timeline with zeros for missing days
        timeline = []
        current_date = start_date.date()
        events_dict = {row[0]: row[1] for row in events}

        while current_date <= end_date.date():
            timeline.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "value": events_dict.get(current_date, 0)
            })
            current_date += timedelta(days=1)

        total_events = sum(item["value"] for item in timeline)

        return (
            timeline,
            total_events,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )

    @staticmethod
    def get_category_analytics(db: Session, business_id: Optional[UUID] = None) -> Tuple[List[dict], int, int]:
        """
        Get category distribution analytics.

        If business_id is None, returns analytics for all events (system admins).
        Returns category breakdown with counts and percentages.
        """
        query = db.query(Event.category, func.count(Event.id)).filter(Event.is_deleted == False)

        if business_id is not None:
            query = query.filter(Event.business_id == business_id)

        category_stats = query.group_by(Event.category).order_by(func.count(Event.id).desc()).all()

        total_events = sum(count for _, count in category_stats)

        distribution = []
        for category, count in category_stats:
            percentage = (count / total_events * 100) if total_events > 0 else 0
            distribution.append({
                "category": category,
                "count": count,
                "percentage": round(percentage, 2)
            })

        unique_categories = len(category_stats)

        return distribution, total_events, unique_categories

    @staticmethod
    def get_sentiment_analytics(db: Session, business_id: Optional[UUID] = None) -> Tuple[dict, int, float]:
        """
        Get sentiment analysis metrics.

        If business_id is None, returns analytics for all events (system admins).
        Returns sentiment distribution and average score.
        """
        sentiment_dist = AnalyticsService._calculate_sentiment_distribution(db, business_id)

        event_query = db.query(Event).filter(Event.is_deleted == False)
        if business_id is not None:
            event_query = event_query.filter(Event.business_id == business_id)
        total_events = event_query.count()

        # Calculate average sentiment (excluding nulls)
        avg_sentiment = (
            event_query
            .with_entities(func.avg(Event.sentiment_score))
            .filter(Event.sentiment_score.isnot(None))
            .scalar()
        ) or 0.0

        return sentiment_dist, total_events, round(avg_sentiment, 3)

    @staticmethod
    def get_relevance_metrics(db: Session, business_id: Optional[UUID] = None) -> dict:
        """
        Get relevance score metrics.

        If business_id is None, returns metrics for all events (system admins).
        Returns relevance distribution and statistics.
        """
        event_query = db.query(Event).filter(Event.is_deleted == False)
        if business_id is not None:
            event_query = event_query.filter(Event.business_id == business_id)

        total_events = event_query.count()
        avg_score = event_query.with_entities(func.avg(Event.relevance_score)).scalar() or 0.0

        high_count = event_query.filter(Event.relevance_score >= 0.7).count()
        medium_count = event_query.filter(
            and_(Event.relevance_score >= 0.4, Event.relevance_score < 0.7)
        ).count()
        low_count = event_query.filter(Event.relevance_score < 0.4).count()

        high_percentage = (high_count / total_events * 100) if total_events > 0 else 0

        return {
            "avg_score": round(avg_score, 3),
            "high_relevance_count": high_count,
            "medium_relevance_count": medium_count,
            "low_relevance_count": low_count,
            "high_relevance_percentage": round(high_percentage, 2),
        }

    @staticmethod
    def get_growth_metrics(db: Session, business_id: Optional[UUID] = None, period_days: int = 7) -> dict:
        """
        Get growth metrics comparing current period to previous period.

        If business_id is None, returns metrics for all data (system admins).
        Returns trend data for events and clients.
        """
        now = datetime.utcnow()
        current_start = now - timedelta(days=period_days)
        previous_start = current_start - timedelta(days=period_days)

        # Current period events
        current_events_query = db.query(Event).filter(
            Event.is_deleted == False,
            Event.event_date >= current_start,
            Event.event_date <= now
        )
        if business_id is not None:
            current_events_query = current_events_query.filter(Event.business_id == business_id)
        current_events = current_events_query.count()

        # Previous period events
        previous_events_query = db.query(Event).filter(
            Event.is_deleted == False,
            Event.event_date >= previous_start,
            Event.event_date < current_start
        )
        if business_id is not None:
            previous_events_query = previous_events_query.filter(Event.business_id == business_id)
        previous_events = previous_events_query.count()

        # Calculate event trend
        events_change = current_events - previous_events
        events_change_pct = (
            (events_change / previous_events * 100) if previous_events > 0 else 0
        )

        if events_change > 0:
            events_trend = "up"
        elif events_change < 0:
            events_trend = "down"
        else:
            events_trend = "stable"

        # Current period new clients
        current_clients_query = db.query(Client).filter(
            Client.is_deleted == False,
            Client.created_at >= current_start,
            Client.created_at <= now
        )
        if business_id is not None:
            current_clients_query = current_clients_query.filter(Client.business_id == business_id)
        current_clients = current_clients_query.count()

        # Previous period new clients
        previous_clients_query = db.query(Client).filter(
            Client.is_deleted == False,
            Client.created_at >= previous_start,
            Client.created_at < current_start
        )
        if business_id is not None:
            previous_clients_query = previous_clients_query.filter(Client.business_id == business_id)
        previous_clients = previous_clients_query.count()

        # Calculate client trend
        clients_change = current_clients - previous_clients
        clients_change_pct = (
            (clients_change / previous_clients * 100) if previous_clients > 0 else 0
        )

        if clients_change > 0:
            clients_trend = "up"
        elif clients_change < 0:
            clients_trend = "down"
        else:
            clients_trend = "stable"

        return {
            "events_trend": {
                "current_value": current_events,
                "previous_value": previous_events,
                "change": events_change,
                "change_percentage": round(events_change_pct, 2),
                "trend": events_trend,
            },
            "clients_trend": {
                "current_value": current_clients,
                "previous_value": previous_clients,
                "change": clients_change,
                "change_percentage": round(clients_change_pct, 2),
                "trend": clients_trend,
            },
            "period": f"last_{period_days}_days",
        }

    @staticmethod
    def _calculate_sentiment_distribution(db: Session, business_id: Optional[UUID] = None) -> dict:
        """
        Calculate sentiment distribution with percentages.

        If business_id is None, calculates for all events (system admins).
        Internal helper method.
        """
        event_query = db.query(Event).filter(Event.is_deleted == False)
        if business_id is not None:
            event_query = event_query.filter(Event.business_id == business_id)
        total_events = event_query.count()

        positive = event_query.filter(Event.sentiment_score > 0.3).count()
        neutral = event_query.filter(
            and_(Event.sentiment_score >= -0.3, Event.sentiment_score <= 0.3)
        ).count()
        negative = event_query.filter(Event.sentiment_score < -0.3).count()

        # Calculate percentages
        positive_pct = (positive / total_events * 100) if total_events > 0 else 0
        neutral_pct = (neutral / total_events * 100) if total_events > 0 else 0
        negative_pct = (negative / total_events * 100) if total_events > 0 else 0

        return {
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
            "positive_percentage": round(positive_pct, 2),
            "neutral_percentage": round(neutral_pct, 2),
            "negative_percentage": round(negative_pct, 2),
        }
