from pathlib import Path

from flask import Blueprint, Response, current_app, render_template
from flask_login import current_user

from ...models import Client, Projet

bp = Blueprint("main", __name__)

#: Visuel d'accueil facultatif. Le fichier n'est pas versionné : il peut donc
#: être présent sur le poste d'un conseiller et absent d'un déploiement. Quand
#: il manque, la page retombe sur l'illustration SVG du projet.
VISUEL_ACCUEIL = "img/accueil.webp"


def visuel_accueil() -> str | None:
    chemin = Path(current_app.static_folder) / VISUEL_ACCUEIL
    return VISUEL_ACCUEIL if chemin.is_file() else None


@bp.route("/robots.txt")
def robots():
    """Aucun moteur n'a de raison d'explorer un outil de gestion de dossiers
    clients. La balise `noindex` de chaque page dit la même chose ; ce fichier
    l'annonce avant même le premier chargement."""
    return Response("User-agent: *\nDisallow: /\n", mimetype="text/plain")


@bp.route("/")
def index():
    """Page d'accueil : présentation si visiteur, tableau de bord si connecté."""
    if not current_user.is_authenticated:
        # Page vitrine : elle présente le cabinet à un visiteur, pas l'outil.
        from ...cabinet import ACTIVITE, NOM, QUESTIONS_FREQUENTES, coordonnees

        return render_template(
            "index.html", cabinet_nom=NOM, cabinet_activite=ACTIVITE,
            questions=QUESTIONS_FREQUENTES, coordonnees=coordonnees(),
            visuel_accueil=visuel_accueil(),
        )

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
