from datetime import datetime
from app.extensions import db
from sqlalchemy.orm import declared_attr
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

def get_current_user_id():
    """Helper to retrieve current user ID from JWT if available."""
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity and isinstance(identity, dict):
            return identity.get('id')
        return identity
    except Exception:
        return None

class AuditMixin(object):
    """
    Base Mixin containing common columns and Audit Trail functionality.
    Provides standard fields: id, created_at, updated_at, created_by, updated_by.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @declared_attr
    def created_by(cls):
        return db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
        
    @declared_attr
    def updated_by(cls):
        return db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def save(self):
        """Saves the instance to the database."""
        user_id = get_current_user_id()
        if not self.id:
            self.created_by = user_id
        self.updated_by = user_id
        
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
            
    def delete(self):
        """Deletes the instance from the database."""
        db.session.delete(self)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
            
    def update(self, **kwargs):
        """Updates attributes and saves."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()

    @classmethod
    def get_by_id(cls, record_id):
        """Fetch record by ID."""
        return db.session.query(cls).get(record_id)
        
    def to_dict(self):
        """Convert object to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
