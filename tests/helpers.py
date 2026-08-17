"""Helpers de parcours pour les tests d'intégration."""
from app.models import Client, Projet, Scenario, ZonePreset


def inscrire_et_connecter(http, email="rene@choubel.com", nom="René"):
    return http.post(
        "/auth/register",
        data={"nom": nom, "email": email, "password": "motdepasse", "confirm": "motdepasse"},
        follow_redirects=True,
    )


#: Fiche client minimale acceptée : le cabinet recueille systématiquement ces
#: quatre informations, le formulaire les exige donc.
DONNEES_CLIENT = {
    "nom": "Investisseur Test",
    "situation_professionnelle": "Salarié(e) du privé",
    "nationalite": "Marocaine",
    "budget_disponible": "1000000",
}


def creer_parcours_complet(http, app):
    """Client → projet (zone Maroc) → scénario crédit ; renvoie les ids."""
    http.post("/clients/nouveau", data=DONNEES_CLIENT)
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
