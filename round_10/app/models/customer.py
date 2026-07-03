"""
app/models/customer.py
=======================
SQLAlchemy ORM model for the Customer entity.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db


class Customer(db.Model):
    """
    Represents a customer in the Mini CRM system.

    A Customer is a confirmed contact who has been formally onboarded.
    They can originate from a converted Lead or be created directly.
    """

    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    phone = db.Column(db.String(20), nullable=True)
    company = db.Column(db.String(150), nullable=True)
    address = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.String(30),
        nullable=False,
        default="active",
        comment="Lifecycle status: active | inactive | archived",
    )
    source = db.Column(
        db.String(50),
        nullable=True,
        comment="Acquisition channel: direct | referral | lead_conversion | …",
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

    # Relationships
    leads = db.relationship(
        "Lead",
        back_populates="customer",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    notes = db.relationship(
        "Note",
        back_populates="customer",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialise the model instance to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "company": self.company,
            "address": self.address,
            "status": self.status,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Customer id={self.id} email={self.email!r}>"
