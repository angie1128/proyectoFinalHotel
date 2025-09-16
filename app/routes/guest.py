from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.room import Room
from app.models.reservation import Reservation
from app.forms.reservation import ReservationForm
from datetime import datetime

# Definimos un solo blueprint
guest_bp = Blueprint("guest", __name__, url_prefix="/guest")

# ----------------- DASHBOARD -----------------
@guest_bp.route('/dashboard')
@login_required
def dashboard():
    reservations = Reservation.query.filter_by(guest_id=current_user.id).order_by(Reservation.created_at.desc()).all()
    current_reservation = Reservation.query.filter_by(
        guest_id=current_user.id,
        status='confirmada'
    ).filter(
        Reservation.checked_in_at.isnot(None),
        Reservation.checked_out_at.is_(None)
    ).first()
    
    return render_template(
        'guest/dashboard.html', 
        reservations=reservations,
        current_reservation=current_reservation
    )

# ----------------- PERFIL -----------------
@guest_bp.route("/profile")
@login_required
def profile():
    return render_template("guest/profile.html", user=current_user)

@guest_bp.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    email = request.form.get("email")
    phone = request.form.get("phone")
    username = request.form.get("username")

    if not email or not username:
        flash("El correo y el usuario son obligatorios.", "danger")
        return redirect(url_for("guest.profile"))

    existing_email = current_user.__class__.query.filter_by(email=email).first()
    if existing_email and existing_email.id != current_user.id:
        flash("Ese correo ya está en uso.", "danger")
        return redirect(url_for("guest.profile"))

    existing_username = current_user.__class__.query.filter_by(username=username).first()
    if existing_username and existing_username.id != current_user.id:
        flash("Ese nombre de usuario ya está en uso.", "danger")
        return redirect(url_for("guest.profile"))

    current_user.email = email
    current_user.phone = phone
    current_user.username = username
    db.session.commit()

    flash("Perfil actualizado con éxito.", "success")
    return redirect(url_for("guest.profile"))

# ----------------- RESERVAS -----------------
@guest_bp.route('/reserve', methods=['GET', 'POST'])
@login_required
def reserve():
    available_rooms = Room.query.filter_by(status='disponible').all()
    form = ReservationForm()
    form.room_id.choices = [(r.id, f'Habitación {r.number} - {r.get_type_display()} (${r.price}/noche)') 
                            for r in available_rooms]

    if form.validate_on_submit():
        room = Room.query.get(int(form.room_id.data))
        if not room or room.status != 'disponible':
            flash('La habitación seleccionada no está disponible.', 'danger')
            return redirect(url_for('guest.reserve'))

        nights = (form.check_out_date.data - form.check_in_date.data).days
        if nights <= 0:
            flash('La fecha de check-out debe ser posterior a la de check-in.', 'danger')
            return redirect(url_for('guest.reserve'))

        total_price = room.price * nights

        reservation = Reservation(
            guest_id=current_user.id,
            room_id=room.id,
            check_in_date=form.check_in_date.data,
            check_out_date=form.check_out_date.data,
            guests_count=form.guests_count.data,
            total_price=total_price,
            special_requests=form.special_requests.data,
            status='pendiente'
        )

        db.session.add(reservation)
        db.session.commit()

        flash(f'¡Reservación creada exitosamente! Total: ${total_price:.2f}', 'success')
        return redirect(url_for('guest.reservations'))

    return render_template("guest/reserve.html", form=form, available_rooms=available_rooms)

@guest_bp.route('/reservations')
@login_required
def reservations():
    reservations = Reservation.query.filter_by(guest_id=current_user.id).order_by(Reservation.created_at.desc()).all()
    total_reservations = len(reservations)
    pending_reservations = len([r for r in reservations if r.status == 'pendiente'])
    confirmed_reservations = len([r for r in reservations if r.status == 'confirmada'])
    completed_reservations = len([r for r in reservations if r.status == 'completada'])
    
    return render_template(
        'guest/reservations.html', 
        reservations=reservations,
        total_reservations=total_reservations,
        pending_reservations=pending_reservations,
        confirmed_reservations=confirmed_reservations,
        completed_reservations=completed_reservations
    )

@guest_bp.route('/reservation/<int:id>')
@login_required
def view_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    if reservation.guest_id != current_user.id:
        flash("No tienes permiso para ver esta reservación.", "danger")
        return redirect(url_for('guest.reservations'))
    return render_template('guest/view_reservation.html', reservation=reservation)

# ----------------- HABITACIONES -----------------
@guest_bp.route("/rooms")
@login_required
def rooms():
    rooms = Room.query.all()
    return render_template("guest/rooms.html", rooms=rooms)

@guest_bp.route('/book/<int:room_id>', methods=['GET', 'POST'])
@login_required
def book_room(room_id):
    room = Room.query.get_or_404(room_id)
    if request.method == 'POST':
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')

        if not check_in or not check_out:
            flash("Debe seleccionar fechas válidas.", "danger")
            return redirect(url_for('guest.book_room', room_id=room.id))

        reservation = Reservation(
            guest_id=current_user.id,
            room_id=room.id,
            check_in_date=datetime.strptime(check_in, "%Y-%m-%d"),
            check_out_date=datetime.strptime(check_out, "%Y-%m-%d"),
            total_price=room.price
        )
        db.session.add(reservation)
        db.session.commit()
        flash("Habitación reservada con éxito.", "success")
        return redirect(url_for('guest.reservations'))

    return render_template('guest/book_room.html', room=room)


@guest_bp.route('/reservations/<int:id>/cancel', methods=['POST', 'GET'])
@login_required
def cancel_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    if reservation.guest_id != current_user.id:
        flash("No tienes permiso para cancelar esta reservación.", "danger")
        return redirect(url_for('guest.reservations'))

    reservation.status = 'cancelada'
    db.session.commit()
    flash("Reservación cancelada exitosamente.", "success")
    return redirect(url_for('guest.reservations'))
