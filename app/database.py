import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///campagain_tenda.db")

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
	engine_kwargs["connect_args"] = {"check_same_thread": False}

db = create_engine(DATABASE_URL, future=True, **engine_kwargs)

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