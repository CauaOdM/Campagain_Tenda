import os
import tempfile
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker


DEFAULT_DB_PATH = Path(tempfile.gettempdir()) / "campagain_tenda.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DB_PATH}"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

engine_kwargs = {
    "future": True,
    "pool_pre_ping": True,
}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {
        "check_same_thread": False,
        "timeout": 30,
    }

db = create_engine(DATABASE_URL, **engine_kwargs)


if DATABASE_URL.startswith("sqlite"):

    @event.listens_for(db, "connect")
    def configure_sqlite_connection(connection, _):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA busy_timeout = 30000")
        cursor.execute("PRAGMA journal_mode = WAL")
        cursor.close()


Session = sessionmaker(
    bind=db,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)

Base = declarative_base()


def get_session():
    return Session()