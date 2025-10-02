from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os
from functools import wraps

from app import db
from app.models.user import User
from app.models.room import Room
from app.models.reservation import Reservation
from app.forms.auth import CreateStaffForm, EditProfileForm, ChangePasswordForm
from app.forms.room import RoomForm

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

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
# Función genérica para crear PDF con estilo rosado
# -------------------------
def create_pdf(title, headers, data_rows):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18
    )
    elements = []
    styles = getSampleStyleSheet()

    # Título principal
    elements.append(Paragraph(f"<b><font color='#FF69B4' size=16>{title}</font></b>", styles['Title']))
    elements.append(Spacer(1, 12))

    # Tabla
    table_data = [headers] + data_rows
    table = Table(table_data, hAlign='LEFT', repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.pink),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.lavenderblush])
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
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

@admin_bp.route("/rooms/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_room():
    form = RoomForm()
    if form.validate_on_submit():
        room = Room(
            number=form.number.data,
            type=form.type.data,
            price=form.price.data,
            status=form.status.data,
            description=form.description.data,
            max_occupancy=form.max_occupancy.data
        )
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(upload_path)
            room.image = filename

        db.session.add(room)
        db.session.commit()
        flash("Habitación creada correctamente", "success")
        return redirect(url_for("admin.rooms"))
    return render_template("admin/create_room.html", form=form)

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

        if form.image.data:
            if room.image:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], room.image)
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename = secure_filename(form.image.data.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(upload_path)
            room.image = filename

        db.session.commit()
        flash("Habitación actualizada", "success")
        return redirect(url_for("admin.rooms"))
    return render_template("admin/edit_room.html", form=form, room=room)

@admin_bp.route('/rooms/<int:room_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    if room.image and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], room.image)):
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], room.image))
    db.session.delete(room)
    db.session.commit()
    flash(f'Habitación {room.number} eliminada exitosamente.', 'danger')
    return redirect(url_for('admin.rooms'))

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
    total_reservations = Reservation.query.count()
    pending_reservations = Reservation.query.filter_by(status='pending').count()
    confirmed_reservations = Reservation.query.filter_by(status='confirmed').count()
    cancelled_reservations = Reservation.query.filter_by(status='cancelled').count()

    return render_template('admin/reservations.html',
                           reservations=reservations,
                           total_reservations=total_reservations,
                           pending_reservations=pending_reservations,
                           confirmed_reservations=confirmed_reservations,
                           cancelled_reservations=cancelled_reservations)

@admin_bp.route('/reservations/<int:reservation_id>/detail')
@login_required
@admin_required
def reservation_detail(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    return render_template('admin/reservation_detail.html', reservation=reservation)

@admin_bp.route('/reservations/<int:reservation_id>/confirm')
@login_required
@admin_required
def confirm_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    reservation.status = 'confirmed'
    db.session.commit()
    flash(f'Reservación #{reservation.id} confirmada correctamente.', 'success')
    return redirect(url_for('admin.reservations'))

@admin_bp.route('/reservations/<int:reservation_id>/cancel')
@login_required
@admin_required
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    reservation.status = 'cancelled'
    db.session.commit()
    flash(f'Reservación #{reservation.id} cancelada correctamente.', 'success')
    return redirect(url_for('admin.reservations'))

# -------------------------
# Descarga PDF de una sola reserva
# -------------------------
@admin_bp.route('/reservations/<int:reservation_id>/download_pdf')
@login_required
@admin_required
def download_reservation_pdf(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    headers = ["Campo", "Información"]
    data_rows = [
        ["Nombre", reservation.guest.get_full_name() if reservation.guest else "-"],
        ["Email", reservation.guest.email if reservation.guest else "-"],
        ["Teléfono", reservation.guest.phone or "-"],
        ["Habitación", f"{reservation.room.number} ({reservation.room.type})" if reservation.room else "-"],
        ["Check-in", reservation.check_in_date.strftime("%d/%m/%Y")],
        ["Check-out", reservation.check_out_date.strftime("%d/%m/%Y")],
        ["Huéspedes", str(reservation.guests_count)],
        ["Estado", reservation.get_status_display()],
        ["Total", f"${reservation.total_price:.2f}"]
    ]

    buffer = create_pdf("Detalle de Reservación", headers, data_rows)
    return send_file(buffer, as_attachment=True, download_name="Reservacion.pdf", mimetype='application/pdf')
# -------------------------
# Descarga PDF de todas las reservas
# -------------------------
@admin_bp.route('/reservations/download_pdf')
@login_required
@admin_required
def download_all_reservations_pdf():
    reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
    if not reservations:
        flash("No hay reservas registradas para generar el PDF.", "warning")
        return redirect(url_for('admin.reservations'))

    headers = ["Huésped", "Email", "Habitación", "Check-in", "Check-out", "Estado"]
    data_rows = []
    for res in reservations:
        data_rows.append([
            res.guest.get_full_name() if res.guest else "-",
            res.guest.email if res.guest else "-",
            f"{res.room.number} ({res.room.type})" if res.room else "-",
            res.check_in_date.strftime("%d/%m/%Y"),
            res.check_out_date.strftime("%d/%m/%Y"),
            res.get_status_display()
        ])

    buffer = create_pdf("Lista de Todas las Reservas", headers, data_rows)
    return send_file(buffer, as_attachment=True, download_name="Todas_Las_Reservas.pdf", mimetype='application/pdf')

# -------------------------
# Users
# -------------------------
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    search_query = request.args.get('search', '').strip()
    role_filter = request.args.get('role', 'all')

    query = User.query

    if search_query:
        query = query.filter(
            db.or_(
                User.first_name.ilike(f'%{search_query}%'),
                User.last_name.ilike(f'%{search_query}%'),
                User.username.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%')
            )
        )

    if role_filter != 'all':
        query = query.filter_by(role=role_filter)

    users = query.all()

    # Statistics (keeping them for now, but will replace in template)
    total_users = User.query.count()
    guest_users = User.query.filter_by(role='huesped').count()
    receptionist_users = User.query.filter_by(role='recepcionista').count()
    admin_users = User.query.filter_by(role='admin').count()

    return render_template('admin/users.html',
                          users=users,
                          total_users=total_users,
                          guest_users=guest_users,
                          receptionist_users=receptionist_users,
                          admin_users=admin_users,
                          search_query=search_query,
                          role_filter=role_filter)

@admin_bp.route('/users/<int:id>')
@login_required
@admin_required
def view_user(id):
    user = User.query.get_or_404(id)
    return render_template('admin/view_user.html', user=user)


@admin_bp.route('/users/download_pdf')
@login_required
@admin_required
def download_all_users_pdf():
    users = User.query.all()
    if not users:
        flash("No hay usuarios registrados para generar el PDF.", "warning")
        return redirect(url_for('admin.users'))

    headers = ["Nombre", "Email", "Teléfono", "Rol"]
    data_rows = []
    for user in users:
        data_rows.append([
            user.get_full_name(),
            user.email,
            user.phone or "-",
            user.role
        ])

    buffer = create_pdf("Lista de Usuarios Registrados", headers, data_rows)
    return send_file(buffer, as_attachment=True, download_name="Usuarios_Registrados.pdf", mimetype='application/pdf')

# -------------------------
# Perfil admin
# -------------------------
@admin_bp.route('/profile')
@login_required
@admin_required
def profile():
    return render_template('admin/profile.html', user=current_user)

@admin_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash("Perfil actualizado correctamente.", "success")
        return redirect(url_for('admin.profile'))
    return render_template("admin/edit_profile.html", form=form, user=current_user)

@admin_bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
@admin_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("La contraseña actual no es correcta.", "danger")
            return redirect(url_for('admin.change_password'))
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash("Contraseña actualizada correctamente.", "success")
        return redirect(url_for('admin.profile'))
    return render_template("admin/change_password.html", form=form)

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
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone=form.phone.data,
                role='recepcionista'
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash(f'Recepcionista {user.get_full_name()} creado exitosamente.', 'success')
            return redirect(url_for('admin.staff'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el usuario: {str(e)}', 'danger')
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en {getattr(form, field).label.text}: {error}", 'danger')
    return render_template('admin/create_staff.html', form=form)

@admin_bp.route('/staff/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_staff(user_id):
    user = User.query.get_or_404(user_id)
    form = CreateStaffForm(obj=user)
    if form.validate_on_submit():
        try:
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data
            user.phone = form.phone.data
            user.username = form.username.data
            if form.password.data:
                user.set_password(form.password.data)
            db.session.commit()
            flash(f'Recepcionista {user.get_full_name()} actualizado exitosamente.', 'success')
            return redirect(url_for('admin.staff'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el usuario: {str(e)}', 'danger')
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en {getattr(form, field).label.text}: {error}", 'danger')
    return render_template('admin/edit_staff.html', form=form, user=user)

@admin_bp.route('/staff/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_staff(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'Recepcionista {user.get_full_name()} eliminado exitosamente.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el usuario: {str(e)}', 'danger')
    return redirect(url_for('admin.staff'))

@admin_bp.route('/staff/download_pdf')
@login_required
@admin_required
def download_all_staff_pdf():
    staff_members = User.query.filter_by(role='recepcionista').all()
    if not staff_members:
        flash("No hay personal registrado para generar el PDF.", "warning")
        return redirect(url_for('admin.staff'))

    headers = ["Nombre", "Email", "Teléfono", "Usuario"]
    data_rows = []
    for staff in staff_members:
        data_rows.append([
            staff.get_full_name(),
            staff.email,
            staff.phone or "-",
            staff.username
        ])

    buffer = create_pdf("Lista de Recepcionistas", headers, data_rows)
    return send_file(buffer, as_attachment=True, download_name="Personal_Recepcionistas.pdf", mimetype='application/pdf')