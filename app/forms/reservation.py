from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, IntegerField, TextAreaField, SubmitField, FloatField, HiddenField, RadioField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from datetime import date, datetime
from app.models.room import Room

class ReservationForm(FlaskForm):
    guest_id = SelectField("Huésped", coerce=int, validators=[DataRequired()])
    check_in_date = DateField("Check-in", validators=[DataRequired()])
    check_out_date = DateField("Check-out", validators=[DataRequired()])
    guests_count = IntegerField("Número de huéspedes", validators=[DataRequired(), NumberRange(min=1, max=4)])
    room_id = RadioField("Habitación", coerce=int, validators=[DataRequired(message="Debes seleccionar una habitación")])
    total_price = HiddenField()
    special_requests = TextAreaField("Peticiones especiales")
    submit = SubmitField("Confirmar Reserva")

    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
    
    def validate_check_in_date(self, check_in_date):
        if check_in_date.data < date.today():
            raise ValidationError('La fecha de check-in no puede ser anterior a hoy.')
    
    def validate_check_out_date(self, check_out_date):
        if hasattr(self, 'check_in_date') and self.check_in_date.data:
            if check_out_date.data <= self.check_in_date.data:
                raise ValidationError('La fecha de check-out debe ser posterior a la de check-in.')

class PublicReservationForm(FlaskForm):
    check_in_date = DateField("Fecha de llegada", validators=[DataRequired()])
    check_out_date = DateField("Fecha de salida", validators=[DataRequired()])
    guests_count = IntegerField("Número de huéspedes", default=1, validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField("Buscar Habitaciones Disponibles")

    def validate_check_in_date(self, check_in_date):
        if check_in_date.data < date.today():
            raise ValidationError('La fecha de llegada no puede ser anterior a hoy.')

    def validate_check_out_date(self, check_out_date):
        if hasattr(self, 'check_in_date') and self.check_in_date.data:
            if check_out_date.data <= self.check_in_date.data:
                raise ValidationError('La fecha de salida debe ser posterior a la de llegada.')

class ReservationStatusForm(FlaskForm):
    reservation_id = HiddenField()
    action = HiddenField()
    submit = SubmitField('Confirmar')
