"""
SQLite implementation of the storage interface.
Provides persistent storage using SQLite database.
"""

import sqlite3
import json
import logging
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from contextlib import contextmanager

from .base import BaseStorage
from src.models import ClientDTO, EventDTO, SearchCacheDTO
from config import settings


# Configure logging
logger = logging.getLogger(__name__)


class SQLiteStorage(BaseStorage):
    """SQLite implementation of storage interface."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize SQLite storage.

        Args:
            db_path: Path to SQLite database file. If None, uses settings.
        """
        if db_path is None:
            # Use data directory from settings
            data_dir = settings.get_data_dir()
            self.db_path = str(data_dir / "client_intelligence.db")
        else:
            self.db_path = db_path

        self._connection = None
        logger.info(f"SQLite storage initialized with database: {self.db_path}")

    # ==================== Connection Management ====================

    def connect(self) -> None:
        """Establish connection to SQLite database."""
        try:
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self._connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
            logger.info("Connected to SQLite database")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise ConnectionError(f"Database connection failed: {e}")

    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Disconnected from database")

    def is_connected(self) -> bool:
        """Check if connected to database."""
        return self._connection is not None

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Usage:
            with storage.get_connection() as conn:
                cursor = conn.cursor()
                ...
        """
        if not self.is_connected():
            self.connect()

        try:
            yield self._connection
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            pass  # Keep connection open for reuse

    # ==================== Database Management ====================

    def _migrate_schema(self, cursor) -> None:
        """Check and migrate schema to add missing columns."""
        # Check if events table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='events'
        """)
        if not cursor.fetchone():
            return  # Table doesn't exist yet, will be created fresh

        # Check if status column exists in events table
        cursor.execute("PRAGMA table_info(events)")
        columns = [row[1] for row in cursor.fetchall()]

        if "status" not in columns:
            logger.info("Adding 'status' column to events table...")
            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN status TEXT NOT NULL DEFAULT 'new'
            """)
            logger.info("Migration complete: Added status column")

    def initialize_database(self) -> None:
        """Initialize database schema."""
        logger.info("Initializing database schema...")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Run migration first to handle existing databases
            self._migrate_schema(cursor)

            # Create clients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    industry TEXT,
                    priority TEXT NOT NULL DEFAULT 'medium',
                    keywords TEXT,  -- JSON array
                    monitoring_since TEXT NOT NULL,
                    last_checked TEXT,
                    metadata TEXT,  -- JSON object
                    domain TEXT,
                    description TEXT,
                    account_owner TEXT,
                    tier TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indices for clients
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_clients_name
                ON clients(name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_clients_priority
                ON clients(priority)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_clients_active
                ON clients(is_active)
            """)

            # Create events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT,
                    source_url TEXT,
                    source_name TEXT,
                    published_date TEXT NOT NULL,
                    discovered_date TEXT NOT NULL,
                    relevance_score REAL NOT NULL DEFAULT 0.5,
                    sentiment TEXT NOT NULL DEFAULT 'neutral',
                    sentiment_score REAL,
                    status TEXT NOT NULL DEFAULT 'new',
                    tags TEXT,  -- JSON array
                    user_notes TEXT,
                    metadata TEXT,  -- JSON object
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
                )
            """)

            # Create indices for events
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_client
                ON events(client_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_type
                ON events(event_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_published
                ON events(published_date DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_relevance
                ON events(relevance_score DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_status
                ON events(status)
            """)

            # Create search_cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_cache (
                    query_hash TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    api_source TEXT NOT NULL,
                    results TEXT NOT NULL,  -- JSON array
                    result_count INTEGER NOT NULL DEFAULT 0,
                    cached_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    metadata TEXT  -- JSON object
                )
            """)

            # Create index for cache expiry
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_expires
                ON search_cache(expires_at)
            """)

            # Create job_runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_runs (
                    id TEXT PRIMARY KEY,
                    job_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    status TEXT NOT NULL DEFAULT 'running',
                    results_summary TEXT,
                    error_message TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indices for job_runs
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_job_runs_name
                ON job_runs(job_name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_job_runs_start
                ON job_runs(start_time DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_job_runs_status
                ON job_runs(status)
            """)

            # Create notification_rules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_rules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    event_types TEXT,
                    min_relevance_score REAL NOT NULL DEFAULT 0.7,
                    client_ids TEXT,
                    keywords TEXT,
                    frequency TEXT NOT NULL DEFAULT 'immediate',
                    recipient_emails TEXT,
                    notification_type TEXT NOT NULL DEFAULT 'email',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    last_triggered TEXT,
                    trigger_count INTEGER NOT NULL DEFAULT 0
                )
            """)

            # Create indices for notification_rules
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notification_rules_active
                ON notification_rules(is_active)
            """)

            # Create notification_logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_logs (
                    id TEXT PRIMARY KEY,
                    rule_id TEXT,
                    rule_name TEXT NOT NULL,
                    notification_type TEXT NOT NULL DEFAULT 'email',
                    recipient TEXT NOT NULL,
                    subject TEXT,
                    content TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    error_message TEXT,
                    sent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    event_id TEXT
                )
            """)

            # Create indices for notification_logs
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notification_logs_sent_at
                ON notification_logs(sent_at DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notification_logs_status
                ON notification_logs(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notification_logs_rule_id
                ON notification_logs(rule_id)
            """)

            logger.info("Database schema initialized successfully")

    def drop_all_tables(self) -> None:
        """Drop all tables from database."""
        logger.warning("Dropping all tables from database!")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS events")
            cursor.execute("DROP TABLE IF EXISTS clients")
            cursor.execute("DROP TABLE IF NOT EXISTS search_cache")

            logger.info("All tables dropped")

    def get_database_info(self) -> Dict[str, Any]:
        """Get database information."""
        info = {
            "path": self.db_path,
            "exists": os.path.exists(self.db_path),
            "size_bytes": 0,
            "size_mb": 0,
            "tables": [],
        }

        if info["exists"]:
            info["size_bytes"] = os.path.getsize(self.db_path)
            info["size_mb"] = round(info["size_bytes"] / (1024 * 1024), 2)

            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                info["tables"] = [row[0] for row in cursor.fetchall()]

        return info

    # ==================== Client CRUD Operations ====================

    def create_client(self, client: ClientDTO) -> ClientDTO:
        """Create a new client record. Compatible with both INTEGER and TEXT id columns."""
        is_valid, error = client.validate()
        if not is_valid:
            raise ValueError(f"Invalid client: {error}")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if id column is INTEGER or TEXT
            cursor.execute("PRAGMA table_info(clients)")
            id_type = next((row[2] for row in cursor.fetchall() if row[1] == "id"), None)

            if id_type and "INT" in id_type.upper():
                # Old schema with INTEGER id - let database auto-generate
                # Also include created_at and updated_at for old schema
                try:
                    cursor.execute("""
                        INSERT INTO clients (
                            name, industry, priority, keywords,
                            monitoring_since, last_checked, metadata,
                            domain, description, account_owner, tier, is_active,
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        client.name,
                        client.industry,
                        client.priority,
                        json.dumps(client.keywords),
                        client.monitoring_since.isoformat(),
                        client.last_checked.isoformat() if client.last_checked else None,
                        json.dumps(client.metadata),
                        client.domain,
                        client.description,
                        client.account_owner,
                        client.tier,
                        1 if client.is_active else 0,
                        datetime.utcnow().isoformat(),  # created_at
                        datetime.utcnow().isoformat(),  # updated_at
                    ))
                    # Update client with auto-generated id
                    client.id = str(cursor.lastrowid)
                except sqlite3.Error as e:
                    logger.error(f"Failed to insert client. Error: {e}")
                    logger.error(f"Client data: name={client.name}, industry={client.industry}, priority={client.priority}")
                    raise
            else:
                # New schema with TEXT id - use provided UUID
                cursor.execute("""
                    INSERT INTO clients (
                        id, name, industry, priority, keywords,
                        monitoring_since, last_checked, metadata,
                        domain, description, account_owner, tier, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    client.id,
                    client.name,
                    client.industry,
                    client.priority,
                    json.dumps(client.keywords),
                    client.monitoring_since.isoformat(),
                    client.last_checked.isoformat() if client.last_checked else None,
                    json.dumps(client.metadata),
                    client.domain,
                    client.description,
                    client.account_owner,
                    client.tier,
                    1 if client.is_active else 0,
                ))

            logger.info(f"Created client: {client.name} ({client.id})")
            return client

    def get_client(self, client_id: str) -> Optional[ClientDTO]:
        """Retrieve a client by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_client(row)
            return None

    def get_all_clients(self, active_only: bool = True) -> List[ClientDTO]:
        """Retrieve all clients."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if active_only:
                cursor.execute("SELECT * FROM clients WHERE is_active = 1 ORDER BY name")
            else:
                cursor.execute("SELECT * FROM clients ORDER BY name")

            return [self._row_to_client(row) for row in cursor.fetchall()]

    def update_client(self, client_id: str, updates: Dict[str, Any]) -> Optional[ClientDTO]:
        """Update a client record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Build dynamic UPDATE query
            set_clauses = []
            values = []

            for key, value in updates.items():
                if key in ['keywords', 'metadata'] and isinstance(value, (list, dict)):
                    value = json.dumps(value)
                elif key in ['monitoring_since', 'last_checked'] and isinstance(value, datetime):
                    value = value.isoformat()
                elif key == 'is_active' and isinstance(value, bool):
                    value = 1 if value else 0

                set_clauses.append(f"{key} = ?")
                values.append(value)

            if not set_clauses:
                return self.get_client(client_id)

            # Add updated_at
            set_clauses.append("updated_at = ?")
            values.append(datetime.utcnow().isoformat())

            values.append(client_id)  # For WHERE clause

            query = f"UPDATE clients SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)

            if cursor.rowcount > 0:
                logger.info(f"Updated client: {client_id}")
                return self.get_client(client_id)
            return None

    def delete_client(self, client_id: str) -> bool:
        """Delete a client record and all associated events."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # First delete all events associated with this client
            cursor.execute("DELETE FROM events WHERE client_id = ?", (client_id,))
            events_deleted = cursor.rowcount

            # Then delete the client
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))

            if cursor.rowcount > 0:
                logger.info(f"Deleted client: {client_id} and {events_deleted} associated events")
                return True
            return False

    def search_clients(self, query: str) -> List[ClientDTO]:
        """Search clients by name or keywords."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_pattern = f"%{query}%"

            cursor.execute("""
                SELECT * FROM clients
                WHERE name LIKE ? OR keywords LIKE ?
                ORDER BY name
            """, (search_pattern, search_pattern))

            return [self._row_to_client(row) for row in cursor.fetchall()]

    # ==================== Event CRUD Operations ====================

    def create_event(self, event: EventDTO) -> EventDTO:
        """Create a new event record. Compatible with both INTEGER and TEXT id columns."""
        is_valid, error = event.validate()
        if not is_valid:
            raise ValueError(f"Invalid event: {error}")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if id column is INTEGER or TEXT
            cursor.execute("PRAGMA table_info(events)")
            id_type = next((row[2] for row in cursor.fetchall() if row[1] == "id"), None)

            if id_type and "INT" in id_type.upper():
                # Old schema with INTEGER id - let database auto-generate
                # Old schema also requires 'category' field (legacy from SQLAlchemy model)
                cursor.execute("""
                    INSERT INTO events (
                        client_id, category, event_type, title, summary,
                        source_url, source_name, published_date, discovered_date,
                        relevance_score, sentiment, sentiment_score, status,
                        tags, user_notes, metadata,
                        description, url, source, event_date, discovered_at, is_read, is_starred
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.client_id,
                    event.event_type,  # category = event_type for compatibility
                    event.event_type,
                    event.title,
                    event.summary,
                    event.source_url,
                    event.source_name,
                    event.published_date.isoformat(),
                    event.discovered_date.isoformat(),
                    event.relevance_score,
                    event.sentiment,
                    event.sentiment_score,
                    event.status,
                    json.dumps(event.tags),
                    event.user_notes,
                    json.dumps(event.metadata),
                    # Legacy fields for old schema compatibility
                    event.summary,  # description
                    event.source_url,  # url
                    event.source_name,  # source
                    event.published_date.isoformat(),  # event_date
                    event.discovered_date.isoformat(),  # discovered_at
                    0,  # is_read (False)
                    0,  # is_starred (False)
                ))
                # Update event with auto-generated id
                event.id = str(cursor.lastrowid)
            else:
                # New schema with TEXT id - use provided UUID
                cursor.execute("""
                    INSERT INTO events (
                        id, client_id, event_type, title, summary,
                        source_url, source_name, published_date, discovered_date,
                        relevance_score, sentiment, sentiment_score, status,
                        tags, user_notes, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.id,
                    event.client_id,
                    event.event_type,
                    event.title,
                    event.summary,
                    event.source_url,
                    event.source_name,
                    event.published_date.isoformat(),
                    event.discovered_date.isoformat(),
                    event.relevance_score,
                    event.sentiment,
                    event.sentiment_score,
                    event.status,
                    json.dumps(event.tags),
                    event.user_notes,
                    json.dumps(event.metadata),
                ))

            logger.info(f"Created event: {event.title[:50]}... ({event.id})")
            return event

    def get_event(self, event_id: str) -> Optional[EventDTO]:
        """Retrieve an event by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_event(row)
            return None

    def get_events_by_client(
        self,
        client_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[EventDTO]:
        """Retrieve events for a specific client."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM events
                WHERE client_id = ?
                ORDER BY published_date DESC
                LIMIT ? OFFSET ?
            """, (client_id, limit, offset))

            return [self._row_to_event(row) for row in cursor.fetchall()]

    def get_recent_events(
        self,
        days: int = 7,
        min_relevance: float = 0.0,
        limit: int = 100
    ) -> List[EventDTO]:
        """Retrieve recent events across all clients."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            since_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

            cursor.execute("""
                SELECT * FROM events
                WHERE published_date >= ? AND relevance_score >= ?
                ORDER BY published_date DESC
                LIMIT ?
            """, (since_date, min_relevance, limit))

            return [self._row_to_event(row) for row in cursor.fetchall()]

    def get_all_events(self) -> List[EventDTO]:
        """Retrieve all events from the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM events
                ORDER BY published_date DESC
            """)
            return [self._row_to_event(row) for row in cursor.fetchall()]

    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Optional[EventDTO]:
        """Update an event record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Build dynamic UPDATE query
            set_clauses = []
            values = []

            for key, value in updates.items():
                if key in ['tags', 'metadata'] and isinstance(value, (list, dict)):
                    value = json.dumps(value)
                elif key in ['published_date', 'discovered_date'] and isinstance(value, datetime):
                    value = value.isoformat()

                set_clauses.append(f"{key} = ?")
                values.append(value)

            if not set_clauses:
                return self.get_event(event_id)

            values.append(event_id)  # For WHERE clause

            query = f"UPDATE events SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)

            if cursor.rowcount > 0:
                logger.info(f"Updated event: {event_id}")
                return self.get_event(event_id)
            return None

    def delete_event(self, event_id: str) -> bool:
        """Delete an event record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))

            if cursor.rowcount > 0:
                logger.info(f"Deleted event: {event_id}")
                return True
            return False

    def search_events(
        self,
        query: str,
        client_id: Optional[str] = None
    ) -> List[EventDTO]:
        """Search events by title or summary."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_pattern = f"%{query}%"

            if client_id:
                cursor.execute("""
                    SELECT * FROM events
                    WHERE client_id = ? AND (title LIKE ? OR summary LIKE ?)
                    ORDER BY published_date DESC
                """, (client_id, search_pattern, search_pattern))
            else:
                cursor.execute("""
                    SELECT * FROM events
                    WHERE title LIKE ? OR summary LIKE ?
                    ORDER BY published_date DESC
                """, (search_pattern, search_pattern))

            return [self._row_to_event(row) for row in cursor.fetchall()]

    # ==================== Cache CRUD Operations ====================

    def create_cache(self, cache: SearchCacheDTO) -> SearchCacheDTO:
        """Create a new cache entry."""
        is_valid, error = cache.validate()
        if not is_valid:
            raise ValueError(f"Invalid cache: {error}")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO search_cache (
                    query_hash, query, api_source, results, result_count,
                    cached_at, expires_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cache.query_hash,
                cache.query,
                cache.api_source,
                json.dumps(cache.results),
                cache.result_count,
                cache.cached_at.isoformat(),
                cache.expires_at.isoformat(),
                json.dumps(cache.metadata),
            ))

            logger.info(f"Created cache entry: {cache.query_hash[:16]}...")
            return cache

    def get_cache(self, query_hash: str) -> Optional[SearchCacheDTO]:
        """Retrieve cache entry by query hash."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM search_cache
                WHERE query_hash = ? AND expires_at > ?
            """, (query_hash, datetime.utcnow().isoformat()))

            row = cursor.fetchone()
            if row:
                return self._row_to_cache(row)
            return None

    def delete_expired_cache(self) -> int:
        """Delete all expired cache entries."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM search_cache
                WHERE expires_at <= ?
            """, (datetime.utcnow().isoformat(),))

            count = cursor.rowcount
            if count > 0:
                logger.info(f"Deleted {count} expired cache entries")
            return count

    def clear_all_cache(self) -> int:
        """Delete all cache entries."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM search_cache")
            count = cursor.rowcount
            logger.info(f"Cleared all cache ({count} entries)")
            return count

    # ==================== Statistics & Analytics ====================

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics. Compatible with both old and new schemas."""
        stats = {}

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check which columns exist in events table
            cursor.execute("PRAGMA table_info(events)")
            event_columns = {row[1] for row in cursor.fetchall()}

            # Determine which date column to use (old: event_date, new: published_date)
            date_column = "published_date" if "published_date" in event_columns else "event_date"

            # Determine if status column exists
            has_status = "status" in event_columns

            # Client stats
            cursor.execute("SELECT COUNT(*) FROM clients WHERE is_active = 1")
            stats["active_clients"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM clients")
            stats["total_clients"] = cursor.fetchone()[0]

            # Event stats
            cursor.execute("SELECT COUNT(*) FROM events")
            stats["total_events"] = cursor.fetchone()[0]

            # New events count (only if status column exists)
            if has_status:
                cursor.execute("""
                    SELECT COUNT(*) FROM events
                    WHERE status = 'new'
                """)
                stats["new_events"] = cursor.fetchone()[0]
            else:
                # Fallback: use is_read if status doesn't exist
                cursor.execute("""
                    SELECT COUNT(*) FROM events
                    WHERE is_read = 0
                """)
                stats["new_events"] = cursor.fetchone()[0]

            # Recent events (last 7 days)
            cursor.execute(f"""
                SELECT COUNT(*) FROM events
                WHERE {date_column} >= ?
            """, ((datetime.utcnow() - timedelta(days=7)).isoformat(),))
            stats["events_last_7_days"] = cursor.fetchone()[0]

            # Cache stats
            cursor.execute("SELECT COUNT(*) FROM search_cache")
            stats["total_cache_entries"] = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM search_cache
                WHERE expires_at > ?
            """, (datetime.utcnow().isoformat(),))
            stats["valid_cache_entries"] = cursor.fetchone()[0]

        return stats

    def get_client_statistics(self, client_id: str) -> Dict[str, Any]:
        """Get statistics for a specific client."""
        stats = {}

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Total events
            cursor.execute("""
                SELECT COUNT(*) FROM events WHERE client_id = ?
            """, (client_id,))
            stats["total_events"] = cursor.fetchone()[0]

            # Events by status
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM events
                WHERE client_id = ?
                GROUP BY status
            """, (client_id,))
            stats["events_by_status"] = {row[0]: row[1] for row in cursor.fetchall()}

            # Events by type
            cursor.execute("""
                SELECT event_type, COUNT(*) as count
                FROM events
                WHERE client_id = ?
                GROUP BY event_type
            """, (client_id,))
            stats["events_by_type"] = {row[0]: row[1] for row in cursor.fetchall()}

            # Average relevance
            cursor.execute("""
                SELECT AVG(relevance_score)
                FROM events
                WHERE client_id = ?
            """, (client_id,))
            avg_relevance = cursor.fetchone()[0]
            stats["average_relevance"] = round(avg_relevance, 2) if avg_relevance else 0.0

        return stats

    # ==================== Helper Methods ====================

    def _row_to_client(self, row: sqlite3.Row) -> ClientDTO:
        """Convert database row to ClientDTO."""
        return ClientDTO(
            id=row["id"],
            name=row["name"],
            industry=row["industry"],
            priority=row["priority"],
            keywords=json.loads(row["keywords"]) if row["keywords"] else [],
            monitoring_since=datetime.fromisoformat(row["monitoring_since"]),
            last_checked=datetime.fromisoformat(row["last_checked"]) if row["last_checked"] else None,
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            domain=row["domain"],
            description=row["description"],
            account_owner=row["account_owner"],
            tier=row["tier"],
            is_active=bool(row["is_active"]),
        )

    def _row_to_event(self, row: sqlite3.Row) -> EventDTO:
        """Convert database row to EventDTO."""
        return EventDTO(
            id=row["id"],
            client_id=row["client_id"],
            event_type=row["event_type"],
            title=row["title"],
            summary=row["summary"],
            source_url=row["source_url"],
            source_name=row["source_name"],
            published_date=datetime.fromisoformat(row["published_date"]),
            discovered_date=datetime.fromisoformat(row["discovered_date"]),
            relevance_score=row["relevance_score"],
            sentiment=row["sentiment"],
            sentiment_score=row["sentiment_score"],
            status=row["status"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            user_notes=row["user_notes"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )

    def _row_to_cache(self, row: sqlite3.Row) -> SearchCacheDTO:
        """Convert database row to SearchCacheDTO."""
        return SearchCacheDTO(
            query=row["query"],
            api_source=row["api_source"],
            results=json.loads(row["results"]) if row["results"] else [],
            cached_at=datetime.fromisoformat(row["cached_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]),
            result_count=row["result_count"],
            query_hash=row["query_hash"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )

    # ==================== Job Run Operations ====================

    def create_job_run(self, job_run) -> None:
        """Create a new job run record."""
        from src.models.job_run import JobRun

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO job_runs (
                    id, job_name, start_time, end_time, status,
                    results_summary, error_message, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_run.id,
                job_run.job_name,
                job_run.start_time.isoformat(),
                job_run.end_time.isoformat() if job_run.end_time else None,
                job_run.status,
                job_run.results_summary,
                job_run.error_message,
                json.dumps(job_run.metadata),
            ))
            logger.info(f"Created job run: {job_run.id} for job {job_run.job_name}")

    def update_job_run(self, job_run) -> None:
        """Update an existing job run record."""
        from src.models.job_run import JobRun

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE job_runs
                SET end_time = ?, status = ?, results_summary = ?,
                    error_message = ?, metadata = ?
                WHERE id = ?
            """, (
                job_run.end_time.isoformat() if job_run.end_time else None,
                job_run.status,
                job_run.results_summary,
                job_run.error_message,
                json.dumps(job_run.metadata),
                job_run.id,
            ))
            logger.info(f"Updated job run: {job_run.id} with status {job_run.status}")

    def get_job_run(self, job_run_id: str):
        """Get a specific job run by ID."""
        from src.models.job_run import JobRun

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM job_runs WHERE id = ?", (job_run_id,))
            row = cursor.fetchone()

            if row:
                return JobRun(
                    id=row["id"],
                    job_name=row["job_name"],
                    start_time=datetime.fromisoformat(row["start_time"]),
                    end_time=datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
                    status=row["status"],
                    results_summary=row["results_summary"],
                    error_message=row["error_message"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                )
            return None

    def get_recent_job_runs(self, job_name: Optional[str] = None, limit: int = 50):
        """Get recent job runs, optionally filtered by job name."""
        from src.models.job_run import JobRun

        with self.get_connection() as conn:
            cursor = conn.cursor()

            if job_name:
                cursor.execute("""
                    SELECT * FROM job_runs
                    WHERE job_name = ?
                    ORDER BY start_time DESC
                    LIMIT ?
                """, (job_name, limit))
            else:
                cursor.execute("""
                    SELECT * FROM job_runs
                    ORDER BY start_time DESC
                    LIMIT ?
                """, (limit,))

            runs = []
            for row in cursor.fetchall():
                runs.append(JobRun(
                    id=row["id"],
                    job_name=row["job_name"],
                    start_time=datetime.fromisoformat(row["start_time"]),
                    end_time=datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
                    status=row["status"],
                    results_summary=row["results_summary"],
                    error_message=row["error_message"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                ))

            return runs

    def get_job_stats(self):
        """Get statistics about job runs."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Total runs
            cursor.execute("SELECT COUNT(*) as total FROM job_runs")
            total = cursor.fetchone()["total"]

            # Runs by status
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM job_runs
                GROUP BY status
            """)
            by_status = {row["status"]: row["count"] for row in cursor.fetchall()}

            # Runs by job name
            cursor.execute("""
                SELECT job_name, COUNT(*) as count
                FROM job_runs
                GROUP BY job_name
            """)
            by_job = {row["job_name"]: row["count"] for row in cursor.fetchall()}

            # Recent failures
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM job_runs
                WHERE status = 'failed'
                AND start_time >= datetime('now', '-7 days')
            """)
            recent_failures = cursor.fetchone()["count"]

            return {
                "total": total,
                "by_status": by_status,
                "by_job": by_job,
                "recent_failures": recent_failures,
            }

    # Notification Rules CRUD operations

    def create_notification_rule(self, rule) -> None:
        """Create a new notification rule."""
        from src.models.notification_rule import NotificationRule

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notification_rules (
                    id, name, description, is_active, event_types,
                    min_relevance_score, client_ids, keywords, frequency,
                    recipient_emails, notification_type, created_at,
                    updated_at, last_triggered, trigger_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule.id,
                rule.name,
                rule.description,
                1 if rule.is_active else 0,
                json.dumps(rule.event_types),
                rule.min_relevance_score,
                json.dumps(rule.client_ids),
                json.dumps(rule.keywords),
                rule.frequency,
                json.dumps(rule.recipient_emails),
                rule.notification_type,
                rule.created_at.isoformat(),
                rule.updated_at.isoformat(),
                rule.last_triggered.isoformat() if rule.last_triggered else None,
                rule.trigger_count,
            ))
            logger.info(f"Created notification rule: {rule.id}")

    def update_notification_rule(self, rule) -> None:
        """Update an existing notification rule."""
        from src.models.notification_rule import NotificationRule

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE notification_rules
                SET name = ?, description = ?, is_active = ?,
                    event_types = ?, min_relevance_score = ?,
                    client_ids = ?, keywords = ?, frequency = ?,
                    recipient_emails = ?, notification_type = ?,
                    updated_at = ?, last_triggered = ?, trigger_count = ?
                WHERE id = ?
            """, (
                rule.name,
                rule.description,
                1 if rule.is_active else 0,
                json.dumps(rule.event_types),
                rule.min_relevance_score,
                json.dumps(rule.client_ids),
                json.dumps(rule.keywords),
                rule.frequency,
                json.dumps(rule.recipient_emails),
                rule.notification_type,
                rule.updated_at.isoformat(),
                rule.last_triggered.isoformat() if rule.last_triggered else None,
                rule.trigger_count,
                rule.id,
            ))
            logger.info(f"Updated notification rule: {rule.id}")

    def get_notification_rule(self, rule_id: str):
        """Get a specific notification rule by ID."""
        from src.models.notification_rule import NotificationRule

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM notification_rules WHERE id = ?
            """, (rule_id,))

            row = cursor.fetchone()
            if row:
                return self._row_to_notification_rule(row)
            return None

    def get_all_notification_rules(self, active_only: bool = False):
        """Get all notification rules."""
        from src.models.notification_rule import NotificationRule

        with self.get_connection() as conn:
            cursor = conn.cursor()

            if active_only:
                cursor.execute("""
                    SELECT * FROM notification_rules
                    WHERE is_active = 1
                    ORDER BY name
                """)
            else:
                cursor.execute("""
                    SELECT * FROM notification_rules
                    ORDER BY name
                """)

            return [self._row_to_notification_rule(row) for row in cursor.fetchall()]

    def delete_notification_rule(self, rule_id: str) -> None:
        """Delete a notification rule."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM notification_rules WHERE id = ?
            """, (rule_id,))
            logger.info(f"Deleted notification rule: {rule_id}")

    def _row_to_notification_rule(self, row: sqlite3.Row):
        """Convert database row to NotificationRule object."""
        from src.models.notification_rule import NotificationRule

        return NotificationRule(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            is_active=bool(row["is_active"]),
            event_types=json.loads(row["event_types"]) if row["event_types"] else [],
            min_relevance_score=row["min_relevance_score"],
            client_ids=json.loads(row["client_ids"]) if row["client_ids"] else [],
            keywords=json.loads(row["keywords"]) if row["keywords"] else [],
            frequency=row["frequency"],
            recipient_emails=json.loads(row["recipient_emails"]) if row["recipient_emails"] else [],
            notification_type=row["notification_type"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            last_triggered=datetime.fromisoformat(row["last_triggered"]) if row["last_triggered"] else None,
            trigger_count=row["trigger_count"],
        )

    # Notification Logs CRUD operations

    def create_notification_log(self, log) -> None:
        """Create a new notification log entry."""
        from src.models.notification_log import NotificationLog

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notification_logs (
                    id, rule_id, rule_name, notification_type, recipient,
                    subject, content, status, error_message, sent_at, event_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log.id,
                log.rule_id,
                log.rule_name,
                log.notification_type,
                log.recipient,
                log.subject,
                log.content,
                log.status,
                log.error_message,
                log.sent_at.isoformat(),
                log.event_id,
            ))
            logger.info(f"Created notification log: {log.id}")

    def get_notification_logs(self, limit: int = 100, rule_id: str = None, status: str = None):
        """Get notification logs with optional filters."""
        from src.models.notification_log import NotificationLog

        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM notification_logs WHERE 1=1"
            params = []

            if rule_id:
                query += " AND rule_id = ?"
                params.append(rule_id)

            if status:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY sent_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [self._row_to_notification_log(row) for row in cursor.fetchall()]

    def get_notification_log(self, log_id: str):
        """Get a specific notification log by ID."""
        from src.models.notification_log import NotificationLog

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM notification_logs WHERE id = ?
            """, (log_id,))

            row = cursor.fetchone()
            if row:
                return self._row_to_notification_log(row)
            return None

    def _row_to_notification_log(self, row: sqlite3.Row):
        """Convert database row to NotificationLog object."""
        from src.models.notification_log import NotificationLog

        return NotificationLog(
            id=row["id"],
            rule_id=row["rule_id"],
            rule_name=row["rule_name"],
            notification_type=row["notification_type"],
            recipient=row["recipient"],
            subject=row["subject"] or "",
            content=row["content"] or "",
            status=row["status"],
            error_message=row["error_message"],
            sent_at=datetime.fromisoformat(row["sent_at"]),
            event_id=row["event_id"],
        )
