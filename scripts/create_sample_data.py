"""
Script para crear datos de muestra en la base de datos del hotel
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.room import Room
from app.models.reservation import Reservation
from datetime import datetime, date, timedelta
import random

def create_sample_data():
    app = create_app()
    
    with app.app_context():
        print("Creando datos de muestra...")
        
        # Crear usuarios de muestra
        users_data = [
            {
                'username': 'recepcionista1',
                'email': 'recepcionista@hotel.com',
                'first_name': 'María',
                'last_name': 'González',
                'phone': '+1234567890',
                'role': 'recepcionista',
                'password': 'recep123'
            },
            {
                'username': 'juan_perez',
                'email': 'juan@email.com',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'phone': '+1234567891',
                'role': 'huesped',
                'password': 'guest123'
            },
            {
                'username': 'ana_martinez',
                'email': 'ana@email.com',
                'first_name': 'Ana',
                'last_name': 'Martínez',
                'phone': '+1234567892',
                'role': 'huesped',
                'password': 'guest123'
            },
            {
                'username': 'carlos_lopez',
                'email': 'carlos@email.com',
                'first_name': 'Carlos',
                'last_name': 'López',
                'phone': '+1234567893',
                'role': 'huesped',
                'password': 'guest123'
            }
        ]
        
        created_users = []
        for user_data in users_data:
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    phone=user_data['phone'],
                    role=user_data['role']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                created_users.append(user)
                print(f"Usuario creado: {user.username} ({user.role})")
        
        # Crear habitaciones adicionales
        additional_rooms = [
            {'number': '103', 'type': 'individual', 'price': 85.00, 'description': 'Habitación individual con escritorio'},
            {'number': '104', 'type': 'doble', 'price': 125.00, 'description': 'Habitación doble con vista al mar'},
            {'number': '105', 'type': 'familiar', 'price': 160.00, 'description': 'Habitación familiar con cocina'},
            {'number': '203', 'type': 'suite', 'price': 220.00, 'description': 'Suite ejecutiva con sala de estar'},
            {'number': '204', 'type': 'doble', 'price': 130.00, 'description': 'Habitación doble premium'},
            {'number': '301', 'type': 'suite', 'price': 250.00, 'description': 'Suite presidencial con terraza'},
            {'number': '302', 'type': 'individual', 'price': 90.00, 'description': 'Habitación individual premium'},
            {'number': '303', 'type': 'familiar', 'price': 170.00, 'description': 'Habitación familiar deluxe'}
        ]
        
        for room_data in additional_rooms:
            existing_room = Room.query.filter_by(number=room_data['number']).first()
            if not existing_room:
                room = Room(
                    number=room_data['number'],
                    type=room_data['type'],
                    price=room_data['price'],
                    description=room_data['description'],
                    status='disponible',
                    max_occupancy=2 if room_data['type'] == 'individual' else 4 if room_data['type'] == 'familiar' else 3
                )
                db.session.add(room)
                print(f"Habitación creada: {room.number} - {room.get_type_display()}")
        
        db.session.commit()
        
        # Crear reservaciones de muestra
        guest_users = User.query.filter_by(role='huesped').all()
        available_rooms = Room.query.filter_by(status='disponible').all()
        
        if guest_users and available_rooms:
            # Reservaciones pasadas
            for i in range(5):
                guest = random.choice(guest_users)
                room = random.choice(available_rooms)
                
                check_in = date.today() - timedelta(days=random.randint(30, 90))
                check_out = check_in + timedelta(days=random.randint(1, 7))
                nights = (check_out - check_in).days
                
                reservation = Reservation(
                    guest_id=guest.id,
                    room_id=room.id,
                    check_in_date=check_in,
                    check_out_date=check_out,
                    guests_count=random.randint(1, room.max_occupancy),
                    total_price=room.price * nights,
                    status='completada',
                    checked_in_at=datetime.combine(check_in, datetime.min.time()),
                    checked_out_at=datetime.combine(check_out, datetime.min.time())
                )
                db.session.add(reservation)
                print(f"Reservación completada creada: {guest.get_full_name()} - Habitación {room.number}")
            
            # Reservaciones futuras
            for i in range(3):
                guest = random.choice(guest_users)
                room = random.choice(available_rooms)
                
                check_in = date.today() + timedelta(days=random.randint(1, 30))
                check_out = check_in + timedelta(days=random.randint(2, 10))
                nights = (check_out - check_in).days
                
                status = random.choice(['pendiente', 'confirmada'])
                
                reservation = Reservation(
                    guest_id=guest.id,
                    room_id=room.id,
                    check_in_date=check_in,
                    check_out_date=check_out,
                    guests_count=random.randint(1, room.max_occupancy),
                    total_price=room.price * nights,
                    status=status,
                    special_requests='Solicitud de ejemplo' if random.choice([True, False]) else None
                )
                
                if status == 'confirmada':
                    admin_user = User.query.filter_by(role='administrador').first()
                    if admin_user:
                        reservation.confirmed_by_id = admin_user.id
                        reservation.confirmed_at = datetime.utcnow()
                
                db.session.add(reservation)
                print(f"Reservación {status} creada: {guest.get_full_name()} - Habitación {room.number}")
        
        db.session.commit()
        print("\n¡Datos de muestra creados exitosamente!")
        print("\nCredenciales de acceso:")
        print("Administrador: admin@hotel.com / admin123")
        print("Recepcionista: recepcionista@hotel.com / recep123")
        print("Huéspedes: juan@email.com, ana@email.com, carlos@email.com / guest123")

if __name__ == '__main__':
    create_sample_data()
