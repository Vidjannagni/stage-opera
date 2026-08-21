# L'étude automatique — méthode et justification

L'outil sait désormais **construire seul les montages financiers d'un dossier,
les confronter et en proposer un**, avec l'explication à dire au client. Ce
document décrit ce qui se passe entre le clic et la page de proposition, et
défend chacune des décisions prises.

Le code correspondant tient en trois modules du moteur — indépendants de Flask,
donc testables seuls :

| Module | Rôle |
|---|---|
| `app/core/hypotheses.py` | Les valeurs par défaut : taux par durée, assurance, revalorisations, frais de revente, actualisation. |
| `app/core/generation.py` | Fabrique la famille de montages et **la trace** : chaque paramètre porte son origine. |
| `app/core/arbitrage.py` | Calcule, classe selon l'objectif du client, et met la conclusion en mots. |

---

## 1. Pourquoi automatiser

Le formulaire de scénario demandait onze valeurs — apport, taux, assurance,
durée, horizon, revalorisations, frais de revente, taux d'actualisation. En
rendez-vous, un conseiller ne les a pas toutes en tête, et surtout : **il ne
sait pas encore laquelle essayer**. Il fallait donc saisir un montage pour
découvrir qu'il n'était pas le bon, puis recommencer.

L'étude automatique inverse la charge : le conseiller décrit **le bien et le
client**, l'outil se charge des montages. Ce que l'on saisissait, on le lit
maintenant.

## 2. Comment les montages sont construits

### La règle de financement

Une seule règle, explicite et vérifiable : **une banque prête sur le bien, pas
sur les frais**. Les frais d'acquisition et les travaux restent donc à la charge
de l'acquéreur, ce qui fixe mécaniquement l'apport minimal d'un dossier :

```
apport minimal = frais d'acquisition + travaux
```

C'est la règle la plus défendable dont nous disposions sans données bancaires
réelles ; elle est isolée dans `hypotheses.PART_FINANCABLE_DU_PRIX`, une
constante à revoir avec le cabinet.

### La famille engendrée

| Famille | Apport | Durées |
|---|---|---|
| Paiement comptant | coût d'entrée total | — |
| Crédit à apport minimal | frais + travaux | 15, 20, 25 ans |
| Crédit à apport renforcé | apport minimal + 10 % du prix | 15, 20, 25 ans |
| Crédit avec tout le budget en apport | budget déclaré du client, borné par l'apport minimal et le coût total | 15, 20, 25 ans |

Soit une dizaine de montages, dédoublonnés : deux montages de même mode, même
apport et même durée n'apparaissent qu'une fois. Un client dont le budget
couvre tout le coût d'entrée ne se voit pas proposer un « crédit » sans capital
emprunté — c'est l'achat comptant.

**Le taux suit la durée** (15 ans : 4,60 % ; 20 ans : 4,90 % ; 25 ans : 5,20 %),
parce qu'une banque facture le temps. Sans cette variation, l'outil aurait
mécaniquement recommandé la durée la plus longue à chaque dossier.

### Ce qui n'est pas engendré

L'**horizon** ne varie pas : c'est celui du client, pas un levier de montage.
Le faire varier reviendrait à répondre à une autre question que la sienne.

## 3. Comment les montages sont classés

### Il n'y a pas de bon montage dans l'absolu

Le cabinet a été clair : *« un investissement peut être rentable pour une
personne et ne pas l'être pour une autre »*. Le classement est donc **relatif
à un client** :

- il ne compare que des montages portant sur **le même bien** et le **même
  horizon** ;
- chaque critère est ramené entre le meilleur et le moins bon des montages **de
  cette étude** (0 à 1), puis pondéré selon l'**objectif déclaré** ;
- un score n'est donc **pas une note** : il n'a de sens qu'à l'intérieur d'une
  page. Deux études ne se comparent pas.

### Les pondérations

| Critère | Revenu locatif | Plus-value | Patrimoine |
|---|---:|---:|---:|
| Cash-flow mensuel | 40 % | 15 % | 25 % |
| Rendement net | 25 % | — | — |
| Valeur créée sur l'horizon | 20 % | 40 % | 30 % |
| TRI | — | 30 % | 20 % |
| Argent immobilisé au départ *(moins il y en a, mieux c'est)* | 15 % | 15 % | 25 % |

Le rendement net et le cash-flow dominent pour un objectif de revenu : c'est
l'ordre de lecture indiqué par le cabinet. Pour une opération **sans loyer**, le
rendement locatif n'existe pas ; son poids est redistribué sur les autres
critères, et le tableau des poids affiché à l'écran le montre.

Ces pondérations traduisent une intention, pas une vérité de marché. Elles sont
**affichées sur la page** et regroupées dans une seule table du code
(`arbitrage.POIDS`) : les discuter avec le cabinet ne demande pas de relire
l'application.

### Ce qui est écarté, et comment on le dit

Un montage dont l'apport dépasse le budget déclaré est **écarté, jamais
masqué** : il figure sur la page avec son motif chiffré — *« apport de
1 070 000 MAD pour un budget déclaré de 1 000 000 MAD — il manque 70 000 MAD »*.
Quand aucun montage ne tient dans le budget, la page le dit en tête et propose
les trois sorties possibles plutôt que d'afficher un classement trompeur.

Un budget **non renseigné** ne déclenche aucun filtrage : l'outil signale qu'il
n'a pas pu écarter, plutôt que de filtrer sur une valeur inventée.

## 4. La mise en mots

La proposition est rendue en quatre registres, volontairement séparés :

1. **Le résumé** — une phrase, en langage courant, avec l'apport, l'effort
   mensuel et la valeur créée à l'horizon. Aucun terme technique non explicité.
2. **Pourquoi celui-ci** — les écarts chiffrés avec le montage classé juste
   après.
3. **Ce que les autres font mieux** — l'inverse. Un argumentaire qui ne
   nommerait pas ce que l'on perd serait de la vente, pas du conseil. C'est
   typiquement là qu'apparaît l'**effet de levier** : l'achat comptant l'emporte
   souvent sur le cash-flow, tout en rendant moins par dirham engagé.
4. **À dire au client avant qu'il s'engage** — effort mensuel négatif, apport
   qui consomme presque tout le budget, revente avant la fin du prêt, bien non
   livré, prix de sortie hypothétique.

## 5. Traçabilité : la constitution complète

Chaque montage porte la liste de **tous** ses paramètres, avec pour chacun d'où
vient la valeur : *dossier*, *brief du client*, *zone de marché*, *calculé*,
*hypothèse par défaut*, *règle de génération*. La page l'affiche à la demande,
montage par montage. Un chiffre qu'on ne peut pas justifier devant un client
n'a pas sa place dans une proposition.

## 6. Du montage proposé au scénario enregistré

Un montage retenu est enregistré comme **scénario ordinaire** : il rejoint la
page de résultats, la comparaison, l'export PDF et l'export Excel, et reste
modifiable champ par champ. L'étude est un point de départ, pas une impasse.

Techniquement, l'enregistrement **rejoue l'étude côté serveur** — elle est
déterministe — au lieu de faire transiter les montages par le formulaire : le
navigateur ne peut donc pas faire enregistrer un montage qui n'a jamais été
proposé.

## 7. Limites assumées

- **Les hypothèses de taux ne sont pas des cotations réelles.** Elles sont
  calibrées sur des ordres de grandeur du marché marocain et attendent la
  validation du cabinet.
- **La capacité d'emprunt n'est pas vérifiée** : l'outil filtre sur l'apport,
  pas sur le taux d'endettement — nous ne collectons pas les revenus du client.
- **Le prix de sortie reste l'hypothèse la plus fragile** quand il n'est pas
  connu ; la page le dit à chaque fois plutôt qu'une fois pour toutes.
- **Aucun échéancier VEFA par tranches** : le décalage de livraison est
  modélisé, pas l'étalement des appels de fonds.

---

*Tests correspondants : `tests/test_etude_automatique.py` — notamment
`test_l_objectif_du_client_change_le_montage_proposé`, qui vérifie que le même
bien et le même budget donnent deux réponses différentes selon l'objectif
déclaré. C'est la position du cabinet, traduite en test.*
