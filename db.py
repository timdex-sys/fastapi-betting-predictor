from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os

# Get database URL from environment (Railway / Neon / local SQLite)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")

# Handle connection args for SQLite vs Postgres
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# SQLAlchemy session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency to provide a session per request in FastAPI routes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Optional: Initialize tables (run once manually)
if __name__ == "__main__":
    from models_db import Base
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully.")
    except SQLAlchemyError as e:
        print(f"❌ Error creating tables: {e}")
