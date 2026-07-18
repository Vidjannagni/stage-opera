"""Exports PDF / Excel (implémentation prévue en semaine 4)."""
from flask import Blueprint, render_template

bp = Blueprint("exports", __name__)


@bp.route("/")
def index():
    return render_template("placeholder.html", module="Exports PDF / Excel", semaine=4)
