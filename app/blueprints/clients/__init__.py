"""Dossiers clients (implémentation prévue en semaine 2)."""
from flask import Blueprint, render_template

bp = Blueprint("clients", __name__)


@bp.route("/")
def liste():
    return render_template("placeholder.html", module="Dossiers clients", semaine=2)
