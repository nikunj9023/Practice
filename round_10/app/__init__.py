"""
app/__init__.py
================
Application Factory.

All Flask extension bindings, blueprint registrations, error handler
attachments, and database table creations happen here and only here.

Usage::

    from app import create_app
    app = create_app()
"""

from __future__ import annotations

import logging

from flask import Flask, jsonify

from config import get_config
from app.extensions import db
from app.utils.logger import setup_logging
from app.utils.exceptions import register_error_handlers


def create_app(config_override: dict | None = None) -> Flask:
    """
    Flask Application Factory.

    Parameters
    ----------
    config_override : dict | None
        Optional mapping of configuration keys to override.
        Primarily used in tests to switch to the testing config.

    Returns
    -------
    Flask
        A fully configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)

    # ----------------------------------------------------------------
    # 1. Configuration
    # ----------------------------------------------------------------
    app.config.from_object(get_config())
    if config_override:
        app.config.update(config_override)

    # ----------------------------------------------------------------
    # 2. Logging (must happen before anything else that logs)
    # ----------------------------------------------------------------
    setup_logging(level=app.config.get("LOG_LEVEL", "INFO"))
    logger = logging.getLogger(__name__)
    logger.info("Starting Mini CRM | env=%s", app.config.get("ENV", "development"))

    # ----------------------------------------------------------------
    # 3. Extensions
    # ----------------------------------------------------------------
    db.init_app(app)

    # ----------------------------------------------------------------
    # 4. Register models so SQLAlchemy can see them before create_all()
    # ----------------------------------------------------------------
    with app.app_context():
        # Import all models here to ensure their tables are created.
        from app.models.customer import Customer   # noqa: F401
        from app.models.lead import Lead           # noqa: F401
        from app.models.followup import FollowUp   # noqa: F401
        from app.models.note import Note           # noqa: F401

        db.create_all()
        logger.info("Database tables verified / created.")

    # ----------------------------------------------------------------
    # 5. Register Blueprints
    # ----------------------------------------------------------------
    from app.routes.customer_routes import customer_bp
    from app.routes.lead_routes import lead_bp
    from app.routes.followup_routes import followup_bp
    from app.routes.note_routes import note_bp

    app.register_blueprint(customer_bp)
    app.register_blueprint(lead_bp)
    app.register_blueprint(followup_bp)
    app.register_blueprint(note_bp)

    logger.info(
        "Blueprints registered: customers, leads, followups, notes"
    )

    # ----------------------------------------------------------------
    # 6. Global error handlers
    # ----------------------------------------------------------------
    register_error_handlers(app)

    # ----------------------------------------------------------------
    # 7. Health-check endpoint
    # ----------------------------------------------------------------
    @app.get("/health")
    def health_check():
        """
        Liveness probe endpoint.

        Returns ``200 OK`` with a JSON body when the application is running.
        Used by load-balancers and CI pipelines to confirm the server is up.
        """
        return jsonify({"status": "ok", "service": "Mini CRM API", "version": "1.0.0"})

    # ----------------------------------------------------------------
    # 8. API root / documentation index
    # ----------------------------------------------------------------
    @app.get("/api/v1/")
    def api_index():
        """Return a machine-readable listing of available API resource groups."""
        return jsonify(
            {
                "status": "success",
                "data": {
                    "version": "1.0.0",
                    "resources": {
                        "customers": "/api/v1/customers/",
                        "leads": "/api/v1/leads/",
                        "followups (nested)": "/api/v1/leads/<lead_id>/followups/",
                        "followups (pending)": "/api/v1/followups/pending",
                        "notes (nested)": "/api/v1/customers/<customer_id>/notes/",
                    },
                },
            }
        )

    return app
