"""Cas réels transmis par le cabinet — référence de validation de la méthode.

Ces deux dossiers sont ceux décrits par le mentor pour illustrer sa règle de
décision : *un investissement est bon lorsqu'il permet au client de générer de
la valeur ; tout dépend de son horizon et du facteur temps.* Ni l'un ni l'autre
ne comporte de loyer — la valeur vient entièrement de la plus-value, ce que
l'outil doit savoir reproduire.

Chaque montant est vérifiable à la main : la zone Maroc applique 7 % de frais
d'acquisition (4 + 1,5 + 1 + 0,5).
"""
import pytest

from app.core.scenario import calculer_scenario

from test_core import faux_projet, faux_scenario


def projet_terrain(**surcharges):
    """Terrain : aucun loyer, aucune charge d'exploitation."""
    defauts = dict(
        type_operation="terrain",
        budget_travaux=0.0,
        loyer_mensuel=0.0,
        charges_copro_annuelles=0.0,
        assurance_annuelle=0.0,
        taxe_annuelle=0.0,
        delai_livraison_mois=0,
    )
    defauts.update(surcharges)
    return faux_projet(**defauts)


def scenario_comptant(**surcharges):
    defauts = dict(mode="cash", apport=0.0, taux_interet=0.0, taux_assurance=0.0)
    defauts.update(surcharges)
    return faux_scenario(**defauts)


# ── Client 1 : portage foncier sur 10 ans ────────────────────────────────────
def test_cas_client_1_portage_foncier():
    """Terrain conservé, revendu par lots après valorisation de la zone.

    Achat 1 000 000 + 7 % de frais = 1 070 000 investis. Revente des parcelles
    à 16 070 000 au bout de 10 ans → bénéfice de 15 000 000, conforme au
    « bénéfice d'environ 15 millions » décrit par le cabinet.
    """
    resultats = calculer_scenario(
        projet_terrain(prix_bien=1_000_000.0),
        scenario_comptant(horizon_annees=10, prix_revente=16_070_000.0),
    )

    assert resultats["acquisition"]["cout_total"] == pytest.approx(1_070_000)
    assert resultats["projection"]["investissement_initial"] == pytest.approx(1_070_000)

    revente = resultats["revente"]
    assert revente["prix_revente_saisi"] is True
    assert revente["valeur_bien_horizon"] == pytest.approx(16_070_000)
    assert revente["plus_value_brute"] == pytest.approx(15_070_000)

    # Valeur créée = bénéfice net du coût d'entrée, sans aucun loyer.
    assert resultats["indicateurs"]["valeur_creee"] == pytest.approx(15_000_000)
    assert resultats["indicateurs"]["cashflow_annuel"] == pytest.approx(0.0)
    assert resultats["rendements"]["brut"] == pytest.approx(0.0)

    # (16 070 000 / 1 070 000)^(1/10) − 1 ≈ 31 % par an
    assert resultats["indicateurs"]["tri"] == pytest.approx(31.1, abs=0.5)


# ── Client 2 : construction-revente ──────────────────────────────────────────
def test_cas_client_2_construction_revente():
    """Terrain viabilisé, immeuble R+4 de 20 appartements, revente sur 2 ans.

    Terrain 1 100 000 + 7 % (77 000) + construction 8 000 000 = 9 177 000.
    Revente de l'ensemble à 14 177 000 → plus-value nette de 5 000 000,
    conforme aux « 5 millions de plus-value nette » décrits par le cabinet.
    """
    resultats = calculer_scenario(
        projet_terrain(prix_bien=1_100_000.0, budget_travaux=8_000_000.0),
        scenario_comptant(horizon_annees=2, prix_revente=14_177_000.0),
    )

    assert resultats["acquisition"]["cout_total"] == pytest.approx(9_177_000)
    assert resultats["indicateurs"]["valeur_creee"] == pytest.approx(5_000_000)


def test_le_facteur_temps_departage_les_deux_clients():
    """Le classement des deux dossiers s'inverse avec l'horizon.

    C'est la conclusion du cabinet : à la sortie du client 2 (2 ans), lui seul a
    créé de la valeur ; sur l'horizon du client 1 (10 ans), le portage foncier
    l'emporte largement. Aucun seuil ne permettrait de trancher a priori.
    """
    client_1 = calculer_scenario(
        projet_terrain(prix_bien=1_000_000.0),
        scenario_comptant(horizon_annees=10, prix_revente=16_070_000.0),
    )
    client_2 = calculer_scenario(
        projet_terrain(prix_bien=1_100_000.0, budget_travaux=8_000_000.0),
        scenario_comptant(horizon_annees=2, prix_revente=14_177_000.0),
    )

    valeur_1 = client_1["indicateurs"]["valeur_creee"]
    valeur_2 = client_2["indicateurs"]["valeur_creee"]

    # À 2 ans, le client 1 n'a encore rien encaissé : il est en attente.
    cumul_client_1_a_2_ans = client_1["projection"]["lignes"][1]["cumul"]
    assert cumul_client_1_a_2_ans < 0 < valeur_2

    # À son horizon, il crée trois fois la valeur de la promotion (15 M / 5 M).
    assert valeur_1 > valeur_2
    assert valeur_1 / valeur_2 == pytest.approx(3.0)


# ── Facteur temps : achat sur plan (VEFA) ────────────────────────────────────
def test_vefa_aucun_loyer_avant_livraison():
    """24 mois de chantier : ni loyer ni charges les deux premières années."""
    resultats = calculer_scenario(
        faux_projet(delai_livraison_mois=24),
        faux_scenario(mode="cash", horizon_annees=10),
    )
    lignes = resultats["projection"]["lignes"]

    assert lignes[0]["loyer"] == 0.0 and lignes[0]["charges"] == 0.0
    assert lignes[1]["loyer"] == 0.0 and lignes[1]["charges"] == 0.0
    assert lignes[2]["loyer"] == pytest.approx(84_000)

    # Le cash-flow mis en avant est celui du régime de croisière, pas celui de
    # l'année 1 qui ne représente rien pour un bien encore en chantier.
    indicateurs = resultats["indicateurs"]
    assert indicateurs["cashflow_annuel_annee1"] == pytest.approx(0.0)
    assert indicateurs["cashflow_annuel"] == pytest.approx(84_000 - 12_000 - 10_800)


def test_vefa_livraison_en_cours_dannee_est_proratisee():
    """Livraison à 6 mois : l'année 1 ne compte qu'un semestre d'exploitation."""
    resultats = calculer_scenario(
        faux_projet(delai_livraison_mois=6),
        faux_scenario(mode="cash", horizon_annees=10),
    )
    lignes = resultats["projection"]["lignes"]

    assert lignes[0]["loyer"] == pytest.approx(42_000)  # 84 000 × 6/12
    assert lignes[0]["charges"] == pytest.approx(6_000)  # 12 000 × 6/12
    assert lignes[1]["loyer"] == pytest.approx(84_000)


def test_prix_de_revente_saisi_prime_sur_la_revalorisation():
    """Un prix négocié remplace la projection par revalorisation annuelle."""
    projet = faux_projet()
    revalorise = calculer_scenario(
        projet, faux_scenario(mode="cash", horizon_annees=10, revalorisation_bien_pct=3.0)
    )
    saisi = calculer_scenario(
        projet,
        faux_scenario(
            mode="cash", horizon_annees=10,
            revalorisation_bien_pct=3.0, prix_revente=2_000_000.0,
        ),
    )

    assert revalorise["revente"]["prix_revente_saisi"] is False
    assert revalorise["revente"]["valeur_bien_horizon"] == pytest.approx(
        1_000_000 * 1.03**10
    )
    assert saisi["revente"]["valeur_bien_horizon"] == pytest.approx(2_000_000)
