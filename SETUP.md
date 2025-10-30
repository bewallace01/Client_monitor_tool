# Client Intelligence Monitor - Setup Guide

> Production-ready client intelligence monitoring platform with FastAPI backend and React frontend

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Option 1: Full Stack (Recommended)](#option-1-full-stack-recommended)
  - [Option 2: Docker Setup](#option-2-docker-setup)
  - [Option 3: Development Mode](#option-3-development-mode)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Database Setup](#database-setup)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

---

## Overview

The Client Intelligence Monitor is a modern web application built with:

- **Backend**: FastAPI (Python) - REST API with PostgreSQL/SQLite
- **Frontend**: React + TypeScript + Vite - Modern responsive UI
- **Database**: PostgreSQL (production) or SQLite (development)
- **Cache**: Redis (optional for production)
- **Styling**: TailwindCSS
- **State Management**: React Query (TanStack Query)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   React Frontend                        │
│              (Vite + TypeScript + Tailwind)             │
│                  Port: 5173                             │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────┐
│                  FastAPI Backend                        │
│            (Python 3.9+ + SQLAlchemy)                   │
│                  Port: 8000                             │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│   PostgreSQL    │    │      Redis       │
│   Port: 5432    │    │    Port: 6379    │
│   (Production)  │    │    (Optional)    │
│                 │    │                  │
│   or SQLite     │    └──────────────────┘
│   (Development) │
└─────────────────┘
```

---

## Prerequisites

### Required Software

- **Python**: 3.9 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher (comes with Node.js)
- **Git**: For version control

### Optional (for Production)

- **PostgreSQL**: 15.x or higher
- **Redis**: 7.x or higher
- **Docker**: 20.x or higher (for containerized deployment)
- **Docker Compose**: 2.x or higher

### System Requirements

- **RAM**: 2GB minimum, 4GB recommended
- **Disk Space**: 1GB minimum
- **OS**: Windows, macOS, or Linux

---

## Installation

### Option 1: Full Stack (Recommended)

This option runs both frontend and backend locally for development.

#### Step 1: Clone the Repository

```bash
cd "C:\Users\bwall\Desktop\Client Monitor"
```

#### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
copy .env.example .env

# Initialize database
python -m alembic upgrade head

# (Optional) Create initial admin user
python scripts/create_admin.py

# (Optional) Create default business
python scripts/create_default_business.py
```

#### Step 3: Frontend Setup

```bash
# Open a new terminal window
cd frontend

# Install dependencies
npm install

# Create .env file
copy .env.example .env
```

#### Step 4: Start Services

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

### Option 2: Docker Setup

This option uses Docker Compose to run all services in containers.

#### Step 1: Install Docker

Download and install Docker Desktop from: https://www.docker.com/products/docker-desktop

#### Step 2: Configure Environment

```bash
# Copy environment files
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env

# Edit backend/.env to match your setup
```

#### Step 3: Start All Services

```bash
# Start only database and cache (minimal)
docker compose up -d postgres redis

# Or start full stack (backend + frontend + database + cache)
docker compose --profile full up -d
```

#### Step 4: Initialize Database

```bash
# Run migrations
docker compose exec backend alembic upgrade head

# Create admin user
docker compose exec backend python scripts/create_admin.py
```

#### Access Points:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

---

### Option 3: Development Mode

Fastest way to get started with SQLite (no PostgreSQL required).

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Set SQLite mode in .env
echo DATABASE_URL=sqlite:///./data/client_intelligence.db > .env
echo USE_SQLITE=True >> .env

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## Configuration

### Backend Configuration

Edit `backend/.env`:

```env
# Application
APP_NAME=Client Intelligence Monitor
APP_VERSION=2.0.0
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# Database (choose one)
# Option 1: SQLite (Development)
DATABASE_URL=sqlite:///./data/client_intelligence.db
USE_SQLITE=True

# Option 2: PostgreSQL (Production)
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/client_intelligence
# USE_SQLITE=False

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# External APIs (Optional)
GOOGLE_API_KEY=your-google-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
NEWSAPI_KEY=your-newsapi-key
USE_MOCK_APIS=True

# Scheduler
SCHEDULER_ENABLED=True
SCHEDULER_TIMEZONE=UTC

# CORS (add your frontend URL)
ALLOWED_ORIGINS=["http://localhost:5173"]
```

### Frontend Configuration

Edit `frontend/.env`:

```env
# API Base URL
VITE_API_BASE_URL=http://localhost:8000

# Optional: Other environment-specific settings
```

---

## Running the Application

### Development Mode

**Backend:**
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### Production Mode

**Backend:**
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend:**
```bash
cd frontend
npm run build
npm run preview
```

---

## Database Setup

### Using SQLite (Development)

SQLite requires no additional setup. The database file will be created automatically at `backend/data/client_intelligence.db`.

### Using PostgreSQL (Production)

#### Option 1: Docker Compose (Recommended)

```bash
docker compose up -d postgres
```

#### Option 2: Manual Installation

1. Install PostgreSQL 15+
2. Create database:
```sql
CREATE DATABASE client_intelligence;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE client_intelligence TO postgres;
```

3. Update `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/client_intelligence
USE_SQLITE=False
```

### Running Migrations

```bash
cd backend
venv\Scripts\activate

# View current version
alembic current

# Upgrade to latest
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "description"
```

### Verify Database Setup

```bash
cd backend
python scripts/verify_tables.py
```

---

## API Documentation

### Interactive API Docs

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Key API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout

#### Clients
- `GET /api/v1/clients` - List all clients
- `POST /api/v1/clients` - Create client
- `GET /api/v1/clients/{id}` - Get client details
- `PUT /api/v1/clients/{id}` - Update client
- `DELETE /api/v1/clients/{id}` - Delete client

#### Events
- `GET /api/v1/events` - List all events
- `POST /api/v1/events` - Create event
- `GET /api/v1/events/{id}` - Get event details
- `PUT /api/v1/events/{id}` - Update event
- `DELETE /api/v1/events/{id}` - Delete event

#### Analytics
- `GET /api/v1/analytics/overview` - Dashboard metrics
- `GET /api/v1/analytics/trends` - Trend analysis
- `GET /api/v1/analytics/clients/{id}/summary` - Client summary

#### Search
- `GET /api/v1/search` - Global search across clients and events

---

## Troubleshooting

### Backend Issues

#### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <process_id> /F
```

#### Database Connection Error
- Check PostgreSQL is running: `docker compose ps postgres`
- Verify DATABASE_URL in `.env`
- Test connection: `python backend/app/database/test_connection.py`

#### Import Errors
```bash
# Reinstall dependencies
cd backend
pip install --upgrade -r requirements.txt
```

### Frontend Issues

#### Port Already in Use
```bash
# Vite will automatically try alternative ports (5174, 5175, etc.)
# Or specify a port:
npm run dev -- --port 3000
```

#### Module Not Found
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Build Errors
```bash
# Clear cache and rebuild
cd frontend
npm run build --force
```

### Docker Issues

#### Containers Not Starting
```bash
# View logs
docker compose logs backend
docker compose logs postgres

# Restart services
docker compose restart
```

#### Database Not Initialized
```bash
docker compose exec backend alembic upgrade head
```

### Common Errors

#### "CORS Error" in Browser
- Add your frontend URL to `ALLOWED_ORIGINS` in `backend/.env`
- Restart backend server

#### "Connection Refused"
- Ensure backend is running on port 8000
- Check `VITE_API_BASE_URL` in `frontend/.env`

#### "Alembic Migration Failed"
```bash
# Reset migrations (⚠️ will delete data)
cd backend
rm -rf alembic/versions/*.py
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

---

## Project Structure

```
Client Monitor/
│
├── archive/                    # Archived legacy files
│   ├── legacy-streamlit/      # Old Streamlit application
│   ├── old-scripts/           # Deprecated scripts
│   └── old-docs/              # Old documentation
│
├── backend/                    # FastAPI Backend
│   ├── alembic/               # Database migrations
│   │   ├── versions/          # Migration files
│   │   └── env.py            # Alembic environment
│   │
│   ├── app/                   # Application code
│   │   ├── api/              # API routes
│   │   │   └── routes/       # Endpoint definitions
│   │   ├── core/             # Core functionality
│   │   │   ├── config.py     # Settings
│   │   │   └── security.py   # Auth & security
│   │   ├── database/         # Database layer
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── main.py           # FastAPI app
│   │
│   ├── scripts/              # Utility scripts
│   ├── tests/                # Backend tests
│   ├── data/                 # SQLite database (if used)
│   ├── .env.example          # Environment template
│   ├── alembic.ini           # Alembic config
│   └── requirements.txt      # Python dependencies
│
├── frontend/                  # React Frontend
│   ├── public/               # Static assets
│   ├── src/                  # Source code
│   │   ├── components/       # Reusable components
│   │   ├── pages/            # Page components
│   │   ├── contexts/         # React contexts
│   │   ├── hooks/            # Custom hooks
│   │   ├── services/         # API services
│   │   ├── types/            # TypeScript types
│   │   ├── utils/            # Utility functions
│   │   ├── App.tsx           # Main app component
│   │   └── main.tsx          # Entry point
│   │
│   ├── .env.example          # Environment template
│   ├── index.html            # HTML template
│   ├── package.json          # Node dependencies
│   ├── tsconfig.json         # TypeScript config
│   ├── tailwind.config.js    # Tailwind config
│   └── vite.config.ts        # Vite config
│
├── docs/                      # Documentation
│   ├── USER_GUIDE.md         # User documentation
│   ├── DEVELOPER_GUIDE.md    # Developer docs
│   ├── API_SETUP.md          # API configuration
│   └── DEPLOYMENT.md         # Deployment guide
│
├── tests/                     # Integration tests
├── .env.example               # Root environment template
├── .gitignore                # Git ignore rules
├── docker-compose.yml        # Docker configuration
├── README.md                 # Project overview
└── SETUP.md                  # This file
```

---

## Next Steps

After installation:

1. **Create Admin User**: Run `python backend/scripts/create_admin.py`
2. **Create Default Business**: Run `python backend/scripts/create_default_business.py`
3. **Add Sample Data**: Use the UI or import data via API
4. **Configure APIs**: Set up external API keys in `.env` (optional)
5. **Explore Features**: Visit http://localhost:5173

---

## Getting Help

- **Documentation**: Check the `docs/` folder
- **API Docs**: http://localhost:8000/docs
- **Issues**: Report bugs or request features

---

## Production Deployment

For production deployment instructions, see:
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Full deployment guide
- [docker-compose.yml](docker-compose.yml) - Container orchestration

### Quick Production Checklist

- [ ] Set `DEBUG=False` in backend `.env`
- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable Redis for caching
- [ ] Configure CORS with your production domain
- [ ] Set up SSL/TLS certificates
- [ ] Configure backup strategy
- [ ] Set up monitoring and logging
- [ ] Review security settings

---

**Built with ❤️ for Customer Success Professionals**

