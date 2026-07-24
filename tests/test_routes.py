"""Tests d'intégration des routes (semaine 2) : parcours complet et cloisonnement."""
import pytest

from app.extensions import db
from app.models import Projet, Scenario, User
from helpers import creer_parcours_complet, inscrire_et_connecter


def test_acces_anonyme_redirige_vers_login(http):
    reponse = http.get("/clients/")
    assert reponse.status_code == 302
    assert "/auth/login" in reponse.headers["Location"]


def test_inscription_et_connexion(http, app):
    reponse = inscrire_et_connecter(http)
    assert reponse.status_code == 200
    with app.app_context():
        assert User.query.filter_by(email="rene@choubel.com").count() == 1


def test_parcours_complet_maroc(http, app):
    inscrire_et_connecter(http)
    client_id, projet_id, scenario_id = creer_parcours_complet(http, app)

    # Le détail du projet affiche la devise MAD et les rendements
    page = http.get(f"/projets/{projet_id}").get_data(as_text=True)
    assert "MAD" in page and "Rendement brut" in page

    # La page de résultats du scénario répond avec les indicateurs
    page = http.get(f"/scenarios/{scenario_id}/resultats").get_data(as_text=True)
    assert "TRI" in page and "VAN" in page and "Cash-flow" in page

    # L'endpoint JSON renvoie les résultats complets et cohérents
    donnees = http.get(f"/scenarios/{scenario_id}/resultats.json").get_json()
    assert donnees["acquisition"]["cout_total"] == pytest.approx(1_170_000)
    assert donnees["financement"]["capital_emprunte"] == pytest.approx(870_000)
    assert donnees["devise"] == "MAD"
    assert donnees["indicateurs"]["tri"] is not None
    # CRD annuel présent pour le graphique d'amortissement, décroissant
    crds = [l["crd"] for l in donnees["projection"]["lignes"]]
    assert crds[0] < 870_000 and crds == sorted(crds, reverse=True)


def test_projet_herite_des_taux_de_zone(http, app):
    inscrire_et_connecter(http)
    _, projet_id, _ = creer_parcours_complet(http, app)
    with app.app_context():
        projet = db.session.get(Projet, projet_id)
        assert projet.taux_frais_override is None
        assert projet.taux_frais_acquisition == pytest.approx(7.0)  # zone Maroc
        assert projet.taux_imposition == pytest.approx(15.0)


def test_comparaison_de_scenarios(http, app):
    inscrire_et_connecter(http)
    _, projet_id, scenario_id = creer_parcours_complet(http, app)
    http.post(
        f"/scenarios/nouveau/{projet_id}",
        data={
            "nom": "Achat cash", "mode": "cash", "apport": "0",
            "taux_interet": "0", "taux_assurance": "0", "duree_annees": "20",
            "horizon_annees": "20", "revalorisation_loyer_pct": "1",
            "revalorisation_bien_pct": "1.5", "frais_revente_pct": "0",
            "taux_actualisation": "3",
        },
    )
    with app.app_context():
        ids = [s.id for s in Scenario.query.all()]
    page = http.get(f"/scenarios/comparer?ids={ids[0]}&ids={ids[1]}")
    assert page.status_code == 200
    texte = page.get_data(as_text=True)
    assert "Crédit 20 ans" in texte and "Achat cash" in texte and "TRI" in texte


def test_comparaison_exige_deux_scenarios(http, app):
    inscrire_et_connecter(http)
    _, _, scenario_id = creer_parcours_complet(http, app)
    reponse = http.get(f"/scenarios/comparer?ids={scenario_id}")
    assert reponse.status_code == 302  # redirection avec message d'avertissement


def test_apercu_calcul_a_la_volee(http, app):
    inscrire_et_connecter(http)
    _, projet_id, _ = creer_parcours_complet(http, app)
    donnees = http.post(
        f"/scenarios/apercu/{projet_id}",
        json={
            "mode": "credit", "apport": "300000", "taux_interet": "4.5",
            "taux_assurance": "0.3", "duree_annees": "20", "horizon_annees": "20",
            "revalorisation_loyer_pct": "1", "revalorisation_bien_pct": "1.5",
            "frais_revente_pct": "0", "taux_actualisation": "3",
        },
    ).get_json()
    assert donnees["financement"]["capital_emprunte"] == pytest.approx(870_000)
    assert donnees["indicateurs"]["tri"] is not None
    # Aucun scénario persisté par l'aperçu
    with app.app_context():
        assert Scenario.query.filter_by(nom="apercu").count() == 0


def test_apercu_donnees_invalides(http, app):
    inscrire_et_connecter(http)
    _, projet_id, _ = creer_parcours_complet(http, app)
    donnees = http.post(
        f"/scenarios/apercu/{projet_id}",
        json={"mode": "n'importe quoi", "duree_annees": "abc"},
    ).get_json()
    # Retombe sur les valeurs par défaut sans erreur serveur
    assert donnees["financement"]["mode"] == "credit"


def test_cloisonnement_entre_conseillers(http, app):
    inscrire_et_connecter(http)
    client_id, projet_id, scenario_id = creer_parcours_complet(http, app)
    http.post("/auth/logout")

    inscrire_et_connecter(http, email="autre@choubel.com", nom="Autre")
    assert http.get(f"/clients/{client_id}").status_code == 404
    assert http.get(f"/projets/{projet_id}").status_code == 404
    assert http.get(f"/scenarios/{scenario_id}/resultats").status_code == 404
    assert http.get(f"/scenarios/{scenario_id}/resultats.json").status_code == 404
