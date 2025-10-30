"""FastAPI application entry point."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.routes import (
    clients,
    events,
    event_interactions,
    analytics,
    scheduler,
    search,
    auth,
    users,
    businesses,
    tags,
    notifications,
    api_configs,
    user_preferences,
    automation_schedules,
    email_logs,
    monitoring_jobs,
    api_health,
)
from app.services.scheduler_integration_service import SchedulerIntegrationService

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Professional client intelligence monitoring platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(businesses.router, prefix=settings.API_V1_PREFIX)
app.include_router(clients.router, prefix=settings.API_V1_PREFIX)
app.include_router(events.router, prefix=settings.API_V1_PREFIX)
app.include_router(event_interactions.router, prefix=settings.API_V1_PREFIX)
app.include_router(tags.router, prefix=settings.API_V1_PREFIX)
app.include_router(notifications.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(scheduler.router, prefix=settings.API_V1_PREFIX)
app.include_router(search.router, prefix=settings.API_V1_PREFIX)
app.include_router(api_configs.router, prefix=f"{settings.API_V1_PREFIX}/api-configs", tags=["API Configurations"])
app.include_router(user_preferences.router, prefix=settings.API_V1_PREFIX)
app.include_router(automation_schedules.router, prefix=settings.API_V1_PREFIX)
app.include_router(email_logs.router, prefix=settings.API_V1_PREFIX)
app.include_router(monitoring_jobs.router, prefix=settings.API_V1_PREFIX)
app.include_router(api_health.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "api": settings.API_V1_PREFIX
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.get(f"{settings.API_V1_PREFIX}/info", tags=["Info"])
async def api_info():
    """API version and information."""
    return {
        "api_version": "v1",
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "environment": "development" if settings.DEBUG else "production"
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print(f"[STARTUP] {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    print(f"[INFO] Debug mode: {settings.DEBUG}")
    print(f"[INFO] API docs available at: http://localhost:8000/docs")
    print(f"[INFO] Registered {len(app.routes)} routes including auth routes")

    # Start the automation scheduler
    try:
        logger.info("Starting automation scheduler...")
        await SchedulerIntegrationService.start_scheduler()
        logger.info("Automation scheduler started successfully")
        print(f"[INFO] Automation scheduler started")
    except Exception as e:
        logger.error(f"Failed to start automation scheduler: {str(e)}")
        print(f"[ERROR] Failed to start automation scheduler: {str(e)}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print(f"[SHUTDOWN] {settings.APP_NAME} shutting down...")

    # Shutdown the automation scheduler
    try:
        logger.info("Shutting down automation scheduler...")
        await SchedulerIntegrationService.shutdown_scheduler()
        logger.info("Automation scheduler shut down successfully")
        print(f"[INFO] Automation scheduler shut down")
    except Exception as e:
        logger.error(f"Error shutting down automation scheduler: {str(e)}")
        print(f"[ERROR] Error shutting down automation scheduler: {str(e)}")


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

