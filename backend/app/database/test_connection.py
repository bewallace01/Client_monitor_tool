"""Test database connection script."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.database.connection import engine, SessionLocal
from app.core.config import settings


def test_connection():
    """Test database connection."""
    print(f"Testing connection to: {settings.DATABASE_URL}")
    print("-" * 60)

    try:
        # Test engine connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("[OK] Engine connection successful")

        # Test session
        db = SessionLocal()
        try:
            # For SQLite, use a different query
            if settings.USE_SQLITE:
                result = db.execute(text("SELECT sqlite_version()"))
                version = result.scalar()
                print(f"[OK] Session connection successful")
                print(f"[OK] SQLite version: {version}")
            else:
                result = db.execute(text("SELECT version()"))
                version = result.scalar()
                print(f"[OK] Session connection successful")
                print(f"[OK] Database version: {version}")
        finally:
            db.close()

        print("-" * 60)
        print("All database tests passed!")
        return True

    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print("-" * 60)
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
