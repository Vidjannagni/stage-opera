"""Étude automatique : génération des montages, classement, mise en mots.

Ce que ces tests protègent, dans l'ordre d'importance métier :

1. la **règle de financement** qui fixe l'apport minimal (frais + travaux) ;
2. le fait que l'**objectif du client change la réponse** — c'est la traduction
   informatique de la position du cabinet : il n'y a pas de bon montage dans
   l'absolu ;
3. le fait qu'aucun montage **hors budget** ne soit proposé, ni écarté en
   silence ;
4. la **traçabilité** : tout paramètre affiché indique d'où il vient.
"""
import pytest

from app.core.arbitrage import etudier, poids_effectifs
from app.core.generation import apport_minimal, generer
from app.extensions import db
from app.models import Brief, Client, Projet, Scenario, User, ZonePreset
from helpers import inscrire_et_connecter, creer_parcours_complet


# ─── Montage d'un dossier de référence, en mémoire ──────────────────────────

def dossier(app, **surcharges):
    """Appartement de Casablanca : 1,2 M, 150 k de travaux, 8 500 de loyer."""
    with app.app_context():
        numero = User.query.count() + 1
        utilisateur = User(email=f"etude{numero}@choubel.com", nom="Conseiller")
        utilisateur.set_password("motdepasse")
        db.session.add(utilisateur)
        db.session.flush()
        client = Client(
            user_id=utilisateur.id, nom="M. Alaoui",
            budget_disponible=surcharges.pop("budget", 1_500_000),
        )
        db.session.add(client)
        db.session.flush()
        db.session.add(Brief(
            client_id=client.id,
            objectif=surcharges.pop("objectif", "revenu"),
            horizon_annees=surcharges.pop("horizon", 20),
        ))
        zone = ZonePreset.query.filter_by(nom="Maroc").first()
        champs = dict(
            client_id=client.id, zone_id=zone.id, nom="Appartement Gauthier",
            prix_bien=1_200_000, budget_travaux=150_000, loyer_mensuel=8_500,
            charges_copro_annuelles=7_200, taxe_annuelle=4_500,
            frais_gestion_pct=5.0, vacance_pct=5.0,
        )
        champs.update(surcharges)
        projet = Projet(**champs)
        db.session.add(projet)
        db.session.commit()
        return projet.id


def etude_du_dossier(app, projet_id, **surcharges):
    with app.app_context():
        projet = db.session.get(Projet, projet_id)
        return etudier(
            projet, projet.client.brief,
            surcharges.get("budget", projet.client.budget_disponible),
            surcharges.get("prix_revente"),
        )


# ─── Génération ─────────────────────────────────────────────────────────────

def test_apport_minimal_couvre_frais_et_travaux(app):
    """La banque prête sur le bien : le reste est à la charge de l'acquéreur."""
    projet_id = dossier(app)
    with app.app_context():
        projet = db.session.get(Projet, projet_id)
        # 7 % de frais sur 1 200 000 = 84 000, plus 150 000 de travaux
        assert apport_minimal(projet) == pytest.approx(234_000)


def test_les_montages_partagent_le_bien_et_l_horizon_du_client(app):
    projet_id = dossier(app, horizon=12)
    with app.app_context():
        projet = db.session.get(Projet, projet_id)
        candidats = generer(projet, projet.client.brief, projet.client.budget_disponible)
        assert len(candidats) >= 4
        assert {c.horizon_annees for c in candidats} == {12}
        assert {c.signature for c in candidats} .__len__() == len(candidats)
        assert any(c.mode == "cash" for c in candidats)
        assert any(c.mode == "credit" for c in candidats)


def test_chaque_parametre_affiche_son_origine(app):
    """Un montage doit pouvoir être défendu ligne à ligne devant un client."""
    projet_id = dossier(app)
    with app.app_context():
        projet = db.session.get(Projet, projet_id)
        for candidat in generer(projet, projet.client.brief, 1_500_000):
            assert candidat.constitution
            for ligne in candidat.constitution:
                assert ligne["libelle"] and ligne["valeur"] and ligne["origine"]
            libelles = [l["libelle"] for l in candidat.constitution]
            assert "Prix du bien" in libelles
            assert "Coût d'entrée total" in libelles


def test_un_montage_hors_budget_est_ecarte_avec_son_motif(app):
    projet_id = dossier(app, budget=250_000)
    resultat = etude_du_dossier(app, projet_id)
    assert resultat["ecartes"], "l'achat comptant dépasse le budget déclaré"
    for ecarte in resultat["ecartes"]:
        assert "il manque" in ecarte["ecarte"]
    assert all(not e["ecarte"] for e in resultat["classement"])


def test_budget_inconnu_n_ecarte_rien(app):
    """Sans budget déclaré, l'outil ne filtre pas sur une valeur inventée."""
    projet_id = dossier(app)
    with app.app_context():
        projet = db.session.get(Projet, projet_id)
        resultat = etudier(projet, projet.client.brief, None)
    assert resultat["ecartes"] == []


# ─── Classement ─────────────────────────────────────────────────────────────

def test_les_poids_somment_a_un_et_ignorent_le_loyer_sans_loyer():
    for objectif in ("revenu", "plus_value", "patrimoine"):
        poids = poids_effectifs(objectif, est_locatif=True)
        assert sum(poids.values()) == pytest.approx(1.0)
        sans_loyer = poids_effectifs(objectif, est_locatif=False)
        assert sum(sans_loyer.values()) == pytest.approx(1.0)
        assert "rendement_net" not in sans_loyer


def test_l_objectif_du_client_change_le_montage_proposé(app):
    """Le cœur du sujet : même bien, même budget, réponse différente.

    Budget calibré pour ne retenir que les crédits à apport minimal : les trois
    montages ne diffèrent alors que par la durée. Un client qui cherche du
    revenu veut la mensualité la plus légère (25 ans) ; un client qui vise la
    plus-value veut payer le moins d'intérêts (15 ans).
    """
    revenu = etude_du_dossier(app, dossier(app, budget=250_000, objectif="revenu"))
    assert revenu["meilleur"]["candidat"].duree_annees == 25

    plus_value = etude_du_dossier(
        app, dossier(app, budget=250_000, objectif="plus_value")
    )
    assert plus_value["meilleur"]["candidat"].duree_annees == 15


def test_le_classement_est_deterministe(app):
    projet_id = dossier(app)
    premier = etude_du_dossier(app, projet_id)
    second = etude_du_dossier(app, projet_id)
    assert [e["candidat"].nom for e in premier["classement"]] == \
           [e["candidat"].nom for e in second["classement"]]


def test_aucun_montage_tenable_est_dit_explicitement(app):
    projet_id = dossier(app, budget=1_000)
    resultat = etude_du_dossier(app, projet_id)
    assert resultat["aucun_tenable"] is True
    # La page reste exploitable : les montages sont classés pour information.
    assert resultat["meilleur"] is not None


def test_operation_sans_loyer_classee_sur_la_plus_value(app):
    projet_id = dossier(
        app, type_operation="terrain", loyer_mensuel=0, budget_travaux=0,
        charges_copro_annuelles=0, taxe_annuelle=0, frais_gestion_pct=0,
        vacance_pct=0, prix_bien=1_000_000, objectif="plus_value", horizon=10,
        budget=1_000_000,
    )
    resultat = etude_du_dossier(app, projet_id, prix_revente=16_070_000)
    assert "rendement_net" not in resultat["poids"]
    meilleur = resultat["meilleur"]
    # 1 000 000 + 7 % de frais investis, revente à 16 070 000 : la valeur créée
    # reste du même ordre que le cas de référence du cabinet.
    assert meilleur["criteres"]["valeur_creee"] > 14_000_000


# ─── Mise en mots ───────────────────────────────────────────────────────────

def test_l_explication_est_chiffree_et_nuancée(app):
    resultat = etude_du_dossier(app, dossier(app))
    explication = resultat["explication"]
    assert resultat["meilleur"]["candidat"].nom in explication["titre"]
    assert "MAD" in explication["resume"]
    assert explication["arguments"], "une proposition sans argument n'en est pas une"
    # L'achat comptant l'emporte sur le cash-flow mais perd sur le TRI : la
    # page doit le dire, sans quoi elle serait un argumentaire de vente.
    assert explication["nuances"]
    assert any("levier" in n for n in explication["nuances"])


def test_les_points_de_vigilance_signalent_l_hypothese_de_sortie(app):
    resultat = etude_du_dossier(app, dossier(app))
    assert any("prix de sortie" in p for p in resultat["explication"]["vigilance"])


# ─── Parcours web ───────────────────────────────────────────────────────────

def test_page_d_etude_et_enregistrement(http, app):
    inscrire_et_connecter(http)
    client_id, projet_id, _ = creer_parcours_complet(http, app)
    with app.app_context():
        db.session.add(Brief(client_id=client_id, objectif="revenu", horizon_annees=20))
        db.session.commit()

    page = http.get(f"/etudes/{projet_id}").get_data(as_text=True)
    assert "Montage proposé" in page
    assert "Tous les montages étudiés" in page
    assert "Composition détaillée" in page

    with app.app_context():
        avant = Scenario.query.count()
    reponse = http.post(
        f"/etudes/{projet_id}/retenir",
        data={"rangs": ["1", "2"], "objectif": "revenu", "horizon": "20"},
        follow_redirects=True,
    )
    assert reponse.status_code == 200
    with app.app_context():
        assert Scenario.query.count() == avant + 2


def test_deux_etudes_ne_creent_pas_deux_scenarios_homonymes(http, app):
    inscrire_et_connecter(http)
    _, projet_id, _ = creer_parcours_complet(http, app)
    for _ in range(2):
        http.post(f"/etudes/{projet_id}/retenir", data={"rangs": ["1"]})
    with app.app_context():
        noms = [s.nom for s in Scenario.query.all()]
    assert len(noms) == len(set(noms))


def test_etude_cloisonnee_par_conseiller(http, app):
    inscrire_et_connecter(http)
    _, projet_id, _ = creer_parcours_complet(http, app)
    http.post("/auth/logout")
    inscrire_et_connecter(http, email="autre@choubel.com", nom="Autre")
    assert http.get(f"/etudes/{projet_id}").status_code == 404
    assert http.post(f"/etudes/{projet_id}/retenir", data={}).status_code == 404
