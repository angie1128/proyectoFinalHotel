from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.room import Room
from app.models.reservation import Reservation
from app.forms.reservation import ReservationForm
from datetime import datetime

guest_bp = Blueprint('guest', __name__)

@guest_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's reservations
    reservations = Reservation.query.filter_by(guest_id=current_user.id).order_by(Reservation.created_at.desc()).all()
    
    # Get current reservation (checked in but not checked out)
    current_reservation = Reservation.query.filter_by(
        guest_id=current_user.id,
        status='confirmada'
    ).filter(
        Reservation.checked_in_at.isnot(None),
        Reservation.checked_out_at.is_(None)
    ).first()
    
    return render_template('guest/dashboard.html', 
                         reservations=reservations,
                         current_reservation=current_reservation)

@guest_bp.route('/reserve', methods=['GET', 'POST'])
@login_required
def reserve():
    form = ReservationForm()
    if form.validate_on_submit():
        room = Room.query.get(form.room_id.data)
        nights = (form.check_out_date.data - form.check_in_date.data).days
        total_price = room.price * nights
        
        reservation = Reservation(
            guest_id=current_user.id,
            room_id=form.room_id.data,
            check_in_date=form.check_in_date.data,
            check_out_date=form.check_out_date.data,
            guests_count=form.guests_count.data,
            total_price=total_price,
            special_requests=form.special_requests.data
        )
        
        db.session.add(reservation)
        db.session.commit()
        
        flash(f'¡Reservación creada exitosamente! Total: ${total_price:.2f}', 'success')
        return redirect(url_for('guest.dashboard'))
    
    return render_template('guest/reserve.html', form=form)

@guest_bp.route('/reservations')
@login_required
def reservations():
    reservations = Reservation.query.filter_by(guest_id=current_user.id).order_by(Reservation.created_at.desc()).all()
    return render_template('guest/reservations.html', reservations=reservations)

@guest_bp.route('/profile')
@login_required
def profile():
    return render_template('guest/profile.html')
