import os
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import Column, Integer, DateTime, String, JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _resolve_database_url() -> str:
    explicit = os.getenv("DATABASE_URL")
    if explicit:
        return explicit

    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return "sqlite+aiosqlite:////tmp/mediguard.db"

    # Test if current directory is writable for SQLite
    try:
        test_path = Path("./.write_test_mediguard")
        test_path.touch()
        test_path.unlink()
        return "sqlite+aiosqlite:///./mediguard.db"
    except Exception:
        return "sqlite+aiosqlite:////tmp/mediguard.db"


DATABASE_URL = _resolve_database_url()

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class VitalsRecord(Base):
    __tablename__ = "vitals_records"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True)
    vitals = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SepsisAlertRecord(Base):
    __tablename__ = "sepsis_alerts"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True)
    qsofa_score = Column(Integer, nullable=True)
    result = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PrescriptionRecord(Base):
    __tablename__ = "prescriptions"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True)
    doctor_name = Column(String, nullable=True)
    prescription = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class InteractionResultRecord(Base):
    __tablename__ = "interaction_results"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True)
    risk_level = Column(String, nullable=True)
    result = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


async def init_db():
    """Create tables on startup if they don't exist yet."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session