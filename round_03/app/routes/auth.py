from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
from werkzeug.security import check_password_hash
from app.utils.decorators import roles_required
# In a real app, you would import the User model here:
# from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Mock data for demonstration purposes
MOCK_USERS = {
    "admin@example.com": {
        "id": 1,
        "password_hash": "scrypt:32768:8:1$vT0M1vT8$8e8d8869c9b4d8c6b71f98d7811985c7885b5a7a72d312891918a38b29", # password is "password123"
        "role": "Admin",
        "is_active": True
    },
    "employee@example.com": {
        "id": 2,
        "password_hash": "scrypt:32768:8:1$vT0M1vT8$8e8d8869c9b4d8c6b71f98d7811985c7885b5a7a72d312891918a38b29", # password is "password123"
        "role": "Employee",
        "is_active": True
    }
}

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return Access & Refresh tokens.
    """
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Bad Request", "message": "Email and password are required"}), 400

    email = data.get('email')
    password = data.get('password')

    # Mock user retrieval - replace with DB query: User.query.filter_by(email=email).first()
    user = MOCK_USERS.get(email)
    
    if not user:
        return jsonify({"error": "Unauthorized", "message": "Invalid email or password"}), 401
        
    if not user.get('is_active'):
        return jsonify({"error": "Forbidden", "message": "Account is inactive. Please contact support."}), 403

    # Verify password (using a dummy check for boilerplate since we use mock)
    # In real app: if not check_password_hash(user.password_hash, password):
    if password != "password123": 
        return jsonify({"error": "Unauthorized", "message": "Invalid email or password"}), 401

    # Create tokens
    # Identity is typically user ID. Additional claims store roles.
    identity = {"id": user.get('id'), "email": email}
    additional_claims = {"role": user.get('role')}
    
    access_token = create_access_token(identity=identity, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=identity, additional_claims=additional_claims)

    # Centralized audit log example
    if hasattr(current_app, 'audit_log'):
        current_app.audit_log("LOGIN_SUCCESS", user.get('id'), details="User logged in successfully")

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.get('id'),
            "email": email,
            "role": user.get('role')
        }
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """
    Refresh access token using the refresh token.
    """
    identity = get_jwt_identity()
    claims = get_jwt()
    
    # We pass the same role claim to the new access token
    additional_claims = {"role": claims.get('role')}
    
    new_access_token = create_access_token(identity=identity, additional_claims=additional_claims)
    
    return jsonify({
        "message": "Token refreshed successfully",
        "access_token": new_access_token
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get details of the currently authenticated user.
    """
    identity = get_jwt_identity()
    claims = get_jwt()
    
    return jsonify({
        "user": {
            "id": identity.get('id') if isinstance(identity, dict) else identity,
            "email": identity.get('email') if isinstance(identity, dict) else None,
            "role": claims.get('role')
        }
    }), 200


# Example of RBAC Protected Route
@auth_bp.route('/admin-only', methods=['GET'])
@jwt_required()
@roles_required('Admin')
def admin_dashboard():
    """
    Demonstrates an endpoint protected by RBAC. Only 'Admin' can access.
    """
    identity = get_jwt_identity()
    return jsonify({
        "message": "Welcome to the Admin Dashboard!",
        "user_id": identity.get('id') if isinstance(identity, dict) else identity
    }), 200
