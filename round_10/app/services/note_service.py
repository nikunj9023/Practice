"""
app/services/note_service.py
==============================
Business logic layer for Note operations.

Enforces:
  - Customer must exist before a note can be added
  - Title and content cannot be blank
  - Category must be a recognised value
  - Maximum content length (10,000 chars) to prevent abuse
"""

from __future__ import annotations

import logging
from typing import Optional

from app.repositories.note_repository import NoteRepository
from app.repositories.customer_repository import CustomerRepository
from app.utils.exceptions import (
    InvalidFieldError,
    MissingFieldError,
    ValidationError,
)

logger = logging.getLogger(__name__)

_VALID_CATEGORIES = frozenset({"general", "meeting", "call", "email", "important", "other"})
_MAX_CONTENT_LENGTH = 10_000  # characters


class NoteService:
    """Orchestrates all business workflows related to Notes."""

    def __init__(
        self,
        note_repo: NoteRepository | None = None,
        customer_repo: CustomerRepository | None = None,
    ) -> None:
        self._note_repo: NoteRepository = note_repo or NoteRepository()
        self._customer_repo: CustomerRepository = customer_repo or CustomerRepository()

    # ==================================================================
    # Internal validators
    # ==================================================================

    def _validate_title(self, title: str) -> str:
        stripped = title.strip()
        if not stripped:
            raise InvalidFieldError("title", "Title cannot be blank.")
        if len(stripped) > 200:
            raise InvalidFieldError("title", "Title must be at most 200 characters.")
        return stripped

    def _validate_content(self, content: str) -> str:
        stripped = content.strip()
        if not stripped:
            raise InvalidFieldError("content", "Content cannot be blank.")
        if len(stripped) > _MAX_CONTENT_LENGTH:
            raise InvalidFieldError(
                "content",
                f"Content must not exceed {_MAX_CONTENT_LENGTH:,} characters "
                f"(received {len(stripped):,}).",
            )
        return stripped

    def _validate_category(self, category: str) -> str:
        if category not in _VALID_CATEGORIES:
            raise InvalidFieldError(
                "category",
                f"Allowed values: {sorted(_VALID_CATEGORIES)}. Got: '{category}'.",
            )
        return category

    # ==================================================================
    # Public operations
    # ==================================================================

    def create_note(self, data: dict) -> dict:
        """
        Validate input and create a Note linked to a Customer.

        Parameters
        ----------
        data : dict
            Required: ``customer_id``, ``title``, ``content``.
            Optional: ``category``, ``is_pinned``, ``author``.

        Returns
        -------
        dict
            Serialised created Note.

        Raises
        ------
        MissingFieldError
            If any required field is absent.
        CustomerNotFoundError
            If the referenced Customer does not exist.
        InvalidFieldError
            If any field fails validation.
        """
        logger.info("NoteService.create_note | customer_id=%s", data.get("customer_id"))

        missing = [f for f in ("customer_id", "title", "content") if not data.get(f)]
        if missing:
            raise MissingFieldError(missing)

        # Verify customer exists – raises CustomerNotFoundError if absent
        self._customer_repo.get_by_id(int(data["customer_id"]))

        category = data.get("category", "general")
        is_pinned = data.get("is_pinned", False)

        if not isinstance(is_pinned, bool):
            raise InvalidFieldError("is_pinned", "Must be a boolean (true or false).")

        cleaned = {
            "customer_id": int(data["customer_id"]),
            "title": self._validate_title(data["title"]),
            "content": self._validate_content(data["content"]),
            "category": self._validate_category(category),
            "is_pinned": is_pinned,
            "author": data.get("author", "").strip() or None,
        }

        note = self._note_repo.create(cleaned)
        logger.info("NoteService.create_note: success | id=%d", note.id)
        return note.to_dict()

    # ------------------------------------------------------------------

    def get_note(self, note_id: int) -> dict:
        """
        Fetch a single Note by ID.

        Raises
        ------
        NoteNotFoundError
        """
        return self._note_repo.get_by_id(note_id).to_dict()

    # ------------------------------------------------------------------

    def list_notes_for_customer(
        self,
        customer_id: int,
        category: Optional[str] = None,
        pinned_only: bool = False,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """
        Return a paginated list of Notes for a Customer.

        Pinned notes always appear first within the result set.

        Raises
        ------
        CustomerNotFoundError
            If the Customer does not exist.
        InvalidFieldError
            If ``category`` is not a recognised value.
        """
        # Validate customer exists
        self._customer_repo.get_by_id(customer_id)

        if category and category not in _VALID_CATEGORIES:
            raise InvalidFieldError("category", f"Allowed: {sorted(_VALID_CATEGORIES)}.")

        page = max(1, int(page))
        per_page = min(max(1, int(per_page)), 100)

        result = self._note_repo.get_all_for_customer(
            customer_id=customer_id,
            category=category,
            pinned_only=pinned_only,
            page=page,
            per_page=per_page,
        )
        result["items"] = [n.to_dict() for n in result["items"]]
        return result

    # ------------------------------------------------------------------

    def update_note(self, note_id: int, data: dict) -> dict:
        """
        Apply a partial update to a Note (PATCH semantics).

        All supplied fields are validated before the update is committed.

        Raises
        ------
        NoteNotFoundError
        InvalidFieldError / ValidationError
        """
        logger.info("NoteService.update_note | id=%d", note_id)

        if not data:
            raise ValidationError("At least one field must be provided for update.")

        cleaned: dict = {}

        if "title" in data:
            cleaned["title"] = self._validate_title(data["title"])

        if "content" in data:
            cleaned["content"] = self._validate_content(data["content"])

        if "category" in data:
            cleaned["category"] = self._validate_category(data["category"])

        if "is_pinned" in data:
            if not isinstance(data["is_pinned"], bool):
                raise InvalidFieldError("is_pinned", "Must be a boolean.")
            cleaned["is_pinned"] = data["is_pinned"]

        if "author" in data:
            cleaned["author"] = data["author"].strip() if data["author"] else None

        updated = self._note_repo.update(note_id, cleaned)
        logger.info("NoteService.update_note: success | id=%d", updated.id)
        return updated.to_dict()

    # ------------------------------------------------------------------

    def delete_note(self, note_id: int) -> dict:
        """
        Delete a Note.

        Raises
        ------
        NoteNotFoundError
        """
        logger.info("NoteService.delete_note | id=%d", note_id)
        self._note_repo.get_by_id(note_id)  # validates existence first
        self._note_repo.delete(note_id)
        return {
            "message": f"Note id={note_id} deleted successfully.",
            "deleted_id": note_id,
        }

    # ------------------------------------------------------------------

    def pin_note(self, note_id: int) -> dict:
        """
        Pin a Note so it appears at the top of the customer's note list.

        Idempotent – pinning an already-pinned note is a no-op.

        Raises
        ------
        NoteNotFoundError
        """
        logger.info("NoteService.pin_note | id=%d", note_id)
        note = self._note_repo.get_by_id(note_id)
        if note.is_pinned:
            return note.to_dict()  # idempotent
        updated = self._note_repo.update(note_id, {"is_pinned": True})
        return updated.to_dict()

    def unpin_note(self, note_id: int) -> dict:
        """
        Unpin a Note.

        Idempotent – unpinning an already-unpinned note is a no-op.

        Raises
        ------
        NoteNotFoundError
        """
        logger.info("NoteService.unpin_note | id=%d", note_id)
        note = self._note_repo.get_by_id(note_id)
        if not note.is_pinned:
            return note.to_dict()
        updated = self._note_repo.update(note_id, {"is_pinned": False})
        return updated.to_dict()
