from flask import Blueprint, render_template, redirect, url_for, flash
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

@main_bp.route("/reserve", methods=["GET", "POST"])
def reserve():
    """
    Página de reserva que requiere autenticación para proceder.
    """
    from flask_login import current_user
    from app.forms.reservation import PublicReservationForm
    from datetime import datetime

    if not current_user.is_authenticated:
        # Usuario no autenticado, mostrar mensaje de login requerido
        return render_template("main/reserve.html", requires_login=True)

    form = PublicReservationForm()
    available_rooms = []
    search_performed = False

    if form.validate_on_submit():
        search_performed = True
        check_in = form.check_in_date.data
        check_out = form.check_out_date.data

        if check_in and check_out and check_out > check_in:
            # Find rooms that are available for the selected dates
            # This is a simplified check - in a real app you'd check against existing reservations
            available_rooms = Room.query.filter_by(status='disponible').all()

            # For now, we'll show all available rooms
            # In a production app, you'd filter out rooms that have conflicting reservations
        else:
            flash("Por favor selecciona fechas válidas.", "warning")

    return render_template("main/reserve.html",
                          form=form,
                          available_rooms=available_rooms,
                          search_performed=search_performed,
                          requires_login=False)
