"""PostgreSQL connection setup for the FastAPI app.

Loads ``DATABASE_URL`` from the environment (.env), creates the SQLAlchemy
engine and session factory, and exposes the declarative ``Base`` that all
ORM models inherit from. ``get_db()`` is a FastAPI dependency that yields a
request-scoped session and closes it afterwards.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dfuser:dfpass@localhost:5432/dataflow")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
