"""Financement : mensualité (annuité constante), amortissement, coût du crédit.

Conventions :
- taux en pourcentage annuel (4.0 = 4 %) ;
- l'assurance est calculée sur le capital initial (prime constante), convention
  la plus courante pour les prêts immobiliers.
"""


def mensualite(capital: float, taux_annuel_pct: float, duree_annees: int) -> float:
    """Mensualité hors assurance : M = C·t / (1 − (1+t)^−n).

    t = taux mensuel, n = nombre de mensualités. Cas limite t=0 : M = C/n.
    """
    if capital < 0 or taux_annuel_pct < 0:
        raise ValueError("capital et taux doivent être positifs")
    if duree_annees <= 0:
        raise ValueError("la durée doit être strictement positive")
    if capital == 0:
        return 0.0
    n = duree_annees * 12
    t = taux_annuel_pct / 100.0 / 12.0
    if t == 0:
        return capital / n
    return capital * t / (1.0 - (1.0 + t) ** -n)


def mensualite_assurance(capital: float, taux_assurance_pct: float) -> float:
    """Prime d'assurance mensuelle sur capital initial : C · taux/100 / 12."""
    if capital < 0 or taux_assurance_pct < 0:
        raise ValueError("capital et taux d'assurance doivent être positifs")
    return capital * taux_assurance_pct / 100.0 / 12.0


def tableau_amortissement(
    capital: float, taux_annuel_pct: float, duree_annees: int
) -> list[dict]:
    """Échéancier mensuel hors assurance.

    Chaque ligne : mois (1..n), interet, capital_rembourse, crd (capital
    restant dû en fin de mois). La dernière ligne solde exactement le CRD
    pour absorber les arrondis flottants.
    """
    if capital == 0:
        return []
    m = mensualite(capital, taux_annuel_pct, duree_annees)
    t = taux_annuel_pct / 100.0 / 12.0
    n = duree_annees * 12
    lignes: list[dict] = []
    crd = capital
    for mois in range(1, n + 1):
        interet = crd * t
        rembourse = m - interet
        if mois == n:
            rembourse = crd  # solde exact
        crd = max(crd - rembourse, 0.0)
        lignes.append(
            {"mois": mois, "interet": interet, "capital_rembourse": rembourse, "crd": crd}
        )
    return lignes


def capital_restant_du(
    capital: float, taux_annuel_pct: float, duree_annees: int, apres_annees: int
) -> float:
    """Capital restant dû après `apres_annees` années de remboursement."""
    if apres_annees <= 0:
        return capital
    if apres_annees >= duree_annees or capital == 0:
        return 0.0
    lignes = tableau_amortissement(capital, taux_annuel_pct, duree_annees)
    return lignes[apres_annees * 12 - 1]["crd"]


def cout_credit(
    capital: float, taux_annuel_pct: float, taux_assurance_pct: float, duree_annees: int
) -> dict:
    """Synthèse du crédit : mensualités et coûts totaux sur la durée."""
    m_hors_assurance = mensualite(capital, taux_annuel_pct, duree_annees)
    m_assurance = mensualite_assurance(capital, taux_assurance_pct)
    n = duree_annees * 12
    cout_interets = m_hors_assurance * n - capital
    cout_assurance = m_assurance * n
    return {
        "mensualite_hors_assurance": m_hors_assurance,
        "mensualite_assurance": m_assurance,
        "mensualite_totale": m_hors_assurance + m_assurance,
        "cout_interets": cout_interets,
        "cout_assurance": cout_assurance,
        "cout_total_credit": cout_interets + cout_assurance,
    }
