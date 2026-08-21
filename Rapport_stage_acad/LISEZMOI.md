# Rapport de stage académique — dossier de travail

Deux livrables :

| Livrable | Fichier | Produit par | Contrainte respectée |
|---|---|---|---|
| Rapport | `rapport_stage.pdf` | `rapport_stage.tex` (LaTeX) | 12 pt, interligne 1,5, justifié, paginé ; corps de texte ≈ 19 pages ; annexes |
| Soutenance | `Soutenance_stage_HOUNKPETOHOU.pptx` | `construire_presentation.py` | 16 diapositives, 16:9, pour un exposé de 10 minutes |

## Le rapport

La mise en page reprend le **gabarit des rapports hebdomadaires** remis au
cabinet (`rapports/_preambule.tex`) : même page de garde sur fond navy, mêmes
bandeaux de partie à pastille numérotée, même table des matières, mêmes en-têtes
et pieds de page. Seule la typographie du corps diffère, parce que l'école
l'impose : 12 pt, interligne 1,5, texte justifié. Les sections non numérotées
(remerciements, introduction, conclusion…) utilisent une variante du bandeau,
sans numéro et en teinte d'accent — `\mainsectionstar` au lieu de
`\mainsection`.

```bash
latexmk -pdf rapport_stage.tex
latexmk -c                       # nettoyer les fichiers intermédiaires
```

## La présentation

Le `.pptx` s'ouvre et se modifie normalement dans PowerPoint : chaque élément est
une forme native — zone de texte, rectangle, tableau, image. Aucune diapositive
n'est une image aplatie.

Le script `construire_presentation.py` sert à **régénérer** le fichier depuis
zéro si l'on veut refondre la charte d'un coup :

```bash
python3 construire_presentation.py     # écrase le .pptx
```

Toute la charte tient dans un seul bloc en tête du script (couleurs, polices,
marges, hauteur du bandeau). Changer `NAVY`, `OR`, `TITRE_POLICE` et relancer
suffit à rhabiller les seize diapositives.

**Attention :** si vous modifiez le `.pptx` à la main dans PowerPoint, ne
relancez plus le script — il écraserait vos retouches. À partir du moment où
vous prenez la main dans PowerPoint, le script devient une archive.

Pensez à exporter un PDF depuis PowerPoint avant la soutenance, en secours si
la machine de projection ne lit pas le `.pptx`.

## Avant l'envoi : renseigner les champs manquants

Tout ce qui reste à compléter apparaît **en rouge** dans le rapport comme dans
la présentation. La liste complète figure en annexe E du rapport. Les valeurs se
modifient en tête de `rapport_stage.tex` :

```latex
\newcommand{\numetudiant}{…}
\newcommand{\tuteurnom}{…}
\newcommand{\tuteurfonction}{…}
```

Pour retrouver tous les marqueurs du rapport :

```bash
grep -n "acompleter" rapport_stage.tex
```

Dans la présentation, ils se corrigent directement dans PowerPoint (texte rouge)
ou dans le script (`a_completer(...)` et le nom du tuteur sur la diapositive 1).

## Images

- `img/app_*.png` — captures de l'application RentImmo (productions du stage),
  prises sur le jeu de démonstration.
- `img/slides/` — les mêmes captures recadrées pour les diapositives : le
  haut de l'écran seulement, au format du cadre qui l'accueille.
- `img/photos/` — photographies sous licence libre ; auteurs et licences dans
  `img/photos/CREDITS.md`, rappelés sous chaque figure du rapport et sur la
  dernière diapositive.

Pour régénérer les captures après une évolution de l'application, un script s'en
charge — même jeu de données, même largeur, même définition, donc des figures
comparables d'une version à l'autre :

```bash
.venv/bin/python outils/capturer_ecrans.py     # depuis la racine du dépôt
```

Il monte l'application sur une base en mémoire, y crée le jeu de démonstration,
photographie chaque écran avec Chrome en mode « headless » (1440 points de large,
deux pixels par point), puis produit les deux jeux de recadrages : ceux du corps
du rapport (`app_etude_carte.png`, `app_resultats_haut.png`, dont les bornes sont
en pixels) et ceux des diapositives (`img/slides/`, définis par le rapport
largeur/hauteur du cadre — si la page s'allonge, le cadrage reste bon).

Les diapositives sont donc, elles aussi, régénérables : après une évolution de
l'interface, relancer le script puis `construire_presentation.py` suffit à
remettre la soutenance à jour.

## Structure du rapport

Elle suit le guide de rédaction fourni par l'école : page de garde informative,
remerciements, glossaire et abréviations, table des matières, introduction,
première partie (entreprise, secteur, mission), deuxième partie (déroulé,
difficultés, apports), conclusion, sources, annexes.

## Structure de la présentation

Elle suit la liste des points attendus : entreprise et services, fonctionnement
observé, diagnostic, périmètre d'intervention, réalisations et validation,
passation, conclusion et perspectives, bilan personnel.
