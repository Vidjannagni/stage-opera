from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from ..projets.forms import ChampMontant, zero_si_vide


class ScenarioForm(FlaskForm):
    nom = StringField(
        "Nom du scénario", validators=[DataRequired(), Length(max=120)],
        render_kw={"list": "liste-scenarios", "placeholder": "Ex. : Crédit 20 ans"},
    )
    mode = SelectField(
        "Mode de financement",
        choices=[("credit", "Crédit"), ("cash", "Cash (sans emprunt)")],
        validators=[DataRequired()],
    )

    apport = ChampMontant(
        "Apport",
        validators=[Optional(), NumberRange(min=0)], filters=[zero_si_vide],
        render_kw={"placeholder": "Ex. : 300 000"},
    )
    taux_interet = FloatField(
        "Taux d'intérêt annuel (%)", default=4.5,
        validators=[Optional(), NumberRange(min=0, max=30)], filters=[zero_si_vide],
    )
    taux_assurance = FloatField(
        "Taux d'assurance annuel (%)", default=0.3,
        validators=[Optional(), NumberRange(min=0, max=5)], filters=[zero_si_vide],
    )
    duree_annees = IntegerField(
        "Durée du prêt (années)", default=20,
        validators=[DataRequired(), NumberRange(min=1, max=35)],
    )

    horizon_annees = IntegerField(
        "Horizon de projection (années)", default=20,
        validators=[DataRequired(), NumberRange(min=1, max=50)],
    )
    revalorisation_loyer_pct = FloatField(
        "Revalorisation annuelle du loyer (%)", default=1.0,
        validators=[Optional(), NumberRange(min=-10, max=20)], filters=[zero_si_vide],
    )
    revalorisation_bien_pct = FloatField(
        "Revalorisation annuelle du bien (%)", default=1.5,
        validators=[Optional(), NumberRange(min=-10, max=20)], filters=[zero_si_vide],
    )
    prix_revente = ChampMontant(
        "Prix de revente à l'horizon",
        validators=[Optional(), NumberRange(min=0)],
        render_kw={"placeholder": "Ex. : 16 070 000 — laisser vide si inconnu"},
        description="Prix connu ou négocié (construction-revente, lotissement). "
                    "Laisser vide pour appliquer la revalorisation annuelle.",
    )
    frais_revente_pct = FloatField(
        "Frais de revente (% de la valeur)", default=0.0,
        validators=[Optional(), NumberRange(min=0, max=20)], filters=[zero_si_vide],
    )
    taux_actualisation = FloatField(
        "Taux d'actualisation pour la VAN (%)", default=3.0,
        validators=[Optional(), NumberRange(min=0, max=20)], filters=[zero_si_vide],
    )

    submit = SubmitField("Enregistrer")

    #: Renseigné par la vue : le contrôle ci-dessous dépend du type d'opération.
    projet = None

    def validate(self, extra_validators=None) -> bool:
        """Une opération sans loyer doit pouvoir créer de la valeur.

        Sans prix de revente ni revalorisation du bien, un terrain resterait à
        sa valeur d'achat : le scénario n'aurait rien à montrer.
        """
        if not super().validate(extra_validators):
            return False
        if (
            self.projet is not None
            and not self.projet.est_locatif
            and not self.prix_revente.data
            and not self.revalorisation_bien_pct.data
        ):
            self.prix_revente.errors.append(
                "Une opération sans loyer a besoin d'un prix de revente, ou "
                "d'une revalorisation annuelle du bien, pour créer de la valeur."
            )
            return False
        return True
