from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Cargar configuración desde Config
    if config_class is None:
        from config import DevelopmentConfig
        config_class = DevelopmentConfig
    app.config.from_object(config_class)

    # Carpeta de subida de imágenes
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'img', 'hab')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    # Modelos
    from app.models.user import User
    from app.models.room import Room
    from app.models.reservation import Reservation
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
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
    
    return app
