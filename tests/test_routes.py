"""Tests d'intégration des routes (semaine 2) : parcours complet et cloisonnement."""
import json
from pathlib import Path

import pytest

from app import create_app
from app.extensions import db
from app.models import Client, Projet, Scenario, User, ZonePreset


@pytest.fixture()
def app():
    app = create_app("test")
    with app.app_context():
        db.create_all()
        zones = json.loads(
            (Path(app.root_path).parent / "data" / "zones.json").read_text("utf-8")
        )
        db.session.add_all([ZonePreset(**z) for z in zones])
        db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture()
def http(app):
    return app.test_client()


def inscrire_et_connecter(http, email="rene@choubel.com", nom="René"):
    return http.post(
        "/auth/register",
        data={"nom": nom, "email": email, "password": "motdepasse", "confirm": "motdepasse"},
        follow_redirects=True,
    )


def creer_parcours_complet(http, app):
    """Client → projet (zone Maroc) → scénario crédit ; renvoie les ids."""
    http.post("/clients/nouveau", data={"nom": "Investisseur Test"})
    with app.app_context():
        client_id = Client.query.first().id
        zone_maroc = ZonePreset.query.filter_by(nom="Maroc").first().id
    http.post(
        f"/projets/nouveau/{client_id}",
        data={
            "nom": "Appartement Casablanca", "zone_id": zone_maroc,
            "prix_bien": "1000000", "budget_travaux": "100000",
            "loyer_mensuel": "7000", "charges_copro_annuelles": "6000",
            "assurance_annuelle": "2000", "taxe_annuelle": "4000",
            "frais_gestion_pct": "", "vacance_pct": "", "entretien_annuel": "",
        },
    )
    with app.app_context():
        projet_id = Projet.query.first().id
    http.post(
        f"/scenarios/nouveau/{projet_id}",
        data={
            "nom": "Crédit 20 ans", "mode": "credit", "apport": "300000",
            "taux_interet": "4.5", "taux_assurance": "0.3", "duree_annees": "20",
            "horizon_annees": "20", "revalorisation_loyer_pct": "1",
            "revalorisation_bien_pct": "1.5", "frais_revente_pct": "0",
            "taux_actualisation": "3",
        },
    )
    with app.app_context():
        scenario_id = Scenario.query.first().id
    return client_id, projet_id, scenario_id


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


def test_projet_herite_des_taux_de_zone(http, app):
    inscrire_et_connecter(http)
    _, projet_id, _ = creer_parcours_complet(http, app)
    with app.app_context():
        projet = db.session.get(Projet, projet_id)
        assert projet.taux_frais_override is None
        assert projet.taux_frais_acquisition == pytest.approx(7.0)  # zone Maroc
        assert projet.taux_imposition == pytest.approx(15.0)


def test_cloisonnement_entre_conseillers(http, app):
    inscrire_et_connecter(http)
    client_id, projet_id, scenario_id = creer_parcours_complet(http, app)
    http.post("/auth/logout")

    inscrire_et_connecter(http, email="autre@choubel.com", nom="Autre")
    assert http.get(f"/clients/{client_id}").status_code == 404
    assert http.get(f"/projets/{projet_id}").status_code == 404
    assert http.get(f"/scenarios/{scenario_id}/resultats").status_code == 404
    assert http.get(f"/scenarios/{scenario_id}/resultats.json").status_code == 404
