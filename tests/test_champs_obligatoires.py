"""Champs obligatoires et contrôles de cohérence.

Chaque règle testée ici découle du cadrage métier (docs/retour_cabinet.md) :
le cabinet recueille systématiquement certaines informations, et certains
dossiers seraient inexploitables sans elles.
"""
from app.models import Brief, Client, Projet, Scenario, ZonePreset
from helpers import DONNEES_CLIENT, inscrire_et_connecter
from test_processus import DONNEES_BRIEF


def zone_maroc(app):
    with app.app_context():
        return ZonePreset.query.filter_by(nom="Maroc").first().id


# ── Fiche client : les quatre informations du premier entretien ──────────────
def test_client_refuse_sans_les_informations_systematiques(http, app):
    inscrire_et_connecter(http)

    for champ in ("situation_professionnelle", "nationalite", "budget_disponible"):
        donnees = {**DONNEES_CLIENT}
        donnees[champ] = ""
        reponse = http.post("/clients/nouveau", data=donnees)
        assert reponse.status_code == 200, champ
        with app.app_context():
            assert Client.query.count() == 0, f"{champ} vide ne devrait pas passer"

    http.post("/clients/nouveau", data=DONNEES_CLIENT)
    with app.app_context():
        assert Client.query.count() == 1


def test_budget_nul_reste_accepte(http, app):
    """Zéro est une valeur, pas une absence : un client peut n'avoir aucun
    apport disponible et financer entièrement à crédit."""
    inscrire_et_connecter(http)
    http.post("/clients/nouveau", data={**DONNEES_CLIENT, "budget_disponible": "0"})
    with app.app_context():
        assert Client.query.one().budget_disponible == 0


# ── Brief : standing, zone, superficie et budget ─────────────────────────────
def preparer_client(http, app):
    inscrire_et_connecter(http)
    http.post("/clients/nouveau", data=DONNEES_CLIENT)
    with app.app_context():
        return Client.query.first().id


def test_brief_refuse_sans_zone_recherchee(http, app):
    client_id = preparer_client(http, app)
    http.post(f"/clients/{client_id}/brief", data={**DONNEES_BRIEF, "zone_recherchee": ""})
    with app.app_context():
        assert Brief.query.count() == 0


def test_brief_refuse_sans_aucune_borne_de_superficie(http, app):
    client_id = preparer_client(http, app)
    reponse = http.post(
        f"/clients/{client_id}/brief",
        data={**DONNEES_BRIEF, "superficie_min": "", "superficie_max": ""},
    )
    assert "au moins une borne de superficie" in reponse.get_data(as_text=True)
    with app.app_context():
        assert Brief.query.count() == 0


def test_brief_accepte_une_seule_borne(http, app):
    """« Jusqu'à 100 m² » est une réponse courante : le plancher est facultatif."""
    client_id = preparer_client(http, app)
    http.post(
        f"/clients/{client_id}/brief",
        data={**DONNEES_BRIEF, "superficie_min": "", "budget_min": ""},
    )
    with app.app_context():
        brief = Brief.query.one()
        assert brief.superficie_min is None and brief.superficie_max == 30000


# ── Dossier : un locatif suppose un loyer ────────────────────────────────────
def donnees_projet(app, **surcharges):
    donnees = {
        "nom": "Appartement test", "zone_id": zone_maroc(app),
        "type_operation": "locatif", "statut": "recherche",
        "prix_bien": "1000000", "loyer_mensuel": "7000",
    }
    donnees.update(surcharges)
    return donnees


def test_dossier_locatif_refuse_sans_loyer(http, app):
    client_id = preparer_client(http, app)
    reponse = http.post(
        f"/projets/nouveau/{client_id}",
        data=donnees_projet(app, loyer_mensuel=""),
    )
    contenu = reponse.get_data(as_text=True)
    assert "Un dossier locatif suppose un loyer" in contenu
    # Le message oriente vers le bon type d'opération plutôt que de bloquer.
    assert "Terrain / revente" in contenu
    with app.app_context():
        assert Projet.query.count() == 0


def test_dossier_terrain_accepte_sans_loyer(http, app):
    client_id = preparer_client(http, app)
    http.post(
        f"/projets/nouveau/{client_id}",
        data=donnees_projet(app, type_operation="terrain", loyer_mensuel=""),
    )
    with app.app_context():
        assert Projet.query.one().loyer_mensuel == 0


# ── Scénario : une opération sans loyer doit avoir une sortie ────────────────
def preparer_terrain(http, app):
    client_id = preparer_client(http, app)
    http.post(
        f"/projets/nouveau/{client_id}",
        data=donnees_projet(app, nom="Terrain test", type_operation="terrain",
                            loyer_mensuel=""),
    )
    with app.app_context():
        return Projet.query.first().id


DONNEES_SCENARIO = {
    "nom": "Portage", "mode": "cash", "apport": "0", "taux_interet": "0",
    "taux_assurance": "0", "duree_annees": "10", "horizon_annees": "10",
    "revalorisation_loyer_pct": "0", "revalorisation_bien_pct": "0",
    "frais_revente_pct": "0", "taux_actualisation": "3",
}


def test_scenario_terrain_refuse_sans_sortie(http, app):
    projet_id = preparer_terrain(http, app)
    reponse = http.post(
        f"/scenarios/nouveau/{projet_id}",
        data={**DONNEES_SCENARIO, "prix_revente": ""},
    )
    assert "besoin d&#39;un prix de revente" in reponse.get_data(as_text=True)
    with app.app_context():
        assert Scenario.query.count() == 0


def test_scenario_terrain_accepte_avec_revalorisation_seule(http, app):
    projet_id = preparer_terrain(http, app)
    http.post(
        f"/scenarios/nouveau/{projet_id}",
        data={**DONNEES_SCENARIO, "prix_revente": "", "revalorisation_bien_pct": "4"},
    )
    with app.app_context():
        assert Scenario.query.count() == 1


def test_scenario_locatif_reste_libre_de_prix_de_revente(http, app):
    """Un locatif crée déjà de la valeur par ses loyers : la contrainte ne
    s'applique qu'aux opérations sans loyer."""
    client_id = preparer_client(http, app)
    http.post(f"/projets/nouveau/{client_id}", data=donnees_projet(app))
    with app.app_context():
        projet_id = Projet.query.first().id
    http.post(
        f"/scenarios/nouveau/{projet_id}",
        data={**DONNEES_SCENARIO, "prix_revente": ""},
    )
    with app.app_context():
        assert Scenario.query.count() == 1
