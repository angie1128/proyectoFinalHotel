from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # -------------------------------
    # Configuración
    # -------------------------------
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///hotel.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # -------------------------------
    # Inicializar extensiones
    # -------------------------------
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # -------------------------------
    # Modelos
    # -------------------------------
    from app.models.user import User
    from app.models.room import Room
    from app.models.reservation import Reservation
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # -------------------------------
    # Blueprints
    # -------------------------------
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    from app.routes.receptionist import receptionist_bp
    from app.routes.guest import guest_bp
    
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(receptionist_bp, url_prefix="/receptionist")
    app.register_blueprint(guest_bp, url_prefix="/guest")
    
    # -------------------------------
    # Crear tablas y datos de prueba
    # -------------------------------
    with app.app_context():
        db.create_all()
        
        # Crear usuario admin si no existe
        admin_user = User.query.filter_by(email='admin@hotel.com').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@hotel.com',
                role='administrador'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            
            # Habitaciones de ejemplo
            sample_rooms = [
                Room(number='101', type='individual', price=80.00, status='disponible', description='Habitación individual con vista al jardín'),
                Room(number='102', type='doble', price=120.00, status='disponible', description='Habitación doble con balcón'),
                Room(number='201', type='suite', price=200.00, status='disponible', description='Suite presidencial con jacuzzi'),
                Room(number='202', type='familiar', price=150.00, status='disponible', description='Habitación familiar para 4 personas'),
            ]
            
            for room in sample_rooms:
                db.session.add(room)
            
            db.session.commit()
    
    return app
