"""
app/services/followup_service.py
==================================
Business logic layer for FollowUp operations.

Enforces:
  - Scheduled date must be in the future
  - Lead must exist before a follow-up can be created
  - Only pending follow-ups can be completed/cancelled (not re-opened)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from app.repositories.followup_repository import FollowUpRepository
from app.repositories.lead_repository import LeadRepository
from app.utils.exceptions import (
    BusinessRuleViolationError,
    FollowUpDateInPastError,
    InvalidFieldError,
    MissingFieldError,
    ValidationError,
)

logger = logging.getLogger(__name__)

_VALID_TYPES = frozenset({"call", "email", "meeting", "demo", "proposal", "other"})
_VALID_STATUSES = frozenset({"pending", "completed", "cancelled"})


class FollowUpService:
    """Orchestrates all business workflows related to FollowUps."""

    def __init__(
        self,
        followup_repo: FollowUpRepository | None = None,
        lead_repo: LeadRepository | None = None,
    ) -> None:
        self._followup_repo: FollowUpRepository = followup_repo or FollowUpRepository()
        self._lead_repo: LeadRepository = lead_repo or LeadRepository()

    # ==================================================================
    # Internal validators
    # ==================================================================

    def _parse_and_validate_scheduled_at(self, raw_value) -> datetime:
        """
        Parse an ISO-8601 datetime string and ensure it is in the future.

        Accepts both offset-aware and offset-naive (UTC assumed) strings.
        """
        if not raw_value:
            raise MissingFieldError(["scheduled_at"])

        try:
            if isinstance(raw_value, datetime):
                scheduled = raw_value
            else:
                # fromisoformat handles both 'Z' suffix and '+HH:MM' offsets
                scheduled = datetime.fromisoformat(str(raw_value).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            raise InvalidFieldError(
                "scheduled_at",
                "Must be an ISO-8601 datetime string (e.g. '2026-12-31T14:00:00+05:30').",
            )

        # Make timezone-aware for comparison
        if scheduled.tzinfo is None:
            scheduled = scheduled.replace(tzinfo=timezone.utc)

        if scheduled <= datetime.now(timezone.utc):
            raise FollowUpDateInPastError()

        return scheduled

    # ==================================================================
    # Public operations
    # ==================================================================

    def create_followup(self, data: dict) -> dict:
        """
        Validate input and create a FollowUp linked to a Lead.

        Parameters
        ----------
        data : dict
            Required: ``lead_id``, ``scheduled_at``.
            Optional: ``follow_up_type``, ``assigned_to``, ``outcome``.

        Returns
        -------
        dict
            Serialised created FollowUp.

        Raises
        ------
        MissingFieldError
            If ``lead_id`` or ``scheduled_at`` are absent.
        LeadNotFoundError
            If the referenced Lead does not exist.
        FollowUpDateInPastError
            If ``scheduled_at`` is not a future datetime.
        InvalidFieldError
            If ``follow_up_type`` is not in the allowed set.
        """
        logger.info("FollowUpService.create_followup | lead_id=%s", data.get("lead_id"))

        missing = [f for f in ("lead_id", "scheduled_at") if not data.get(f)]
        if missing:
            raise MissingFieldError(missing)

        # Validate lead existence – raises LeadNotFoundError if absent
        self._lead_repo.get_by_id(int(data["lead_id"]))

        follow_up_type = data.get("follow_up_type", "call")
        if follow_up_type not in _VALID_TYPES:
            raise InvalidFieldError(
                "follow_up_type",
                f"Allowed values: {sorted(_VALID_TYPES)}. Got: '{follow_up_type}'.",
            )

        scheduled_at = self._parse_and_validate_scheduled_at(data["scheduled_at"])

        cleaned = {
            "lead_id": int(data["lead_id"]),
            "follow_up_type": follow_up_type,
            "scheduled_at": scheduled_at,
            "status": "pending",
            "assigned_to": data.get("assigned_to", "").strip() or None,
            "outcome": data.get("outcome", "").strip() or None,
        }

        followup = self._followup_repo.create(cleaned)
        logger.info("FollowUpService.create_followup: success | id=%d", followup.id)
        return followup.to_dict()

    # ------------------------------------------------------------------

    def get_followup(self, followup_id: int) -> dict:
        """
        Fetch a single FollowUp by ID.

        Raises
        ------
        FollowUpNotFoundError
        """
        return self._followup_repo.get_by_id(followup_id).to_dict()

    # ------------------------------------------------------------------

    def list_followups_for_lead(
        self,
        lead_id: int,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """
        Return paginated FollowUps belonging to a Lead.

        Raises
        ------
        LeadNotFoundError
            If the Lead does not exist.
        InvalidFieldError
            If ``status`` is not one of the allowed values.
        """
        # Validate lead exists
        self._lead_repo.get_by_id(lead_id)

        if status and status not in _VALID_STATUSES:
            raise InvalidFieldError("status", f"Allowed: {sorted(_VALID_STATUSES)}.")

        page = max(1, int(page))
        per_page = min(max(1, int(per_page)), 100)

        result = self._followup_repo.get_all_for_lead(
            lead_id=lead_id, status=status, page=page, per_page=per_page
        )
        result["items"] = [f.to_dict() for f in result["items"]]
        return result

    # ------------------------------------------------------------------

    def list_pending_followups(self, page: int = 1, per_page: int = 20) -> dict:
        """Return all pending FollowUps across all Leads, sorted by scheduled_at ascending."""
        page = max(1, int(page))
        per_page = min(max(1, int(per_page)), 100)
        result = self._followup_repo.get_pending(page=page, per_page=per_page)
        result["items"] = [f.to_dict() for f in result["items"]]
        return result

    # ------------------------------------------------------------------

    def update_followup(self, followup_id: int, data: dict) -> dict:
        """
        Apply a partial update to a FollowUp.

        Business rules:
          - A ``completed`` or ``cancelled`` follow-up cannot be re-opened to ``pending``.
          - If ``outcome`` is supplied without ``status=completed``, the outcome is stored
            but the status is not automatically changed.

        Raises
        ------
        FollowUpNotFoundError
        BusinessRuleViolationError
            If someone tries to re-open a terminal-state follow-up.
        FollowUpDateInPastError
            If a new ``scheduled_at`` is in the past.
        """
        logger.info("FollowUpService.update_followup | id=%d", followup_id)

        if not data:
            raise ValidationError("At least one field must be supplied for update.")

        followup = self._followup_repo.get_by_id(followup_id)
        cleaned: dict = {}

        # --- Status rule ---
        if "status" in data:
            new_status = data["status"]
            if new_status not in _VALID_STATUSES:
                raise InvalidFieldError("status", f"Allowed: {sorted(_VALID_STATUSES)}.")
            if followup.status in ("completed", "cancelled") and new_status == "pending":
                raise BusinessRuleViolationError(
                    message=(
                        f"A follow-up in '{followup.status}' state cannot be re-opened to "
                        "'pending'. Cancel and create a new follow-up instead."
                    ),
                    rule="followup_no_reopen",
                )
            cleaned["status"] = new_status

        if "follow_up_type" in data:
            if data["follow_up_type"] not in _VALID_TYPES:
                raise InvalidFieldError(
                    "follow_up_type",
                    f"Allowed: {sorted(_VALID_TYPES)}. Got: '{data['follow_up_type']}'.",
                )
            cleaned["follow_up_type"] = data["follow_up_type"]

        if "scheduled_at" in data:
            cleaned["scheduled_at"] = self._parse_and_validate_scheduled_at(
                data["scheduled_at"]
            )

        if "assigned_to" in data:
            cleaned["assigned_to"] = data["assigned_to"].strip() if data["assigned_to"] else None

        if "outcome" in data:
            cleaned["outcome"] = data["outcome"].strip() if data["outcome"] else None

        updated = self._followup_repo.update(followup_id, cleaned)
        return updated.to_dict()

    # ------------------------------------------------------------------

    def delete_followup(self, followup_id: int) -> dict:
        """
        Delete a FollowUp.

        Raises
        ------
        FollowUpNotFoundError
        """
        logger.info("FollowUpService.delete_followup | id=%d", followup_id)
        followup = self._followup_repo.get_by_id(followup_id)
        self._followup_repo.delete(followup_id)
        return {
            "message": f"FollowUp id={followup_id} deleted successfully.",
            "deleted_id": followup_id,
        }
