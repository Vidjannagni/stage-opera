# RentImmo — Guide d'utilisation

*Outil d'accompagnement de l'investisseur immobilier — Choubel Consulting.*
Ce guide s'adresse au **conseiller** et suit l'ordre réel d'un accompagnement,
du premier entretien à la remise du document.

---

## 1. Démarrage et connexion

Lancez l'application (voir le README) puis ouvrez `http://127.0.0.1:5000`.
Créez votre compte consultant ou connectez-vous. **Chaque conseiller ne voit que
ses propres dossiers.**

Le **tableau de bord** affiche vos clients, l'avancement de vos dossiers et les
briefs de recherche qu'il reste à renseigner.

> Pour vous entraîner : `flask demo-data` crée un dossier complet
> (connexion `demo@choubel.com` / `demo1234`).

## 2. Ouvrir la fiche client

**Clients → Nouveau dossier client.** Quatre informations sont recueillies
systématiquement au premier entretien :

- le **nom** ;
- la **situation professionnelle** (salarié, profession libérale, chef
  d'entreprise, retraité…) ;
- la **nationalité** — elle conditionne l'accès au crédit et le rapatriement des
  fonds ;
- le **budget disponible**.

E-mail, téléphone et notes servent à votre suivi.

## 3. Renseigner le brief de recherche

L'enregistrement de la fiche vous amène directement au **brief**, c'est-à-dire ce
que le client recherche :

- **type de bien** (terrain, villa, appartement, immeuble) et **standing**
  (économique, social, moyen, haut standing, luxe) ;
- **superficie** recherchée et **zone géographique** ;
- pour un appartement : **chambres, salles de bains, salons, étage, orientation**
  (ce bloc disparaît si vous choisissez « Terrain ») ;
- **commodités** souhaitées : transports, écoles, commerces… ;
- **type d'acquisition** : bien déjà construit ou achat sur plan (VEFA) ;
- **budget** et **mode de financement** (comptant ou prêt bancaire).

Deux réponses comptent particulièrement : l'**objectif** (revenu locatif,
plus-value, constitution de patrimoine) et l'**horizon d'investissement**.

> **Pourquoi c'est décisif.** Il n'existe pas de seuil universel de rentabilité :
> un même bien peut convenir à un client et pas à un autre. L'objectif et
> l'horizon sont la grille de lecture de tous les chiffres qui suivront ; ils
> sont rappelés en tête de chaque écran de résultats.

## 4. Créer le dossier du bien

Depuis la fiche client : **+ Nouveau dossier**.

- **Type d'opération** — le réglage à choisir en premier :
  - *Locatif* : le bien sera mis en location ;
  - *Terrain / revente* : la valeur vient de la plus-value, pas d'un loyer. Le
    bloc d'exploitation locative disparaît.
- **Zone de marché** : le Maroc est présélectionné (MAD) ; la France et une zone
  personnalisée sont disponibles. L'encart bleu rappelle les taux appliqués, et
  **tous les calculs s'actualisent selon la zone**.
- **Où en est le dossier ?** : recherche, présentation, visites, compromis,
  notaire, livraison. Le déroulé s'affiche en bandeau sur la page du dossier.
- **Acquisition** : prix, budget travaux (ou coût de construction), et
  **délai de livraison en mois** pour un achat sur plan.
- **Exploitation** (locatif seulement) : loyer, charges, gestion, vacance,
  entretien, taxe. En rendez-vous, ne remplissez que ce que vous connaissez :
  les champs vides valent zéro.

## 5. Détailler les travaux (facultatif)

La carte **Travaux détaillés** permet de chiffrer poste par poste. Dès qu'un
poste existe, **le budget devient la somme des postes** — utile pour justifier le
chiffre devant le client.

## 6. Construire les scénarios

**+ Nouveau scénario** depuis le dossier. Deux modes : **crédit** (apport, taux,
assurance, durée) ou **cash**.

Les **hypothèses de projection** pilotent les indicateurs de sortie : horizon,
revalorisation du loyer et du bien, frais de revente, taux d'actualisation. Le
champ **Prix de revente à l'horizon** remplace la revalorisation annuelle quand
le prix de sortie est connu ou négocié — c'est le cas d'une opération de
construction-revente ou d'un lotissement.

La carte **Aperçu instantané** recalcule cash-flow, valeur créée, mensualité,
TRI et VAN **à chaque saisie**, avant même d'enregistrer.

## 7. Lire la page de résultats

Les indicateurs sont présentés dans l'ordre où le cabinet les regarde.

**Pour un locatif :**

| Indicateur | Lecture en une phrase |
|---|---|
| **Rendement net** | Le rendement du bien après charges, vacance et gestion. |
| **Cash-flow mensuel** | Ce que le client encaisse (vert) ou débourse (rouge) chaque mois. |
| Rendement net-net | Le même, après impôt. |
| Valeur créée | Le gain total sur l'horizon, revente comprise. |
| TRI · VAN | Arguments de second rang, utiles pour comparer deux montages. |

**Pour un terrain ou une revente :** la **valeur créée** et la **plus-value**
passent en tête, les rendements locatifs disparaissent.

Un encart **Achat sur plan** signale, le cas échéant, que le bien ne produit ni
loyer ni charges jusqu'à sa livraison — alors que les annuités courent déjà. Les
années concernées apparaissent en italique dans le tableau de projection, avec la
mention « en chantier ».

**Dupliquer** crée une variante pour tester une autre hypothèse sans perdre
l'original.

## 8. Comparer les scénarios

Sur la page du dossier, cochez 2 à 4 scénarios puis **Comparer la sélection** :
tableau côte à côte (dans le même ordre de lecture) et courbes de cash-flow
cumulé superposées. Le croisement des courbes montre à partir de quelle année un
montage devient plus intéressant que l'autre.

## 9. Remettre un document au client

Depuis la page de résultats :

- **Export PDF** : rapport aux couleurs du cabinet, rappelant l'objectif du
  client, les hypothèses et les conventions de calcul ;
- **Export Excel** : feuilles *Hypothèses*, *Indicateurs*, *Projection* et
  *Amortissement*, pour les clients qui veulent retravailler les chiffres.

## 10. Bonnes pratiques et limites

- **L'outil ne conclut jamais à votre place.** Il n'affiche aucun verdict et
  aucun seuil : il présente les chiffres au regard de l'objectif et de l'horizon
  du client, à qui revient l'arbitrage.
- Les **valeurs par défaut des zones** (frais, imposition) sont des valeurs de
  travail : vérifiez-les quand la situation du client est spécifique, et
  utilisez les champs de surcharge du dossier.
- La fiscalité est traitée par **taux effectif** sur le revenu locatif.
  **La plus-value de revente n'est pas imposée par l'outil** : à retraiter à la
  main pour une opération de terrain.
- Toute modification d'hypothèse **recalcule tout** : aucun chiffre affiché ne
  peut être obsolète.
