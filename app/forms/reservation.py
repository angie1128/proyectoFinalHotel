from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, IntegerField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from datetime import date, datetime
from app.models.room import Room

class ReservationForm(FlaskForm):
    room_id = SelectField('Habitación', coerce=int, validators=[DataRequired()])
    check_in_date = DateField('Fecha de Check-in', validators=[DataRequired()])
    check_out_date = DateField('Fecha de Check-out', validators=[DataRequired()])
    guests_count = IntegerField('Número de Huéspedes', validators=[DataRequired(), NumberRange(min=1)])
    special_requests = TextAreaField('Solicitudes Especiales')
    submit = SubmitField('Reservar')
    
    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        self.room_id.choices = [(r.id, f'Habitación {r.number} - {r.get_type_display()} (${r.price}/noche)') 
                               for r in Room.query.filter_by(status='disponible').all()]
    
    def validate_check_in_date(self, check_in_date):
        if check_in_date.data < date.today():
            raise ValidationError('La fecha de check-in no puede ser anterior a hoy.')
    
    def validate_check_out_date(self, check_out_date):
        if hasattr(self, 'check_in_date') and self.check_in_date.data:
            if check_out_date.data <= self.check_in_date.data:
                raise ValidationError('La fecha de check-out debe ser posterior a la de check-in.')

class ReservationStatusForm(FlaskForm):
    reservation_id = HiddenField()
    action = HiddenField()
    submit = SubmitField('Confirmar')
