"""Biens / projets d'investissement."""
from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from ...core import coherence
from ...core.acquisition import cout_acquisition, frais_acquisition
from ...core.estimation import REGLES as REGLES_ESTIMATION
from ...core.rendement import rendements
from ...extensions import db
from ...models import Client, LigneTravaux, Projet, ZonePreset
from ..clients import client_du_conseiller
from .forms import LigneTravauxForm, ProjetForm

bp = Blueprint("projets", __name__)


def projet_du_conseiller(projet_id: int) -> Projet:
    projet = db.session.get(Projet, projet_id)
    if projet is None or projet.client.user_id != current_user.id:
        abort(404)
    return projet


def preparer_form(form: ProjetForm) -> list[dict]:
    """Alimente le sélecteur de zone et renvoie les zones pour le JS du formulaire."""
    zones = ZonePreset.query.order_by(ZonePreset.par_defaut.desc(), ZonePreset.nom).all()
    form.zone_id.choices = [(z.id, z.nom) for z in zones]
    return [
        {
            "id": z.id,
            "nom": z.nom,
            "devise": z.devise,
            "taux_frais_total": z.taux_frais_total,
            "taux_imposition_defaut": z.taux_imposition_defaut,
            "personnalisable": z.personnalisable,
        }
        for z in zones
    ]


@bp.route("/")
@login_required
def liste():
    projets = (
        Projet.query.join(Client)
        .filter(Client.user_id == current_user.id)
        .order_by(Projet.created_at.desc())
        .all()
    )
    return render_template("projets/liste.html", projets=projets)


def signaler_les_ecarts(projet: Projet) -> None:
    """Dit ce qui, dans le dossier enregistré, s'éloigne du brief du client.

    Un avertissement, jamais un refus : proposer plus grand ou plus cher est un
    acte de conseil, mais il doit être dit par le conseiller plutôt que
    découvert par le client.
    """
    releves = coherence.ecarts(
        projet.client.brief, projet,
        cout_acquisition(projet.prix_bien, projet.taux_frais_acquisition,
                         projet.budget_travaux),
    )
    for ecart in releves:
        flash(f"Écart avec le brief — {ecart['phrase']}", "warning")


@bp.route("/nouveau/<int:client_id>", methods=["GET", "POST"])
@login_required
def nouveau(client_id: int):
    client = client_du_conseiller(client_id)
    form = ProjetForm()
    zones = preparer_form(form)
    if form.validate_on_submit():
        projet = Projet(client_id=client.id)
        form.populate_obj(projet)
        db.session.add(projet)
        db.session.commit()
        flash(f"Projet « {projet.nom} » créé.", "success")
        signaler_les_ecarts(projet)
        return redirect(url_for("projets.detail", projet_id=projet.id))
    if not form.is_submitted():
        zone_defaut = ZonePreset.query.filter_by(par_defaut=True).first()
        if zone_defaut:
            form.zone_id.data = zone_defaut.id
    # Ce que le brief dit déjà n'est pas redemandé : il sert de point de départ.
    form.preremplir_avec_le_brief(client.brief)
    return render_template(
        "projets/form.html", form=form, client=client, zones=zones,
        regles=REGLES_ESTIMATION, titre=f"Nouveau projet pour {client.nom}",
        brief=client.brief, criteres_brief=coherence.resume(client.brief),
    )


@bp.route("/<int:projet_id>")
@login_required
def detail(projet_id: int):
    projet = projet_du_conseiller(projet_id)
    frais = frais_acquisition(projet.prix_bien, projet.taux_frais_acquisition)
    cout_total = cout_acquisition(
        projet.prix_bien, projet.taux_frais_acquisition, projet.budget_travaux
    )
    # Charges annuelles selon la convention du moteur (vacance + gestion incluses)
    loyer_effectif = 12.0 * projet.loyer_mensuel * (1.0 - projet.vacance_pct / 100.0)
    charges = (
        projet.charges_copro_annuelles + projet.assurance_annuelle
        + projet.entretien_annuel + projet.taxe_annuelle
        + loyer_effectif * projet.frais_gestion_pct / 100.0
        + 12.0 * projet.loyer_mensuel * projet.vacance_pct / 100.0
    )
    rdts = rendements(projet.loyer_mensuel, charges, cout_total, projet.taux_imposition)
    brief = projet.client.brief
    return render_template(
        "projets/detail.html", projet=projet, frais=frais,
        cout_total=cout_total, rdts=rdts, form_travaux=LigneTravauxForm(),
        brief=brief, criteres_brief=coherence.resume(brief),
        ecarts=coherence.ecarts(brief, projet, cout_total),
    )


def _synchroniser_budget_travaux(projet: Projet) -> None:
    """Si des postes détaillés existent, le budget travaux est leur somme."""
    lignes = projet.lignes_travaux.all()
    if lignes:
        projet.budget_travaux = sum(l.montant for l in lignes)


@bp.route("/<int:projet_id>/travaux", methods=["POST"])
@login_required
def ajouter_travaux(projet_id: int):
    projet = projet_du_conseiller(projet_id)
    form = LigneTravauxForm()
    if form.validate_on_submit():
        db.session.add(
            LigneTravaux(
                projet_id=projet.id, libelle=form.libelle.data,
                categorie=form.categorie.data, montant=form.montant.data,
            )
        )
        db.session.flush()
        _synchroniser_budget_travaux(projet)
        db.session.commit()
        flash("Poste de travaux ajouté — budget travaux actualisé.", "success")
    else:
        flash("Poste invalide : libellé et montant sont requis.", "warning")
    return redirect(url_for("projets.detail", projet_id=projet.id))


@bp.route("/travaux/<int:ligne_id>/supprimer", methods=["POST"])
@login_required
def supprimer_travaux(ligne_id: int):
    ligne = db.session.get(LigneTravaux, ligne_id)
    if ligne is None or ligne.projet.client.user_id != current_user.id:
        abort(404)
    projet = ligne.projet
    db.session.delete(ligne)
    db.session.flush()
    # Après suppression, le budget suit la somme restante (0 si plus aucun poste)
    projet.budget_travaux = sum(l.montant for l in projet.lignes_travaux.all())
    db.session.commit()
    flash("Poste de travaux supprimé — budget travaux actualisé.", "info")
    return redirect(url_for("projets.detail", projet_id=projet.id))


@bp.route("/<int:projet_id>/modifier", methods=["GET", "POST"])
@login_required
def modifier(projet_id: int):
    projet = projet_du_conseiller(projet_id)
    form = ProjetForm(obj=projet)
    zones = preparer_form(form)
    if form.validate_on_submit():
        form.populate_obj(projet)
        db.session.commit()
        flash("Projet mis à jour — les indicateurs sont recalculés.", "success")
        signaler_les_ecarts(projet)
        return redirect(url_for("projets.detail", projet_id=projet.id))
    return render_template(
        "projets/form.html", form=form, client=projet.client, zones=zones,
        regles=REGLES_ESTIMATION, titre=f"Modifier « {projet.nom} »",
        brief=projet.client.brief, criteres_brief=coherence.resume(projet.client.brief),
    )


@bp.route("/<int:projet_id>/supprimer", methods=["POST"])
@login_required
def supprimer(projet_id: int):
    projet = projet_du_conseiller(projet_id)
    client_id = projet.client_id
    db.session.delete(projet)
    db.session.commit()
    flash(f"Projet « {projet.nom} » supprimé.", "info")
    return redirect(url_for("clients.detail", client_id=client_id))
