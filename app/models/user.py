from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='huesped')  # huesped, recepcionista, administrador
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    reservations = db.relationship('Reservation', foreign_keys='Reservation.guest_id', backref='guest', lazy=True)
    confirmed_reservations = db.relationship('Reservation', foreign_keys='Reservation.confirmed_by_id', backref='confirmed_by_staff', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'administrador'
    
    def is_receptionist(self):
        return self.role == 'recepcionista'
    
    def is_guest(self):
        return self.role == 'huesped'
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def get_role_display(self):
        roles = {
            'huesped': 'Huésped',
            'recepcionista': 'Recepcionista',
            'administrador': 'Administrador'
        }
        return roles.get(self.role, self.role.title())
    
    def __repr__(self):
        return f'<User {self.username}>'
