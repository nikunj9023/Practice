"""
app/utils/exceptions.py
========================
Custom domain exception hierarchy and global Flask error-handler registration.

All exceptions raised anywhere in the Service or Repository layer are mapped
here to deterministic HTTP status codes so that routes remain thin and
exception handling is centralised in ONE place.
"""

from __future__ import annotations

import logging
from typing import Any

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Base Domain Exception
# ---------------------------------------------------------------------------

class CRMBaseException(Exception):
    """
    Root of every domain-specific exception in this application.

    Attributes
    ----------
    message : str
        Human-readable description of what went wrong.
    status_code : int
        The HTTP status code that should be returned to the client.
    payload : dict | None
        Optional extra context that will be included in the JSON error body.
    """

    status_code: int = 500
    default_message: str = "An unexpected internal error occurred."

    def __init__(
        self,
        message: str | None = None,
        status_code: int | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.default_message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Serialise the exception to a JSON-friendly dictionary."""
        body: dict[str, Any] = {
            "error": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code,
        }
        if self.payload:
            body["details"] = self.payload
        return body


# ---------------------------------------------------------------------------
# 400 – Validation / Bad Request
# ---------------------------------------------------------------------------

class ValidationError(CRMBaseException):
    """Raised when incoming request data fails schema or business-rule validation."""

    status_code = 400
    default_message = "The supplied data is invalid."

    def __init__(
        self,
        message: str | None = None,
        field_errors: dict[str, str] | None = None,
    ) -> None:
        payload = {"field_errors": field_errors} if field_errors else None
        super().__init__(message=message, payload=payload)


class MissingFieldError(ValidationError):
    """Raised when a required field is absent from the request body."""

    default_message = "One or more required fields are missing."

    def __init__(self, fields: list[str]) -> None:
        super().__init__(
            message=f"Missing required fields: {', '.join(fields)}",
            field_errors={f: "This field is required." for f in fields},
        )


class InvalidFieldError(ValidationError):
    """Raised when a field value has an incorrect format or type."""

    default_message = "One or more fields contain invalid values."

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(
            message=f"Invalid value for '{field}': {reason}",
            field_errors={field: reason},
        )


# ---------------------------------------------------------------------------
# 404 – Not Found
# ---------------------------------------------------------------------------

class NotFoundError(CRMBaseException):
    """Raised when a requested resource does not exist in the data store."""

    status_code = 404
    default_message = "The requested resource was not found."

    def __init__(self, resource: str, identifier: Any) -> None:
        super().__init__(
            message=f"{resource} with identifier '{identifier}' was not found.",
            payload={"resource": resource, "identifier": str(identifier)},
        )


class CustomerNotFoundError(NotFoundError):
    """Raised when a Customer record cannot be located."""

    def __init__(self, customer_id: Any) -> None:
        super().__init__(resource="Customer", identifier=customer_id)


class LeadNotFoundError(NotFoundError):
    """Raised when a Lead record cannot be located."""

    def __init__(self, lead_id: Any) -> None:
        super().__init__(resource="Lead", identifier=lead_id)


class FollowUpNotFoundError(NotFoundError):
    """Raised when a FollowUp record cannot be located."""

    def __init__(self, followup_id: Any) -> None:
        super().__init__(resource="FollowUp", identifier=followup_id)


class NoteNotFoundError(NotFoundError):
    """Raised when a Note record cannot be located."""

    def __init__(self, note_id: Any) -> None:
        super().__init__(resource="Note", identifier=note_id)


# ---------------------------------------------------------------------------
# 409 – Conflict / Duplicate
# ---------------------------------------------------------------------------

class DuplicateResourceError(CRMBaseException):
    """Raised when creating a resource that already exists (e.g. duplicate email)."""

    status_code = 409
    default_message = "A resource with the supplied data already exists."

    def __init__(self, resource: str, field: str, value: Any) -> None:
        super().__init__(
            message=f"A {resource} with {field} '{value}' already exists.",
            payload={"resource": resource, "conflict_field": field, "conflict_value": str(value)},
        )


class DuplicateCustomerEmailError(DuplicateResourceError):
    """Raised when a Customer with the given email already exists."""

    def __init__(self, email: str) -> None:
        super().__init__(resource="Customer", field="email", value=email)


# ---------------------------------------------------------------------------
# 403 – Forbidden / Business Rule Violation
# ---------------------------------------------------------------------------

class BusinessRuleViolationError(CRMBaseException):
    """
    Raised when a requested operation violates a domain business rule that
    cannot be expressed purely as a field-level validation error.
    """

    status_code = 403
    default_message = "The requested operation violates a business rule."

    def __init__(self, message: str, rule: str | None = None) -> None:
        payload = {"rule": rule} if rule else None
        super().__init__(message=message, payload=payload)


class LeadAlreadyConvertedError(BusinessRuleViolationError):
    """Raised when attempting to convert a Lead that is already converted."""

    def __init__(self, lead_id: Any) -> None:
        super().__init__(
            message=f"Lead '{lead_id}' has already been converted to a customer.",
            rule="lead_conversion_idempotency",
        )


class InvalidLeadStatusTransitionError(BusinessRuleViolationError):
    """Raised when a Lead status transition is not allowed by the workflow."""

    def __init__(self, current_status: str, requested_status: str) -> None:
        super().__init__(
            message=(
                f"Transition from status '{current_status}' to '{requested_status}' "
                "is not permitted."
            ),
            rule="lead_status_state_machine",
        )


class FollowUpDateInPastError(BusinessRuleViolationError):
    """Raised when a FollowUp is scheduled for a date/time in the past."""

    def __init__(self) -> None:
        super().__init__(
            message="A follow-up cannot be scheduled for a date and time in the past.",
            rule="followup_future_date_constraint",
        )


# ---------------------------------------------------------------------------
# 422 – Unprocessable Entity
# ---------------------------------------------------------------------------

class UnprocessableEntityError(CRMBaseException):
    """
    Raised when the request body is syntactically valid JSON but semantically
    incorrect (e.g. an enum value that does not match any known option).
    """

    status_code = 422
    default_message = "The request body is semantically invalid."


# ---------------------------------------------------------------------------
# 500 – Internal / Repository Errors
# ---------------------------------------------------------------------------

class RepositoryError(CRMBaseException):
    """
    Raised when an unexpected error occurs in the data access layer
    (e.g. database connection failure, constraint violation not otherwise caught).
    """

    status_code = 500
    default_message = "A data access error occurred. Please try again later."

    def __init__(self, operation: str, original_error: Exception | None = None) -> None:
        payload: dict[str, Any] = {"operation": operation}
        if original_error is not None:
            payload["original_error"] = str(original_error)
        super().__init__(
            message=f"Repository operation '{operation}' failed.",
            payload=payload,
        )


# ---------------------------------------------------------------------------
# Global Flask Error Handlers Registration
# ---------------------------------------------------------------------------

def register_error_handlers(app: Flask) -> None:
    """
    Attach global error handlers to the Flask application instance.

    This function must be called from ``create_app()`` **after** the app is
    configured so that all error responses are uniformly structured JSON
    regardless of which layer raised the exception.

    Parameters
    ----------
    app : Flask
        The Flask application factory product.
    """

    @app.errorhandler(CRMBaseException)
    def handle_crm_exception(error: CRMBaseException):
        """Catch all domain exceptions and convert them to structured JSON."""
        logger.warning(
            "Domain exception [%s] raised: %s | payload=%s",
            error.__class__.__name__,
            error.message,
            error.payload,
        )
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        """Explicit handler for 400 validation failures."""
        logger.info("Validation error: %s", error.message)
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(NotFoundError)
    def handle_not_found(error: NotFoundError):
        """Explicit handler for 404 not-found errors."""
        logger.info("Not found: %s", error.message)
        response = jsonify(error.to_dict())
        response.status_code = 404
        return response

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Convert Werkzeug HTTP exceptions to the same JSON envelope."""
        logger.warning("HTTP exception %d: %s", error.code, error.description)
        body = {
            "error": error.name,
            "message": error.description,
            "status_code": error.code,
        }
        response = jsonify(body)
        response.status_code = error.code  # type: ignore[assignment]
        return response

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error: Exception):
        """Catch-all for any unhandled Python exception – never expose internals."""
        logger.exception("Unhandled exception: %s", str(error))
        body = {
            "error": "InternalServerError",
            "message": "An unexpected server error occurred. Please contact support.",
            "status_code": 500,
        }
        response = jsonify(body)
        response.status_code = 500
        return response
