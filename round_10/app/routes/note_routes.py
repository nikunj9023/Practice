"""
app/routes/note_routes.py
===========================
Flask Blueprint for the Note REST API.

Notes are always scoped to a Customer; they are nested under the customer
resource for creation and listing, and addressed directly for single-record
operations.

API Surface
-----------
  POST   /api/v1/customers/<customer_id>/notes/     Create a note for a customer
  GET    /api/v1/customers/<customer_id>/notes/     List notes for a customer
  GET    /api/v1/notes/<id>                         Get single note
  PATCH  /api/v1/notes/<id>                         Partial update
  DELETE /api/v1/notes/<id>                         Hard delete
  POST   /api/v1/notes/<id>/pin                     Pin a note
  DELETE /api/v1/notes/<id>/pin                     Unpin a note
"""

from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request

from app.services.note_service import NoteService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Blueprint registration
# ---------------------------------------------------------------------------

note_bp = Blueprint("notes", __name__)

_service = NoteService()


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
# Nested routes: /api/v1/customers/<customer_id>/notes/
# ---------------------------------------------------------------------------


@note_bp.post("/api/v1/customers/<int:customer_id>/notes/")
def create_note(customer_id: int):
    """
    Create a Note linked to a Customer.

    **Path parameter**: ``customer_id`` (integer)

    **Request body** (JSON):

    .. code-block:: json

        {
            "title":     "Discovery call summary",
            "content":   "Client is interested in the annual plan.",
            "category":  "call",
            "is_pinned": false,
            "author":    "Nikunj Parmar"
        }

    **Responses**:
        - ``201 Created``     – note created
        - ``400 Bad Request`` – missing / invalid fields
        - ``404 Not Found``   – customer not found
    """
    logger.debug("POST /api/v1/customers/%d/notes/", customer_id)
    body = request.get_json(silent=True) or {}
    body["customer_id"] = customer_id   # Inject from path
    result = _service.create_note(body)
    return _success(result, 201)


@note_bp.get("/api/v1/customers/<int:customer_id>/notes/")
def list_notes_for_customer(customer_id: int):
    """
    List Notes for a Customer, pinned notes first.

    **Query parameters**:
        - ``category``    – ``general`` | ``meeting`` | ``call`` | ``email`` | ``important`` | ``other``
        - ``pinned_only`` – ``true`` to return only pinned notes
        - ``page``        – page number (default: 1)
        - ``per_page``    – records per page (default: 20, max: 100)

    **Responses**:
        - ``200 OK``      – paginated note list
        - ``404 Not Found`` – customer not found
    """
    logger.debug("GET /api/v1/customers/%d/notes/", customer_id)
    category = request.args.get("category") or None
    pinned_only = request.args.get("pinned_only", "false").lower() == "true"
    page, per_page = _get_pagination_params()
    result = _service.list_notes_for_customer(
        customer_id=customer_id,
        category=category,
        pinned_only=pinned_only,
        page=page,
        per_page=per_page,
    )
    return _paginated(result)


# ---------------------------------------------------------------------------
# Top-level routes: /api/v1/notes/<id>
# ---------------------------------------------------------------------------


@note_bp.get("/api/v1/notes/<int:note_id>")
def get_note(note_id: int):
    """
    Retrieve a single Note by ID.

    **Responses**:
        - ``200 OK``      – note record
        - ``404 Not Found`` – note not found
    """
    logger.debug("GET /api/v1/notes/%d", note_id)
    result = _service.get_note(note_id)
    return _success(result)


@note_bp.patch("/api/v1/notes/<int:note_id>")
def update_note(note_id: int):
    """
    Partially update a Note (PATCH semantics).

    **Request body** (JSON, all fields optional):

    .. code-block:: json

        {
            "title":     "Updated title",
            "content":   "Revised note content.",
            "category":  "important",
            "is_pinned": true
        }

    **Responses**:
        - ``200 OK``      – updated note
        - ``400 Bad Request`` – invalid field values
        - ``404 Not Found``   – note not found
    """
    logger.debug("PATCH /api/v1/notes/%d", note_id)
    body = request.get_json(silent=True) or {}
    result = _service.update_note(note_id, body)
    return _success(result)


@note_bp.delete("/api/v1/notes/<int:note_id>")
def delete_note(note_id: int):
    """
    Hard-delete a Note.

    **Responses**:
        - ``200 OK``      – deletion confirmation
        - ``404 Not Found`` – note not found
    """
    logger.debug("DELETE /api/v1/notes/%d", note_id)
    result = _service.delete_note(note_id)
    return _success(result)


@note_bp.post("/api/v1/notes/<int:note_id>/pin")
def pin_note(note_id: int):
    """
    Pin a Note so it appears at the top of its customer's note list.

    Idempotent – calling on an already-pinned note returns ``200 OK``
    with the unchanged record.

    **Responses**:
        - ``200 OK``      – note (pinned)
        - ``404 Not Found`` – note not found
    """
    logger.debug("POST /api/v1/notes/%d/pin", note_id)
    result = _service.pin_note(note_id)
    return _success(result)


@note_bp.delete("/api/v1/notes/<int:note_id>/pin")
def unpin_note(note_id: int):
    """
    Unpin a Note.

    Idempotent – calling on an already-unpinned note returns ``200 OK``.

    **Responses**:
        - ``200 OK``      – note (unpinned)
        - ``404 Not Found`` – note not found
    """
    logger.debug("DELETE /api/v1/notes/%d/pin", note_id)
    result = _service.unpin_note(note_id)
    return _success(result)
