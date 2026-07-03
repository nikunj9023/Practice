"""
app/repositories/note_repository.py
======================================
Data-access layer for the Note entity.
"""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.note import Note
from app.utils.exceptions import NoteNotFoundError, RepositoryError

logger = logging.getLogger(__name__)


class NoteRepository:
    """Encapsulates all CRUD and query operations for the Note model."""

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(self, data: dict) -> Note:
        """
        Persist a new Note linked to a Customer.

        Parameters
        ----------
        data : dict
            Must contain ``customer_id``, ``title``, and ``content``.

        Returns
        -------
        Note
            The committed Note instance.

        Raises
        ------
        RepositoryError
            On database failure.
        """
        logger.debug("NoteRepository.create | customer_id=%s", data.get("customer_id"))
        note = Note(
            customer_id=data["customer_id"],
            title=data["title"].strip(),
            content=data["content"].strip(),
            category=data.get("category", "general"),
            is_pinned=data.get("is_pinned", False),
            author=data.get("author"),
        )
        try:
            db.session.add(note)
            db.session.commit()
            db.session.refresh(note)
            logger.info(
                "Note created | id=%d customer_id=%d", note.id, note.customer_id
            )
            return note
        except SQLAlchemyError as exc:
            db.session.rollback()
            logger.error("DB error on note create: %s", exc)
            raise RepositoryError("create_note", exc) from exc

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_by_id(self, note_id: int) -> Note:
        """
        Retrieve a Note by primary key.

        Raises
        ------
        NoteNotFoundError
            If no record with ``note_id`` exists.
        """
        logger.debug("NoteRepository.get_by_id | id=%d", note_id)
        try:
            note = db.session.get(Note, note_id)
        except SQLAlchemyError as exc:
            raise RepositoryError("get_note_by_id", exc) from exc
        if note is None:
            raise NoteNotFoundError(note_id)
        return note

    def get_all_for_customer(
        self,
        customer_id: int,
        category: Optional[str] = None,
        pinned_only: bool = False,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """
        Return a paginated list of Notes for a Customer.

        Pinned notes are returned first within the sorted result set.

        Parameters
        ----------
        customer_id : int
            The parent Customer identifier.
        category : str | None
            Optional filter by category.
        pinned_only : bool
            When ``True``, only return pinned notes.
        """
        logger.debug(
            "NoteRepository.get_all_for_customer | customer_id=%d category=%s pinned=%s",
            customer_id, category, pinned_only,
        )
        try:
            query = (
                Note.query
                .filter_by(customer_id=customer_id)
                .order_by(
                    Note.is_pinned.desc(),   # pinned first
                    Note.created_at.desc(),
                )
            )
            if category:
                query = query.filter_by(category=category)
            if pinned_only:
                query = query.filter_by(is_pinned=True)
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            return {
                "items": pagination.items,
                "total": pagination.total,
                "page": pagination.page,
                "per_page": pagination.per_page,
                "pages": pagination.pages,
            }
        except SQLAlchemyError as exc:
            raise RepositoryError("list_notes_for_customer", exc) from exc

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, note_id: int, data: dict) -> Note:
        """
        Apply a partial update to a Note (PATCH semantics).

        Raises
        ------
        NoteNotFoundError
        RepositoryError
        """
        logger.debug("NoteRepository.update | id=%d", note_id)
        note = self.get_by_id(note_id)

        updatable = ("title", "content", "category", "is_pinned", "author")
        for field in updatable:
            if field in data:
                value = data[field]
                # Strip whitespace from text fields
                if field in ("title", "content") and isinstance(value, str):
                    value = value.strip()
                setattr(note, field, value)

        try:
            db.session.commit()
            db.session.refresh(note)
            logger.info("Note updated | id=%d", note.id)
            return note
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise RepositoryError("update_note", exc) from exc

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, note_id: int) -> None:
        """
        Hard-delete a Note.

        Raises
        ------
        NoteNotFoundError
        RepositoryError
        """
        logger.debug("NoteRepository.delete | id=%d", note_id)
        note = self.get_by_id(note_id)
        try:
            db.session.delete(note)
            db.session.commit()
            logger.info("Note deleted | id=%d", note_id)
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise RepositoryError("delete_note", exc) from exc
