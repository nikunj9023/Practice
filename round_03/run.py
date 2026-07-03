from app import create_app
from app.extensions import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Ensure database tables are created before running
        db.create_all()
    
    # Run the application
    app.run(debug=True, port=5000)
