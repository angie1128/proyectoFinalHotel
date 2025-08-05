from app import create_app, db
from app.models import User, Room, RoomType, Reservation, Service, UserRole, RoomStatus
import os

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Room': Room,
        'RoomType': RoomType,
        'Reservation': Reservation,
        'Service': Service,
        'UserRole': UserRole,
        'RoomStatus': RoomStatus
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Crear algunos datos de ejemplo si no existen
        if not RoomType.query.first():
            # Tipos de habitación
            standard = RoomType(
                name='Estándar',
                description='Habitación cómoda con todas las comodidades básicas',
                capacity=2,
                price_per_night=100.00,
                amenities='WiFi, TV, Aire acondicionado, Baño privado'
            )
            
            deluxe = RoomType(
                name='Deluxe',
                description='Habitación espaciosa con vista al mar y amenidades premium',
                capacity=3,
                price_per_night=180.00,
                amenities='WiFi, TV 4K, Aire acondicionado, Minibar, Vista al mar, Balcón'
            )
            
            suite = RoomType(
                name='Suite',
                description='Suite de lujo con sala separada y servicios exclusivos',
                capacity=4,
                price_per_night=300.00,
                amenities='WiFi, TV 4K, Aire acondicionado, Minibar, Jacuzzi, Servicio a la habitación 24h, Vista panorámica'
            )
            
            db.session.add_all([standard, deluxe, suite])
            db.session.commit()
            
            # Habitaciones de ejemplo
            rooms_data = [
                (101, 1, standard.id), (102, 1, standard.id), (103, 1, deluxe.id),
                (201, 2, standard.id), (202, 2, deluxe.id), (203, 2, suite.id),
                (301, 3, deluxe.id), (302, 3, suite.id), (303, 3, suite.id)
            ]
            
            for number, floor, room_type_id in rooms_data:
                room = Room(
                    number=str(number),
                    floor=floor,
                    room_type_id=room_type_id,
                    status=RoomStatus.AVAILABLE
                )
                db.session.add(room)
            
            # Servicios adicionales
            services_data = [
                ('Servicio a la habitación', 'Comida y bebidas entregadas a su habitación', 25.00, 'Alimentación'),
                ('Spa y masajes', 'Relajación completa con masajes profesionales', 80.00, 'Bienestar'),
                ('Lavandería', 'Servicio de lavado y planchado de ropa', 15.00, 'Servicios'),
                ('Transporte al aeropuerto', 'Traslado cómodo desde y hacia el aeropuerto', 35.00, 'Transporte'),
                ('Tour guiado', 'Conoce la ciudad con nuestros guías expertos', 60.00, 'Entretenimiento')
            ]
            
            for name, description, price, category in services_data:
                service = Service(
                    name=name,
                    description=description,
                    price=price,
                    category=category
                )
                db.session.add(service)
            
            db.session.commit()
            print("Datos de ejemplo creados exitosamente!")
    
    app.run(debug=True, host='0.0.0.0', port=8086)
