# RentImmo — Script de démonstration (≈ 10 minutes)

*Cas d'usage : rendez-vous avec M. Alaoui, primo-investisseur, qui hésite entre
crédit et achat comptant pour un appartement à Casablanca.*

**Préparation (avant le rendez-vous)** : `flask demo-data` puis connexion avec
`demo@choubel.com` / `demo1234`. Le dossier « M. Alaoui » contient déjà le bien
et trois scénarios.

---

## Séquence 1 — Poser le décor (2 min)

1. Ouvrir le dossier **M. Alaoui** → projet **« Appartement Gauthier — Casablanca »**.
2. Montrer l'en-tête : zone **Maroc (MAD)** — « l'outil applique automatiquement
   les frais et la fiscalité de votre marché ».
3. Lire les cartes : prix 1 200 000, frais 84 000 (7 %), travaux 150 000,
   **coût total 1 434 000 MAD**. Dérouler la carte **Travaux détaillés** :
   « chaque poste est justifié, le budget est la somme ».
4. Conclure sur les rendements : « brut ~7 %, mais ce qui compte pour vous,
   c'est le net-net après charges et impôt ».

**Message clé : le vrai coût d'entrée n'est pas le prix affiché de l'annonce.**

## Séquence 2 — Le scénario crédit (3 min)

1. Ouvrir **« Crédit 20 ans »** (apport 300 000, taux 4,9 %, assurance 0,35 %).
2. Lire les quatre tuiles dans l'ordre : cash-flow mensuel, TRI, VAN, net-net.
   Phrase type : « votre effort d'épargne mensuel est de X MAD ; en échange,
   votre argent travaille à Y % par an, revente comprise ».
3. Graphique **cash-flow cumulé** : montrer le point où la courbe repasse au
   positif — « c'est l'année où le projet vous a remboursé votre effort ».
4. Graphique **capital restant dû** : « chaque annuité construit votre
   patrimoine, voici la dette qui fond ».

## Séquence 3 — Jouer une variante en direct (2 min)

1. Cliquer **Dupliquer**, puis dans la variante changer l'apport (p. ex.
   400 000) : l'**aperçu instantané** recalcule mensualité, cash-flow, TRI et
   VAN à chaque frappe — sans enregistrer.
2. Phrase type : « avec 100 000 d'apport en plus, votre cash-flow mensuel
   s'améliore de X, mais votre TRI baisse : l'effet de levier diminue ».
3. Enregistrer la variante si le client veut la garder, sinon quitter.

**Message clé : on teste vos hypothèses en direct, pas de retour au bureau.**

## Séquence 4 — Crédit ou cash ? (2 min)

1. Retour au projet ; cocher **Crédit 20 ans**, **Crédit 25 ans**, **Achat
   cash** → **Comparer la sélection**.
2. Tableau : montrer la ligne cash-flow (le cash est confortable) puis la ligne
   TRI (le crédit rémunère mieux chaque dirham investi).
3. Courbes superposées : commenter le croisement des trajectoires.
4. Conclusion type : « le bon choix dépend de votre priorité — revenu immédiat
   ou rendement du capital ; les chiffres sont là pour arbitrer ».

## Séquence 5 — Remise du document (1 min)

1. Ouvrir le scénario retenu → **Export PDF** : « vous repartez avec l'analyse
   complète, hypothèses et conventions incluses ».
2. Mentionner l'**export Excel** pour les clients qui veulent manipuler les
   chiffres eux-mêmes.

---

## Parades aux questions fréquentes

- **« Vos frais de 7 %, ça vient d'où ? »** → Encart de la zone Maroc :
  enregistrement 4 %, conservation foncière 1,5 %, notaire 1 %, divers 0,5 % —
  ajustables si votre dossier diffère.
- **« Et si le bien reste vide ? »** → Modifier la vacance locative devant le
  client : tout se recalcule.
- **« Et l'impôt ? »** → Taux effectif de la zone (15 % par défaut au Maroc),
  remplaçable par le taux réel du client ; l'outil ne remplace pas un conseil
  fiscal.
- **« Puis-je comparer avec un bien en France ? »** → Créer un projet en zone
  France : frais 7,5 %, EUR, imposition 30 % appliqués automatiquement.
