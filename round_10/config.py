"""
config.py
==========
Centralised configuration for all environments.

Usage in the app factory::

    app.config.from_object(get_config())

Environment is selected by the ``FLASK_ENV`` environment variable
(defaults to ``development``).
"""

from __future__ import annotations

import os
from pathlib import Path

# Base directory of the project (where this file lives)
BASE_DIR = Path(__file__).resolve().parent


class BaseConfig:
    """Settings shared by every environment."""

    # Flask
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JSON_SORT_KEYS: bool = False
    PROPAGATE_EXCEPTIONS: bool = False

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ECHO: bool = False               # Set True to log all SQL
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "pool_pre_ping": True,                  # Detect stale connections
        "pool_recycle": 300,                    # Recycle connections every 5 min
    }

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Pagination defaults (informational; enforced in the service layer)
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100


class DevelopmentConfig(BaseConfig):
    """Local development – verbose logging, local SQLite database."""

    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'crm_dev.db'}",
    )
    SQLALCHEMY_ECHO: bool = True


class TestingConfig(BaseConfig):
    """Unit / integration tests – in-memory SQLite so no disk state leaks."""

    TESTING: bool = True
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    WTF_CSRF_ENABLED: bool = False


class ProductionConfig(BaseConfig):
    """Production – uses DATABASE_URL env var; SQLALCHEMY_ECHO is off."""

    DEBUG: bool = False
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'crm_prod.db'}",
    )

    # In production, always override SECRET_KEY from the environment.
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")


# ---------------------------------------------------------------------------
# Config resolver
# ---------------------------------------------------------------------------

_CONFIG_MAP: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config() -> type[BaseConfig]:
    """Return the correct config class based on ``FLASK_ENV``."""
    env = os.getenv("FLASK_ENV", "development").lower()
    config_class = _CONFIG_MAP.get(env, DevelopmentConfig)
    return config_class
