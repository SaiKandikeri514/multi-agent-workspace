import os
import logging
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
import datetime

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)

class InternalCRM(Base):
    __tablename__ = "internal_crm"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, unique=True, index=True)
    sla_level = Column(String)
    status = Column(String)

# Database connection logic
connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")

if connection_name:
    # Use Cloud SQL / PostgreSQL setup
    logger.info(f"Connecting to Postgres Cloud SQL instance: {connection_name}")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASS", "password")
    db_name = os.environ.get("DB_NAME", "postgres")
    # A generic implementation, to be replaced by asyncpg or connector if running strictly on GCP.
    db_url = f"postgresql+psycopg2://{user}:{password}@/{db_name}?host=/cloudsql/{connection_name}"
    engine = create_engine(db_url)
else:
    # Graceful fallback to local SQLite for test/demo mode
    logger.warning("No Cloud SQL config found. Falling back to local SQLite.")
    engine = create_engine("sqlite:///./hackathon.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
