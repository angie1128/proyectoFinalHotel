#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos de ejemplo
"""

import sys
import os

# Agregar el directorio padre al path para importar la app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Room, Booking
from datetime import datetime, date, timedelta
import json

def init_database():
    """Inicializa la base de datos con datos de ejemplo"""
    
    app = create_app()
    
    with app.app_context():
        print("🗑️ Eliminando tablas existentes...")
        db.drop_all()
        
        # Crear todas las tablas
        print("🔨 Creando tablas de base de datos...")
        db.create_all()
        print("✅ Tablas de base de datos creadas")
        
        # Crear usuario administrador
        create_admin_user()
        
        # Crear recepcionista de ejemplo
        create_sample_receptionist()
        
        # Crear habitaciones de ejemplo
        create_sample_rooms()
        
        # Crear usuarios huéspedes de ejemplo
        create_sample_users()
        
        print("🎉 Base de datos inicializada correctamente!")

def create_admin_user():
    """Crea el usuario administrador"""
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        admin = User(
            username='admin',
            email='admin@hotelboutique.com',
            first_name='Administrador',
            last_name='Hotel',
            phone='+1234567890',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("👤 Usuario administrador creado (admin/admin123)")
    else:
        print("👤 Usuario administrador ya existe")

def create_sample_receptionist():
    """Crea un recepcionista de ejemplo"""
    receptionist = User.query.filter_by(username='recepcion').first()
    
    if not receptionist:
        receptionist = User(
            username='recepcion',
            email='recepcion@hotelboutique.com',
            first_name='Ana',
            last_name='Martínez',
            phone='+1234567899',
            role='receptionist'
        )
        receptionist.set_password('recepcion123')
        db.session.add(receptionist)
        db.session.commit()
        print("👤 Usuario recepcionista creado (recepcion/recepcion123)")
    else:
        print("👤 Usuario recepcionista ya existe")

def create_sample_rooms():
    """Crea habitaciones de ejemplo"""
    if Room.query.count() > 0:
        print("🏨 Las habitaciones ya existen")
        return
    
    rooms_data = [
        {
            'name': 'Suite Presidencial',
            'description': 'La suite más lujosa del hotel con vista panorámica a la ciudad. Incluye sala de estar, dormitorio principal, baño de mármol con jacuzzi, terraza privada de 50m² y servicio de mayordomo personal las 24 horas.',
            'price_per_night': 450.00,
            'capacity': 4,
            'room_type': 'suite',
            'amenities': json.dumps(['WiFi premium', 'TV 75" OLED', 'Sistema de sonido Bose', 'Minibar premium', 'Jacuzzi', 'Terraza privada', 'Servicio de mayordomo 24h', 'Caja fuerte', 'Aire acondicionado inteligente']),
            'image_url': '/placeholder.svg?height=400&width=600',
            'is_available': True
        },
        {
            'name': 'Suite Junior',
            'description': 'Elegante suite con sala de estar separada y todas las comodidades modernas. Perfecta para estancias de negocios o placer. Incluye escritorio ejecutivo y área de reuniones.',
            'price_per_night': 280.00,
            'capacity': 3,
            'room_type': 'suite',
            'amenities': json.dumps(['WiFi premium', 'TV 65" 4K', 'Minibar', 'Escritorio ejecutivo', 'Balcón', 'Cafetera Nespresso', 'Caja fuerte', 'Aire acondicionado']),
            'image_url': '/placeholder.svg?height=400&width=600',
            'is_available': True
        },
        {
            'name': 'Habitación Deluxe',
            'description': 'Habitación espaciosa con decoración contemporánea y vista a los jardines del hotel. Ideal para parejas que buscan romance y tranquilidad en un ambiente sofisticado.',
            'price_per_night': 180.00,
            'capacity': 2,
            'room_type': 'deluxe',
            'amenities': json.dumps(['WiFi', 'TV 55" Smart', 'Minibar', 'Cafetera', 'Vista a jardines', 'Balcón privado', 'Caja fuerte', 'Aire acondicionado']),
            'image_url': '/placeholder.svg?height=400&width=600',
            'is_available': True
        },
        {
            'name': 'Habitación Superior',
            'description': 'Habitación confortable con todas las amenidades básicas y un toque de elegancia. Perfecta para viajeros de negocios que valoran la funcionalidad y el confort.',
            'price_per_night': 120.00,
            'capacity': 2,
            'room_type': 'superior',
            'amenities': json.dumps(['WiFi', 'TV 43" Smart', 'Escritorio', 'Cafetera', 'Caja fuerte', 'Aire acondicionado', 'Plancha']),
            'image_url': '/placeholder.svg?height=400&width=600',
            'is_available': True
        },
        {
            'name': 'Habitación Estándar',
            'description': 'Habitación acogedora con todo lo necesario para una estancia cómoda. Excelente relación calidad-precio sin comprometer la calidad del servicio.',
            'price_per_night': 85.00,
            'capacity': 2,
            'room_type': 'standard',
            'amenities': json.dumps(['WiFi', 'TV 40" Smart', 'Cafetera', 'Caja fuerte', 'Aire acondicionado']),
            'image_url': '/placeholder.svg?height=400&width=600',
            'is_available': True
        },
        {
            'name': 'Suite Familiar',
            'description': 'Amplia suite con dos dormitorios conectados, perfecta para familias. Incluye área de juegos para niños, cocina equipada y amplio balcón con vista a la piscina.',
            'price_per_night': 320.00,
            'capacity': 6,
            'room_type': 'family',
            'amenities': json.dumps(['WiFi', 'TV 55" en cada habitación', 'Cocina equipada', 'Área de juegos', 'Balcón grande', 'Microondas', 'Refrigerador', 'Caja fuerte']),
            'image_url': '/placeholder.svg?height=400&width=600',
            'is_available': True
        },
        {
            'name': 'Suite Ejecutiva',
            'description': 'Suite diseñada especialmente para ejecutivos, con oficina privada, sala de reuniones y acceso al lounge ejecutivo. Incluye servicios de secretaría.',
            'price_per_night': 380.00,
            'capacity': 2,
            'room_type': 'executive',
            'amenities': json.dumps(['WiFi premium', 'TV 65"', 'Oficina privada', 'Impresora', 'Fax', 'Acceso lounge ejecutivo', 'Servicio de secretaría', 'Minibar premium']),
            'image_url': '/placeholder.svg?height=400&width=600',
            'is_available': True
        },
        {
            'name': 'Habitación Económica',
            'description': 'Habitación funcional y limpia, ideal para viajeros con presupuesto ajustado que no quieren renunciar a la calidad del servicio.',
            'price_per_night': 65.00,
            'capacity': 1,
            'room_type': 'economy',
            'amenities': json.dumps(['WiFi', 'TV 32"', 'Escritorio pequeño', 'Cafetera', 'Aire acondicionado']),
            'image_url': '/placeholder.svg?height=400&width=600',
            'is_available': True
        }
    ]
    
    for room_data in rooms_data:
        room = Room(**room_data)
        db.session.add(room)
    
    db.session.commit()
    print(f"🏨 {len(rooms_data)} habitaciones creadas")

def create_sample_users():
    """Crea usuarios huéspedes de ejemplo"""
    sample_users = [
        {
            'username': 'juan_perez',
            'email': 'juan.perez@email.com',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'phone': '+1234567891',
            'password': 'password123',
            'role': 'guest'
        },
        {
            'username': 'maria_garcia',
            'email': 'maria.garcia@email.com',
            'first_name': 'María',
            'last_name': 'García',
            'phone': '+1234567892',
            'password': 'password123',
            'role': 'guest'
        },
        {
            'username': 'carlos_rodriguez',
            'email': 'carlos.rodriguez@email.com',
            'first_name': 'Carlos',
            'last_name': 'Rodríguez',
            'phone': '+1234567893',
            'password': 'password123',
            'role': 'guest'
        },
        {
            'username': 'ana_martinez',
            'email': 'ana.martinez@email.com',
            'first_name': 'Ana',
            'last_name': 'Martínez',
            'phone': '+1234567894',
            'password': 'password123',
            'role': 'guest'
        },
        {
            'username': 'luis_gonzalez',
            'email': 'luis.gonzalez@email.com',
            'first_name': 'Luis',
            'last_name': 'González',
            'phone': '+1234567895',
            'password': 'password123',
            'role': 'guest'
        },
        {
            'username': 'sofia_lopez',
            'email': 'sofia.lopez@email.com',
            'first_name': 'Sofía',
            'last_name': 'López',
            'phone': '+1234567896',
            'password': 'password123',
            'role': 'guest'
        },
        {
            'username': 'diego_hernandez',
            'email': 'diego.hernandez@email.com',
            'first_name': 'Diego',
            'last_name': 'Hernández',
            'phone': '+1234567897',
            'password': 'password123',
            'role': 'guest'
        },
        {
            'username': 'valentina_torres',
            'email': 'valentina.torres@email.com',
            'first_name': 'Valentina',
            'last_name': 'Torres',
            'phone': '+1234567898',
            'password': 'password123',
            'role': 'guest'
        }
    ]
    
    created_count = 0
    for user_data in sample_users:
        if not User.query.filter_by(username=user_data['username']).first():
            password = user_data.pop('password')
            user = User(**user_data)
            user.set_password(password)
            db.session.add(user)
            created_count += 1
    
    db.session.commit()
    print(f"👥 {created_count} usuarios huéspedes de ejemplo creados")

if __name__ == '__main__':
    init_database()
