from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

db = create_engine("sqlite:///mensuração-crm.db")

Session = sessionmaker(bind=db)

Base = declarative_base()