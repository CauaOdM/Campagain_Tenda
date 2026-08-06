import os
import tempfile
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool


SQLITE_DIR = Path(tempfile.gettempdir()) / "campagain_tenda"
SQLITE_DIR.mkdir(parents=True, exist_ok=True)

SQLITE_PATH = SQLITE_DIR / "campagain_tenda.db"
DEFAULT_DATABASE_URL = f"sqlite:///{SQLITE_PATH}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL).strip()

engine_kwargs = {
    "future": True,
    "pool_pre_ping": True,
}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update(
        {
            "connect_args": {
                "check_same_thread": False,
                "timeout": 30,
            },
            # Evita reaproveitar conexões ligadas a um arquivo temporário antigo.
            "poolclass": NullPool,
        }
    )

db = create_engine(DATABASE_URL, **engine_kwargs)


if DATABASE_URL.startswith("sqlite"):

    @event.listens_for(db, "connect")
    def configure_sqlite_connection(connection, _):
        cursor = connection.cursor()
        cursor.execute("PRAGMA busy_timeout = 30000")
        cursor.execute("PRAGMA foreign_keys = ON")
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
