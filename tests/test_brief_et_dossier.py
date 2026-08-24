"""Le brief et le dossier : deux objets, et le lien entre eux.

Le **brief** dit ce que le client cherche — un type de bien, des fourchettes,
un objectif, un horizon. Il y en a un par client.

Le **dossier** chiffre *un bien précis* qu'on lui propose — un prix, des
travaux, un loyer. Il y en a autant que de biens étudiés.

Rien n'obligeait la seconde à répondre à la première : on pouvait chiffrer un
45 m² à deux millions pour un client venu chercher 70 m² à un million et demi,
sans que rien ne le signale. Ces tests vérifient que l'écart est dit — et
qu'il n'est jamais bloquant, proposer autre chose restant un acte de conseil.
"""
from app.core import coherence
from app.models import Client, Projet, ZonePreset
from helpers import DONNEES_CLIENT, inscrire_et_connecter
from test_processus import DONNEES_BRIEF

BRIEF_APPARTEMENT = {
    "type_bien": "Appartement", "standing": "Moyen standing",
    "zone_recherchee": "Casablanca — Gauthier",
    "superficie_min": "70", "superficie_max": "100",
    "budget_min": "1000000", "budget_max": "1500000",
    "type_acquisition": "existant", "mode_financement": "pret",
    "objectif": "revenu", "horizon_annees": "20",
    "commodites": "Transports en commun",
}


def preparer(http, app, brief=BRIEF_APPARTEMENT):
    """Conseiller connecté, client avec brief ; renvoie (client_id, zone_id)."""
    inscrire_et_connecter(http)
    http.post("/clients/nouveau", data=DONNEES_CLIENT)
    with app.app_context():
        client_id = Client.query.first().id
        zone_id = ZonePreset.query.filter_by(nom="Maroc").first().id
    if brief:
        http.post(f"/clients/{client_id}/brief", data=brief)
    return client_id, zone_id


def donnees_projet(zone_id, **surcharges):
    donnees = {
        "nom": "Appartement Gauthier", "zone_id": zone_id, "statut": "visites",
        "type_operation": "locatif", "surface_m2": "85", "prix_bien": "1200000",
        "budget_travaux": "0", "loyer_mensuel": "8500",
        "charges_copro_annuelles": "", "assurance_annuelle": "", "taxe_annuelle": "",
        "frais_gestion_pct": "", "vacance_pct": "", "entretien_annuel": "",
        "delai_livraison_mois": "0",
    }
    donnees.update(surcharges)
    return donnees


# ── Les écarts sont dits ─────────────────────────────────────────────────────
def test_un_bien_conforme_au_brief_ne_signale_rien(http, app):
    client_id, zone_id = preparer(http, app)
    http.post(f"/projets/nouveau/{client_id}", data=donnees_projet(zone_id))

    with app.app_context():
        projet = Projet.query.one()
        assert coherence.ecarts(projet.client.brief, projet) == []


def test_un_bien_trop_petit_et_trop_cher_est_signale(http, app):
    client_id, zone_id = preparer(http, app)
    reponse = http.post(
        f"/projets/nouveau/{client_id}",
        data=donnees_projet(zone_id, surface_m2="45", prix_bien="2000000"),
        follow_redirects=True,
    )
    page = reponse.get_data(as_text=True)

    assert "sous les 70 m² demandés" in page
    assert "au-dessus du budget maximal annoncé" in page
    with app.app_context():
        assert Projet.query.count() == 1, "l'écart avertit, il ne bloque pas"


def test_le_budget_se_compare_au_cout_dentree_pas_au_seul_prix(http, app):
    """1 450 000 tient dans le budget ; avec 7 % de frais, non. C'est ce que le
    client sort de sa poche qui compte."""
    client_id, zone_id = preparer(http, app)
    http.post(f"/projets/nouveau/{client_id}",
              data=donnees_projet(zone_id, prix_bien="1450000"))

    with app.app_context():
        projet = Projet.query.one()
        assert coherence.ecarts(projet.client.brief, projet) == []
        sur_le_cout = coherence.ecarts(projet.client.brief, projet, cout_total=1_551_500)
        assert len(sur_le_cout) == 1
        assert sur_le_cout[0]["champ"] == "prix_bien"


def test_un_dossier_sans_loyer_pour_qui_attend_un_revenu(http, app):
    """Le rapprochement se fait sur l'objectif, pas sur le type de bien."""
    client_id, zone_id = preparer(http, app)
    http.post(f"/projets/nouveau/{client_id}",
              data=donnees_projet(zone_id, type_operation="terrain", loyer_mensuel="0"))

    with app.app_context():
        projet = Projet.query.one()
        phrases = [e["phrase"] for e in coherence.ecarts(projet.client.brief, projet)]
        assert any("attend un revenu locatif" in p for p in phrases)


def test_une_revente_pour_qui_vise_la_plus_value_ne_signale_rien(http, app):
    """Un appartement acheté pour être revendu se chiffre sans loyer : c'est
    cohérent, et l'outil ne doit pas crier au loup."""
    client_id, zone_id = preparer(
        http, app, brief={**BRIEF_APPARTEMENT, "objectif": "plus_value"})
    http.post(f"/projets/nouveau/{client_id}",
              data=donnees_projet(zone_id, type_operation="terrain", loyer_mensuel="0"))

    with app.app_context():
        projet = Projet.query.one()
        assert coherence.ecarts(projet.client.brief, projet) == []


def test_sans_brief_aucun_ecart_et_la_page_le_dit(http, app):
    """Faute de brief, rien ne dit ce que le client cherche : l'outil ne peut
    pas inventer l'écart, mais il doit dire qu'il ne sait pas."""
    client_id, zone_id = preparer(http, app, brief=None)
    http.post(f"/projets/nouveau/{client_id}", data=donnees_projet(zone_id))

    with app.app_context():
        projet_id = Projet.query.one().id
    page = http.get(f"/projets/{projet_id}").get_data(as_text=True)
    assert "n'a pas de brief de recherche" in page


# ── Le dossier en recherche ──────────────────────────────────────────────────
def test_en_recherche_le_bien_nest_pas_encore_decrit(http, app):
    """Aucun bien n'est arrêté : son adresse et sa superficie ne se demandent
    pas, et le prix saisi n'est qu'une hypothèse."""
    client_id, _ = preparer(http, app)
    page = http.get(f"/projets/nouveau/{client_id}").get_data(as_text=True)

    assert 'data-champ="surface_m2" hidden' in page
    assert 'data-champ="adresse" hidden' in page
    assert "Prix envisagé" in page
    assert "aucun bien n&#39;est encore" in page or "aucun bien n'est encore" in page


def test_des_la_presentation_le_bien_se_decrit(http, app):
    client_id, zone_id = preparer(http, app)
    http.post(f"/projets/nouveau/{client_id}", data=donnees_projet(zone_id))
    with app.app_context():
        projet_id = Projet.query.one().id

    page = http.get(f"/projets/{projet_id}/modifier").get_data(as_text=True)
    assert 'data-champ="surface_m2" hidden' not in page
    assert "Prix du bien" in page


def test_le_brief_prerenseigne_le_dossier(http, app):
    """Ce que le client a déjà dit n'est pas redemandé."""
    client_id, _ = preparer(http, app)
    page = http.get(f"/projets/nouveau/{client_id}").get_data(as_text=True)

    assert 'value="Appartement — Casablanca — Gauthier"' in page
    assert "70 à 100 m² demandés" in page          # filigrane de la superficie
    assert "1 000 000 à 1 500 000 de budget annoncé" in page


def test_un_client_venu_pour_un_terrain_ouvre_un_dossier_terrain(http, app):
    client_id, _ = preparer(http, app, brief=DONNEES_BRIEF)
    page = http.get(f"/projets/nouveau/{client_id}").get_data(as_text=True)

    assert '<option selected value="terrain">' in page


# ── Le rappel du brief ───────────────────────────────────────────────────────
def test_le_dossier_rappelle_ce_que_le_client_cherche(http, app):
    client_id, zone_id = preparer(http, app)
    http.post(f"/projets/nouveau/{client_id}", data=donnees_projet(zone_id))
    with app.app_context():
        projet_id = Projet.query.one().id

    page = http.get(f"/projets/{projet_id}").get_data(as_text=True)
    assert "Ce que le client cherche" in page
    assert "70 à 100 m²" in page
    assert "Revenu locatif régulier, sur 20 ans" in page


# ── Le mode de financement annoncé ───────────────────────────────────────────
def test_letude_rappelle_le_mode_de_financement_annonce(http, app):
    """Le client disait vouloir payer comptant, et c'est un crédit qui ressort.

    L'étude ne cache pas les montages à crédit — les écarter sans les avoir
    chiffrés reviendrait à décider à sa place — mais elle dit que la réponse
    n'est pas celle qu'il avait en tête.
    """
    client_id, zone_id = preparer(
        http, app, brief={**BRIEF_APPARTEMENT, "mode_financement": "comptant"})
    http.post(f"/projets/nouveau/{client_id}", data=donnees_projet(zone_id))
    with app.app_context():
        projet_id = Projet.query.one().id

    page = http.get(f"/etudes/{projet_id}?budget=400000").get_data(as_text=True)
    assert "annoncé vouloir payer comptant" in page
