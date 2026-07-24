# RentImmo — Guide d'utilisation

*Outil d'analyse de rentabilité d'investissement immobilier — Choubel Consulting.*
Ce guide s'adresse au **conseiller** ; il suit l'ordre d'un rendez-vous client réel.

---

## 1. Démarrage et connexion

Lancez l'application (voir le README pour l'installation) puis ouvrez
`http://127.0.0.1:5000`. Créez votre compte consultant (« Créer un compte ») ou
connectez-vous. **Chaque conseiller ne voit que ses propres dossiers** : vos
clients ne sont jamais visibles par un autre compte.

> Pour vous entraîner : `flask demo-data` crée un dossier complet
> (connexion `demo@choubel.com` / `demo1234`).

## 2. Créer le dossier client

**Clients → Nouveau dossier.** Seul le nom est obligatoire ; e-mail, téléphone
et notes sont là pour votre suivi. Le dossier regroupera tous les biens étudiés
pour ce client.

## 3. Saisir le bien (projet)

Depuis le dossier client : **+ Nouveau projet**.

- **Zone de marché** : c'est le réglage central. Le **Maroc** est présélectionné
  (devise MAD) ; la France et une zone personnalisée sont disponibles. L'encart
  bleu sous le sélecteur rappelle les taux appliqués — frais d'acquisition et
  imposition — et **tous les calculs s'actualisent selon la zone choisie**.
- **Acquisition** : prix du bien et budget travaux. Le champ « taux de frais »
  ne se remplit que pour déroger au taux de la zone (laissez-le vide sinon).
- **Exploitation** : loyer mensuel attendu, charges annuelles (copropriété,
  assurance, entretien, taxe), frais de gestion et vacance locative en % du
  loyer. En rendez-vous, ne remplissez que ce que vous connaissez : les champs
  vides valent zéro.

La page du projet affiche immédiatement le **coût total d'acquisition** et les
**trois rendements** (brut, net, net-net), utilisables tels quels face au client :

- *brut* = loyers annuels / coût total d'acquisition ;
- *net* = idem après charges, vacance et gestion ;
- *net-net* = idem après impôt au taux effectif de la zone.

## 4. Détailler les travaux (facultatif)

Sur la page du projet, la carte **Travaux détaillés** permet de chiffrer poste
par poste (catégorie + montant). Dès qu'un poste existe, **le budget travaux du
projet devient la somme des postes** — utile pour justifier le chiffre devant
le client. Supprimer un poste réajuste le budget.

## 5. Construire les scénarios de financement

**+ Nouveau scénario** depuis le projet. Deux modes :

- **Crédit** : apport, taux d'intérêt, taux d'assurance, durée ;
- **Cash** : achat comptant, aucun emprunt.

Les **hypothèses de projection** (horizon, revalorisation du loyer et du bien,
frais de revente, taux d'actualisation) pilotent le TRI et la VAN.

La carte **Aperçu instantané** recalcule mensualité, cash-flow, TRI et VAN
**à chaque saisie** : faites varier l'apport ou la durée en direct devant le
client avant même d'enregistrer.

## 6. Lire la page de résultats

Quatre indicateurs en tête de page :

| Indicateur | Lecture en une phrase |
|---|---|
| **Cash-flow mensuel** | Ce que le client débourse (rouge) ou encaisse (vert) chaque mois, tout compris. |
| **TRI** | Le taux de rendement annuel de l'argent réellement investi, revente incluse. |
| **VAN** | Ce que le projet rapporte en plus d'un placement au taux d'actualisation ; positive = créateur de valeur. |
| **Rendement net-net** | Le rendement du bien après charges et impôt. |

Suivent le détail chiffré (acquisition, financement, exploitation) et trois
graphiques : cash-flow annuel et cumulé, capital restant dû, décomposition du
coût d'acquisition. Le tableau de projection donne l'année par année.

**Dupliquer** crée une variante du scénario pour tester une autre hypothèse
sans perdre l'original.

## 7. Comparer les scénarios

Sur la page du projet, cochez 2 à 4 scénarios puis **Comparer la sélection** :
tableau d'indicateurs côte à côte et courbes de cash-flow cumulé superposées.
C'est l'écran de décision : le croisement des courbes montre à partir de quelle
année un montage devient plus intéressant que l'autre.

## 8. Remettre un document au client

Depuis la page de résultats d'un scénario :

- **Export PDF** : rapport complet aux couleurs du cabinet, prêt à imprimer ou
  envoyer — hypothèses, conventions de calcul et projection incluses.
- **Export Excel** : classeur avec feuilles *Hypothèses*, *Indicateurs*,
  *Projection* et *Amortissement* mensuel, pour les clients qui veulent
  retravailler les chiffres.

## 9. Bonnes pratiques et limites

- Les **valeurs par défaut des zones** (frais, imposition) sont des valeurs de
  travail : vérifiez-les avec le client quand sa situation est spécifique, et
  utilisez les champs de surcharge du projet le cas échéant.
- La fiscalité est traitée par **taux effectif** : l'outil ne modélise pas les
  régimes fiscaux détaillés ni ne remplace un conseil fiscal.
- Toute modification d'hypothèse **recalcule tout** : aucun chiffre affiché ne
  peut être obsolète.
- Le rapport PDF rappelle explicitement les conventions — appuyez-vous dessus
  si le client conteste un chiffre.
