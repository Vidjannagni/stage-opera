"""Dossiers clients — cloisonnés par conseiller connecté."""
from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from ...core import profil_bien
from ...extensions import db
from ...models import Brief, Client
from .forms import BriefForm, ClientForm

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
        client = Client(user_id=current_user.id)
        form.populate_obj(client)
        db.session.add(client)
        db.session.commit()
        flash(
            f"Dossier « {client.nom} » créé — renseignez maintenant son brief "
            "de recherche.", "success",
        )
        return redirect(url_for("clients.brief", client_id=client.id))
    return render_template("clients/form.html", form=form, titre="Nouveau dossier client")


@bp.route("/<int:client_id>")
@login_required
def detail(client_id: int):
    client = client_du_conseiller(client_id)
    return render_template("clients/detail.html", client=client)


@bp.route("/<int:client_id>/brief", methods=["GET", "POST"])
@login_required
def brief(client_id: int):
    """Cahier de recherche : les critères recueillis au premier entretien."""
    client = client_du_conseiller(client_id)
    brief = client.brief
    form = BriefForm(obj=brief)
    if form.validate_on_submit():
        if brief is None:
            brief = Brief(client_id=client.id)
            db.session.add(brief)
        form.populate_obj(brief)
        db.session.commit()
        flash("Brief de recherche enregistré.", "success")
        return redirect(url_for("clients.detail", client_id=client.id))
    # Les tables de `profil_bien` servent deux fois : au formulaire, pour ne
    # valider que les champs qui s'appliquent, et à la page, pour masquer les
    # autres sans rechargement quand le type de bien change.
    return render_template(
        "clients/brief.html", form=form, client=client, brief=brief,
        PROFILS=profil_bien.PROFILS,
        CHAMPS_OPTIONNELS=profil_bien.CHAMPS_OPTIONNELS,
        ACQUISITIONS=profil_bien.ACQUISITIONS,
        RESEAUX=profil_bien.RESEAUX,
        ZONES_URBANISME=profil_bien.ZONES_URBANISME,
    )


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
