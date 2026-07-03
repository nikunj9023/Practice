"""
app/models/note.py
==================
SQLAlchemy ORM model for the Note entity.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db


class Note(db.Model):
    """
    Represents a free-text note attached to a Customer record.

    Notes can optionally be tagged for quick filtering and can be pinned
    to appear first in listings.
    """

    __tablename__ = "notes"

    VALID_CATEGORIES = ("general", "meeting", "call", "email", "important", "other")

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    customer = db.relationship(
        "Customer",
        back_populates="notes",
        lazy="joined",
    )

    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(
        db.String(50),
        nullable=False,
        default="general",
        comment="Tag for filtering: general | meeting | call | email | important | other",
    )
    is_pinned = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        comment="Pinned notes appear at the top of the customer's note listing.",
    )
    author = db.Column(
        db.String(150),
        nullable=True,
        comment="Name or identifier of the team member who created the note.",
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
    # Public helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "is_pinned": self.is_pinned,
            "author": self.author,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Note id={self.id} customer_id={self.customer_id} title={self.title!r}>"
