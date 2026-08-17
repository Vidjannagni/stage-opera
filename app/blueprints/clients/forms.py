from flask_wtf import FlaskForm
from wtforms import (
    EmailField, FloatField, IntegerField, SelectField, StringField, SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired, Email, InputRequired, Length, NumberRange, Optional,
)

from ...models import Brief


class ClientForm(FlaskForm):
    """Fiche client.

    Les quatre premiers champs sont obligatoires : le cabinet a indiqué les
    recueillir *systématiquement* au premier entretien (cf. docs/retour_cabinet.md,
    réponse 5). Les rendre facultatifs laisserait passer des dossiers qu'un
    conseiller ne pourrait pas exploiter.
    """

    nom = StringField("Nom du client", validators=[DataRequired(), Length(max=120)])
    situation_professionnelle = StringField(
        "Situation professionnelle", validators=[DataRequired(), Length(max=120)],
        render_kw={"list": "liste-situations", "placeholder": "Ex. : Chef d'entreprise"},
    )
    nationalite = StringField(
        "Nationalité", validators=[DataRequired(), Length(max=80)],
        description="Conditionne l'accès au crédit et le rapatriement des fonds.",
        render_kw={"list": "liste-nationalites", "placeholder": "Ex. : Marocaine"},
    )
    budget_disponible = FloatField(
        "Budget disponible", validators=[InputRequired(), NumberRange(min=0)],
        render_kw={"placeholder": "Ex. : 1 500 000"},
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
        "Niveau de standing", default="Moyen standing",
        choices=[(s, s) for s in Brief.STANDINGS], validators=[DataRequired()],
    )
    zone_recherchee = StringField(
        "Zone géographique recherchée", validators=[DataRequired(), Length(max=160)],
        render_kw={"list": "liste-zones", "placeholder": "Ex. : Casablanca — Gauthier"},
    )
    superficie_min = FloatField(
        "Superficie minimale (m²)", validators=[Optional(), NumberRange(min=0)],
        render_kw={"placeholder": "Ex. : 70"},
    )
    superficie_max = FloatField(
        "Superficie maximale (m²)", validators=[Optional(), NumberRange(min=0)],
        render_kw={"placeholder": "Ex. : 100"},
    )

    nb_chambres = IntegerField("Chambres", validators=[Optional(), NumberRange(min=0, max=50)])
    nb_salles_bains = IntegerField("Salles de bains", validators=[Optional(), NumberRange(min=0, max=50)])
    nb_salons = IntegerField("Salons", validators=[Optional(), NumberRange(min=0, max=50)])
    etage = StringField(
        "Étage souhaité", validators=[Optional(), Length(max=40)],
        render_kw={"list": "liste-etages", "placeholder": "Ex. : 2e étage"},
    )
    orientation = StringField(
        "Orientation", validators=[Optional(), Length(max=40)],
        render_kw={"list": "liste-orientations", "placeholder": "Ex. : Sud"},
    )

    commodites = TextAreaField(
        "Commodités souhaitées", validators=[Optional()],
        description="Cochez ci-dessous, ou saisissez librement.",
        render_kw={"rows": 2, "placeholder": "Ex. : Transports en commun, écoles et crèches"},
    )
    type_acquisition = SelectField(
        "Type d'acquisition", default="existant",
        choices=list(Brief.TYPES_ACQUISITION), validators=[DataRequired()],
    )
    budget_min = FloatField(
        "Budget minimal", validators=[Optional(), NumberRange(min=0)],
        render_kw={"placeholder": "Ex. : 1 000 000"},
    )
    budget_max = FloatField(
        "Budget maximal", validators=[Optional(), NumberRange(min=0)],
        render_kw={"placeholder": "Ex. : 1 500 000"},
    )
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
        """Contrôles portant sur plusieurs champs à la fois.

        La superficie et le budget sont cités par le cabinet parmi les critères
        recueillis : on n'impose pas la fourchette complète — un client dit
        souvent « jusqu'à tant » sans plancher — mais au moins une des deux
        bornes.
        """
        if not super().validate(extra_validators):
            return False
        valide = True
        for bas, haut, libelle in (
            (self.superficie_min, self.superficie_max, "superficie"),
            (self.budget_min, self.budget_max, "budget"),
        ):
            if bas.data is None and haut.data is None:
                haut.errors.append(
                    f"Indiquez au moins une borne de {libelle} (minimale ou maximale)."
                )
                valide = False
            elif bas.data is not None and haut.data is not None and bas.data > haut.data:
                haut.errors.append(f"Le {libelle} maximal doit être supérieur au minimum.")
                valide = False
        return valide
