"""Tests unitaires du moteur de calcul (semaine 2).

Les valeurs de référence proviennent de calculs indépendants (formule
d'annuité vérifiée sur simulateurs de crédit usuels, VAN/TRI à la main).
"""
import pytest

from app.core.acquisition import cout_acquisition, frais_acquisition
from app.core.financement import (
    capital_restant_du,
    cout_credit,
    mensualite,
    mensualite_assurance,
    tableau_amortissement,
)
from app.core.indicateurs import tri, van
from app.core.rendement import rendements
from app.core.scenario import calculer_scenario


# ── Acquisition ──────────────────────────────────────────────────────────────
def test_frais_acquisition_zone_maroc():
    # Zone Maroc : 4 + 1.5 + 1 + 0.5 = 7 % du prix
    assert frais_acquisition(1_000_000, 7.0) == pytest.approx(70_000)


def test_cout_acquisition_complet():
    assert cout_acquisition(1_000_000, 7.0, 150_000) == pytest.approx(1_220_000)


def test_acquisition_rejette_valeurs_negatives():
    with pytest.raises(ValueError):
        frais_acquisition(-1, 7.0)
    with pytest.raises(ValueError):
        cout_acquisition(100, 7.0, travaux=-5)


# ── Financement ──────────────────────────────────────────────────────────────
def test_mensualite_reference_externe():
    # 200 000 à 4 % sur 20 ans → 1 211,96 (simulateurs de référence)
    assert mensualite(200_000, 4.0, 20) == pytest.approx(1211.96, abs=0.01)


def test_mensualite_taux_zero():
    assert mensualite(120_000, 0.0, 10) == pytest.approx(1000.0)


def test_mensualite_capital_nul():
    assert mensualite(0, 4.0, 20) == 0.0


def test_mensualite_assurance_sur_capital_initial():
    # 200 000 à 0,36 % → 60 / mois
    assert mensualite_assurance(200_000, 0.36) == pytest.approx(60.0)


def test_amortissement_coherent():
    capital = 200_000
    lignes = tableau_amortissement(capital, 4.0, 20)
    assert len(lignes) == 240
    # Le premier mois d'intérêts vaut C * t
    assert lignes[0]["interet"] == pytest.approx(capital * 0.04 / 12)
    # La somme du capital remboursé vaut le capital emprunté, CRD final nul
    assert sum(l["capital_rembourse"] for l in lignes) == pytest.approx(capital)
    assert lignes[-1]["crd"] == pytest.approx(0.0)


def test_capital_restant_du():
    assert capital_restant_du(200_000, 4.0, 20, 0) == 200_000
    assert capital_restant_du(200_000, 4.0, 20, 20) == 0.0
    crd_10_ans = capital_restant_du(200_000, 4.0, 20, 10)
    assert 0 < crd_10_ans < 200_000
    # Cohérence avec le tableau d'amortissement
    assert crd_10_ans == pytest.approx(
        tableau_amortissement(200_000, 4.0, 20)[119]["crd"]
    )


def test_cout_credit_synthese():
    synthese = cout_credit(200_000, 4.0, 0.36, 20)
    assert synthese["mensualite_totale"] == pytest.approx(1211.96 + 60.0, abs=0.01)
    assert synthese["cout_interets"] == pytest.approx(
        synthese["mensualite_hors_assurance"] * 240 - 200_000
    )
    assert synthese["cout_assurance"] == pytest.approx(60.0 * 240)


# ── Rendements ───────────────────────────────────────────────────────────────
def test_rendements_trois_niveaux():
    # L=1000, C=2400/an, P_acq=240 000, tau=15 %
    r = rendements(1000, 2400, 240_000, 15.0)
    assert r["brut"] == pytest.approx(5.0)
    assert r["net"] == pytest.approx(4.0)
    assert r["net_net"] == pytest.approx(3.4)


def test_rendements_revenu_negatif_non_impose():
    # Charges > loyers : pas d'impôt, net-net == net
    r = rendements(100, 5000, 100_000, 30.0)
    assert r["net"] < 0
    assert r["net_net"] == pytest.approx(r["net"])


def test_rendements_cout_nul_rejete():
    with pytest.raises(ValueError):
        rendements(1000, 0, 0, 0)


# ── VAN / TRI ────────────────────────────────────────────────────────────────
def test_van_actualisation_simple():
    # -1000 puis +1100 actualisé à 10 % → VAN nulle
    assert van([-1000, 1100], 10.0) == pytest.approx(0.0)


def test_van_taux_zero():
    assert van([-1000, 500, 600], 0.0) == pytest.approx(100.0)


def test_tri_un_flux():
    assert tri([-1000, 1100]) == pytest.approx(10.0, abs=1e-4)


def test_tri_deux_ans():
    # 1000 * 1.1² = 1210
    assert tri([-1000, 0, 1210]) == pytest.approx(10.0, abs=1e-4)


def test_tri_sans_solution():
    assert tri([1000, 1100]) is None
    assert tri([-1000, -1100]) is None
    assert tri([-1000]) is None


def test_tri_annule_la_van():
    flux = [-150_000, 8000, 8200, 8400, 8600, 160_000]
    taux = tri(flux)
    assert taux is not None
    assert van(flux, taux) == pytest.approx(0.0, abs=0.01)


# ── Orchestration scénario ───────────────────────────────────────────────────
class FauxObjet:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def faux_projet(**surcharges):
    defauts = dict(
        prix_bien=1_000_000.0,
        budget_travaux=100_000.0,
        taux_frais_acquisition=7.0,
        loyer_mensuel=7000.0,
        charges_copro_annuelles=6000.0,
        assurance_annuelle=2000.0,
        frais_gestion_pct=0.0,
        vacance_pct=0.0,
        entretien_annuel=0.0,
        taxe_annuelle=4000.0,
        taux_imposition=15.0,
        zone=FauxObjet(devise="MAD"),
    )
    defauts.update(surcharges)
    return FauxObjet(**defauts)


def faux_scenario(**surcharges):
    defauts = dict(
        mode="credit",
        apport=300_000.0,
        taux_interet=4.5,
        taux_assurance=0.3,
        duree_annees=20,
        horizon_annees=20,
        revalorisation_loyer_pct=0.0,
        revalorisation_bien_pct=0.0,
        frais_revente_pct=0.0,
        taux_actualisation=3.0,
    )
    defauts.update(surcharges)
    return FauxObjet(**defauts)


def test_scenario_credit_coherent():
    resultats = calculer_scenario(faux_projet(), faux_scenario())
    acq = resultats["acquisition"]
    fin = resultats["financement"]
    assert acq["cout_total"] == pytest.approx(1_170_000)  # 1M + 7% + 100k
    assert fin["capital_emprunte"] == pytest.approx(870_000)
    assert resultats["projection"]["investissement_initial"] == pytest.approx(300_000)
    # Année 1 : loyer 84 000, charges 12 000, impôt 15 % de 72 000 = 10 800
    exploitation = resultats["exploitation"]
    assert exploitation["loyer_effectif"] == pytest.approx(84_000)
    assert exploitation["impot_annuel"] == pytest.approx(10_800)
    # Le TRI annule la VAN des flux du scénario
    taux = resultats["indicateurs"]["tri"]
    assert taux is not None
    assert van(resultats["projection"]["flux"], taux) == pytest.approx(0.0, abs=1.0)


def test_scenario_cash_sans_credit():
    resultats = calculer_scenario(faux_projet(), faux_scenario(mode="cash"))
    assert resultats["financement"]["capital_emprunte"] == 0.0
    assert resultats["financement"]["mensualite_totale"] == 0.0
    assert resultats["projection"]["investissement_initial"] == pytest.approx(1_170_000)
    # Sans crédit, le cash-flow annuel = revenu net d'impôt
    assert resultats["indicateurs"]["cashflow_annuel"] == pytest.approx(
        84_000 - 12_000 - 10_800
    )


def test_scenario_vacance_et_gestion():
    projet = faux_projet(vacance_pct=10.0, frais_gestion_pct=5.0)
    resultats = calculer_scenario(projet, faux_scenario(mode="cash"))
    exploitation = resultats["exploitation"]
    assert exploitation["loyer_effectif"] == pytest.approx(84_000 * 0.9)
    assert exploitation["charges_totales"] == pytest.approx(12_000 + 84_000 * 0.9 * 0.05)


def test_scenario_derniere_annee_integre_revente():
    resultats = calculer_scenario(
        faux_projet(), faux_scenario(horizon_annees=10, revalorisation_bien_pct=2.0)
    )
    lignes = resultats["projection"]["lignes"]
    assert len(lignes) == 10
    assert lignes[-1]["revente"] > 0
    # Revente = valeur revalorisée moins le CRD après 10 ans
    valeur_attendue = 1_000_000 * 1.02**10
    crd = capital_restant_du(870_000, 4.5, 20, 10)
    assert lignes[-1]["revente"] == pytest.approx(valeur_attendue - crd)
