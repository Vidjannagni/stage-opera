"""Indicateurs de décision : VAN et TRI sur des flux annuels.

Convention : flux[0] est le flux de l'année 0 (investissement initial,
généralement négatif), flux[k] le cash-flow de l'année k.
"""

_TRI_BORNE_BASSE = -0.9999  # -99,99 % par an
_TRI_BORNE_HAUTE = 10.0     # +1000 % par an
_PRECISION = 1e-7
_MAX_ITERATIONS = 200


def van(flux: list[float], taux_actualisation_pct: float) -> float:
    """Valeur actuelle nette : somme des F_k / (1+a)^k."""
    a = taux_actualisation_pct / 100.0
    if a <= -1.0:
        raise ValueError("le taux d'actualisation doit être supérieur à -100 %")
    return sum(f / (1.0 + a) ** k for k, f in enumerate(flux))


def tri(flux: list[float]) -> float | None:
    """Taux de rentabilité interne en %, ou None si aucune solution exploitable.

    Résolution par Newton-Raphson, avec repli sur une bissection bornée
    [-99,99 %, +1000 %] si Newton ne converge pas (flux à signes multiples).
    """
    if len(flux) < 2 or all(f >= 0 for f in flux) or all(f <= 0 for f in flux):
        return None

    def f(taux: float) -> float:
        return sum(fk / (1.0 + taux) ** k for k, fk in enumerate(flux))

    def f_prime(taux: float) -> float:
        return sum(
            -k * fk / (1.0 + taux) ** (k + 1) for k, fk in enumerate(flux) if k > 0
        )

    # Newton-Raphson depuis un point de départ raisonnable.
    taux = 0.05
    for _ in range(50):
        derivee = f_prime(taux)
        if derivee == 0:
            break
        suivant = taux - f(taux) / derivee
        if suivant <= _TRI_BORNE_BASSE or suivant >= _TRI_BORNE_HAUTE:
            break
        if abs(suivant - taux) < _PRECISION:
            return suivant * 100.0
        taux = suivant

    # Repli : bissection sur un intervalle où f change de signe.
    bas, haut = _TRI_BORNE_BASSE, _TRI_BORNE_HAUTE
    f_bas, f_haut = f(bas), f(haut)
    if f_bas * f_haut > 0:
        return None
    for _ in range(_MAX_ITERATIONS):
        milieu = (bas + haut) / 2.0
        f_milieu = f(milieu)
        if abs(f_milieu) < _PRECISION or (haut - bas) / 2.0 < _PRECISION:
            return milieu * 100.0
        if f_bas * f_milieu < 0:
            haut = milieu
        else:
            bas, f_bas = milieu, f_milieu
    return ((bas + haut) / 2.0) * 100.0
