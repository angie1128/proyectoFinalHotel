#!/usr/bin/env python3
"""
Script para crear usuarios de prueba en el sistema hotelero
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, UserRole

def create_test_users():
    app = create_app()
    
    with app.app_context():
        # Crear usuarios de prueba si no existen
        test_users = [
            {
                'username': 'admin_test',
                'email': 'admin@hotel.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'Principal',
                'phone': '+1234567890',
                'role': UserRole.ADMIN
            },
            {
                'username': 'recepcionista1',
                'email': 'recepcion@hotel.com',
                'password': 'recep123',
                'first_name': 'María',
                'last_name': 'González',
                'phone': '+1234567891',
                'role': UserRole.RECEPTIONIST
            },
            {
                'username': 'limpieza1',
                'email': 'limpieza@hotel.com',
                'password': 'limpi123',
                'first_name': 'Carlos',
                'last_name': 'Rodríguez',
                'phone': '+1234567892',
                'role': UserRole.HOUSEKEEPING
            },
            {
                'username': 'huesped1',
                'email': 'huesped@hotel.com',
                'password': 'guest123',
                'first_name': 'Ana',
                'last_name': 'Martínez',
                'phone': '+1234567893',
                'role': UserRole.GUEST
            }
        ]
        
        created_users = []
        
        for user_data in test_users:
            # Verificar si el usuario ya existe
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
                created_users.append(user_data)
        
        try:
            db.session.commit()
            print("✅ Usuarios de prueba creados exitosamente:")
            print("\n📋 CREDENCIALES DE PRUEBA:")
            print("=" * 50)
            
            for user_data in created_users:
                print(f"\n🔑 {user_data['role'].value.upper()}")
                print(f"   Email: {user_data['email']}")
                print(f"   Contraseña: {user_data['password']}")
                print(f"   Nombre: {user_data['first_name']} {user_data['last_name']}")
            
            if not created_users:
                print("ℹ️  Los usuarios de prueba ya existen en la base de datos")
                print("\n📋 CREDENCIALES EXISTENTES:")
                print("=" * 50)
                for user_data in test_users:
                    print(f"\n🔑 {user_data['role'].value.upper()}")
                    print(f"   Email: {user_data['email']}")
                    print(f"   Contraseña: {user_data['password']}")
                    
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear usuarios: {e}")

if __name__ == '__main__':
    create_test_users()
