"""
app/models/followup.py
======================
SQLAlchemy ORM model for the FollowUp entity.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db


class FollowUp(db.Model):
    """
    Represents a scheduled follow-up activity linked to a Lead.

    A follow-up captures the planned interaction (call, email, meeting, etc.)
    and tracks whether it has been completed.
    """

    __tablename__ = "follow_ups"

    VALID_TYPES = ("call", "email", "meeting", "demo", "proposal", "other")
    VALID_STATUSES = ("pending", "completed", "cancelled")

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lead_id = db.Column(
        db.Integer,
        db.ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lead = db.relationship(
        "Lead",
        back_populates="follow_ups",
        lazy="joined",
    )

    follow_up_type = db.Column(
        db.String(50),
        nullable=False,
        default="call",
        comment="Type of follow-up: call | email | meeting | demo | proposal | other",
    )
    scheduled_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        comment="Future date/time when the follow-up is scheduled to occur.",
    )
    outcome = db.Column(
        db.Text,
        nullable=True,
        comment="Notes captured after the follow-up has been completed.",
    )
    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending",
        comment="Lifecycle: pending | completed | cancelled",
    )
    assigned_to = db.Column(
        db.String(150),
        nullable=True,
        comment="Name or identifier of the team member responsible for this follow-up.",
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
    def is_pending(self) -> bool:
        return self.status == "pending"

    @property
    def is_overdue(self) -> bool:
        """True if the follow-up is still pending but its scheduled time is past."""
        return self.status == "pending" and self.scheduled_at < datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "follow_up_type": self.follow_up_type,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "outcome": self.outcome,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "is_overdue": self.is_overdue,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<FollowUp id={self.id} lead_id={self.lead_id} "
            f"type={self.follow_up_type!r} status={self.status!r}>"
        )
