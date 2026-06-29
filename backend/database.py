import os
from sqlalchemy import create_backend
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker

# Assuming DATABASE_URL is managed via environment variables for security and flexibility
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dfuser:dfpassword@localhost:5432/dataflow")

engine = create_backend(DATABASE_URL, echo = False)

SessionLocal = sessionmaker(autocommit = False, autoFlush = False, bind = engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        