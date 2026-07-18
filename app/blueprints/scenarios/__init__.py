"""Scénarios de financement : création, résultats, endpoint JSON de calcul."""
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, url_for
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


@bp.route("/<int:scenario_id>/supprimer", methods=["POST"])
@login_required
def supprimer(scenario_id: int):
    scenario = scenario_du_conseiller(scenario_id)
    projet_id = scenario.projet_id
    db.session.delete(scenario)
    db.session.commit()
    flash(f"Scénario « {scenario.nom} » supprimé.", "info")
    return redirect(url_for("projets.detail", projet_id=projet_id))
