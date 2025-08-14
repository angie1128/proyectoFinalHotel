from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateField, IntegerField, FloatField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from wtforms.widgets import DateInput
from app.models.models import User, UserRole
from datetime import date

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    role = SelectField('Rol', choices=[
        (UserRole.GUEST.value, 'Huésped'),
        (UserRole.RECEPTIONIST.value, 'Recepcionista'),
        (UserRole.HOUSEKEEPING.value, 'Limpieza'),
        (UserRole.ADMIN.value, 'Administrador')
    ], validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('Nombre', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Apellido', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Teléfono', validators=[Length(max=20)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar Contraseña', 
                             validators=[DataRequired(), EqualTo('password')])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nombre de usuario ya está en uso.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email ya está registrado.')

class ReservationForm(FlaskForm):
    check_in = DateField('Fecha de Entrada', 
                        validators=[DataRequired()], 
                        widget=DateInput())
    check_out = DateField('Fecha de Salida', 
                         validators=[DataRequired()], 
                         widget=DateInput())
    adults = IntegerField('Adultos', validators=[DataRequired(), NumberRange(min=1, max=10)])
    children = IntegerField('Niños', validators=[NumberRange(min=0, max=10)], default=0)
    special_requests = TextAreaField('Solicitudes Especiales')
    
    def validate_check_out(self, check_out):
        if check_out.data <= self.check_in.data:
            raise ValidationError('La fecha de salida debe ser posterior a la fecha de entrada.')
        
    def validate_check_in(self, check_in):
        if check_in.data < date.today():
            raise ValidationError('La fecha de entrada no puede ser anterior a hoy.')

class RoomForm(FlaskForm):
    number = StringField('Número de Habitación', validators=[DataRequired(), Length(max=10)])
    floor = IntegerField('Piso', validators=[DataRequired(), NumberRange(min=1, max=50)])
    room_type_id = SelectField('Tipo de Habitación', coerce=int, validators=[DataRequired()])
    status = SelectField('Estado', choices=[
        ('available', 'Disponible'),
        ('occupied', 'Ocupada'),
        ('maintenance', 'Mantenimiento'),
        ('cleaning', 'Limpieza')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notas')
