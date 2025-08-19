from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.room import Room
from app.models.reservation import Reservation

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Get featured rooms for carousel
    featured_rooms = Room.query.filter_by(status='disponible').limit(6).all()
    return render_template('main/index.html', featured_rooms=featured_rooms)

@main_bp.route('/rooms')
def rooms():
    rooms = Room.query.filter_by(status='disponible').all()
    return render_template('main/rooms.html', rooms=rooms)

@main_bp.route('/about')
def about():
    return render_template('main/about.html')

@main_bp.route('/contact')
def contact():
    return render_template('main/contact.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    elif current_user.is_receptionist():
        return redirect(url_for('receptionist.dashboard'))
    else:
        return redirect(url_for('guest.dashboard'))
