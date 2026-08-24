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

S'y ajoute **l'or du logo Choubel Consulting**. Le logo fourni par le cabinet
est or sur fond noir ; la teinte a été relevée directement sur le fichier
(`#F9CC28` en moyenne sur les pixels dorés). Elle sert d'accent de marque sur la
page d'accueil et sur le toit de l'illustration, pour que le logo ne jure pas
avec le reste de la page.

S'y ajoutent enfin deux teintes fonctionnelles, et non décoratives :

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

**Seule exception : le logo du cabinet**, qui est une image fournie par le
client et lui appartient (`app/static/img/logo-choubel.jpg`).

### L'illustration d'accueil

Elle représente une **villa posée sur sa parcelle**, en projection isométrique
avec volumes ombrés — le rendu communément appelé « 3D doux ». Chaque solide
reçoit trois tons : face éclairée, face de côté, face d'ombre. Le relief est
donc obtenu par la seule colorimétrie, sans image matricielle ni bibliothèque
3D. Le toit reprend l'or du logo.

Le sujet n'est pas choisi au hasard : la parcelle est représentée avant le bâti,
parce que les deux cas réels transmis par le mentor sont des **opérations
foncières**.

**Inspiration revendiquée.** Le style — isométrie, formes arrondies, ombres
douces, palette bois et crème — est celui d'un genre très répandu chez les
illustrateurs (*isometric house*, *clay render*). Le dessin, lui, est
entièrement original : aucune illustration existante n'a été copiée, ni
décalquée, ni téléchargée. **Un style ne se protège pas, une œuvre si** — et
reprendre le fichier d'un illustrateur identifié dans un livrable académique
aurait été une faute, indépendamment du rendu.

## 3. La page d'accueil présente le cabinet, pas l'outil

C'est la seule page visible sans compte. Elle suit donc un ordre de lecture de
site vitrine, et non d'application :

1. **Qui** — logo du cabinet, métier annoncé en une phrase, bouton d'accès ;
2. **Quoi** — bandeau des biens traités : terrains, villas, appartements,
   immeubles, de l'économique au luxe, neuf, ancien ou sur plan ;
3. **Comment** — les six étapes de l'accompagnement, du recueil du besoin à la
   livraison, telles que le cabinet les a décrites ;
4. **La règle de décision**, citée dans les mots du mentor : *« un investissement
   est bon lorsqu'il permet au client de générer de la valeur »* ;
5. **Ce que l'outil apporte** en rendez-vous, en six points ;
6. **L'invitation** à ouvrir un dossier.

Elle comporte en outre une **foire aux questions** reprenant les questions
réellement posées en rendez-vous.

Les deux dossiers réels du cabinet y ont figuré un temps, puis en ont été
retirés : publier des performances passées sur une page ouverte engage le
cabinet, et cela dépassait ce qu'on nous avait autorisé à diffuser. Ils restent
documentés dans [`retour_cabinet.md`](retour_cabinet.md) et servent de cas de
référence aux tests du moteur.

Aucun contenu n'est inventé : types de biens, étapes, citation et réponses de la
FAQ proviennent tous des réponses du cabinet consignées dans
[`retour_cabinet.md`](retour_cabinet.md).

**Les coordonnées ne sont pas inventées non plus.** Tant que le cabinet ne les
a pas fournies, la page affiche une invitation à les compléter plutôt qu'un
numéro fictif. Elles sont regroupées dans `app/cabinet.py`, renseignables par
variables d'environnement. Publier un faux numéro sur une vitrine aurait été
indéfendable dans un travail académique.

## 4. La hiérarchie visuelle traduit la hiérarchie métier

Le cabinet a indiqué regarder d'abord le **rendement net** et le **cash-flow**,
TRI et VAN ne venant qu'ensuite. Cette hiérarchie est rendue visible :

- les deux indicateurs de tête utilisent la classe `.stat-primaire` : fond plus
  clair, ombre portée, liseré de couleur, valeur en plus grand ;
- les autres utilisent `.stat-secondaire` : bordure discontinue, pas d'ombre,
  valeur plus petite.

Un lecteur qui ne connaît pas le métier voit donc immédiatement, sans lire, ce
qui compte le plus. C'est le seul rôle de cette différence de traitement.

## 5. Moins de champs à l'écran

Le mentor décrit un premier entretien où l'on note ce que le client sait dire.
Les formulaires suivent ce principe : **seuls les champs qu'on remplit devant un
client sont visibles**, le reste est replié dans un bloc « Réglages avancés ».

Trois mesures s'y sont ajoutées après le reproche fait à l'outil — « il y a trop
de choses à remplir » :

1. **Le formulaire de scénario est sorti du chemin principal.** L'étude
   automatique construit les montages ; on ne saisit plus onze valeurs pour
   découvrir qu'un montage ne convenait pas (cf.
   [`etude_automatique.md`](etude_automatique.md)).
2. **Un formulaire vierge s'ouvre vide, pas rempli de zéros.** Les champs de
   charges affichaient « 0.0 » : l'écran paraissait déjà rempli, les exemples en
   filigrane n'apparaissaient jamais, et il fallait effacer chaque zéro avant de
   saisir. Puisque le formulaire annonce que « les champs vides valent zéro »,
   afficher le vide dit la même chose en moins encombrant (`ChampMontant`).
3. **Les charges courantes s'estiment d'un clic**, à partir du prix et du loyer
   — voir la section 10.

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

### Le brief : les précisions se replient

Le bloc « distribution souhaitée » (chambres, salles de bains, salons, étage,
orientation) est désormais replié. Le cabinet cite ces critères en terminant par
« etc. » : ce sont des souhaits, pas des conditions. Le formulaire du brief tient
ainsi à l'écran sans faire défiler.

## 6. Ce qui est obligatoire, et pourquoi

Un formulaire trop permissif laisse créer des dossiers inexploitables. Les
règles retenues découlent toutes du cadrage métier :

| Champ | Obligatoire | Justification |
|---|---|---|
| Nom, situation professionnelle, nationalité, budget disponible | oui | Le cabinet les recueille **systématiquement** au premier entretien (réponse 5). La nationalité et la situation conditionnent l'accès au crédit local. |
| Standing et zone recherchée (brief) | oui | Cités parmi les critères du premier entretien (réponse 4). |
| Superficie et budget (brief) | au moins une borne | Un client dit souvent « jusqu'à tant » sans plancher : exiger la fourchette complète serait faux. |
| Loyer mensuel | oui **si** l'opération est locative | Un dossier locatif sans loyer ne produit aucun indicateur. Le message d'erreur oriente vers le type « Terrain / revente » plutôt que de bloquer. |
| Prix de revente **ou** revalorisation | oui **si** l'opération est sans loyer | Sans l'un des deux, un terrain resterait à sa valeur d'achat : le scénario n'aurait rien à montrer. |
| Chambres, salles de bains, salons, étage, orientation | non | Le cabinet les cite pour un appartement en terminant par « etc. » : ce sont des précisions, pas des conditions. Le bloc disparaît d'ailleurs pour un terrain. |

Deux principes ont guidé ces choix. **Zéro reste une valeur admise** — un budget
disponible nul est une information, pas une absence de réponse. Et **une
obligation doit toujours indiquer la sortie** : refuser un loyer vide sans dire
qu'il existe un type « terrain » serait une impasse.

Ces règles sont couvertes par `tests/test_champs_obligatoires.py`.

## 7. Des suggestions, jamais des contraintes

Plusieurs champs libres proposent désormais une liste de valeurs
(`app/suggestions.py`) : situation professionnelle, nationalité, zone
recherchée, étage, orientation, commodités, postes de travaux, noms de
scénarios. Tous les champs numériques portent en outre un exemple en filigrane
(« Ex. : 1 200 000 »).

Le choix technique est un **`<datalist>` HTML et non une liste déroulante
fermée**, et il se justifie :

- une liste fermée serait fausse dès le premier cas particulier — une
  nationalité absente, un quartier non répertorié — et bloquerait le conseiller
  en plein rendez-vous ;
- une liste ouverte accélère la saisie sans rien interdire ;
- elle **homogénéise le vocabulaire** entre conseillers, ce qui rend les
  dossiers comparables — c'est le vrai bénéfice, au-delà du gain de frappe.

Restent en liste fermée (`SelectField`) les seules valeurs qui alimentent les
calculs ou les filtres : type de bien, standing, type d'acquisition, mode de
financement, objectif, type d'opération, étape du dossier, mode de financement
du scénario. Leur ensemble est arrêté, donc les fermer est légitime.

Les commodités disposent en plus de **puces cliquables** qui ajoutent ou
retirent une valeur du champ libre : c'est le seul champ où le cabinet a cité
une énumération (« transports, écoles, commerces »), et où l'on coche
naturellement plusieurs entrées. Les réseaux d'un terrain, ajoutés ensuite,
reprennent le même mécanisme.

## 7 bis. Un formulaire qui suit le bien recherché

Le brief sert pour un terrain comme pour un appartement, un immeuble de rapport
ou un local commercial. Les questions, elles, ne se recouvrent pas : le standing
ne veut rien dire pour un terrain, la VEFA n'existe pas sur un terrain nu, un
local se juge sur son état et son passage.

Laisser toutes les questions à l'écran aurait un coût précis : **une question
sans objet se remplit au hasard**, et un critère inventé oriente ensuite une
recherche pour rien. Le formulaire masque donc ce qui ne s'applique pas, adapte
les libellés (superficie *habitable*, *utile* ou *du terrain*) et les puces de
commodités, et propose les seuls modes d'acquisition qui existent pour ce bien.

**Trois niveaux de standing, et non cinq.** Le cabinet en citait cinq
(économique, social, moyen standing, haut standing, luxe). Les deux extrêmes se
plaidaient toujours par rapport aux trois autres, sans critère qui les sépare :
les garder revenait surtout à s'assurer que deux conseillers classent le même
bien différemment, et rendait les dossiers moins comparables — l'inverse du but
poursuivi. Les briefs déjà saisis sont rapatriés vers le niveau voisin par la
migration, plutôt que vidés.

Trois précautions :

1. **Une seule table décide** (`app/core/profil_bien.py`). Le formulaire, la
   page et la fiche client la lisent ; elles ne peuvent donc pas diverger, et
   ajouter un type de bien tient en une entrée.
2. **Le serveur applique la même règle que l'écran.** Masquer un champ ne prouve
   rien : un formulaire soumis sans JavaScript passe par `appliquer_type`, qui
   n'exige, ne valide et n'enregistre que les champs qui s'appliquent.
3. **Ce qui n'est plus demandé est effacé.** Un brief passé d'appartement à
   terrain garderait sinon un standing que plus personne n'a saisi, et que la
   fiche client afficherait comme un critère du client.

Ces règles sont couvertes par `tests/test_champs_par_type.py`.

## 7 ter. Le brief et le dossier, et le lien qui manquait

Deux objets se répondent dans l'outil, et rien ne les distinguait à l'écran :

| | Brief | Dossier (projet) |
| --- | --- | --- |
| Dit quoi | ce que le client **cherche** | ce qu'on lui **propose** |
| Contenu | fourchettes, objectif, horizon | prix, travaux, loyer d'**un bien** |
| Combien | un par client | autant que de biens étudiés |
| Calculs | aucun | rendements, cash-flow, VAN, TRI |

Faute de lien entre les deux, on pouvait chiffrer un 45 m² à deux millions pour
un client venu chercher 70 m² à un million et demi sans que rien ne le signale,
et le formulaire du dossier redemandait ce que le brief savait déjà. Trois
changements en découlent.

**Le brief est rappelé là où on chiffre.** La page du dossier et son formulaire
affichent « ce que le client cherche » à côté du bien étudié. Ce qui est déjà
connu sert de valeur de départ — nom du dossier, localisation, type d'opération
— et les fourchettes apparaissent en filigrane des champs concernés.

**Le formulaire suit l'étape du dossier.** Tant qu'on en est à la *recherche*,
aucun bien n'est arrêté : demander son adresse et sa superficie n'a pas de sens,
et le prix saisi est annoncé comme une hypothèse de travail. Les deux champs
apparaissent dès la *présentation au client*. À la différence du brief, **rien
n'est effacé** : un champ n'y est pas *sans objet*, il est *pas encore connu*,
et une superficie saisie hier reste vraie demain.

**Les écarts sont nommés, jamais bloqués** (`app/core/coherence.py`). Superficie
hors fourchette, coût d'entrée hors budget, dossier sans loyer pour un client
venu chercher un revenu, achat sur plan sans délai : chacun donne une phrase,
affichée sur la page du dossier et à l'enregistrement. Le rapprochement se fait
sur l'**objectif** du client, jamais sur le type de bien : un appartement acheté
pour être revendu se chiffre légitimement sans loyer, et un contrôle qui
comparerait « appartement recherché » à « opération de revente » crierait au
loup sur un dossier cohérent. Un avertissement qui se déclenche à tort est pire
qu'absent : on cesse de le lire. C'est la même doctrine que partout
ailleurs dans l'outil — **il documente une décision, il ne la prend pas** :
proposer autre chose que ce qui a été demandé est un acte de conseil, mais il
doit être dit par le conseiller plutôt que découvert par le client.

Le budget se compare au **coût d'entrée** (prix + frais + travaux), pas au prix
affiché : c'est ce que le client sort de sa poche, et un bien « dans le budget »
qui en sort dès qu'on ajoute 7 % de frais n'y est pas.

Ces règles sont couvertes par `tests/test_brief_et_dossier.py`.

## 8. Accessibilité et lisibilité

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

## 9. Ce qui a été volontairement écarté

- **Photographies de biens** : l'outil est un support de calcul, pas une vitrine
  d'annonces. Une photo de bien n'apporterait rien à la décision et poserait un
  problème de droits ; l'illustration dessinée joue le même rôle d'accroche sans
  cet inconvénient.
- **Polices externes** : dépendance réseau inutile ; la pile de polices système
  rend bien sur tous les postes et évite un chargement supplémentaire.
- **Animations** : hors un léger relief au survol des cartes de présentation,
  aucune animation. En rendez-vous, le mouvement détourne l'attention des
  chiffres.
- **Mode sombre** : l'outil est projeté ou imprimé, deux contextes où le fond
  clair est préférable. L'ajouter aurait doublé le travail de contraste sans
  bénéfice pour l'usage visé.

## 10. L'estimation des charges : proposer sans décider

Un conseiller connaît toujours le prix et le loyer ; devant un client, il connaît
rarement le montant exact du syndic, de la taxe ou de l'assurance. Ces champs
restaient donc à zéro — ce qui **gonfle artificiellement le rendement net**.

Le bouton « Estimer les charges courantes » applique des règles calibrées sur le
marché marocain (`app/core/estimation.py`), toutes affichées après le clic :

| Champ | Règle | Pourquoi celle-là |
|---|---|---|
| Charges de copropriété | 8 % du loyer annuel | Ordre de grandeur d'un syndic de moyen standing. |
| Taxe annuelle | 10,5 % du loyer annuel | Taux de la taxe de services communaux sur la valeur locative, en zone urbaine. |
| Assurance | 0,15 % du prix | Multirisque habitation d'un propriétaire non occupant. |
| Entretien | 0,5 % du prix et par an | Provision d'usage pour l'entretien courant. |
| Frais de gestion | 5 % du loyer | Tarif courant d'une agence de gestion locative. |
| Vacance locative | 5 % du loyer | Environ trois semaines de vide par an. |

Trois précautions, sans lesquelles une estimation serait malhonnête :

- **rien n'est estimé en silence** : l'action est explicite, les champs remplis
  sont visibles, et la règle employée est affichée sous le bouton ;
- **une valeur saisie n'est jamais écrasée**, y compris un zéro — « pas de frais
  de gestion » est une information, pas une case oubliée ;
- **les montants sont arrondis à la centaine** : afficher « 8 160 » donnerait à
  une estimation une précision qu'elle n'a pas.

Les coefficients vivent côté serveur et sont transmis au navigateur : l'interface
et le moteur ne peuvent pas diverger.

## 11. La page d'étude se lit comme une réponse

L'écran de proposition rompt volontairement avec la grille des autres pages : une
**carte détachée**, un liseré d'accent, une phrase en grand caractère, puis les
chiffres qui l'appuient. C'est le seul écran de l'application qui affirme quelque
chose ; il devait se distinguer d'un tableau de bord.

Trois registres y sont séparés, chacun avec sa propre puce — un « + » pour les
avantages, un tiret pour ce que les autres montages font mieux, un « ! » pour les
points de vigilance. La distinction ne repose donc pas sur la couleur seule, et
survit à une impression en noir et blanc. Le classement complet, bien qu'il vive
dans un formulaire (cases à cocher), reste imprimé : c'est la page que l'on remet
au client.

## 12. Le document remis au client

Le rapport PDF exporté par l'application est composé **comme les rapports du
projet**, et non comme une page web imprimée. Les correspondances sont
littérales :

| Élément du gabarit LaTeX | Transposition dans le PDF |
|---|---|
| Page de garde sur fond navy, pastille de titre, sous-titre en teinte d'accent | Bandeau de tête du document, mêmes couleurs, mêmes étiquettes en capitales |
| Bandeau de partie : pastille numérotée, barre bleue, titre centré en italique | Reproduit en CSS, section par section |
| Tableaux entièrement quadrillés, en-tête sur fond bleu, lignes alternées | `table.grille` : filets sur **toutes** les lignes, en-tête `#dbe7f1`, alternance blanc / gris |
| Police à empattements (Computer Modern) | Pile `Latin Modern Roman`, puis Nimbus Roman, Liberation Serif, Times |
| Pied de page : auteur, numéro de page en bleu, cabinet | Identique, via les marges nommées de `@page` |

Trois exigences de lisibilité s'y ajoutent, qui ne viennent pas du gabarit mais
de l'usage :

- **les en-têtes de colonnes se répètent** quand un tableau se coupe entre deux
  pages (`<thead>`) — une colonne de chiffres sans intitulé, en haut d'une page,
  ne se lit pas ;
- **les montants sont alignés au chiffre près** (`tabular-nums`) et jamais
  coupés en fin de ligne ;
- **le texte est justifié avec un retrait d'alinéa**, comme dans les rapports,
  et les blocs de conventions restent en fer à gauche pour se distinguer du
  corps.

La mise en page n'utilise ni *flexbox* ni grille CSS : uniquement des tableaux
et des blocs, les modèles les mieux supportés par WeasyPrint. Un export remis à
un client ne doit jamais casser.
