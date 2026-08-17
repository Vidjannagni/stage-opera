"""Page vitrine — la seule page visible sans compte.

Elle présente le cabinet à un visiteur. Son contenu provient intégralement du
cadrage métier (docs/retour_cabinet.md) : ces tests vérifient qu'il y figure
et, pour les coordonnées, qu'aucune valeur fictive n'est publiée.
"""
from helpers import DONNEES_CLIENT, inscrire_et_connecter


def test_vitrine_presente_le_cabinet(http):
    page = http.get("/").get_data(as_text=True)

    assert "Choubel Consulting" in page
    assert "logo-choubel.jpg" in page          # le logo du cabinet
    assert "Terrains" in page and "Immeubles" in page   # les biens traités
    assert page.count("<li><strong>") == 6     # les six étapes du métier
    assert "facteur temps" in page             # la règle de décision, citée


def test_vitrine_naffiche_aucune_coordonnee_inventee(http, monkeypatch):
    """Tant que le cabinet n'a rien fourni, la page invite à compléter plutôt
    que d'afficher un numéro fictif."""
    page = http.get("/").get_data(as_text=True)
    assert "Coordonnées à renseigner" in page


def test_vitrine_affiche_les_coordonnees_fournies(http, monkeypatch):
    monkeypatch.setattr("app.cabinet.TELEPHONE", "+212 5 22 00 00 00")
    monkeypatch.setattr("app.cabinet.EMAIL", "contact@choubel.example")

    page = http.get("/").get_data(as_text=True)
    assert "+212 5 22 00 00 00" in page
    assert "contact@choubel.example" in page
    assert "Coordonnées à renseigner" not in page


def test_conseiller_connecte_voit_le_tableau_de_bord(http, app):
    """La vitrine s'efface une fois connecté : la racine devient l'outil."""
    inscrire_et_connecter(http)
    http.post("/clients/nouveau", data=DONNEES_CLIENT)

    page = http.get("/").get_data(as_text=True)
    assert "Tableau de bord" in page
    assert "Questions fréquentes" not in page
