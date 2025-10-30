"""Monitoring job execution API endpoints."""

import logging
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.dependencies import get_current_active_user as get_current_user
from app.models.user import User
from app.services.automation_engine_service import AutomationEngineService
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring-jobs", tags=["Monitoring Jobs"])


class ExecuteMonitoringJobRequest(BaseModel):
    """Request to execute a monitoring job."""
    client_ids: Optional[List[UUID]] = Field(
        None,
        description="Specific client IDs to monitor (null = all active clients)"
    )
    days_back: int = Field(
        21,
        ge=1,
        le=90,
        description="Number of days to search back (default: 21 days / 3 weeks)"
    )
    max_results_per_source: int = Field(
        10,
        ge=1,
        le=100,
        description="Maximum results per API source (default: 10)"
    )
    force_mock: bool = Field(
        False,
        description="Force use of mock APIs for testing"
    )


class ExecuteMonitoringJobResponse(BaseModel):
    """Response from executing a monitoring job."""
    success: bool
    job_run_id: str
    clients_processed: int
    events_found: int
    events_new: int
    notifications_sent: int
    duration_seconds: float
    error: Optional[str] = None


@router.post("/execute", response_model=ExecuteMonitoringJobResponse)
async def execute_monitoring_job(
    request: ExecuteMonitoringJobRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute a client monitoring job immediately.

    This endpoint allows you to run a monitoring job on-demand without
    creating a schedule. Useful for:
    - Testing the monitoring workflow
    - One-time monitoring runs
    - Manual triggered monitoring
    - Development and debugging

    The job will:
    1. Search configured APIs for client information
    2. Enrich with CRM data
    3. Process through AI for classification
    4. Create events
    5. Send notifications based on user preferences

    **Parameters:**
    - `client_ids`: Specific clients to monitor (null = all active clients)
    - `days_back`: Number of days to search back (1-90, default: 21)
    - `max_results_per_source`: Maximum results per API source (1-100, default: 10)
    - `force_mock`: Use mock APIs instead of real ones (for testing)

    **Returns:**
    - Job execution summary with metrics
    """
    try:
        logger.info(
            f"User {current_user.id} triggered manual monitoring job for business {current_user.business_id} "
            f"(days_back={request.days_back}, max_results={request.max_results_per_source})"
        )

        # Execute the monitoring job
        result = await AutomationEngineService.execute_client_monitoring_job(
            db=db,
            business_id=current_user.business_id,
            client_ids=request.client_ids,
            job_run_id=None,  # Generate new job run ID
            user_id=current_user.id,
            days_back=request.days_back,
            max_results_per_source=request.max_results_per_source,
            force_mock=request.force_mock
        )

        return ExecuteMonitoringJobResponse(
            success=result.get("success", False),
            job_run_id=str(result.get("job_run_id", "")),
            clients_processed=result.get("clients_processed", 0),
            events_found=result.get("events_found", 0),
            events_new=result.get("events_new", 0),
            notifications_sent=result.get("notifications_sent", 0),
            duration_seconds=result.get("duration_seconds", 0.0),
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"Error executing monitoring job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute monitoring job: {str(e)}"
        )


@router.post("/execute-for-client/{client_id}", response_model=ExecuteMonitoringJobResponse)
async def execute_monitoring_job_for_client(
    client_id: UUID,
    force_mock: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute monitoring job for a specific client.

    Quick endpoint to monitor a single client. Useful for:
    - Testing monitoring for a specific client
    - Client detail page "Refresh" button
    - On-demand client updates

    **Parameters:**
    - `client_id`: The client to monitor
    - `force_mock`: Use mock APIs (for testing)
    """
    try:
        logger.info(
            f"User {current_user.id} triggered monitoring for client {client_id}"
        )

        # Execute for single client
        result = await AutomationEngineService.execute_client_monitoring_job(
            db=db,
            business_id=current_user.business_id,
            client_ids=[client_id],
            job_run_id=None,
            user_id=current_user.id,
            force_mock=force_mock
        )

        return ExecuteMonitoringJobResponse(
            success=result.get("success", False),
            job_run_id=str(result.get("job_run_id", "")),
            clients_processed=result.get("clients_processed", 0),
            events_found=result.get("events_found", 0),
            events_new=result.get("events_new", 0),
            notifications_sent=result.get("notifications_sent", 0),
            duration_seconds=result.get("duration_seconds", 0.0),
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"Error executing monitoring job for client {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute monitoring job: {str(e)}"
        )


@router.post("/test", response_model=ExecuteMonitoringJobResponse)
async def test_monitoring_workflow(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Test the monitoring workflow with mock data.

    This endpoint runs a complete monitoring workflow using mock APIs only.
    No real API keys required. Perfect for:
    - Testing the system end-to-end
    - Demonstrating the workflow
    - Onboarding new users
    - Development and debugging

    The test will:
    1. Use mock search results (realistic test data)
    2. Use mock CRM data (deterministic based on client)
    3. Use mock AI classification (rule-based)
    4. Create real events in your database
    5. Send real notifications (if thresholds met)

    **Note:** This creates real events and notifications in your database.
    """
    try:
        logger.info(
            f"User {current_user.id} running test monitoring workflow"
        )

        # Execute with force_mock=True
        result = await AutomationEngineService.execute_client_monitoring_job(
            db=db,
            business_id=current_user.business_id,
            client_ids=None,  # All clients
            job_run_id=None,
            user_id=current_user.id,
            force_mock=True  # Force mock APIs
        )

        return ExecuteMonitoringJobResponse(
            success=result.get("success", False),
            job_run_id=str(result.get("job_run_id", "")),
            clients_processed=result.get("clients_processed", 0),
            events_found=result.get("events_found", 0),
            events_new=result.get("events_new", 0),
            notifications_sent=result.get("notifications_sent", 0),
            duration_seconds=result.get("duration_seconds", 0.0),
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"Error running test workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run test workflow: {str(e)}"
        )
