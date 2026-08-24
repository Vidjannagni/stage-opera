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

Étude automatique (ajoutée après le retour du cabinet sur la lourdeur de la
saisie — cf. docs/etude_automatique.md) :
- ``hypotheses``   : valeurs par défaut (taux par durée, revalorisations…).
- ``generation``   : fabrique la famille de montages, chaque paramètre tracé.
- ``arbitrage``    : classe selon l'objectif du client et met la réponse en mots.
- ``estimation``   : ordres de grandeur des charges courantes d'un locatif.
- ``format_fr``    : mise en forme française des nombres dans les phrases.

Le brief du client et le bien qu'on lui chiffre (ajoutés après un relevé
d'incohérences entre les deux écrans) :
- ``profil_bien``  : ce qu'il est logique de demander selon le type de bien.
- ``coherence``    : ce qui, dans un dossier, s'écarte de ce que le client a
  demandé — dit, jamais bloqué.
"""
