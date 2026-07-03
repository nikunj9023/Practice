from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import logging
from flask import request

# Database and ORM
db = SQLAlchemy()
migrate = Migrate()

# JWT Authentication
jwt = JWTManager()

# Centralized Logger setup
def setup_logger(app):
    # Configure basic logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('flask.app')
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)
    
    # Audit log specific method
    def audit_log(action, user_id, details=None):
        logger.info(f"AUDIT | User: {user_id} | Action: {action} | IP: {request.remote_addr} | Details: {details}")
    
    app.audit_log = audit_log

def init_extensions(app):
    """Initializes all Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    setup_logger(app)
