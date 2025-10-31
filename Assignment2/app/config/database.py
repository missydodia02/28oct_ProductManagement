# app/config/database.py
"""
Database connection module using Prisma client.

Purpose:
- Create a single Prisma client instance that the whole app re-uses.
- Provide lifecycle helpers to connect/disconnect Prisma when FastAPI starts/stops.
- Provide a simple dependency (get_db) to access the Prisma client inside routes/services.

Java comparison:
- This is like creating a single Hibernate SessionFactory or a Spring-managed DataSource/EntityManager
  and exposing it via dependency injection.
"""

from prisma import Prisma
from typing import Generator

# Create Prisma client instance (singleton for the app)
# In Java: like "private static final SessionFactory sessionFactory = ..."
prisma = Prisma()


async def connect_db() -> None:
    """
    Connect Prisma client to the database.
    This should be called during application startup (FastAPI @app.on_event("startup")).

    Java comparison:
    - Similar to opening a pooled DataSource or initializing Hibernate's SessionFactory.
    """
    await prisma.connect()
    
    print("Prisma client connected to DB.")


async def disconnect_db() -> None:
    """
    Disconnect Prisma client from the database.
    This should be called during application shutdown (FastAPI @app.on_event("shutdown")).

    Java comparison:
    - Similar to closing DataSource connections or destroying the SessionFactory at shutdown.
    """
    await prisma.disconnect()
    print(" Prisma client disconnected from DB.")


def get_db() -> Prisma:
    """
    Dependency to return the Prisma client.
    Use this in FastAPI routes like: db: Prisma = Depends(get_db)

    Notes:
    - Prisma client is asynchronous but can be used from sync routes as well through the generated
      sync wrappers (depending on the prisma version). For simplicity we return the client directly.
    - If you need per-request transactional sessions, we will create functions to begin/commit/rollback
      transactions in service layer (we'll add that later if required).
    """
    return prisma


# from sqlalchemy import create_engine                 # To create DB engine
# from sqlalchemy.ext.declarative import declarative_base  # Base class for model classes
# from sqlalchemy.orm import sessionmaker               # Factory for DB sessions
# from dotenv import load_dotenv                        # To load .env file
# import os

# # Load variables from .env file located at project root
# load_dotenv()

# # Read DATABASE_URL environment variable (e.g. postgresql://user:pw@host:port/dbname)
# DATABASE_URL = os.getenv("DATABASE_URL")

# # Create SQLAlchemy engine. Echo=False to avoid SQL logs (set True for debug)
# engine = create_engine(DATABASE_URL, echo=False)

# # Create a configured "Session" class
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Base class that our ORM models will inherit from
# Base = declarative_base()

# # Dependency function for FastAPI to get DB session per request
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
