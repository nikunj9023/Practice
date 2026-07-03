"""app/repositories package."""
from app.repositories.customer_repository import CustomerRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.followup_repository import FollowUpRepository
from app.repositories.note_repository import NoteRepository

__all__ = [
    "CustomerRepository",
    "LeadRepository",
    "FollowUpRepository",
    "NoteRepository",
]
