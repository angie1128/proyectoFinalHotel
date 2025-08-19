from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(get_dashboard_url(current_user.role))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('Por favor completa todos los campos', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Tu cuenta ha sido desactivada. Contacta al administrador.', 'error')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'¡Bienvenido, {user.first_name}!', 'success')
            
            if next_page:
                return redirect(next_page)
            else:
                return redirect(get_dashboard_url(user.role))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(get_dashboard_url(current_user.role))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        # Validaciones
        if not all([username, email, password, confirm_password, first_name, last_name]):
            flash('Por favor completa todos los campos obligatorios', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return render_template('auth/register.html')
        
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            flash('Por favor ingresa un email válido', 'error')
            return render_template('auth/register.html')
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'error')
            return render_template('auth/register.html')
        
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role='guest'  # Los usuarios que se registran son siempre huéspedes
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('¡Registro exitoso! Ya puedes iniciar sesión', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear la cuenta. Inténtalo de nuevo', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/create-receptionist', methods=['GET', 'POST'])
@login_required
def create_receptionist():
    if not current_user.is_admin:
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        # Validaciones
        if not all([username, email, password, first_name, last_name]):
            flash('Por favor completa todos los campos obligatorios', 'error')
            return render_template('auth/create_receptionist.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return render_template('auth/create_receptionist.html')
        
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            flash('Por favor ingresa un email válido', 'error')
            return render_template('auth/create_receptionist.html')
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso', 'error')
            return render_template('auth/create_receptionist.html')
        
        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'error')
            return render_template('auth/create_receptionist.html')
        
        # Crear nuevo recepcionista
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role='receptionist',
            created_by=current_user.id
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash(f'Recepcionista {user.full_name} creado exitosamente', 'success')
            return redirect(url_for('admin.manage_users'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear la cuenta del recepcionista', 'error')
    
    return render_template('auth/create_receptionist.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.phone = request.form.get('phone')
        
        # Cambiar contraseña si se proporciona
        new_password = request.form.get('new_password')
        if new_password:
            if len(new_password) < 6:
                flash('La nueva contraseña debe tener al menos 6 caracteres', 'error')
                return render_template('auth/edit_profile.html')
            current_user.set_password(new_password)
        
        try:
            db.session.commit()
            flash('Perfil actualizado correctamente', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el perfil', 'error')
    
    return render_template('auth/edit_profile.html')

def get_dashboard_url(role):
    if role == 'admin':
        return url_for('admin.dashboard')
    elif role == 'receptionist':
        return url_for('receptionist.dashboard')
    else:  # guest
        return url_for('main.index')
