from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Email

class CheckinForm(FlaskForm):
    guest_email = StringField("Correo del huésped", validators=[DataRequired(), Email()])
    check_out_date = DateField("Fecha de salida", validators=[DataRequired()])
    submit = SubmitField("Buscar Huésped")
