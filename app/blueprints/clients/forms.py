from flask_wtf import FlaskForm
from wtforms import (
    EmailField, FloatField, IntegerField, SelectField, StringField, SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

from ...models import Brief


class ClientForm(FlaskForm):
    """Fiche client. Le cabinet recueille systématiquement nom, situation
    professionnelle, nationalité et budget disponible."""

    nom = StringField("Nom du client", validators=[DataRequired(), Length(max=120)])
    situation_professionnelle = StringField(
        "Situation professionnelle", validators=[Optional(), Length(max=120)],
        description="Salarié, profession libérale, chef d'entreprise, retraité…",
    )
    nationalite = StringField(
        "Nationalité", validators=[Optional(), Length(max=80)],
        description="Conditionne l'accès au crédit et le rapatriement des fonds.",
    )
    budget_disponible = FloatField(
        "Budget disponible", validators=[Optional(), NumberRange(min=0)]
    )
    email = EmailField("Adresse e-mail", validators=[Optional(), Email()])
    telephone = StringField("Téléphone", validators=[Optional(), Length(max=40)])
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Enregistrer")


class BriefForm(FlaskForm):
    """Cahier de recherche renseigné au premier entretien."""

    type_bien = SelectField(
        "Type de bien recherché", default="Appartement",
        choices=[(t, t) for t in Brief.TYPES_BIEN], validators=[DataRequired()],
    )
    standing = SelectField(
        "Niveau de standing",
        choices=[("", "— non précisé —")] + [(s, s) for s in Brief.STANDINGS],
        validators=[Optional()],
    )
    zone_recherchee = StringField(
        "Zone géographique recherchée", validators=[Optional(), Length(max=160)]
    )
    superficie_min = FloatField("Superficie minimale (m²)", validators=[Optional(), NumberRange(min=0)])
    superficie_max = FloatField("Superficie maximale (m²)", validators=[Optional(), NumberRange(min=0)])

    nb_chambres = IntegerField("Chambres", validators=[Optional(), NumberRange(min=0, max=50)])
    nb_salles_bains = IntegerField("Salles de bains", validators=[Optional(), NumberRange(min=0, max=50)])
    nb_salons = IntegerField("Salons", validators=[Optional(), NumberRange(min=0, max=50)])
    etage = StringField("Étage souhaité", validators=[Optional(), Length(max=40)])
    orientation = StringField("Orientation", validators=[Optional(), Length(max=40)])

    commodites = TextAreaField(
        "Commodités souhaitées", validators=[Optional()],
        description="Transports, écoles, commerces, santé…",
    )
    type_acquisition = SelectField(
        "Type d'acquisition", default="existant",
        choices=list(Brief.TYPES_ACQUISITION), validators=[DataRequired()],
    )
    budget_min = FloatField("Budget minimal", validators=[Optional(), NumberRange(min=0)])
    budget_max = FloatField("Budget maximal", validators=[Optional(), NumberRange(min=0)])
    mode_financement = SelectField(
        "Mode de financement", default="pret",
        choices=list(Brief.MODES_FINANCEMENT), validators=[DataRequired()],
    )

    objectif = SelectField(
        "Objectif de l'investissement", default="revenu",
        choices=list(Brief.OBJECTIFS), validators=[DataRequired()],
    )
    horizon_annees = IntegerField(
        "Horizon d'investissement (années)", default=10,
        validators=[DataRequired(), NumberRange(min=1, max=50)],
        description="Le facteur temps départage deux dossiers autrement comparables.",
    )

    submit = SubmitField("Enregistrer le brief")

    def validate(self, extra_validators=None) -> bool:
        if not super().validate(extra_validators):
            return False
        valide = True
        for bas, haut, libelle in (
            (self.superficie_min, self.superficie_max, "superficie"),
            (self.budget_min, self.budget_max, "budget"),
        ):
            if bas.data is not None and haut.data is not None and bas.data > haut.data:
                haut.errors.append(f"Le {libelle} maximal doit être supérieur au minimum.")
                valide = False
        return valide
