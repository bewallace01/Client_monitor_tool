"""Event raw data service for managing unprocessed API responses."""

import json
import logging
from typing import Optional, List, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.event_raw_data import EventRawData
from app.schemas.event_raw_data import EventRawDataCreate

logger = logging.getLogger(__name__)


class EventRawDataService:
    """Service for managing raw event data from APIs."""

    @staticmethod
    def save_raw_data(
        db: Session,
        business_id: UUID,
        client_id: UUID,
        job_run_id: Optional[UUID],
        source_api: str,
        raw_content: dict,
        search_query: str
    ) -> EventRawData:
        """
        Save raw API response to database.

        Args:
            db: Database session
            business_id: Business UUID
            client_id: Client UUID
            job_run_id: JobRun UUID
            source_api: API source name
            raw_content: Raw API response dict
            search_query: Search query used

        Returns:
            Created EventRawData instance
        """
        # Serialize raw content to JSON
        raw_content_json = json.dumps(raw_content)

        # Calculate content hash
        from app.services.search_aggregator_service import SearchAggregatorService
        content_hash = SearchAggregatorService.calculate_content_hash(
            json.dumps(raw_content.get("title", "") + raw_content.get("snippet", ""))
        )

        raw_data = EventRawData(
            business_id=business_id,
            client_id=client_id,
            job_run_id=job_run_id,
            source_api=source_api,
            raw_content=raw_content_json,
            search_query=search_query,
            content_hash=content_hash,
            is_processed=False
        )

        db.add(raw_data)
        db.commit()
        db.refresh(raw_data)

        logger.debug(f"Saved raw data from {source_api} for client {client_id}")
        return raw_data

    @staticmethod
    def bulk_save_raw_data(
        db: Session,
        business_id: UUID,
        client_id: UUID,
        job_run_id: Optional[UUID],
        source_api: str,
        results: List[dict],
        search_query: str
    ) -> List[EventRawData]:
        """
        Save multiple raw API responses in bulk.

        Args:
            db: Database session
            business_id: Business UUID
            client_id: Client UUID
            job_run_id: JobRun UUID
            source_api: API source name
            results: List of result dicts
            search_query: Search query used

        Returns:
            List of created EventRawData instances
        """
        raw_data_list = []

        for result in results:
            try:
                raw_data = EventRawDataService.save_raw_data(
                    db=db,
                    business_id=business_id,
                    client_id=client_id,
                    job_run_id=job_run_id,
                    source_api=source_api,
                    raw_content=result,
                    search_query=search_query
                )
                raw_data_list.append(raw_data)
            except Exception as e:
                logger.error(f"Failed to save raw data: {str(e)}")
                continue

        logger.info(f"Saved {len(raw_data_list)} raw data entries from {source_api}")
        return raw_data_list

    @staticmethod
    def get_unprocessed_data(
        db: Session,
        business_id: UUID,
        limit: int = 100
    ) -> List[EventRawData]:
        """
        Get unprocessed raw data for a business.

        Args:
            db: Database session
            business_id: Business UUID
            limit: Maximum number of records

        Returns:
            List of EventRawData instances
        """
        return db.query(EventRawData).filter(
            EventRawData.business_id == business_id,
            EventRawData.is_processed == False
        ).order_by(
            EventRawData.created_at.asc()
        ).limit(limit).all()

    @staticmethod
    def get_raw_data_by_job(
        db: Session,
        job_run_id: UUID
    ) -> List[EventRawData]:
        """Get all raw data for a specific job run."""
        return db.query(EventRawData).filter(
            EventRawData.job_run_id == job_run_id
        ).all()

    @staticmethod
    def mark_as_processed(
        db: Session,
        raw_data_id: UUID,
        event_id: UUID
    ):
        """
        Mark raw data as processed and link to created event.

        Args:
            db: Database session
            raw_data_id: EventRawData UUID
            event_id: Created Event UUID
        """
        raw_data = db.query(EventRawData).filter(
            EventRawData.id == raw_data_id
        ).first()

        if raw_data:
            raw_data.mark_as_processed(event_id)
            db.commit()
            logger.debug(f"Marked raw data {raw_data_id} as processed")

    @staticmethod
    def mark_as_failed(
        db: Session,
        raw_data_id: UUID,
        error_message: str
    ):
        """
        Mark raw data processing as failed.

        Args:
            db: Database session
            raw_data_id: EventRawData UUID
            error_message: Error message
        """
        raw_data = db.query(EventRawData).filter(
            EventRawData.id == raw_data_id
        ).first()

        if raw_data:
            raw_data.mark_as_failed(error_message)
            db.commit()
            logger.debug(f"Marked raw data {raw_data_id} as failed")

    @staticmethod
    def get_statistics(
        db: Session,
        business_id: UUID
    ) -> dict:
        """
        Get statistics about raw data for a business.

        Args:
            db: Database session
            business_id: Business UUID

        Returns:
            Dict with statistics
        """
        total = db.query(EventRawData).filter(
            EventRawData.business_id == business_id
        ).count()

        processed = db.query(EventRawData).filter(
            EventRawData.business_id == business_id,
            EventRawData.is_processed == True,
            EventRawData.processed_into_event_id.isnot(None)
        ).count()

        failed = db.query(EventRawData).filter(
            EventRawData.business_id == business_id,
            EventRawData.is_processed == True,
            EventRawData.processing_error.isnot(None)
        ).count()

        unprocessed = total - processed - failed

        # Count by source
        from sqlalchemy import func
        by_source = db.query(
            EventRawData.source_api,
            func.count(EventRawData.id)
        ).filter(
            EventRawData.business_id == business_id
        ).group_by(EventRawData.source_api).all()

        return {
            "total_raw_data": total,
            "processed_count": processed,
            "failed_count": failed,
            "unprocessed_count": unprocessed,
            "by_source_api": {source: count for source, count in by_source}
        }

    @staticmethod
    def parse_raw_content(raw_data: EventRawData) -> Optional[dict]:
        """Parse raw content JSON string to dict."""
        try:
            return json.loads(raw_data.raw_content)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Failed to parse raw_content for {raw_data.id}: {str(e)}")
            return None

    @staticmethod
    def cleanup_old_processed(
        db: Session,
        business_id: UUID,
        days_old: int = 90
    ) -> int:
        """
        Delete processed raw data older than specified days.

        Args:
            db: Database session
            business_id: Business UUID
            days_old: Delete data older than this many days

        Returns:
            Number of records deleted
        """
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        deleted = db.query(EventRawData).filter(
            EventRawData.business_id == business_id,
            EventRawData.is_processed == True,
            EventRawData.created_at < cutoff_date
        ).delete()

        db.commit()
        logger.info(f"Deleted {deleted} old processed raw data entries")
        return deleted
