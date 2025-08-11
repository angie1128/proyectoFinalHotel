from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app.models import User, Room, RoomType, Reservation, Service, UserRole, RoomStatus, ReservationStatus
from app.forms import LoginForm, RegisterForm, ReservationForm, RoomForm
from app import db
from datetime import datetime, date
import json

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Mostrar algunos tipos de habitaciones para huéspedes no autenticados
    room_types = RoomType.query.limit(3).all()
    return render_template('index.html', room_types=room_types)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data) and user.role.value == form.role.data:
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        flash('Email, contraseña o rol incorrectos', 'error')
    return render_template('auth/login.html', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            role=UserRole.GUEST  # Solo puede registrarse como huésped
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('main.login'))
    return render_template('auth/register.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == UserRole.ADMIN:
        return render_template('dashboard/admin.html')
    elif current_user.role == UserRole.RECEPTIONIST:
        return render_template('reception/dashboard.html')
    elif current_user.role == UserRole.HOUSEKEEPING:
        return render_template('cleaning/dashboard.html')
    else:  # GUEST
        return render_template('dashboard/guest.html')

@main.route('/rooms')
@login_required
def rooms():
    if current_user.role in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
        rooms = Room.query.all()
        return render_template('rooms/list.html', rooms=rooms)
    else:
        # Para huéspedes, mostrar tipos de habitaciones disponibles
        room_types = RoomType.query.all()
        return render_template('rooms/guest_view.html', room_types=room_types)

@main.route('/reservations')
@login_required
def reservations():
    if current_user.role == UserRole.GUEST:
        reservations = Reservation.query.filter_by(guest_id=current_user.id).all()
    else:
        reservations = Reservation.query.all()
    return render_template('reservations/list.html', reservations=reservations)

@main.route('/make_reservation', methods=['GET', 'POST'])
@login_required
def make_reservation():
    if current_user.role != UserRole.GUEST:
        flash('Solo los huéspedes pueden hacer reservaciones', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = ReservationForm()
    room_types = RoomType.query.all()
    
    if form.validate_on_submit():
        # Buscar habitación disponible
        available_rooms = []
        for room_type in room_types:
            for room in room_type.rooms:
                if room.status == RoomStatus.AVAILABLE and room.is_available(form.check_in.data, form.check_out.data):
                    available_rooms.append(room)
                    break  # Tomar la primera disponible de este tipo
        
        if available_rooms:
            # Crear reservación con la primera habitación disponible
            room = available_rooms[0]
            nights = (form.check_out.data - form.check_in.data).days
            total_amount = nights * room.room_type.price_per_night
            
            reservation = Reservation(
                guest_id=current_user.id,
                room_id=room.id,
                check_in=form.check_in.data,
                check_out=form.check_out.data,
                adults=form.adults.data,
                children=form.children.data,
                total_amount=total_amount,
                special_requests=form.special_requests.data
            )
            db.session.add(reservation)
            db.session.commit()
            flash('¡Reservación creada exitosamente!', 'success')
            return redirect(url_for('main.reservations'))
        else:
            flash('No hay habitaciones disponibles para las fechas seleccionadas', 'error')
    
    return render_template('reservations/create.html', form=form, room_types=room_types)

@main.route('/api/dashboard_stats')
@login_required
def dashboard_stats():
    if current_user.role not in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
        return jsonify({'error': 'No autorizado'}), 403
    
    total_rooms = Room.query.count()
    occupied_rooms = Room.query.filter_by(status=RoomStatus.OCCUPIED).count()
    available_rooms = Room.query.filter_by(status=RoomStatus.AVAILABLE).count()
    pending_reservations = Reservation.query.filter_by(status=ReservationStatus.PENDING).count()
    
    return jsonify({
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'available_rooms': available_rooms,
        'pending_reservations': pending_reservations
    })

@main.route('/profile')
@login_required
def profile():
    if current_user.role == UserRole.GUEST:
        return render_template('profile/guest.html')
    else:
        return render_template('profile/staff.html')

@main.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_users():
    if current_user.role != UserRole.ADMIN:
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        try:
            # Validar que las contraseñas coincidan
            if request.form.get('password') != request.form.get('confirm_password'):
                return jsonify({'success': False, 'message': 'Las contraseñas no coinciden'}), 400
            
            # Verificar que el email y username no existan
            existing_email = User.query.filter_by(email=request.form.get('email')).first()
            existing_username = User.query.filter_by(username=request.form.get('username')).first()
            
            if existing_email:
                return jsonify({'success': False, 'message': 'El email ya está registrado'}), 400
            if existing_username:
                return jsonify({'success': False, 'message': 'El nombre de usuario ya existe'}), 400
            
            # Crear nuevo usuario
            user = User(
                username=request.form.get('username'),
                email=request.form.get('email'),
                first_name=request.form.get('first_name'),
                last_name=request.form.get('last_name'),
                phone=request.form.get('phone'),
                role=UserRole(request.form.get('role'))
            )
            user.set_password(request.form.get('password'))
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': f'Usuario {user.get_full_name()} creado exitosamente',
                'user': {
                    'id': user.id,
                    'name': user.get_full_name(),
                    'email': user.email,
                    'role': user.role.value
                }
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error al crear usuario: {str(e)}'}), 500
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@main.route('/admin/reports')
@login_required
def admin_reports():
    if current_user.role != UserRole.ADMIN:
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/reports.html')

@main.route('/admin/services')
@login_required
def admin_services():
    if current_user.role != UserRole.ADMIN:
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.dashboard'))
    
    services = Service.query.all()
    return render_template('admin/services.html', services=services)

@main.route('/admin/maintenance')
@login_required
def admin_maintenance():
    if current_user.role != UserRole.ADMIN:
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/maintenance.html')
