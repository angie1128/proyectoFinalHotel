from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum
from app import db

class UserRole(Enum):
    GUEST = 'guest'
    RECEPTIONIST = 'receptionist'
    HOUSEKEEPING = 'housekeeping'
    ADMIN = 'admin'

class RoomStatus(Enum):
    AVAILABLE = 'available'
    OCCUPIED = 'occupied'
    MAINTENANCE = 'maintenance'
    CLEANING = 'cleaning'

class ReservationStatus(Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CHECKED_IN = 'checked_in'
    CHECKED_OUT = 'checked_out'
    CANCELLED = 'cancelled'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.GUEST)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relaciones
    reservations = db.relationship('Reservation', backref='guest', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_role(self, role):
        return self.role == role

    def __repr__(self):
        return f'<User {self.username}>'

class RoomType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    capacity = db.Column(db.Integer, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    amenities = db.Column(db.Text)  # JSON string
    image_url = db.Column(db.String(200))
    
    # Relaciones
    rooms = db.relationship('Room', backref='room_type', lazy='dynamic')

    def __repr__(self):
        return f'<RoomType {self.name}>'

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), unique=True, nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(RoomStatus), nullable=False, default=RoomStatus.AVAILABLE)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_type.id'), nullable=False)
    notes = db.Column(db.Text)
    last_maintenance = db.Column(db.DateTime)
    
    # Relaciones
    reservations = db.relationship('Reservation', backref='room', lazy='dynamic')

    def is_available(self, check_in, check_out):
        overlapping = Reservation.query.filter(
            Reservation.room_id == self.id,
            Reservation.status.in_([ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN]),
            Reservation.check_out > check_in,
            Reservation.check_in < check_out
        ).first()
        return overlapping is None

    def __repr__(self):
        return f'<Room {self.number}>'

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    adults = db.Column(db.Integer, nullable=False, default=1)
    children = db.Column(db.Integer, nullable=False, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(ReservationStatus), nullable=False, default=ReservationStatus.PENDING)
    special_requests = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    services = db.relationship('ReservationService', backref='reservation', lazy='dynamic')

    @property
    def nights(self):
        return (self.check_out - self.check_in).days

    def calculate_total(self):
        base_amount = self.nights * self.room.room_type.price_per_night
        services_amount = sum([rs.total_amount for rs in self.services])
        return base_amount + services_amount

    def __repr__(self):
        return f'<Reservation {self.id} - Room {self.room.number}>'

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relaciones
    reservation_services = db.relationship('ReservationService', backref='service', lazy='dynamic')

    def __repr__(self):
        return f'<Service {self.name}>'

class ReservationService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ReservationService {self.reservation_id}-{self.service_id}>'
