from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    special_requests = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def nights(self):
        return (self.check_out - self.check_in).days
    
    @property
    def status_display(self):
        status_map = {
            'pending': 'Pendiente',
            'confirmed': 'Confirmada',
            'cancelled': 'Cancelada'
        }
        return status_map.get(self.status, self.status)
    
    def calculate_total_price(self):
        if self.room:
            return float(self.room.price_per_night) * self.nights
        return 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'room_id': self.room_id,
            'room_name': self.room.name if self.room else None,
            'check_in': self.check_in.isoformat(),
            'check_out': self.check_out.isoformat(),
            'guests': self.guests,
            'nights': self.nights,
            'total_price': float(self.total_price),
            'status': self.status,
            'status_display': self.status_display,
            'special_requests': self.special_requests,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Booking {self.id} - {self.user.username if self.user else "Unknown"}>'
