"""Financement : mensualité (annuité constante), amortissement, coût du crédit.

M = C * t / (1 - (1+t)^-n), t = taux mensuel (nominal + assurance), n = mois.
Cas limite t = 0 : M = C / n.

Implémentation prévue en semaine 2 (feuille de route).
"""


def mensualite(capital: float, taux_annuel_pct: float, duree_annees: int) -> float:
    raise NotImplementedError("Semaine 2 — moteur de calcul")


def tableau_amortissement(
    capital: float, taux_annuel_pct: float, duree_annees: int
) -> list[dict]:
    """Échéancier mensuel : intérêts, capital remboursé, capital restant dû."""
    raise NotImplementedError("Semaine 2 — moteur de calcul")
