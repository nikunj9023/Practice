"""
app/repositories/followup_repository.py
=========================================
Data-access layer for the FollowUp entity.
"""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.followup import FollowUp
from app.utils.exceptions import FollowUpNotFoundError, RepositoryError

logger = logging.getLogger(__name__)


class FollowUpRepository:
    """Encapsulates all CRUD and query operations for the FollowUp model."""

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(self, data: dict) -> FollowUp:
        """
        Persist a new FollowUp linked to a Lead.

        Parameters
        ----------
        data : dict
            Must contain ``lead_id`` and ``scheduled_at`` at minimum.

        Returns
        -------
        FollowUp
            The committed FollowUp instance.

        Raises
        ------
        RepositoryError
            On database failure.
        """
        logger.debug("FollowUpRepository.create | lead_id=%s", data.get("lead_id"))
        followup = FollowUp(
            lead_id=data["lead_id"],
            follow_up_type=data.get("follow_up_type", "call"),
            scheduled_at=data["scheduled_at"],
            outcome=data.get("outcome"),
            status=data.get("status", "pending"),
            assigned_to=data.get("assigned_to"),
        )
        try:
            db.session.add(followup)
            db.session.commit()
            db.session.refresh(followup)
            logger.info(
                "FollowUp created | id=%d lead_id=%d scheduled_at=%s",
                followup.id,
                followup.lead_id,
                followup.scheduled_at,
            )
            return followup
        except SQLAlchemyError as exc:
            db.session.rollback()
            logger.error("DB error on followup create: %s", exc)
            raise RepositoryError("create_followup", exc) from exc

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_by_id(self, followup_id: int) -> FollowUp:
        """
        Retrieve a FollowUp by primary key.

        Raises
        ------
        FollowUpNotFoundError
            If no record with ``followup_id`` exists.
        """
        logger.debug("FollowUpRepository.get_by_id | id=%d", followup_id)
        try:
            followup = db.session.get(FollowUp, followup_id)
        except SQLAlchemyError as exc:
            raise RepositoryError("get_followup_by_id", exc) from exc
        if followup is None:
            raise FollowUpNotFoundError(followup_id)
        return followup

    def get_all_for_lead(
        self,
        lead_id: int,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """
        Return a paginated list of FollowUps for a given Lead.

        Parameters
        ----------
        lead_id : int
            The parent Lead identifier.
        status : str | None
            Optional filter: ``pending`` | ``completed`` | ``cancelled``.
        """
        logger.debug(
            "FollowUpRepository.get_all_for_lead | lead_id=%d status=%s", lead_id, status
        )
        try:
            query = (
                FollowUp.query
                .filter_by(lead_id=lead_id)
                .order_by(FollowUp.scheduled_at.asc())
            )
            if status:
                query = query.filter_by(status=status)
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            return {
                "items": pagination.items,
                "total": pagination.total,
                "page": pagination.page,
                "per_page": pagination.per_page,
                "pages": pagination.pages,
            }
        except SQLAlchemyError as exc:
            raise RepositoryError("list_followups_for_lead", exc) from exc

    def get_pending(self, page: int = 1, per_page: int = 20) -> dict:
        """Return a paginated list of all pending (not yet completed) FollowUps, oldest first."""
        try:
            query = (
                FollowUp.query
                .filter_by(status="pending")
                .order_by(FollowUp.scheduled_at.asc())
            )
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            return {
                "items": pagination.items,
                "total": pagination.total,
                "page": pagination.page,
                "per_page": pagination.per_page,
                "pages": pagination.pages,
            }
        except SQLAlchemyError as exc:
            raise RepositoryError("list_pending_followups", exc) from exc

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, followup_id: int, data: dict) -> FollowUp:
        """
        Apply a partial update to a FollowUp (PATCH semantics).

        Raises
        ------
        FollowUpNotFoundError
        RepositoryError
        """
        logger.debug("FollowUpRepository.update | id=%d", followup_id)
        followup = self.get_by_id(followup_id)

        updatable = ("follow_up_type", "scheduled_at", "outcome", "status", "assigned_to")
        for field in updatable:
            if field in data:
                setattr(followup, field, data[field])

        try:
            db.session.commit()
            db.session.refresh(followup)
            logger.info("FollowUp updated | id=%d status=%s", followup.id, followup.status)
            return followup
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise RepositoryError("update_followup", exc) from exc

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, followup_id: int) -> None:
        """
        Hard-delete a FollowUp record.

        Raises
        ------
        FollowUpNotFoundError
        RepositoryError
        """
        logger.debug("FollowUpRepository.delete | id=%d", followup_id)
        followup = self.get_by_id(followup_id)
        try:
            db.session.delete(followup)
            db.session.commit()
            logger.info("FollowUp deleted | id=%d", followup_id)
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise RepositoryError("delete_followup", exc) from exc
