from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.models.room import Room
from app.models.booking import Booking
from datetime import datetime, date

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_guests = User.query.filter_by(role='guest').count()
    total_receptionists = User.query.filter_by(role='receptionist').count()
    total_rooms = Room.query.count()
    total_bookings = Booking.query.count()
    pending_bookings = Booking.query.filter_by(status='pending').count()
    
    # Reservas recientes
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    
    # Habitaciones más reservadas
    popular_rooms = db.session.query(Room, db.func.count(Booking.id).label('booking_count'))\
                             .join(Booking)\
                             .group_by(Room.id)\
                             .order_by(db.func.count(Booking.id).desc())\
                             .limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_guests=total_guests,
                         total_receptionists=total_receptionists,
                         total_rooms=total_rooms,
                         total_bookings=total_bookings,
                         pending_bookings=pending_bookings,
                         recent_bookings=recent_bookings,
                         popular_rooms=popular_rooms)

@admin_bp.route('/bookings')
@login_required
@admin_required
def manage_bookings():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Booking.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    bookings = query.order_by(Booking.created_at.desc())\
                   .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/bookings.html', 
                         bookings=bookings, 
                         current_status=status_filter)

@admin_bp.route('/booking/<int:booking_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form.get('status')
    
    if new_status not in ['pending', 'confirmed', 'cancelled', 'checked_in', 'completed']:
        flash('Estado inválido', 'error')
        return redirect(url_for('admin.manage_bookings'))
    
    try:
        booking.status = new_status
        db.session.commit()
        flash(f'Estado de reserva actualizado a {new_status}', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al actualizar el estado', 'error')
    
    return redirect(url_for('admin.manage_bookings'))

@admin_bp.route('/rooms')
@login_required
@admin_required
def manage_rooms():
    page = request.args.get('page', 1, type=int)
    rooms = Room.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/rooms.html', rooms=rooms)

@admin_bp.route('/room/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_room():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price_per_night = request.form.get('price_per_night', type=float)
        capacity = request.form.get('capacity', type=int)
        room_type = request.form.get('room_type')
        image_url = request.form.get('image_url')
        amenities = request.form.getlist('amenities')
        
        if not all([name, price_per_night, capacity, room_type]):
            flash('Por favor completa todos los campos obligatorios', 'error')
            return render_template('admin/create_room.html')
        
        try:
            room = Room(
                name=name,
                description=description,
                price_per_night=price_per_night,
                capacity=capacity,
                room_type=room_type,
                image_url=image_url
            )
            room.set_amenities(amenities)
            
            db.session.add(room)
            db.session.commit()
            flash('Habitación creada exitosamente', 'success')
            return redirect(url_for('admin.manage_rooms'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear la habitación', 'error')
    
    return render_template('admin/create_room.html')

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', '')
    
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    users = query.order_by(User.created_at.desc())\
               .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/users.html', users=users, current_role=role_filter)

@admin_bp.route('/user/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        status = 'activado' if user.is_active else 'desactivado'
        flash(f'Usuario {user.full_name} {status} exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al cambiar el estado del usuario', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('No puedes eliminar tu propia cuenta', 'error')
        return redirect(url_for('admin.manage_users'))
    
    if user.role == 'admin':
        flash('No se pueden eliminar cuentas de administrador', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        # Verificar si tiene reservas activas
        active_bookings = Booking.query.filter_by(user_id=user.id)\
                                      .filter(Booking.status.in_(['confirmed', 'checked_in']))\
                                      .count()
        
        if active_bookings > 0:
            flash('No se puede eliminar un usuario con reservas activas', 'error')
            return redirect(url_for('admin.manage_users'))
        
        db.session.delete(user)
        db.session.commit()
        flash(f'Usuario {user.full_name} eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar el usuario', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    # Estadísticas para reportes
    today = date.today()
    
    # Reservas por mes
    monthly_bookings = db.session.query(
        db.func.date_trunc('month', Booking.created_at).label('month'),
        db.func.count(Booking.id).label('count')
    ).group_by(db.func.date_trunc('month', Booking.created_at))\
     .order_by(db.func.date_trunc('month', Booking.created_at).desc())\
     .limit(12).all()
    
    # Ingresos por mes
    monthly_revenue = db.session.query(
        db.func.date_trunc('month', Booking.created_at).label('month'),
        db.func.sum(Booking.total_price).label('revenue')
    ).filter(Booking.status.in_(['confirmed', 'checked_in', 'completed']))\
     .group_by(db.func.date_trunc('month', Booking.created_at))\
     .order_by(db.func.date_trunc('month', Booking.created_at).desc())\
     .limit(12).all()
    
    return render_template('admin/reports.html',
                         monthly_bookings=monthly_bookings,
                         monthly_revenue=monthly_revenue)
