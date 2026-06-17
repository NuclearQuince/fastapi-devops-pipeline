import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL is read from the environment. Locally it falls back to SQLite
# so the app can run without needing a real Postgres instance.
# In production (Render), this will be set to the Postgres connection string.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")

# The engine manages the actual connection pool to the database.
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory for creating new database sessions.
# Each request gets its own session via the get_db() dependency below.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class all our ORM models (like RequestLog) inherit from.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per request.
    Ensures the session is always closed after the request finishes,
    even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
