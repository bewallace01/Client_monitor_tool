# Quick Start Guide: Client Monitoring Automation

This guide will help you set up your first automated client monitoring workflow in 5 minutes.

## Prerequisites

- Backend server running
- At least one client in your account
- User account with authentication token

## Option 1: Test with Mock APIs (No Setup Required)

The fastest way to see the system in action without any API keys.

### Step 1: Test the Monitoring Workflow

```bash
curl -X POST "http://localhost:8000/api/v1/monitoring-jobs/test" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

**What this does:**
- Runs complete monitoring workflow using mock APIs
- Creates real events in your database
- Sends notifications based on your preferences
- Returns execution summary

**Expected Response:**
```json
{
  "success": true,
  "job_run_id": "uuid",
  "clients_processed": 3,
  "events_found": 12,
  "events_new": 8,
  "notifications_sent": 4,
  "duration_seconds": 2.5
}
```

### Step 2: View Created Events

```bash
curl -X GET "http://localhost:8000/api/v1/events/?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

You should see newly created events with:
- Categories (risk, expansion, news, etc.)
- Relevance scores (0.0-1.0)
- Sentiment analysis (-1.0 to 1.0)
- AI-generated summaries

### Step 3: Create a Daily Schedule

```bash
curl -X POST "http://localhost:8000/api/v1/automation-schedules/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "YOUR_BUSINESS_ID",
    "created_by_user_id": YOUR_USER_ID,
    "name": "Daily Morning Monitoring (Mock)",
    "description": "Test schedule using mock APIs",
    "job_type": "client_monitoring",
    "client_ids": null,
    "config": "{\"force_mock\": true}",
    "schedule_type": "daily",
    "hour_of_day": 9,
    "is_active": true
  }'
```

**Result:** System will now automatically monitor all clients every day at 9 AM using mock data.

---

## Option 2: Production Setup with Real APIs

For actual client monitoring with real data sources.

### Step 1: Configure API Keys

Add these to your `.env` file:

```bash
# Search API (choose at least one)
GOOGLE_SEARCH_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id

# CRM (choose at least one)
SALESFORCE_CLIENT_ID=your_salesforce_client_id
SALESFORCE_CLIENT_SECRET=your_salesforce_client_secret
SALESFORCE_REFRESH_TOKEN=your_refresh_token

# AI Provider (choose at least one)
OPENAI_API_KEY=your_openai_key
# or
ANTHROPIC_API_KEY=your_anthropic_key

# Email (required for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME=Client Monitor
```

### Step 2: Configure API Settings via UI

1. Navigate to Settings > API Configurations
2. Add Google Search API configuration
3. Add Salesforce CRM configuration
4. Add OpenAI or Anthropic AI configuration

Or via API:

```bash
# Add Google Search API
curl -X POST "http://localhost:8000/api/v1/api-configs/api-configs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "google_search",
    "api_key": "YOUR_GOOGLE_API_KEY",
    "config": "{\"search_engine_id\": \"YOUR_SEARCH_ENGINE_ID\"}",
    "is_active": true
  }'
```

### Step 3: Set Your Notification Preferences

```bash
curl -X PUT "http://localhost:8000/api/v1/user-preferences/me" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "relevance_threshold": 0.7,
    "notification_categories": ["risk", "expansion", "news"],
    "notification_frequency": "instant",
    "email_notifications_enabled": true,
    "assigned_clients_only": false
  }'
```

**What these settings mean:**
- `relevance_threshold: 0.7` - Only notify for events with 70%+ relevance
- `notification_categories` - Only notify for these event types
- `notification_frequency: "instant"` - Get notified immediately
- `email_notifications_enabled: true` - Send email notifications

### Step 4: Run Your First Real Monitoring Job

```bash
curl -X POST "http://localhost:8000/api/v1/monitoring-jobs/execute" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_ids": null,
    "force_mock": false
  }'
```

This will:
1. Search Google for information about your clients
2. Enrich with Salesforce CRM data
3. Process through AI (OpenAI/Anthropic)
4. Create events with relevance scores
5. Send notifications to users who meet thresholds
6. Generate insights for high-relevance events

### Step 5: Create Production Schedule

```bash
curl -X POST "http://localhost:8000/api/v1/automation-schedules/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "YOUR_BUSINESS_ID",
    "created_by_user_id": YOUR_USER_ID,
    "name": "Daily Client Monitoring",
    "description": "Monitor all clients every morning",
    "job_type": "client_monitoring",
    "client_ids": null,
    "schedule_type": "daily",
    "hour_of_day": 9,
    "is_active": true
  }'
```

---

## Common Schedules

### Hourly Monitoring
```json
{
  "schedule_type": "hourly",
  "minute_of_hour": 0
}
```

### Weekly Monday Morning
```json
{
  "schedule_type": "weekly",
  "day_of_week": 0,
  "hour_of_day": 9
}
```

### Custom Cron (Weekdays at 9 AM and 3 PM)
```json
{
  "schedule_type": "custom",
  "cron_expression": "0 9,15 * * 1-5"
}
```

---

## Managing Schedules

### View All Schedules

```bash
curl -X GET "http://localhost:8000/api/v1/automation-schedules/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Activate/Deactivate Schedule

```bash
# Activate
curl -X POST "http://localhost:8000/api/v1/automation-schedules/{schedule_id}/activate" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Deactivate
curl -X POST "http://localhost:8000/api/v1/automation-schedules/{schedule_id}/deactivate" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Manually Trigger Schedule

```bash
curl -X POST "http://localhost:8000/api/v1/automation-schedules/{schedule_id}/trigger" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Bulk Operations

```bash
# Activate multiple schedules
curl -X POST "http://localhost:8000/api/v1/automation-schedules/bulk/activate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_ids": [
      "uuid1",
      "uuid2",
      "uuid3"
    ]
  }'
```

---

## Monitoring Your Automation

### Check Scheduler Status

```bash
curl -X GET "http://localhost:8000/api/v1/scheduler/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "running": true,
  "total_jobs": 5,
  "jobs": [
    {
      "id": "schedule-uuid",
      "name": "Daily Client Monitoring",
      "next_run": "2025-10-29T09:00:00Z"
    }
  ]
}
```

### View Recent Job Runs

```bash
curl -X GET "http://localhost:8000/api/v1/scheduler/jobs/recent?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Check Email Delivery Stats

```bash
curl -X GET "http://localhost:8000/api/v1/email-logs/stats/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "total_emails": 100,
  "sent": 95,
  "failed": 3,
  "pending": 2,
  "opened": 70,
  "clicked": 25,
  "open_rate": 73.68,
  "click_rate": 26.32,
  "delivery_rate": 95.0
}
```

---

## Troubleshooting

### Schedule Not Running

1. Check if active: `GET /api/v1/automation-schedules/{id}`
2. Check scheduler status: `GET /api/v1/scheduler/status`
3. Look for errors in `last_error_message`
4. Check `consecutive_failures` (auto-disabled at 5)

### No Events Created

1. Verify clients exist and are active
2. Check API configurations are valid
3. Try with `force_mock: true` first
4. Check job run details: `GET /api/v1/scheduler/jobs/recent`

### No Notifications Received

1. Check preferences: `GET /api/v1/user-preferences/me`
2. Verify `notification_enabled` and `email_notifications_enabled` are true
3. Check event relevance scores meet your threshold
4. Check email logs: `GET /api/v1/email-logs/`

### API Errors

- System automatically falls back to mock APIs on failure
- Check API key validity in settings
- Verify API quotas haven't been exceeded
- Test with single client first

---

## Next Steps

1. **Customize Notification Preferences**
   - Adjust relevance thresholds
   - Set up digest schedules
   - Configure category filters

2. **Create Multiple Schedules**
   - Different schedules for different client groups
   - Varied frequencies (hourly, daily, weekly)
   - Separate schedules for high-priority clients

3. **Monitor Performance**
   - Track email open rates
   - Review event relevance scores
   - Analyze job run durations

4. **Optimize Configuration**
   - Fine-tune AI prompts
   - Adjust search keywords
   - Configure CRM field mappings

---

## API Documentation

Full API documentation available at: `http://localhost:8000/docs`

Interactive API testing at: `http://localhost:8000/redoc`

---

## Support

For detailed documentation, see:
- [AUTOMATION_SYSTEM.md](./AUTOMATION_SYSTEM.md) - Complete system documentation
- [README.md](./README.md) - Project overview
- API Docs at `/docs` - Interactive API documentation

For issues:
- Check application logs
- Review database migrations
- Verify environment variables
- Test with mock APIs first
