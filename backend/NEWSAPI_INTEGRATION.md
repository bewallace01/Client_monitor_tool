# NewsAPI Integration Guide

## Overview

NewsAPI has been fully integrated into the Client Monitoring Automation System. This integration allows you to search for news articles about your clients from thousands of news sources worldwide.

## Features

### NewsAPI Service (`newsapi_service.py`)

**Capabilities:**
- Search for news articles about specific clients
- Filter by language (English, Spanish, French, etc.)
- Sort by relevancy, popularity, or publish date
- Date range filtering (up to 30 days for free tier)
- Get top headlines by country and category
- Relevance scoring for articles

**Key Methods:**

1. **`search_client()`** - Search for articles about a client
   - Builds optimized query with client name and domain
   - Filters by date range (last 30 days)
   - Returns normalized results

2. **`get_top_headlines()`** - Get breaking news
   - Filter by country (US, GB, CA, etc.)
   - Filter by category (business, technology, etc.)
   - Search within headlines

3. **`extract_results_for_storage()`** - Normalize API response
   - Standardizes article format
   - Extracts title, description, content, URL
   - Includes source, author, publish date

4. **`calculate_relevance_score()`** - Score article relevance
   - Checks title, description, content for client mentions
   - Recency bonus for articles within 7 days
   - Returns score 0.0-1.0

## Configuration

### 1. Get NewsAPI Key

Sign up at: https://newsapi.org/

**Free Tier Limits:**
- 100 requests per day
- Last 30 days of articles
- Up to 100 articles per request

**Paid Plans:** Unlimited requests, full archive access

### 2. Add API Configuration

Via API:
```bash
curl -X POST "http://localhost:8000/api/v1/api-configs/api-configs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "newsapi",
    "api_key": "YOUR_NEWSAPI_KEY",
    "is_active": true
  }'
```

Via Environment Variable:
```bash
NEWS_API_KEY=your_newsapi_key_here
```

## Usage

### Automatic Integration

NewsAPI is automatically included in monitoring jobs when configured:

```bash
# Run monitoring job (NewsAPI will be used if configured)
curl -X POST "http://localhost:8000/api/v1/monitoring-jobs/execute" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_ids": null,
    "force_mock": false
  }'
```

### How It Works

1. **Query Building:**
   - Client name: `"Acme Corp"`
   - Client domain: `acme.com`
   - Combined query: `"Acme Corp" AND acme.com`

2. **Search Execution:**
   - Searches last 30 days (free tier limit)
   - Returns up to 10 articles per client
   - Sorts by relevancy

3. **Result Processing:**
   - Extracts article details
   - Calculates relevance scores
   - Deduplicates with Google Search results
   - Stores in `event_raw_data` table

4. **AI Classification:**
   - Articles processed through AI
   - Categorized (news, risk, expansion, etc.)
   - Relevance and sentiment scored
   - Events created for high-relevance articles

## Search Strategy

### Query Optimization

NewsAPI uses AND logic for better results:

**Example for "Acme Corp" with domain "acme.com":**
```
"Acme Corp" AND acme.com
```

This ensures articles mention both the company name AND their domain.

### Additional Keywords

You can add keywords via client configuration:
```json
{
  "keywords": ["product launch", "acquisition", "partnership"]
}
```

Resulting query:
```
"Acme Corp" AND acme.com AND (product launch OR acquisition OR partnership)
```

## Multi-Source Benefits

### Combined with Google Search

When both Google Search and NewsAPI are configured:

1. **Google Search provides:**
   - General web content
   - Company websites
   - Press releases
   - Blog posts

2. **NewsAPI provides:**
   - News articles
   - Mainstream media coverage
   - Breaking news
   - Industry publications

3. **Together they provide:**
   - Comprehensive coverage
   - Diverse perspectives
   - Better event detection
   - Higher confidence scores

### Deduplication

The system automatically deduplicates results:
- Same URL = duplicate
- Similar titles = duplicate
- Same content hash = duplicate

This ensures you don't get the same article from multiple sources.

## Response Format

### Raw NewsAPI Response

```json
{
  "status": "ok",
  "totalResults": 15,
  "articles": [
    {
      "source": {
        "id": "techcrunch",
        "name": "TechCrunch"
      },
      "author": "John Doe",
      "title": "Acme Corp Announces New Product",
      "description": "Acme Corp unveiled their latest innovation...",
      "url": "https://techcrunch.com/article",
      "urlToImage": "https://image.url",
      "publishedAt": "2025-10-28T10:00:00Z",
      "content": "Full article content here..."
    }
  ]
}
```

### Normalized for Storage

```json
{
  "title": "Acme Corp Announces New Product",
  "description": "Acme Corp unveiled their latest innovation...",
  "content": "Full article content here...",
  "url": "https://techcrunch.com/article",
  "source": "TechCrunch",
  "author": "John Doe",
  "published_at": "2025-10-28T10:00:00Z",
  "url_to_image": "https://image.url",
  "api_source": "newsapi"
}
```

## API Limits & Best Practices

### Free Tier Limitations

- **100 requests/day**
  - ~10 clients monitored per day (10 requests per client)
  - Or monitor more clients less frequently

- **30 days history**
  - Can't search articles older than 30 days
  - SearchAggregatorService automatically limits to 30 days

- **100 results per request**
  - System defaults to 10 results per client
  - Can increase up to 100 if needed

### Optimization Tips

1. **Schedule wisely:**
   ```json
   {
     "schedule_type": "daily",
     "hour_of_day": 9
   }
   ```
   One daily run = 1 request per client

2. **Batch clients:**
   - Monitor 10 clients = 10 requests
   - Stay within 100/day limit

3. **Use with Google:**
   - Google for general content
   - NewsAPI for news articles
   - Better coverage without duplicate requests

## Monitoring & Troubleshooting

### Check NewsAPI Usage

```bash
# View recent job runs
curl -X GET "http://localhost:8000/api/v1/scheduler/jobs/recent?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Look for:
- `sources_used`: Should include "newsapi"
- `events_found`: Articles processed
- `errors`: Any NewsAPI errors

### Common Errors

**1. Rate Limit Exceeded (429)**
```
"error": "NewsAPI error: 429"
```
Solution: Reduce monitoring frequency or upgrade to paid plan

**2. Invalid API Key (401)**
```
"error": "NewsAPI error: 401"
```
Solution: Check API key in configuration

**3. No Results**
```
"totalResults": 0
```
Possible reasons:
- Client name too generic
- No recent news coverage
- Query too restrictive

### Fallback Behavior

If NewsAPI fails:
1. Error logged in job run
2. System continues with other sources (Google)
3. If all sources fail, uses mock data
4. No workflow interruption

## Testing

### Test NewsAPI Integration

```bash
# 1. Add NewsAPI configuration
curl -X POST "http://localhost:8000/api/v1/api-configs/api-configs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "newsapi",
    "api_key": "YOUR_KEY",
    "is_active": true
  }'

# 2. Run test job
curl -X POST "http://localhost:8000/api/v1/monitoring-jobs/execute" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_ids": ["your-client-uuid"],
    "force_mock": false
  }'

# 3. Check results
curl -X GET "http://localhost:8000/api/v1/events/?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Expected Behavior

**With valid NewsAPI key:**
- Articles returned from NewsAPI
- Events created from news content
- `source_api`: "newsapi" in raw data

**Without NewsAPI key:**
- Falls back to Google Search (if configured)
- Or falls back to mock data
- No errors, graceful degradation

## Comparison with Other Sources

| Feature | Google Search | NewsAPI | Mock |
|---------|--------------|---------|------|
| **Content Type** | General web | News articles | Test data |
| **Free Tier** | 100/day | 100/day | Unlimited |
| **History** | Any | 30 days | Any |
| **Quality** | High | Very High | Medium |
| **Coverage** | Broad | News focus | Limited |
| **Best For** | General monitoring | Breaking news | Testing |

## Advanced Features

### Language Support

Search in multiple languages:
```python
# English (default)
language="en"

# Spanish
language="es"

# French
language="fr"

# German
language="de"
```

### Sort Options

```python
# By relevancy (default)
sort_by="relevancy"

# By popularity (most shared)
sort_by="popularity"

# By publish date (newest first)
sort_by="publishedAt"
```

### Country-Specific Headlines

```python
# US headlines
country="us"

# UK headlines
country="gb"

# Canada headlines
country="ca"
```

## Next Steps

1. **Get API Key:** Sign up at https://newsapi.org/
2. **Add Configuration:** Via API or environment variable
3. **Test:** Run a monitoring job
4. **Schedule:** Create daily schedule for automatic monitoring
5. **Monitor:** Check job runs and events

## Support

- **NewsAPI Docs:** https://newsapi.org/docs
- **API Status:** https://newsapi.org/status
- **Support:** Contact NewsAPI support team

## Integration Status

✅ **Complete**
- NewsAPI service implemented
- SearchAggregator integration complete
- Automatic fallback configured
- Deduplication working
- Multi-language support
- API configuration ready

**Ready for production use with NewsAPI key!**
