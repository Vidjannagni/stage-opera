"""Hypothèses par défaut utilisées pour construire les scénarios automatiquement.

Elles ne remplacent jamais une donnée saisie : elles ne servent qu'à
**proposer** un montage quand personne n'a renseigné la valeur. Chaque
hypothèse est ici commentée, parce qu'un chiffre non justifié n'a pas sa place
dans un calcul montré à un client.

Toutes ces valeurs sont **à faire valider par le cabinet** ; elles sont
regroupées dans ce seul module pour qu'une révision tienne en une ligne.
"""

#: Taux d'intérêt annuel proposé selon la durée du prêt (%).
#: Une banque facture la durée : plus le prêt est long, plus le taux est élevé.
#: Ordres de grandeur du marché marocain observés au cadrage du projet.
TAUX_PAR_DUREE = {15: 4.60, 20: 4.90, 25: 5.20}

#: Durées de prêt proposées, dans l'ordre où elles sont présentées.
DUREES = (15, 20, 25)

#: Taux d'assurance emprunteur annuel (% du capital initial).
TAUX_ASSURANCE = 0.35

#: Revalorisation annuelle du loyer (%) — indexation prudente.
REVALORISATION_LOYER = 1.5

#: Revalorisation annuelle de la valeur du bien (%).
REVALORISATION_BIEN = 2.0

#: Frais de revente (% de la valeur de sortie) : commission et formalités.
FRAIS_REVENTE = 2.5

#: Taux d'actualisation de la VAN (%) — coût du temps pour le client.
TAUX_ACTUALISATION = 3.0

#: Part du **prix du bien** qu'une banque accepte de financer (%).
#: Règle retenue : la banque prête sur le bien, pas sur les frais. Les frais
#: d'acquisition et les travaux restent donc à la charge de l'acquéreur, ce qui
#: fixe mécaniquement l'apport minimal d'un dossier.
PART_FINANCABLE_DU_PRIX = 100.0

#: Supplément d'apport, en % du prix, du montage « apport renforcé ».
SUPPLEMENT_APPORT_RENFORCE = 10.0

#: Horizon retenu quand le client n'en a pas déclaré, en années.
#: Distinct selon le type d'opération : un locatif se juge sur le long terme,
#: une opération de revente sur un cycle court.
HORIZON_DEFAUT_LOCATIF = 20
HORIZON_DEFAUT_REVENTE = 10


def taux_interet(duree_annees: int) -> float:
    """Taux proposé pour une durée, avec repli sur la durée la plus proche."""
    if duree_annees in TAUX_PAR_DUREE:
        return TAUX_PAR_DUREE[duree_annees]
    proche = min(TAUX_PAR_DUREE, key=lambda d: abs(d - duree_annees))
    return TAUX_PAR_DUREE[proche]


def horizon_defaut(est_locatif: bool) -> int:
    return HORIZON_DEFAUT_LOCATIF if est_locatif else HORIZON_DEFAUT_REVENTE
