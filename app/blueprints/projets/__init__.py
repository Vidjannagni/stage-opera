"""Biens / projets d'investissement (implémentation prévue en semaines 2-3)."""
from flask import Blueprint, render_template

bp = Blueprint("projets", __name__)


@bp.route("/")
def liste():
    return render_template("placeholder.html", module="Projets", semaine=2)
