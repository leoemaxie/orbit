import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, JSON, Enum, Numeric, Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


def _uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc)


class RunStatus(str, enum.Enum):
    pending = "pending"
    discovering = "discovering"
    retrieving = "retrieving"
    extracting = "extracting"
    validating = "validating"
    storing = "storing"
    verified = "verified"
    failed = "failed"


class Automation(Base):
    """The stored automation spec derived from a natural-language goal."""
    __tablename__ = "automations"

    id = Column(String, primary_key=True, default=_uuid)
    raw_goal = Column(Text, nullable=False)
    spec = Column(JSON, nullable=False)  # structured automation specification
    created_at = Column(DateTime(timezone=True), default=_now)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    active = Column(Boolean, default=True)

    runs = relationship("Run", back_populates="automation", cascade="all, delete-orphan")


class Run(Base):
    """A single execution of an automation."""
    __tablename__ = "runs"

    id = Column(String, primary_key=True, default=_uuid)
    automation_id = Column(String, ForeignKey("automations.id"), nullable=False)
    status = Column(Enum(RunStatus), default=RunStatus.pending, nullable=False)
    started_at = Column(DateTime(timezone=True), default=_now)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    # verification checklist, filled in as the run progresses
    sources_found = Column(JSON, nullable=True)      # list of discovered URLs
    pages_retrieved = Column(JSON, nullable=True)     # list of URLs successfully fetched
    extracted_count = Column(String, nullable=True)
    validated_count = Column(String, nullable=True)
    error = Column(Text, nullable=True)

    automation = relationship("Automation", back_populates="runs")
    results = relationship("Result", back_populates="run", cascade="all, delete-orphan")


class Result(Base):
    """A single extracted + validated record from one run."""
    __tablename__ = "results"

    id = Column(String, primary_key=True, default=_uuid)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)

    product = Column(String, nullable=True)
    price = Column(Numeric, nullable=True)
    currency = Column(String, nullable=True)
    availability = Column(String, nullable=True)
    seller = Column(String, nullable=True)
    url = Column(Text, nullable=True)

    valid = Column(Boolean, default=False)
    validation_errors = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=_now)

    run = relationship("Run", back_populates="results")
