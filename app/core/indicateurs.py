"""Indicateurs de décision : cash-flow annuel, VAN, TRI.

VAN = somme des F_k / (1+a)^k ; TRI = taux annulant la VAN, résolu par
Newton-Raphson avec repli sur bissection bornée (flux à signes multiples).

Implémentation prévue en semaine 2 (feuille de route).
"""


def van(flux: list[float], taux_actualisation_pct: float) -> float:
    raise NotImplementedError("Semaine 2 — moteur de calcul")


def tri(flux: list[float]) -> float | None:
    """Renvoie le TRI en %, ou None si aucune solution exploitable."""
    raise NotImplementedError("Semaine 2 — moteur de calcul")
