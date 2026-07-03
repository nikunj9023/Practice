# Round 10 – Mini CRM (Live Pair Programming)

## Architecture Overview

This project implements a **production-grade Mini CRM** backend using **Clean Architecture**
with three strict layers: Repository → Service → Controller (Blueprint).

```
round_10/
├── app/
│   ├── __init__.py              ← Application Factory (create_app)
│   ├── extensions.py            ← Shared Flask extension singletons (SQLAlchemy)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── customer.py          ← Customer ORM model
│   │   ├── lead.py              ← Lead ORM model (state machine)
│   │   ├── followup.py          ← FollowUp ORM model
│   │   └── note.py              ← Note ORM model (pinning support)
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── customer_repository.py   ← CRUD + search + email-exists
│   │   ├── lead_repository.py       ← CRUD + status/customer_id filters
│   │   ├── followup_repository.py   ← CRUD + lead-scoped + pending list
│   │   └── note_repository.py       ← CRUD + pinning sort + category filter
│   ├── services/
│   │   ├── __init__.py
│   │   ├── customer_service.py  ← Validation, uniqueness, business rules
│   │   ├── lead_service.py      ← State machine + Lead→Customer conversion
│   │   ├── followup_service.py  ← Future-date enforcement, re-open prevention
│   │   └── note_service.py      ← Content limits, pin/unpin idempotency
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── customer_routes.py   ← Blueprint: /api/v1/customers/
│   │   ├── lead_routes.py       ← Blueprint: /api/v1/leads/ + /convert
│   │   ├── followup_routes.py   ← Blueprint: nested + /followups/pending
│   │   └── note_routes.py       ← Blueprint: nested + /pin /unpin
│   └── utils/
│       ├── __init__.py
│       ├── exceptions.py        ← Domain exception hierarchy + error handlers
│       └── logger.py            ← Structured rotating-file logger
├── instance/                    ← SQLite database files (gitignored)
├── logs/                        ← Rotating log files (gitignored)
├── config.py                    ← Development / Testing / Production configs
├── run.py                       ← Development server entry point
└── requirements.txt
```

---

## API Reference

### Base URL: `http://localhost:5000`

### Customers  `/api/v1/customers/`

| Method | Endpoint                        | Description                        |
|--------|---------------------------------|------------------------------------|
| POST   | `/api/v1/customers/`            | Create a customer                  |
| GET    | `/api/v1/customers/`            | List customers (filter + paginate) |
| GET    | `/api/v1/customers/search?q=…`  | Search by name / email / company   |
| GET    | `/api/v1/customers/<id>`        | Get single customer                |
| PATCH  | `/api/v1/customers/<id>`        | Partial update                     |
| DELETE | `/api/v1/customers/<id>`        | Hard delete (cascade)              |

### Leads  `/api/v1/leads/`

| Method | Endpoint                        | Description                                    |
|--------|---------------------------------|------------------------------------------------|
| POST   | `/api/v1/leads/`                | Create a lead (status = `new`)                 |
| GET    | `/api/v1/leads/`                | List leads (filter by status / customer_id)    |
| GET    | `/api/v1/leads/<id>`            | Get single lead                                |
| PATCH  | `/api/v1/leads/<id>`            | Partial update / advance status state machine  |
| POST   | `/api/v1/leads/<id>/convert`    | Convert `qualified` lead → Customer            |
| DELETE | `/api/v1/leads/<id>`            | Hard delete (cascade follow-ups)               |

**Lead Status State Machine:**
```
new → contacted → qualified → converted (terminal)
 ↘         ↘           ↘
  lost      lost        lost          (terminal)
```

### Follow-Ups

| Method | Endpoint                                      | Description                        |
|--------|-----------------------------------------------|------------------------------------|
| POST   | `/api/v1/leads/<lead_id>/followups/`          | Create follow-up for a lead        |
| GET    | `/api/v1/leads/<lead_id>/followups/`          | List follow-ups for a lead         |
| GET    | `/api/v1/followups/pending`                   | All pending follow-ups (dashboard) |
| GET    | `/api/v1/followups/<id>`                      | Get single follow-up               |
| PATCH  | `/api/v1/followups/<id>`                      | Update (complete / reschedule)     |
| DELETE | `/api/v1/followups/<id>`                      | Hard delete                        |

### Notes

| Method | Endpoint                                      | Description                        |
|--------|-----------------------------------------------|------------------------------------|
| POST   | `/api/v1/customers/<customer_id>/notes/`      | Create note for a customer         |
| GET    | `/api/v1/customers/<customer_id>/notes/`      | List notes (pinned first)          |
| GET    | `/api/v1/notes/<id>`                          | Get single note                    |
| PATCH  | `/api/v1/notes/<id>`                          | Partial update                     |
| DELETE | `/api/v1/notes/<id>`                          | Hard delete                        |
| POST   | `/api/v1/notes/<id>/pin`                      | Pin a note (idempotent)            |
| DELETE | `/api/v1/notes/<id>/pin`                      | Unpin a note (idempotent)          |

---

## Running the Server

```bash
cd Practice/round_10

# Install dependencies
pip install -r requirements.txt

# Start development server
python3 run.py
# → http://localhost:5000
```

## Key Design Decisions

### Repository Pattern
Every repository is the single source of truth for its model's DB access.
It raises only **domain exceptions** — never raw `SQLAlchemyError`.

### Service Layer
Services are **framework-agnostic** — they import nothing from Flask.
They receive plain Python dicts and return plain Python dicts.
All validation, business rules, and state-machine enforcement live here.

### Controller / Blueprint Layer
Routes only:
1. Parse the HTTP request (`request.get_json()`, query params, path vars).
2. Call the appropriate service method.
3. Return a uniform JSON envelope with the correct HTTP status code.

### Exception Hierarchy
```
CRMBaseException
├── ValidationError
│   ├── MissingFieldError        → 400
│   └── InvalidFieldError        → 400
├── NotFoundError                → 404
│   ├── CustomerNotFoundError
│   ├── LeadNotFoundError
│   ├── FollowUpNotFoundError
│   └── NoteNotFoundError
├── DuplicateResourceError       → 409
│   └── DuplicateCustomerEmailError
├── BusinessRuleViolationError   → 403
│   ├── LeadAlreadyConvertedError
│   ├── InvalidLeadStatusTransitionError
│   └── FollowUpDateInPastError
├── UnprocessableEntityError     → 422
└── RepositoryError              → 500
```

All exceptions are caught by the **global error handler** in `exceptions.py`
and serialised into a consistent JSON envelope:
```json
{
  "error": "CustomerNotFoundError",
  "message": "Customer with identifier '99' was not found.",
  "status_code": 404,
  "details": { "resource": "Customer", "identifier": "99" }
}
```
