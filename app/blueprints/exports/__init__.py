"""Exports client : rapport PDF (WeasyPrint) et classeur Excel (openpyxl)."""
from datetime import date
from io import BytesIO
from pathlib import Path

from flask import (
    Blueprint, current_app, flash, redirect, render_template, send_file, url_for,
)
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
    """Document remis au client.

    WeasyPrint s'appuie sur des bibliothèques système (Pango, Cairo) que les
    hébergements gratuits ne fournissent pas toujours. L'import est différé
    pour que leur absence n'empêche pas l'application de démarrer, et rattrapé
    ici pour qu'elle ne se solde pas par une page d'erreur muette : le
    conseiller doit savoir que c'est cet hébergement qui ne sait pas produire
    de PDF, et que l'export Excel, lui, fonctionne.
    """
    try:
        from weasyprint import HTML
    except (ImportError, OSError) as manque:
        current_app.logger.warning("Export PDF indisponible : %s", manque)
        flash(
            "L'export PDF n'est pas disponible sur cet hébergement : il demande "
            "des bibliothèques système absentes du serveur. L'export Excel "
            "contient les mêmes chiffres.", "warning",
        )
        return redirect(url_for("scenarios.resultats", scenario_id=scenario_id))

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
