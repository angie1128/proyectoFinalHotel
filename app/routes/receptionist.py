from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app import db
from app.models.room import Room
from app.models.reservation import Reservation
from app.forms.checkin import CheckinForm
from app.forms.reservation import ReservationForm   # ✅ agregado
from app.models.user import User
from datetime import datetime
from functools import wraps
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from app.forms.profile import EditProfileForm

# --- BLUEPRINT ---
receptionist_bp = Blueprint(
    "receptionist",
    __name__,
    url_prefix="/receptionist",
    template_folder="templates/receptionist"
)

# --- Decorador para recepcionista ---
def receptionist_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_receptionist() or current_user.is_admin()):
            flash('Acceso denegado. Se requieren permisos de recepcionista.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


# --- DASHBOARD ---
@receptionist_bp.route('/dashboard')
@login_required
@receptionist_required
def dashboard():
    today = datetime.now().date()
    todays_checkins = Reservation.query.filter_by(check_in_date=today, status='confirmada').all()
    todays_checkouts = Reservation.query.filter(
        Reservation.check_out_date == today,
        Reservation.checked_in_at.isnot(None),
        Reservation.checked_out_at.is_(None)
    ).all()

    available_rooms = Room.query.filter_by(status='disponible').count()
    occupied_rooms = Room.query.filter_by(status='ocupada').count()
    maintenance_rooms = Room.query.filter_by(status='mantenimiento').count()

    return render_template(
        'receptionist/dashboard.html',
        current_time=datetime.now(),
        available_rooms=available_rooms,
        occupied_rooms=occupied_rooms,
        maintenance_rooms=maintenance_rooms,
        pending_checkins=len(todays_checkins),
        pending_checkouts=len(todays_checkouts),
        todays_checkins=todays_checkins,
        todays_checkouts=todays_checkouts
    )


# --- ROOMS ---
@receptionist_bp.route('/rooms')
@login_required
@receptionist_required
def rooms():
    rooms = Room.query.all()
    return render_template('receptionist/rooms.html', rooms=rooms)


# --- RESERVATIONS ---
@receptionist_bp.route("/reservations")
@login_required
@receptionist_required
def reservations():
    reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
    return render_template("receptionist/reservations.html", reservations=reservations)


@receptionist_bp.route("/reservations/new", methods=["GET", "POST"])
@login_required
@receptionist_required
def new_reservation():
    form = ReservationForm()

    # Cargar huéspedes disponibles (solo rol = huésped)
    guests = User.query.filter_by(role="huesped").all()
    form.guest_id.choices = [(u.id, u.get_full_name()) for u in guests]

    # Cargar habitaciones disponibles
    available_rooms = Room.query.all()
    if available_rooms:
        form.room_id.choices = [(r.id, f'Habitación {r.number} - {r.get_type_display()} (${r.price}/noche)')
                               for r in available_rooms]
    else:
        form.room_id.choices = [(-1, 'No hay habitaciones disponibles')]

    if form.validate_on_submit():
        # Buscar la habitación seleccionada
        room = Room.query.get(form.room_id.data)

        if not room or room.status != "disponible":
            flash("⚠️ La habitación seleccionada ya no está disponible.", "danger")
            return redirect(url_for("receptionist.new_reservation"))

        # Calcular precio total (ejemplo: días * precio habitación)
        nights = (form.check_out_date.data - form.check_in_date.data).days
        total_price = nights * room.price

        # Crear la reserva
        reservation = Reservation(
            guest_id=form.guest_id.data,
            room_id=room.id,
            check_in_date=form.check_in_date.data,
            check_out_date=form.check_out_date.data,
            guests_count=form.guests_count.data,
            total_price=total_price,
            special_requests=form.special_requests.data,
            status="pendiente"
        )
        db.session.add(reservation)

        # Marcar la habitación como ocupada
        room.status = "ocupada"
        db.session.commit()

        flash("✅ Reserva creada exitosamente.", "success")
        return redirect(url_for("receptionist.reservations"))

    return render_template(
        "receptionist/new_reservation.html",
        form=form,
        available_rooms=available_rooms
    )


@receptionist_bp.route("/reservation/<int:reservation_id>")
@login_required
@receptionist_required
def reservation_detail(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    return render_template("receptionist/reservation_detail.html", reservation=reservation)


# --- UPDATE STATUS (ÚNICA VERSIÓN) ---
@receptionist_bp.route("/reservation/<int:reservation_id>/update/<string:status>")
@login_required
@receptionist_required
def update_status(reservation_id, status):
    reservation = Reservation.query.get_or_404(reservation_id)

    if status == "confirmada":
        reservation.status = "confirmada"
        reservation.confirmed_at = datetime.utcnow()
    elif status == "cancelada":
        reservation.status = "cancelada"
    elif status == "checkin":
        reservation.checked_in_at = datetime.utcnow()
        reservation.status = "en curso"
        reservation.room.status = "ocupada"
    elif status == "checkout":
        reservation.checked_out_at = datetime.utcnow()
        reservation.status = "completada"
        reservation.room.status = "limpieza"

    db.session.commit()
    flash("Estado de la reserva actualizado.", "success")
    return redirect(url_for("receptionist.reservation_detail", reservation_id=reservation.id))


# --- GENERAR PDF DE RESERVAS ---
@receptionist_bp.route("/reservations/pdf")
@login_required
@receptionist_required
def reservations_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    pink_style = ParagraphStyle(
        "PinkTitle",
        parent=styles["Heading1"],
        textColor=colors.HexColor("#e91e63"),
        fontSize=18,
        spaceAfter=12
    )
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f8bbd0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ])

    story = []
    story.append(Paragraph("Reporte de Reservas", pink_style))
    story.append(Spacer(1, 12))

    reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
    data = [["ID", "Huésped", "Habitación", "Check-in", "Check-out", "Estado"]]

    for r in reservations:
        guest_name = r.guest.get_full_name() if r.guest else "N/A"
        data.append([
            str(r.id),
            guest_name,
            r.room.number if r.room else "N/A",
            r.check_in_date.strftime("%d/%m/%Y"),
            r.check_out_date.strftime("%d/%m/%Y"),
            r.get_status_display()
        ])

    table = Table(data, colWidths=[40, 120, 80, 80, 80, 80])
    table.setStyle(table_style)
    story.append(table)

    doc.build(story)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="reporte_reservas.pdf",
        mimetype="application/pdf"
    )


# --- CHECK-IN ---
@receptionist_bp.route('/checkin')
@login_required
@receptionist_required
def checkin_page():
    today = datetime.now().date()
    reservations = Reservation.query.filter_by(check_in_date=today, status='confirmada').all()
    form = CheckinForm()
    return render_template('receptionist/checkin.html', reservations=reservations, form=form)


@receptionist_bp.route('/checkin/<int:reservation_id>')
@login_required
@receptionist_required
def checkin(reservation_id):
    res = Reservation.query.get_or_404(reservation_id)
    if res.status == 'confirmada' and res.check_in_date <= datetime.now().date():
        res.checked_in_at = datetime.utcnow()
        res.room.status = 'ocupada'
        db.session.commit()
        flash(f'Check-in realizado para {res.guest.get_full_name()}.', 'success')
    else:
        flash('No se puede realizar el check-in.', 'warning')
    return redirect(url_for('receptionist.checkin_page'))


@receptionist_bp.route('/checkin/new', methods=['GET', 'POST'])
@login_required
@receptionist_required
def new_checkin():
    form = CheckinForm()
    guest = None
    guest_reservations = []

    if form.validate_on_submit():
        guest = User.query.filter_by(email=form.guest_email.data).first()
        if not guest:
            flash("No existe un usuario con ese correo.", "danger")
            return redirect(url_for('receptionist.new_checkin'))
        
        guest_reservations = Reservation.query.filter(
            Reservation.guest_id == guest.id,
            Reservation.status.in_(['pendiente', 'confirmada'])
        ).all()
        
        if not guest_reservations:
            flash("El huésped no tiene reservas activas. Puedes crear un check-in desde cero.", "info")

    rooms = Room.query.all()

    return render_template(
        'receptionist/new_checkin.html',
        form=form,
        guest=guest,
        guest_reservations=guest_reservations,
        rooms=rooms
    )


@receptionist_bp.route('/checkin/select/<int:guest_id>/<int:room_id>/<check_out_date>')
@login_required
@receptionist_required
def checkin_select_room(guest_id, room_id, check_out_date):
    guest = User.query.get_or_404(guest_id)
    room = Room.query.get_or_404(room_id)

    if room.status != 'disponible':
        flash(f'La habitación {room.number} no está disponible.', 'warning')
        return redirect(url_for('receptionist.new_checkin'))

    reservation = Reservation(
        guest_id=guest.id,
        room_id=room.id,
        check_in_date=datetime.now().date(),
        check_out_date=datetime.strptime(check_out_date, "%Y-%m-%d").date(),
        status='confirmada',
        checked_in_at=datetime.utcnow()
    )
    room.status = 'ocupada'
    db.session.add(reservation)
    db.session.commit()
    flash(f'Check-in realizado para {guest.get_full_name()} en habitación {room.number}.', 'success')
    return redirect(url_for('receptionist.new_checkin'))


# --- CHECK-OUT ---
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
        flash(f'Check-out realizado para {reservation.room.number}', 'success')
    else:
        flash('No se puede realizar el check-out.', 'warning')
    return redirect(url_for('receptionist.checkin_page'))


@receptionist_bp.route('/checkout')
@login_required
@receptionist_required
def checkout_page():
    todays_checkouts = Reservation.query.filter(
        Reservation.check_out_date == datetime.now().date(),
        Reservation.checked_in_at.isnot(None),
        Reservation.checked_out_at.is_(None)
    ).all()
    return render_template('receptionist/checkout.html', todays_checkouts=todays_checkouts)


# --- PAYMENTS ---
@receptionist_bp.route('/payments')
@login_required
@receptionist_required
def payments():
    reservations_with_payments = Reservation.query.filter(
        Reservation.status.in_(['confirmada', 'en curso', 'completada'])
    ).order_by(Reservation.created_at.desc()).all()
    return render_template('receptionist/payments.html', reservations=reservations_with_payments)


# Ruta para actualizar el tipo de pago
@receptionist_bp.route('/payments/update/<int:reservation_id>', methods=['POST'])
@login_required
@receptionist_required
def update_payment(reservation_id):
    from flask import request, redirect, url_for, flash
    res = Reservation.query.get_or_404(reservation_id)

    payment_type = request.form.get('payment_type')
    payment_detail = None

    if payment_type == 'efectivo':
        payment_detail = f"Valor recibido: {request.form.get('cash_amount')}"
    elif payment_type == 'transferencia':
        payment_detail = f"Plataforma: {request.form.get('transfer_method')}"
    elif payment_type == 'tarjeta':
        card_number = request.form.get('card_number')
        last_digits = card_number[-4:] if card_number else "N/A"
        payment_detail = f"Tarjeta terminada en {last_digits}"

    res.payment_type = payment_type
    res.payment_detail = payment_detail

    db.session.commit()
    flash('Pago registrado correctamente', 'success')
    return redirect(url_for('receptionist.payments'))

@receptionist_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@receptionist_required
def profile():
    form = EditProfileForm(
        original_username=current_user.username,
        original_email=current_user.email,
        obj=current_user
    )

    if form.validate_on_submit():
        # Actualizar datos básicos
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data

        # Actualizar contraseña solo si se ingresó
        if form.password.data:
            current_user.set_password(form.password.data)

        db.session.commit()
        flash("✅ Perfil actualizado correctamente.", "success")
        return redirect(url_for('receptionist.profile'))

    return render_template(
        'receptionist/profile.html',
        form=form,
        user=current_user
    )
