"""Automation schedule API endpoints."""

import logging
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.dependencies import get_current_active_user as get_current_user
from app.models.user import User
from app.schemas.automation_schedule import (
    AutomationScheduleResponse,
    AutomationScheduleCreate,
    AutomationScheduleUpdate,
    AutomationScheduleList
)
from app.services.automation_schedule_service import AutomationScheduleService
from app.services.scheduler_integration_service import SchedulerIntegrationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/automation-schedules", tags=["Automation Schedules"])


@router.get("/", response_model=AutomationScheduleList)
def list_schedules(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    job_type: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_desc: Optional[bool] = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List automation schedules for current business.

    Supports pagination, filtering by active status and job type, and sorting.
    """
    try:
        schedules, total = AutomationScheduleService.get_schedules(
            db=db,
            business_id=current_user.business_id,
            skip=skip,
            limit=limit,
            is_active=is_active,
            job_type=job_type,
            sort_by=sort_by,
            sort_desc=sort_desc
        )

        return {
            "items": schedules,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Error listing schedules: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list schedules"
        )


@router.get("/{schedule_id}", response_model=AutomationScheduleResponse)
def get_schedule(
    schedule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific automation schedule by ID."""
    try:
        schedule = AutomationScheduleService.get_schedule(
            db=db,
            schedule_id=schedule_id,
            business_id=current_user.business_id
        )

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )

        return schedule

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch schedule"
        )


@router.post("/", response_model=AutomationScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: AutomationScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new automation schedule.

    The schedule will be automatically registered with the scheduler if active.
    """
    # Ensure business_id matches current user
    if schedule_data.business_id != current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create schedules for other businesses"
        )

    # Set created_by_user_id to current user
    schedule_data.created_by_user_id = current_user.id

    try:
        # Create schedule in database
        schedule = AutomationScheduleService.create_schedule(
            db=db,
            schedule_data=schedule_data
        )

        # Register with scheduler if active
        if schedule.is_active and schedule.schedule_type != "manual":
            await SchedulerIntegrationService.add_schedule(schedule)

        logger.info(f"User {current_user.id} created schedule {schedule.id}")
        return schedule

    except Exception as e:
        logger.error(f"Error creating schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create schedule: {str(e)}"
        )


@router.put("/{schedule_id}", response_model=AutomationScheduleResponse)
async def update_schedule(
    schedule_id: UUID,
    updates: AutomationScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an automation schedule.

    Changes to schedule configuration will be reflected in the scheduler.
    """
    try:
        # Update schedule in database
        schedule = AutomationScheduleService.update_schedule(
            db=db,
            schedule_id=schedule_id,
            updates=updates,
            business_id=current_user.business_id
        )

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )

        # Update in scheduler
        await SchedulerIntegrationService.update_schedule(schedule)

        logger.info(f"User {current_user.id} updated schedule {schedule_id}")
        return schedule

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update schedule: {str(e)}"
        )


@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an automation schedule.

    This will remove the schedule from the database and unregister it from the scheduler.
    """
    try:
        # Delete from database
        success = AutomationScheduleService.delete_schedule(
            db=db,
            schedule_id=schedule_id,
            business_id=current_user.business_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )

        # Remove from scheduler
        await SchedulerIntegrationService.remove_schedule(schedule_id)

        logger.info(f"User {current_user.id} deleted schedule {schedule_id}")
        return {"message": "Schedule deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete schedule"
        )


@router.post("/{schedule_id}/activate", response_model=AutomationScheduleResponse)
async def activate_schedule(
    schedule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Activate a schedule.

    This will enable the schedule and register it with the scheduler.
    """
    try:
        schedule = AutomationScheduleService.activate_schedule(
            db=db,
            schedule_id=schedule_id,
            business_id=current_user.business_id
        )

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )

        # Register with scheduler
        if schedule.schedule_type != "manual":
            await SchedulerIntegrationService.add_schedule(schedule)

        logger.info(f"User {current_user.id} activated schedule {schedule_id}")
        return schedule

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate schedule"
        )


@router.post("/{schedule_id}/deactivate", response_model=AutomationScheduleResponse)
async def deactivate_schedule(
    schedule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deactivate a schedule.

    This will disable the schedule and unregister it from the scheduler.
    """
    try:
        schedule = AutomationScheduleService.deactivate_schedule(
            db=db,
            schedule_id=schedule_id,
            business_id=current_user.business_id
        )

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )

        # Remove from scheduler
        await SchedulerIntegrationService.remove_schedule(schedule_id)

        logger.info(f"User {current_user.id} deactivated schedule {schedule_id}")
        return schedule

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate schedule"
        )


@router.post("/{schedule_id}/trigger")
async def trigger_schedule(
    schedule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger a schedule to run immediately.

    Useful for testing or running jobs on-demand outside their normal schedule.
    """
    try:
        # Verify schedule exists and belongs to user's business
        schedule = AutomationScheduleService.get_schedule(
            db=db,
            schedule_id=schedule_id,
            business_id=current_user.business_id
        )

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )

        # Trigger the job
        result = await SchedulerIntegrationService.trigger_manual_run(
            db=db,
            schedule_id=schedule_id
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to trigger schedule")
            )

        logger.info(f"User {current_user.id} manually triggered schedule {schedule_id}")
        return {
            "message": "Schedule triggered successfully",
            "schedule_id": str(schedule_id)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger schedule: {str(e)}"
        )


# Bulk Operations

from pydantic import BaseModel


class BulkScheduleOperationRequest(BaseModel):
    """Request for bulk schedule operations."""
    schedule_ids: List[UUID]


class BulkScheduleOperationResponse(BaseModel):
    """Response from bulk schedule operations."""
    success_count: int
    failed_count: int
    failed_ids: List[str]
    message: str


@router.post("/bulk/activate", response_model=BulkScheduleOperationResponse)
async def bulk_activate_schedules(
    request: BulkScheduleOperationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Activate multiple schedules at once.

    Useful for:
    - Enabling multiple schedules after configuration
    - Re-enabling schedules after maintenance
    - Bulk management operations
    """
    success_count = 0
    failed_count = 0
    failed_ids = []

    for schedule_id in request.schedule_ids:
        try:
            schedule = AutomationScheduleService.activate_schedule(
                db=db,
                schedule_id=schedule_id,
                business_id=current_user.business_id
            )

            if schedule:
                # Register with scheduler
                if schedule.schedule_type != "manual":
                    await SchedulerIntegrationService.add_schedule(schedule)
                success_count += 1
            else:
                failed_count += 1
                failed_ids.append(str(schedule_id))

        except Exception as e:
            logger.error(f"Error activating schedule {schedule_id}: {str(e)}")
            failed_count += 1
            failed_ids.append(str(schedule_id))

    logger.info(
        f"User {current_user.id} bulk activated {success_count} schedules, "
        f"{failed_count} failed"
    )

    return BulkScheduleOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        failed_ids=failed_ids,
        message=f"Activated {success_count} schedule(s), {failed_count} failed"
    )


@router.post("/bulk/deactivate", response_model=BulkScheduleOperationResponse)
async def bulk_deactivate_schedules(
    request: BulkScheduleOperationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deactivate multiple schedules at once.

    Useful for:
    - Temporarily pausing automation
    - Disabling schedules during maintenance
    - Bulk management operations
    """
    success_count = 0
    failed_count = 0
    failed_ids = []

    for schedule_id in request.schedule_ids:
        try:
            schedule = AutomationScheduleService.deactivate_schedule(
                db=db,
                schedule_id=schedule_id,
                business_id=current_user.business_id
            )

            if schedule:
                # Remove from scheduler
                await SchedulerIntegrationService.remove_schedule(schedule_id)
                success_count += 1
            else:
                failed_count += 1
                failed_ids.append(str(schedule_id))

        except Exception as e:
            logger.error(f"Error deactivating schedule {schedule_id}: {str(e)}")
            failed_count += 1
            failed_ids.append(str(schedule_id))

    logger.info(
        f"User {current_user.id} bulk deactivated {success_count} schedules, "
        f"{failed_count} failed"
    )

    return BulkScheduleOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        failed_ids=failed_ids,
        message=f"Deactivated {success_count} schedule(s), {failed_count} failed"
    )


@router.post("/bulk/delete", response_model=BulkScheduleOperationResponse)
async def bulk_delete_schedules(
    request: BulkScheduleOperationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete multiple schedules at once.

    Useful for:
    - Cleaning up old schedules
    - Bulk management operations

    **Warning:** This operation cannot be undone.
    """
    success_count = 0
    failed_count = 0
    failed_ids = []

    for schedule_id in request.schedule_ids:
        try:
            success = AutomationScheduleService.delete_schedule(
                db=db,
                schedule_id=schedule_id,
                business_id=current_user.business_id
            )

            if success:
                # Remove from scheduler
                await SchedulerIntegrationService.remove_schedule(schedule_id)
                success_count += 1
            else:
                failed_count += 1
                failed_ids.append(str(schedule_id))

        except Exception as e:
            logger.error(f"Error deleting schedule {schedule_id}: {str(e)}")
            failed_count += 1
            failed_ids.append(str(schedule_id))

    logger.info(
        f"User {current_user.id} bulk deleted {success_count} schedules, "
        f"{failed_count} failed"
    )

    return BulkScheduleOperationResponse(
        success_count=success_count,
        failed_count=failed_count,
        failed_ids=failed_ids,
        message=f"Deleted {success_count} schedule(s), {failed_count} failed"
    )
