from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.config import get_settings
from app.models.base import Base

settings = get_settings()
database_path = Path(settings.sqlite_db_path)
database_url = settings.database_url or f"sqlite:///{database_path}"
engine = create_engine(database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
metadata = Base.metadata


if database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[no-redef]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()


def get_db_session() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
