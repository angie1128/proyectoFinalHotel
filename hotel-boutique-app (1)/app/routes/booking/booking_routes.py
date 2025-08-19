from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models import Room, Booking, User
from datetime import datetime, date

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/create/<int:room_id>', methods=['GET', 'POST'])
@login_required
def create_booking(room_id):
    room = Room.query.get_or_404(room_id)
    
    if request.method == 'POST':
        check_in_str = request.form.get('check_in')
        check_out_str = request.form.get('check_out')
        guests = request.form.get('guests', type=int)
        special_requests = request.form.get('special_requests', '')
        
        if not all([check_in_str, check_out_str, guests]):
            flash('Por favor completa todos los campos obligatorios', 'error')
            return render_template('booking/create.html', room=room)
        
        try:
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
            
            # Validaciones
            if check_in >= check_out:
                flash('La fecha de salida debe ser posterior a la de entrada', 'error')
                return render_template('booking/create.html', room=room)
            
            if check_in < date.today():
                flash('La fecha de entrada no puede ser anterior a hoy', 'error')
                return render_template('booking/create.html', room=room)
            
            if guests > room.capacity:
                flash(f'Esta habitación tiene capacidad máxima para {room.capacity} huéspedes', 'error')
                return render_template('booking/create.html', room=room)
            
            # Verificar disponibilidad
            if not room.is_available_for_dates(check_in, check_out):
                flash('La habitación no está disponible para las fechas seleccionadas', 'error')
                return render_template('booking/create.html', room=room)
            
            # Calcular precio total
            nights = (check_out - check_in).days
            total_price = float(room.price_per_night) * nights
            
            # Crear reserva
            booking = Booking(
                user_id=current_user.id,
                room_id=room.id,
                check_in=check_in,
                check_out=check_out,
                guests=guests,
                total_price=total_price,
                special_requests=special_requests,
                status='pending'
            )
            
            db.session.add(booking)
            db.session.commit()
            
            flash('¡Reserva creada exitosamente! Te contactaremos pronto para confirmarla.', 'success')
            return redirect(url_for('booking.my_bookings'))
            
        except ValueError:
            flash('Formato de fecha inválido', 'error')
        except Exception as e:
            db.session.rollback()
            flash('Error al crear la reserva. Inténtalo de nuevo', 'error')
    
    return render_template('booking/create.html', room=room)

@booking_bp.route('/create_booking/<int:room_id>', methods=['POST'])
@login_required
def create_booking_from_detail(room_id):
    return create_booking(room_id)

@booking_bp.route('/my-bookings')
@login_required
def my_bookings():
    page = request.args.get('page', 1, type=int)
    bookings = Booking.query.filter_by(user_id=current_user.id)\
                           .order_by(Booking.created_at.desc())\
                           .paginate(page=page, per_page=10, error_out=False)
    
    today = date.today()
    return render_template('booking/my_bookings.html', bookings=bookings, today=today)

@booking_bp.route('/detail/<int:booking_id>')
@login_required
def booking_detail(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Verificar que la reserva pertenece al usuario actual o es admin
    if booking.user_id != current_user.id and not current_user.is_admin:
        flash('No tienes permiso para ver esta reserva', 'error')
        return redirect(url_for('booking.my_bookings'))
    
    return render_template('booking/detail.html', booking=booking)

@booking_bp.route('/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Verificar permisos
    if booking.user_id != current_user.id and not current_user.is_admin:
        flash('No tienes permiso para cancelar esta reserva', 'error')
        return redirect(url_for('booking.my_bookings'))
    
    # Solo se pueden cancelar reservas pendientes o confirmadas
    if booking.status not in ['pending', 'confirmed']:
        flash('Esta reserva no se puede cancelar', 'error')
        return redirect(url_for('booking.booking_detail', booking_id=booking_id))
    
    # No se pueden cancelar reservas que ya comenzaron
    if booking.check_in <= date.today():
        flash('No se pueden cancelar reservas que ya han comenzado', 'error')
        return redirect(url_for('booking.booking_detail', booking_id=booking_id))
    
    try:
        booking.status = 'cancelled'
        db.session.commit()
        flash('Reserva cancelada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al cancelar la reserva', 'error')
    
    return redirect(url_for('booking.booking_detail', booking_id=booking_id))

@booking_bp.route('/profile')
@login_required
def guest_profile():
    # Estadísticas del usuario
    total_bookings = Booking.query.filter_by(user_id=current_user.id).count()
    completed_bookings = Booking.query.filter_by(user_id=current_user.id, status='completed').count()
    upcoming_bookings = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.check_in > date.today(),
        Booking.status.in_(['confirmed', 'pending'])
    ).count()
    
    return render_template('booking/guest_profile.html',
                         total_bookings=total_bookings,
                         completed_bookings=completed_bookings,
                         upcoming_bookings=upcoming_bookings)

@booking_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    try:
        current_user.full_name = request.form.get('full_name')
        current_user.email = request.form.get('email')
        
        # Campos opcionales
        phone = request.form.get('phone')
        if phone:
            current_user.phone = phone
            
        db.session.commit()
        flash('Perfil actualizado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al actualizar el perfil', 'error')
    
    return redirect(url_for('booking.guest_profile'))

@booking_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        flash('Todos los campos son obligatorios', 'error')
        return redirect(url_for('booking.guest_profile'))
    
    if not check_password_hash(current_user.password_hash, current_password):
        flash('La contraseña actual es incorrecta', 'error')
        return redirect(url_for('booking.guest_profile'))
    
    if new_password != confirm_password:
        flash('Las contraseñas nuevas no coinciden', 'error')
        return redirect(url_for('booking.guest_profile'))
    
    if len(new_password) < 6:
        flash('La nueva contraseña debe tener al menos 6 caracteres', 'error')
        return redirect(url_for('booking.guest_profile'))
    
    try:
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash('Contraseña cambiada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al cambiar la contraseña', 'error')
    
    return redirect(url_for('booking.guest_profile'))
