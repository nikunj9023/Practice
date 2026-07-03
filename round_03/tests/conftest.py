import pytest
from flask import Flask
from app.extensions import db, init_extensions
from app.routes.auth import auth_bp

def create_test_app():
    """Create a minimal Flask application for testing."""
    app = Flask(__name__)
    
    # Test Configuration
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # In-memory database for isolated tests
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'test-secret-key-123'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False # Tokens don't expire during tests
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    
    return app

@pytest.fixture(scope='session')
def app():
    """Session-wide test Flask application."""
    app = create_test_app()
    yield app

@pytest.fixture(scope='session')
def db_engine(app):
    """Session-wide database engine."""
    with app.app_context():
        # Create all tables in the in-memory database
        db.create_all()
        yield db
        # Drop all tables after the session completes
        db.drop_all()

@pytest.fixture(scope='function')
def db_session(app, db_engine):
    """
    Function-scoped database session.
    Provides an isolated transaction for each test, rolling back changes afterwards.
    """
    with app.app_context():
        connection = db_engine.engine.connect()
        transaction = connection.begin()
        
        # Bind the session to the connection
        options = dict(bind=connection, binds={})
        session = db_engine.create_scoped_session(options=options)
        
        db_engine.session = session
        
        yield session
        
        # Cleanup: Rollback transaction and close connection
        transaction.rollback()
        connection.close()
        session.remove()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def auth_headers(client):
    """
    Helper fixture to authenticate and return headers for a test user.
    """
    def _auth_headers(email="admin@example.com", password="password123"):
        response = client.post('/api/auth/login', json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            token = response.json.get("access_token")
            return {"Authorization": f"Bearer {token}"}
        return {}
    return _auth_headers
