from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, TextAreaField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from app.models.room import Room

class RoomForm(FlaskForm):
    number = StringField('Número de Habitación', validators=[DataRequired(), Length(max=50)])
    type = SelectField('Tipo', choices=[('individual', 'Individual'), ('doble', 'Doble'), ('suite', 'Suite'), ('familiar', 'Familiar')], validators=[DataRequired()])
    max_occupancy = IntegerField('Capacidad Máxima', validators=[DataRequired(), NumberRange(min=1)])
    price = FloatField('Precio por Noche', validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField('Descripción', validators=[Length(max=500)])
    amenities = TextAreaField('Comodidades', validators=[Length(max=500)])
    status = SelectField('Estado', choices=[('disponible', 'Disponible'), ('ocupada', 'Ocupada'), ('mantenimiento', 'Mantenimiento'), ('limpieza', 'Limpieza')], validators=[DataRequired()])
    image = FileField('Imagen')
    submit = SubmitField('Guardar')

    def __init__(self, *args, **kwargs):
        super(RoomForm, self).__init__(*args, **kwargs)
        self.room = kwargs.get('obj')  # Obtener el objeto Room si existe (para edición)

    def validate_number(self, number):
        # Excluir el registro actual si estamos editando
        if self.room and self.room.id:
            if Room.query.filter_by(number=number.data).filter(Room.id != self.room.id).first():
                raise ValidationError('Este número de habitación ya existe.')
        else:
            if Room.query.filter_by(number=number.data).first():
                raise ValidationError('Este número de habitación ya existe.')