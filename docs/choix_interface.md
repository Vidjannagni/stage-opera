# Choix d'interface — justification

Ce document existe pour une raison précise : chaque élément visuel de
l'application doit pouvoir être expliqué. Rien n'a été ajouté « parce que c'est
joli ».

---

## 1. La palette vient du cabinet, elle n'est pas inventée

Les documents LaTeX du projet (`feuille_de_route.tex`, `rapports/_preambule.tex`)
définissent déjà trois couleurs :

```latex
\definecolor{eccblue}{RGB}{0,82,145}
\definecolor{navy}{RGB}{12,25,48}
\definecolor{accent}{RGB}{0,188,170}
```

Ce sont exactement les variables `--ecc-blue`, `--ecc-navy` et `--ecc-accent` de
`app/static/css/custom.css`. **L'application et les rapports remis au cabinet
partagent donc la même charte**, ce qui est l'argument principal : la cohérence
entre le logiciel et les livrables papier n'est pas un hasard.

S'y ajoutent seulement deux teintes fonctionnelles, et non décoratives :

| Couleur | Usage | Pourquoi |
|---|---|---|
| Vert `#157347` | Cash-flow, VAN, valeur créée **positifs** | Lecture immédiate du signe devant un client |
| Rouge `#b02a37` | Les mêmes, **négatifs** | Idem |

Le signe n'est jamais porté par la seule couleur : le montant est écrit avec son
signe, ce qui reste lisible pour une personne daltonienne ou sur une impression
en noir et blanc.

## 2. Aucune image externe

Toutes les illustrations et tous les pictogrammes sont des **SVG écrits à la
main** dans `app/templates/_illustrations.html`. Aucune photographie, aucune
banque d'images, aucune police téléchargée.

Quatre raisons, dans l'ordre d'importance :

1. **Aucune question de licence** — un rapport académique n'a pas à justifier
   les droits d'une photo trouvée en ligne.
2. **Rien ne casse en démonstration** — pas de requête réseau, donc pas d'image
   manquante si la connexion est mauvaise le jour de la soutenance.
3. **Poids négligeable** — quelques kilo-octets de balisage au lieu de plusieurs
   centaines de kilo-octets d'images.
4. **La charte est respectée automatiquement** — les SVG héritent des couleurs
   CSS, donc un changement de palette se propage sans retoucher d'image.

L'illustration d'accueil n'est pas décorative non plus : elle représente un
terrain, des immeubles de hauteur croissante et une courbe de valorisation —
c'est-à-dire les trois objets du métier du cabinet, dont le terrain, que les cas
réels transmis par le mentor ont placé au premier plan.

## 3. La hiérarchie visuelle traduit la hiérarchie métier

Le cabinet a indiqué regarder d'abord le **rendement net** et le **cash-flow**,
TRI et VAN ne venant qu'ensuite. Cette hiérarchie est rendue visible :

- les deux indicateurs de tête utilisent la classe `.stat-primaire` : fond plus
  clair, ombre portée, liseré de couleur, valeur en plus grand ;
- les autres utilisent `.stat-secondaire` : bordure discontinue, pas d'ombre,
  valeur plus petite.

Un lecteur qui ne connaît pas le métier voit donc immédiatement, sans lire, ce
qui compte le plus. C'est le seul rôle de cette différence de traitement.

## 4. Moins de champs à l'écran

Le mentor décrit un premier entretien où l'on note ce que le client sait dire.
Les formulaires suivent ce principe : **seuls les champs qu'on remplit devant un
client sont visibles**, le reste est replié dans un bloc « Réglages avancés ».

| Formulaire | Visible par défaut | Replié |
|---|---|---|
| Dossier | Bien, zone, étape, prix, travaux, délai de livraison, loyer, charges de copropriété, taxe, gestion, vacance | Surcharges de taux de la zone, assurance, entretien |
| Scénario | Mode, apport, taux d'intérêt, durée, horizon, revalorisations, prix de revente | Taux d'assurance, frais de revente, taux d'actualisation |

Le critère de tri est simple et défendable : **un réglage est replié si sa valeur
par défaut convient dans la très grande majorité des cas** — les taux de frais et
d'imposition viennent déjà de la zone de marché, et le taux d'actualisation
n'influe que sur la VAN, indicateur de second rang.

Rien n'a été supprimé : tous les champs restent accessibles en un clic, et le
moteur de calcul est inchangé.

## 5. Accessibilité et lisibilité

- **Chiffres alignés** : `font-variant-numeric: tabular-nums` sur toutes les
  colonnes de montants, pour que les ordres de grandeur se comparent à l'œil.
- **Graphiques doublés d'un tableau** : chaque figure a son équivalent chiffré
  sur la même page, et un `aria-label` qui y renvoie.
- **Contraste** : texte principal `#16202f` sur blanc, texte secondaire
  `#5b6875` — au-dessus du seuil AA dans les deux cas.
- **Étapes du dossier** : l'étape courante porte `aria-current="step"`, les
  étapes franchies sont marquées d'une coche en plus de la couleur.
- **Impression** : une feuille de style dédiée retire navigation, boutons et
  formulaires, pour qu'une page imprimée reste exploitable.

## 6. Ce qui a été volontairement écarté

- **Photographies de biens** : l'outil est un support de calcul, pas une vitrine
  d'annonces. Une photo n'apporterait rien à la décision et poserait un problème
  de droits.
- **Polices externes** : dépendance réseau inutile ; la pile de polices système
  rend bien sur tous les postes et évite un chargement supplémentaire.
- **Animations** : hors un léger relief au survol des cartes de présentation,
  aucune animation. En rendez-vous, le mouvement détourne l'attention des
  chiffres.
- **Mode sombre** : l'outil est projeté ou imprimé, deux contextes où le fond
  clair est préférable. L'ajouter aurait doublé le travail de contraste sans
  bénéfice pour l'usage visé.
