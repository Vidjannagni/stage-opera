from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


def zero_si_vide(valeur):
    """Champ numérique laissé vide → 0 (les colonnes ne sont pas nullables).

    Ne pas appliquer aux champs *_override : NULL y signifie « utiliser la
    valeur de la zone ».
    """
    return 0.0 if valeur is None else valeur


class ProjetForm(FlaskForm):
    nom = StringField("Nom du projet", validators=[DataRequired(), Length(max=160)])
    adresse = StringField("Adresse / localisation", validators=[Optional(), Length(max=255)])
    zone_id = SelectField("Zone de marché", coerce=int, validators=[DataRequired()])
    surface_m2 = FloatField("Surface (m²)", validators=[Optional(), NumberRange(min=0)])

    prix_bien = FloatField(
        "Prix du bien", validators=[DataRequired(), NumberRange(min=1)]
    )
    budget_travaux = FloatField(
        "Budget travaux", default=0.0,
        validators=[Optional(), NumberRange(min=0)], filters=[zero_si_vide],
    )
    taux_frais_override = FloatField(
        "Taux de frais d'acquisition (%)",
        validators=[Optional(), NumberRange(min=0, max=100)],
        description="Laisser vide pour utiliser le taux de la zone.",
    )

    loyer_mensuel = FloatField(
        "Loyer mensuel attendu", validators=[DataRequired(), NumberRange(min=0)]
    )
    charges_copro_annuelles = FloatField(
        "Charges de copropriété (annuelles)", default=0.0,
        validators=[Optional(), NumberRange(min=0)], filters=[zero_si_vide],
    )
    assurance_annuelle = FloatField(
        "Assurance (annuelle)", default=0.0,
        validators=[Optional(), NumberRange(min=0)], filters=[zero_si_vide],
    )
    frais_gestion_pct = FloatField(
        "Frais de gestion (% du loyer)", default=0.0,
        validators=[Optional(), NumberRange(min=0, max=100)], filters=[zero_si_vide],
    )
    vacance_pct = FloatField(
        "Vacance locative (% du loyer)", default=0.0,
        validators=[Optional(), NumberRange(min=0, max=100)], filters=[zero_si_vide],
    )
    entretien_annuel = FloatField(
        "Entretien (annuel)", default=0.0,
        validators=[Optional(), NumberRange(min=0)], filters=[zero_si_vide],
    )
    taxe_annuelle = FloatField(
        "Taxe annuelle (foncière / services communaux)", default=0.0,
        validators=[Optional(), NumberRange(min=0)], filters=[zero_si_vide],
    )
    taux_imposition_override = FloatField(
        "Taux d'imposition effectif (%)",
        validators=[Optional(), NumberRange(min=0, max=100)],
        description="Laisser vide pour utiliser le taux par défaut de la zone.",
    )

    submit = SubmitField("Enregistrer")


class LigneTravauxForm(FlaskForm):
    libelle = StringField("Poste", validators=[DataRequired(), Length(max=160)])
    categorie = SelectField(
        "Catégorie",
        choices=[
            ("Gros œuvre", "Gros œuvre"),
            ("Second œuvre", "Second œuvre"),
            ("Électricité / Plomberie", "Électricité / Plomberie"),
            ("Cuisine / Salle de bain", "Cuisine / Salle de bain"),
            ("Décoration", "Décoration"),
            ("Autre", "Autre"),
        ],
    )
    montant = FloatField("Montant", validators=[DataRequired(), NumberRange(min=0.01)])
    submit_travaux = SubmitField("Ajouter le poste")
