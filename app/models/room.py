from app import db
from datetime import datetime

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # individual, doble, suite, familiar
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='disponible')  # disponible, ocupada, mantenimiento, limpieza
    description = db.Column(db.Text)
    image = db.Column(db.String(255), nullable=True)  # solo guardamos "Hab1.png"
    amenities = db.Column(db.Text)  # JSON string of amenities
    max_occupancy = db.Column(db.Integer, default=2)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
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
        Devuelve la ruta relativa al static para renderizar en templates.
        """
        if self.image:
            return f"img/hab/{self.image}"
        return "img/hab/default.jpg"
    
    def __repr__(self):
        return f'<Room {self.number}>'
