from flask import Blueprint, render_template
from flask_login import current_user

from ...models import Client, Projet

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Page d'accueil : présentation si visiteur, tableau de bord si connecté."""
    if not current_user.is_authenticated:
        return render_template("index.html")

    clients = current_user.clients.order_by(Client.nom).all()
    projets = (
        Projet.query.join(Client)
        .filter(Client.user_id == current_user.id)
        .order_by(Projet.created_at.desc())
        .all()
    )
    # Répartition des dossiers dans le déroulé recherche → livraison.
    par_statut = [
        (libelle, sum(1 for p in projets if p.statut == code))
        for code, libelle in Projet.STATUTS
    ]
    return render_template(
        "tableau_de_bord.html",
        clients=clients,
        projets=projets,
        derniers=projets[:5],
        par_statut=par_statut,
        sans_brief=[c for c in clients if c.brief is None],
    )
