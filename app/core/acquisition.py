"""Coût d'acquisition : P_acq = prix + frais(zone) + travaux."""


def frais_acquisition(prix: float, taux_frais_pct: float) -> float:
    """Frais d'acquisition : F_acq = P * taux/100.

    Le taux est la somme des taux de la zone (enregistrement, publicité
    foncière, notaire, divers) ou la surcharge saisie au niveau du bien.
    """
    if prix < 0 or taux_frais_pct < 0:
        raise ValueError("prix et taux de frais doivent être positifs")
    return prix * taux_frais_pct / 100.0


def cout_acquisition(prix: float, taux_frais_pct: float, travaux: float = 0.0) -> float:
    """Coût total d'acquisition : P_acq = P + F_acq + T."""
    if travaux < 0:
        raise ValueError("le budget travaux doit être positif")
    return prix + frais_acquisition(prix, taux_frais_pct) + travaux
