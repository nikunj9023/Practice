"""
app/routes/customer_routes.py
==============================
Flask Blueprint for the Customer REST API.

Responsibility boundary:
  - HTTP request parsing (JSON body, query parameters, path variables)
  - Calling the CustomerService with clean Python values
  - Mapping service results → deterministic HTTP status codes
  - Returning uniform JSON envelopes

No business logic, validation, or database code lives here.

API Surface
-----------
  POST   /api/v1/customers/                     Create a customer
  GET    /api/v1/customers/                     List / paginate customers
  GET    /api/v1/customers/search               Search customers
  GET    /api/v1/customers/<id>                 Get single customer
  PATCH  /api/v1/customers/<id>                 Partial update
  DELETE /api/v1/customers/<id>                 Hard delete
"""

from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request

from app.services.customer_service import CustomerService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Blueprint registration
# ---------------------------------------------------------------------------

customer_bp = Blueprint(
    "customers",
    __name__,
    url_prefix="/api/v1/customers",
)

# Singleton service instance (stateless – safe to share across requests)
_service = CustomerService()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _success(data: dict | list, status_code: int = 200):
    """Wrap a successful result in a uniform JSON envelope."""
    return jsonify({"status": "success", "data": data}), status_code


def _paginated(result: dict, status_code: int = 200):
    """Wrap a paginated service result in a uniform JSON envelope."""
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
    """Extract and coerce pagination query parameters."""
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
    except (TypeError, ValueError):
        page, per_page = 1, 20
    return page, per_page


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@customer_bp.post("/")
def create_customer():
    """
    Create a new Customer.

    **Request body** (JSON):

    .. code-block:: json

        {
            "name":    "Nikunj Parmar",
            "email":   "nikunj@example.com",
            "phone":   "+91-9876543210",
            "company": "Neev Trust",
            "address": "Ahmedabad, Gujarat",
            "status":  "active",
            "source":  "referral"
        }

    **Responses**:
        - ``201 Created`` – customer successfully created
        - ``400 Bad Request`` – missing / invalid fields
        - ``409 Conflict`` – email already registered
    """
    logger.debug("POST /api/v1/customers/")
    body = request.get_json(silent=True) or {}
    result = _service.create_customer(body)
    return _success(result, 201)


@customer_bp.get("/")
def list_customers():
    """
    List customers with optional status filter and pagination.

    **Query parameters**:
        - ``status``   – ``active`` | ``inactive`` | ``archived``
        - ``page``     – page number (default: 1)
        - ``per_page`` – records per page (default: 20, max: 100)

    **Responses**:
        - ``200 OK`` – paginated customer list
        - ``400 Bad Request`` – invalid status value
    """
    logger.debug("GET /api/v1/customers/")
    status = request.args.get("status") or None
    page, per_page = _get_pagination_params()
    result = _service.list_customers(status=status, page=page, per_page=per_page)
    return _paginated(result)


@customer_bp.get("/search")
def search_customers():
    """
    Search customers by name, email, or company (substring match).

    **Query parameters**:
        - ``q``        – search term (minimum 2 characters, required)
        - ``page``     – page number (default: 1)
        - ``per_page`` – records per page (default: 20, max: 100)

    **Responses**:
        - ``200 OK`` – matching customers
        - ``400 Bad Request`` – query too short or missing
    """
    logger.debug("GET /api/v1/customers/search")
    q = request.args.get("q", "")
    page, per_page = _get_pagination_params()
    result = _service.search_customers(query_str=q, page=page, per_page=per_page)
    return _paginated(result)


@customer_bp.get("/<int:customer_id>")
def get_customer(customer_id: int):
    """
    Retrieve a single Customer by ID.

    **Path parameter**: ``customer_id`` (integer)

    **Responses**:
        - ``200 OK`` – customer record
        - ``404 Not Found`` – no customer with that ID
    """
    logger.debug("GET /api/v1/customers/%d", customer_id)
    result = _service.get_customer(customer_id)
    return _success(result)


@customer_bp.patch("/<int:customer_id>")
def update_customer(customer_id: int):
    """
    Partially update a Customer (PATCH semantics – only supplied fields change).

    **Path parameter**: ``customer_id`` (integer)

    **Request body** (JSON, all fields optional):

    .. code-block:: json

        {
            "name":    "Updated Name",
            "phone":   "+91-9000000000",
            "status":  "inactive"
        }

    **Responses**:
        - ``200 OK`` – updated customer record
        - ``400 Bad Request`` – invalid field values
        - ``404 Not Found`` – customer not found
        - ``409 Conflict`` – email collision with another customer
    """
    logger.debug("PATCH /api/v1/customers/%d", customer_id)
    body = request.get_json(silent=True) or {}
    result = _service.update_customer(customer_id, body)
    return _success(result)


@customer_bp.delete("/<int:customer_id>")
def delete_customer(customer_id: int):
    """
    Hard-delete a Customer and all cascade-linked records.

    **Path parameter**: ``customer_id`` (integer)

    **Responses**:
        - ``200 OK`` – deletion confirmation
        - ``404 Not Found`` – customer not found
    """
    logger.debug("DELETE /api/v1/customers/%d", customer_id)
    result = _service.delete_customer(customer_id)
    return _success(result)
