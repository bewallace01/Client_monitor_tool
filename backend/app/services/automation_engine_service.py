"""Automation engine service - orchestrates the complete monitoring workflow.

This is the core service that brings together:
- Search APIs (Google, Serper, News)
- CRM enrichment (Salesforce, HubSpot)
- AI processing (OpenAI, Anthropic)
- Event creation and storage
- Notification filtering and delivery
- Email notifications
"""

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from typing import Protocol

# Lightweight Protocol to avoid hard import requirement during static analysis
class Session(Protocol):  # type: ignore
    def add(self, *args, **kwargs): ...
    def commit(self, *args, **kwargs): ...
    def refresh(self, *args, **kwargs): ...
    def query(self, *args, **kwargs): ...

from app.models.client import Client
from app.models.event import Event
from app.models.job_run import JobRun
from app.models.api_config import APIConfig
from app.schemas.api_config import APIProvider
from app.schemas.job_run import JobStatus

# Import all the services we need
from app.services.search_aggregator_service import SearchAggregatorService
from app.services.crm_service import CRMService
from app.services.ai_processor_service import AIProcessorService
from app.services.event_raw_data_service import EventRawDataService
from app.services.event_service import EventService
from app.services.user_preference_service import UserPreferenceService
from app.services.email_service import EmailService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class AutomationEngineService:
    """Orchestrates the complete client monitoring automation workflow."""

    @staticmethod
    async def execute_client_monitoring_job(
        db: Session,
        business_id: uuid.UUID,
        client_ids: Optional[List[uuid.UUID]] = None,
        job_run_id: Optional[uuid.UUID] = None,
        user_id: Optional[int] = None,
        days_back: int = 30,
        max_results_per_source: int = 10,
        force_mock: bool = False
    ) -> Dict[str, Any]:
        """
        Execute full client monitoring workflow.

        Steps:
        1. Create/update JobRun record
        2. For each client:
           a. Search all configured APIs
           b. Save raw data
           c. Enrich with CRM data
           d. Process through AI to create Events
           e. Check notification thresholds
           f. Generate insights for qualifying events
           g. Send notifications
        3. Update JobRun with metrics
        4. Return summary

        Args:
            db: Database session
            business_id: Business UUID
            client_ids: Optional list of specific client IDs (None = all active clients)
            job_run_id: Optional existing JobRun ID
            user_id: Optional user ID who triggered the job
            days_back: Number of days to search back (default: 30)
            max_results_per_source: Maximum results per API source (default: 10)
            force_mock: Force use of mock APIs (for testing)

        Returns:
            Dict with execution summary
        """
        logger.info(f"Starting client monitoring job for business {business_id}")

        # Create or get job run
        if not job_run_id:
            job_run_id = uuid.uuid4()

        job_run = AutomationEngineService._create_job_run(
            db=db,
            job_run_id=job_run_id,
            business_id=business_id,
            job_type="client_monitoring"
        )

        try:
            # Get clients to monitor
            clients = AutomationEngineService._get_clients_to_monitor(
                db=db,
                business_id=business_id,
                client_ids=client_ids
            )

            if not clients:
                logger.warning(f"No active clients found for business {business_id}")
                AutomationEngineService._complete_job_run(
                    db=db,
                    job_run=job_run,
                    events_found=0,
                    events_new=0,
                    clients_processed=0
                )
                return {
                    "success": True,
                    "message": "No active clients to monitor",
                    "clients_processed": 0,
                    "events_found": 0,
                    "events_new": 0
                }

            # Get AI API configuration
            ai_config = AutomationEngineService._get_ai_config(db, business_id)
            ai_provider = ai_config.provider if ai_config else "mock"
            ai_api_key = ai_config.api_key if ai_config else None

            total_events_found = 0
            total_events_new = 0
            clients_processed = 0

            # Process each client
            for client in clients:
                try:
                    logger.info(f"Processing client: {client.name}")

                    result = await AutomationEngineService._process_single_client(
                        db=db,
                        business_id=business_id,
                        client=client,
                        job_run_id=job_run.id,
                        ai_provider=ai_provider,
                        ai_api_key=ai_api_key,
                        force_mock=force_mock,
                        days_back=days_back,
                        max_results_per_source=max_results_per_source
                    )

                    total_events_found += result["events_found"]
                    total_events_new += result["events_new"]
                    clients_processed += 1

                except Exception as e:
                    logger.error(f"Failed to process client {client.name}: {str(e)}")
                    continue

            # Complete job run
            AutomationEngineService._complete_job_run(
                db=db,
                job_run=job_run,
                events_found=total_events_found,
                events_new=total_events_new,
                clients_processed=clients_processed
            )

            logger.info(
                f"Completed client monitoring job: {clients_processed} clients, "
                f"{total_events_new} new events"
            )

            return {
                "success": True,
                "job_run_id": str(job_run.id),
                "clients_processed": clients_processed,
                "events_found": total_events_found,
                "events_new": total_events_new
            }

        except Exception as e:
            logger.error(f"Client monitoring job failed: {str(e)}")
            AutomationEngineService._fail_job_run(db, job_run, str(e))
            raise

    @staticmethod
    async def _process_single_client(
        db: Session,
        business_id: uuid.UUID,
        client: Client,
        job_run_id: uuid.UUID,
        ai_provider: str,
        ai_api_key: Optional[str],
        force_mock: bool = False,
        days_back: int = 30,
        max_results_per_source: int = 10
    ) -> Dict[str, int]:
        """Process monitoring for a single client."""

        events_found = 0
        events_new = 0

        # Step 1: Search all configured APIs
        logger.info(f"Searching for {client.name}...")
        search_results = await SearchAggregatorService.search_all_sources(
            db=db,
            business_id=business_id,
            client=client,
            days_back=days_back,
            max_results_per_source=max_results_per_source,
            force_mock=force_mock,
            job_run_id=job_run_id
        )

        results = search_results.get("results", [])
        events_found = len(results)

        if not results:
            logger.info(f"No search results found for {client.name}")
            return {"events_found": 0, "events_new": 0}

        # Step 2: Save raw data
        logger.info(f"Saving {len(results)} raw data entries for {client.name}...")
        saved_raw_data = EventRawDataService.bulk_save_raw_data(
            db=db,
            business_id=business_id,
            client_id=client.id,
            job_run_id=job_run_id,
            source_api=search_results.get("sources_used", ["unknown"])[0],
            results=results,
            search_query=f"{client.name}"
        )

        # Step 3: Get CRM enrichment
        logger.info(f"Fetching CRM data for {client.name}...")
        crm_data = await CRMService.enrich_client(
            db=db,
            business_id=business_id,
            client=client,
            force_mock=force_mock
        )

        # Step 4: Process each result through AI and create events
        # Process all results (limited by max_results_per_source from search)
        for idx, result in enumerate(results):
            try:
                # Prepare raw data for AI
                raw_data_for_ai = {
                    "items": [result] if "items" not in result else result["items"]
                }

                # AI Classification
                logger.info(f"Classifying event {idx+1}/{len(results[:5])} for {client.name}...")
                classification = await AIProcessorService.classify_event(
                    raw_data=raw_data_for_ai,
                    client=client,
                    crm_data=crm_data,
                    provider=ai_provider,
                    api_key=ai_api_key
                )

                #Extract URL (NewsAPI uses "url", Google uses "link")
                event_url = result.get("url") or result.get("link")
                event_source = result.get("source", "Unknown")
                
                # Check for duplicate events
                existing_event = AutomationEngineService._check_duplicate_event(
                    db=db,
                    business_id=business_id,
                    client_id=client.id,
                    title=classification.get("title", ""),
                    url=event_url,
                    source=event_source
                )

                if existing_event:
                    logger.info(f"Duplicate event found, skipping: {classification.get('title')}")
                    continue

                # Create event
                event = AutomationEngineService._create_event_from_classification(
                    db=db,
                    business_id=business_id,
                    client_id=client.id,
                    classification=classification,
                    source=event_source,
                    url=event_url
                )

                events_new += 1

                # Mark raw data as processed
                if idx < len(saved_raw_data):
                    EventRawDataService.mark_as_processed(
                        db=db,
                        raw_data_id=saved_raw_data[idx].id,
                        event_id=event.id
                    )

                # Step 5: Check if event meets notification threshold
                users_to_notify = UserPreferenceService.get_users_to_notify(
                    db=db,
                    business_id=business_id,
                    event=event
                )

                if not users_to_notify:
                    logger.info(f"No users to notify for event: {event.title}")
                    continue

                # Step 6: Generate AI insights for high-relevance events
                insights = None
                if event.relevance_score >= 0.7:
                    logger.info(f"Generating insights for high-relevance event: {event.title}")
                    insights = await AIProcessorService.generate_insights(
                        event=event,
                        client=client,
                        crm_data=crm_data,
                        provider=ai_provider,
                        api_key=ai_api_key
                    )

                # Step 7: Send notifications
                for user in users_to_notify:
                    try:
                        # Create in-app notification
                        NotificationService.create_notification(
                            db=db,
                            business_id=business_id,
                            user_id=user.id,
                            notification_type="high_relevance_event",
                            title=f"New Event: {client.name}",
                            message=event.title,
                            related_event_id=event.id,
                            related_client_id=client.id,
                            priority="high" if event.relevance_score >= 0.8 else "normal"
                        )

                        # Send email if enabled
                        user_prefs = UserPreferenceService.get_or_create_preferences(
                            db=db,
                            user_id=user.id,
                            business_id=business_id
                        )

                        if user_prefs.email_notifications_enabled:
                            await EmailService.send_event_notification(
                                db=db,
                                user=user,
                                event=event,
                                client=client,
                                insights=insights,
                                crm_data=crm_data
                            )

                    except Exception as e:
                        logger.error(f"Failed to notify user {user.id}: {str(e)}")
                        continue

            except Exception as e:
                logger.error(f"Failed to process result for {client.name}: {str(e)}")
                if idx < len(saved_raw_data):
                    EventRawDataService.mark_as_failed(
                        db=db,
                        raw_data_id=saved_raw_data[idx].id,
                        error_message=str(e)
                    )
                continue

        return {
            "events_found": events_found,
            "events_new": events_new
        }

    @staticmethod
    def _get_clients_to_monitor(
        db: Session,
        business_id: uuid.UUID,
        client_ids: Optional[List[uuid.UUID]]
    ) -> List[Client]:
        """Get list of clients to monitor."""
        query = db.query(Client).filter(
            Client.business_id == business_id,
            Client.is_active == True,
            Client.is_deleted == False
        )

        if client_ids:
            query = query.filter(Client.id.in_(client_ids))

        return query.all()

    @staticmethod
    def _get_ai_config(db: Session, business_id: uuid.UUID) -> Optional[APIConfig]:
        """Get AI API configuration for business."""
        ai_providers = [APIProvider.OPENAI, APIProvider.ANTHROPIC]

        return db.query(APIConfig).filter(
            APIConfig.business_id == business_id,
            APIConfig.provider.in_(ai_providers),
            APIConfig.is_active == True
        ).first()

    @staticmethod
    def _create_job_run(
        db: Session,
        job_run_id: uuid.UUID,
        business_id: uuid.UUID,
        job_type: str
    ) -> JobRun:
        """Create new job run record."""
        job_run = JobRun(
            id=job_run_id,
            job_id=str(job_run_id),
            job_type=job_type,
            business_id=business_id,
            status=JobStatus.RUNNING.value,
            started_at=datetime.utcnow()
        )
        db.add(job_run)
        db.commit()
        db.refresh(job_run)
        return job_run

    @staticmethod
    def _complete_job_run(
        db: Session,
        job_run: JobRun,
        events_found: int,
        events_new: int,
        clients_processed: int
    ):
        """Mark job run as completed."""
        job_run.mark_completed(
            events_found=events_found,
            events_new=events_new,
            clients_processed=clients_processed
        )
        db.commit()

    @staticmethod
    def _fail_job_run(db: Session, job_run: JobRun, error_message: str):
        """Mark job run as failed."""
        job_run.mark_failed(error_message)
        db.commit()

    @staticmethod
    def _check_duplicate_event(
        db: Session,
        business_id: uuid.UUID,
        client_id: uuid.UUID,
        title: str,
        url: Optional[str],
        source: Optional[str] = None,
    ) -> Optional[Event]:
        """Check if event already exists."""
        from datetime import timedelta
        
        # Only check for duplicates within the last 7 days to avoid false positives
        # from old test data or stale events
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        # Check by URL first (most reliable) - but only recent events
        if url:
            event = db.query(Event).filter(
                Event.business_id == business_id,
                Event.client_id == client_id,
                Event.url == url,
                Event.discovered_at >= seven_days_ago,
                Event.is_deleted == False
            ).first()
            if event:
                return event

        # Check by title with stricter constraints:
        # - Same source (to avoid cross-source false positives)
        # - Recently discovered (24 hours) to reduce over-aggressive dedupe
        one_day_ago = datetime.utcnow() - timedelta(days=1)

        filters = [
            Event.business_id == business_id,
            Event.client_id == client_id,
            Event.title == title,
            Event.discovered_at >= one_day_ago,
            Event.is_deleted == False,
        ]
        if source:
            filters.append(Event.source == source)

        event = db.query(Event).filter(*filters).first()

        return event

    @staticmethod
    def _create_event_from_classification(
        db: Session,
        business_id: uuid.UUID,
        client_id: uuid.UUID,
        classification: Dict[str, Any],
        source: str,
        url: Optional[str]
    ) -> Event:
        """Create event from AI classification."""
        import json

        # Parse event date
        event_date = datetime.utcnow()
        if classification.get("event_date"):
            try:
                event_date = datetime.fromisoformat(
                    classification["event_date"].replace("Z", "+00:00")
                )
            except:
                pass

        # Serialize tags
        tags_json = None
        if classification.get("tags"):
            tags_json = json.dumps(classification["tags"])

        event = Event(
            business_id=business_id,
            client_id=client_id,
            title=classification.get("title", "")[:500],
            description=classification.get("description"),
            url=url,
            source=source,
            source_type="news",
            category=classification.get("category", "other"),
            subcategory=classification.get("subcategory"),
            tags=tags_json,
            relevance_score=classification.get("relevance_score", 0.5),
            sentiment_score=classification.get("sentiment_score"),
            confidence_score=classification.get("confidence_score"),
            event_date=event_date,
            discovered_at=datetime.utcnow()
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        logger.info(f"Created event: {event.title}")
        return event