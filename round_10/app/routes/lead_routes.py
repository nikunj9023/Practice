"""
app/routes/lead_routes.py
===========================
Flask Blueprint for the Lead REST API.

API Surface
-----------
  POST   /api/v1/leads/                         Create a lead
  GET    /api/v1/leads/                         List / paginate leads
  GET    /api/v1/leads/<id>                     Get single lead
  PATCH  /api/v1/leads/<id>                     Partial update (incl. status transition)
  POST   /api/v1/leads/<id>/convert             Convert lead → customer
  DELETE /api/v1/leads/<id>                     Hard delete
"""

from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request

from app.services.lead_service import LeadService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Blueprint registration
# ---------------------------------------------------------------------------

lead_bp = Blueprint(
    "leads",
    __name__,
    url_prefix="/api/v1/leads",
)

_service = LeadService()


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
# Endpoints
# ---------------------------------------------------------------------------


@lead_bp.post("/")
def create_lead():
    """
    Create a new Lead in the ``new`` status.

    **Request body** (JSON):

    .. code-block:: json

        {
            "title":           "Software Licence Deal",
            "first_name":      "Ravi",
            "last_name":       "Shah",
            "email":           "ravi@example.com",
            "phone":           "+91-9876543210",
            "company":         "Tech Corp",
            "source":          "web",
            "estimated_value": 75000.00,
            "notes":           "Interested in annual subscription."
        }

    **Responses**:
        - ``201 Created``    – lead successfully created
        - ``400 Bad Request``– missing / invalid fields
    """
    logger.debug("POST /api/v1/leads/")
    body = request.get_json(silent=True) or {}
    result = _service.create_lead(body)
    return _success(result, 201)


@lead_bp.get("/")
def list_leads():
    """
    List leads with optional filters and pagination.

    **Query parameters**:
        - ``status``      – ``new`` | ``contacted`` | ``qualified`` | ``converted`` | ``lost``
        - ``customer_id`` – filter by linked customer (integer)
        - ``page``        – page number (default: 1)
        - ``per_page``    – records per page (default: 20, max: 100)

    **Responses**:
        - ``200 OK`` – paginated lead list
    """
    logger.debug("GET /api/v1/leads/")
    status = request.args.get("status") or None
    customer_id_raw = request.args.get("customer_id")
    try:
        customer_id = int(customer_id_raw) if customer_id_raw else None
    except (TypeError, ValueError):
        customer_id = None
    page, per_page = _get_pagination_params()
    result = _service.list_leads(
        status=status, customer_id=customer_id, page=page, per_page=per_page
    )
    return _paginated(result)


@lead_bp.get("/<int:lead_id>")
def get_lead(lead_id: int):
    """
    Retrieve a single Lead by ID.

    **Responses**:
        - ``200 OK``      – lead record
        - ``404 Not Found`` – no lead with that ID
    """
    logger.debug("GET /api/v1/leads/%d", lead_id)
    result = _service.get_lead(lead_id)
    return _success(result)


@lead_bp.patch("/<int:lead_id>")
def update_lead(lead_id: int):
    """
    Partially update a Lead.

    Advancing the lead through the status state machine is done via this
    endpoint by including a ``status`` field in the body.

    **State machine** (allowed transitions)::

        new → contacted | lost
        contacted → qualified | lost
        qualified → converted | lost
        converted → (terminal)
        lost → (terminal)

    **Responses**:
        - ``200 OK``    – updated lead
        - ``400 Bad Request`` – invalid field or disallowed status transition
        - ``403 Forbidden``   – attempt to transition from a terminal state
        - ``404 Not Found``   – lead not found
    """
    logger.debug("PATCH /api/v1/leads/%d", lead_id)
    body = request.get_json(silent=True) or {}
    result = _service.update_lead(lead_id, body)
    return _success(result)


@lead_bp.post("/<int:lead_id>/convert")
def convert_lead(lead_id: int):
    """
    Convert a **qualified** Lead into a Customer.

    This endpoint triggers the CRM's core conversion workflow:
      1. Validates the lead is in the ``qualified`` state.
      2. Creates (or links to an existing) Customer from lead data.
      3. Marks the lead as ``converted`` and stores ``customer_id``.

    **Responses**:
        - ``200 OK``   – ``{lead: {...}, customer: {...}, message: "…"}``
        - ``403 Forbidden`` – lead already converted or not yet qualified
        - ``404 Not Found`` – lead not found
    """
    logger.debug("POST /api/v1/leads/%d/convert", lead_id)
    result = _service.convert_lead(lead_id)
    return _success(result)


@lead_bp.delete("/<int:lead_id>")
def delete_lead(lead_id: int):
    """
    Hard-delete a Lead and its cascade-linked FollowUps.

    **Responses**:
        - ``200 OK``      – deletion confirmation
        - ``404 Not Found`` – lead not found
    """
    logger.debug("DELETE /api/v1/leads/%d", lead_id)
    result = _service.delete_lead(lead_id)
    return _success(result)
