"""Dossiers clients — cloisonnés par conseiller connecté."""
from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from ...extensions import db
from ...models import Client
from .forms import ClientForm

bp = Blueprint("clients", __name__)


def client_du_conseiller(client_id: int) -> Client:
    """Renvoie le client s'il appartient au conseiller connecté, sinon 404."""
    client = db.session.get(Client, client_id)
    if client is None or client.user_id != current_user.id:
        abort(404)
    return client


@bp.route("/")
@login_required
def liste():
    clients = current_user.clients.order_by(Client.nom).all()
    return render_template("clients/liste.html", clients=clients)


@bp.route("/nouveau", methods=["GET", "POST"])
@login_required
def nouveau():
    form = ClientForm()
    if form.validate_on_submit():
        client = Client(
            user_id=current_user.id,
            nom=form.nom.data,
            email=form.email.data,
            telephone=form.telephone.data,
            notes=form.notes.data,
        )
        db.session.add(client)
        db.session.commit()
        flash(f"Dossier client « {client.nom} » créé.", "success")
        return redirect(url_for("clients.detail", client_id=client.id))
    return render_template("clients/form.html", form=form, titre="Nouveau dossier client")


@bp.route("/<int:client_id>")
@login_required
def detail(client_id: int):
    client = client_du_conseiller(client_id)
    return render_template("clients/detail.html", client=client)


@bp.route("/<int:client_id>/modifier", methods=["GET", "POST"])
@login_required
def modifier(client_id: int):
    client = client_du_conseiller(client_id)
    form = ClientForm(obj=client)
    if form.validate_on_submit():
        form.populate_obj(client)
        db.session.commit()
        flash("Dossier client mis à jour.", "success")
        return redirect(url_for("clients.detail", client_id=client.id))
    return render_template(
        "clients/form.html", form=form, titre=f"Modifier « {client.nom} »"
    )


@bp.route("/<int:client_id>/supprimer", methods=["POST"])
@login_required
def supprimer(client_id: int):
    client = client_du_conseiller(client_id)
    db.session.delete(client)
    db.session.commit()
    flash(f"Dossier « {client.nom} » supprimé, ainsi que ses projets.", "info")
    return redirect(url_for("clients.liste"))
