import os
from flask_migrate import upgrade
from app import create_app, db
from app.models import User, Room, Booking

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Room': Room, 
        'Booking': Booking
    }

@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # Create database tables
    db.create_all()
    
    # Create sample data
    create_sample_data()

def create_sample_data():
    """Create sample rooms and admin user."""
    
    # Create admin user if it doesn't exist
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@hotelboutique.com',
            first_name='Admin',
            last_name='Hotel',
            phone='+1234567890',
            role='admin'  # Usando el nuevo sistema de roles
        )
        admin.set_password('admin123')
        db.session.add(admin)
    
    # Create receptionist user if it doesn't exist
    receptionist = User.query.filter_by(username='recepcion').first()
    if not receptionist:
        receptionist = User(
            username='recepcion',
            email='recepcion@hotelboutique.com',
            first_name='María',
            last_name='García',
            phone='+1234567891',
            role='receptionist'  # Agregando usuario recepcionista
        )
        receptionist.set_password('recepcion123')
        db.session.add(receptionist)
    
    # Create sample rooms if they don't exist
    if Room.query.count() == 0:
        rooms = [
            Room(
                name='Suite Presidencial',
                description='La suite más lujosa del hotel con vista panorámica a la ciudad. Incluye sala de estar, dormitorio principal, baño de mármol y terraza privada.',
                price_per_night=450.00,
                capacity=4,
                room_type='suite',
                image_url='/placeholder.svg?height=400&width=600',
                is_available=True
            ),
            Room(
                name='Suite Junior',
                description='Elegante suite con sala de estar separada y todas las comodidades modernas. Perfecta para estancias de negocios o placer.',
                price_per_night=280.00,
                capacity=3,
                room_type='suite',
                image_url='/placeholder.svg?height=400&width=600',
                is_available=True
            ),
            Room(
                name='Habitación Deluxe',
                description='Habitación espaciosa con decoración contemporánea y vista a los jardines del hotel. Ideal para parejas.',
                price_per_night=180.00,
                capacity=2,
                room_type='deluxe',
                image_url='/placeholder.svg?height=400&width=600',
                is_available=True
            ),
            Room(
                name='Habitación Superior',
                description='Habitación confortable con todas las amenidades básicas y un toque de elegancia. Perfecta para viajeros de negocios.',
                price_per_night=120.00,
                capacity=2,
                room_type='superior',
                image_url='/placeholder.svg?height=400&width=600',
                is_available=True
            ),
            Room(
                name='Habitación Estándar',
                description='Habitación acogedora con todo lo necesario para una estancia cómoda. Excelente relación calidad-precio.',
                price_per_night=85.00,
                capacity=2,
                room_type='standard',
                image_url='/placeholder.svg?height=400&width=600',
                is_available=True
            ),
            Room(
                name='Suite Familiar',
                description='Amplia suite con dos dormitorios, perfecta para familias. Incluye área de juegos para niños y cocina pequeña.',
                price_per_night=320.00,
                capacity=6,
                room_type='family',
                image_url='/placeholder.svg?height=400&width=600',
                is_available=True
            )
        ]
        
        for room in rooms:
            amenities = ['WiFi', 'TV', 'Minibar', 'Aire Acondicionado']
            if room.room_type == 'suite':
                amenities.extend(['Jacuzzi', 'Terraza', 'Servicio 24h'])
            elif room.room_type == 'family':
                amenities.extend(['Cocina', 'Área de juegos'])
            room.set_amenities(amenities)
            db.session.add(room)
    
    db.session.commit()
    print("Sample data created successfully!")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
