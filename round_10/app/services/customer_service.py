"""
app/services/customer_service.py
==================================
Business logic layer for Customer operations.

This layer is responsible for:
  - Field-level and cross-field validation
  - Business rule enforcement (e.g. email uniqueness)
  - Orchestrating repository calls
  - Emitting structured audit log entries
  - Raising domain exceptions that propagate to the global error handler

No Flask imports appear here – the service is framework-agnostic and
fully testable without an application context.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from app.repositories.customer_repository import CustomerRepository
from app.utils.exceptions import (
    DuplicateCustomerEmailError,
    InvalidFieldError,
    MissingFieldError,
    ValidationError,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants / Validation configuration
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
_PHONE_RE = re.compile(r"^\+?[0-9\s\-().]{7,20}$")
_VALID_STATUSES = frozenset({"active", "inactive", "archived"})
_VALID_SOURCES = frozenset({"direct", "referral", "lead_conversion", "web", "event", "other"})


class CustomerService:
    """
    Orchestrates all business workflows related to Customers.

    The ``CustomerRepository`` is injected through the constructor,
    which makes the service trivially testable with a mock repository.
    """

    def __init__(self, repository: CustomerRepository | None = None) -> None:
        self._repo: CustomerRepository = repository or CustomerRepository()

    # ==================================================================
    # Internal validators
    # ==================================================================

    def _validate_email(self, email: str) -> str:
        """Normalise and validate an email address."""
        if not email or not email.strip():
            raise MissingFieldError(["email"])
        normalised = email.strip().lower()
        if not _EMAIL_RE.match(normalised):
            raise InvalidFieldError("email", "Must be a valid email address.")
        return normalised

    def _validate_phone(self, phone: str) -> str:
        """Normalise and validate an optional phone number."""
        stripped = phone.strip()
        if not _PHONE_RE.match(stripped):
            raise InvalidFieldError(
                "phone",
                "Must contain 7–20 characters and may include digits, spaces, "
                "hyphens, parentheses, and a leading '+'.",
            )
        return stripped

    def _validate_status(self, status: str) -> str:
        if status not in _VALID_STATUSES:
            raise InvalidFieldError(
                "status",
                f"Allowed values: {sorted(_VALID_STATUSES)}. Got: '{status}'.",
            )
        return status

    def _validate_source(self, source: str) -> str:
        if source not in _VALID_SOURCES:
            raise InvalidFieldError(
                "source",
                f"Allowed values: {sorted(_VALID_SOURCES)}. Got: '{source}'.",
            )
        return source

    def _validate_name(self, name: str) -> str:
        stripped = name.strip()
        if len(stripped) < 2:
            raise InvalidFieldError("name", "Must be at least 2 characters long.")
        if len(stripped) > 150:
            raise InvalidFieldError("name", "Must be at most 150 characters long.")
        return stripped

    # ==================================================================
    # Public operations
    # ==================================================================

    def create_customer(self, data: dict) -> dict:
        """
        Validate input, enforce uniqueness, and create a Customer record.

        Parameters
        ----------
        data : dict
            Raw request payload.  Expected keys:
                - ``name``  (required, str)
                - ``email`` (required, str)
                - ``phone`` (optional, str)
                - ``company`` (optional, str)
                - ``address`` (optional, str)
                - ``status`` (optional, str, default: ``'active'``)
                - ``source`` (optional, str)

        Returns
        -------
        dict
            Serialised representation of the created Customer.

        Raises
        ------
        MissingFieldError
            If ``name`` or ``email`` are absent.
        InvalidFieldError
            If any supplied field fails format validation.
        DuplicateCustomerEmailError
            If the email already exists in the system.
        """
        logger.info("CustomerService.create_customer | email=%s", data.get("email"))

        # --- Required field presence ---
        missing = [f for f in ("name", "email") if not data.get(f)]
        if missing:
            raise MissingFieldError(missing)

        # --- Field-level validation ---
        cleaned: dict = {}
        cleaned["name"] = self._validate_name(data["name"])
        cleaned["email"] = self._validate_email(data["email"])

        if data.get("phone"):
            cleaned["phone"] = self._validate_phone(data["phone"])

        if data.get("company"):
            cleaned["company"] = data["company"].strip()

        if data.get("address"):
            cleaned["address"] = data["address"].strip()

        status = data.get("status", "active")
        cleaned["status"] = self._validate_status(status)

        if data.get("source"):
            cleaned["source"] = self._validate_source(data["source"])

        # --- Cross-field / business rule: email uniqueness ---
        if self._repo.email_exists(cleaned["email"]):
            logger.warning(
                "CustomerService.create_customer: duplicate email=%s", cleaned["email"]
            )
            raise DuplicateCustomerEmailError(cleaned["email"])

        customer = self._repo.create(cleaned)
        logger.info(
            "CustomerService.create_customer: success | id=%d email=%s",
            customer.id, customer.email,
        )
        return customer.to_dict()

    # ------------------------------------------------------------------

    def get_customer(self, customer_id: int) -> dict:
        """
        Fetch a single Customer by ID.

        Returns
        -------
        dict
            Serialised Customer.

        Raises
        ------
        CustomerNotFoundError
            If no Customer with ``customer_id`` exists.
        """
        logger.debug("CustomerService.get_customer | id=%d", customer_id)
        customer = self._repo.get_by_id(customer_id)
        return customer.to_dict()

    # ------------------------------------------------------------------

    def list_customers(
        self,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """
        Return a paginated list of Customers, optionally filtered by status.

        Parameters
        ----------
        status : str | None
            Filter: ``active`` | ``inactive`` | ``archived``.
        page : int
            1-based page number (default: 1).
        per_page : int
            Page size, capped at 100 to protect against abuse.

        Returns
        -------
        dict
            ``{items: [...], total, page, per_page, pages}``
        """
        logger.debug(
            "CustomerService.list_customers | status=%s page=%d per_page=%d",
            status, page, per_page,
        )
        # Guard: status filter
        if status and status not in _VALID_STATUSES:
            raise InvalidFieldError("status", f"Allowed values: {sorted(_VALID_STATUSES)}.")

        # Guard: pagination sanity
        page = max(1, int(page))
        per_page = min(max(1, int(per_page)), 100)

        result = self._repo.get_all(status=status, page=page, per_page=per_page)
        result["items"] = [c.to_dict() for c in result["items"]]
        return result

    # ------------------------------------------------------------------

    def search_customers(
        self, query_str: str, page: int = 1, per_page: int = 20
    ) -> dict:
        """
        Search Customers by name, email, or company substring.

        Raises
        ------
        ValidationError
            If the search query is blank or fewer than 2 characters.
        """
        if not query_str or len(query_str.strip()) < 2:
            raise ValidationError(
                "Search query must be at least 2 characters long.",
                field_errors={"q": "Minimum length is 2 characters."},
            )
        page = max(1, int(page))
        per_page = min(max(1, int(per_page)), 100)

        result = self._repo.search(query_str, page=page, per_page=per_page)
        result["items"] = [c.to_dict() for c in result["items"]]
        return result

    # ------------------------------------------------------------------

    def update_customer(self, customer_id: int, data: dict) -> dict:
        """
        Apply a partial update to a Customer.

        Only fields included in ``data`` are changed; the rest remain as-is.
        All supplied fields are validated before the update is committed.

        Returns
        -------
        dict
            Serialised updated Customer.

        Raises
        ------
        CustomerNotFoundError
        DuplicateCustomerEmailError
        InvalidFieldError / ValidationError
        """
        logger.info("CustomerService.update_customer | id=%d", customer_id)

        if not data:
            raise ValidationError("At least one field must be provided for update.")

        cleaned: dict = {}

        if "name" in data:
            cleaned["name"] = self._validate_name(data["name"])

        if "email" in data:
            cleaned["email"] = self._validate_email(data["email"])
            # Uniqueness check: must exclude current customer
            if self._repo.email_exists(cleaned["email"], exclude_id=customer_id):
                raise DuplicateCustomerEmailError(cleaned["email"])

        if "phone" in data:
            cleaned["phone"] = self._validate_phone(data["phone"]) if data["phone"] else None

        if "company" in data:
            cleaned["company"] = data["company"].strip() if data["company"] else None

        if "address" in data:
            cleaned["address"] = data["address"].strip() if data["address"] else None

        if "status" in data:
            cleaned["status"] = self._validate_status(data["status"])

        if "source" in data:
            cleaned["source"] = self._validate_source(data["source"]) if data["source"] else None

        customer = self._repo.update(customer_id, cleaned)
        logger.info("CustomerService.update_customer: success | id=%d", customer.id)
        return customer.to_dict()

    # ------------------------------------------------------------------

    def delete_customer(self, customer_id: int) -> dict:
        """
        Delete a Customer and all cascade-linked records.

        Returns
        -------
        dict
            Confirmation payload: ``{message, deleted_id}``.

        Raises
        ------
        CustomerNotFoundError
        """
        logger.info("CustomerService.delete_customer | id=%d", customer_id)
        # Calling get_by_id first ensures we raise CustomerNotFoundError cleanly
        customer = self._repo.get_by_id(customer_id)
        self._repo.delete(customer_id)
        logger.info("CustomerService.delete_customer: success | id=%d", customer_id)
        return {
            "message": f"Customer '{customer.name}' (id={customer_id}) deleted successfully.",
            "deleted_id": customer_id,
        }
