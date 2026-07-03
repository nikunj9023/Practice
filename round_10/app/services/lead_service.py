"""
app/services/lead_service.py
==============================
Business logic layer for Lead operations.

Responsibilities:
  - Input validation (required fields, format, enum values)
  - Status state-machine enforcement
  - Lead-to-Customer conversion workflow
  - Structured audit logging
"""

from __future__ import annotations

import logging
import re
from decimal import Decimal, InvalidOperation
from typing import Optional

from app.repositories.lead_repository import LeadRepository
from app.repositories.customer_repository import CustomerRepository
from app.utils.exceptions import (
    InvalidFieldError,
    InvalidLeadStatusTransitionError,
    LeadAlreadyConvertedError,
    MissingFieldError,
    ValidationError,
)

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
_VALID_SOURCES = frozenset(
    {"web", "referral", "event", "cold_call", "email_campaign", "social_media", "other"}
)


class LeadService:
    """Orchestrates all business workflows related to Leads."""

    def __init__(
        self,
        lead_repo: LeadRepository | None = None,
        customer_repo: CustomerRepository | None = None,
    ) -> None:
        self._lead_repo: LeadRepository = lead_repo or LeadRepository()
        self._customer_repo: CustomerRepository = customer_repo or CustomerRepository()

    # ==================================================================
    # Internal validators
    # ==================================================================

    def _validate_email(self, email: str) -> str:
        normalised = email.strip().lower()
        if not _EMAIL_RE.match(normalised):
            raise InvalidFieldError("email", "Must be a valid email address.")
        return normalised

    def _validate_estimated_value(self, value) -> Optional[Decimal]:
        if value is None:
            return None
        try:
            dec = Decimal(str(value))
        except InvalidOperation:
            raise InvalidFieldError(
                "estimated_value", "Must be a valid decimal number (e.g. 1500.00)."
            )
        if dec < 0:
            raise InvalidFieldError("estimated_value", "Must be a non-negative number.")
        return dec

    # ==================================================================
    # Public operations
    # ==================================================================

    def create_lead(self, data: dict) -> dict:
        """
        Validate input and create a new Lead record in the ``new`` status.

        Parameters
        ----------
        data : dict
            Expected keys: ``title``, ``first_name``, ``email`` (required);
            ``last_name``, ``phone``, ``company``, ``source``,
            ``estimated_value``, ``notes`` (optional).

        Returns
        -------
        dict
            Serialised created Lead.

        Raises
        ------
        MissingFieldError / InvalidFieldError / ValidationError
        """
        logger.info("LeadService.create_lead | email=%s", data.get("email"))

        missing = [f for f in ("title", "first_name", "email") if not data.get(f)]
        if missing:
            raise MissingFieldError(missing)

        cleaned: dict = {
            "title": data["title"].strip(),
            "first_name": data["first_name"].strip(),
            "last_name": data.get("last_name", "").strip() or None,
            "email": self._validate_email(data["email"]),
            "phone": data.get("phone", "").strip() or None,
            "company": data.get("company", "").strip() or None,
            "status": "new",   # Always starts as 'new'
            "notes": data.get("notes", "").strip() or None,
        }

        if data.get("source"):
            if data["source"] not in _VALID_SOURCES:
                raise InvalidFieldError(
                    "source", f"Allowed: {sorted(_VALID_SOURCES)}. Got: '{data['source']}'."
                )
            cleaned["source"] = data["source"]

        cleaned["estimated_value"] = self._validate_estimated_value(
            data.get("estimated_value")
        )

        lead = self._lead_repo.create(cleaned)
        logger.info("LeadService.create_lead: success | id=%d", lead.id)
        return lead.to_dict()

    # ------------------------------------------------------------------

    def get_lead(self, lead_id: int) -> dict:
        """
        Fetch a single Lead by ID.

        Raises
        ------
        LeadNotFoundError
        """
        return self._lead_repo.get_by_id(lead_id).to_dict()

    # ------------------------------------------------------------------

    def list_leads(
        self,
        status: Optional[str] = None,
        customer_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """Return a paginated list of Leads with optional status/customer_id filters."""
        from app.models.lead import Lead as LeadModel
        if status and status not in LeadModel.VALID_STATUSES:
            raise InvalidFieldError(
                "status",
                f"Allowed: {LeadModel.VALID_STATUSES}. Got: '{status}'.",
            )
        page = max(1, int(page))
        per_page = min(max(1, int(per_page)), 100)
        result = self._lead_repo.get_all(
            status=status, customer_id=customer_id, page=page, per_page=per_page
        )
        result["items"] = [lead.to_dict() for lead in result["items"]]
        return result

    # ------------------------------------------------------------------

    def update_lead(self, lead_id: int, data: dict) -> dict:
        """
        Apply a partial update to a Lead.

        Status transitions are validated against the state machine defined
        on the Lead model.

        Raises
        ------
        LeadNotFoundError
        InvalidLeadStatusTransitionError
            If the requested status transition is not allowed.
        LeadAlreadyConvertedError
            If someone tries to edit a converted lead's status back.
        InvalidFieldError / ValidationError
        """
        logger.info("LeadService.update_lead | id=%d", lead_id)

        if not data:
            raise ValidationError("At least one field must be supplied for update.")

        lead = self._lead_repo.get_by_id(lead_id)  # raises LeadNotFoundError if absent

        cleaned: dict = {}

        for field in ("title", "first_name", "last_name", "phone", "company", "notes"):
            if field in data:
                cleaned[field] = data[field].strip() if isinstance(data[field], str) else data[field]

        if "email" in data:
            cleaned["email"] = self._validate_email(data["email"])

        if "estimated_value" in data:
            cleaned["estimated_value"] = self._validate_estimated_value(data["estimated_value"])

        if "source" in data:
            if data["source"] and data["source"] not in _VALID_SOURCES:
                raise InvalidFieldError(
                    "source",
                    f"Allowed: {sorted(_VALID_SOURCES)}. Got: '{data['source']}'.",
                )
            cleaned["source"] = data["source"]

        # --- State-machine enforcement ---
        if "status" in data:
            requested_status = data["status"]
            if not lead.can_transition_to(requested_status):
                if lead.is_converted():
                    raise LeadAlreadyConvertedError(lead_id)
                raise InvalidLeadStatusTransitionError(lead.status, requested_status)
            cleaned["status"] = requested_status

        updated_lead = self._lead_repo.update(lead_id, cleaned)
        logger.info(
            "LeadService.update_lead: success | id=%d new_status=%s",
            updated_lead.id, updated_lead.status,
        )
        return updated_lead.to_dict()

    # ------------------------------------------------------------------

    def convert_lead(self, lead_id: int) -> dict:
        """
        Convert a qualified Lead into a Customer record.

        This is the core CRM conversion workflow:
          1. Fetch the Lead, validate it is in the ``qualified`` state.
          2. Create a Customer from Lead data.
          3. Update Lead status to ``converted`` and link its ``customer_id``.

        Returns
        -------
        dict
            ``{lead: {...}, customer: {...}, message: str}``

        Raises
        ------
        LeadNotFoundError
        LeadAlreadyConvertedError
            If the Lead is already converted.
        InvalidLeadStatusTransitionError
            If the Lead is not in the ``qualified`` state.
        """
        logger.info("LeadService.convert_lead | lead_id=%d", lead_id)

        lead = self._lead_repo.get_by_id(lead_id)

        if lead.is_converted():
            raise LeadAlreadyConvertedError(lead_id)

        if not lead.can_transition_to("converted"):
            raise InvalidLeadStatusTransitionError(lead.status, "converted")

        # Build customer data from lead
        customer_data = {
            "name": lead.full_name,
            "email": lead.email,
            "phone": lead.phone,
            "company": lead.company,
            "status": "active",
            "source": "lead_conversion",
        }

        # Check email uniqueness for customer
        existing_customer = self._customer_repo.get_by_email(lead.email)
        if existing_customer:
            # Link to the existing customer instead of creating a duplicate
            customer = existing_customer
            logger.info(
                "LeadService.convert_lead: linking to existing customer id=%d",
                customer.id,
            )
        else:
            customer = self._customer_repo.create(customer_data)
            logger.info(
                "LeadService.convert_lead: new customer created id=%d", customer.id
            )

        # Update lead status
        self._lead_repo.update(lead_id, {"status": "converted", "customer_id": customer.id})
        updated_lead = self._lead_repo.get_by_id(lead_id)

        logger.info(
            "LeadService.convert_lead: success | lead_id=%d → customer_id=%d",
            lead_id, customer.id,
        )
        return {
            "message": f"Lead '{lead.full_name}' successfully converted to Customer.",
            "lead": updated_lead.to_dict(),
            "customer": customer.to_dict(),
        }

    # ------------------------------------------------------------------

    def delete_lead(self, lead_id: int) -> dict:
        """
        Delete a Lead and its cascade-linked FollowUps.

        Raises
        ------
        LeadNotFoundError
        """
        logger.info("LeadService.delete_lead | id=%d", lead_id)
        lead = self._lead_repo.get_by_id(lead_id)
        self._lead_repo.delete(lead_id)
        return {
            "message": f"Lead '{lead.full_name}' (id={lead_id}) deleted successfully.",
            "deleted_id": lead_id,
        }
