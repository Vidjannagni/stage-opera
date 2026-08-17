"""Scénarios de financement : création, résultats, comparaison, calcul JSON."""
from flask import (
    Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for,
)
from flask_login import current_user, login_required

from ...core.scenario import calculer_scenario
from ...extensions import db
from ...models import Scenario
from ..projets import projet_du_conseiller
from .forms import ScenarioForm

bp = Blueprint("scenarios", __name__)


def scenario_du_conseiller(scenario_id: int) -> Scenario:
    scenario = db.session.get(Scenario, scenario_id)
    if scenario is None or scenario.projet.client.user_id != current_user.id:
        abort(404)
    return scenario


@bp.route("/")
@login_required
def liste():
    return redirect(url_for("projets.liste"))


@bp.route("/nouveau/<int:projet_id>", methods=["GET", "POST"])
@login_required
def nouveau(projet_id: int):
    projet = projet_du_conseiller(projet_id)
    form = ScenarioForm()
    form.projet = projet
    if form.validate_on_submit():
        scenario = Scenario(projet_id=projet.id)
        form.populate_obj(scenario)
        db.session.add(scenario)
        db.session.commit()
        flash(f"Scénario « {scenario.nom} » créé.", "success")
        return redirect(url_for("scenarios.resultats", scenario_id=scenario.id))
    return render_template(
        "scenarios/form.html", form=form, projet=projet,
        titre=f"Nouveau scénario — {projet.nom}",
    )


@bp.route("/<int:scenario_id>/modifier", methods=["GET", "POST"])
@login_required
def modifier(scenario_id: int):
    scenario = scenario_du_conseiller(scenario_id)
    form = ScenarioForm(obj=scenario)
    form.projet = scenario.projet
    if form.validate_on_submit():
        form.populate_obj(scenario)
        db.session.commit()
        flash("Scénario mis à jour — indicateurs recalculés.", "success")
        return redirect(url_for("scenarios.resultats", scenario_id=scenario.id))
    return render_template(
        "scenarios/form.html", form=form, projet=scenario.projet,
        titre=f"Modifier « {scenario.nom} »",
    )


@bp.route("/<int:scenario_id>/resultats")
@login_required
def resultats(scenario_id: int):
    scenario = scenario_du_conseiller(scenario_id)
    calculs = calculer_scenario(scenario.projet, scenario)
    return render_template(
        "scenarios/resultats.html", scenario=scenario, projet=scenario.projet, r=calculs
    )


@bp.route("/<int:scenario_id>/resultats.json")
@login_required
def resultats_json(scenario_id: int):
    """Résultats complets en JSON — utilisé par l'interface dynamique (semaine 3)."""
    scenario = scenario_du_conseiller(scenario_id)
    return jsonify(calculer_scenario(scenario.projet, scenario))


@bp.route("/comparer")
@login_required
def comparer():
    """Comparaison de 2 à 4 scénarios d'un même projet, côte à côte."""
    ids = request.args.getlist("ids", type=int)
    if not 2 <= len(ids) <= 4:
        flash("Sélectionnez entre 2 et 4 scénarios à comparer.", "warning")
        return redirect(request.referrer or url_for("projets.liste"))
    scenarios = [scenario_du_conseiller(i) for i in ids]
    projet = scenarios[0].projet
    if any(s.projet_id != projet.id for s in scenarios):
        flash("Les scénarios comparés doivent porter sur le même projet.", "warning")
        return redirect(url_for("projets.detail", projet_id=projet.id))
    comparaison = [
        {"scenario": s, "r": calculer_scenario(projet, s)} for s in scenarios
    ]
    comparaison_json = [
        {"nom": c["scenario"].nom, "cumul": [l["cumul"] for l in c["r"]["projection"]["lignes"]]}
        for c in comparaison
    ]
    return render_template(
        "scenarios/comparaison.html", projet=projet,
        comparaison=comparaison, comparaison_json=comparaison_json,
    )


def _nombre(donnees: dict, cle: str, defaut: float = 0.0) -> float:
    try:
        return float(donnees.get(cle) or defaut)
    except (TypeError, ValueError):
        return defaut


@bp.route("/apercu/<int:projet_id>", methods=["POST"])
@login_required
def apercu(projet_id: int):
    """Calcul à la volée pour le formulaire de scénario, sans persistance."""
    projet = projet_du_conseiller(projet_id)
    donnees = request.get_json(silent=True) or {}
    brouillon = Scenario(
        projet_id=projet.id,
        nom="apercu",
        mode=donnees.get("mode") if donnees.get("mode") in Scenario.MODES else "credit",
        apport=_nombre(donnees, "apport"),
        taux_interet=_nombre(donnees, "taux_interet"),
        taux_assurance=_nombre(donnees, "taux_assurance"),
        duree_annees=max(1, int(_nombre(donnees, "duree_annees", 20))),
        horizon_annees=max(1, int(_nombre(donnees, "horizon_annees", 20))),
        revalorisation_loyer_pct=_nombre(donnees, "revalorisation_loyer_pct"),
        revalorisation_bien_pct=_nombre(donnees, "revalorisation_bien_pct"),
        frais_revente_pct=_nombre(donnees, "frais_revente_pct"),
        taux_actualisation=_nombre(donnees, "taux_actualisation", 3.0),
        # Vide = la valeur à l'horizon suit la revalorisation annuelle.
        prix_revente=_nombre(donnees, "prix_revente") or None,
    )
    return jsonify(calculer_scenario(projet, brouillon))


CHAMPS_DUPLIQUES = (
    "mode", "apport", "taux_interet", "taux_assurance", "duree_annees",
    "horizon_annees", "revalorisation_loyer_pct", "revalorisation_bien_pct",
    "frais_revente_pct", "taux_actualisation", "prix_revente",
)


@bp.route("/<int:scenario_id>/dupliquer", methods=["POST"])
@login_required
def dupliquer(scenario_id: int):
    """Copie un scénario pour tester une variante sans perdre l'original."""
    original = scenario_du_conseiller(scenario_id)
    copie = Scenario(
        projet_id=original.projet_id,
        nom=f"{original.nom} (variante)",
        **{champ: getattr(original, champ) for champ in CHAMPS_DUPLIQUES},
    )
    db.session.add(copie)
    db.session.commit()
    flash(f"Scénario dupliqué : « {copie.nom} » — modifiez la variante.", "success")
    return redirect(url_for("scenarios.modifier", scenario_id=copie.id))


@bp.route("/<int:scenario_id>/supprimer", methods=["POST"])
@login_required
def supprimer(scenario_id: int):
    scenario = scenario_du_conseiller(scenario_id)
    projet_id = scenario.projet_id
    db.session.delete(scenario)
    db.session.commit()
    flash(f"Scénario « {scenario.nom} » supprimé.", "info")
    return redirect(url_for("projets.detail", projet_id=projet_id))
