# RentImmo — Script de démonstration (≈ 10 minutes)

*Cas d'usage : deux clients aux objectifs opposés. **M. Alaoui**, chef
d'entreprise marocain, budget 1,5 M MAD, cherche un appartement locatif à
Casablanca — un revenu régulier. **Mme Benali**, profession libérale, cherche
un terrain en périphérie — une plus-value à dix ans. Le même outil doit
répondre aux deux sans les juger à la même aune.*

**Préparation** : `flask demo-data` puis connexion `demo@choubel.com` /
`demo1234`. Le compte contient les deux dossiers clients, leurs briefs, deux
biens et quatre scénarios.

---

## Séquence 1 — Le besoin avant le bien (2 min)

1. Tableau de bord : « voici mes clients et où en est chaque dossier ».
2. Ouvrir **M. Alaoui** : montrer la fiche — situation professionnelle,
   nationalité, budget disponible. « Ce sont les quatre choses que nous
   demandons systématiquement. »
3. Dérouler le **brief de recherche** : type, standing, superficie, zone,
   commodités, mode de financement.
4. Basculer le **type de bien** sur « Terrain » sous les yeux du cabinet : le
   standing et la distribution disparaissent, la viabilisation, le relief et le
   zonage apparaissent, et l'achat sur plan n'est plus proposé. « Le formulaire
   ne pose que les questions qui ont un sens pour le bien cherché. »
5. Remettre « Appartement », puis s'arrêter sur l'encart bleu :
   **objectif = revenu locatif, horizon 20 ans**.

**Message clé : nous partons de votre besoin, pas d'un bien à vendre.**

## Séquence 2 — Le coût d'entrée réel (2 min)

1. Ouvrir **« Appartement Gauthier — Casablanca »**. Montrer le bandeau
   d'avancement : le dossier en est à l'étape **Visites**.
2. Lire les tuiles : prix 1 200 000, frais 84 000 (7 %), travaux 150 000,
   **coût total 1 434 000 MAD**. Dérouler les **travaux détaillés** : « chaque
   poste est justifié, le budget est leur somme ».
3. Rendements : « le net est ce qui compte, le brut est un argument de vitrine ».

**Message clé : le vrai coût d'entrée n'est pas le prix de l'annonce.**

## Séquence 3 — L'étude automatique (2 min)

C'est le moment fort de la démonstration : **ne rien saisir, et obtenir une
réponse argumentée.**

1. Depuis le dossier : **Lancer l'étude automatique**.
2. Lire la carte de proposition **à voix haute, telle quelle** : c'est une phrase
   de français, pas un tableau. « Avec un apport de… le bien paie ses charges…
   au bout de 20 ans, l'opération lui aura rapporté… »
3. Montrer les trois registres : *pourquoi celui-ci*, *ce que les autres font
   mieux*, *ce qu'il faut vous dire avant de vous engager*. Insister sur le
   deuxième : « l'outil vous dit aussi ce que ce montage vous coûte. »
4. Dérouler **la composition détaillée** d'un montage : chaque paramètre indique
   d'où il vient. « Rien ici n'est sorti d'un chapeau. »
5. Si un montage a été écarté, lire son motif : « le comptant demandait
   1 434 000 : il manquait… »
6. **Ajuster l'étude** → horizon 5 ans, relancer : le classement change sous les
   yeux du client. « Votre horizon change la réponse, pas seulement les chiffres. »

**Message clé : l'outil ne vous vend pas un montage, il vous montre pourquoi
celui-là.**

## Séquence 3 bis — Entrer dans le montage retenu (1 min)

1. **Enregistrer ce montage comme scénario** : on arrive sur la page de résultats
   habituelle. « Ce que la machine a proposé reste modifiable ligne à ligne. »
2. Lire les deux tuiles de tête **dans cet ordre** : rendement net, puis
   cash-flow mensuel. « Votre effort d'épargne est de X MAD par mois. »
3. Graphique du **cash-flow cumulé** : montrer l'année où la courbe repasse au
   positif.

## Séquence 4 — Jouer une variante en direct (1 min)

1. **Dupliquer**, puis changer l'apport (400 000) : l'**aperçu instantané**
   recalcule cash-flow, valeur créée, TRI et VAN à chaque frappe.
2. Phrase type : « avec 100 000 d'apport en plus, votre cash-flow s'améliore,
   mais votre TRI baisse : l'effet de levier diminue ».

## Séquence 5 — Crédit, cash… ou terrain ? (3 min)

1. Cocher **Crédit 20 ans**, **Crédit 25 ans**, **Achat cash** → **Comparer**.
   Commenter dans l'ordre du tableau : rendement net, cash-flow, valeur créée,
   puis TRI et VAN.
2. Passer au dossier de **Mme Benali** — objectif *plus-value*, horizon 10 ans —
   et ouvrir **« Terrain 3 ha — périphérie »**, scénario **Portage 10 ans**.
3. Montrer que l'écran a changé de nature : **aucun rendement locatif**, la
   **valeur créée (15 000 000 MAD)** et la **plus-value** passent en tête.
4. Phrase type : « ce terrain ne rapporte rien pendant dix ans, et c'est
   pourtant lui qui crée le plus de valeur. Tout dépend de votre horizon. »

**Message clé : le bon investissement dépend de votre objectif et du temps dont
vous disposez — pas d'un seuil de rentabilité.**

## Séquence 6 — Remise du document (1 min)

**Export PDF** : « vous repartez avec l'analyse complète — votre objectif, les
hypothèses et les conventions y figurent ». Mentionner l'**export Excel**.

---

## Parades aux questions fréquentes

- **« Vos frais de 7 %, ça vient d'où ? »** → Encart de la zone Maroc :
  enregistrement 4 %, conservation foncière 1,5 %, notaire 1 %, divers 0,5 % —
  ajustables si le dossier diffère.
- **« À partir de quel rendement c'est intéressant ? »** → Il n'y a pas de
  seuil. On regarde ce que l'opération vous fait gagner sur *votre* horizon.
  C'est exactement la démonstration de la séquence 5.
- **« Et si le bien reste vide ? »** → Modifier la vacance locative devant le
  client : tout se recalcule.
- **« J'achète sur plan, quand est-ce que ça rapporte ? »** → Renseigner le
  délai de livraison : l'outil met les années de chantier en attente, sans
  loyer, alors que les mensualités courent déjà.
- **« Et l'impôt ? »** → Taux effectif de la zone sur le revenu locatif (15 % au
  Maroc), remplaçable par le taux réel. La plus-value de revente n'est pas
  imposée par l'outil : à retraiter séparément.
- **« Puis-je comparer avec un bien en France ? »** → Créer un dossier en zone
  France : frais 7,5 %, EUR, imposition 30 % appliqués automatiquement.
