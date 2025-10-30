"""Database connection and session management."""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import settings
from src.models.client import Base


class Database:
    """Database manager with connection pooling and session management."""

    def __init__(self, database_url: str = None):
        """
        Initialize database connection.

        Args:
            database_url: Database URL. If None, uses settings.database_url
        """
        self.database_url = database_url or settings.database_url

        # Create engine with SQLite-specific settings
        connect_args = {}
        if self.database_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}

        self.engine = create_engine(
            self.database_url,
            connect_args=connect_args,
            echo=settings.debug,  # Log SQL queries in debug mode
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all tables from the database. USE WITH CAUTION!"""
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.

        Usage:
            with db.get_session() as session:
                client = session.query(Client).first()

        Yields:
            SQLAlchemy Session object
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_session_direct(self) -> Session:
        """
        Get a session directly (caller responsible for closing).

        Returns:
            SQLAlchemy Session object
        """
        return self.SessionLocal()


# Global database instance
db = Database()
