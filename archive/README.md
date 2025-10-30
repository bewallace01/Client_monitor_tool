# Archive Folder

This folder contains legacy files from previous versions of the Client Intelligence Monitor application.

## Contents

### legacy-streamlit/
Contains the original Streamlit-based application that has been replaced by the modern FastAPI + React architecture.

**Key files:**
- `app.py` - Original Streamlit dashboard
- `src/` - Legacy Python modules
- `config/` - Old configuration system
- `requirements.txt` - Streamlit dependencies
- `settings.json` - Old settings file
- `client_intelligence.db` - Legacy SQLite database

### old-scripts/
Contains deprecated utility scripts that are no longer needed in the new architecture.

**Files:**
- `seed_data.py` - Old data seeding (replaced by backend scripts)
- `seed_demo_data.py` - Demo data generation (replaced)
- `setup_db_new.py` - Old database setup
- `migrate_*.py` - Legacy migration scripts
- `test_*.py` - Old test files
- `run_monitor.py` - Old monitoring script
- `start_scheduler.py` - Old scheduler
- `test_collector.py` - Legacy test file
- `run_tests.py` - Old test runner
- `run.bat` - Windows batch file
- `pytest.ini` - Old pytest configuration
- `requirements-test.txt` - Old test dependencies

### old-docs/
Contains outdated documentation files.

**Files:**
- `QUICKSTART.md` - Old quick start guide
- `PROJECT_STATUS.md` - Historical project status
- `DATABASE_REDESIGN.md` - Database redesign notes
- `MIGRATION_PLAN.md` - Migration planning document
- `DOCKER_SETUP.md` - Old Docker setup guide

## Migration Notes

The application has been modernized with:

- **Backend**: Streamlit → FastAPI
- **Frontend**: Embedded HTML/CSS → React + TypeScript + Vite
- **Database**: Legacy SQLite schema → Alembic migrations with PostgreSQL support
- **API**: N/A → RESTful API with OpenAPI documentation
- **Authentication**: N/A → JWT-based auth system
- **Multi-user**: No → Yes, with business/organization support
- **Deployment**: Local only → Docker + cloud-ready

## Restoration

If you need to restore any legacy files for reference:

```bash
# From the archive folder
cp legacy-streamlit/app.py ../app.py.backup
```

## Deletion

These files are kept for reference but can be safely deleted if disk space is needed:

```bash
# From the project root
rm -rf archive/
```

**Last Updated**: 2025-10-27
