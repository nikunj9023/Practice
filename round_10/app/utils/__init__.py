"""app/utils package."""
from app.utils.exceptions import (
    CRMBaseException,
    ValidationError,
    MissingFieldError,
    InvalidFieldError,
    NotFoundError,
    CustomerNotFoundError,
    LeadNotFoundError,
    FollowUpNotFoundError,
    NoteNotFoundError,
    DuplicateResourceError,
    DuplicateCustomerEmailError,
    BusinessRuleViolationError,
    LeadAlreadyConvertedError,
    InvalidLeadStatusTransitionError,
    FollowUpDateInPastError,
    RepositoryError,
    register_error_handlers,
)
from app.utils.logger import setup_logging, get_logger

__all__ = [
    # Exceptions
    "CRMBaseException",
    "ValidationError",
    "MissingFieldError",
    "InvalidFieldError",
    "NotFoundError",
    "CustomerNotFoundError",
    "LeadNotFoundError",
    "FollowUpNotFoundError",
    "NoteNotFoundError",
    "DuplicateResourceError",
    "DuplicateCustomerEmailError",
    "BusinessRuleViolationError",
    "LeadAlreadyConvertedError",
    "InvalidLeadStatusTransitionError",
    "FollowUpDateInPastError",
    "RepositoryError",
    "register_error_handlers",
    # Logging
    "setup_logging",
    "get_logger",
]
