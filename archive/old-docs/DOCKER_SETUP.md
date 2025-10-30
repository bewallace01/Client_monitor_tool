# Docker Setup Guide

This guide explains how to set up and run the Client Intelligence Monitor using Docker.

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+

### Installing Docker

**Windows:**
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Run the installer
3. Restart your computer
4. Verify installation: `docker --version` and `docker compose version`

**Mac:**
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Drag Docker.app to Applications
3. Start Docker Desktop
4. Verify installation: `docker --version` and `docker compose version`

**Linux:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## Quick Start

### Option 1: Database Services Only (Recommended for Development)

Run only PostgreSQL and Redis, use local Python/Node.js for development:

```bash
# Start PostgreSQL and Redis
docker compose up -d postgres redis

# Verify services are running
docker compose ps

# View logs
docker compose logs postgres
docker compose logs redis

# Stop services
docker compose stop

# Remove services and data
docker compose down -v
```

Then run backend and frontend locally:
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Option 2: Full Stack with Docker

Run everything in containers (backend, frontend, database, cache):

```bash
# Start all services
docker compose --profile full up -d

# View logs
docker compose --profile full logs -f

# Stop all services
docker compose --profile full down
```

## Service Details

### PostgreSQL Database
- **Port:** 5432
- **Database:** client_intelligence
- **Username:** postgres
- **Password:** postgres (change in production!)
- **Connection String:** `postgresql://postgres:postgres@localhost:5432/client_intelligence`

### Redis Cache
- **Port:** 6379
- **Connection String:** `redis://localhost:6379/0`

### Backend API (Full Stack Only)
- **Port:** 8000
- **Swagger Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Frontend (Full Stack Only)
- **Port:** 5173
- **URL:** http://localhost:5173

## Database Management

### Connect to PostgreSQL

```bash
# Using Docker exec
docker compose exec postgres psql -U postgres -d client_intelligence

# Using psql client (if installed locally)
psql -h localhost -U postgres -d client_intelligence
```

### Backup Database

```bash
# Backup
docker compose exec postgres pg_dump -U postgres client_intelligence > backup.sql

# Restore
docker compose exec -T postgres psql -U postgres client_intelligence < backup.sql
```

### Reset Database

```bash
# Stop and remove volumes
docker compose down -v

# Start fresh
docker compose up -d postgres redis
```

## Redis Management

### Connect to Redis

```bash
# Using Docker exec
docker compose exec redis redis-cli

# Test connection
docker compose exec redis redis-cli ping
```

### Clear Redis Cache

```bash
docker compose exec redis redis-cli FLUSHALL
```

## Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

```bash
# Find process using port 5432 (PostgreSQL)
# Windows
netstat -ano | findstr :5432
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5432
kill -9 <PID>
```

### Container Won't Start

```bash
# Check logs
docker compose logs <service_name>

# Remove and rebuild
docker compose down
docker compose up -d --build
```

### Database Connection Issues

1. Verify services are healthy:
   ```bash
   docker compose ps
   ```

2. Check backend can reach PostgreSQL:
   ```bash
   cd backend
   python app/database/test_connection.py
   ```

3. Update DATABASE_URL in backend/.env:
   ```
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/client_intelligence
   USE_SQLITE=False
   ```

## Production Deployment

For production, create a `docker-compose.prod.yml`:

1. Use environment variables for secrets
2. Set up proper networking and security
3. Use a reverse proxy (nginx) for SSL
4. Set resource limits
5. Configure proper logging
6. Use Docker secrets or external secret management
7. Set up automated backups

Example production environment variables:
```bash
DATABASE_URL=postgresql://user:secure_password@db:5432/production_db
REDIS_URL=redis://:secure_password@redis:6379/0
DEBUG=False
SECRET_KEY=<generate-secure-random-key>
```

## Development vs Production

**Development (Current Setup):**
- Uses SQLite by default (no Docker required)
- Debug mode enabled
- Hot reload enabled
- Exposed ports for all services

**Production (Recommended):**
- PostgreSQL in Docker with backups
- Redis for caching and sessions
- Containerized backend and frontend
- Environment-based configuration
- SSL/TLS enabled
- Resource limits and monitoring
