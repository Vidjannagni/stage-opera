from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from ...core import coherence
from ...models import Projet


def zero_si_vide(valeur):
    """Champ numérique laissé vide → 0 (les colonnes ne sont pas nullables).

    Ne pas appliquer aux champs *_override : NULL y signifie « utiliser la
    valeur de la zone ».

    C'est ce filtre qui permet aux champs de charges de n'avoir *aucune* valeur
    par défaut : un formulaire vierge s'affiche vide, avec ses exemples en
    filigrane, au lieu d'une colonne de « 0.0 » qui donne l'impression d'un
    formulaire déjà rempli — et qui empêchait de distinguer « pas de frais de
    gestion » de « champ pas encore rempli ».
    """
    return 0.0 if valeur is None else valeur


def zero_entier_si_vide(valeur):
    """Variante entière de `zero_si_vide`, pour les colonnes Integer."""
    return 0 if valeur is None else valeur


class ChampMontant(FloatField):
    """Champ numérique où **zéro s'affiche comme un champ vide**.

    Sans cela, un formulaire vierge s'ouvrait sur une colonne de « 0.0 » :
    l'écran paraissait déjà rempli, les exemples en filigrane n'apparaissaient
    jamais, et le conseiller devait effacer chaque zéro avant de saisir. Comme
    le formulaire annonce que « les champs vides valent zéro », afficher le
    vide plutôt que le zéro dit exactement la même chose, en moins encombrant.
    """

    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        return "" if not self.data else str(self.data)


class ChampEntier(IntegerField):
    """Variante entière de `ChampMontant` (délai de livraison, durées)."""

    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        return "" if not self.data else str(self.data)


class ProjetForm(FlaskForm):
    """Le chiffrage d'un bien précis, proposé à un client.

    À ne pas confondre avec le brief : celui-ci dit ce que le client cherche
    (fourchettes, objectif), celui-là chiffre **un bien** qu'on lui propose.

    Le formulaire suit l'avancement du dossier. Tant qu'on en est à la
    recherche, aucun bien n'est arrêté : demander son adresse et sa superficie
    n'aurait pas de sens, et les fourchettes du brief suffisent — le prix
    saisi est alors une hypothèse de travail. Ces champs apparaissent à partir
    de la présentation au client, quand le bien existe vraiment.
    """

    #: Ce qui ne se demande qu'une fois un bien identifié.
    CHAMPS_DU_BIEN = ("adresse", "surface_m2")

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
    budget_travaux = ChampMontant(
        "Budget travaux / construction",
        validators=[Optional(), NumberRange(min=0)], filters=[zero_si_vide],
        render_kw={"placeholder": "Ex. : 150 000 — ou 0 si rien à prévoir"},
    )
    taux_frais_override = FloatField(
        "Taux de frais d'acquisition (%)",
        validators=[Optional(), NumberRange(min=0, max=100)],
        description="Laisser vide pour utiliser le taux de la zone.",
    )
    delai_livraison_mois = ChampEntier(
        "Délai de livraison (mois)",
        render_kw={"placeholder": "0 pour un bien déjà livré, 24 pour une VEFA"},
        validators=[Optional(), NumberRange(min=0, max=120)], filters=[zero_entier_si_vide],
        description="Achat sur plan (VEFA) : mois avant livraison. "
                    "Aucun loyer n'est perçu d'ici là.",
    )

    loyer_mensuel = ChampMontant(
        "Loyer mensuel attendu",
        validators=[Optional(), NumberRange(min=0)], filters=[zero_si_vide],
        render_kw={"placeholder": "Ex. : 8 500"},
    )
    charges_copro_annuelles = ChampMontant(
        "Charges de copropriété (annuelles)",
        validators=[Optional(), NumberRange(min=0)], filters=[zero_si_vide],
    )
    assurance_annuelle = ChampMontant(
        "Assurance (annuelle)",
        validators=[Optional(), NumberRange(min=0)], filters=[zero_si_vide],
    )
    frais_gestion_pct = ChampMontant(
        "Frais de gestion (% du loyer)",
        validators=[Optional(), NumberRange(min=0, max=100)], filters=[zero_si_vide],
        render_kw={"placeholder": "Ex. : 5 — laisser vide en gestion directe"},
    )
    vacance_pct = ChampMontant(
        "Vacance locative (% du loyer)",
        validators=[Optional(), NumberRange(min=0, max=100)], filters=[zero_si_vide],
        render_kw={"placeholder": "Ex. : 5 — soit environ trois semaines par an"},
    )
    entretien_annuel = ChampMontant(
        "Entretien (annuel)",
        validators=[Optional(), NumberRange(min=0)], filters=[zero_si_vide],
    )
    taxe_annuelle = ChampMontant(
        "Taxe annuelle (foncière / services communaux)",
        validators=[Optional(), NumberRange(min=0)], filters=[zero_si_vide],
    )
    taux_imposition_override = FloatField(
        "Taux d'imposition effectif (%)",
        validators=[Optional(), NumberRange(min=0, max=100)],
        description="Laisser vide pour utiliser le taux par défaut de la zone.",
    )

    submit = SubmitField("Enregistrer")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.appliquer_statut(self.statut.data)

    def appliquer_statut(self, statut: str | None) -> None:
        """Adapte les questions à l'avancement du dossier.

        Rien n'est effacé au passage — contrairement au brief, où un champ sans
        objet pour le type de bien est vidé. Ici l'étape avance : une superficie
        saisie hier reste vraie demain, elle est seulement demandée plus tard.
        """
        cherche_encore = statut == coherence.STATUT_SANS_BIEN
        self.prix_bien.label.text = "Prix envisagé" if cherche_encore else "Prix du bien"
        self.prix_bien.description = (
            "Hypothèse de travail, à confirmer une fois le bien trouvé."
            if cherche_encore else None
        )
        self.surface_m2.label.text = (
            "Superficie du bien (m²)" if not cherche_encore else "Superficie (m²)"
        )

    def preremplir_avec_le_brief(self, brief) -> None:
        """Reprend du brief ce qui est déjà connu, pour ne pas le redemander.

        Tout reste modifiable : ce sont des valeurs de départ, pas des
        contraintes. Un conseiller qui propose autre chose que ce qui a été
        demandé le fait sciemment — et l'écart lui est signalé.
        """
        if brief is None or self.is_submitted():
            return
        if not self.adresse.data:
            self.adresse.data = brief.zone_recherchee
        if not self.nom.data:
            self.nom.data = f"{brief.type_bien} — {brief.zone_recherchee or ''}".strip(" —")
        # Un client venu chercher un terrain n'attend pas un chiffrage locatif.
        if brief.type_bien == "Terrain":
            self.type_operation.data = "terrain"
        self.surface_m2.render_kw = dict(
            self.surface_m2.render_kw or {},
            placeholder=_attendu(brief.superficie_min, brief.superficie_max, "m² demandés"),
        )
        self.prix_bien.render_kw = dict(
            self.prix_bien.render_kw or {},
            placeholder=_attendu(brief.budget_min, brief.budget_max, "de budget annoncé"),
        )

    def validate(self, extra_validators=None) -> bool:
        """Un dossier locatif sans loyer ne produirait aucun indicateur.

        On ne l'exige que dans ce cas : une opération de type terrain n'a par
        définition pas de loyer, et le champ y vaut légitimement zéro.
        """
        self.appliquer_statut(self.statut.data)
        if not super().validate(extra_validators):
            return False
        if self.type_operation.data == "locatif" and not self.loyer_mensuel.data:
            self.loyer_mensuel.errors.append(
                "Un dossier locatif suppose un loyer. Pour un bien sans loyer, "
                "choisissez le type d'opération « Terrain / revente »."
            )
            return False
        return True


def _attendu(bas, haut, suffixe: str) -> str:
    """Filigrane rappelant la fourchette du brief : « Ex. : 70 à 100 m² demandés »."""
    from ...core.format_fr import montant_texte

    if bas and haut:
        fourchette = f"{montant_texte(bas)} à {montant_texte(haut)}"
    elif haut:
        fourchette = f"jusqu'à {montant_texte(haut)}"
    elif bas:
        fourchette = f"à partir de {montant_texte(bas)}"
    else:
        return ""
    return f"{fourchette} {suffixe}"


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
