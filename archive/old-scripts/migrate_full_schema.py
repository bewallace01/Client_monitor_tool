"""
Comprehensive database migration script.
Migrates from old SQLAlchemy schema to new DTO-based schema.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import sqlite3
from config import settings

def migrate_database():
    """Migrate database schema from old to new format."""
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
            conn.close()
            return 0

        # Get current columns
        cursor.execute("PRAGMA table_info(events)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        print(f"[INFO] Found {len(columns)} columns in events table")

        migrations_applied = []

        # Migration 1: Add status column
        if "status" not in columns:
            print("[MIGRATE] Adding 'status' column...")
            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN status TEXT NOT NULL DEFAULT 'new'
            """)
            migrations_applied.append("status")

        # Migration 2: Add published_date (map from event_date)
        if "published_date" not in columns and "event_date" in columns:
            print("[MIGRATE] Adding 'published_date' column (mapping from event_date)...")
            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN published_date TEXT
            """)
            # Copy data from event_date to published_date
            cursor.execute("""
                UPDATE events
                SET published_date = event_date
            """)
            migrations_applied.append("published_date")

        # Migration 3: Add discovered_date (map from discovered_at)
        if "discovered_date" not in columns and "discovered_at" in columns:
            print("[MIGRATE] Adding 'discovered_date' column (mapping from discovered_at)...")
            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN discovered_date TEXT
            """)
            # Copy data from discovered_at to discovered_date
            cursor.execute("""
                UPDATE events
                SET discovered_date = discovered_at
            """)
            migrations_applied.append("discovered_date")

        # Migration 4: Add event_type (default to category for now)
        if "event_type" not in columns:
            print("[MIGRATE] Adding 'event_type' column...")
            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN event_type TEXT
            """)
            # Map from category if it exists
            if "category" in columns:
                cursor.execute("""
                    UPDATE events
                    SET event_type = CASE
                        WHEN category = 'FUNDING' THEN 'funding'
                        WHEN category = 'ACQUISITION' THEN 'acquisition'
                        WHEN category = 'LEADERSHIP' THEN 'leadership'
                        WHEN category = 'PRODUCT' THEN 'product'
                        WHEN category = 'NEWS' THEN 'news'
                        ELSE 'other'
                    END
                """)
            else:
                cursor.execute("UPDATE events SET event_type = 'news'")
            migrations_applied.append("event_type")

        # Migration 5: Add summary (map from description)
        if "summary" not in columns and "description" in columns:
            print("[MIGRATE] Adding 'summary' column (mapping from description)...")
            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN summary TEXT
            """)
            cursor.execute("""
                UPDATE events
                SET summary = description
            """)
            migrations_applied.append("summary")

        # Migration 6: Add source_url (map from url)
        if "source_url" not in columns and "url" in columns:
            print("[MIGRATE] Adding 'source_url' column (mapping from url)...")
            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN source_url TEXT
            """)
            cursor.execute("""
                UPDATE events
                SET source_url = url
            """)
            migrations_applied.append("source_url")

        # Migration 7: Add source_name (map from source)
        if "source_name" not in columns and "source" in columns:
            print("[MIGRATE] Adding 'source_name' column (mapping from source)...")
            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN source_name TEXT
            """)
            cursor.execute("""
                UPDATE events
                SET source_name = source
            """)
            migrations_applied.append("source_name")

        # Migration 8: Add sentiment (derive from sentiment_score)
        if "sentiment" not in columns:
            print("[MIGRATE] Adding 'sentiment' column...")
            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN sentiment TEXT DEFAULT 'neutral'
            """)
            if "sentiment_score" in columns:
                cursor.execute("""
                    UPDATE events
                    SET sentiment = CASE
                        WHEN sentiment_score >= 0.3 THEN 'positive'
                        WHEN sentiment_score <= -0.3 THEN 'negative'
                        ELSE 'neutral'
                    END
                """)
            migrations_applied.append("sentiment")

        # Migration 9: Add tags column (empty JSON array)
        if "tags" not in columns:
            print("[MIGRATE] Adding 'tags' column...")
            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN tags TEXT DEFAULT '[]'
            """)
            cursor.execute("UPDATE events SET tags = '[]' WHERE tags IS NULL")
            migrations_applied.append("tags")

        # Migration 10: Add metadata column (empty JSON object)
        if "metadata" not in columns:
            print("[MIGRATE] Adding 'metadata' column...")
            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN metadata TEXT DEFAULT '{}'
            """)
            cursor.execute("UPDATE events SET metadata = '{}' WHERE metadata IS NULL")
            migrations_applied.append("metadata")

        # ==================== Migrate Clients Table ====================

        # Get clients table columns
        cursor.execute("PRAGMA table_info(clients)")
        client_columns = {row[1]: row[2] for row in cursor.fetchall()}

        # Migration 11: Add priority column to clients
        if "priority" not in client_columns:
            print("[MIGRATE] Adding 'priority' column to clients table...")
            cursor.execute("""
                ALTER TABLE clients
                ADD COLUMN priority TEXT NOT NULL DEFAULT 'medium'
            """)
            migrations_applied.append("clients.priority")

        # Migration 12: Add keywords column to clients (map from search_keywords)
        if "keywords" not in client_columns and "search_keywords" in client_columns:
            print("[MIGRATE] Adding 'keywords' column to clients table...")
            cursor.execute("""
                ALTER TABLE clients
                ADD COLUMN keywords TEXT
            """)
            cursor.execute("""
                UPDATE clients
                SET keywords = search_keywords
            """)
            migrations_applied.append("clients.keywords")

        # Migration 13: Add monitoring_since column to clients (map from created_at)
        if "monitoring_since" not in client_columns and "created_at" in client_columns:
            print("[MIGRATE] Adding 'monitoring_since' column to clients table...")
            cursor.execute("""
                ALTER TABLE clients
                ADD COLUMN monitoring_since TEXT
            """)
            cursor.execute("""
                UPDATE clients
                SET monitoring_since = created_at
            """)
            migrations_applied.append("clients.monitoring_since")

        # Migration 14: Add last_checked column to clients (map from last_checked_at)
        if "last_checked" not in client_columns and "last_checked_at" in client_columns:
            print("[MIGRATE] Adding 'last_checked' column to clients table...")
            cursor.execute("""
                ALTER TABLE clients
                ADD COLUMN last_checked TEXT
            """)
            cursor.execute("""
                UPDATE clients
                SET last_checked = last_checked_at
            """)
            migrations_applied.append("clients.last_checked")

        # Migration 15: Add metadata column to clients
        if "metadata" not in client_columns:
            print("[MIGRATE] Adding 'metadata' column to clients table...")
            cursor.execute("""
                ALTER TABLE clients
                ADD COLUMN metadata TEXT DEFAULT '{}'
            """)
            cursor.execute("UPDATE clients SET metadata = '{}' WHERE metadata IS NULL")
            migrations_applied.append("clients.metadata")

        # Commit all changes
        conn.commit()

        print("\n" + "=" * 60)
        if migrations_applied:
            print(f"[SUCCESS] Applied {len(migrations_applied)} migrations:")
            for migration in migrations_applied:
                print(f"  - {migration}")
        else:
            print("[OK] Schema is up-to-date. No migrations needed.")

        print("\nNext steps:")
        print("1. Refresh your browser (Ctrl+R or Cmd+R)")
        print("2. Navigate to the Database page")
        print("3. The page should now load without errors")

        conn.close()
        return 0

    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return 1


if __name__ == "__main__":
    sys.exit(migrate_database())
