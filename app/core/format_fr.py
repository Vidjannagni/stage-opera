"""Mise en forme française des nombres, côté moteur.

Les gabarits disposent du filtre Jinja ``montant``; le moteur, lui, produit des
phrases d'explication destinées au client et a besoin des mêmes conventions :
espace comme séparateur de milliers, virgule décimale.
"""


def montant_texte(valeur: float, devise: str = "") -> str:
    """1234567.4 → « 1 234 567 MAD » (arrondi à l'unité)."""
    texte = f"{valeur:,.0f}".replace(",", " ").replace("−", "-")
    return f"{texte} {devise}".strip()


def pct_texte(valeur: float, decimales: int = 2) -> str:
    """4.9 → « 4,90 % »."""
    return f"{valeur:.{decimales}f} %".replace(".", ",")


def annees_texte(nombre: int) -> str:
    return f"{nombre} an" if nombre <= 1 else f"{nombre} ans"
