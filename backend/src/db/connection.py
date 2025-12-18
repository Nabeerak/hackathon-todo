"""Database connection and session management."""
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator

from ..config import settings


# Create database engine with connection pooling
engine = create_engine(
    settings.database_url,
    echo=settings.environment == "development",
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Number of connections to maintain
    max_overflow=10,  # Max additional connections when pool is full
)


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Get database session with automatic commit/rollback.

    Usage:
        with get_session() as session:
            user = session.get(User, user_id)
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db_session() -> Session:
    """
    Get database session for dependency injection.

    Usage with FastAPI:
        @app.get("/users")
        def get_users(session: Session = Depends(get_db_session)):
            ...
    """
    with get_session() as session:
        yield session
