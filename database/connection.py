"""
database/connection.py
Engine/session factory. SQLite-by-default so `streamlit run streamlit_app.py`
works with zero external services; set DATABASE_URL to a
PostgreSQL+PostGIS DSN in .env for production deployments.
"""
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from core.logging_config import get_logger

logger = get_logger(__name__)

_connect_args = {"check_same_thread": False} if Config.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    Config.DATABASE_URL,
    connect_args=_connect_args,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@contextmanager
def get_session():
    """Context-managed session: `with get_session() as db: ...`"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        logger.exception("Database session rolled back due to error")
        raise
    finally:
        session.close()
