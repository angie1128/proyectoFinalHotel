from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price_per_night = db.Column(db.Numeric(10, 2), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    amenities = db.Column(db.Text)  # JSON string de amenidades
    image_url = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    bookings = db.relationship('Booking', backref='room', lazy=True)
    
    @property
    def amenities_list(self):
        import json
        try:
            return json.loads(self.amenities) if self.amenities else []
        except:
            return []
    
    def get_amenities(self):
        """Retorna las amenidades como lista"""
        return self.amenities_list
    
    def set_amenities(self, amenities_list):
        import json
        self.amenities = json.dumps(amenities_list)
    
    def is_available_for_dates(self, check_in, check_out):
        from app.models.booking import Booking
        overlapping_bookings = Booking.query.filter(
            Booking.room_id == self.id,
            Booking.status.in_(['confirmed', 'pending']),
            Booking.check_in < check_out,
            Booking.check_out > check_in
        ).count()
        return overlapping_bookings == 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price_per_night': float(self.price_per_night),
            'capacity': self.capacity,
            'room_type': self.room_type,
            'amenities': self.amenities_list,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Room {self.name}>'
