"""Exports client : rapport PDF (WeasyPrint) et classeur Excel (openpyxl)."""
from datetime import date
from io import BytesIO
from pathlib import Path

from flask import Blueprint, current_app, render_template, send_file
from flask_login import login_required
from werkzeug.utils import secure_filename

from ...core.financement import tableau_amortissement
from ...core.scenario import calculer_scenario
from ..scenarios import scenario_du_conseiller
from .excel import construire_classeur

bp = Blueprint("exports", __name__)


@bp.route("/scenario/<int:scenario_id>/pdf")
@login_required
def scenario_pdf(scenario_id: int):
    from weasyprint import HTML  # import différé : dépendances système lourdes

    scenario = scenario_du_conseiller(scenario_id)
    projet = scenario.projet
    html = render_template(
        "exports/rapport_pdf.html",
        projet=projet, scenario=scenario,
        r=calculer_scenario(projet, scenario),
        date_generation=date.today().strftime("%d/%m/%Y"),
    )
    racine = Path(current_app.root_path).parent
    pdf = HTML(string=html, base_url=str(racine)).write_pdf()
    nom = secure_filename(f"RentImmo_{projet.nom}_{scenario.nom}") or "rapport"
    return send_file(
        BytesIO(pdf), mimetype="application/pdf",
        as_attachment=True, download_name=f"{nom}.pdf",
    )


@bp.route("/scenario/<int:scenario_id>/excel")
@login_required
def scenario_excel(scenario_id: int):
    scenario = scenario_du_conseiller(scenario_id)
    projet = scenario.projet
    calculs = calculer_scenario(projet, scenario)
    amortissement = (
        tableau_amortissement(
            calculs["financement"]["capital_emprunte"],
            scenario.taux_interet, scenario.duree_annees,
        )
        if scenario.mode == "credit" else []
    )
    flux = construire_classeur(projet, scenario, calculs, amortissement)
    nom = secure_filename(f"RentImmo_{projet.nom}_{scenario.nom}") or "export"
    return send_file(
        flux,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True, download_name=f"{nom}.xlsx",
    )
