from .main.main_routes import main_bp
from .auth.auth_routes import auth_bp
from .booking.booking_routes import booking_bp
from .admin.admin_routes import admin_bp
from .receptionist.receptionist_routes import receptionist_bp

__all__ = ['main_bp', 'auth_bp', 'booking_bp', 'admin_bp', 'receptionist_bp']
