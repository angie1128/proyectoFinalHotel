from app import db
from datetime import datetime

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    guests_count = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pendiente')  # pendiente, confirmada, cancelada, completada
    special_requests = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    checked_in_at = db.Column(db.DateTime)
    checked_out_at = db.Column(db.DateTime)
    confirmed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    payment_type = db.Column(db.String(50))      # NUEVO
    payment_detail = db.Column(db.String(200)) 
    def get_status_display(self):
        status_map = {
        'pending': 'Pendiente',
        'pendiente': 'Pendiente',
        'confirmed': 'Confirmada',
        'confirmada': 'Confirmada',
        'cancelled': 'Cancelada',
        'cancelada': 'Cancelada',
        'completed': 'Completada',
        'completada': 'Completada'
        }
        return status_map.get(self.status, self.status)

    def get_nights_count(self):
        return (self.check_out_date - self.check_in_date).days
    
    def can_check_in(self):
        return self.status == 'confirmada' and not self.checked_in_at
    
    def can_check_out(self):
        return self.checked_in_at and not self.checked_out_at
    
    def __repr__(self):
        return f'<Reservation {self.id}>'
