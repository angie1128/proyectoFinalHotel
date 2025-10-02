from app import db
from datetime import datetime

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # individual, doble, suite, familiar
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='disponible')  # disponible, ocupada, mantenimiento, limpieza
    description = db.Column(db.Text)
    image = db.Column(db.String(255), nullable=True)  # nombre del archivo de imagen
    amenities = db.Column(db.Text)  # JSON string of amenities
    max_occupancy = db.Column(db.Integer, default=2)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    reservations = db.relationship('Reservation', backref='room', lazy=True)
    
    def is_available(self):
        return self.status == 'disponible'
    
    def get_type_display(self):
        types = {
            'individual': 'Individual',
            'doble': 'Doble',
            'suite': 'Suite',
            'familiar': 'Familiar'
        }
        return types.get(self.type, self.type.title())
    
    def get_status_display(self):
        statuses = {
            'disponible': 'Disponible',
            'ocupada': 'Ocupada',
            'mantenimiento': 'En Mantenimiento',
            'limpieza': 'En Limpieza'
        }
        return statuses.get(self.status, self.status.title())
    
    def get_image_path(self):
        """
        Devuelve la ruta correcta de la imagen.
        - Imágenes seed (Hab1.png, etc.) están en /static/img/hab/
        - Imágenes subidas por admin están en /static/uploads/
        """
        if self.image:
            # Si el nombre de la imagen parece ser de seed (empieza con 'Hab'), usar img/hab/
            if self.image.startswith('Hab') and self.image.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                return f"img/hab/{self.image}"
            # De lo contrario, es una imagen subida, usar uploads/
            else:
                return f"uploads/{self.image}"
        # Si no tiene imagen asignada
        return "img/hab/default.jpg"
    
    def __repr__(self):
        return f'<Room {self.number}>'
