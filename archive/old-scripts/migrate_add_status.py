"""
Database migration script to add 'status' column to events table.
This fixes the schema mismatch between old SQLAlchemy and new SQLite storage.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import sqlite3
from config import settings

def migrate_database():
    """Add status column to events table if it doesn't exist."""
    db_path = settings.database_url.replace("sqlite:///", "")

    print(f"Migrating database: {db_path}")
    print("=" * 60)

    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if events table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='events'
        """)

        if not cursor.fetchone():
            print("[INFO] Events table doesn't exist yet. No migration needed.")
            return

        # Check if status column exists
        cursor.execute("PRAGMA table_info(events)")
        columns = [row[1] for row in cursor.fetchall()]

        if "status" in columns:
            print("[OK] Status column already exists. No migration needed.")
        else:
            print("[INFO] Adding 'status' column to events table...")

            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN status TEXT NOT NULL DEFAULT 'new'
            """)

            conn.commit()
            print("[OK] Successfully added 'status' column!")
            print("[OK] All existing events will have status='new'")

        print("\n" + "=" * 60)
        print("[SUCCESS] Migration complete!")
        print("\nNext steps:")
        print("1. Refresh your browser (Ctrl+R or Cmd+R)")
        print("2. Navigate to the Database page")
        print("3. The page should now load without errors")

    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return 1
    finally:
        if conn:
            conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(migrate_database())
