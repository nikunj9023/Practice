"""
app/extensions.py
==================
Initialises and exposes shared Flask extension instances.

Each extension is created WITHOUT an app instance here (the Application
Factory pattern).  They are bound to the app inside ``create_app()`` via
``init_app()``.  This prevents circular imports and makes the extensions
importable from any module without pulling the full app in.
"""

from flask_sqlalchemy import SQLAlchemy

# Single shared SQLAlchemy instance used across all models and repositories.
db: SQLAlchemy = SQLAlchemy()
