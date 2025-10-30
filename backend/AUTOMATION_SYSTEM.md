# Client Monitoring Automation System

## Overview

This document describes the complete automation system built for proactive customer success monitoring. The system automates the collection, processing, and notification of client-related events using configurable schedules and AI-powered analysis.

## Architecture

### Workflow Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                     AUTOMATION WORKFLOW                              │
└─────────────────────────────────────────────────────────────────────┘

1. SCHEDULED TRIGGER (APScheduler)
   ↓
2. SEARCH & COLLECT
   ├── Google Custom Search API
   ├── NewsAPI (placeholder)
   ├── Serper API (placeholder)
   └── Mock API (fallback)
   ↓
3. SAVE RAW DATA (EventRawData table)
   ↓
4. CRM ENRICHMENT
   ├── Salesforce API
   ├── HubSpot API (placeholder)
   └── Mock API (fallback)
   ↓
5. AI CLASSIFICATION (OpenAI/Anthropic/Mock)
   ├── Categorization
   ├── Relevance scoring (0.0-1.0)
   ├── Sentiment analysis (-1.0 to 1.0)
   └── Risk assessment
   ↓
6. CREATE EVENTS (Event table)
   ↓
7. NOTIFICATION FILTERING (UserPreference)
   ├── Relevance threshold check
   ├── Category filters
   └── Assignment rules
   ↓
8. AI INSIGHTS GENERATION (for high-relevance events >= 0.7)
   ├── Detailed insights
   ├── Recommended actions
   └── Urgency assessment
   ↓
9. NOTIFICATIONS
   ├── In-app (Notification table)
   └── Email (EmailLog table)
```

## Database Schema

### New Tables

#### 1. user_preferences
Stores user notification preferences and thresholds.

**Fields:**
- `id` (UUID) - Primary key
- `user_id` (Integer) - Foreign key to users
- `business_id` (UUID) - Foreign key to businesses
- `notification_enabled` (Boolean) - Enable in-app notifications
- `email_notifications_enabled` (Boolean) - Enable email notifications
- `relevance_threshold` (Float, 0.0-1.0) - Minimum relevance score for notifications
- `notification_categories` (JSON) - Categories to monitor (null = all)
- `notification_frequency` (String) - instant, daily, weekly
- `assigned_clients_only` (Boolean) - Only notify for assigned clients
- `digest_time` (Time) - Time of day for digests
- `digest_day_of_week` (Integer, 0-6) - Day for weekly digests
- `created_at` (DateTime)
- `updated_at` (DateTime)

#### 2. event_raw_data
Stores unprocessed API responses for debugging and reprocessing.

**Fields:**
- `id` (UUID) - Primary key
- `business_id` (UUID) - Foreign key to businesses
- `client_id` (UUID) - Foreign key to clients
- `source_api` (String) - API source (google_search, news_api, etc.)
- `raw_content` (Text) - JSON string of raw API response
- `content_hash` (String) - SHA256 hash for deduplication
- `is_processed` (Boolean) - Processing status
- `processed_into_event_id` (UUID) - Link to created event
- `created_at` (DateTime)
- `processed_at` (DateTime)

#### 3. automation_schedules
User-defined schedules for automated monitoring jobs.

**Fields:**
- `id` (UUID) - Primary key
- `business_id` (UUID) - Foreign key to businesses
- `created_by_user_id` (Integer) - Foreign key to users
- `name` (String) - User-friendly schedule name
- `description` (Text) - Schedule description
- `job_type` (String) - client_monitoring, search_only, notification_digest
- `client_ids` (JSON) - Client UUIDs to monitor (null = all)
- `config` (JSON) - Job configuration (force_mock, etc.)
- `schedule_type` (String) - manual, hourly, daily, weekly, monthly, custom
- `cron_expression` (String) - Custom cron expression
- `hour_of_day` (Integer, 0-23) - Hour for daily/weekly schedules
- `minute_of_hour` (Integer, 0-59) - Minute for hourly schedules
- `day_of_week` (Integer, 0-6) - Day for weekly schedules (0=Monday)
- `day_of_month` (Integer, 1-31) - Day for monthly schedules
- `is_active` (Boolean) - Whether schedule is active
- `last_run_at` (DateTime) - Last execution timestamp
- `next_run_at` (DateTime) - Next scheduled execution
- `last_run_status` (String) - success, failed
- `last_run_job_id` (UUID) - Foreign key to job_runs
- `consecutive_failures` (Integer) - Failure counter (auto-disable at 5)
- `last_error_message` (Text) - Last error description
- `last_error_at` (DateTime) - Last error timestamp
- `created_at` (DateTime)
- `updated_at` (DateTime)

#### 4. email_logs
Tracks email delivery, opens, and clicks.

**Fields:**
- `id` (UUID) - Primary key
- `business_id` (UUID) - Foreign key to businesses
- `user_id` (Integer) - Foreign key to users
- `event_id` (UUID) - Foreign key to events (nullable)
- `job_run_id` (UUID) - Foreign key to job_runs (nullable)
- `email_type` (String) - event_notification, digest, alert, system
- `recipient_email` (String) - Email address
- `subject` (String) - Email subject
- `body_preview` (Text) - Email body preview
- `sent_at` (DateTime) - Send timestamp
- `status` (String) - sent, failed, pending, bounced
- `error_message` (Text) - Error details if failed
- `retry_count` (Integer) - Number of retry attempts
- `provider` (String) - Email provider (smtp, sendgrid, etc.)
- `provider_message_id` (String) - Provider's message ID
- `opened_at` (DateTime) - Email open timestamp
- `clicked_at` (DateTime) - Link click timestamp

## Service Layer

### Core Services

#### 1. MockAPIService
Provides realistic test data when real APIs are unavailable.

**Methods:**
- `mock_search_results()` - Google-formatted search results
- `mock_news_results()` - News API formatted results
- `mock_crm_data()` - Salesforce-like CRM data (deterministic)
- `mock_ai_classification()` - Rule-based event classification
- `mock_ai_insights()` - Contextual insights generation

#### 2. GoogleSearchService
Google Custom Search API integration.

**Methods:**
- `search_client()` - Search for client with keywords
- `build_search_query()` - Optimize search query with client info
- `extract_results_for_storage()` - Normalize results

**Configuration Required:**
- `GOOGLE_SEARCH_API_KEY` - API key
- `GOOGLE_SEARCH_ENGINE_ID` - Custom search engine ID

#### 3. SalesforceService
Salesforce CRM OAuth and data fetching.

**Methods:**
- `authenticate()` - OAuth 2.0 authentication
- `get_enriched_account_data()` - Fetch account, contacts, opportunities, cases

**Configuration Required:**
- `SALESFORCE_CLIENT_ID`
- `SALESFORCE_CLIENT_SECRET`
- `SALESFORCE_REFRESH_TOKEN` (or username/password)

#### 4. CRMService
Unified CRM abstraction layer with automatic fallback.

**Methods:**
- `enrich_client()` - Get CRM data (auto-routes to provider or mock)
- `is_at_risk()` - Check if client is at risk
- `calculate_engagement_score()` - Calculate 0.0-1.0 engagement score

#### 5. AIProcessorService
AI processing with multi-provider support.

**Methods:**
- `classify_event()` - Classify and score events
- `generate_insights()` - Generate insights for high-relevance events

**Supported Providers:**
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Mock (rule-based, no API key needed)

#### 6. SearchAggregatorService
Multi-source search with deduplication.

**Methods:**
- `search_all_sources()` - Search all configured APIs in parallel
- `deduplicate_results()` - Remove duplicates by URL/title/content

#### 7. UserPreferenceService
User preference management and notification filtering.

**Methods:**
- `get_or_create_preferences()` - Get preferences with defaults
- `update_preferences()` - Update user settings
- `should_notify_for_event()` - Check if user should be notified
- `get_users_to_notify()` - Get all users to notify for an event
- `get_users_for_digest()` - Get users for digest emails

#### 8. AutomationScheduleService
Schedule CRUD and time calculations.

**Methods:**
- `create_schedule()` - Create new schedule
- `get_schedules()` - List schedules with filters
- `update_schedule()` - Update schedule configuration
- `delete_schedule()` - Delete schedule
- `activate_schedule()` / `deactivate_schedule()` - Toggle schedule
- `get_all_active_schedules()` - Get all active schedules
- `update_last_run()` - Update execution timestamp
- `record_job_success()` / `record_job_failure()` - Track execution results

#### 9. EventRawDataService
Raw data storage and processing tracking.

**Methods:**
- `save_raw_data()` - Save single raw API response
- `bulk_save_raw_data()` - Save multiple responses
- `mark_as_processed()` - Link raw data to created event
- `get_unprocessed_data()` - Get data pending processing

#### 10. EmailService
SMTP email delivery with HTML templates.

**Methods:**
- `send_event_notification()` - Send event notification email
- `_build_event_email_html()` - Build beautiful HTML email

**Configuration Required:**
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`

#### 11. AutomationEngineService
**Core orchestration service** - ties everything together.

**Methods:**
- `execute_client_monitoring_job()` - Execute complete workflow
- `_process_single_client()` - Process one client
- `_create_job_run()` - Initialize job tracking
- `_complete_job_run()` - Finalize job with metrics

**Workflow:**
1. Create JobRun record
2. Get clients to monitor
3. For each client:
   - Search APIs (SearchAggregatorService)
   - Save raw data (EventRawDataService)
   - Enrich with CRM (CRMService)
   - Classify with AI (AIProcessorService)
   - Create Events (EventService)
   - Check notification thresholds (UserPreferenceService)
   - Generate insights for qualifying events (AIProcessorService)
   - Send notifications (NotificationService, EmailService)
4. Update JobRun with metrics

#### 12. SchedulerIntegrationService
APScheduler integration with FastAPI lifecycle.

**Methods:**
- `start_scheduler()` - Initialize and load schedules
- `shutdown_scheduler()` - Graceful shutdown
- `register_schedule()` - Register single schedule
- `add_schedule()` / `update_schedule()` / `remove_schedule()` - Dynamic management
- `trigger_manual_run()` - Manually execute schedule
- `get_scheduler_status()` - Get current status

**Features:**
- Automatic schedule loading on startup
- Real-time updates without restart
- Graceful handling of failures
- Auto-disable after 5 consecutive failures
- Support for all schedule types

## API Endpoints

### User Preferences

#### GET /api/v1/user-preferences/me
Get current user's preferences (creates defaults if none exist).

**Response:**
```json
{
  "id": "uuid",
  "user_id": 123,
  "business_id": "uuid",
  "notification_enabled": true,
  "email_notifications_enabled": true,
  "relevance_threshold": 0.7,
  "notification_categories": ["expansion", "risk"],
  "notification_frequency": "instant",
  "assigned_clients_only": false,
  "digest_time": "09:00:00",
  "digest_day_of_week": 0,
  "created_at": "2025-10-28T...",
  "updated_at": "2025-10-28T..."
}
```

#### PUT /api/v1/user-preferences/me
Update current user's preferences.

**Request Body:**
```json
{
  "relevance_threshold": 0.8,
  "notification_categories": ["risk", "expansion"],
  "notification_frequency": "daily",
  "digest_time": "10:00:00"
}
```

#### GET /api/v1/user-preferences/{user_id}
Get specific user's preferences (admin only or own).

#### POST /api/v1/user-preferences/
Create preferences for a user (admin only).

#### DELETE /api/v1/user-preferences/{preference_id}
Delete preferences (admin only).

### Automation Schedules

#### GET /api/v1/automation-schedules/
List schedules with filtering and pagination.

**Query Parameters:**
- `skip` (default: 0) - Pagination offset
- `limit` (default: 50, max: 100) - Items per page
- `is_active` (optional) - Filter by active status
- `job_type` (optional) - Filter by job type

**Response:**
```json
{
  "schedules": [...],
  "total": 10,
  "skip": 0,
  "limit": 50
}
```

#### POST /api/v1/automation-schedules/
Create new schedule.

**Request Body:**
```json
{
  "business_id": "uuid",
  "created_by_user_id": 123,
  "name": "Daily Morning Monitoring",
  "description": "Monitor all clients every morning",
  "job_type": "client_monitoring",
  "client_ids": null,
  "schedule_type": "daily",
  "hour_of_day": 9,
  "is_active": true
}
```

**Schedule Types:**
- `manual` - No automatic execution
- `hourly` - Every hour at specified minute
- `daily` - Daily at specified hour
- `weekly` - Weekly on specified day and hour
- `monthly` - Monthly on specified day and hour
- `custom` - Custom cron expression

#### GET /api/v1/automation-schedules/{schedule_id}
Get specific schedule.

#### PUT /api/v1/automation-schedules/{schedule_id}
Update schedule.

#### DELETE /api/v1/automation-schedules/{schedule_id}
Delete schedule.

#### POST /api/v1/automation-schedules/{schedule_id}/activate
Activate schedule (starts scheduling).

#### POST /api/v1/automation-schedules/{schedule_id}/deactivate
Deactivate schedule (stops scheduling).

#### POST /api/v1/automation-schedules/{schedule_id}/trigger
Manually trigger schedule to run immediately.

### Email Logs

#### GET /api/v1/email-logs/
List email logs with filtering.

**Query Parameters:**
- `skip`, `limit` - Pagination
- `email_type` - Filter by type
- `status` - Filter by status
- `recipient_email` - Filter by recipient
- `event_id` - Filter by event
- `start_date`, `end_date` - Date range filter

#### GET /api/v1/email-logs/{log_id}
Get specific email log.

#### GET /api/v1/email-logs/user/{user_id}
Get logs for specific user.

#### GET /api/v1/email-logs/event/{event_id}
Get logs related to specific event.

#### GET /api/v1/email-logs/stats/summary
Get email statistics.

**Response:**
```json
{
  "total_emails": 100,
  "sent": 95,
  "failed": 3,
  "pending": 2,
  "bounced": 0,
  "opened": 70,
  "clicked": 25,
  "open_rate": 73.68,
  "click_rate": 26.32,
  "delivery_rate": 95.0,
  "by_type": {
    "event_notification": 80,
    "digest": 15,
    "alert": 5
  }
}
```

### Scheduler Status

#### GET /api/v1/scheduler/status
Get current scheduler status.

**Response:**
```json
{
  "running": true,
  "total_jobs": 5,
  "jobs": [
    {
      "id": "schedule-uuid",
      "name": "Daily Morning Monitoring",
      "next_run": "2025-10-29T09:00:00Z"
    }
  ]
}
```

## Configuration

### Environment Variables

#### Required for Production

**Database:**
- `DATABASE_URL` - Database connection string

**API Keys (at least one search API):**
- `GOOGLE_SEARCH_API_KEY` - Google Custom Search API
- `GOOGLE_SEARCH_ENGINE_ID` - Custom search engine ID
- `NEWS_API_KEY` - NewsAPI key (optional)
- `SERPER_API_KEY` - Serper API key (optional)

**CRM (at least one recommended):**
- `SALESFORCE_CLIENT_ID`
- `SALESFORCE_CLIENT_SECRET`
- `SALESFORCE_REFRESH_TOKEN`
- `HUBSPOT_API_KEY` (optional, not yet implemented)

**AI Provider (at least one recommended):**
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key

**Email (required for notifications):**
- `SMTP_HOST` - SMTP server
- `SMTP_PORT` - SMTP port (587 for TLS, 465 for SSL)
- `SMTP_USERNAME` - SMTP username
- `SMTP_PASSWORD` - SMTP password
- `SMTP_FROM_EMAIL` - From email address
- `SMTP_FROM_NAME` - From name

#### Optional for Development

**Mock Mode:**
- Set `force_mock=true` in schedule config to use mock APIs
- Mock APIs work without any API keys

## Usage Examples

### Creating a Daily Monitoring Schedule

```python
import requests

# Create schedule
response = requests.post(
    "http://localhost:8000/api/v1/automation-schedules/",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "business_id": "your-business-uuid",
        "created_by_user_id": 123,
        "name": "Daily Client Monitoring",
        "description": "Monitor all clients every day at 9 AM",
        "job_type": "client_monitoring",
        "client_ids": None,  # Monitor all clients
        "schedule_type": "daily",
        "hour_of_day": 9,
        "is_active": True
    }
)

schedule = response.json()
print(f"Created schedule: {schedule['id']}")
```

### Setting User Notification Preferences

```python
# Update preferences
response = requests.put(
    "http://localhost:8000/api/v1/user-preferences/me",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "relevance_threshold": 0.8,  # Only high-relevance events
        "notification_categories": ["risk", "expansion"],  # Only these categories
        "notification_frequency": "daily",  # Daily digest
        "digest_time": "10:00:00",  # 10 AM digest
        "assigned_clients_only": True  # Only assigned clients
    }
)
```

### Manually Triggering a Schedule

```python
# Trigger schedule immediately
response = requests.post(
    f"http://localhost:8000/api/v1/automation-schedules/{schedule_id}/trigger",
    headers={"Authorization": f"Bearer {token}"}
)

print(response.json())
# {"message": "Schedule triggered successfully", "schedule_id": "..."}
```

## Testing

### Using Mock APIs

For testing without API keys, create schedules with mock configuration:

```python
{
  "name": "Test Schedule",
  "job_type": "client_monitoring",
  "schedule_type": "manual",
  "config": "{\"force_mock\": true}",  # Force mock APIs
  "is_active": True
}
```

Then trigger manually:
```bash
POST /api/v1/automation-schedules/{id}/trigger
```

### Expected Behavior

With mock APIs, the system will:
1. Generate realistic search results (3-5 results per client)
2. Create deterministic CRM data (same client_id = same data)
3. Use rule-based AI classification (no API calls)
4. Create events with relevance scores
5. Send notifications based on thresholds
6. Track everything in JobRun

## Monitoring

### Check Scheduler Health

```bash
GET /api/v1/scheduler/status
```

### View Recent Job Runs

```bash
GET /api/v1/scheduler/jobs/recent?limit=10
```

### Check Email Delivery Stats

```bash
GET /api/v1/email-logs/stats/summary
```

### Monitor Failed Schedules

Schedules with 5+ consecutive failures are automatically disabled.
Check `consecutive_failures` field in schedule details.

## Troubleshooting

### Schedule Not Running

1. Check if schedule is active: `GET /api/v1/automation-schedules/{id}`
2. Check scheduler status: `GET /api/v1/scheduler/status`
3. Check for errors in `last_error_message`
4. Check `consecutive_failures` (auto-disabled at 5)

### No Notifications Received

1. Check user preferences: `GET /api/v1/user-preferences/me`
2. Verify `notification_enabled` and `email_notifications_enabled` are true
3. Check `relevance_threshold` - events must meet this threshold
4. Check event relevance scores: `GET /api/v1/events/`
5. Check email logs: `GET /api/v1/email-logs/`

### API Failures

1. System automatically falls back to mock APIs on failure
2. Check `force_mock` in schedule config
3. Verify API keys in environment variables
4. Check service logs for API errors

## Performance Considerations

### Rate Limiting

- Google Search: 100 queries/day (free tier)
- OpenAI: Depends on plan
- Salesforce: Depends on plan

### Optimization

- Events are deduplicated by content hash
- Raw data is saved before processing for reprocessing
- AI insights only generated for high-relevance events (>= 0.7)
- Maximum 5 events created per client per job run
- Search results are cached in raw_data table

### Scaling

- Use background workers for job execution
- Implement job queuing (Celery, RQ)
- Add Redis for caching
- Use PostgreSQL for production
- Consider separate read replicas for analytics

## Next Steps

1. **Frontend Integration**: Connect React components to these APIs
2. **HubSpot Integration**: Complete HubSpot CRM service
3. **NewsAPI & Serper**: Complete news search integrations
4. **Webhook Support**: Add webhooks for event notifications
5. **Advanced Scheduling**: Add dependency chains and conditional execution
6. **Analytics Dashboard**: Visualize automation performance
7. **A/B Testing**: Test different notification strategies

## Support

For issues or questions:
- Check logs in `backend/logs/`
- Review API docs at `/docs`
- Check database with `alembic current`
- Verify migrations with `alembic history`
