from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

import os

from app import db
from app.models.user import User
from app.models.room import Room
from app.models.reservation import Reservation
from app.forms.auth import CreateStaffForm
from app.forms.room import RoomForm
from functools import wraps

admin_bp = Blueprint('admin', __name__)

# -------------------------
# Decorador de administrador
# -------------------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# -------------------------
# Dashboard
# -------------------------
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_rooms = Room.query.count()
    available_rooms = Room.query.filter_by(status='disponible').count()
    occupied_rooms = Room.query.filter_by(status='ocupada').count()
    maintenance_rooms = Room.query.filter_by(status='mantenimiento').count()
    total_users = User.query.count()
    pending_reservations = Reservation.query.filter_by(status='pendiente').count()
    recent_reservations = Reservation.query.order_by(Reservation.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                           total_rooms=total_rooms,
                           available_rooms=available_rooms,
                           occupied_rooms=occupied_rooms,
                           maintenance_rooms=maintenance_rooms,
                           total_users=total_users,
                           pending_reservations=pending_reservations,
                           recent_reservations=recent_reservations)

# -------------------------
# Rooms
# -------------------------
@admin_bp.route('/rooms')
@login_required
@admin_required
def rooms():
    rooms = Room.query.all()
    return render_template('admin/rooms.html', rooms=rooms)
# Crear habitación
@admin_bp.route("/rooms/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_room():
    form = RoomForm()
    if form.validate_on_submit():
        room = Room(
            number=form.number.data,
            type=form.type.data,
            price=form.price.data,
            status=form.status.data,
            description=form.description.data,
            max_occupancy=form.max_occupancy.data,
            amenities=form.amenities.data
        )

        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            # Crear carpeta si no existe
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            upload_path = os.path.join(upload_folder, filename)
            form.image.data.save(upload_path)
            room.image = filename  # Guardamos solo el nombre

        db.session.add(room)
        db.session.commit()
        flash("Habitación creada correctamente", "success")
        return redirect(url_for("admin.rooms"))

    return render_template("admin/create_room.html", form=form)


# Editar habitación
# Editar habitación
@admin_bp.route("/rooms/edit/<int:room_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_room(room_id):
    room = Room.query.get_or_404(room_id)
    form = RoomForm(obj=room)

    if form.validate_on_submit():
        room.number = form.number.data
        room.type = form.type.data
        room.price = form.price.data
        room.status = form.status.data
        room.description = form.description.data
        room.max_occupancy = form.max_occupancy.data
        room.amenities = form.amenities.data

        if form.image.data:
            # Eliminar imagen vieja si existe
            if room.image:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], room.image)
                if os.path.exists(old_path):
                    os.remove(old_path)

            filename = secure_filename(form.image.data.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            upload_path = os.path.join(upload_folder, filename)
            form.image.data.save(upload_path)
            room.image = filename

        db.session.commit()
        flash("Habitación actualizada correctamente", "success")
        return redirect(url_for("admin.rooms"))

    return render_template("admin/edit_room.html", form=form, room=room)

# -------------------------
# Eliminar habitación
# -------------------------
@admin_bp.route('/rooms/<int:room_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)

    # Eliminar imagen si existe
    if room.image and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], room.image)):
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], room.image))

    db.session.delete(room)
    db.session.commit()
    flash(f'Habitación {room.number} eliminada exitosamente.', 'danger')
    return redirect(url_for('admin.rooms'))

# -------------------------
# Actualizar estado de habitación
# -------------------------
@admin_bp.route('/rooms/<int:room_id>/status/<status>')
@login_required
@admin_required
def update_room_status(room_id, status):
    room = Room.query.get_or_404(room_id)
    if status not in ['disponible', 'ocupada', 'mantenimiento', 'limpieza']:
        flash('Estado no válido.', 'danger')
        return redirect(url_for('admin.rooms'))
    room.status = status
    db.session.commit()
    flash(f'Estado de la habitación {room.number} actualizado a "{status}".', 'success')
    return redirect(url_for('admin.rooms'))

# -------------------------
# Reservations
# -------------------------
@admin_bp.route('/reservations')
@login_required
@admin_required
def reservations():
    reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
    return render_template('admin/reservations.html', reservations=reservations)

# -------------------------
# Users
# -------------------------
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

# -------------------------
# Perfil admin
# -------------------------
@admin_bp.route('/profile')
@login_required
@admin_required
def profile():
    return render_template('admin/profile.html', user=current_user)

# -------------------------
# Staff
# -------------------------
@admin_bp.route('/staff')
@login_required
@admin_required
def staff():
    staff_members = User.query.filter_by(role='recepcionista').all()
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
            role='recepcionista'  # rol fijo
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Usuario {user.username} creado exitosamente.', 'success')
        return redirect(url_for('admin.staff'))
    return render_template('admin/create_staff.html', form=form)

@admin_bp.route('/staff/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_staff(user_id):
    user = User.query.get_or_404(user_id)
    form = CreateStaffForm(obj=user)

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.username = form.username.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash(f'Usuario {user.username} actualizado exitosamente.', 'success')
        return redirect(url_for('admin.staff'))

    return render_template('admin/edit_staff.html', form=form, user=user)

@admin_bp.route('/staff/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_staff(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuario {user.username} eliminado exitosamente.', 'danger')
    return redirect(url_for('admin.staff'))

# -------------------------
# Descargar PDF de todo el personal
# -------------------------
@admin_bp.route('/staff/download_pdf')
@login_required
@admin_required
def download_all_staff_pdf():
    staff_members = User.query.filter_by(role='recepcionista').all()
    if not staff_members:
        flash("No hay personal registrado para generar el PDF.", "warning")
        return redirect(url_for('admin.staff'))

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setTitle("Personal_Recepcionistas")

    # Título
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "Lista de Recepcionistas")

    y = height - 80
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "ID")
    pdf.drawString(80, y, "Nombre")
    pdf.drawString(250, y, "Email")
    pdf.drawString(400, y, "Teléfono")
    pdf.drawString(480, y, "Usuario")
    y -= 20
    pdf.setFont("Helvetica", 12)

    for staff in staff_members:
        if y < 50:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 12)

        pdf.drawString(50, y, str(staff.id))
        pdf.drawString(80, y, staff.get_full_name())
        pdf.drawString(250, y, staff.email)
        pdf.drawString(400, y, staff.phone)
        pdf.drawString(480, y, staff.username)
        y -= 20

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return send_file(buffer,
                     as_attachment=True,
                     download_name="Personal_Recepcionistas.pdf",
                     mimetype='application/pdf')
