# Quick Start Guide

Get the Client Intelligence Monitor running in under 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.9+)
python --version

# Check Node.js version (need 18+)
node --version

# Check npm version (need 9+)
npm --version
```

## Option 1: Development Mode (SQLite)

Fastest way to get started - no PostgreSQL required!

### Backend Setup

```bash
cd backend
python -m venv venv

# Activate virtual environment
venv\Scripts\activate              # Windows
# source venv/bin/activate         # macOS/Linux

pip install -r requirements.txt
copy .env.example .env

# Initialize database
alembic upgrade head

# Start backend
uvicorn app.main:app --reload
```

Backend will run at: http://localhost:8000

### Frontend Setup (New Terminal)

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Frontend will run at: http://localhost:5173

### First Steps

1. Open http://localhost:5173 in your browser
2. Create an account or login
3. Start adding clients and events!
4. Check API docs at http://localhost:8000/docs

---

## Option 2: Docker (Full Stack)

Use Docker for a complete production-like environment.

```bash
# Start database and cache
docker compose up -d postgres redis

# Initialize database
docker compose exec postgres psql -U postgres -c "CREATE DATABASE client_intelligence;"

# Start all services
docker compose --profile full up -d

# Run migrations
docker compose exec backend alembic upgrade head
```

Access:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Option 3: Production Setup

For deployment with PostgreSQL.

### 1. Install PostgreSQL

**Windows**: Download from https://www.postgresql.org/download/windows/

**macOS**:
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu)**:
```bash
sudo apt update
sudo apt install postgresql-15
sudo systemctl start postgresql
```

### 2. Create Database

```bash
sudo -u postgres psql
CREATE DATABASE client_intelligence;
CREATE USER postgres WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE client_intelligence TO postgres;
\q
```

### 3. Configure Backend

Edit `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:your-secure-password@localhost:5432/client_intelligence
USE_SQLITE=False
DEBUG=False
SECRET_KEY=generate-a-secure-random-key-here
```

### 4. Run Application

```bash
# Backend
cd backend
venv\Scripts\activate
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend
cd frontend
npm run build
npm run preview
```

---

## Troubleshooting

### "Port already in use"

**Backend (port 8000):**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

**Frontend (port 5173):**
Vite will automatically try ports 5174, 5175, etc.

### "Module not found"

**Backend:**
```bash
cd backend
pip install --upgrade -r requirements.txt
```

**Frontend:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### "Database connection failed"

**Check if PostgreSQL is running:**
```bash
# Windows
services.msc  # Look for PostgreSQL service

# macOS
brew services list

# Linux
sudo systemctl status postgresql
```

**Test connection:**
```bash
cd backend
python app/database/test_connection.py
```

### "CORS errors in browser"

1. Check `backend/.env` has your frontend URL in `ALLOWED_ORIGINS`
2. Restart backend server
3. Clear browser cache

---

## Essential Commands

### Backend

```bash
# Start dev server
uvicorn app.main:app --reload

# Run migrations
alembic upgrade head

# Create migration
alembic revision --autogenerate -m "description"

# Create admin user
python scripts/create_admin.py

# Run tests
pytest
```

### Frontend

```bash
# Dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Docker

```bash
# Start all services
docker compose up -d

# Start with full stack
docker compose --profile full up -d

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop all services
docker compose down

# Rebuild and restart
docker compose up -d --build
```

---

## Project Structure Quick Reference

```
Client Monitor/
├── backend/              # FastAPI backend
│   ├── app/             # Application code
│   ├── alembic/         # Database migrations
│   ├── scripts/         # Utility scripts
│   └── .env             # Backend config
│
├── frontend/            # React frontend
│   ├── src/            # Source code
│   ├── public/         # Static files
│   └── .env            # Frontend config
│
└── archive/            # Legacy Streamlit app
```

---

## Next Steps

Once running:

1. **Create your first business**: Visit Settings → Businesses
2. **Add clients**: Navigate to Clients page
3. **Monitor events**: Check the Dashboard
4. **Explore API**: Visit http://localhost:8000/docs
5. **Configure external APIs**: See [API_SETUP.md](docs/API_SETUP.md)

---

## Getting Help

- **Detailed Setup**: [SETUP.md](SETUP.md)
- **API Documentation**: http://localhost:8000/docs
- **User Guide**: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- **Developer Guide**: [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)

---

**Need more help?** See the full [SETUP.md](SETUP.md) documentation.
