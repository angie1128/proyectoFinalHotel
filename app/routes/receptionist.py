from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.room import Room
from app.models.reservation import Reservation
from app.forms.room import RoomForm
from datetime import datetime
from functools import wraps

receptionist_bp = Blueprint('receptionist', __name__)

def receptionist_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_receptionist() or current_user.is_admin()):
            flash('Acceso denegado. Se requieren permisos de recepcionista.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@receptionist_bp.route('/dashboard')
@login_required
@receptionist_required
def dashboard():
    # Today's check-ins and check-outs
    today_checkins = Reservation.query.filter_by(
        check_in_date=datetime.now().date(),
        status='confirmada'
    ).all()
    
    today_checkouts = Reservation.query.filter(
        Reservation.check_out_date == datetime.now().date(),
        Reservation.checked_in_at.isnot(None),
        Reservation.checked_out_at.is_(None)
    ).all()
    
    # Pending reservations
    pending_reservations = Reservation.query.filter_by(status='pendiente').all()
    
    # Room status
    available_rooms = Room.query.filter_by(status='disponible').count()
    occupied_rooms = Room.query.filter_by(status='ocupada').count()
    maintenance_rooms = Room.query.filter_by(status='mantenimiento').count()
    cleaning_rooms = Room.query.filter_by(status='limpieza').count()
    
    current_time = datetime.now()
    
    return render_template('receptionist/dashboard.html',
                         today_checkins=today_checkins,
                         today_checkouts=today_checkouts,
                         pending_reservations=pending_reservations,
                         available_rooms=available_rooms,
                         occupied_rooms=occupied_rooms,
                         maintenance_rooms=maintenance_rooms,
                         cleaning_rooms=cleaning_rooms,
                         current_time=current_time,
                         todays_checkins=today_checkins,
                         todays_checkouts=today_checkouts,
                         pending_checkins=len(today_checkins),
                         pending_checkouts=len(today_checkouts))

@receptionist_bp.route('/reservations')
@login_required
@receptionist_required
def reservations():
    reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
    
    total_reservations = len(reservations)
    pending_reservations = len([r for r in reservations if r.status == 'pendiente'])
    confirmed_reservations = len([r for r in reservations if r.status == 'confirmada'])
    active_reservations = len([r for r in reservations if r.status in ['confirmada', 'checked_in']])
    
    return render_template('receptionist/reservations.html', 
                         reservations=reservations,
                         total_reservations=total_reservations,
                         pending_reservations=pending_reservations,
                         confirmed_reservations=confirmed_reservations,
                         active_reservations=active_reservations)

@receptionist_bp.route('/reservations/<int:reservation_id>/confirm')
@login_required
@receptionist_required
def confirm_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.status == 'pendiente':
        reservation.status = 'confirmada'
        reservation.confirmed_at = datetime.utcnow()
        reservation.confirmed_by_id = current_user.id
        db.session.commit()
        flash(f'Reservación #{reservation.id} confirmada exitosamente.', 'success')
    else:
        flash('Esta reservación no puede ser confirmada.', 'warning')
    
    return redirect(url_for('receptionist.reservations'))

@receptionist_bp.route('/reservations/<int:reservation_id>/cancel')
@login_required
@receptionist_required
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.status in ['pendiente', 'confirmada']:
        reservation.status = 'cancelada'
        # Free up the room if it was occupied
        if reservation.room.status == 'ocupada':
            reservation.room.status = 'limpieza'
        db.session.commit()
        flash(f'Reservación #{reservation.id} cancelada exitosamente.', 'success')
    else:
        flash('Esta reservación no puede ser cancelada.', 'warning')
    
    return redirect(url_for('receptionist.reservations'))

@receptionist_bp.route('/checkin')
@login_required
@receptionist_required
def checkin_page():
    # Get reservations ready for check-in
    checkin_reservations = Reservation.query.filter_by(
        check_in_date=datetime.now().date(),
        status='confirmada'
    ).all()
    
    return render_template('receptionist/checkin.html', 
                         reservations=checkin_reservations)

@receptionist_bp.route('/checkout')
@login_required
@receptionist_required
def checkout_page():
    # Get reservations ready for check-out
    checkout_reservations = Reservation.query.filter(
        Reservation.check_out_date == datetime.now().date(),
        Reservation.checked_in_at.isnot(None),
        Reservation.checked_out_at.is_(None)
    ).all()
    
    return render_template('receptionist/checkout.html', 
                         reservations=checkout_reservations)

@receptionist_bp.route('/payments')
@login_required
@receptionist_required
def payments():
    # Get reservations with payment information
    reservations_with_payments = Reservation.query.filter(
        Reservation.status.in_(['confirmada', 'checked_in', 'completada'])
    ).order_by(Reservation.created_at.desc()).all()
    
    return render_template('receptionist/payments.html', 
                         reservations=reservations_with_payments)

@receptionist_bp.route('/checkin/<int:reservation_id>')
@login_required
@receptionist_required
def checkin(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.status == 'confirmada' and reservation.check_in_date <= datetime.now().date():
        reservation.checked_in_at = datetime.utcnow()
        reservation.room.status = 'ocupada'
        db.session.commit()
        flash(f'Check-in realizado para la habitación {reservation.room.number}.', 'success')
    else:
        flash('No se puede realizar el check-in para esta reservación.', 'warning')
    
    return redirect(url_for('receptionist.dashboard'))

@receptionist_bp.route('/checkout/<int:reservation_id>')
@login_required
@receptionist_required
def checkout(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.checked_in_at and not reservation.checked_out_at:
        reservation.checked_out_at = datetime.utcnow()
        reservation.status = 'completada'
        reservation.room.status = 'limpieza'
        db.session.commit()
        flash(f'Check-out realizado para la habitación {reservation.room.number}.', 'success')
    else:
        flash('No se puede realizar el check-out para esta reservación.', 'warning')
    
    return redirect(url_for('receptionist.dashboard'))

@receptionist_bp.route('/rooms')
@login_required
@receptionist_required
def rooms():
    rooms = Room.query.all()
    
    total_rooms = len(rooms)
    available_rooms = len([r for r in rooms if r.status == 'disponible'])
    occupied_rooms = len([r for r in rooms if r.status == 'ocupada'])
    maintenance_rooms = len([r for r in rooms if r.status == 'mantenimiento'])
    
    return render_template('receptionist/rooms.html', 
                         rooms=rooms,
                         total_rooms=total_rooms,
                         available_rooms=available_rooms,
                         occupied_rooms=occupied_rooms,
                         maintenance_rooms=maintenance_rooms)

@receptionist_bp.route('/rooms/<int:room_id>/status', methods=['POST'])
@login_required
@receptionist_required
def update_room_status(room_id):
    room = Room.query.get_or_404(room_id)
    new_status = request.form.get('status')
    
    if new_status in ['disponible', 'mantenimiento', 'limpieza']:
        room.status = new_status
        db.session.commit()
        flash(f'Estado de la habitación {room.number} actualizado a {room.get_status_display()}.', 'success')
    else:
        flash('Estado inválido.', 'danger')
    
    return redirect(url_for('receptionist.rooms'))

@receptionist_bp.route('/rooms/<int:room_id>/status/<status>')
@login_required
@receptionist_required
def update_room_status_get(room_id, status):
    room = Room.query.get_or_404(room_id)
    
    if status in ['disponible', 'mantenimiento', 'limpieza']:
        room.status = status
        db.session.commit()
        flash(f'Estado de la habitación {room.number} actualizado a {room.get_status_display()}.', 'success')
    else:
        flash('Estado inválido.', 'danger')
    
    return redirect(url_for('receptionist.rooms'))
