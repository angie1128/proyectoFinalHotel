from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.room import Room
from app.models.booking import Booking
from datetime import datetime, timedelta
from functools import wraps

receptionist_bp = Blueprint('receptionist', __name__, url_prefix='/receptionist')

def receptionist_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_manage_bookings:
            flash('Acceso denegado. Se requieren permisos de recepcionista.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@receptionist_bp.route('/dashboard')
@login_required
@receptionist_required
def dashboard():
    # Estadísticas para recepcionista
    today = datetime.now().date()
    
    # Reservas de hoy
    today_checkins = Booking.query.filter(
        db.func.date(Booking.check_in) == today
    ).count()
    
    today_checkouts = Booking.query.filter(
        db.func.date(Booking.check_out) == today
    ).count()
    
    # Habitaciones disponibles
    occupied_rooms = db.session.query(Room.id).join(Booking).filter(
        Booking.check_in <= today,
        Booking.check_out > today,
        Booking.status == 'confirmed'
    ).subquery()
    
    available_rooms = Room.query.filter(~Room.id.in_(occupied_rooms)).count()
    total_rooms = Room.query.count()
    
    # Reservas recientes
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    
    return render_template('receptionist/dashboard.html',
                         today_checkins=today_checkins,
                         today_checkouts=today_checkouts,
                         available_rooms=available_rooms,
                         total_rooms=total_rooms,
                         recent_bookings=recent_bookings)

@receptionist_bp.route('/bookings')
@login_required
@receptionist_required
def manage_bookings():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('receptionist/manage_bookings.html', bookings=bookings)

@receptionist_bp.route('/bookings/<int:booking_id>/checkin')
@login_required
@receptionist_required
def checkin_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status != 'confirmed':
        flash('Solo se pueden hacer check-in de reservas confirmadas', 'error')
        return redirect(url_for('receptionist.manage_bookings'))
    
    booking.status = 'checked_in'
    db.session.commit()
    
    flash(f'Check-in realizado para {booking.user.full_name}', 'success')
    return redirect(url_for('receptionist.manage_bookings'))

@receptionist_bp.route('/bookings/<int:booking_id>/checkout')
@login_required
@receptionist_required
def checkout_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status != 'checked_in':
        flash('Solo se pueden hacer check-out de huéspedes que ya hicieron check-in', 'error')
        return redirect(url_for('receptionist.manage_bookings'))
    
    booking.status = 'completed'
    db.session.commit()
    
    flash(f'Check-out realizado para {booking.user.full_name}', 'success')
    return redirect(url_for('receptionist.manage_bookings'))

@receptionist_bp.route('/rooms')
@login_required
@receptionist_required
def view_rooms():
    rooms = Room.query.order_by(Room.room_number).all()
    return render_template('receptionist/view_rooms.html', rooms=rooms)
