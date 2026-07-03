from flask import Flask
from flask_cors import CORS
from app.extensions import init_extensions
from app.routes.auth import auth_bp
from app.routes.employees import employees_bp
from app.routes.attendance import attendance_bp
from app.routes.leaves import leaves_bp

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'dev-secret-key-123'
    
    # Initialize extensions
    init_extensions(app)
    
    # Enable CORS for all routes (allows React frontend on :5173)
    CORS(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(leaves_bp)
    
    @app.route('/')
    def index():
        return {"message": "Welcome to the API Boilerplate. Available endpoints are under /api/auth"}
    
    return app
