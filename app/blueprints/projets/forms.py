from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from ...models import Projet


def zero_si_vide(valeur):
    """Champ numérique laissé vide → 0 (les colonnes ne sont pas nullables).

    Ne pas appliquer aux champs *_override : NULL y signifie « utiliser la
    valeur de la zone ».
    """
    return 0.0 if valeur is None else valeur


def zero_entier_si_vide(valeur):
    """Variante entière de `zero_si_vide`, pour les colonnes Integer."""
    return 0 if valeur is None else valeur


class ProjetForm(FlaskForm):
    nom = StringField(
        "Nom du dossier", validators=[DataRequired(), Length(max=160)],
        render_kw={"placeholder": "Ex. : Appartement Gauthier — Casablanca"},
    )
    adresse = StringField(
        "Adresse / localisation", validators=[Optional(), Length(max=255)],
        render_kw={"list": "liste-zones", "placeholder": "Ex. : Quartier Gauthier, Casablanca"},
    )
    zone_id = SelectField("Zone de marché", coerce=int, validators=[DataRequired()])
    surface_m2 = FloatField(
        "Surface (m²)", validators=[Optional(), NumberRange(min=0)],
        render_kw={"placeholder": "Ex. : 85"},
    )
    type_operation = SelectField(
        "Type d'opération", default="locatif",
        choices=list(Projet.TYPES_OPERATION), validators=[DataRequired()],
        description="Un terrain ou une opération de revente n'a pas de loyer : "
                    "la valeur vient de la plus-value.",
    )
    statut = SelectField(
        "Où en est le dossier ?", default="recherche",
        choices=list(Projet.STATUTS), validators=[DataRequired()],
    )

    prix_bien = FloatField(
        "Prix du bien", validators=[DataRequired(), NumberRange(min=1)],
        render_kw={"placeholder": "Ex. : 1 200 000"},
    )
    budget_travaux = FloatField(
        "Budget travaux / construction", default=0.0,
        validators=[Optional(), NumberRange(min=0)], filters=[zero_si_vide],
        render_kw={"placeholder": "Ex. : 150 000 — ou 0 si rien à prévoir"},
    )
    taux_frais_override = FloatField(
        "Taux de frais d'acquisition (%)",
        validators=[Optional(), NumberRange(min=0, max=100)],
        description="Laisser vide pour utiliser le taux de la zone.",
    )
    delai_livraison_mois = IntegerField(
        "Délai de livraison (mois)", default=0,
        render_kw={"placeholder": "0 pour un bien déjà livré, 24 pour une VEFA"},
        validators=[Optional(), NumberRange(min=0, max=120)], filters=[zero_entier_si_vide],
        description="Achat sur plan (VEFA) : mois avant livraison. "
                    "Aucun loyer n'est perçu d'ici là.",
    )

    loyer_mensuel = FloatField(
        "Loyer mensuel attendu", default=0.0,
        validators=[Optional(), NumberRange(min=0)], filters=[zero_si_vide],
        render_kw={"placeholder": "Ex. : 8 500"},
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
        render_kw={"placeholder": "Ex. : 5 — laisser vide en gestion directe"},
    )
    vacance_pct = FloatField(
        "Vacance locative (% du loyer)", default=0.0,
        validators=[Optional(), NumberRange(min=0, max=100)], filters=[zero_si_vide],
        render_kw={"placeholder": "Ex. : 5 — soit environ trois semaines par an"},
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
    libelle = StringField(
        "Poste", validators=[DataRequired(), Length(max=160)],
        render_kw={"list": "liste-postes-travaux", "placeholder": "Ex. : Cuisine équipée"},
    )
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
    montant = FloatField(
        "Montant", validators=[DataRequired(), NumberRange(min=0.01)],
        render_kw={"placeholder": "Ex. : 80 000"},
    )
    submit_travaux = SubmitField("Ajouter le poste")
