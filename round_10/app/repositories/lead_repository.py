"""
app/repositories/lead_repository.py
=====================================
Data-access layer for the Lead entity.
"""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models.lead import Lead
from app.utils.exceptions import LeadNotFoundError, RepositoryError

logger = logging.getLogger(__name__)


class LeadRepository:
    """Encapsulates all CRUD and query operations for the Lead model."""

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(self, data: dict) -> Lead:
        """
        Persist a new Lead to the database.

        Parameters
        ----------
        data : dict
            Validated lead fields. Must contain at minimum ``title``,
            ``first_name``, and ``email``.

        Returns
        -------
        Lead
            The newly created, committed Lead instance.

        Raises
        ------
        RepositoryError
            On any unexpected database failure.
        """
        logger.debug("LeadRepository.create | email=%s", data.get("email"))
        lead = Lead(
            title=data["title"],
            first_name=data["first_name"],
            last_name=data.get("last_name"),
            email=data["email"].lower().strip(),
            phone=data.get("phone"),
            company=data.get("company"),
            status=data.get("status", "new"),
            source=data.get("source"),
            estimated_value=data.get("estimated_value"),
            notes=data.get("notes"),
            customer_id=data.get("customer_id"),
        )
        try:
            db.session.add(lead)
            db.session.commit()
            db.session.refresh(lead)
            logger.info("Lead created | id=%d email=%s", lead.id, lead.email)
            return lead
        except SQLAlchemyError as exc:
            db.session.rollback()
            logger.error("DB error on lead create: %s", exc)
            raise RepositoryError("create_lead", exc) from exc

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_by_id(self, lead_id: int) -> Lead:
        """
        Retrieve a Lead by primary key.

        Raises
        ------
        LeadNotFoundError
            If no Lead with ``lead_id`` exists.
        """
        logger.debug("LeadRepository.get_by_id | id=%d", lead_id)
        try:
            lead = db.session.get(Lead, lead_id)
        except SQLAlchemyError as exc:
            raise RepositoryError("get_lead_by_id", exc) from exc
        if lead is None:
            raise LeadNotFoundError(lead_id)
        return lead

    def get_all(
        self,
        status: Optional[str] = None,
        customer_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """Return a paginated, optionally filtered list of Leads."""
        logger.debug(
            "LeadRepository.get_all | status=%s customer_id=%s page=%d",
            status, customer_id, page,
        )
        try:
            query = Lead.query.order_by(Lead.created_at.desc())
            if status:
                query = query.filter_by(status=status)
            if customer_id is not None:
                query = query.filter_by(customer_id=customer_id)
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            return {
                "items": pagination.items,
                "total": pagination.total,
                "page": pagination.page,
                "per_page": pagination.per_page,
                "pages": pagination.pages,
            }
        except SQLAlchemyError as exc:
            raise RepositoryError("list_leads", exc) from exc

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, lead_id: int, data: dict) -> Lead:
        """
        Apply a partial update to a Lead (PATCH semantics).

        Raises
        ------
        LeadNotFoundError
            If no Lead with ``lead_id`` exists.
        RepositoryError
            On database failure.
        """
        logger.debug("LeadRepository.update | id=%d", lead_id)
        lead = self.get_by_id(lead_id)

        updatable_fields = (
            "title", "first_name", "last_name", "phone",
            "company", "status", "source", "estimated_value", "notes", "customer_id",
        )
        for field in updatable_fields:
            if field in data:
                setattr(lead, field, data[field])

        if "email" in data:
            lead.email = data["email"].lower().strip()

        try:
            db.session.commit()
            db.session.refresh(lead)
            logger.info("Lead updated | id=%d status=%s", lead.id, lead.status)
            return lead
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise RepositoryError("update_lead", exc) from exc

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, lead_id: int) -> None:
        """
        Hard-delete a Lead and its cascade-linked FollowUp records.

        Raises
        ------
        LeadNotFoundError
        RepositoryError
        """
        logger.debug("LeadRepository.delete | id=%d", lead_id)
        lead = self.get_by_id(lead_id)
        try:
            db.session.delete(lead)
            db.session.commit()
            logger.info("Lead deleted | id=%d", lead_id)
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise RepositoryError("delete_lead", exc) from exc
