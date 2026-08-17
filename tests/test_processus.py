"""Alignement sur le processus du cabinet : profil client, brief, déroulé du
dossier, opérations sans loyer et achat sur plan.

Ces tests couvrent aussi le rendu des écrans concernés.
"""
from app.extensions import db
from app.models import Brief, Client, Projet, Scenario, ZonePreset
from helpers import inscrire_et_connecter


def zone_maroc(app):
    with app.app_context():
        return ZonePreset.query.filter_by(nom="Maroc").first().id


def creer_client(http, **surcharges):
    donnees = {
        "nom": "M. Alaoui",
        "situation_professionnelle": "Chef d'entreprise",
        "nationalite": "Marocaine",
        "budget_disponible": "1200000",
    }
    donnees.update(surcharges)
    return http.post("/clients/nouveau", data=donnees, follow_redirects=True)


DONNEES_BRIEF = {
    "type_bien": "Terrain",
    "standing": "Moyen standing",
    "zone_recherchee": "Périphérie de Casablanca",
    "superficie_min": "20000",
    "superficie_max": "30000",
    "commodites": "Axe routier, école à proximité",
    "type_acquisition": "existant",
    "budget_min": "900000",
    "budget_max": "1100000",
    "mode_financement": "comptant",
    "objectif": "plus_value",
    "horizon_annees": "10",
}


# ── Profil client ────────────────────────────────────────────────────────────
def test_fiche_client_enregistre_le_profil_recueilli(http, app):
    inscrire_et_connecter(http)
    creer_client(http)

    with app.app_context():
        client = Client.query.first()
        assert client.situation_professionnelle == "Chef d'entreprise"
        assert client.nationalite == "Marocaine"
        assert client.budget_disponible == 1_200_000


def test_creation_client_oriente_vers_le_brief(http, app):
    inscrire_et_connecter(http)
    reponse = creer_client(http)
    assert "Brief de recherche" in reponse.get_data(as_text=True)


# ── Brief de recherche ───────────────────────────────────────────────────────
def test_brief_enregistre_puis_modifie(http, app):
    inscrire_et_connecter(http)
    creer_client(http)
    with app.app_context():
        client_id = Client.query.first().id

    http.post(f"/clients/{client_id}/brief", data=DONNEES_BRIEF, follow_redirects=True)
    with app.app_context():
        brief = Brief.query.filter_by(client_id=client_id).one()
        assert brief.type_bien == "Terrain"
        assert brief.objectif == "plus_value"
        assert brief.horizon_annees == 10

    # Une seconde soumission met à jour le brief existant, sans le dupliquer.
    http.post(
        f"/clients/{client_id}/brief",
        data={**DONNEES_BRIEF, "horizon_annees": "15"}, follow_redirects=True,
    )
    with app.app_context():
        assert Brief.query.filter_by(client_id=client_id).count() == 1
        assert Brief.query.filter_by(client_id=client_id).one().horizon_annees == 15


def test_brief_refuse_un_budget_incoherent(http, app):
    inscrire_et_connecter(http)
    creer_client(http)
    with app.app_context():
        client_id = Client.query.first().id

    reponse = http.post(
        f"/clients/{client_id}/brief",
        data={**DONNEES_BRIEF, "budget_min": "2000000", "budget_max": "1000000"},
    )
    assert "supérieur au minimum" in reponse.get_data(as_text=True)
    with app.app_context():
        assert Brief.query.count() == 0


def test_objectif_du_client_rappele_sur_la_fiche(http, app):
    inscrire_et_connecter(http)
    creer_client(http)
    with app.app_context():
        client_id = Client.query.first().id
    http.post(f"/clients/{client_id}/brief", data=DONNEES_BRIEF)

    page = http.get(f"/clients/{client_id}").get_data(as_text=True)
    assert "Plus-value à la revente" in page
    assert "10 ans" in page


# ── Tableau de bord ──────────────────────────────────────────────────────────
def test_tableau_de_bord_liste_les_briefs_manquants(http, app):
    inscrire_et_connecter(http)
    creer_client(http)

    page = http.get("/").get_data(as_text=True)
    assert "Tableau de bord" in page
    assert "Briefs à compléter" in page
    assert "M. Alaoui" in page


# ── Opération sans loyer (cas du cabinet) ────────────────────────────────────
def creer_terrain(http, app):
    creer_client(http)
    with app.app_context():
        client_id = Client.query.first().id
    http.post(
        f"/projets/nouveau/{client_id}",
        data={
            "nom": "Terrain 3 ha — périphérie", "zone_id": zone_maroc(app),
            "type_operation": "terrain", "statut": "compromis",
            "prix_bien": "1000000", "budget_travaux": "", "loyer_mensuel": "",
            "delai_livraison_mois": "",
        },
    )
    with app.app_context():
        return Projet.query.first().id


def test_operation_terrain_sans_loyer(http, app):
    inscrire_et_connecter(http)
    projet_id = creer_terrain(http, app)

    with app.app_context():
        projet = db.session.get(Projet, projet_id)
        assert projet.type_operation == "terrain"
        assert projet.loyer_mensuel == 0.0
        assert projet.statut == "compromis"

    page = http.get(f"/projets/{projet_id}").get_data(as_text=True)
    assert "sans loyer" in page
    # Les rendements locatifs n'ont pas de sens ici : ils ne sont pas affichés.
    assert "Rendement net-net" not in page


def test_resultats_terrain_mettent_la_plus_value_en_avant(http, app):
    inscrire_et_connecter(http)
    projet_id = creer_terrain(http, app)
    http.post(
        f"/scenarios/nouveau/{projet_id}",
        data={
            "nom": "Portage 10 ans", "mode": "cash", "apport": "0",
            "taux_interet": "0", "taux_assurance": "0", "duree_annees": "10",
            "horizon_annees": "10", "revalorisation_loyer_pct": "0",
            "revalorisation_bien_pct": "0", "frais_revente_pct": "0",
            "taux_actualisation": "3", "prix_revente": "16070000",
        },
    )
    with app.app_context():
        scenario_id = Scenario.query.first().id
        assert db.session.get(Scenario, scenario_id).prix_revente == 16_070_000

    page = http.get(f"/scenarios/{scenario_id}/resultats").get_data(as_text=True)
    assert "Valeur créée" in page
    assert "Plus-value à la revente" in page

    resultats = http.get(f"/scenarios/{scenario_id}/resultats.json").get_json()
    assert resultats["indicateurs"]["valeur_creee"] == 15_000_000
    assert resultats["revente"]["prix_revente_saisi"] is True


# ── Achat sur plan ───────────────────────────────────────────────────────────
def test_achat_sur_plan_signale_et_differe_le_loyer(http, app):
    inscrire_et_connecter(http)
    creer_client(http)
    with app.app_context():
        client_id = Client.query.first().id
    http.post(
        f"/projets/nouveau/{client_id}",
        data={
            "nom": "Appartement VEFA", "zone_id": zone_maroc(app),
            "type_operation": "locatif", "statut": "notaire",
            "prix_bien": "1000000", "loyer_mensuel": "7000",
            "delai_livraison_mois": "24",
        },
    )
    with app.app_context():
        projet_id = Projet.query.first().id
    http.post(
        f"/scenarios/nouveau/{projet_id}",
        data={
            "nom": "Cash", "mode": "cash", "apport": "0", "taux_interet": "0",
            "taux_assurance": "0", "duree_annees": "10", "horizon_annees": "10",
            "revalorisation_loyer_pct": "0", "revalorisation_bien_pct": "0",
            "frais_revente_pct": "0", "taux_actualisation": "3",
        },
    )
    with app.app_context():
        scenario_id = Scenario.query.first().id

    page = http.get(f"/scenarios/{scenario_id}/resultats").get_data(as_text=True)
    assert "Achat sur plan" in page
    assert "en chantier" in page

    lignes = http.get(f"/scenarios/{scenario_id}/resultats.json").get_json()["projection"]["lignes"]
    assert lignes[0]["loyer"] == 0.0
    assert lignes[2]["loyer"] == 84_000.0
