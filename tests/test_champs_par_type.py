"""Le brief s'ajuste au type de bien recherché.

Le cabinet remplit ce formulaire devant le client. Une question sans objet —
le standing d'un terrain, l'achat sur plan d'un terrain nu, les chambres d'un
local commercial — se remplit au hasard, et un critère inventé oriente ensuite
une recherche pour rien.

L'écran masque ces champs, mais l'écran ne prouve rien : ces tests passent par
le formulaire soumis, c'est-à-dire par le serveur, seule barrière qui compte.
"""
from app.core import profil_bien
from app.models import Brief, Client
from helpers import DONNEES_CLIENT, inscrire_et_connecter
from test_processus import DONNEES_BRIEF


def preparer_client(http, app):
    inscrire_et_connecter(http)
    http.post("/clients/nouveau", data=DONNEES_CLIENT)
    with app.app_context():
        return Client.query.first().id


DONNEES_APPARTEMENT = {
    "type_bien": "Appartement",
    "standing": "Haut standing",
    "zone_recherchee": "Casablanca — Gauthier",
    "superficie_min": "70", "superficie_max": "100",
    "nb_chambres": "3", "nb_salles_bains": "2", "nb_salons": "1",
    "etage": "2e étage", "orientation": "Sud",
    "commodites": "Transports en commun",
    "type_acquisition": "vefa",
    "budget_min": "1000000", "budget_max": "1500000",
    "mode_financement": "pret", "objectif": "revenu", "horizon_annees": "15",
}


# ── Ce qui n'est pas demandé n'est pas enregistré ────────────────────────────
def test_un_terrain_nenregistre_pas_de_standing(http, app):
    """Même soumis — formulaire forgé, JavaScript désactivé — le standing d'un
    terrain ne doit pas entrer en base : il n'a pas de sens."""
    client_id = preparer_client(http, app)
    http.post(f"/clients/{client_id}/brief",
              data={**DONNEES_BRIEF, "standing": "Haut standing"})

    with app.app_context():
        brief = Brief.query.one()
        assert brief.type_bien == "Terrain"
        assert brief.standing is None
        assert brief.nb_chambres is None


def test_un_terrain_ne_sachete_pas_sur_plan(http, app):
    """La VEFA n'existe pas pour un terrain nu : la valeur soumise est ramenée
    à un mode d'acquisition qui a du sens pour ce bien."""
    client_id = preparer_client(http, app)
    http.post(f"/clients/{client_id}/brief",
              data={**DONNEES_BRIEF, "type_acquisition": "vefa"})

    with app.app_context():
        brief = Brief.query.one()
        assert brief.type_acquisition == "terrain_nu"
        assert brief.type_acquisition_libelle == "Terrain nu"


def test_changer_de_type_efface_les_criteres_sans_objet(http, app):
    """Un brief passé d'appartement à terrain garderait sinon un standing et
    des chambres que plus personne n'a saisis, et que la fiche client
    afficherait comme des critères du client."""
    client_id = preparer_client(http, app)
    http.post(f"/clients/{client_id}/brief", data=DONNEES_APPARTEMENT)
    with app.app_context():
        assert Brief.query.one().standing == "Haut standing"

    http.post(f"/clients/{client_id}/brief", data=DONNEES_BRIEF)
    with app.app_context():
        brief = Brief.query.one()
        assert brief.standing is None and brief.nb_chambres is None
        assert brief.etage is None and brief.orientation is None
        assert brief.viabilisation == "Eau potable, Électricité"
        assert brief.zone_urbanisme == "Zone villa"


def test_un_terrain_enregistre_ce_qui_le_chiffre(http, app):
    client_id = preparer_client(http, app)
    http.post(f"/clients/{client_id}/brief", data=DONNEES_BRIEF)

    with app.app_context():
        brief = Brief.query.one()
        assert brief.topographie == "Plat"
        assert brief.constructibilite == "Constructible"


def test_un_immeuble_se_compte_en_lots(http, app):
    client_id = preparer_client(http, app)
    http.post(f"/clients/{client_id}/brief", data={
        **DONNEES_APPARTEMENT, "type_bien": "Immeuble", "nb_lots": "12",
        "type_acquisition": "vefa",
    })

    with app.app_context():
        brief = Brief.query.one()
        assert brief.nb_lots == 12
        assert brief.nb_chambres is None          # un immeuble n'a pas de chambres
        assert brief.type_acquisition == "existant"  # pas de VEFA sur un immeuble


def test_un_local_commercial_a_un_etat_et_pas_un_standing(http, app):
    client_id = preparer_client(http, app)
    http.post(f"/clients/{client_id}/brief", data={
        **DONNEES_APPARTEMENT, "type_bien": "Local commercial",
        "etat_local": "À rafraîchir", "type_acquisition": "bail",
    })

    with app.app_context():
        brief = Brief.query.one()
        assert brief.etat_local == "À rafraîchir"
        assert brief.standing is None
        assert brief.type_acquisition_libelle == "Bail commercial"


# ── Ce que la page propose ───────────────────────────────────────────────────
def test_la_page_masque_les_champs_sans_objet(http, app):
    """Le champ reste dans la page — le conseiller peut changer de type sans
    recharger — mais il est masqué tant qu'il n'a pas d'objet."""
    client_id = preparer_client(http, app)
    http.post(f"/clients/{client_id}/brief", data=DONNEES_BRIEF)

    page = http.get(f"/clients/{client_id}/brief").get_data(as_text=True)
    assert 'data-champ="standing" hidden' in page
    assert 'data-champ="viabilisation"' in page
    assert 'data-champ="viabilisation" hidden' not in page
    assert '<option value="vefa">' not in page   # la VEFA n'est pas proposée
    assert 'value="terrain_nu">Terrain nu' in page


def test_trois_niveaux_de_standing(http, app):
    """Cinq nuances garantissaient surtout que deux conseillers classent le
    même bien différemment."""
    client_id = preparer_client(http, app)
    page = http.get(f"/clients/{client_id}/brief").get_data(as_text=True)

    assert profil_bien.STANDINGS == ("Économique", "Moyen standing", "Haut standing")
    for disparu in ("Social", "Luxe"):
        assert f'value="{disparu}"' not in page


# ── Cohérence des profils eux-mêmes ──────────────────────────────────────────
def test_chaque_profil_est_complet_et_valide(app):
    """Ajouter un type de bien ne doit pas laisser un champ sans libellé ni un
    mode d'acquisition inconnu du catalogue."""
    from app.blueprints.clients.forms import BriefForm

    with app.test_request_context():
        champs_du_formulaire = set(BriefForm()._fields)
    for type_bien, profil in profil_bien.PROFILS.items():
        assert profil["acquisitions"], type_bien
        for valeur in profil["acquisitions"]:
            assert valeur in profil_bien.ACQUISITIONS, (type_bien, valeur)
        for champ in profil["champs"]:
            assert champ in profil_bien.CHAMPS_OPTIONNELS, (type_bien, champ)
        for champ in profil["libelles"]:
            assert champ in champs_du_formulaire, (type_bien, champ)
        assert profil["commodites"] and profil["note"]


def test_tous_les_types_de_biens_ont_un_profil():
    for type_bien in profil_bien.TYPES_BIEN:
        assert type_bien in profil_bien.PROFILS
