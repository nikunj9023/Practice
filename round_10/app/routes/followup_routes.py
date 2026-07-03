"""
app/routes/followup_routes.py
==============================
Flask Blueprint for the FollowUp REST API.

All FollowUp routes are nested under their parent Lead for discoverability,
with a separate top-level endpoint to retrieve all pending follow-ups.

API Surface
-----------
  POST   /api/v1/leads/<lead_id>/followups/          Create a follow-up for a lead
  GET    /api/v1/leads/<lead_id>/followups/          List follow-ups for a lead
  GET    /api/v1/followups/pending                   List all pending follow-ups
  GET    /api/v1/followups/<id>                      Get single follow-up
  PATCH  /api/v1/followups/<id>                      Partial update
  DELETE /api/v1/followups/<id>                      Hard delete
"""

from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request

from app.services.followup_service import FollowUpService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Blueprint registration – two URL prefixes handled via a single blueprint
# ---------------------------------------------------------------------------

followup_bp = Blueprint(
    "followups",
    __name__,
)

_service = FollowUpService()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _success(data: dict | list, status_code: int = 200):
    return jsonify({"status": "success", "data": data}), status_code


def _paginated(result: dict, status_code: int = 200):
    return (
        jsonify(
            {
                "status": "success",
                "data": result["items"],
                "meta": {
                    "total": result["total"],
                    "page": result["page"],
                    "per_page": result["per_page"],
                    "pages": result["pages"],
                },
            }
        ),
        status_code,
    )


def _get_pagination_params():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
    except (TypeError, ValueError):
        page, per_page = 1, 20
    return page, per_page


# ---------------------------------------------------------------------------
# Nested routes: /api/v1/leads/<lead_id>/followups/
# ---------------------------------------------------------------------------


@followup_bp.post("/api/v1/leads/<int:lead_id>/followups/")
def create_followup(lead_id: int):
    """
    Schedule a new FollowUp for a Lead.

    **Path parameter**: ``lead_id`` (integer)

    **Request body** (JSON):

    .. code-block:: json

        {
            "follow_up_type": "call",
            "scheduled_at":   "2026-12-31T10:00:00+05:30",
            "assigned_to":    "Nikunj Parmar",
            "outcome":        null
        }

    **Responses**:
        - ``201 Created``     – follow-up created
        - ``400 Bad Request`` – missing / invalid fields or past date
        - ``403 Forbidden``   – business rule violation
        - ``404 Not Found``   – lead not found
    """
    logger.debug("POST /api/v1/leads/%d/followups/", lead_id)
    body = request.get_json(silent=True) or {}
    # Inject lead_id from the path so callers don't have to repeat it in body
    body["lead_id"] = lead_id
    result = _service.create_followup(body)
    return _success(result, 201)


@followup_bp.get("/api/v1/leads/<int:lead_id>/followups/")
def list_followups_for_lead(lead_id: int):
    """
    List FollowUps belonging to a specific Lead.

    **Query parameters**:
        - ``status``   – ``pending`` | ``completed`` | ``cancelled``
        - ``page``     – page number (default: 1)
        - ``per_page`` – records per page (default: 20, max: 100)

    **Responses**:
        - ``200 OK``      – paginated follow-up list
        - ``404 Not Found`` – lead not found
    """
    logger.debug("GET /api/v1/leads/%d/followups/", lead_id)
    status = request.args.get("status") or None
    page, per_page = _get_pagination_params()
    result = _service.list_followups_for_lead(
        lead_id=lead_id, status=status, page=page, per_page=per_page
    )
    return _paginated(result)


# ---------------------------------------------------------------------------
# Top-level routes: /api/v1/followups/
# ---------------------------------------------------------------------------


@followup_bp.get("/api/v1/followups/pending")
def list_pending_followups():
    """
    List all pending FollowUps across all Leads, sorted by scheduled_at ascending.

    Useful for a CRM agent's daily dashboard view.

    **Query parameters**:
        - ``page``     – page number (default: 1)
        - ``per_page`` – records per page (default: 20, max: 100)

    **Responses**:
        - ``200 OK`` – paginated list of pending follow-ups
    """
    logger.debug("GET /api/v1/followups/pending")
    page, per_page = _get_pagination_params()
    result = _service.list_pending_followups(page=page, per_page=per_page)
    return _paginated(result)


@followup_bp.get("/api/v1/followups/<int:followup_id>")
def get_followup(followup_id: int):
    """
    Retrieve a single FollowUp by ID.

    **Responses**:
        - ``200 OK``      – follow-up record
        - ``404 Not Found`` – follow-up not found
    """
    logger.debug("GET /api/v1/followups/%d", followup_id)
    result = _service.get_followup(followup_id)
    return _success(result)


@followup_bp.patch("/api/v1/followups/<int:followup_id>")
def update_followup(followup_id: int):
    """
    Partially update a FollowUp.

    Common use-cases:
      - Mark as completed:  ``{"status": "completed", "outcome": "Agreed to demo."}``
      - Mark as cancelled:  ``{"status": "cancelled"}``
      - Reschedule:         ``{"scheduled_at": "2026-11-01T14:00:00+05:30"}``

    Business rules enforced:
      - A ``completed`` or ``cancelled`` follow-up **cannot** be re-opened to ``pending``.
      - ``scheduled_at`` must be a future datetime.

    **Responses**:
        - ``200 OK``      – updated follow-up
        - ``400 Bad Request`` – invalid fields or past date
        - ``403 Forbidden``   – attempt to re-open a terminal-state follow-up
        - ``404 Not Found``   – follow-up not found
    """
    logger.debug("PATCH /api/v1/followups/%d", followup_id)
    body = request.get_json(silent=True) or {}
    result = _service.update_followup(followup_id, body)
    return _success(result)


@followup_bp.delete("/api/v1/followups/<int:followup_id>")
def delete_followup(followup_id: int):
    """
    Hard-delete a FollowUp.

    **Responses**:
        - ``200 OK``      – deletion confirmation
        - ``404 Not Found`` – follow-up not found
    """
    logger.debug("DELETE /api/v1/followups/%d", followup_id)
    result = _service.delete_followup(followup_id)
    return _success(result)
