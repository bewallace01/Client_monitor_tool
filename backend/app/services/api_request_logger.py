"""API Request Logging Service for tracking API usage."""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.api_request_log import APIRequestLog

logger = logging.getLogger(__name__)


class APIRequestLogger:
    """Log and track API requests for monitoring and rate limiting."""

    @staticmethod
    def log_request(
        db: Session,
        business_id: UUID,
        api_config_id: UUID,
        provider: str,
        success: bool,
        status_code: Optional[int] = None,
        response_time_ms: Optional[float] = None,
        results_count: Optional[int] = None,
        error_message: Optional[str] = None,
        error_type: Optional[str] = None,
        client_id: Optional[UUID] = None,
        client_name: Optional[str] = None,
        job_run_id: Optional[UUID] = None,
        endpoint: Optional[str] = None,
        method: str = "GET",
        rate_limit_remaining: Optional[int] = None,
        rate_limit_reset: Optional[datetime] = None
    ) -> APIRequestLog:
        """
        Log an API request.

        Args:
            db: Database session
            business_id: Business UUID
            api_config_id: API config UUID
            provider: API provider name
            success: Whether request succeeded
            status_code: HTTP status code
            response_time_ms: Response time in milliseconds
            results_count: Number of results returned
            error_message: Error message if failed
            error_type: Type of error (rate_limit, timeout, etc.)
            client_id: Client UUID if request was for specific client
            client_name: Client name
            job_run_id: Job run UUID if part of automation
            endpoint: API endpoint called
            method: HTTP method
            rate_limit_remaining: Remaining requests in rate limit window
            rate_limit_reset: When rate limit resets

        Returns:
            Created APIRequestLog
        """
        log_entry = APIRequestLog(
            business_id=business_id,
            api_config_id=api_config_id,
            provider=provider,
            endpoint=endpoint,
            method=method,
            client_id=client_id,
            client_name=client_name,
            job_run_id=job_run_id,
            status_code=status_code,
            success=success,
            response_time_ms=response_time_ms,
            results_count=results_count or 0,
            error_message=error_message[:1000] if error_message else None,  # Truncate long errors
            error_type=error_type,
            rate_limit_remaining=rate_limit_remaining,
            rate_limit_reset=rate_limit_reset
        )

        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

        return log_entry

    @staticmethod
    def get_recent_logs(
        db: Session,
        business_id: UUID,
        api_config_id: Optional[UUID] = None,
        provider: Optional[str] = None,
        success: Optional[bool] = None,
        hours_back: int = 24,
        limit: int = 100
    ) -> List[APIRequestLog]:
        """
        Get recent API request logs.

        Args:
            db: Database session
            business_id: Business UUID
            api_config_id: Filter by API config
            provider: Filter by provider
            success: Filter by success status
            hours_back: How many hours back to query
            limit: Maximum number of logs to return

        Returns:
            List of APIRequestLog entries
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)

        query = db.query(APIRequestLog).filter(
            APIRequestLog.business_id == business_id,
            APIRequestLog.created_at >= cutoff_time
        )

        if api_config_id:
            query = query.filter(APIRequestLog.api_config_id == api_config_id)

        if provider:
            query = query.filter(APIRequestLog.provider == provider)

        if success is not None:
            query = query.filter(APIRequestLog.success == success)

        return query.order_by(APIRequestLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_usage_stats(
        db: Session,
        business_id: UUID,
        api_config_id: Optional[UUID] = None,
        hours_back: int = 24
    ) -> Dict[str, Any]:
        """
        Get API usage statistics.

        Args:
            db: Database session
            business_id: Business UUID
            api_config_id: Filter by API config
            hours_back: How many hours back to calculate stats

        Returns:
            Dict with usage statistics
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)

        query = db.query(APIRequestLog).filter(
            APIRequestLog.business_id == business_id,
            APIRequestLog.created_at >= cutoff_time
        )

        if api_config_id:
            query = query.filter(APIRequestLog.api_config_id == api_config_id)

        all_logs = query.all()

        if not all_logs:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "success_rate": 0.0,
                "avg_response_time_ms": 0.0,
                "total_results": 0,
                "errors_by_type": {},
                "requests_per_hour": 0.0
            }

        successful = [log for log in all_logs if log.success]
        failed = [log for log in all_logs if not log.success]

        # Calculate average response time (only for successful requests with timing data)
        response_times = [log.response_time_ms for log in successful if log.response_time_ms is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0

        # Count errors by type
        errors_by_type = {}
        for log in failed:
            if log.error_type:
                errors_by_type[log.error_type] = errors_by_type.get(log.error_type, 0) + 1

        # Calculate total results
        total_results = sum(log.results_count or 0 for log in successful)

        return {
            "total_requests": len(all_logs),
            "successful_requests": len(successful),
            "failed_requests": len(failed),
            "success_rate": len(successful) / len(all_logs) * 100 if all_logs else 0.0,
            "avg_response_time_ms": round(avg_response_time, 2),
            "total_results": total_results,
            "errors_by_type": errors_by_type,
            "requests_per_hour": len(all_logs) / hours_back if hours_back > 0 else 0.0
        }

    @staticmethod
    def get_usage_by_provider(
        db: Session,
        business_id: UUID,
        hours_back: int = 24
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get API usage statistics grouped by provider.

        Args:
            db: Database session
            business_id: Business UUID
            hours_back: How many hours back to calculate stats

        Returns:
            Dict mapping provider names to their usage stats
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)

        # Get all unique providers
        providers = db.query(APIRequestLog.provider).filter(
            APIRequestLog.business_id == business_id,
            APIRequestLog.created_at >= cutoff_time
        ).distinct().all()

        provider_stats = {}
        for (provider,) in providers:
            stats = APIRequestLogger.get_usage_stats(
                db=db,
                business_id=business_id,
                hours_back=hours_back
            )
            # Filter stats for this provider
            provider_logs = db.query(APIRequestLog).filter(
                APIRequestLog.business_id == business_id,
                APIRequestLog.provider == provider,
                APIRequestLog.created_at >= cutoff_time
            ).all()

            successful = [log for log in provider_logs if log.success]
            failed = [log for log in provider_logs if not log.success]

            response_times = [log.response_time_ms for log in successful if log.response_time_ms is not None]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0

            errors_by_type = {}
            for log in failed:
                if log.error_type:
                    errors_by_type[log.error_type] = errors_by_type.get(log.error_type, 0) + 1

            total_results = sum(log.results_count or 0 for log in successful)

            provider_stats[provider] = {
                "total_requests": len(provider_logs),
                "successful_requests": len(successful),
                "failed_requests": len(failed),
                "success_rate": len(successful) / len(provider_logs) * 100 if provider_logs else 0.0,
                "avg_response_time_ms": round(avg_response_time, 2),
                "total_results": total_results,
                "errors_by_type": errors_by_type,
                "requests_per_hour": len(provider_logs) / hours_back if hours_back > 0 else 0.0
            }

        return provider_stats

    @staticmethod
    def check_rate_limit(
        db: Session,
        api_config_id: UUID,
        max_requests_per_hour: int
    ) -> tuple[bool, int]:
        """
        Check if rate limit would be exceeded.

        Args:
            db: Database session
            api_config_id: API config UUID
            max_requests_per_hour: Maximum allowed requests per hour

        Returns:
            Tuple of (within_limit, current_count)
        """
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        current_count = db.query(func.count(APIRequestLog.id)).filter(
            APIRequestLog.api_config_id == api_config_id,
            APIRequestLog.created_at >= one_hour_ago
        ).scalar()

        return current_count < max_requests_per_hour, current_count

    @staticmethod
    def get_failure_summary(
        db: Session,
        business_id: UUID,
        hours_back: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get summary of recent failures.

        Args:
            db: Database session
            business_id: Business UUID
            hours_back: How many hours back to query

        Returns:
            List of failure summaries
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)

        failures = db.query(APIRequestLog).filter(
            APIRequestLog.business_id == business_id,
            APIRequestLog.success == False,
            APIRequestLog.created_at >= cutoff_time
        ).order_by(APIRequestLog.created_at.desc()).limit(50).all()

        return [
            {
                "provider": f.provider,
                "error_type": f.error_type,
                "error_message": f.error_message,
                "client_name": f.client_name,
                "status_code": f.status_code,
                "created_at": f.created_at.isoformat()
            }
            for f in failures
        ]
