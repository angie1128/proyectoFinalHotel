from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.room import Room
from app.models.reservation import Reservation
from app.forms.auth import CreateStaffForm
from app.forms.room import RoomForm
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Statistics
    total_rooms = Room.query.count()
    available_rooms = Room.query.filter_by(status='disponible').count()
    occupied_rooms = Room.query.filter_by(status='ocupada').count()
    total_users = User.query.count()
    pending_reservations = Reservation.query.filter_by(status='pendiente').count()
    
    # Recent reservations
    recent_reservations = Reservation.query.order_by(Reservation.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_rooms=total_rooms,
                         available_rooms=available_rooms,
                         occupied_rooms=occupied_rooms,
                         total_users=total_users,
                         pending_reservations=pending_reservations,
                         recent_reservations=recent_reservations)

@admin_bp.route('/staff')
@login_required
@admin_required
def staff():
    staff_members = User.query.filter(User.role.in_(['recepcionista', 'administrador'])).all()
    return render_template('admin/staff.html', staff_members=staff_members)

@admin_bp.route('/staff/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_staff():
    form = CreateStaffForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Usuario {user.username} creado exitosamente.', 'success')
        return redirect(url_for('admin.staff'))
    
    return render_template('admin/create_staff.html', form=form)

@admin_bp.route('/rooms')
@login_required
@admin_required
def rooms():
    rooms = Room.query.all()
    return render_template('admin/rooms.html', rooms=rooms)

@admin_bp.route('/rooms/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_room():
    form = RoomForm()
    if form.validate_on_submit():
        room = Room(
            number=form.number.data,
            type=form.type.data,
            price=form.price.data,
            max_occupancy=form.max_occupancy.data,
            description=form.description.data,
            amenities=form.amenities.data,
            status=form.status.data
        )
        db.session.add(room)
        db.session.commit()
        flash(f'Habitación {room.number} creada exitosamente.', 'success')
        return redirect(url_for('admin.rooms'))
    
    return render_template('admin/create_room.html', form=form)

@admin_bp.route('/rooms/<int:room_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_room(room_id):
    room = Room.query.get_or_404(room_id)
    form = RoomForm(original_room=room, obj=room)
    
    if form.validate_on_submit():
        form.populate_obj(room)
        db.session.commit()
        flash(f'Habitación {room.number} actualizada exitosamente.', 'success')
        return redirect(url_for('admin.rooms'))
    
    return render_template('admin/edit_room.html', form=form, room=room)

@admin_bp.route('/reservations')
@login_required
@admin_required
def reservations():
    reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
    return render_template('admin/reservations.html', reservations=reservations)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:id>')
@login_required
@admin_required
def view_user(id):
    user = User.query.get_or_404(id)
    return render_template('admin/view_user.html', user=user)

@admin_bp.route('/profile')
@login_required
@admin_required
def profile():
    return render_template('admin/profile.html', user=current_user)
