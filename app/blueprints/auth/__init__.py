"""Authentification des consultants."""
import os

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ...extensions import db
from ...models import User
from .forms import LoginForm, MotDePasseForm, RegisterForm

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            destination = request.args.get("next")
            if destination and destination.startswith("/"):
                return redirect(destination)
            return redirect(url_for("clients.liste"))
        flash("Identifiants incorrects.", "danger")
    return render_template("auth/login.html", form=form)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegisterForm()
    # En ligne, l'inscription peut être réservée aux porteurs d'un code.
    code_attendu = os.environ.get("CODE_INSCRIPTION")
    if form.validate_on_submit():
        email = form.email.data.lower()
        if code_attendu and form.code_inscription.data != code_attendu:
            flash("Code d'inscription invalide — demandez-le au cabinet.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("Un compte existe déjà avec cette adresse.", "warning")
        else:
            user = User(email=email, nom=form.nom.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Compte créé, bienvenue !", "success")
            return redirect(url_for("clients.liste"))
    return render_template(
        "auth/register.html", form=form, code_requis=bool(code_attendu)
    )


@bp.route("/mon-compte", methods=["GET", "POST"])
@login_required
def mon_compte():
    """Le conseiller change son mot de passe lui-même.

    Sans cet écran, un mot de passe provisoire attribué en console resterait
    le mot de passe définitif du conseiller, connu de l'administrateur.
    """
    form = MotDePasseForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.actuel.data):
            flash("Mot de passe actuel incorrect.", "danger")
        else:
            current_user.set_password(form.nouveau.data)
            db.session.commit()
            flash("Mot de passe changé.", "success")
            return redirect(url_for("main.index"))
    return render_template("auth/mon_compte.html", form=form)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("main.index"))
