"""Scénarios de financement et comparaison (implémentation prévue en semaines 2-3)."""
from flask import Blueprint, render_template

bp = Blueprint("scenarios", __name__)


@bp.route("/")
def liste():
    return render_template("placeholder.html", module="Scénarios", semaine=3)
