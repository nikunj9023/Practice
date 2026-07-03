"""app/models package – exposes all ORM models for convenient imports."""
from app.models.customer import Customer
from app.models.lead import Lead
from app.models.followup import FollowUp
from app.models.note import Note

__all__ = ["Customer", "Lead", "FollowUp", "Note"]
