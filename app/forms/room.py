from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length
from app.models.room import Room

class RoomForm(FlaskForm):
    number = StringField('Número de Habitación', validators=[DataRequired(), Length(max=10)])
    type = SelectField('Tipo', choices=[
        ('individual', 'Individual'),
        ('doble', 'Doble'),
        ('suite', 'Suite'),
        ('familiar', 'Familiar')
    ], validators=[DataRequired()])
    price = FloatField('Precio por Noche', validators=[DataRequired(), NumberRange(min=0)])
    max_occupancy = IntegerField('Capacidad Máxima', validators=[DataRequired(), NumberRange(min=1, max=10)])
    description = TextAreaField('Descripción')
    amenities = TextAreaField('Comodidades')
    status = SelectField('Estado', choices=[
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('mantenimiento', 'En Mantenimiento'),
        ('limpieza', 'En Limpieza')
    ], validators=[DataRequired()])
    submit = SubmitField('Guardar')
    
    def __init__(self, original_room=None, *args, **kwargs):
        super(RoomForm, self).__init__(*args, **kwargs)
        self.original_room = original_room
    
    def validate_number(self, number):
        if self.original_room is None or number.data != self.original_room.number:
            room = Room.query.filter_by(number=number.data).first()
            if room:
                raise ValidationError('Este número de habitación ya existe.')
