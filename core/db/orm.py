import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from core.db.session import Base
from core.models.enums import RunStatus


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Automation(Base):
    """Stored goal and dynamic execution plan."""
    __tablename__ = "automations"

    id = Column(String, primary_key=True, default=_uuid)
    raw_goal = Column(Text, nullable=False)
    plan = Column(JSON, nullable=False)  # stores serialized ExecutionPlan
    created_at = Column(DateTime(timezone=True), default=_now)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    active = Column(Boolean, default=True)

    runs = relationship("Run", back_populates="automation", cascade="all, delete-orphan")


class Run(Base):
    """A single execution of an autonomous web-data automation."""
    __tablename__ = "runs"

    id = Column(String, primary_key=True, default=_uuid)
    automation_id = Column(String, ForeignKey("automations.id"), nullable=False)
    status = Column(Enum(RunStatus), default=RunStatus.pending, nullable=False)
    started_at = Column(DateTime(timezone=True), default=_now)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    # Verification and provenance audit trail
    sources_found = Column(JSON, nullable=True)        # list of discovered source URLs
    pages_retrieved = Column(JSON, nullable=True)      # list of successfully retrieved URLs
    extracted_count = Column(Integer, default=0)
    validated_count = Column(Integer, default=0)
    condition_matched = Column(Boolean, nullable=True) # whether user condition was triggered
    condition_message = Column(Text, nullable=True)    # summary of condition evaluation
    reasoning_log = Column(JSON, nullable=True)        # self-correction/agent decision log
    error = Column(Text, nullable=True)

    automation = relationship("Automation", back_populates="runs")
    results = relationship("Result", back_populates="run", cascade="all, delete-orphan")


class Result(Base):
    """A single extracted and validated record with dynamic domain-agnostic JSON payload."""
    __tablename__ = "results"

    id = Column(String, primary_key=True, default=_uuid)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)

    url = Column(Text, nullable=True)
    data = Column(JSON, nullable=False, default=dict)  # domain-agnostic extracted fields

    valid = Column(Boolean, default=False)
    validation_errors = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)

    run = relationship("Run", back_populates="results")
