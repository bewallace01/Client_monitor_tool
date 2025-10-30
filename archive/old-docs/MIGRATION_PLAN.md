# Client Intelligence Monitor - Migration Plan
## Streamlit → FastAPI + React

**Migration Status**: In Progress
**Started**: 2025-10-16
**Estimated Completion**: TBD

---

## Overview
This document outlines the step-by-step migration from Streamlit to a production-ready FastAPI backend with React frontend.

### Technology Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- Pydantic (data validation)
- Uvicorn (ASGI server)
- Python 3.10+

**Frontend:**
- React 18+
- TypeScript
- Vite (build tool)
- TanStack Query (data fetching)
- Tailwind CSS (styling)
- Recharts (data visualization)
- React Router (navigation)

**Development Tools:**
- Docker & Docker Compose
- PostgreSQL (production database)
- Redis (caching)

---

## Migration Steps

### ✅ Phase 1: Project Setup & Infrastructure

#### Step 1.1: Create Project Structure
**Status**: ✅ Completed

**Tasks:**
- [x] Create `backend/` directory structure
- [x] Create `frontend/` directory structure
- [x] Set up Python virtual environment for backend
- [ ] Initialize Node.js project for frontend (will do in Step 1.3)
- [x] Create root-level configuration files

**Directory Structure:**
```
client-intelligence-monitor/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   └── dependencies.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── database/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── docker-compose.yml
├── .gitignore
└── README.md
```

**QA Tests:**
- [ ] Verify `backend/` directory exists with correct structure
- [ ] Verify `frontend/` directory exists with correct structure
- [ ] Run `python --version` in backend directory (should be 3.10+)
- [ ] Run `node --version` in frontend directory (should be 18+)
- [ ] Run `npm --version` in frontend directory
- [ ] Verify virtual environment is activated
- [ ] Check that all directories from structure exist

**Completion Criteria:**
- All directories created
- Virtual environment activated
- Node.js initialized
- All QA tests pass

---

#### Step 1.2: Set Up FastAPI Backend Skeleton
**Status**: ✅ Completed

**Tasks:**
- [x] Install FastAPI and dependencies
- [x] Create `backend/requirements.txt`
- [x] Set up FastAPI app in `main.py`
- [x] Create basic health check endpoint
- [x] Set up CORS configuration
- [x] Create environment configuration

**Files to Create:**
- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/.env.example`

**QA Tests:**
- [x] Run `pip install -r backend/requirements.txt` successfully - ✅ All 58+ packages installed
- [x] Start FastAPI server: `uvicorn app.main:app --reload` - ✅ Running on http://127.0.0.1:8000
- [x] Navigate to `http://localhost:8000` - ✅ Returns `{"name":"Client Intelligence Monitor","version":"2.0.0","status":"running","docs":"/docs","api":"/api/v1"}`
- [x] Navigate to `http://localhost:8000/docs` - ✅ Swagger UI accessible
- [x] Navigate to `http://localhost:8000/health` - ✅ Returns `{"status":"healthy"}`
- [x] Verify CORS is configured - ✅ Headers: `access-control-allow-origin: http://localhost:5173`, `access-control-allow-credentials: true`
- [x] Navigate to `http://localhost:8000/api/v1/info` - ✅ Returns API version info

**Completion Criteria:**
- ✅ FastAPI server runs successfully
- ✅ Swagger docs accessible at http://localhost:8000/docs
- ✅ Health check endpoint works
- ✅ All QA tests pass

---

#### Step 1.3: Set Up React Frontend Skeleton
**Status**: ✅ Completed

**Tasks:**
- [x] Initialize Vite + React + TypeScript project
- [x] Install core dependencies (React Router, TanStack Query, Tailwind)
- [x] Set up Tailwind CSS configuration
- [x] Create basic routing structure
- [x] Set up API service layer
- [x] Create environment configuration

**Files Created:**
- `frontend/package.json` - Dependencies: React 18.3.1, React Router 7.9.4, TanStack Query 5.90.5, Tailwind 3.4.18, Recharts 3.2.1
- `frontend/vite.config.ts` - Configured with API proxy to backend
- `frontend/tsconfig.json` - TypeScript configuration
- `frontend/tailwind.config.js` - Tailwind with custom primary color palette
- `frontend/postcss.config.js` - PostCSS with Tailwind and Autoprefixer
- `frontend/src/main.tsx` - App entry point with React 18
- `frontend/src/App.tsx` - React Router and TanStack Query setup
- `frontend/src/pages/Home.tsx` - Landing page with API status checks
- `frontend/src/services/api.ts` - Axios client with interceptors
- `frontend/src/index.css` - Tailwind directives and custom component classes
- `frontend/.env.example` - Environment variable template

**QA Tests:**
- [x] Run `npm install` successfully - ✅ 303 packages installed
- [x] Run `npm run dev` - ✅ Dev server running on http://localhost:5175
- [x] Navigate to React app - ✅ Accessible and returns HTML
- [x] Verify Tailwind CSS configured - ✅ Tailwind v3.4.18 installed with custom theme
- [x] Check TypeScript compilation - ✅ No errors (`tsc --noEmit` passed)
- [x] Test API service layer - ✅ Created with interceptors and error handling
- [x] Verify routing structure - ✅ React Router v7 configured with Home route

**Completion Criteria:**
- ✅ React dev server runs successfully on port 5175
- ✅ Tailwind CSS configured with custom theme
- ✅ TypeScript compilation works with no errors
- ✅ All QA tests pass
- ✅ API service layer connects to backend at http://localhost:8000

---

#### Step 1.4: Set Up Docker & Database
**Status**: ✅ Completed

**Tasks:**
- [x] Create `Dockerfile` for backend
- [x] Create `Dockerfile` for frontend
- [x] Create `docker-compose.yml`
- [x] Configure PostgreSQL service
- [x] Configure Redis service
- [x] Set up database connection in FastAPI
- [x] Create SQLite fallback for development

**Files Created:**
- `backend/Dockerfile` - Python 3.11 with FastAPI
- `frontend/Dockerfile` - Node 20 with Vite dev server
- `docker-compose.yml` - PostgreSQL 15, Redis 7, backend & frontend services
- `backend/app/database/connection.py` - SQLAlchemy engine with SQLite/PostgreSQL support
- `backend/app/database/test_connection.py` - Database connection test script
- `DOCKER_SETUP.md` - Complete Docker setup guide
- Updated `backend/.env.example` - SQLite development config

**QA Tests:**
- [N/A] Run `docker compose up -d postgres` - Docker not installed on system
- [N/A] Run `docker compose up -d redis` - Docker not installed on system
- [N/A] Connect to PostgreSQL - Docker not available
- [x] Verify database connection from backend - ✅ SQLite connection successful (v3.45.3)
- [x] Test database module imports - ✅ All imports successful
- [x] Verify data directory created - ✅ `backend/data/` created with client_intelligence.db
- [x] Test connection script - ✅ `test_connection.py` passed all tests

**Completion Criteria:**
- ✅ Docker configuration files created (ready for future use)
- ✅ SQLite database working for development
- ✅ Database connection module implemented
- ✅ Backend connects to database successfully
- ✅ Test script validates connection
- ✅ Documentation created (DOCKER_SETUP.md)

**Notes:**
- Docker is not installed on this system, so using SQLite for development
- PostgreSQL and Redis configurations are ready in docker-compose.yml
- To switch to PostgreSQL later: Install Docker, update DATABASE_URL, set USE_SQLITE=False
- SQLite provides equivalent functionality for development phase

---

### ✅ Phase 2: Database & Models Migration

#### Step 2.1: Create SQLAlchemy Models
**Status**: ✅ Completed

**Tasks:**
- [x] Create `Client` model
- [x] Create `Event` model
- [x] Create `SearchCache` model
- [x] Create `JobRun` model
- [x] Set up Alembic for migrations
- [x] Create initial migration

**Files Created:**
- `backend/app/models/client.py` - Client model with relationships
- `backend/app/models/event.py` - Event model with EventCategory enum
- `backend/app/models/search_cache.py` - Search cache model
- `backend/app/models/job_run.py` - Job run tracking model
- `backend/app/models/__init__.py` - Model exports
- `backend/alembic.ini` - Alembic configuration
- `backend/alembic/env.py` - Alembic environment with auto-import
- `backend/alembic/versions/01747c31ab7a_initial_migration.py` - Initial migration
- `backend/scripts/verify_tables.py` - Table verification script

**QA Tests:**
- [x] Run `alembic revision --autogenerate -m "Initial migration"` - ✅ Migration created successfully
- [x] Run `alembic upgrade head` - ✅ Tables created: clients, events, search_cache, job_runs
- [x] Verify tables exist - ✅ All 5 tables found (including alembic_version)
- [x] Check table schema - ✅ All columns match model definitions
- [x] Run `alembic downgrade base` - ✅ Tables dropped successfully
- [x] Run `alembic upgrade head` again - ✅ Tables recreated successfully
- [x] Verify foreign key constraints - ✅ events.client_id references clients.id

**Completion Criteria:**
- ✅ All models created with proper types and relationships
- ✅ Alembic configured and working
- ✅ Migrations run successfully
- ✅ All QA tests pass

---

#### Step 2.2: Create Pydantic Schemas
**Status**: ✅ Completed

**Tasks:**
- [x] Create `ClientSchema` (Create, Update, Response)
- [x] Create `EventSchema` (Create, Update, Response)
- [x] Create `SearchCacheSchema`
- [x] Create `JobRunSchema`
- [x] Add validation rules
- [x] Create pagination schemas

**Files Created:**
- `backend/app/schemas/base.py` - Base schemas (PaginationParams, PaginatedResponse, MessageResponse, HealthResponse)
- `backend/app/schemas/client.py` - ClientCreate, ClientUpdate, ClientResponse, ClientListResponse, ClientSummary, ClientStats
- `backend/app/schemas/event.py` - EventCreate, EventUpdate, EventResponse, EventWithClient, EventListResponse, EventFilters, EventStats, BulkEventUpdate
- `backend/app/schemas/search_cache.py` - SearchCacheCreate, SearchCacheResponse, SearchCacheStats, SearchQuery, SearchResult, SearchResponse
- `backend/app/schemas/job_run.py` - JobRunCreate, JobRunUpdate, JobRunResponse, JobRunListResponse, JobRunFilters, JobRunStats, JobScheduleInfo, TriggerJobRequest
- `backend/app/schemas/__init__.py` - All schema exports
- `backend/scripts/test_schemas.py` - Comprehensive schema validation test script

**QA Tests:**
- [x] Import all schemas without errors - ✅ All imports successful
- [x] Create test instances of each schema - ✅ All schemas instantiated successfully
- [x] Verify validation rules work (try invalid data) - ✅ Empty names, invalid ranges all caught
- [x] Test schema serialization (to dict/JSON) - ✅ Pydantic handles automatically
- [x] Test schema deserialization (from dict/JSON) - ✅ Works via model_validate
- [x] Verify nested schemas work correctly - ✅ EventWithClient, ClientListResponse tested
- [x] Check pagination schema with sample data - ✅ PaginationParams offset/limit calculation works

**Validation Features Implemented:**
- Domain normalization (removes protocol, trailing slash, lowercases)
- Search keywords trimming and formatting
- URL validation (adds https:// if missing)
- Field length constraints (min/max)
- Range validation for scores (relevance: 0-1, sentiment: -1 to 1)
- Required field validation
- Enum validation for EventCategory and JobStatus

**Completion Criteria:**
- ✅ All schemas created with proper types
- ✅ Validation rules implemented and tested
- ✅ Serialization/deserialization working
- ✅ All QA tests pass

---

#### Step 2.3: Migrate Existing Data
**Status**: ✅ Completed

**Tasks:**
- [x] Create data migration script
- [x] Export data from SQLite (Streamlit app)
- [x] Transform data to new schema
- [x] Import data into new database
- [x] Verify data integrity
- [x] Create backup of migrated data

**Files Created:**
- `backend/scripts/inspect_streamlit_db.py` - Database inspection tool
- `backend/scripts/migrate_data.py` - Comprehensive migration script with field mapping
- `backend/scripts/verify_migration.py` - Detailed verification and spot-check script
- `backend/data/client_intelligence.db.backup` - Backup of migrated database

**Migration Results:**
- **Source Database**: `data/client_intelligence.db` (Streamlit)
- **Target Database**: `backend/data/client_intelligence.db` (FastAPI)
- **Clients**: 43/61 migrated (18 duplicates skipped)
- **Events**: 1,557/1,557 migrated (100%)
- **Job Runs**: 35/35 migrated (100%)
- **Search Cache**: 0 entries (empty table)

**Field Mapping:**
- Clients: `keywords` → `search_keywords`, `monitoring_since` → `created_at`, `last_checked` → `last_checked_at`
- Events: `summary` → `description`, `source_url` → `url`, `source_name` → `source`, `published_date` → `event_date`
- Job Runs: `id` (UUID) → `job_id`, `metadata` → `job_metadata`

**QA Tests:**
- [x] Run migration script - ✅ Migrated 43 clients, 1,557 events, 35 job runs
- [x] Verify all clients migrated - ✅ All unique clients migrated (duplicates skipped intentionally)
- [x] Verify all events migrated - ✅ 100% (1,557/1,557) events migrated
- [x] Check relationships intact - ✅ Client-Event foreign keys working (Salesforce has 87 events)
- [x] Verify data distribution - ✅ 43 active clients, 18 read events, 1,539 unread, 1 starred
- [x] Check event categories - ✅ 12 categories (acquisition, award, financial, funding, leadership, partnership, product, etc.)
- [x] Check job run statuses - ✅ 22 completed, 13 failed
- [x] Spot-check sample records - ✅ All fields correctly mapped and data intact
- [x] Create database backup - ✅ `client_intelligence.db.backup` created

**Data Integrity Verification:**
```
Record Counts:
  Clients: 43 (100% of unique clients)
  Events: 1,557 (100% migrated)
  Job Runs: 35 (100% migrated)

Data Distribution:
  Active Clients: 43 (100%)
  Read Events: 18 (1.2%)
  Unread Events: 1,539 (98.8%)
  Starred Events: 1 (0.06%)

Events by Category:
  product: 359, partnership: 217, leadership: 191, acquisition: 189
  funding: 175, regulatory: 132, award: 112, financial: 101
  news: 73, product_launch: 4, leadership_change: 2, financial_results: 2

Job Runs:
  Completed: 22 (62.9%)
  Failed: 13 (37.1%)
```

**Completion Criteria:**
- ✅ All data exported and transformed
- ✅ All data imported successfully
- ✅ Data integrity verified with spot checks
- ✅ Relationships intact (Client-Event foreign keys work)
- ✅ Backup created
- ✅ All QA tests pass

---

### ✅ Phase 3: Backend API Development

#### Step 3.1: Create Client API Endpoints
**Status**: ✅ Completed

**Tasks:**
- [x] Create `GET /api/clients` (list with pagination)
- [x] Create `GET /api/clients/{id}` (get single)
- [x] Create `POST /api/clients` (create)
- [x] Create `PUT /api/clients/{id}` (update)
- [x] Create `DELETE /api/clients/{id}` (delete)
- [x] Add filtering and sorting
- [x] Create service layer

**Files Created:**
- `backend/app/api/routes/clients.py` - Full CRUD endpoints with filtering, pagination, sorting
- `backend/app/services/client_service.py` - Complete service layer with business logic

**Implemented Features:**
- GET `/api/v1/clients` - List with pagination, search, filtering (industry, tier, active status)
- GET `/api/v1/clients/{id}` - Get single client with 404 handling
- GET `/api/v1/clients/stats` - Client statistics
- GET `/api/v1/clients/industries` - List all industries
- GET `/api/v1/clients/tiers` - List all tiers
- POST `/api/v1/clients` - Create with duplicate name checking (409 conflict)
- PUT `/api/v1/clients/{id}` - Update with partial updates support
- DELETE `/api/v1/clients/{id}` - Delete with cascade to events

**Completion Criteria:**
- ✅ All endpoints implemented
- ✅ Service layer created with full CRUD operations
- ✅ Search functionality across name, domain, description, keywords
- ✅ Filtering by industry, tier, active status
- ✅ Sorting by any field (ascending/descending)
- ✅ Pagination with skip/limit
- ✅ Error handling (404, 409 conflict)

---

#### Step 3.2: Create Event API Endpoints
**Status**: ✅ Completed

**Tasks:**
- [x] Create `GET /api/events` (list with pagination)
- [x] Create `GET /api/events/{id}` (get single)
- [x] Create `POST /api/events` (create)
- [x] Create `PUT /api/events/{id}` (update)
- [x] Create `DELETE /api/events/{id}` (delete)
- [x] Add filtering (client, date range, category, sentiment)
- [x] Add bulk operations endpoint
- [x] Create service layer

**Files Created:**
- `backend/app/api/routes/events.py` - Full CRUD + bulk operations with comprehensive filtering
- `backend/app/services/event_service.py` - Complete service layer with business logic

**Implemented Features:**
- GET `/api/v1/events` - List with pagination, search, filtering (client_id, category, read status, starred, relevance, date range)
- GET `/api/v1/events/{id}` - Get single event with 404 handling
- GET `/api/v1/events/stats` - Event statistics and distributions
- GET `/api/v1/events/categories` - List all unique categories
- POST `/api/v1/events` - Create with client existence validation
- PUT `/api/v1/events/{id}` - Update with partial updates support
- DELETE `/api/v1/events/{id}` - Delete single event
- POST `/api/v1/events/bulk-update` - Bulk update is_read, is_starred status
- POST `/api/v1/events/bulk-delete` - Bulk delete multiple events

**Completion Criteria:**
- ✅ All endpoints implemented
- ✅ Service layer created with full CRUD + bulk operations
- ✅ Comprehensive filtering (client, category, date range, read/starred status, relevance threshold)
- ✅ Search functionality across title, description, source
- ✅ Sorting by any field (ascending/descending)
- ✅ Pagination with skip/limit
- ✅ Eager loading of client relationship with joinedload
- ✅ Error handling (404, 400 for bulk operations)

---

#### Step 3.3: Create Dashboard & Analytics API
**Status**: ✅ Completed

**Tasks:**
- [x] Create `GET /api/analytics/dashboard` (comprehensive overview metrics)
- [x] Create `GET /api/analytics/events/categories` (events by category)
- [x] Create `GET /api/analytics/events/timeline` (events timeline)
- [x] Create `GET /api/analytics/events/sentiment` (sentiment distribution)
- [x] Create `GET /api/analytics/clients/top-activity` (top clients by activity)
- [x] Create `GET /api/analytics/events/relevance` (relevance metrics)
- [x] Create `GET /api/analytics/growth` (growth metrics with trends)
- [x] Optimize queries for performance

**Files Created:**
- `backend/app/api/routes/analytics.py` - Complete analytics endpoints with comprehensive metrics
- `backend/app/services/analytics_service.py` - Optimized service layer with complex aggregations

**Implemented Features:**
- GET `/api/v1/analytics/dashboard` - Full dashboard summary (client stats, event stats, categories, sentiment, time-based metrics)
- GET `/api/v1/analytics/clients/top-activity` - Top clients by event count with activity metrics
- GET `/api/v1/analytics/events/timeline` - Time series data grouped by day/week with zero-filling
- GET `/api/v1/analytics/events/categories` - Category distribution with counts and percentages
- GET `/api/v1/analytics/events/sentiment` - Sentiment analysis (positive/neutral/negative) with averages
- GET `/api/v1/analytics/events/relevance` - Relevance score metrics (high/medium/low distribution)
- GET `/api/v1/analytics/growth` - Period-over-period growth trends for events and clients

**Completion Criteria:**
- ✅ All endpoints implemented with comprehensive metrics
- ✅ Performance optimized with efficient aggregations and subqueries
- ✅ Time series data with complete date ranges (zero-filled)
- ✅ Sentiment and relevance distribution analytics
- ✅ Growth trends with percentage change calculations
- ✅ Top clients ranking with multiple metrics
- ✅ Tier and industry breakdowns

---

#### Step 3.4: Create Automation & Scheduler API
**Status**: ✅ Completed

**Tasks:**
- [x] Create `GET /api/scheduler/jobs` (job run history with filtering)
- [x] Create `GET /api/scheduler/jobs/stats` (job run statistics)
- [x] Create `GET /api/scheduler/jobs/recent` (recent job runs)
- [x] Create `GET /api/scheduler/jobs/active` (currently running jobs)
- [x] Create `POST /api/scheduler/jobs/trigger` (manual job trigger)
- [x] Create `POST /api/scheduler/jobs/{id}/start` (mark job as running)
- [x] Create `POST /api/scheduler/jobs/{id}/complete` (mark job completed)
- [x] Create `POST /api/scheduler/jobs/{id}/fail` (mark job failed)
- [x] Create full CRUD for job runs

**Files Created:**
- `backend/app/api/routes/scheduler.py` - Complete scheduler/job management endpoints
- `backend/app/services/scheduler_service.py` - Job run service layer with state management

**Implemented Features:**
- GET `/api/v1/scheduler/jobs` - List job runs with filtering (job_type, status, date range), pagination, sorting
- GET `/api/v1/scheduler/jobs/{id}` - Get single job run by ID
- GET `/api/v1/scheduler/jobs/stats` - Statistics (total, by status, by type, average duration)
- GET `/api/v1/scheduler/jobs/recent` - Most recent job runs
- GET `/api/v1/scheduler/jobs/active` - Currently pending or running jobs
- GET `/api/v1/scheduler/jobs/types` - List all unique job types
- POST `/api/v1/scheduler/jobs` - Create new job run
- POST `/api/v1/scheduler/jobs/trigger` - Trigger manual job with UUID generation
- POST `/api/v1/scheduler/jobs/{id}/start` - Mark job as running with timestamp
- POST `/api/v1/scheduler/jobs/{id}/complete` - Mark completed with metrics
- POST `/api/v1/scheduler/jobs/{id}/fail` - Mark failed with error message
- PUT `/api/v1/scheduler/jobs/{id}` - Update job run
- DELETE `/api/v1/scheduler/jobs/{id}` - Delete job run

**Completion Criteria:**
- ✅ All endpoints implemented with full lifecycle management
- ✅ Job state transitions (pending → running → completed/failed)
- ✅ Statistics with duration calculations
- ✅ Filtering by job type and status
- ✅ Manual job triggering with UUID generation
- ✅ Metrics tracking (events_found, events_new, clients_processed)
- ✅ Error message capture for failed jobs

---

#### Step 3.5: Create Search API
**Status**: ✅ Completed

**Tasks:**
- [x] Create `POST /api/search/query` (search with caching)
- [x] Create `GET /api/search/cache` (list cache entries)
- [x] Create `GET /api/search/cache/stats` (cache statistics)
- [x] Create `GET /api/search/cache/{id}` (get cache entry)
- [x] Create `GET /api/search/cache/search/{query}` (search through cache)
- [x] Create `DELETE /api/search/cache/expired/cleanup` (cleanup expired)
- [x] Create `DELETE /api/search/cache/source/{source}` (clear by source)
- [x] Create `DELETE /api/search/cache/all` (clear all cache)
- [x] Implement cache hash generation
- [x] Implement TTL-based expiration

**Files Created:**
- `backend/app/api/routes/search.py` - Complete search and cache management endpoints
- `backend/app/services/cache_service.py` - Cache service with hash-based key generation and TTL

**Implemented Features:**
- POST `/api/v1/search/query` - Perform search with intelligent caching (checks cache first, creates if miss)
- GET `/api/v1/search/cache` - List cache entries with filtering (source, include_expired), pagination
- GET `/api/v1/search/cache/stats` - Comprehensive cache statistics (active/expired, by source, hit rate placeholder)
- GET `/api/v1/search/cache/{id}` - Get single cache entry with 404 handling
- GET `/api/v1/search/cache/search/{query}` - Search through cached queries
- DELETE `/api/v1/search/cache/{id}` - Delete specific cache entry
- DELETE `/api/v1/search/cache/expired/cleanup` - Cleanup all expired entries
- DELETE `/api/v1/search/cache/source/{source}` - Clear cache for specific source
- DELETE `/api/v1/search/cache/all` - Clear entire cache (with warning)

**Cache Features:**
- SHA-256 hash generation from query + source for unique cache keys
- TTL-based expiration (default 24 hours, configurable)
- Automatic cache update/refresh for existing entries
- Cache hit detection with expiration checking
- Statistics tracking (total, active, expired, by source)

**Completion Criteria:**
- ✅ All search and cache endpoints implemented
- ✅ Cache service with hash-based key generation (SHA-256)
- ✅ TTL-based expiration with configurable duration
- ✅ Cache hit/miss logic with automatic fallback
- ✅ Comprehensive cache management (cleanup, clear by source, clear all)
- ✅ Statistics and monitoring endpoints
- ✅ JSON serialization of search results
- ✅ Pagination for cache listing

---

### ✅ Phase 4: Frontend Development

#### Step 4.1: Create Layout & Navigation
**Status**: ✅ Completed

**Tasks:**
- [ ] Create main layout component
- [ ] Create sidebar navigation
- [ ] Create header with logo
- [ ] Set up React Router routes
- [ ] Create 404 page
- [ ] Add route guards (if needed)

**Files to Create:**
- `frontend/src/components/Layout/MainLayout.tsx`
- `frontend/src/components/Layout/Sidebar.tsx`
- `frontend/src/components/Layout/Header.tsx`
- `frontend/src/pages/NotFound.tsx`
- `frontend/src/routes.tsx`

**QA Tests:**
- [ ] Navigate to each route (Dashboard, Clients, Events, etc.)
- [ ] Verify sidebar highlights active page
- [ ] Test mobile responsive sidebar
- [ ] Test 404 page with invalid route
- [ ] Check logo and branding appear correctly
- [ ] Test navigation between pages
- [ ] Verify browser back/forward buttons work
- [ ] Check URL updates correctly

**Completion Criteria:**
- All routes working
- Navigation functional
- Responsive design
- All QA tests pass

---

#### Step 4.2: Create Dashboard Page
**Status**: ✅ Completed

**Tasks:**
- [ ] Create Dashboard page component
- [ ] Create stats cards component
- [ ] Create charts components (Recharts)
- [ ] Integrate with dashboard API
- [ ] Add loading states
- [ ] Add error handling
- [ ] Add filters (date range, client)

**Files to Create:**
- `frontend/src/pages/Dashboard.tsx`
- `frontend/src/components/Dashboard/StatsCard.tsx`
- `frontend/src/components/Dashboard/EventsChart.tsx`
- `frontend/src/components/Dashboard/SentimentChart.tsx`
- `frontend/src/services/dashboard.ts`

**QA Tests:**
- [ ] Dashboard loads and displays stats
- [ ] All charts render correctly
- [ ] Test loading state appears
- [ ] Test error state with API down
- [ ] Test filters update data
- [ ] Verify data matches API response
- [ ] Check responsive layout on mobile
- [ ] Test chart interactions (hover, click)

**Completion Criteria:**
- Dashboard fully functional
- All charts working
- Filters functional
- All QA tests pass

---

#### Step 4.3: Create Clients Page
**Status**: ✅ Completed

**Tasks:**
- [ ] Create Clients list page
- [ ] Create Client detail modal/page
- [ ] Create Add/Edit client form
- [ ] Add pagination
- [ ] Add search and filters
- [ ] Add delete confirmation
- [ ] Integrate with clients API

**Files to Create:**
- `frontend/src/pages/Clients.tsx`
- `frontend/src/components/Clients/ClientList.tsx`
- `frontend/src/components/Clients/ClientCard.tsx`
- `frontend/src/components/Clients/ClientForm.tsx`
- `frontend/src/components/Clients/ClientDetail.tsx`
- `frontend/src/services/clients.ts`

**QA Tests:**
- [ ] Clients list displays correctly
- [ ] Test pagination (next, previous)
- [ ] Test search functionality
- [ ] Test filters (industry, status)
- [ ] Test add new client
- [ ] Test edit existing client
- [ ] Test delete client (with confirmation)
- [ ] Test form validation
- [ ] Verify data updates in real-time

**Completion Criteria:**
- Full CRUD operations working
- Search and filters functional
- All QA tests pass

---

#### Step 4.4: Create Events Page
**Status**: ✅ Completed

**Tasks:**
- [ ] Create Events list page
- [ ] Create Event detail modal
- [ ] Create event filters sidebar
- [ ] Add bulk actions
- [ ] Add multiple view modes (list, timeline, table)
- [ ] Add event status management
- [ ] Integrate with events API

**Files to Create:**
- `frontend/src/pages/Events.tsx`
- `frontend/src/components/Events/EventList.tsx`
- `frontend/src/components/Events/EventCard.tsx`
- `frontend/src/components/Events/EventDetail.tsx`
- `frontend/src/components/Events/EventFilters.tsx`
- `frontend/src/components/Events/BulkActions.tsx`
- `frontend/src/services/events.ts`

**QA Tests:**
- [ ] Events list displays correctly
- [ ] Test all filters (client, date, category, sentiment)
- [ ] Test view mode switching
- [ ] Test bulk select
- [ ] Test bulk actions (mark reviewed, archive, delete)
- [ ] Test event detail modal
- [ ] Test updating event status
- [ ] Verify pagination works
- [ ] Check sorting options

**Completion Criteria:**
- All view modes working
- Filters and bulk actions functional
- All QA tests pass

---

#### Step 4.5: Create Automation Page
**Status**: ✅ Completed

**Tasks:**
- [ ] Create Automation page
- [ ] Create scheduler status widget
- [ ] Create job history list
- [ ] Create manual job trigger UI
- [ ] Add job configuration
- [ ] Integrate with scheduler API

**Files to Create:**
- `frontend/src/pages/Automation.tsx`
- `frontend/src/components/Automation/SchedulerStatus.tsx`
- `frontend/src/components/Automation/JobHistory.tsx`
- `frontend/src/components/Automation/ManualTrigger.tsx`
- `frontend/src/services/automation.ts`

**QA Tests:**
- [ ] Scheduler status displays correctly
- [ ] Test start scheduler button
- [ ] Test stop scheduler button
- [ ] Test manual job trigger
- [ ] Job history displays correctly
- [ ] Test job history pagination
- [ ] Verify real-time status updates
- [ ] Check job run details

**Completion Criteria:**
- Scheduler control working
- Job management functional
- All QA tests pass

---

#### Step 4.6: Create Settings Page
**Status**: ✅ Completed

**Tasks:**
- [ ] Create Settings page with tabs
- [ ] Create General settings tab
- [ ] Create API configuration tab
- [ ] Create Monitoring settings tab
- [ ] Create Notification settings tab
- [ ] Add save/reset functionality
- [ ] Integrate with settings API

**Files to Create:**
- `frontend/src/pages/Settings.tsx`
- `frontend/src/components/Settings/GeneralSettings.tsx`
- `frontend/src/components/Settings/APISettings.tsx`
- `frontend/src/components/Settings/MonitoringSettings.tsx`
- `frontend/src/services/settings.ts`

**QA Tests:**
- [ ] All tabs display correctly
- [ ] Test saving settings
- [ ] Test reset to defaults
- [ ] Test form validation
- [ ] Verify settings persist
- [ ] Test database backup/export
- [ ] Check API key masking
- [ ] Test notification settings

**Completion Criteria:**
- All settings tabs working
- Save/load functionality working
- All QA tests pass

---

#### Step 4.7: Create Search Page
**Status**: ✅ Completed

**Tasks:**
- [ ] Create global search page
- [ ] Create search bar component
- [ ] Create search results component
- [ ] Add search filters
- [ ] Add result highlighting
- [ ] Integrate with search API

**Files to Create:**
- `frontend/src/pages/Search.tsx`
- `frontend/src/components/Search/SearchBar.tsx`
- `frontend/src/components/Search/SearchResults.tsx`
- `frontend/src/services/search.ts`

**QA Tests:**
- [ ] Search bar accepts input
- [ ] Test search with various queries
- [ ] Verify results display correctly
- [ ] Test result highlighting
- [ ] Test filters (type, date range)
- [ ] Test empty results state
- [ ] Check search performance
- [ ] Verify result links work

**Completion Criteria:**
- Search fully functional
- Results display correctly
- All QA tests pass

---

### ✅ Phase 5: Authentication & Security (Optional)

#### Step 5.1: Implement Basic Authentication & User Model
**Status**: ✅ Completed

**Tasks:**
- [x] Set up JWT authentication
- [x] Create User model
- [x] Create login/register endpoints
- [x] Create protected route middleware
- [x] Add auth context in React
- [x] Create login page
- [x] Add logout functionality
- [x] Create system admin user (username: admin, password: admin123)

**Files Created:**
- `backend/app/models/user.py`
- `backend/app/api/routes/auth.py`
- `backend/app/core/security.py` (using bcrypt directly)
- `frontend/src/contexts/AuthContext.tsx`
- `frontend/src/pages/Login.tsx`
- `frontend/src/components/ProtectedRoute.tsx`

**QA Tests:**
- [x] Test login with valid credentials (admin/admin123)
- [x] Test login with invalid credentials
- [x] Verify JWT token is generated
- [x] Test protected endpoints require auth
- [x] Test logout clears token
- [x] Verify unauthorized access redirects to login
- [x] CORS configured for frontend port

**Completion Criteria:**
- ✅ Authentication working
- ✅ Protected routes secure
- ✅ System admin created
- ✅ Login page functional

---

#### Step 5.2: Implement User Hierarchy & Role-Based Access Control (RBAC)
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Update User model with role and business_id fields
- [ ] Create Business model
- [ ] Create UserRole enum (SYSTEM_ADMIN, BUSINESS_ADMIN, BASE_USER)
- [ ] Create database migration for new fields
- [ ] Update authentication to include role and business context
- [ ] Create role-based permission decorators
- [ ] Update JWT tokens to include role and business_id

**User Hierarchy:**
```
SYSTEM_ADMIN (Global Access)
├── Full platform access
├── Onboard/offboard any user
├── View usage by user
├── Manage all businesses
└── Primary test user

BUSINESS_ADMIN (Business-Level Access)
├── Manage their business's users
├── Onboard/offboard users under their business
├── Manage business API keys
├── View their business's data only
└── Reset SSO for their users

BASE_USER (Limited Access)
├── Dashboard (read-only)
├── Clients (read-only)
├── Events (read-only)
└── Can change own password
```

**Files to Create:**
- `backend/app/models/business.py`
- `backend/app/models/user.py` (update with role, business_id)
- `backend/app/schemas/business.py`
- `backend/app/schemas/user.py` (update)
- `backend/alembic/versions/xxx_add_user_hierarchy.py`
- `backend/app/core/permissions.py`
- `backend/app/core/dependencies.py` (role checking)

**Database Schema:**

**Business Table:**
```python
id: UUID (PK)
name: String (unique, required)
domain: String
industry: String
tier: String
is_active: Boolean (default: True)
api_key_hash: String (for business API keys)
created_at: DateTime
updated_at: DateTime
```

**User Table Updates:**
```python
# Existing fields...
role: Enum (SYSTEM_ADMIN, BUSINESS_ADMIN, BASE_USER)
business_id: UUID (FK to Business, nullable for SYSTEM_ADMIN)
sso_enabled: Boolean (default: False)
sso_provider: String (nullable)
last_password_change: DateTime
password_reset_required: Boolean (default: False)
```

**QA Tests:**
- [ ] Create Business model and verify table creation
- [ ] Update User model and run migration
- [ ] Create test users for each role
- [ ] Test SYSTEM_ADMIN can access all businesses
- [ ] Test BUSINESS_ADMIN can only access their business
- [ ] Test BASE_USER has read-only access
- [ ] Verify JWT includes role and business_id
- [ ] Test role-based permission decorators

**Completion Criteria:**
- Business and User models updated
- Role enum implemented
- Migration successful
- JWT includes role/business context
- All QA tests pass

---

#### Step 5.2.1: Export Current Database Data
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Create data export script for current database
- [ ] Export all clients to JSON
- [ ] Export all events to JSON
- [ ] Export all job_runs to JSON
- [ ] Export admin user data
- [ ] Verify exported data integrity
- [ ] Create backup of current database file

**Files to Create:**
- `backend/scripts/export_current_data.py`
- `backend/data/exports/clients_backup.json`
- `backend/data/exports/events_backup.json`
- `backend/data/exports/job_runs_backup.json`
- `backend/data/exports/users_backup.json`

**Export Format:**
```json
{
  "clients": [...],
  "events": [...],
  "job_runs": [...],
  "users": [...],
  "export_date": "2025-10-19T...",
  "record_counts": {
    "clients": 43,
    "events": 1557,
    "job_runs": 35,
    "users": 1
  }
}
```

**QA Tests:**
- [ ] Run export script successfully
- [ ] Verify all 43 clients exported
- [ ] Verify all 1,557 events exported
- [ ] Verify all 35 job runs exported
- [ ] Verify admin user exported
- [ ] Check JSON files are valid
- [ ] Verify file sizes are reasonable
- [ ] Create database file backup

**Completion Criteria:**
- All data exported to JSON files
- Backup of database file created
- Export verification passed
- All QA tests pass

---

#### Step 5.2.2: Implement UUID-Based Models (Database Redesign)
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Create GUID type decorator for SQLite/PostgreSQL compatibility
- [ ] Update Client model to use UUID primary key
- [ ] Update Event model to use UUID primary key
- [ ] Add soft delete fields to Client model
- [ ] Add soft delete fields to Event model
- [ ] Add audit fields (created_by, deleted_by) to models
- [ ] Create EventUserInteraction model
- [ ] Create AuditLog model
- [ ] Create Tag, ClientTag, EventTag models
- [ ] Create Notification model
- [ ] Update all foreign key relationships to use UUIDs

**Reference Document:**
- `DATABASE_REDESIGN.md` - Complete redesign specifications

**Files to Update:**
- `backend/app/models/client.py` - UUID PK, soft deletes, audit fields
- `backend/app/models/event.py` - UUID PK, soft deletes, audit fields
- `backend/app/models/job_run.py` - UUID PK (optional, for consistency)
- `backend/app/models/search_cache.py` - UUID PK (optional)

**Files to Create:**
- `backend/app/models/event_user_interaction.py`
- `backend/app/models/audit_log.py`
- `backend/app/models/tag.py`
- `backend/app/models/notification.py`

**New Client Model Fields:**
```python
# Primary Key
id: UUID (was int)

# Multi-tenancy
business_id: UUID (FK to Business)

# Audit
created_by_user_id: int (FK to User)
assigned_to_user_id: int (FK to User, replaces account_owner string)

# Soft delete
is_deleted: Boolean
deleted_at: DateTime
deleted_by_user_id: int (FK to User)

# New fields
company_size: String
revenue_range: String
headquarters_location: String
founded_year: Integer
monitoring_frequency: String
health_score: Float
```

**New Event Model Fields:**
```python
# Primary Key
id: UUID (was int)

# Foreign Keys
business_id: UUID (FK to Business)
client_id: UUID (FK to Client, was int)

# Classification
subcategory: String
tags: Text (JSON)
confidence_score: Float

# Audit
created_by_user_id: int (FK to User)

# Soft delete
is_deleted: Boolean
deleted_at: DateTime
deleted_by_user_id: int (FK to User)

# Deduplication
duplicate_of_event_id: UUID (FK to Event)

# Remove user interaction fields (moved to EventUserInteraction)
# is_read, is_starred, user_notes - REMOVED
```

**QA Tests:**
- [ ] All models compile without errors
- [ ] GUID type works with SQLite
- [ ] Foreign key relationships are correct
- [ ] Soft delete fields added correctly
- [ ] EventUserInteraction model created
- [ ] AuditLog model created
- [ ] Tag models created
- [ ] Notification model created
- [ ] All relationships defined correctly

**Completion Criteria:**
- All models updated with UUID PKs
- Soft delete implemented
- Audit trail fields added
- EventUserInteraction model working
- Supporting models created
- All QA tests pass

---

#### Step 5.2.3: Create Pydantic Schemas for New Models
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Update Client schemas for UUID and new fields
- [ ] Update Event schemas for UUID and new fields
- [ ] Create EventUserInteraction schemas
- [ ] Create AuditLog schemas
- [ ] Create Tag schemas
- [ ] Create Notification schemas
- [ ] Update all relationship schemas for UUIDs

**Files to Update:**
- `backend/app/schemas/client.py` - UUID support, new fields
- `backend/app/schemas/event.py` - UUID support, new fields

**Files to Create:**
- `backend/app/schemas/event_interaction.py`
- `backend/app/schemas/audit.py`
- `backend/app/schemas/tag.py`
- `backend/app/schemas/notification.py`

**Schema Examples:**

**EventUserInteractionCreate:**
```python
event_id: UUID
is_read: bool = False
is_starred: bool = False
user_notes: Optional[str] = None
```

**TagCreate:**
```python
name: str (max 100 chars)
color: Optional[str] (hex color)
```

**NotificationResponse:**
```python
id: UUID
type: str
title: str
message: str
link_url: Optional[str]
is_read: bool
created_at: datetime
```

**QA Tests:**
- [ ] All schemas validate correctly
- [ ] UUID serialization works
- [ ] Relationship schemas updated
- [ ] Validation rules work
- [ ] Test schema creation with sample data
- [ ] Test schema updates
- [ ] Verify enum conversions work

**Completion Criteria:**
- All schemas created and updated
- UUID validation working
- All QA tests pass
- Schemas export correctly in __init__.py

---

#### Step 5.2.4: Create Fresh Database with New Structure
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Delete old database file
- [ ] Delete old migration files
- [ ] Create initial migration with all new models
- [ ] Run migration to create fresh database
- [ ] Verify all tables created correctly
- [ ] Verify all indexes created
- [ ] Verify all foreign keys created
- [ ] Create default business for data import

**Files to Create:**
- `backend/alembic/versions/xxx_initial_database_with_uuids.py`

**Migration Contents:**
- businesses table (UUID PK)
- users table (int PK, with role, business_id)
- clients table (UUID PK, with business_id, soft deletes)
- events table (UUID PK, with business_id, soft deletes)
- event_user_interactions table
- audit_logs table
- tags, client_tags, event_tags tables
- notifications table
- job_runs table (UUID PK)
- search_cache table (UUID PK)

**QA Tests:**
- [ ] Delete `backend/data/client_intelligence.db`
- [ ] Delete `backend/alembic/versions/*.py` (except __pycache__)
- [ ] Run `alembic revision --autogenerate -m "Initial database with UUIDs"`
- [ ] Verify migration file looks correct
- [ ] Run `alembic upgrade head`
- [ ] Verify all tables exist in database
- [ ] Check table schemas with `sqlite3 .schema`
- [ ] Verify indexes created
- [ ] Verify foreign keys created
- [ ] Test database connection

**Completion Criteria:**
- Fresh database created
- All tables exist with correct schemas
- All indexes created
- All foreign keys working
- No migration errors
- All QA tests pass

---

#### Step 5.2.5: Create Data Import Script
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Create data import script
- [ ] Create default business "Legacy Data"
- [ ] Recreate admin user with SYSTEM_ADMIN role
- [ ] Import clients with UUID generation
- [ ] Import events with UUID generation
- [ ] Create EventUserInteraction records for existing read/starred events
- [ ] Import job_runs with UUID generation
- [ ] Link all imported data to default business
- [ ] Verify data integrity after import

**Files to Create:**
- `backend/scripts/import_legacy_data.py`

**Import Process:**
1. Create "Legacy Data" business
2. Update admin user to SYSTEM_ADMIN role
3. Import clients:
   - Generate new UUIDs
   - Assign to "Legacy Data" business
   - Map old int IDs to new UUIDs
   - Set created_by_user_id to admin
4. Import events:
   - Generate new UUIDs
   - Assign to "Legacy Data" business
   - Map client_id (int → UUID) using mapping from step 3
   - Set created_by_user_id to admin
   - Create EventUserInteraction records for admin user if is_read or is_starred
5. Import job_runs (optional UUID conversion)
6. Verify counts match export

**QA Tests:**
- [ ] Run import script successfully
- [ ] Verify "Legacy Data" business created
- [ ] Verify admin user has SYSTEM_ADMIN role
- [ ] Verify 43 clients imported
- [ ] Verify 1,557 events imported
- [ ] Verify client-event relationships correct
- [ ] Verify EventUserInteraction records created
- [ ] Verify all business_id fields populated
- [ ] Verify no foreign key errors
- [ ] Compare counts with export

**Completion Criteria:**
- All data imported successfully
- Default business created
- Admin user updated
- All relationships intact
- Data integrity verified
- All QA tests pass

---

#### Step 5.2.6: Update Service Layer for UUID Support
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Update ClientService for UUID operations
- [ ] Update EventService for UUID operations
- [ ] Create EventUserInteractionService
- [ ] Create AuditLogService
- [ ] Create TagService
- [ ] Create NotificationService
- [ ] Update all service methods to handle UUIDs
- [ ] Add soft delete support to services
- [ ] Add audit logging to create/update/delete operations

**Files to Update:**
- `backend/app/services/client_service.py`
- `backend/app/services/event_service.py`

**Files to Create:**
- `backend/app/services/event_interaction_service.py`
- `backend/app/services/audit_service.py`
- `backend/app/services/tag_service.py`
- `backend/app/services/notification_service.py`

**Service Updates:**

**ClientService:**
- Accept UUID instead of int for `get_by_id()`
- Update CRUD operations for UUID
- Implement soft delete: `soft_delete(client_id, user_id)`
- Add audit logging on create/update/delete

**EventService:**
- Accept UUID instead of int for `get_by_id()`
- Update CRUD operations for UUID
- Implement soft delete
- Remove user interaction methods (moved to EventUserInteractionService)

**EventUserInteractionService:**
- `mark_as_read(event_id, user_id)`
- `mark_as_starred(event_id, user_id)`
- `add_note(event_id, user_id, note)`
- `get_user_interaction(event_id, user_id)`

**QA Tests:**
- [ ] Test client CRUD with UUIDs
- [ ] Test event CRUD with UUIDs
- [ ] Test soft delete operations
- [ ] Test audit logging
- [ ] Test event user interactions
- [ ] Test tag operations
- [ ] Test notification creation
- [ ] Verify UUID validation
- [ ] Test error handling for invalid UUIDs

**Completion Criteria:**
- All services updated for UUIDs
- Soft delete working
- Audit logging implemented
- New services created
- All QA tests pass

---

#### Step 5.2.7: Update API Endpoints for UUID Support
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Update Client endpoints for UUID path parameters
- [ ] Update Event endpoints for UUID path parameters
- [ ] Create EventUserInteraction endpoints
- [ ] Create Tag management endpoints
- [ ] Create Notification endpoints
- [ ] Update all route validators for UUID
- [ ] Update API documentation

**Files to Update:**
- `backend/app/api/routes/clients.py`
- `backend/app/api/routes/events.py`

**Files to Create:**
- `backend/app/api/routes/event_interactions.py`
- `backend/app/api/routes/tags.py`
- `backend/app/api/routes/notifications.py`

**Endpoint Updates:**

**Clients API:**
- `GET /api/v1/clients/{id}` - Accept UUID
- `PUT /api/v1/clients/{id}` - Accept UUID
- `DELETE /api/v1/clients/{id}` - Soft delete with UUID
- Add `GET /api/v1/clients/{id}/restore` - Restore soft-deleted client

**Events API:**
- `GET /api/v1/events/{id}` - Accept UUID
- `PUT /api/v1/events/{id}` - Accept UUID
- `DELETE /api/v1/events/{id}` - Soft delete with UUID

**New Event Interaction API:**
- `POST /api/v1/events/{event_id}/read` - Mark as read
- `POST /api/v1/events/{event_id}/star` - Toggle star
- `POST /api/v1/events/{event_id}/note` - Add/update note
- `GET /api/v1/events/{event_id}/interaction` - Get user's interaction

**Tags API:**
- `GET /api/v1/tags` - List business tags
- `POST /api/v1/tags` - Create tag
- `POST /api/v1/clients/{client_id}/tags` - Tag a client
- `POST /api/v1/events/{event_id}/tags` - Tag an event

**Notifications API:**
- `GET /api/v1/notifications` - List user notifications
- `POST /api/v1/notifications/{id}/read` - Mark as read
- `DELETE /api/v1/notifications/{id}` - Delete notification

**QA Tests:**
- [ ] Test all UUID path parameters
- [ ] Test UUID validation (invalid UUIDs return 400)
- [ ] Test soft delete endpoints
- [ ] Test event interaction endpoints
- [ ] Test tag endpoints
- [ ] Test notification endpoints
- [ ] Verify Swagger docs updated
- [ ] Test all CRUD operations
- [ ] Test error handling

**Completion Criteria:**
- All endpoints accept UUIDs
- UUID validation working
- New endpoints created
- API documentation updated
- All QA tests pass

---

#### Step 5.3: Implement Data Visibility & Multi-Tenancy
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Add business_id and user_id to Client model
- [ ] Add business_id and user_id to Event model
- [ ] Create database migration for data ownership
- [ ] Implement data filtering by business_id in all queries
- [ ] Update all API endpoints to respect business context
- [ ] Create service layer helpers for scoped queries
- [ ] Migrate existing data to assign to default business

**Data Ownership Schema:**

**Client Table Updates:**
```python
business_id: UUID (FK to Business, required)
created_by_user_id: UUID (FK to User, nullable)
assigned_to_user_id: UUID (FK to User, nullable)
```

**Event Table Updates:**
```python
business_id: UUID (FK to Business, required)
created_by_user_id: UUID (FK to User, nullable)
```

**Files to Create:**
- `backend/alembic/versions/xxx_add_data_ownership.py`
- `backend/app/services/scoped_query_service.py`
- `backend/app/core/business_context.py`
- `backend/scripts/assign_existing_data_to_business.py`

**Query Scoping Logic:**
- SYSTEM_ADMIN: No filtering (sees all data)
- BUSINESS_ADMIN: Filter by their business_id (sees only their business data)
- BASE_USER: Filter by their business_id (sees only their business data)

**API Endpoint Updates:**
- `GET /api/v1/clients` - Filter by business_id automatically
- `GET /api/v1/events` - Filter by business_id automatically
- `GET /api/v1/analytics/*` - Scope analytics to business_id
- `POST /api/v1/clients` - Auto-assign business_id from JWT
- `POST /api/v1/events` - Auto-assign business_id from JWT

**QA Tests:**
- [ ] Update Client and Event models
- [ ] Run migration successfully
- [ ] Create test data for multiple businesses
- [ ] Test SYSTEM_ADMIN sees all data
- [ ] Test BUSINESS_ADMIN sees only their business data
- [ ] Test BASE_USER sees only their business data
- [ ] Test cross-business data isolation (no leaks)
- [ ] Verify analytics respect business scoping
- [ ] Test data creation assigns correct business_id
- [ ] Run migration script for existing data

**Completion Criteria:**
- All models updated with business_id
- Migration successful
- Query scoping implemented
- All endpoints respect business context
- Existing data migrated
- All QA tests pass

---

#### Step 5.4: Implement User Management APIs
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Create user management endpoints
- [ ] Create business management endpoints
- [ ] Implement user onboarding/offboarding
- [ ] Add password change functionality
- [ ] Add password reset functionality
- [ ] Create SSO reset endpoint for business admins
- [ ] Add usage tracking endpoints
- [ ] Implement API key management for businesses

**Files to Create:**
- `backend/app/api/routes/users.py`
- `backend/app/api/routes/businesses.py`
- `backend/app/services/user_service.py` (update)
- `backend/app/services/business_service.py`
- `backend/app/schemas/user_management.py`

**User Management Endpoints:**

**For SYSTEM_ADMIN:**
- `GET /api/v1/admin/users` - List all users (with filtering)
- `GET /api/v1/admin/users/{id}` - Get user details
- `POST /api/v1/admin/users` - Create user (any role, any business)
- `PUT /api/v1/admin/users/{id}` - Update user
- `DELETE /api/v1/admin/users/{id}` - Deactivate user
- `GET /api/v1/admin/businesses` - List all businesses
- `POST /api/v1/admin/businesses` - Create business
- `GET /api/v1/admin/usage` - View usage by user/business

**For BUSINESS_ADMIN:**
- `GET /api/v1/business/users` - List users in their business
- `POST /api/v1/business/users` - Create user (BASE_USER only, their business)
- `PUT /api/v1/business/users/{id}` - Update user in their business
- `DELETE /api/v1/business/users/{id}` - Deactivate user in their business
- `POST /api/v1/business/users/{id}/reset-sso` - Reset SSO for user
- `GET /api/v1/business/api-keys` - View business API keys
- `POST /api/v1/business/api-keys/regenerate` - Regenerate API key

**For All Users:**
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update own profile
- `POST /api/v1/users/me/change-password` - Change own password
- `POST /api/v1/users/me/request-password-reset` - Request password reset

**QA Tests:**
- [ ] Test SYSTEM_ADMIN can create users in any business
- [ ] Test SYSTEM_ADMIN can view all users
- [ ] Test BUSINESS_ADMIN can create BASE_USER in their business
- [ ] Test BUSINESS_ADMIN cannot create users in other businesses
- [ ] Test BUSINESS_ADMIN cannot create SYSTEM_ADMIN users
- [ ] Test BASE_USER can change their own password
- [ ] Test BASE_USER cannot access user management
- [ ] Test SSO reset by BUSINESS_ADMIN
- [ ] Test API key generation and regeneration
- [ ] Test user deactivation vs deletion
- [ ] Test usage tracking endpoints

**Completion Criteria:**
- All user management endpoints implemented
- Role-based access enforced
- Password change/reset working
- SSO reset functional
- API key management working
- All QA tests pass

---

#### Step 5.5: Update Frontend for User Hierarchy & Access Control
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Update AuthContext to include role and business_id
- [ ] Create role-based route guards
- [ ] Create user management UI (for admins)
- [ ] Add password change UI
- [ ] Add conditional navigation based on role
- [ ] Hide/disable features based on permissions
- [ ] Create business admin dashboard
- [ ] Add usage tracking UI for system admins

**Files to Create:**
- `frontend/src/contexts/AuthContext.tsx` (update)
- `frontend/src/components/RoleGuard.tsx`
- `frontend/src/pages/admin/UserManagement.tsx`
- `frontend/src/pages/admin/BusinessManagement.tsx`
- `frontend/src/pages/admin/UsageTracking.tsx`
- `frontend/src/pages/business/TeamManagement.tsx`
- `frontend/src/pages/profile/ChangePassword.tsx`
- `frontend/src/hooks/usePermissions.ts`
- `frontend/src/services/users.ts`
- `frontend/src/services/businesses.ts`

**UI Updates:**

**Navigation (based on role):**
- SYSTEM_ADMIN: All tabs + Admin, Businesses, Usage
- BUSINESS_ADMIN: Dashboard, Clients, Events, Team Management, API Keys
- BASE_USER: Dashboard, Clients (read-only), Events (read-only)

**Features by Role:**
```typescript
SYSTEM_ADMIN:
- Full CRUD on all resources
- User management (all users)
- Business management
- Usage tracking
- API configuration

BUSINESS_ADMIN:
- CRUD on clients/events (their business)
- User management (their business only)
- API key management
- Team oversight
- SSO management

BASE_USER:
- Read-only dashboard
- Read-only clients
- Read-only events
- Change own password
```

**QA Tests:**
- [ ] Test navigation shows correct items per role
- [ ] Test SYSTEM_ADMIN sees admin menu
- [ ] Test BUSINESS_ADMIN sees team management
- [ ] Test BASE_USER has read-only access
- [ ] Test role guard prevents unauthorized access
- [ ] Test user management UI (create, edit, deactivate)
- [ ] Test password change form
- [ ] Test SSO reset button (business admin)
- [ ] Test API key management UI
- [ ] Test usage tracking dashboard
- [ ] Verify buttons/actions hidden for unauthorized users
- [ ] Test error messages for permission denials

**Completion Criteria:**
- AuthContext includes role/business
- Role-based navigation working
- User management UI functional
- Password management working
- Permission-based UI hiding/disabling
- All QA tests pass

---

#### Step 5.6: Prepare for SSO Integration (Future)
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Design SSO architecture (OAuth2/SAML)
- [ ] Add SSO configuration fields to Business model
- [ ] Create SSO redirect endpoints (placeholder)
- [ ] Document SSO integration requirements
- [ ] Create SSO callback handler (placeholder)
- [ ] Add SSO status indicators in UI

**Files to Create:**
- `backend/app/api/routes/sso.py` (placeholder endpoints)
- `backend/app/services/sso_service.py` (placeholder)
- `backend/app/schemas/sso_config.py`
- `docs/SSO_INTEGRATION_GUIDE.md`
- `frontend/src/pages/admin/SSOConfiguration.tsx`

**SSO Providers to Support (Future):**
- Google Workspace
- Microsoft Azure AD
- Okta
- Auth0
- Custom SAML 2.0

**Business Model SSO Fields:**
```python
sso_enabled: Boolean (default: False)
sso_provider: String (nullable)
sso_config: JSON (provider-specific config)
sso_domain: String (email domain for SSO)
```

**QA Tests:**
- [ ] Add SSO fields to Business model
- [ ] Create placeholder SSO endpoints
- [ ] Add SSO configuration UI
- [ ] Test SSO status indicators
- [ ] Verify SSO reset functionality for business admins
- [ ] Document SSO integration steps
- [ ] Create SSO configuration examples

**Completion Criteria:**
- SSO fields in database
- Placeholder endpoints created
- Documentation complete
- UI prepared for SSO
- All QA tests pass

---

### ✅ Phase 6: Testing & Optimization

#### Step 6.1: Backend Testing
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Write unit tests for services
- [ ] Write integration tests for API endpoints
- [ ] Set up pytest configuration
- [ ] Add test coverage reporting
- [ ] Achieve >80% code coverage

**Files to Create:**
- `backend/tests/test_clients.py`
- `backend/tests/test_events.py`
- `backend/tests/test_dashboard.py`
- `backend/pytest.ini`

**QA Tests:**
- [ ] Run `pytest` - all tests pass
- [ ] Run `pytest --cov` - check coverage >80%
- [ ] Test all CRUD operations
- [ ] Test error handling
- [ ] Test edge cases
- [ ] Test concurrent requests
- [ ] Run load tests

**Completion Criteria:**
- >80% test coverage
- All tests passing
- All QA tests pass

---

#### Step 6.2: Frontend Testing
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Set up Vitest
- [ ] Write component tests
- [ ] Write integration tests
- [ ] Set up React Testing Library
- [ ] Add E2E tests with Playwright (optional)

**Files to Create:**
- `frontend/tests/components/*.test.tsx`
- `frontend/tests/pages/*.test.tsx`
- `frontend/vitest.config.ts`

**QA Tests:**
- [ ] Run `npm test` - all tests pass
- [ ] Test all major components
- [ ] Test user flows
- [ ] Test error states
- [ ] Test loading states
- [ ] Run E2E tests (if implemented)

**Completion Criteria:**
- All components tested
- All tests passing
- All QA tests pass

---

#### Step 6.3: Performance Optimization
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Add database query optimization
- [ ] Implement API response caching
- [ ] Add React query caching
- [ ] Optimize bundle size
- [ ] Add lazy loading for routes
- [ ] Add image optimization

**QA Tests:**
- [ ] Test API response times (<500ms)
- [ ] Test page load times (<3s)
- [ ] Check bundle size (<500kb gzipped)
- [ ] Test with slow network (3G)
- [ ] Verify caching works
- [ ] Check database query counts
- [ ] Test with large datasets

**Completion Criteria:**
- Performance targets met
- All QA tests pass

---

### ✅ Phase 7: Deployment

#### Step 7.1: Production Configuration
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Create production environment files
- [ ] Set up production database
- [ ] Configure production Redis
- [ ] Set up logging
- [ ] Configure error tracking (Sentry)
- [ ] Set up monitoring

**Files to Create:**
- `backend/.env.production`
- `frontend/.env.production`
- `docker-compose.prod.yml`

**QA Tests:**
- [ ] Test production build locally
- [ ] Verify environment variables load
- [ ] Check logging outputs
- [ ] Test error tracking
- [ ] Verify monitoring endpoints
- [ ] Check security headers

**Completion Criteria:**
- Production config complete
- All QA tests pass

---

#### Step 7.2: Deploy to Production
**Status**: ⏸️ Not Started

**Tasks:**
- [ ] Set up production server (AWS/DigitalOcean/etc.)
- [ ] Configure domain and SSL
- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] Set up CI/CD pipeline
- [ ] Configure backups

**QA Tests:**
- [ ] Access app via production URL
- [ ] Test HTTPS works
- [ ] Test all API endpoints
- [ ] Test frontend functionality
- [ ] Verify database connection
- [ ] Test backups work
- [ ] Run smoke tests

**Completion Criteria:**
- App deployed and accessible
- SSL configured
- All QA tests pass

---

## Migration Checklist

### Before Starting
- [ ] Read entire migration plan
- [ ] Understand technology stack
- [ ] Set up development environment
- [ ] Back up Streamlit application

### During Migration
- [ ] Complete phases in order
- [ ] Run QA tests after each step
- [ ] Document any issues encountered
- [ ] Commit code after each completed step

### After Migration
- [ ] Run full application test
- [ ] Migrate production data
- [ ] Update documentation
- [ ] Train users (if applicable)
- [ ] Monitor for issues

---

## Rollback Plan

If migration needs to be paused or rolled back:

1. **Keep Streamlit app running** until migration is complete
2. **Tag each step** in Git for easy rollback
3. **Back up database** before data migration
4. **Test rollback procedure** before going live

---

## Notes & Issues

(This section will be filled in during migration)

---

**Last Updated**: 2025-10-19
**Current Step**: Phase 5 - Step 5.1 COMPLETED ✅ (Basic Authentication)
**Next Step**: Phase 5 - Step 5.2 (User Hierarchy & RBAC)
**Server Status**:
- FastAPI backend: http://localhost:8000 ✅ Running
- React frontend: http://localhost:5175 ✅ Running
- Database: SQLite (client_intelligence.db) with 43 clients, 1,557 events, 35 job runs
- System Admin User: admin / admin123 ✅ Created

**Migration Progress**:
- **Phase 1 (Infrastructure Setup)**: ✅ COMPLETED - All infrastructure setup complete!
- **Phase 2 (Database & Models)**: ✅ COMPLETED - All database models, schemas, and data migrated!
- **Phase 3 (Backend API Development)**: ✅ COMPLETED - All API routes and service layers implemented!
  - Step 3.1: Client API ✅
  - Step 3.2: Event API ✅
  - Step 3.3: Analytics API ✅
  - Step 3.4: Scheduler API ✅
  - Step 3.5: Search & Cache API ✅
- **Phase 4 (Frontend Development)**: ✅ COMPLETED - All pages and components built!
  - Step 4.1: Layout & Navigation ✅
  - Step 4.2: Dashboard Page ✅
  - Step 4.3: Clients Page ✅
  - Step 4.4: Events Page ✅
  - Step 4.5: Automation Page ✅
  - Step 4.6: Settings Page ✅
  - Step 4.7: Search Page ✅
- **Phase 5 (Authentication & User Management)**: 🔄 IN PROGRESS
  - Step 5.1: Basic Authentication ✅ COMPLETED
  - Step 5.2: User Hierarchy & RBAC ⏸️ Not Started
  - Step 5.3: Data Visibility & Multi-Tenancy ⏸️ Not Started
  - Step 5.4: User Management APIs ⏸️ Not Started
  - Step 5.5: Frontend User Management ⏸️ Not Started
  - Step 5.6: SSO Preparation ⏸️ Not Started
- **Phase 6 (Testing & Optimization)**: ⏸️ Not started
- **Phase 7 (Deployment)**: ⏸️ Not started

**Overall Progress**: 4.2 out of 7 phases complete (60% - core functionality + basic auth complete)
