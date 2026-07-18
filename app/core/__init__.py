"""Moteur de calcul financier — Python pur, sans dépendance Flask.

Toutes les fonctions sont déterministes et testées unitairement (pytest).
Conventions : les taux sont passés en pourcentage (4.0 = 4 %), les montants
dans la devise de la zone du projet.

Modules (implémentation : semaine 2) :
- ``acquisition``  : coût total d'acquisition selon la zone.
- ``financement``  : mensualité, tableau d'amortissement, coût du crédit.
- ``rendement``    : rendements brut, net et net-net.
- ``indicateurs``  : cash-flow, VAN, TRI.
- ``scenario``     : orchestration entrées → résultats complets.
"""
