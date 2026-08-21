"""Étude automatique : l'outil construit les montages, les confronte, propose.

Le conseiller ne remplit plus de formulaire de scénario pour obtenir une
réponse. Il ouvre le dossier, lance l'étude, et lit une proposition motivée.
Les montages restent visibles un par un, avec leur composition complète, et
peuvent être enregistrés en scénarios pour rejoindre les écrans existants
(résultats, comparaison, exports PDF et Excel).
"""
from dataclasses import dataclass

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ...core import hypotheses as hyp
from ...core.arbitrage import etudier
from ...extensions import db
from ...models import Brief, Scenario
from ..projets import projet_du_conseiller

bp = Blueprint("etudes", __name__)

OBJECTIFS = dict(Brief.OBJECTIFS)


@dataclass
class Cadrage:
    """Objectif et horizon effectivement retenus pour l'étude.

    Le brief du client les fournit ; le conseiller peut les surcharger le temps
    d'une simulation, sans modifier la fiche — un « et si le client visait
    plutôt la revente à 10 ans ? » ne doit pas réécrire son dossier.
    """

    objectif: str
    horizon_annees: int
    #: Vrai si l'une des deux valeurs ne vient pas du brief enregistré.
    surcharge: bool = False

    @property
    def objectif_libelle(self) -> str:
        return OBJECTIFS.get(self.objectif, self.objectif)


def cadrage_demande(projet, args) -> Cadrage:
    brief = projet.client.brief
    objectif_brief = brief.objectif if brief else "revenu"
    horizon_brief = (brief.horizon_annees if brief else None) or hyp.horizon_defaut(
        projet.est_locatif
    )

    objectif = args.get("objectif")
    if objectif not in OBJECTIFS:
        objectif = objectif_brief
    horizon = args.get("horizon", type=int)
    if horizon is None or not 1 <= horizon <= 50:
        horizon = horizon_brief
    return Cadrage(
        objectif=objectif, horizon_annees=horizon,
        surcharge=(objectif != objectif_brief or horizon != horizon_brief),
    )


def budget_demande(projet, args) -> float | None:
    """Budget retenu : celui saisi pour l'étude, sinon celui de la fiche client.

    ``None`` (aucun des deux) = budget inconnu : aucun montage n'est écarté et
    l'étude le dit, plutôt que de filtrer sur une valeur inventée.
    """
    budget = args.get("budget", type=float)
    if budget is not None and budget >= 0:
        return budget
    return projet.client.budget_disponible


def _prix_revente(args) -> float | None:
    prix = args.get("prix_revente", type=float)
    return prix if prix and prix > 0 else None


@bp.route("/<int:projet_id>")
@login_required
def etude(projet_id: int):
    projet = projet_du_conseiller(projet_id)
    cadrage = cadrage_demande(projet, request.args)
    budget = budget_demande(projet, request.args)
    prix_revente = _prix_revente(request.args)

    resultat = etudier(projet, cadrage, budget, prix_revente)
    return render_template(
        "etudes/resultat.html", projet=projet, cadrage=cadrage, budget=budget,
        prix_revente=prix_revente, e=resultat, objectifs=Brief.OBJECTIFS,
        hypotheses=hyp,
    )


@bp.route("/<int:projet_id>/retenir", methods=["POST"])
@login_required
def retenir(projet_id: int):
    """Enregistre en scénarios les montages cochés dans l'étude.

    L'étude est rejouée à l'identique côté serveur — elle est déterministe —
    plutôt que de faire transiter les montages par le formulaire : le
    navigateur ne peut donc pas enregistrer un montage qui n'a jamais été
    proposé.
    """
    projet = projet_du_conseiller(projet_id)
    cadrage = cadrage_demande(projet, request.form)
    budget = budget_demande(projet, request.form)
    resultat = etudier(projet, cadrage, budget, _prix_revente(request.form))

    rangs = request.form.getlist("rangs", type=int)
    par_rang = {etude["rang"]: etude for etude in resultat["classement"]}
    choisis = [par_rang[rang] for rang in rangs if rang in par_rang]
    if not choisis and resultat["meilleur"]:
        choisis = [resultat["meilleur"]]
    if not choisis:
        flash("Aucun montage à enregistrer.", "warning")
        return redirect(url_for("etudes.etude", projet_id=projet.id))

    existants = {s.nom for s in projet.scenarios.all()}
    crees = []
    for etude in choisis:
        champs = etude["candidat"].champs_scenario()
        champs["nom"] = _nom_libre(champs["nom"], existants)
        existants.add(champs["nom"])
        scenario = Scenario(projet_id=projet.id, **champs)
        db.session.add(scenario)
        crees.append(scenario)
    db.session.commit()

    if len(crees) == 1:
        flash(
            f"Montage « {crees[0].nom} » enregistré — il est désormais "
            "modifiable comme n'importe quel scénario.", "success",
        )
        return redirect(url_for("scenarios.resultats", scenario_id=crees[0].id))
    flash(f"{len(crees)} montages enregistrés.", "success")
    return redirect(url_for("scenarios.comparer", ids=[s.id for s in crees[:4]]))


def _nom_libre(nom: str, pris: set[str]) -> str:
    """Deux études successives ne doivent pas produire deux scénarios homonymes."""
    if nom not in pris:
        return nom
    indice = 2
    while f"{nom} ({indice})" in pris:
        indice += 1
    return f"{nom} ({indice})"
