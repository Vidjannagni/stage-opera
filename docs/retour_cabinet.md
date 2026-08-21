# Retour du cabinet et adaptation de l'outil

*Entretien de cadrage métier avec Choubel Consulting — août 2026.*

Ce document consigne les réponses du cabinet à nos questions sur sa méthode de
travail, les écarts constatés avec notre cahier des charges initial, et les
modifications apportées à l'application.

---

## 1. Ce que le cabinet nous a répondu

### Indicateurs réellement utilisés (questions 1 et 2)

> « Les deux critères les plus récurrents sont le **rendement net** et le
> **cash-flow** que le bien peut générer par la suite. Viennent ensuite les
> autres éléments cités. »

Le TRI, la VAN et le rendement brut sont donc des indicateurs **secondaires**,
utiles pour argumenter mais pas pour décider.

### Seuils et règles métier (question 3)

> « Oui et non. C'est assez complexe, car au final, c'est souvent le client qui
> a le dernier mot. […] Un investissement peut être rentable pour une personne
> et ne pas l'être pour une autre. »

**Il n'existe pas de seuil de rentabilité.** La conclusion du cabinet :

> « Un investissement est considéré comme bon lorsqu'il permet au client de
> générer de la valeur. Tout dépend donc de son **horizon d'investissement** et
> du **facteur temps**. »

### Les deux cas de référence (questions 3 et 7)

| | Client 1 — portage foncier | Client 2 — construction-revente |
|---|---|---|
| Budget | 1 M MAD | ~1 M MAD |
| Bien | Terrain de 3 ha, zone ciblée | Terrain viabilisé 500 m² à 1,1 M |
| Opération | Conservé, sans mise en valeur | Immeuble R+4, 20 appartements, revendus |
| Horizon | 10 ans | 2 ans |
| Résultat | Projet d'État à 1 km 4 ans plus tard ; morcellement et revente de 2 ha → **~15 M de bénéfice**, 1 ha conservé en réserve | **5 M de plus-value nette** |

À la sortie du client 2, celui-ci semble avoir fait la meilleure opération. Sur
l'horizon du client 1, le classement s'inverse. **Aucun des deux dossiers ne
comporte de loyer.**

### Déroulement d'un rendez-vous (questions 4 et 6)

Informations recueillies au premier entretien : type de bien (terrain, villa,
appartement, immeuble), niveau de standing (économique, social, moyen standing,
haut standing, luxe), distribution pour un appartement (chambres, salles de
bains, salons, étage, orientation), superficie, commodités souhaitées
(transports, écoles, commerces), type d'acquisition (VEFA ou bien déjà
construit), zone géographique, budget prévu, mode de financement (comptant ou
prêt bancaire).

Puis : recherche → présentation des biens → visites → signature du compromis →
acte notarié → livraison du bien.

Le cabinet précise que les critères qualitatifs de la question 6 **sont** ces
critères de recherche.

### Informations systématiquement recueillies (question 5)

Nom du client, situation professionnelle, nationalité, budget disponible.

---

## 2. Écarts constatés avec notre cahier des charges

| # | Écart | Portée |
|---|---|---|
| 1 | Notre page de résultats mettait **TRI et VAN en tête**, le cabinet regarde d'abord rendement net et cash-flow | Restitution |
| 2 | Notre modèle supposait **toujours un loyer** ; les deux cas de référence n'en ont aucun | Moteur de calcul |
| 3 | Le **facteur temps** (horizon, délai de livraison) n'était pas un paramètre de premier plan | Moteur et restitution |
| 4 | La **phase amont** (recueil du besoin, recherche) était absente : on partait d'un bien déjà identifié | Modèle de données |
| 5 | La **fiche client** ignorait situation professionnelle, nationalité et budget disponible | Modèle de données |
| 6 | Le **déroulé du dossier** (compromis, notaire, livraison) n'était pas suivi | Modèle de données |
| 7 | L'achat **sur plan (VEFA)** était traité comme un bien immédiatement louable | Moteur de calcul |

---

## 3. Modifications apportées

### Modèle de données

- **Fiche client** : ajout de la situation professionnelle, de la nationalité et
  du budget disponible.
- **Brief de recherche** (nouveau) : tous les critères du premier entretien, plus
  l'**objectif** du client (revenu locatif, plus-value, patrimoine) et son
  **horizon d'investissement**.
- **Dossier** : type d'opération (`locatif` ou `terrain / revente`), étape du
  dossier (recherche → présentation → visites → compromis → notaire →
  livraison), délai de livraison en mois.
- **Scénario** : prix de revente saisissable, pour une opération dont le prix de
  sortie est connu ou négocié plutôt que déduit d'une revalorisation annuelle.

### Moteur de calcul

- Une opération **sans loyer** est traitée nativement : toute la valeur vient de
  la plus-value.
- Le **délai de livraison** diffère la mise en exploitation : tant que le bien
  n'est pas livré il ne produit ni loyer ni charges, alors que les annuités
  d'emprunt courent déjà. Une livraison en cours d'année est proratisée.
- Le cash-flow mis en avant est celui d'une **année pleinement exploitée**, pas
  celui de l'année 1 qui ne représente rien pour un bien encore en chantier.
- Nouveaux résultats explicites : valeur du bien à l'horizon, **plus-value
  brute**, encaissé à la revente, et **valeur créée** sur l'horizon.

### Restitution

- **Ordre des indicateurs inversé** : rendement net et cash-flow en tête,
  valeur créée ensuite, TRI et VAN en second rang. Même ordre sur la page de
  résultats, l'aperçu instantané, l'écran de comparaison, le rapport PDF et le
  classeur Excel.
- **Aucun seuil universel.** L'objectif et l'horizon du client sont rappelés à
  côté des chiffres ; l'arbitrage reste au client, conformément à la réponse 3.

  *Évolution ultérieure.* L'outil **propose** désormais un montage, via l'étude
  automatique — mais sans jamais introduire de seuil : le classement est calculé
  **relativement à l'objectif déclaré du client**, entre montages portant sur le
  même bien et le même horizon ; la pondération employée est affichée ; ce que
  les autres montages font mieux est dit explicitement ; et les montages écartés
  le sont avec leur motif chiffré. La réponse 3 est ainsi respectée dans son
  fond — « tout dépend de son horizon et du facteur temps » — tout en évitant au
  conseiller d'avoir à deviner quel montage essayer.
  Méthode complète : [`etude_automatique.md`](etude_automatique.md).
- Les écrans s'adaptent au type d'opération : pas de rendement locatif affiché
  pour un terrain, plus-value mise en avant à la place.

### Validation

Les deux cas de référence du cabinet sont désormais des **tests automatisés**
(`tests/test_cas_mentor.py`), vérifiables à la main :

- client 1 : 1 000 000 + 7 % de frais = 1 070 000 investis, revente à 16 070 000
  → **15 000 000 de valeur créée**, TRI ≈ 31 %/an ;
- client 2 : 1 100 000 + 7 % + 8 000 000 de construction = 9 177 000, revente à
  14 177 000 → **5 000 000 de valeur créée** ;
- un test dédié vérifie que le **classement des deux dossiers s'inverse avec
  l'horizon**, ce qui est la conclusion métier du cabinet.

---

## 4. Points restés hors périmètre

Signalés comme utiles mais non implémentés, faute de temps avant la remise :

- **Échéancier VEFA par tranches** : les appels de fonds suivent l'avancement du
  chantier. Nous modélisons le décalage de livraison, pas l'étalement des
  paiements.
- **Calcul de capacité d'emprunt** à partir de la situation professionnelle et du
  budget disponible. L'étude automatique filtre sur l'**apport** (budget déclaré),
  pas sur le taux d'endettement : nous ne collectons pas les revenus du client.
- **Moteur de rapprochement** entre le brief d'un client et un portefeuille de
  biens : l'outil enregistre le besoin, il ne cherche pas encore les biens.
- **Suivi des visites** (dates, retours du client) au sein de l'étape « visites ».

---

## 5. Question restée ouverte

Le cabinet n'a pas commenté le cahier des charges lui-même (question 8). Nous
recommandons de lui soumettre la présente note et la version révisée de
l'application avant validation définitive, en particulier sur deux points :

1. les **valeurs par défaut des zones de marché** (Maroc : frais 7 %, imposition
   effective 15 %) — toujours en attente de validation formelle ;
2. le **traitement fiscal de la plus-value** à la revente, que l'outil n'impose
   pas aujourd'hui : seul le revenu locatif l'est. Pour des opérations de
   terrain, c'est un écart à trancher avec le cabinet.
