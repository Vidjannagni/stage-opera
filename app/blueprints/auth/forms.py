from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class LoginForm(FlaskForm):
    email = EmailField("Adresse e-mail", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Se connecter")


class RegisterForm(FlaskForm):
    nom = StringField("Nom complet", validators=[DataRequired(), Length(max=120)])
    email = EmailField("Adresse e-mail", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Mot de passe", validators=[DataRequired(), Length(min=8, message="8 caractères minimum")]
    )
    confirm = PasswordField(
        "Confirmation",
        validators=[DataRequired(), EqualTo("password", message="Les mots de passe diffèrent")],
    )
    # Vérifié seulement si CODE_INSCRIPTION est défini (déploiement en ligne) :
    # sans cette variable, l'inscription reste libre comme en local.
    code_inscription = StringField(
        "Code d'inscription", validators=[Optional()],
        description="Fourni par le cabinet.",
    )
    submit = SubmitField("Créer le compte")
