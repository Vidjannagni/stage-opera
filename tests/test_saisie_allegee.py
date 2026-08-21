"""Allègement de la saisie : champs vides, estimation des charges.

Le reproche fait à l'outil au retour du cabinet était le nombre de champs à
remplir devant un client. Deux réponses ont été apportées — un formulaire qui
s'ouvre vide plutôt que rempli de zéros, et une estimation des charges
courantes à partir du prix et du loyer. Ces tests vérifient que ni l'une ni
l'autre ne change le sens de ce qui est enregistré.
"""
import re

from app.core.estimation import REGLES, estimer
from app.extensions import db
from app.models import Client, Projet, ZonePreset
from helpers import DONNEES_CLIENT, inscrire_et_connecter


def test_les_charges_estimees_suivent_le_prix_et_le_loyer():
    estimations = estimer(prix_bien=1_200_000, loyer_mensuel=8_500)
    # 8 % de 102 000 = 8 160, arrondi à la centaine
    assert estimations["charges_copro_annuelles"]["valeur"] == 8_200
    # 0,15 % de 1 200 000 = 1 800
    assert estimations["assurance_annuelle"]["valeur"] == 1_800
    # Les pourcentages sont des constantes, pas des montants
    assert estimations["vacance_pct"]["valeur"] == 5.0


def test_toute_estimation_porte_sa_regle():
    """Un chiffre proposé sans justification n'est pas montrable à un client."""
    for champ, estimation in estimer(1_000_000, 5_000).items():
        assert estimation["regle"], champ
        assert estimation["libelle"], champ
        assert REGLES[champ]["base"] in ("loyer_annuel", "prix", "constante")


def test_estimation_sans_donnees_ne_produit_pas_de_montant():
    estimations = estimer(prix_bien=0, loyer_mensuel=0)
    assert estimations["charges_copro_annuelles"]["valeur"] == 0
    assert estimations["assurance_annuelle"]["valeur"] == 0


def test_le_formulaire_de_dossier_s_ouvre_vide(http, app):
    """Aucun « 0.0 » pré-rempli : les exemples en filigrane doivent se voir."""
    inscrire_et_connecter(http)
    http.post("/clients/nouveau", data=DONNEES_CLIENT)
    with app.app_context():
        client_id = Client.query.first().id
    page = http.get(f"/projets/nouveau/{client_id}").get_data(as_text=True)
    for champ in ("charges_copro_annuelles", "taxe_annuelle", "loyer_mensuel",
                  "entretien_annuel", "vacance_pct", "delai_livraison_mois"):
        balise = re.search(r'<input[^>]*id="%s"[^>]*>' % champ, page)
        assert balise and 'value=""' in balise.group(0), champ
    assert 'value="0.0"' not in page
    # Le bouton d'estimation et ses règles sont bien servis au navigateur.
    assert "estimer-charges" in page
    assert "du loyer annuel" in page


def test_un_champ_de_charge_vide_vaut_toujours_zero(http, app):
    """Le confort d'affichage ne change pas ce qui est enregistré."""
    inscrire_et_connecter(http)
    http.post("/clients/nouveau", data=DONNEES_CLIENT)
    with app.app_context():
        client_id = Client.query.first().id
        zone_id = ZonePreset.query.filter_by(nom="Maroc").first().id
    http.post(f"/projets/nouveau/{client_id}", data={
        "nom": "Appartement sans charges saisies", "zone_id": zone_id,
        "prix_bien": "900000", "loyer_mensuel": "6000",
        "budget_travaux": "", "charges_copro_annuelles": "", "taxe_annuelle": "",
        "assurance_annuelle": "", "entretien_annuel": "", "frais_gestion_pct": "",
        "vacance_pct": "", "delai_livraison_mois": "",
    })
    with app.app_context():
        projet = Projet.query.filter_by(nom="Appartement sans charges saisies").first()
        assert projet is not None
        assert projet.budget_travaux == 0.0
        assert projet.charges_copro_annuelles == 0.0
        assert projet.delai_livraison_mois == 0
