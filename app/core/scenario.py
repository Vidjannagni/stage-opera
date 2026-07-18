"""Orchestration : entrées (projet + scénario) → résultats complets.

Les objets `projet` et `scenario` sont les modèles SQLAlchemy (ou tout objet
présentant les mêmes attributs — le moteur reste indépendant de Flask).

Conventions de projection (cf. cahier des charges §3) :
- la vacance locative réduit le loyer effectivement perçu ;
- les frais de gestion suivent le loyer effectif, les autres charges sont
  constantes sur l'horizon ;
- le loyer et la valeur du bien sont revalorisés annuellement ;
- l'investissement initial (année 0) est la part non empruntée du coût
  d'acquisition ; la dernière année intègre la revente nette des frais de
  revente et du capital restant dû.
"""
from .acquisition import cout_acquisition, frais_acquisition
from .financement import capital_restant_du, cout_credit
from .indicateurs import tri, van
from .rendement import rendements


def calculer_scenario(projet, scenario) -> dict:
    # ── Acquisition ───────────────────────────────────────────────────────────
    prix = projet.prix_bien
    taux_frais = projet.taux_frais_acquisition
    travaux = projet.budget_travaux
    frais = frais_acquisition(prix, taux_frais)
    cout_total = cout_acquisition(prix, taux_frais, travaux)

    # ── Financement ───────────────────────────────────────────────────────────
    en_credit = scenario.mode == "credit"
    capital = max(cout_total - scenario.apport, 0.0) if en_credit else 0.0
    credit = cout_credit(
        capital, scenario.taux_interet, scenario.taux_assurance, scenario.duree_annees
    )
    annuite = credit["mensualite_totale"] * 12.0
    investissement_initial = cout_total - capital

    # ── Exploitation (année 1) ────────────────────────────────────────────────
    loyer_annuel = 12.0 * projet.loyer_mensuel
    vacance = loyer_annuel * projet.vacance_pct / 100.0
    loyer_effectif = loyer_annuel - vacance
    gestion = loyer_effectif * projet.frais_gestion_pct / 100.0
    charges_fixes = (
        projet.charges_copro_annuelles
        + projet.assurance_annuelle
        + projet.entretien_annuel
        + projet.taxe_annuelle
    )
    charges_totales = charges_fixes + gestion
    taux_impot = projet.taux_imposition

    # ── Rendements (convention : C inclut vacance et gestion) ────────────────
    rdts = rendements(
        projet.loyer_mensuel, charges_totales + vacance, cout_total, taux_impot
    )

    # ── Projection annuelle sur l'horizon ────────────────────────────────────
    r_loyer = 1.0 + scenario.revalorisation_loyer_pct / 100.0
    r_bien = 1.0 + scenario.revalorisation_bien_pct / 100.0
    horizon = scenario.horizon_annees

    flux = [-investissement_initial]
    lignes = []
    cumul = -investissement_initial
    for annee in range(1, horizon + 1):
        loyer_k = loyer_effectif * r_loyer ** (annee - 1)
        gestion_k = loyer_k * projet.frais_gestion_pct / 100.0
        charges_k = charges_fixes + gestion_k
        revenu_k = loyer_k - charges_k
        impot_k = max(revenu_k, 0.0) * taux_impot / 100.0
        annuite_k = annuite if (en_credit and annee <= scenario.duree_annees) else 0.0
        cashflow_k = revenu_k - impot_k - annuite_k

        revente_k = 0.0
        if annee == horizon:
            valeur_bien = prix * r_bien ** horizon
            crd = capital_restant_du(
                capital, scenario.taux_interet, scenario.duree_annees, horizon
            ) if en_credit else 0.0
            revente_k = valeur_bien * (1.0 - scenario.frais_revente_pct / 100.0) - crd

        flux.append(cashflow_k + revente_k)
        cumul += cashflow_k + revente_k
        lignes.append(
            {
                "annee": annee,
                "loyer": loyer_k,
                "charges": charges_k,
                "impot": impot_k,
                "annuite": annuite_k,
                "cashflow": cashflow_k,
                "revente": revente_k,
                "cumul": cumul,
            }
        )

    # Cash-flow d'exploitation de l'année 1 (hors revente)
    cashflow_annuel = lignes[0]["cashflow"] if lignes else 0.0

    return {
        "acquisition": {
            "prix": prix,
            "taux_frais_pct": taux_frais,
            "frais": frais,
            "travaux": travaux,
            "cout_total": cout_total,
        },
        "financement": {
            "mode": scenario.mode,
            "apport": scenario.apport if en_credit else cout_total,
            "capital_emprunte": capital,
            "duree_annees": scenario.duree_annees if en_credit else 0,
            **credit,
        },
        "exploitation": {
            "loyer_annuel": loyer_annuel,
            "vacance": vacance,
            "loyer_effectif": loyer_effectif,
            "charges_totales": charges_totales,
            "impot_annuel": lignes[0]["impot"] if lignes else 0.0,
        },
        "rendements": rdts,
        "indicateurs": {
            "cashflow_mensuel": cashflow_annuel / 12.0,
            "cashflow_annuel": cashflow_annuel,
            "van": van(flux, scenario.taux_actualisation),
            "tri": tri(flux),
        },
        "projection": {
            "horizon_annees": horizon,
            "investissement_initial": investissement_initial,
            "flux": flux,
            "lignes": lignes,
        },
        "devise": projet.zone.devise if projet.zone else "",
    }
