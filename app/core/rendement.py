"""Rendements locatifs : brut, net, net-net (après impôt au taux effectif).

R_brut    = 12L / P_acq
R_net     = (12L - C) / P_acq
R_net-net = (12L - C)(1 - tau) / P_acq

Implémentation prévue en semaine 2 (feuille de route).
"""


def rendements(
    loyer_mensuel: float, charges_annuelles: float,
    cout_acquisition: float, taux_imposition_pct: float,
) -> dict:
    raise NotImplementedError("Semaine 2 — moteur de calcul")
