from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional


class ClientForm(FlaskForm):
    nom = StringField("Nom du client", validators=[DataRequired(), Length(max=120)])
    email = EmailField("Adresse e-mail", validators=[Optional(), Email()])
    telephone = StringField("Téléphone", validators=[Optional(), Length(max=40)])
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Enregistrer")
