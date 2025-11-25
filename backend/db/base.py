"""
Database base configuration using SQLModel.
"""
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager

import config

# Create engine with SQLite
connect_args = {"check_same_thread": False}  # Needed for SQLite
engine = create_engine(
    config.DATABASE_URL,
    echo=config.DEBUG,
    connect_args=connect_args
)


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency for getting database sessions."""
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_context() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    with Session(engine) as session:
        yield session
