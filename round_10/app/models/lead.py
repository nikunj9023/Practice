"""
app/models/lead.py
==================
SQLAlchemy ORM model for the Lead entity.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db


class Lead(db.Model):
    """
    Represents a sales lead in the Mini CRM system.

    A Lead progresses through a defined status state machine:
        new → contacted → qualified → converted | lost

    Once a Lead is converted it is linked to a Customer record.
    """

    __tablename__ = "leads"

    VALID_STATUSES = ("new", "contacted", "qualified", "converted", "lost")

    # Allowed state-machine transitions: current_status → {allowed next statuses}
    ALLOWED_TRANSITIONS: dict[str, tuple[str, ...]] = {
        "new": ("contacted", "lost"),
        "contacted": ("qualified", "lost"),
        "qualified": ("converted", "lost"),
        "converted": (),   # terminal – no further transitions
        "lost": (),        # terminal – no further transitions
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    company = db.Column(db.String(150), nullable=True)
    status = db.Column(
        db.String(30),
        nullable=False,
        default="new",
        comment="State machine: new | contacted | qualified | converted | lost",
    )
    source = db.Column(
        db.String(50),
        nullable=True,
        comment="Origination channel: web | referral | event | …",
    )
    estimated_value = db.Column(
        db.Numeric(12, 2),
        nullable=True,
        comment="Estimated deal value in the organisation's base currency.",
    )
    notes = db.Column(db.Text, nullable=True)

    # FK → Customer (populated on conversion)
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    customer = db.relationship(
        "Customer",
        back_populates="leads",
        lazy="joined",
    )

    # Relationships
    follow_ups = db.relationship(
        "FollowUp",
        back_populates="lead",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ------------------------------------------------------------------
    # Business helpers
    # ------------------------------------------------------------------

    @property
    def full_name(self) -> str:
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p)

    def is_converted(self) -> bool:
        return self.status == "converted"

    def can_transition_to(self, new_status: str) -> bool:
        allowed = self.ALLOWED_TRANSITIONS.get(self.status, ())
        return new_status in allowed

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "full_name": self.full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "company": self.company,
            "status": self.status,
            "source": self.source,
            "estimated_value": float(self.estimated_value) if self.estimated_value else None,
            "notes": self.notes,
            "customer_id": self.customer_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Lead id={self.id} email={self.email!r} status={self.status!r}>"
