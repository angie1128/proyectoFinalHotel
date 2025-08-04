from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Crear directorio de uploads si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from app.routes import main
    app.register_blueprint(main)
    
    with app.app_context():
        db.create_all()
        # Crear usuario administrador por defecto
        create_default_admin()
    
    return app

def create_default_admin():
    from app.models import User, UserRole
    admin = User.query.filter_by(email='admin@hotel.com').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@hotel.com',
            first_name='Administrador',
            last_name='Sistema',
            role=UserRole.ADMIN
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
