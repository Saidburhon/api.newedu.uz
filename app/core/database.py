from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings

# Create engine with connection pool and timeout settings optimized for PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,  # Number of connections to keep open
    max_overflow=20,  # Max connections beyond pool_size
    pool_timeout=30,  # Seconds to wait before timing out
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Check connection validity before using
    connect_args={
        'connect_timeout': 60,  # Connection timeout in seconds
        'application_name': 'newedu_api'  # Identifies the application in PostgreSQL logs
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
