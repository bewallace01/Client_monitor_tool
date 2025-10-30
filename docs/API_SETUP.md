# API Setup Guide

Complete guide for setting up external APIs for Client Intelligence Monitor.

## Table of Contents

- [Overview](#overview)
- [Google Custom Search API](#google-custom-search-api)
- [NewsAPI](#newsapi)
- [Configuration](#configuration)
- [Testing APIs](#testing-apis)
- [Cost Estimates](#cost-estimates)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

Client Intelligence Monitor can collect news and events from multiple sources:

| API | Purpose | Free Tier | Paid Plans |
|-----|---------|-----------|------------|
| **Google Custom Search** | General web search | 100 queries/day | $5 per 1000 queries |
| **NewsAPI** | News articles | 100 requests/day | Starts at $449/month |
| **Mock APIs** | Testing/Demo | Unlimited | Free |

### When to Use Each Option

- **Mock APIs**: Development, testing, demos (no API keys needed)
- **Google Custom Search**: General client monitoring, web content
- **NewsAPI**: Dedicated news monitoring, press releases
- **Both APIs**: Comprehensive coverage with redundancy

---

## Google Custom Search API

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create New Project**
   - Click "Select a project" in the top navigation
   - Click "NEW PROJECT"
   - Enter project name: `Client Intelligence Monitor`
   - Click "CREATE"

3. **Wait for Project Creation**
   - Takes 10-30 seconds
   - You'll see a notification when complete

### Step 2: Enable Custom Search API

1. **Navigate to API Library**
   - In left sidebar: Click "APIs & Services" > "Library"
   - Or visit: https://console.cloud.google.com/apis/library

2. **Search for Custom Search API**
   - In search box, type: `Custom Search API`
   - Click on "Custom Search API" result

3. **Enable the API**
   - Click "ENABLE" button
   - Wait for API to be enabled (5-10 seconds)

### Step 3: Create API Key

1. **Navigate to Credentials**
   - In left sidebar: Click "APIs & Services" > "Credentials"
   - Or visit: https://console.cloud.google.com/apis/credentials

2. **Create API Key**
   - Click "+ CREATE CREDENTIALS" at top
   - Select "API key"
   - A popup shows your new API key

3. **Copy and Secure API Key**
   ```
   Example: AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```
   - Click "COPY" to copy the key
   - Store securely (never commit to version control)

4. **Restrict API Key (Recommended)**
   - Click "RESTRICT KEY" in the popup
   - Under "API restrictions":
     - Select "Restrict key"
     - Check "Custom Search API"
   - Click "SAVE"

### Step 4: Create Custom Search Engine

1. **Go to Programmable Search Engine**
   - Visit: https://programmablesearchengine.google.com/
   - Sign in with same Google account

2. **Create New Search Engine**
   - Click "Get started" or "Add"
   - Fill in the form:

   **Search engine name**: `Client Intelligence Monitor`

   **What to search**: Select "Search the entire web"

   **Search settings**:
   - Image search: ON
   - SafeSearch: ON (recommended)

3. **Create Search Engine**
   - Click "CREATE"
   - You'll see "Success!" message

4. **Get Search Engine ID**
   - Click "Customize" button
   - In "Basics" tab, find "Search engine ID"
   ```
   Example: 0123456789abcdefg:hijklmnop
   ```
   - Click "Copy to clipboard"

### Step 5: Configure in Application

Add to your `.env` file:

```bash
# Google Custom Search API
GOOGLE_API_KEY=AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GOOGLE_SEARCH_ENGINE_ID=0123456789abcdefg:hijklmnop
```

### Visual Reference (Screenshots)

#### Google Cloud Console - Create Project
```
┌─────────────────────────────────────────────────────────┐
│ Google Cloud                                    [Sign In]│
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Select a project ▼              [NEW PROJECT]           │
│                                                           │
│  Project name: _______________________________           │
│                                                           │
│  [CANCEL]                               [CREATE]         │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

#### Enable Custom Search API
```
┌─────────────────────────────────────────────────────────┐
│ Custom Search API                                        │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Google Custom Search API                                │
│  Programmatic access to Google Search                    │
│                                                           │
│                       [ENABLE]                            │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

#### Create API Key
```
┌─────────────────────────────────────────────────────────┐
│ API key created                                          │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Your API key:                                           │
│  AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX   [COPY]        │
│                                                           │
│  [RESTRICT KEY]                             [CLOSE]      │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

#### Programmable Search Engine - Setup
```
┌─────────────────────────────────────────────────────────┐
│ Create a new search engine                               │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Search engine name:                                     │
│  [Client Intelligence Monitor                       ]    │
│                                                           │
│  What to search:                                         │
│  ( ) Specific sites or pages                            │
│  (•) Search the entire web                              │
│                                                           │
│                                       [CREATE]           │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## NewsAPI

### Step 1: Create Account

1. **Go to NewsAPI Website**
   - Visit: https://newsapi.org/
   - Click "Get API Key" or "Sign Up"

2. **Choose Plan**
   - **Developer Plan**: Free, 100 requests/day
   - **Business Plans**: Paid, more requests + features

3. **Fill Registration Form**
   - First Name: Your first name
   - Email: Your email address
   - Password: Choose strong password
   - Country: Your country

4. **Verify Email**
   - Check your email inbox
   - Click verification link
   - May take 1-5 minutes to arrive

### Step 2: Get API Key

1. **Login to Dashboard**
   - Visit: https://newsapi.org/account
   - Enter email and password

2. **Find API Key**
   - On dashboard page, you'll see:
   ```
   API Key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   - Click "Copy" to copy the key

3. **Note Your Plan Limits**
   - Developer: 100 requests/day
   - Business: Varies by plan
   - Check dashboard for current usage

### Step 3: Configure in Application

Add to your `.env` file:

```bash
# NewsAPI
NEWSAPI_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Visual Reference

#### NewsAPI - Registration
```
┌─────────────────────────────────────────────────────────┐
│ NewsAPI                                          [Login] │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Get your API key                                        │
│                                                           │
│  First Name:  [________________]                         │
│  Email:       [________________]                         │
│  Password:    [________________]                         │
│  Country:     [Select...       ▼]                        │
│                                                           │
│  [ ] I accept terms and conditions                       │
│                                                           │
│                              [GET API KEY]               │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

#### NewsAPI - Dashboard
```
┌─────────────────────────────────────────────────────────┐
│ NewsAPI Dashboard                               [Logout] │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Your API Key:                                           │
│  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx            [Copy]      │
│                                                           │
│  Plan: Developer                                         │
│  Requests today: 12 / 100                                │
│  Requests this month: 347 / 3000                         │
│                                                           │
│  [UPGRADE PLAN]                                          │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables (.env)

Create or edit `.env` file in project root:

```bash
# ==============================================
# API Configuration
# ==============================================

# Enable/disable mock APIs
USE_MOCK_APIS=false

# Google Custom Search API
GOOGLE_API_KEY=AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GOOGLE_SEARCH_ENGINE_ID=0123456789abcdefg:hijklmnop

# NewsAPI
NEWSAPI_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Rate limiting
MAX_API_CALLS_PER_HOUR=100
```

### Settings UI Configuration

1. **Launch Application**
   ```bash
   streamlit run app.py
   ```

2. **Navigate to Settings**
   - Click "⚙️ Settings" in sidebar

3. **Go to API Configuration Tab**
   - Click "API Configuration" tab

4. **Configure Each API**

   **Google Custom Search:**
   - Toggle "Enable Google Search API" to ON
   - Enter "API Key"
   - Enter "Search Engine ID"
   - Click "Test Connection" to verify

   **NewsAPI:**
   - Toggle "Enable NewsAPI" to ON
   - Enter "API Key"
   - Click "Test Connection" to verify

5. **Save Settings**
   - Click "💾 Save Settings" at bottom

### Verification

After configuration, verify APIs are working:

1. **Go to System Testing Page**
   - Settings > System Testing

2. **Check API Status**
   - Should show "✅ Connected" for each enabled API
   - Shows quota/usage information

3. **Test with Real Scan**
   - Add a test client (e.g., "Microsoft")
   - Run "🔍 Scan for Events"
   - Should collect events from configured APIs

---

## Testing APIs

### Test Google Custom Search API

#### Using cURL

```bash
# Replace YOUR_API_KEY and YOUR_SEARCH_ENGINE_ID
curl "https://www.googleapis.com/customsearch/v1?key=YOUR_API_KEY&cx=YOUR_SEARCH_ENGINE_ID&q=test"
```

**Expected Response:**
```json
{
  "kind": "customsearch#search",
  "items": [
    {
      "title": "Test Result",
      "link": "https://example.com",
      "snippet": "Test snippet..."
    }
  ]
}
```

**Error Response:**
```json
{
  "error": {
    "code": 400,
    "message": "API key not valid. Please pass a valid API key.",
    "status": "INVALID_ARGUMENT"
  }
}
```

#### Using Python

```python
import requests

API_KEY = "YOUR_API_KEY"
SEARCH_ENGINE_ID = "YOUR_SEARCH_ENGINE_ID"

url = "https://www.googleapis.com/customsearch/v1"
params = {
    "key": API_KEY,
    "cx": SEARCH_ENGINE_ID,
    "q": "test"
}

response = requests.get(url, params=params)
print(response.status_code)  # Should be 200
print(response.json())
```

### Test NewsAPI

#### Using cURL

```bash
# Replace YOUR_API_KEY
curl "https://newsapi.org/v2/everything?q=test&apiKey=YOUR_API_KEY"
```

**Expected Response:**
```json
{
  "status": "ok",
  "totalResults": 1000,
  "articles": [
    {
      "title": "Article Title",
      "description": "Article description...",
      "url": "https://example.com/article",
      "publishedAt": "2024-01-01T12:00:00Z"
    }
  ]
}
```

**Error Response:**
```json
{
  "status": "error",
  "code": "apiKeyInvalid",
  "message": "Your API key is invalid or incorrect."
}
```

#### Using Python

```python
import requests

API_KEY = "YOUR_API_KEY"

url = "https://newsapi.org/v2/everything"
params = {
    "q": "test",
    "apiKey": API_KEY
}

response = requests.get(url, params=params)
print(response.status_code)  # Should be 200
print(response.json())
```

### Test in Application

1. **Navigate to Settings > System Testing**

2. **Click "🧪 Run System Tests"**

3. **Review Results:**
   - ✅ API connections
   - ✅ Rate limiting
   - ✅ Error handling
   - ✅ Response parsing

---

## Cost Estimates

### Google Custom Search API

**Pricing:**
- First 100 queries per day: **FREE**
- Additional queries: **$5 per 1,000 queries** ($0.005 per query)

**Usage Scenarios:**

| Clients | Scans/Day | Queries/Day | Cost/Month |
|---------|-----------|-------------|------------|
| 10 | 1 | 10 | $0 (free tier) |
| 50 | 1 | 50 | $0 (free tier) |
| 100 | 1 | 100 | $0 (free tier) |
| 200 | 1 | 200 | ~$15 |
| 500 | 1 | 500 | ~$60 |

**Free Tier Tips:**
- Use for 100 or fewer clients
- Scan once per day
- Enables up to 100 queries/day free

**Optimizing Costs:**
- Set `SCAN_LOOKBACK_DAYS=7` (scan weekly instead of daily)
- Use `MIN_RELEVANCE_SCORE=0.7` (filter low-relevance events)
- Enable caching to avoid duplicate queries
- Prioritize high-value clients

### NewsAPI

**Pricing:**

| Plan | Requests/Day | Requests/Month | Cost/Month |
|------|--------------|----------------|------------|
| Developer | 100 | ~3,000 | **$0** |
| Business | Varies | Up to 250,000 | $449+ |
| Enterprise | Unlimited | Unlimited | Custom |

**Developer Plan (Free):**
- 100 requests per day
- 30-day article history
- No commercial use
- Perfect for testing and small-scale use

**Business Plan ($449/month):**
- 250,000 requests/month
- Full article content
- Commercial use allowed
- Live/breaking news

**Usage Scenarios:**

| Clients | Scans/Day | Events/Scan | Requests/Day | Recommended Plan |
|---------|-----------|-------------|--------------|------------------|
| 10 | 1 | 5 | 50 | Developer (Free) |
| 20 | 1 | 5 | 100 | Developer (Free) |
| 50 | 1 | 5 | 250 | Business ($449) |
| 100 | 1 | 5 | 500 | Business ($449) |

**Free Tier Tips:**
- Perfect for up to 20 clients with daily scans
- Use for personal/non-commercial projects
- Combine with Google Search for more coverage

### Combined Usage

**Example: 50 Clients, Daily Monitoring**

**Option 1: Google Only**
- 50 queries/day (within free tier)
- Cost: $0/month
- Coverage: General web content

**Option 2: NewsAPI Only (Free)**
- 50 requests/day (within free tier)
- Cost: $0/month
- Coverage: News articles only

**Option 3: Both APIs (Free)**
- 25 Google queries/day
- 25 NewsAPI requests/day
- Cost: $0/month
- Coverage: Best of both

**Option 4: Both APIs (Paid)**
- 50 Google queries/day
- 50 NewsAPI requests/day
- Cost: $0 + $0 = $0/month (within free tiers)
- Coverage: Comprehensive

### Cost Reduction Strategies

1. **Use Free Tiers Strategically**
   - Stay under 100 queries/day for Google
   - Stay under 100 requests/day for NewsAPI
   - Total: 200 API calls/day free

2. **Intelligent Scanning**
   ```bash
   # Scan high-priority clients daily
   # Scan medium-priority clients every 3 days
   # Scan low-priority clients weekly
   ```

3. **Caching**
   - Enable search result caching
   - Set `CACHE_TTL=86400` (24 hours)
   - Reduces duplicate queries

4. **Event Filtering**
   ```bash
   # Only store high-relevance events
   MIN_RELEVANCE_SCORE=0.6

   # Limit results per scan
   EVENTS_PER_SCAN=10
   ```

5. **Batch Processing**
   - Scan all clients once per day instead of multiple times
   - Use off-peak hours

---

## Best Practices

### API Key Security

**DO:**
- ✅ Store API keys in `.env` file
- ✅ Add `.env` to `.gitignore`
- ✅ Use environment variables
- ✅ Restrict API keys in cloud console
- ✅ Rotate keys periodically (every 90 days)
- ✅ Use separate keys for dev/staging/production

**DON'T:**
- ❌ Commit API keys to version control
- ❌ Share API keys in emails or chat
- ❌ Use production keys in development
- ❌ Leave unrestricted keys active
- ❌ Store keys in code comments

### Rate Limiting

```bash
# Configure in .env
MAX_API_CALLS_PER_HOUR=100

# Application will:
# - Track API calls per hour
# - Queue requests when limit reached
# - Resume after rate limit window passes
```

### Error Handling

The application handles common API errors:

- **API Key Invalid**: Falls back to mock APIs
- **Quota Exceeded**: Shows warning, waits until quota resets
- **Network Errors**: Retries with exponential backoff
- **API Unavailable**: Uses cached data if available

### Monitoring Usage

1. **Check Google Cloud Console**
   - https://console.cloud.google.com/apis/dashboard
   - View quota usage
   - Set up billing alerts

2. **Check NewsAPI Dashboard**
   - https://newsapi.org/account
   - View daily/monthly usage
   - Upgrade plan if needed

3. **Check Application Metrics**
   - Settings > System Testing
   - View API call statistics
   - Monitor rate limit status

### Quota Management

**Set Up Alerts:**

```bash
# Google Cloud Console > Billing > Budgets & alerts
# Create budget alert at 80% of expected usage
```

**Monitor in Application:**
- Settings > System Testing shows API usage
- Warnings when approaching limits
- Automatic fallback to mock data

---

## Troubleshooting

### Google Custom Search Issues

#### Issue: "API key not valid"

**Possible Causes:**
1. API key copied incorrectly (with spaces or line breaks)
2. Custom Search API not enabled
3. API key restrictions too strict

**Solutions:**
```bash
# 1. Verify API key in .env has no spaces
GOOGLE_API_KEY=AIzaSyD...  # No spaces, no quotes

# 2. Check API is enabled:
# Visit: https://console.cloud.google.com/apis/library
# Search for "Custom Search API"
# Should show "API enabled"

# 3. Check API key restrictions:
# Visit: https://console.cloud.google.com/apis/credentials
# Click on your API key
# Under "API restrictions", ensure "Custom Search API" is checked
```

#### Issue: "Search engine not found"

**Possible Causes:**
1. Search Engine ID copied incorrectly
2. Search engine not created
3. Wrong Google account

**Solutions:**
```bash
# 1. Verify Search Engine ID format
GOOGLE_SEARCH_ENGINE_ID=0123456789abcdefg:hijklmnop
# Should contain letters, numbers, and a colon

# 2. Check search engine exists:
# Visit: https://programmablesearchengine.google.com/
# Should see your search engine listed

# 3. Ensure using same Google account for:
# - Cloud Console (API key)
# - Programmable Search Engine (Search Engine ID)
```

#### Issue: "Quota exceeded"

**Solutions:**
```bash
# Check quota usage:
# Visit: https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas

# Options:
# 1. Wait until quota resets (resets daily at midnight PT)
# 2. Reduce scan frequency
# 3. Enable billing to increase quota
```

### NewsAPI Issues

#### Issue: "API key invalid"

**Possible Causes:**
1. API key copied incorrectly
2. Email not verified
3. Account suspended

**Solutions:**
```bash
# 1. Re-copy API key from dashboard
# Visit: https://newsapi.org/account

# 2. Check email for verification link
# Resend verification if needed

# 3. Check account status in dashboard
# Contact NewsAPI support if suspended
```

#### Issue: "Too many requests"

**Possible Causes:**
1. Exceeded daily limit (100 for free tier)
2. Exceeded hourly rate limit

**Solutions:**
```bash
# Check usage:
# Visit: https://newsapi.org/account

# Options:
# 1. Wait until daily quota resets (midnight UTC)
# 2. Reduce number of clients or scan frequency
# 3. Upgrade to paid plan
```

#### Issue: "Developer plan only"

**Error Message**: "This feature requires a paid plan"

**Explanation:**
- Free Developer plan has limitations
- Some endpoints require paid plan

**Solutions:**
1. Use supported endpoints only
2. Upgrade to Business plan if needed

### General API Issues

#### Issue: Network/Connection Errors

**Solutions:**
```bash
# 1. Check internet connection
ping google.com

# 2. Check firewall settings
# Ensure outbound HTTPS allowed

# 3. Test API manually
curl "https://www.googleapis.com/customsearch/v1?key=YOUR_KEY&cx=YOUR_CX&q=test"

# 4. Try using different network
# Corporate firewalls may block API calls
```

#### Issue: Application Not Using Real APIs

**Symptoms:**
- System Testing shows "Mock API" status
- Events seem generic/fake

**Solutions:**
```bash
# 1. Check .env configuration
cat .env | grep USE_MOCK_APIS
# Should be: USE_MOCK_APIS=false

# 2. Verify API keys are set
cat .env | grep API_KEY
# Should show your actual keys

# 3. Restart application
# Stop and start Streamlit to reload .env

# 4. Check Settings UI
# Settings > API Configuration
# Toggle APIs to "Enabled"
```

---

## Additional Resources

### Documentation

- **Google Custom Search API**: https://developers.google.com/custom-search/v1/overview
- **NewsAPI Documentation**: https://newsapi.org/docs
- **Streamlit Secrets**: https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management

### Support

- **Google Cloud Support**: https://cloud.google.com/support
- **NewsAPI Support**: support@newsapi.org
- **Application Issues**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Pricing Pages

- **Google Custom Search Pricing**: https://developers.google.com/custom-search/v1/overview#pricing
- **NewsAPI Pricing**: https://newsapi.org/pricing

---

## Quick Reference

### Google Custom Search Setup Checklist

- [ ] Create Google Cloud project
- [ ] Enable Custom Search API
- [ ] Create API key
- [ ] Restrict API key to Custom Search API
- [ ] Create Programmable Search Engine
- [ ] Copy Search Engine ID
- [ ] Add to `.env` file
- [ ] Test connection

### NewsAPI Setup Checklist

- [ ] Register at newsapi.org
- [ ] Verify email address
- [ ] Copy API key from dashboard
- [ ] Add to `.env` file
- [ ] Test connection
- [ ] Note usage limits

### Environment Variables Template

```bash
# Copy this to .env and fill in your values

# API Configuration
USE_MOCK_APIS=false
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id-here
NEWSAPI_KEY=your-newsapi-key-here
MAX_API_CALLS_PER_HOUR=100
```

---

**Last Updated**: 2025-10-15
**Version**: 1.0.0
