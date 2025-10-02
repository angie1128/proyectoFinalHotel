from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.room import Room
from app.models.reservation import Reservation

main_bp = Blueprint('main', __name__)

# Página principal (Index) con habitaciones dinámicas
@main_bp.route("/")
def index():
    """
    Renderiza la página principal mostrando habitaciones disponibles.
    """
    try:
        rooms = Room.query.filter_by(status="disponible").all()
        print(f"Found {len(rooms)} available rooms")  # Debug logging
        return render_template("main/index.html", rooms=rooms)
    except Exception as e:
        print(f"Database error: {e}")  # Debug logging
        return render_template("main/index.html", rooms=[])

# Página "Sobre nosotros"
@main_bp.route('/about')
def about():
    """
    Renderiza la página "Sobre nosotros".
    """
    return render_template('main/about.html')

# Página "Contacto"
@main_bp.route('/contact')
def contact():
    """
    Renderiza la página de contacto.
    """
    return render_template('main/contact.html')

# Dashboard según el rol del usuario
@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Redirige al dashboard apropiado según el rol del usuario autenticado.
    """
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    elif current_user.is_receptionist():
        return redirect(url_for('receptionist.dashboard'))
    else:
        return redirect(url_for('guest.dashboard'))

@main_bp.route("/rooms")
def rooms():
    """
    Renderiza la página de habitaciones mostrando todas las habitaciones.
    """
    rooms = Room.query.all()
    return render_template("main/rooms.html", rooms=rooms)
