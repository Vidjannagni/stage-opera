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

- **type de bien** : terrain, villa, appartement, immeuble, local commercial ;
- **superficie** recherchée et **zone géographique** ;
- **commodités** souhaitées : transports, écoles, commerces… ;
- **budget** et **mode de financement** (comptant ou prêt bancaire).

**Le formulaire s'ajuste au type de bien**, et c'est le premier champ à
renseigner : les questions qui suivent en dépendent.

| Vous cherchez | On vous demande en plus | Acquisition proposée |
| --- | --- | --- |
| Appartement | **standing** (économique, moyen, haut standing), chambres, salles de bains, salons, étage, orientation | ancien, neuf, VEFA |
| Villa | **standing**, chambres, salles de bains, salons, orientation — ni étage ni ascenseur, et la superficie s'entend terrain compris | ancien, neuf, VEFA |
| Immeuble de rapport | **standing** et **nombre de lots** — pas de détail pièce par pièce | ancien, neuf |
| Local commercial | **état du local** (neuf, bon état, à rafraîchir, à rénover) au lieu du standing | local construit, local neuf, bail commercial |
| Terrain | **réseaux déjà amenés**, **relief**, **zone d'urbanisme**, **constructibilité** — ni standing ni distribution | terrain nu, terrain viabilisé, lot en lotissement |

Les commodités proposées suivent la même logique : une vitrine sur rue et un
flux piéton pour un local, un accès routier et une vue dégagée pour un terrain.

> **Ce qui n'est pas demandé n'est pas enregistré.** Si vous changez le type de
> bien après coup, les critères devenus sans objet sont effacés : un terrain ne
> conservera pas le standing saisi quand le dossier parlait encore d'un
> appartement. Mieux vaut une case vide qu'un critère que le client n'a jamais
> exprimé.

Deux réponses comptent particulièrement : l'**objectif** (revenu locatif,
plus-value, constitution de patrimoine) et l'**horizon d'investissement**.

> **Pourquoi c'est décisif.** Il n'existe pas de seuil universel de rentabilité :
> un même bien peut convenir à un client et pas à un autre. L'objectif et
> l'horizon sont la grille de lecture de tous les chiffres qui suivront ; ils
> sont rappelés en tête de chaque écran de résultats.

## 4. Créer le dossier du bien

Depuis la fiche client : **+ Nouveau dossier**. **Quatre informations suffisent**
pour lancer une étude : le nom du dossier, la zone, le prix et le loyer attendu.
Le bouton **Estimer les charges courantes** remplit le reste à partir du prix et
du loyer, en affichant la règle employée pour chaque montant ; les valeurs déjà
saisies ne sont jamais écrasées, et tout reste modifiable.

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

## 6. Lancer l'étude automatique

C'est le chemin normal, et le plus rapide : depuis le dossier, **Lancer l'étude
automatique**. Rien de plus à saisir.

L'outil construit les montages plausibles — paiement comptant, crédit à apport
minimal, à apport renforcé, ou avec tout le budget en apport, sur 15, 20 et
25 ans — les calcule, les classe **selon l'objectif et l'horizon du client**, et
propose le mieux placé. La page donne, dans l'ordre :

1. **le montage proposé**, résumé en une phrase et en quatre chiffres : apport,
   effort ou cash-flow mensuel, valeur créée à l'horizon, rendement net ;
2. **pourquoi celui-ci** — les écarts chiffrés avec le montage suivant ;
3. **ce que les autres font mieux** — dit franchement : l'achat comptant gagne
   souvent sur le cash-flow tout en rendant moins par dirham engagé ;
4. **ce qu'il faut dire au client** avant qu'il s'engage ;
5. **le classement complet**, et les montages **écartés** avec leur motif chiffré
   (« il manque 70 000 MAD ») ;
6. **la composition détaillée** de chaque montage, paramètre par paramètre, avec
   l'origine de chaque valeur.

**Ajuster l'étude** (en bas de page) rejoue la simulation avec un autre objectif,
un autre horizon, un autre budget ou un prix de revente connu — **sans modifier
la fiche du client**. C'est là qu'on répond au « et si je revendais dans cinq
ans ? » posé en séance.

Un montage retenu s'enregistre en **scénario ordinaire** : cochez-le, puis
« Enregistrer la sélection ». Il rejoint alors la page de résultats, la
comparaison et les exports, et reste modifiable champ par champ.

> **Ce que le classement n'est pas.** Un score n'est pas une note absolue : il ne
> vaut qu'à l'intérieur d'une étude, pour un client donné. La page affiche la
> pondération employée. La décision reste au client — l'outil prépare la
> conversation, il ne la remplace pas.

## 7. Construire un scénario à la main (si besoin)

**+ Scénario à la main** depuis le dossier, quand le montage est déjà connu :
taux négocié avec la banque, apport imposé, durée arrêtée. Deux modes :
**crédit** (apport, taux, assurance, durée) ou **cash**.

Les **hypothèses de projection** pilotent les indicateurs de sortie : horizon,
revalorisation du loyer et du bien, frais de revente, taux d'actualisation. Le
champ **Prix de revente à l'horizon** remplace la revalorisation annuelle quand
le prix de sortie est connu ou négocié — c'est le cas d'une opération de
construction-revente ou d'un lotissement.

La carte **Aperçu instantané** recalcule cash-flow, valeur créée, mensualité,
TRI et VAN **à chaque saisie**, avant même d'enregistrer.

## 8. Lire la page de résultats

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

## 9. Comparer les scénarios

Sur la page du dossier, cochez 2 à 4 scénarios puis **Comparer la sélection** :
tableau côte à côte (dans le même ordre de lecture) et courbes de cash-flow
cumulé superposées. Le croisement des courbes montre à partir de quelle année un
montage devient plus intéressant que l'autre.

## 10. Remettre un document au client

Depuis la page de résultats :

- **Export PDF** : rapport aux couleurs du cabinet, rappelant l'objectif du
  client, les hypothèses et les conventions de calcul ;
- **Export Excel** : feuilles *Hypothèses*, *Indicateurs*, *Projection* et
  *Amortissement*, pour les clients qui veulent retravailler les chiffres.

## 11. Bonnes pratiques et limites

- **L'outil n'applique aucun seuil de rentabilité.** Il présente les chiffres au
  regard de l'objectif et de l'horizon du client, à qui revient l'arbitrage.
- **L'étude automatique propose, elle ne tranche pas.** Elle désigne bien un
  montage de financement, mais elle affiche en même temps la pondération qui l'a
  fait choisir, ce que les autres montages font mieux, et la composition
  complète de chacun : la proposition reste discutable devant le client. Un
  classement ne vaut d'ailleurs qu'à l'intérieur d'une étude — deux études ne se
  comparent pas.
- Les **valeurs par défaut des zones** (frais, imposition) sont des valeurs de
  travail : vérifiez-les quand la situation du client est spécifique, et
  utilisez les champs de surcharge du dossier.
- La fiscalité est traitée par **taux effectif** sur le revenu locatif.
  **La plus-value de revente n'est pas imposée par l'outil** : à retraiter à la
  main pour une opération de terrain.
- Toute modification d'hypothèse **recalcule tout** : aucun chiffre affiché ne
  peut être obsolète.
