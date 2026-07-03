"""
run.py
=======
Entry point for development server.

Usage::

    python run.py
    # or
    FLASK_ENV=production python run.py

For production deployments, use a WSGI server (Gunicorn/uWSGI)::

    gunicorn "app:create_app()" --bind 0.0.0.0:5000 --workers 4
"""

from __future__ import annotations

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development").lower() != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
