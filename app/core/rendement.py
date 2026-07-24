"""Rendements locatifs : brut, net, net-net (après impôt au taux effectif).

R_brut    = 12L / P_acq
R_net     = (12L − C) / P_acq
R_net-net = (12L − C)(1 − τ) / P_acq

Les rendements sont renvoyés en pourcentage (5.2 = 5,2 %).
"""


def rendements(
    loyer_mensuel: float,
    charges_annuelles: float,
    cout_acquisition: float,
    taux_imposition_pct: float,
) -> dict:
    if cout_acquisition <= 0:
        raise ValueError("le coût d'acquisition doit être strictement positif")
    loyer_annuel = 12.0 * loyer_mensuel
    revenu_net = loyer_annuel - charges_annuelles
    # Convention : l'impôt ne s'applique qu'à un revenu net positif.
    impot = max(revenu_net, 0.0) * taux_imposition_pct / 100.0
    return {
        "brut": 100.0 * loyer_annuel / cout_acquisition,
        "net": 100.0 * revenu_net / cout_acquisition,
        "net_net": 100.0 * (revenu_net - impot) / cout_acquisition,
    }
