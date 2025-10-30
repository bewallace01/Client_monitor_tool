# API Examples Collection

Complete collection of example API requests for testing the Client Monitoring Automation System.

## Table of Contents

1. [Authentication](#authentication)
2. [Monitoring Jobs](#monitoring-jobs)
3. [Automation Schedules](#automation-schedules)
4. [Bulk Operations](#bulk-operations)
5. [User Preferences](#user-preferences)
6. [Email Logs](#email-logs)
7. [Scheduler Status](#scheduler-status)

---

## Authentication

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'
```

**Save the token from response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Use in subsequent requests:**
```bash
export TOKEN="your_access_token_here"
```

---

## Monitoring Jobs

### 1. Test Workflow (Mock APIs)

**No API keys required - perfect for testing!**

```bash
curl -X POST "http://localhost:8000/api/v1/monitoring-jobs/test" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "success": true,
  "job_run_id": "123e4567-e89b-12d3-a456-426614174000",
  "clients_processed": 3,
  "events_found": 12,
  "events_new": 8,
  "notifications_sent": 4,
  "duration_seconds": 2.5,
  "error": null
}
```

### 2. Execute Monitoring Job (All Clients)

```bash
curl -X POST "http://localhost:8000/api/v1/monitoring-jobs/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_ids": null,
    "force_mock": false
  }'
```

### 3. Execute for Specific Clients

```bash
curl -X POST "http://localhost:8000/api/v1/monitoring-jobs/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_ids": [
      "client-uuid-1",
      "client-uuid-2"
    ],
    "force_mock": false
  }'
```

### 4. Execute for Single Client (Quick Refresh)

```bash
curl -X POST "http://localhost:8000/api/v1/monitoring-jobs/execute-for-client/CLIENT_UUID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**With Mock APIs:**
```bash
curl -X POST "http://localhost:8000/api/v1/monitoring-jobs/execute-for-client/CLIENT_UUID?force_mock=true" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Automation Schedules

### 1. List All Schedules

```bash
curl -X GET "http://localhost:8000/api/v1/automation-schedules/" \
  -H "Authorization: Bearer $TOKEN"
```

**With Filters:**
```bash
curl -X GET "http://localhost:8000/api/v1/automation-schedules/?is_active=true&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

### 2. Create Daily Schedule

```bash
curl -X POST "http://localhost:8000/api/v1/automation-schedules/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "YOUR_BUSINESS_UUID",
    "created_by_user_id": YOUR_USER_ID,
    "name": "Daily Morning Monitoring",
    "description": "Monitor all clients every morning at 9 AM",
    "job_type": "client_monitoring",
    "client_ids": null,
    "schedule_type": "daily",
    "hour_of_day": 9,
    "is_active": true
  }'
```

### 3. Create Hourly Schedule

```bash
curl -X POST "http://localhost:8000/api/v1/automation-schedules/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "YOUR_BUSINESS_UUID",
    "created_by_user_id": YOUR_USER_ID,
    "name": "Hourly Monitoring",
    "description": "Monitor every hour on the hour",
    "job_type": "client_monitoring",
    "client_ids": null,
    "schedule_type": "hourly",
    "minute_of_hour": 0,
    "is_active": true
  }'
```

### 4. Create Weekly Schedule

```bash
curl -X POST "http://localhost:8000/api/v1/automation-schedules/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "YOUR_BUSINESS_UUID",
    "created_by_user_id": YOUR_USER_ID,
    "name": "Weekly Monday Morning",
    "description": "Monitor every Monday at 9 AM",
    "job_type": "client_monitoring",
    "client_ids": null,
    "schedule_type": "weekly",
    "day_of_week": 0,
    "hour_of_day": 9,
    "is_active": true
  }'
```

### 5. Create Custom Cron Schedule

```bash
curl -X POST "http://localhost:8000/api/v1/automation-schedules/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "YOUR_BUSINESS_UUID",
    "created_by_user_id": YOUR_USER_ID,
    "name": "Weekdays 9 AM and 3 PM",
    "description": "Monitor twice daily on weekdays",
    "job_type": "client_monitoring",
    "client_ids": null,
    "schedule_type": "custom",
    "cron_expression": "0 9,15 * * 1-5",
    "is_active": true
  }'
```

### 6. Create Test Schedule with Mock APIs

```bash
curl -X POST "http://localhost:8000/api/v1/automation-schedules/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "YOUR_BUSINESS_UUID",
    "created_by_user_id": YOUR_USER_ID,
    "name": "Test Schedule (Mock)",
    "description": "Test schedule using mock APIs",
    "job_type": "client_monitoring",
    "client_ids": null,
    "config": "{\"force_mock\": true}",
    "schedule_type": "daily",
    "hour_of_day": 10,
    "is_active": true
  }'
```

### 7. Get Schedule Details

```bash
curl -X GET "http://localhost:8000/api/v1/automation-schedules/SCHEDULE_UUID" \
  -H "Authorization: Bearer $TOKEN"
```

### 8. Update Schedule

```bash
curl -X PUT "http://localhost:8000/api/v1/automation-schedules/SCHEDULE_UUID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Schedule Name",
    "hour_of_day": 10,
    "is_active": true
  }'
```

### 9. Activate Schedule

```bash
curl -X POST "http://localhost:8000/api/v1/automation-schedules/SCHEDULE_UUID/activate" \
  -H "Authorization: Bearer $TOKEN"
```

### 10. Deactivate Schedule

```bash
curl -X POST "http://localhost:8000/api/v1/automation-schedules/SCHEDULE_UUID/deactivate" \
  -H "Authorization: Bearer $TOKEN"
```

### 11. Manually Trigger Schedule

```bash
curl -X POST "http://localhost:8000/api/v1/automation-schedules/SCHEDULE_UUID/trigger" \
  -H "Authorization: Bearer $TOKEN"
```

### 12. Delete Schedule

```bash
curl -X DELETE "http://localhost:8000/api/v1/automation-schedules/SCHEDULE_UUID" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Bulk Operations

### 1. Bulk Activate Schedules

```bash
curl -X POST "http://localhost:8000/api/v1/automation-schedules/bulk/activate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_ids": [
      "schedule-uuid-1",
      "schedule-uuid-2",
      "schedule-uuid-3"
    ]
  }'
```

**Response:**
```json
{
  "success_count": 2,
  "failed_count": 1,
  "failed_ids": ["schedule-uuid-3"],
  "message": "Activated 2 schedule(s), 1 failed"
}
```

### 2. Bulk Deactivate Schedules

```bash
curl -X POST "http://localhost:8000/api/v1/automation-schedules/bulk/deactivate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_ids": [
      "schedule-uuid-1",
      "schedule-uuid-2"
    ]
  }'
```

### 3. Bulk Delete Schedules

```bash
curl -X POST "http://localhost:8000/api/v1/automation-schedules/bulk/delete" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_ids": [
      "schedule-uuid-1",
      "schedule-uuid-2"
    ]
  }'
```

---

## User Preferences

### 1. Get My Preferences

```bash
curl -X GET "http://localhost:8000/api/v1/user-preferences/me" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "id": "pref-uuid",
  "user_id": 123,
  "business_id": "business-uuid",
  "notification_enabled": true,
  "email_notifications_enabled": true,
  "relevance_threshold": 0.7,
  "notification_categories": ["risk", "expansion"],
  "notification_frequency": "instant",
  "assigned_clients_only": false,
  "digest_time": "09:00:00",
  "digest_day_of_week": 0,
  "created_at": "2025-10-28T...",
  "updated_at": "2025-10-28T..."
}
```

### 2. Update My Preferences

```bash
curl -X PUT "http://localhost:8000/api/v1/user-preferences/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "relevance_threshold": 0.8,
    "notification_categories": ["risk", "expansion", "news"],
    "notification_frequency": "daily",
    "digest_time": "10:00:00",
    "email_notifications_enabled": true
  }'
```

### 3. Set High Relevance Threshold (Only Critical Events)

```bash
curl -X PUT "http://localhost:8000/api/v1/user-preferences/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "relevance_threshold": 0.9,
    "notification_categories": ["risk"]
  }'
```

### 4. Configure Daily Digest

```bash
curl -X PUT "http://localhost:8000/api/v1/user-preferences/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notification_frequency": "daily",
    "digest_time": "08:00:00",
    "email_notifications_enabled": true
  }'
```

### 5. Configure Weekly Digest

```bash
curl -X PUT "http://localhost:8000/api/v1/user-preferences/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notification_frequency": "weekly",
    "digest_time": "09:00:00",
    "digest_day_of_week": 0,
    "email_notifications_enabled": true
  }'
```

---

## Email Logs

### 1. List Recent Email Logs

```bash
curl -X GET "http://localhost:8000/api/v1/email-logs/?limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

### 2. Filter by Status

```bash
curl -X GET "http://localhost:8000/api/v1/email-logs/?status=sent&limit=50" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Filter by Email Type

```bash
curl -X GET "http://localhost:8000/api/v1/email-logs/?email_type=event_notification" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Filter by Date Range

```bash
curl -X GET "http://localhost:8000/api/v1/email-logs/?start_date=2025-10-01T00:00:00Z&end_date=2025-10-28T23:59:59Z" \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Get Email Statistics

```bash
curl -X GET "http://localhost:8000/api/v1/email-logs/stats/summary" \
  -H "Authorization: Bearer $TOKEN"
```

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

### 6. Get Logs for Specific Event

```bash
curl -X GET "http://localhost:8000/api/v1/email-logs/event/EVENT_UUID" \
  -H "Authorization: Bearer $TOKEN"
```

### 7. Get My Email Logs

```bash
curl -X GET "http://localhost:8000/api/v1/email-logs/user/YOUR_USER_ID" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Scheduler Status

### 1. Get Scheduler Status

```bash
curl -X GET "http://localhost:8000/api/v1/scheduler/status" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "running": true,
  "total_jobs": 5,
  "jobs": [
    {
      "id": "schedule-uuid-1",
      "name": "Daily Morning Monitoring",
      "next_run": "2025-10-29T09:00:00Z"
    },
    {
      "id": "schedule-uuid-2",
      "name": "Hourly Check",
      "next_run": "2025-10-28T15:00:00Z"
    }
  ]
}
```

### 2. Get Recent Job Runs

```bash
curl -X GET "http://localhost:8000/api/v1/scheduler/jobs/recent?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Get Job Run Details

```bash
curl -X GET "http://localhost:8000/api/v1/scheduler/jobs/JOB_RUN_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Get Job Run Statistics

```bash
curl -X GET "http://localhost:8000/api/v1/scheduler/jobs/stats" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Testing Workflow

### Complete Test Sequence

```bash
# 1. Login
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}' \
  | jq -r '.access_token')

# 2. Set preferences for testing
curl -X PUT "http://localhost:8000/api/v1/user-preferences/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "relevance_threshold": 0.5,
    "notification_enabled": true,
    "email_notifications_enabled": true
  }'

# 3. Run test workflow
curl -X POST "http://localhost:8000/api/v1/monitoring-jobs/test" \
  -H "Authorization: Bearer $TOKEN"

# 4. Check created events
curl -X GET "http://localhost:8000/api/v1/events/?limit=10" \
  -H "Authorization: Bearer $TOKEN"

# 5. Check email logs
curl -X GET "http://localhost:8000/api/v1/email-logs/?limit=10" \
  -H "Authorization: Bearer $TOKEN"

# 6. Create test schedule
SCHEDULE_ID=$(curl -X POST "http://localhost:8000/api/v1/automation-schedules/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "YOUR_BUSINESS_UUID",
    "created_by_user_id": YOUR_USER_ID,
    "name": "Test Schedule",
    "job_type": "client_monitoring",
    "schedule_type": "daily",
    "hour_of_day": 10,
    "config": "{\"force_mock\": true}",
    "is_active": true
  }' | jq -r '.id')

# 7. Check scheduler status
curl -X GET "http://localhost:8000/api/v1/scheduler/status" \
  -H "Authorization: Bearer $TOKEN"

# 8. Manually trigger the schedule
curl -X POST "http://localhost:8000/api/v1/automation-schedules/$SCHEDULE_ID/trigger" \
  -H "Authorization: Bearer $TOKEN"

# 9. Get email stats
curl -X GET "http://localhost:8000/api/v1/email-logs/stats/summary" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Postman Collection

Import this JSON into Postman for a complete collection:

```json
{
  "info": {
    "name": "Client Monitor Automation API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "baseUrl",
      "value": "http://localhost:8000"
    },
    {
      "key": "token",
      "value": ""
    }
  ],
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": "{{baseUrl}}/api/v1/auth/login",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"user@example.com\",\n  \"password\": \"password\"\n}"
            }
          }
        }
      ]
    },
    {
      "name": "Monitoring Jobs",
      "item": [
        {
          "name": "Test Workflow",
          "request": {
            "method": "POST",
            "url": "{{baseUrl}}/api/v1/monitoring-jobs/test",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ]
          }
        }
      ]
    }
  ]
}
```

---

## Common Scenarios

### Scenario 1: Quick Testing
```bash
# Just test the system works
curl -X POST "http://localhost:8000/api/v1/monitoring-jobs/test" \
  -H "Authorization: Bearer $TOKEN"
```

### Scenario 2: Production Setup
```bash
# 1. Configure preferences
# 2. Create daily schedule
# 3. Monitor scheduler status
# 4. Check email delivery
```

### Scenario 3: Client Detail Refresh
```bash
# Refresh single client data
curl -X POST "http://localhost:8000/api/v1/monitoring-jobs/execute-for-client/CLIENT_UUID" \
  -H "Authorization: Bearer $TOKEN"
```

### Scenario 4: Bulk Schedule Management
```bash
# Deactivate all schedules for maintenance
curl -X POST "http://localhost:8000/api/v1/automation-schedules/bulk/deactivate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"schedule_ids": ["uuid1", "uuid2", "uuid3"]}'
```

---

## Tips

1. **Always test with mock APIs first** using `force_mock: true`
2. **Check scheduler status** regularly to ensure jobs are running
3. **Monitor email logs** to track notification delivery
4. **Start with low relevance thresholds** (0.5) and adjust upward
5. **Use bulk operations** for efficient schedule management
6. **Set up digests** to avoid notification overload

---

For complete API documentation, visit: `http://localhost:8000/docs`
