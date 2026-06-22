"""
Core database models.
Every table in the platform lives here (or imports Base from here).
"""
from datetime import datetime
from sqlalchemy import (
    String, Text, Integer, Float, Boolean, DateTime,
    ForeignKey, JSON, Enum as PgEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.session import Base


# ─── Enums ────────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    admin  = "admin"
    manager = "manager"
    sales  = "sales"
    viewer = "viewer"


class ServiceType(str, enum.Enum):
    solidworks_license = "solidworks_license"
    other_license      = "other_license"
    training           = "training"


class LeadStatus(str, enum.Enum):
    new        = "new"
    qualified  = "qualified"
    contacted  = "contacted"
    converted  = "converted"
    lost       = "lost"


# ─── Users & RBAC ─────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id:            Mapped[int]      = mapped_column(Integer, primary_key=True)
    email:         Mapped[str]      = mapped_column(String(255), unique=True, index=True)
    full_name:     Mapped[str]      = mapped_column(String(255))
    hashed_pw:     Mapped[str]      = mapped_column(String(255))
    role:          Mapped[UserRole] = mapped_column(PgEnum(UserRole), default=UserRole.viewer)
    is_active:     Mapped[bool]     = mapped_column(Boolean, default=True)
    # JSON column: {"leads": "read", "scores": "read", "admin": "none", ...}
    permissions:   Mapped[dict]     = mapped_column(JSON, default=dict)
    created_at:    Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ─── Leads (companies) ────────────────────────────────────────────────────────

class Lead(Base):
    __tablename__ = "leads"

    id:              Mapped[int]        = mapped_column(Integer, primary_key=True)
    company_name:    Mapped[str]        = mapped_column(String(255), index=True)
    website:         Mapped[str | None] = mapped_column(String(500))
    linkedin_url:    Mapped[str | None] = mapped_column(String(500))
    country:         Mapped[str | None] = mapped_column(String(100))
    city:            Mapped[str | None] = mapped_column(String(100))
    sector:          Mapped[str | None] = mapped_column(String(200))
    employee_count:  Mapped[int | None] = mapped_column(Integer)
    is_multinational:Mapped[bool]       = mapped_column(Boolean, default=False)
    is_exporter:     Mapped[bool]       = mapped_column(Boolean, default=False)
    under_audit:     Mapped[bool]       = mapped_column(Boolean, default=False)
    # All raw scraped data stored as JSON — flexible, no schema migration needed
    scraped_data:    Mapped[dict]       = mapped_column(JSON, default=dict)
    status:          Mapped[LeadStatus] = mapped_column(PgEnum(LeadStatus), default=LeadStatus.new)
    # Status management fields
    assigned_to_id:  Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    status_notes:    Mapped[str | None] = mapped_column(Text)  # Latest notes on this lead
    last_contacted:  Mapped[datetime | None] = mapped_column(DateTime)
    created_at:      Mapped[datetime]   = mapped_column(DateTime, default=datetime.utcnow)
    updated_at:      Mapped[datetime]   = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scores:  Mapped[list["LeadScore"]]  = relationship("LeadScore", back_populates="lead")
    signals: Mapped[list["LeadSignal"]] = relationship("LeadSignal", back_populates="lead")
    status_history: Mapped[list["LeadStatusHistory"]] = relationship("LeadStatusHistory", back_populates="lead")
    assigned_to: Mapped["User"] = relationship("User", foreign_keys=[assigned_to_id])


# ─── Scores (one row per lead per service) ────────────────────────────────────

class LeadScore(Base):
    __tablename__ = "lead_scores"

    id:           Mapped[int]         = mapped_column(Integer, primary_key=True)
    lead_id:      Mapped[int]         = mapped_column(ForeignKey("leads.id"), index=True)
    service_type: Mapped[ServiceType] = mapped_column(PgEnum(ServiceType))
    service_name: Mapped[str]         = mapped_column(String(255))  # e.g. "SolidWorks Premium"
    score:        Mapped[float]       = mapped_column(Float)        # 0–100
    reasoning:    Mapped[str | None]  = mapped_column(Text)         # AI-generated explanation
    # Which signals contributed and their weights
    signal_breakdown: Mapped[dict]    = mapped_column(JSON, default=dict)
    scored_at:    Mapped[datetime]    = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="scores")


# ─── Signals (timeline of events per lead) ────────────────────────────────────

class LeadSignal(Base):
    __tablename__ = "lead_signals"

    id:          Mapped[int]      = mapped_column(Integer, primary_key=True)
    lead_id:     Mapped[int]      = mapped_column(ForeignKey("leads.id"), index=True)
    signal_type: Mapped[str]      = mapped_column(String(100))  # "new_hire", "funding", "news", "logo_detected"
    title:       Mapped[str]      = mapped_column(String(500))
    detail:      Mapped[str|None] = mapped_column(Text)
    source_url:  Mapped[str|None] = mapped_column(String(1000))
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="signals")


# ─── Lead Status History (audit trail of status changes) ──────────────────────

class LeadStatusHistory(Base):
    __tablename__ = "lead_status_history"

    id:           Mapped[int]        = mapped_column(Integer, primary_key=True)
    lead_id:      Mapped[int]        = mapped_column(ForeignKey("leads.id"), index=True)
    old_status:   Mapped[LeadStatus | None] = mapped_column(PgEnum(LeadStatus))
    new_status:   Mapped[LeadStatus] = mapped_column(PgEnum(LeadStatus))
    changed_by_id:Mapped[int]        = mapped_column(ForeignKey("users.id"))
    notes:        Mapped[str | None] = mapped_column(Text)  # Why was status changed
    changed_at:   Mapped[datetime]   = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="status_history")
    changed_by: Mapped["User"] = relationship("User")


# ─── Services (what ABBK sells — drives scoring dimensions) ───────────────────

class Service(Base):
    __tablename__ = "services"

    id:           Mapped[int]         = mapped_column(Integer, primary_key=True)
    name:         Mapped[str]         = mapped_column(String(255), unique=True)
    service_type: Mapped[ServiceType] = mapped_column(PgEnum(ServiceType))
    description:  Mapped[str | None]  = mapped_column(Text)
    # Scoring weights for this service (JSON dict of signal → weight)
    scoring_weights: Mapped[dict]     = mapped_column(JSON, default=dict)
    is_active:    Mapped[bool]        = mapped_column(Boolean, default=True)
