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

Facteur temps (retour du cabinet) :
- ``projet.delai_livraison_mois`` diffère la mise en exploitation (achat sur
  plan) : tant que le bien n'est pas livré il ne produit ni loyer ni charges
  d'exploitation, mais les annuités d'emprunt courent déjà ;
- ``scenario.prix_revente``, s'il est renseigné, remplace la valeur déduite de
  la revalorisation annuelle (construction-revente, lotissement, prix négocié) ;
- une opération de type ``terrain`` n'a simplement pas de loyer : toute la
  valeur vient de la plus-value.
"""
from .acquisition import cout_acquisition, frais_acquisition
from .financement import cout_credit, tableau_amortissement
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

    # Tableau d'amortissement construit une seule fois ; CRD en fin d'année k
    amortissement = (
        tableau_amortissement(capital, scenario.taux_interet, scenario.duree_annees)
        if en_credit else []
    )

    def crd_fin_annee(annee: int) -> float:
        if not amortissement:
            return 0.0
        mois = min(annee * 12, len(amortissement))
        return amortissement[mois - 1]["crd"] if mois > 0 else capital

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
    delai = max(getattr(projet, "delai_livraison_mois", 0) or 0, 0)

    def mois_exploites(annee: int) -> int:
        """Mois d'exploitation de l'année k, une fois le bien livré (0 à 12)."""
        return min(max(12 * annee - delai, 0), 12)

    # Valeur du bien à l'horizon : prix de revente connu, sinon revalorisation.
    prix_revente_saisi = getattr(scenario, "prix_revente", None)
    valeur_bien_horizon = (
        prix_revente_saisi if prix_revente_saisi else prix * r_bien**horizon
    )
    revente_nette = (
        valeur_bien_horizon * (1.0 - scenario.frais_revente_pct / 100.0)
        - crd_fin_annee(horizon)
    )

    flux = [-investissement_initial]
    lignes = []
    cumul = -investissement_initial
    for annee in range(1, horizon + 1):
        part_annee = mois_exploites(annee) / 12.0
        loyer_k = loyer_effectif * r_loyer ** (annee - 1) * part_annee
        gestion_k = loyer_k * projet.frais_gestion_pct / 100.0
        # Tant que le bien n'est pas livré, il ne supporte pas de charges
        # d'exploitation (copropriété, assurance, entretien, taxe).
        charges_k = charges_fixes * part_annee + gestion_k
        revenu_k = loyer_k - charges_k
        impot_k = max(revenu_k, 0.0) * taux_impot / 100.0
        annuite_k = annuite if (en_credit and annee <= scenario.duree_annees) else 0.0
        cashflow_k = revenu_k - impot_k - annuite_k

        revente_k = revente_nette if annee == horizon else 0.0

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
                "crd": crd_fin_annee(annee),
                "part_exploitee": part_annee,
            }
        )

    # Cash-flow d'exploitation de l'année 1 (hors revente)
    cashflow_annuel = lignes[0]["cashflow"] if lignes else 0.0
    # Cash-flow « de croisière » : première année pleinement exploitée, hors
    # année de revente. Pour un achat sur plan, l'année 1 n'est pas
    # représentative de ce que le bien rendra une fois livré.
    lignes_pleines = [
        l for l in lignes if l["part_exploitee"] == 1.0 and l["revente"] == 0.0
    ]
    cashflow_regime = (
        lignes_pleines[0]["cashflow"] if lignes_pleines else cashflow_annuel
    )

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
            # Impôt d'une année pleinement exploitée (cohérent avec le loyer
            # annuel affiché juste au-dessus, y compris en achat sur plan).
            "impot_annuel": (
                lignes_pleines[0]["impot"] if lignes_pleines
                else (lignes[0]["impot"] if lignes else 0.0)
            ),
        },
        "rendements": rdts,
        # Ordre voulu par le cabinet : rendement net et cash-flow d'abord,
        # TRI et VAN ensuite. La valeur créée matérialise le « facteur temps ».
        "indicateurs": {
            "cashflow_mensuel": cashflow_regime / 12.0,
            "cashflow_annuel": cashflow_regime,
            "cashflow_mensuel_annee1": cashflow_annuel / 12.0,
            "cashflow_annuel_annee1": cashflow_annuel,
            "valeur_creee": cumul,
            "van": van(flux, scenario.taux_actualisation),
            "tri": tri(flux),
        },
        "revente": {
            "valeur_bien_horizon": valeur_bien_horizon,
            "prix_revente_saisi": bool(prix_revente_saisi),
            "plus_value_brute": valeur_bien_horizon - prix,
            "frais_revente": valeur_bien_horizon * scenario.frais_revente_pct / 100.0,
            "capital_restant_du": crd_fin_annee(horizon),
            "revente_nette": revente_nette,
        },
        "projection": {
            "horizon_annees": horizon,
            "investissement_initial": investissement_initial,
            "delai_livraison_mois": delai,
            "flux": flux,
            "lignes": lignes,
        },
        "type_operation": getattr(projet, "type_operation", "locatif"),
        "devise": projet.zone.devise if projet.zone else "",
    }
