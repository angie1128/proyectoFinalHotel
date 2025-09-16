import click
from app import create_app, db
from app.models.user import User
from app.models.room import Room

app = create_app()

@app.cli.command("seed")
def seed():
    """Carga datos iniciales (admin y habitaciones de ejemplo)"""
    with app.app_context():
        # -------------------------------
        # Usuario admin
        # -------------------------------
        admin_user = User.query.filter_by(email='admin@hotel.com').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@hotel.com',
                role='administrador'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            click.echo("✅ Usuario admin creado")
        else:
            click.echo("ℹ️ Usuario admin ya existe")

        # -------------------------------
        # Habitaciones de ejemplo
        # -------------------------------
        if Room.query.count() == 0:
            sample_rooms = [
                Room(number='101', type='individual', price=80.00, status='disponible',
                     description='Habitación individual con vista al jardín', image='Hab1.png'),
                Room(number='102', type='doble', price=120.00, status='disponible',
                     description='Habitación doble con balcón', image='Hab2.png'),
                Room(number='201', type='suite', price=200.00, status='disponible',
                     description='Suite presidencial con jacuzzi', image='Hab3.png'),
                Room(number='202', type='familiar', price=150.00, status='disponible',
                     description='Habitación familiar para 4 personas', image='Hab5.png'),
            ]
            db.session.add_all(sample_rooms)
            click.echo("✅ Habitaciones de ejemplo creadas")
        else:
            click.echo("ℹ️ Ya existen habitaciones en la BD")

        db.session.commit()
        click.echo("🎉 Seed completado")
