from flask import Blueprint, render_template, request, jsonify
from app.models import Room, Booking
from datetime import datetime, date

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Obtener habitaciones destacadas
    featured_rooms = Room.query.filter_by(is_available=True).limit(6).all()
    return render_template('index.html', featured_rooms=featured_rooms)

@main_bp.route('/rooms')
def rooms():
    page = request.args.get('page', 1, type=int)
    room_type = request.args.get('type', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    query = Room.query.filter_by(is_available=True)
    
    if room_type:
        query = query.filter(Room.room_type == room_type)
    if min_price:
        query = query.filter(Room.price_per_night >= min_price)
    if max_price:
        query = query.filter(Room.price_per_night <= max_price)
    
    rooms = query.paginate(
        page=page, per_page=9, error_out=False
    )
    
    room_types = Room.query.with_entities(Room.room_type).distinct().all()
    room_types = [rt[0] for rt in room_types]
    
    return render_template('rooms.html', 
                         rooms=rooms, 
                         room_types=room_types,
                         current_type=room_type,
                         min_price=min_price,
                         max_price=max_price)

@main_bp.route('/room/<int:room_id>')
def room_detail(room_id):
    room = Room.query.get_or_404(room_id)
    return render_template('room_detail.html', room=room)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route('/api/check-availability')
def check_availability():
    room_id = request.args.get('room_id', type=int)
    check_in_str = request.args.get('check_in')
    check_out_str = request.args.get('check_out')
    
    if not all([room_id, check_in_str, check_out_str]):
        return jsonify({'available': False, 'error': 'Faltan parámetros'})
    
    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
        
        if check_in >= check_out or check_in < date.today():
            return jsonify({'available': False, 'error': 'Fechas inválidas'})
        
        room = Room.query.get(room_id)
        if not room:
            return jsonify({'available': False, 'error': 'Habitación no encontrada'})
        
        available = room.is_available_for_dates(check_in, check_out)
        nights = (check_out - check_in).days
        total_price = float(room.price_per_night) * nights
        
        return jsonify({
            'available': available,
            'nights': nights,
            'total_price': total_price,
            'price_per_night': float(room.price_per_night)
        })
        
    except ValueError:
        return jsonify({'available': False, 'error': 'Formato de fecha inválido'})
