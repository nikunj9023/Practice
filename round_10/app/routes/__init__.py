"""app/routes package."""
from app.routes.customer_routes import customer_bp
from app.routes.lead_routes import lead_bp
from app.routes.followup_routes import followup_bp
from app.routes.note_routes import note_bp

__all__ = ["customer_bp", "lead_bp", "followup_bp", "note_bp"]
