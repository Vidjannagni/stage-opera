"""Semaine 5 — cas réels de bout en bout et cas limites.

Le cas France est dimensionné pour être vérifiable à la main : capital emprunté
de 200 000 à 4 % sur 20 ans → mensualité de référence 1 211,96.
"""
import pytest

from app.extensions import db
from app.models import Projet, Scenario, ZonePreset
from helpers import inscrire_et_connecter


def creer_dossier_france(http, app):
    http.post("/clients/nouveau", data={"nom": "Famille Martin"})
    with app.app_context():
        from app.models import Client

        client_id = Client.query.first().id
        zone_france = ZonePreset.query.filter_by(nom="France").first().id
    http.post(
        f"/projets/nouveau/{client_id}",
        data={
            "nom": "T3 Bordeaux", "zone_id": zone_france,
            "prix_bien": "200000", "budget_travaux": "0",
            "loyer_mensuel": "800", "charges_copro_annuelles": "1200",
            "assurance_annuelle": "300", "taxe_annuelle": "1100",
            "frais_gestion_pct": "", "vacance_pct": "", "entretien_annuel": "",
        },
    )
    with app.app_context():
        projet_id = Projet.query.first().id
    return projet_id


def test_cas_reel_france(http, app):
    inscrire_et_connecter(http)
    projet_id = creer_dossier_france(http, app)

    # Zone France : frais 5.8+0.1+1.2+0.4 = 7.5 % → 15 000 ; coût total 215 000
    # Apport 15 000 → capital emprunté exactement 200 000
    http.post(
        f"/scenarios/nouveau/{projet_id}",
        data={
            "nom": "Crédit 4 pour cent", "mode": "credit", "apport": "15000",
            "taux_interet": "4.0", "taux_assurance": "0", "duree_annees": "20",
            "horizon_annees": "20", "revalorisation_loyer_pct": "0",
            "revalorisation_bien_pct": "0", "frais_revente_pct": "0",
            "taux_actualisation": "3",
        },
    )
    with app.app_context():
        scenario_id = Scenario.query.first().id
    r = http.get(f"/scenarios/{scenario_id}/resultats.json").get_json()

    assert r["devise"] == "EUR"
    assert r["acquisition"]["frais"] == pytest.approx(15_000)
    assert r["acquisition"]["cout_total"] == pytest.approx(215_000)
    assert r["financement"]["capital_emprunte"] == pytest.approx(200_000)
    # Valeur de référence externe (simulateurs de crédit)
    assert r["financement"]["mensualite_totale"] == pytest.approx(1211.96, abs=0.01)
    # Imposition France par défaut : 30 %
    assert r["rendements"]["brut"] == pytest.approx(100 * 9600 / 215_000, abs=0.01)
    # Cash-flow annuel : 9600 − 2600 − 30 %×7000 − 12×1211.96 ≈ −9 643.5
    assert r["indicateurs"]["cashflow_annuel"] == pytest.approx(-9643.5, abs=1.0)


def test_changement_de_zone_actualise_les_calculs(http, app):
    """Exigence clé du cadrage : changer la zone recalcule frais, impôt, devise."""
    inscrire_et_connecter(http)
    projet_id = creer_dossier_france(http, app)
    with app.app_context():
        projet = db.session.get(Projet, projet_id)
        avant = projet.taux_frais_acquisition
        zone_maroc = ZonePreset.query.filter_by(nom="Maroc").first()
        projet.zone_id = zone_maroc.id
        db.session.commit()
    page = http.get(f"/projets/{projet_id}").get_data(as_text=True)
    assert "MAD" in page
    with app.app_context():
        projet = db.session.get(Projet, projet_id)
        assert avant == pytest.approx(7.5)
        assert projet.taux_frais_acquisition == pytest.approx(7.0)
        assert projet.taux_imposition == pytest.approx(15.0)


def test_cas_limite_vacance_totale(http, app):
    """Vacance 100 % : aucun loyer perçu, l'outil doit rester cohérent."""
    inscrire_et_connecter(http)
    projet_id = creer_dossier_france(http, app)
    with app.app_context():
        projet = db.session.get(Projet, projet_id)
        projet.vacance_pct = 100.0
        db.session.commit()
    r = http.post(
        f"/scenarios/apercu/{projet_id}",
        json={"mode": "cash", "horizon_annees": "10", "taux_actualisation": "3"},
    ).get_json()
    assert r["exploitation"]["loyer_effectif"] == pytest.approx(0.0)
    assert r["indicateurs"]["cashflow_annuel"] < 0
    assert r["indicateurs"]["van"] < 0  # perte assurée, la VAN doit le montrer


def test_cas_limite_horizon_superieur_a_la_duree(http, app):
    """Horizon 30 ans, prêt 15 ans : les annuités s'arrêtent après le prêt."""
    inscrire_et_connecter(http)
    projet_id = creer_dossier_france(http, app)
    r = http.post(
        f"/scenarios/apercu/{projet_id}",
        json={"mode": "credit", "apport": "15000", "taux_interet": "4",
              "duree_annees": "15", "horizon_annees": "30"},
    ).get_json()
    lignes = r["projection"]["lignes"]
    assert lignes[14]["annuite"] > 0
    assert lignes[15]["annuite"] == 0.0
    assert lignes[14]["crd"] == pytest.approx(0.0, abs=0.01)
    # Après remboursement, le cash-flow annuel remonte
    assert lignes[15]["cashflow"] > lignes[14]["cashflow"]


def test_cas_limite_pret_taux_zero(http, app):
    inscrire_et_connecter(http)
    projet_id = creer_dossier_france(http, app)
    r = http.post(
        f"/scenarios/apercu/{projet_id}",
        json={"mode": "credit", "apport": "15000", "taux_interet": "0",
              "taux_assurance": "0", "duree_annees": "20", "horizon_annees": "20"},
    ).get_json()
    # 200 000 / 240 mois
    assert r["financement"]["mensualite_totale"] == pytest.approx(833.33, abs=0.01)
    assert r["financement"]["cout_interets"] == pytest.approx(0.0, abs=0.01)
