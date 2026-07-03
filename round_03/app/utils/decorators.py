from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def roles_required(*required_roles):
    """
    Decorator for Role-Based Access Control (RBAC).
    Ensures that the current user has one of the specified roles.
    Expects the JWT token to contain a 'role' claim.
    
    Usage:
        @roles_required('Admin', 'HR')
        def some_endpoint():
            ...
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Ensure a valid JWT is present
            verify_jwt_in_request()
            
            # Fetch the JWT claims
            claims = get_jwt()
            user_role = claims.get('role')
            
            if not user_role:
                return jsonify({
                    "error": "Forbidden",
                    "message": "Access denied: Role claim missing in token"
                }), 403
                
            if user_role not in required_roles:
                return jsonify({
                    "error": "Forbidden",
                    "message": f"Access denied: Requires one of {list(required_roles)}, got '{user_role}'"
                }), 403
                
            return fn(*args, **kwargs)
        return decorator
    return wrapper
