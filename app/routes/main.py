from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.room import Room
from app.models.reservation import Reservation

main_bp = Blueprint('main', __name__)

# Página principal (Index) con habitaciones dinámicas
@main_bp.route("/")
def index():
    rooms = Room.query.filter_by(status="disponible").all()
    return render_template("main/index.html", rooms=rooms)

# Página "Sobre nosotros"
@main_bp.route('/about')
def about():
    return render_template('main/about.html')

# Página "Contacto"
@main_bp.route('/contact')
def contact():
    return render_template('main/contact.html')

# Dashboard según el rol del usuario
@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    elif current_user.is_receptionist():
        return redirect(url_for('receptionist.dashboard'))
    else:
        return redirect(url_for('guest.dashboard'))
@main_bp.route("/rooms")
def rooms():
    from app.models.room import Room
    rooms = Room.query.all()
    return render_template("rooms.html", rooms=rooms)
