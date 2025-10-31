# app/config/database.py
#databse connectivity Engin Base session load
from sqlalchemy import create_engine                 # To create DB engine
from sqlalchemy.ext.declarative import declarative_base  # Base class for model classes
from sqlalchemy.orm import sessionmaker               # Factory for DB sessions
from dotenv import load_dotenv                        # To load .env file
import os

# Load variables from .env file located at project root
load_dotenv()

# Read DATABASE_URL environment variable (e.g. postgresql://user:pw@host:port/dbname)
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine. Echo=False to avoid SQL logs (set True for debug)
engine = create_engine(DATABASE_URL, echo=False)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that our ORM models will inherit from
Base = declarative_base()

# Dependency function for FastAPI to get DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
