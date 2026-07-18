"""Authentification des consultants (implémentation prévue en semaine 2)."""
from flask import Blueprint, render_template

bp = Blueprint("auth", __name__)


@bp.route("/login")
def login():
    return render_template("placeholder.html", module="Connexion", semaine=2)
