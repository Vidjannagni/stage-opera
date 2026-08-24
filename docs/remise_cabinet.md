# RentImmo — document de remise

*À l'attention de Choubel Consulting. Ce document accompagne la mise à
disposition de l'outil ; il ne suppose aucune connaissance technique.*

---

## 1. Ce que fait l'outil

RentImmo est une application web : elle s'ouvre dans un navigateur, à une
adresse, sans rien installer. Elle sert à **chiffrer un investissement
immobilier avant de le présenter à un client**, et à conserver la trace de ce
qui a été chiffré.

Elle suit le déroulé du cabinet, du premier entretien à la livraison :

1. la **fiche client** et son **brief de recherche** — ce que le client
   cherche, son objectif et son horizon ;
2. le **dossier d'un bien** — prix, frais, travaux, loyer attendu ;
3. l'**étude automatique** — l'outil construit les montages de financement
   possibles, les confronte, et propose le mieux placé **au regard de
   l'objectif du client** ;
4. les **documents à remettre** — export Excel et PDF.

**Ce qu'elle ne fait pas, délibérément.** Elle n'applique aucun seuil de
rentabilité. Un même bien peut convenir à un client et pas à un autre : c'est
l'objectif et l'horizon déclarés qui servent de grille de lecture, et ils sont
rappelés à côté de chaque chiffre. L'outil documente une décision, il ne la
prend pas.

---

## 2. Y accéder

| | |
|---|---|
| **Adresse** | *(à compléter le jour de la mise en ligne)* |
| **Créer un compte** | *Créer un compte consultant*, avec le **code d'inscription** communiqué séparément |
| **Un compte par conseiller** | chacun ne voit que ses propres dossiers |

Le code d'inscription est ce qui empêche un inconnu de créer un compte sur
l'adresse. **Il se transmet de la main à la main, jamais par un message
public.** S'il circule trop, demandez-en un nouveau.

### Mot de passe oublié

L'outil **n'envoie pas de courriel** : il n'y a pas de lien « mot de passe
oublié ». Demandez un mot de passe provisoire à l'administrateur de l'outil,
puis changez-le vous-même depuis **Mon compte** (votre nom, en haut à droite).
Personne d'autre que vous ne doit connaître votre mot de passe définitif.

---

## 3. Prendre l'outil en main

Le **guide d'utilisation** (`docs/guide_utilisation.md`) déroule les écrans un
par un. Trois points suffisent pour commencer :

- **Le brief avant le bien.** Les indicateurs ne veulent rien dire sans
  l'objectif et l'horizon du client : renseignez le brief en premier.
- **Quatre informations suffisent** pour lancer une étude sur un bien : la
  zone, le prix, le loyer attendu, un nom de dossier. Le reste s'estime d'un
  clic, et chaque estimation affiche la règle employée.
- **Rien n'est écrasé sans vous.** Une valeur que vous avez saisie — même un
  zéro — fait toujours foi sur une valeur estimée.

---

## 4. Les données que vous y mettez

Dès que vous saisissez de vrais clients, l'outil contient des **données
personnelles** : noms, coordonnées, situation professionnelle, budget.

- **N'y mettez que le nécessaire.** Un dossier se chiffre sans numéro de pièce
  d'identité ni relevé bancaire.
- **Les dossiers sont cloisonnés** : chaque conseiller ne voit que les siens.
  Ce n'est pas un affichage, c'est vérifié à chaque requête.
- **Les mots de passe ne sont jamais stockés en clair**, les échanges passent
  par une connexion chiffrée (HTTPS), et l'outil demande explicitement aux
  moteurs de recherche de ne pas l'indexer.

---

## 5. Ce que vous devez savoir sur l'hébergement

**L'application est hébergée sur un compte personnel d'étudiant, sur une offre
gratuite.** C'est ce qui permet de vous la remettre sans frais ni engagement,
mais cela emporte trois conséquences qu'il vaut mieux connaître avant d'y
saisir des dossiers réels :

1. **Ce n'est pas un service contractuel.** Aucune garantie de disponibilité,
   aucun engagement de délai en cas de panne. C'est le prolongement d'un projet
   d'étude, pas une prestation.
2. **L'application dépend d'un compte qui n'est pas le vôtre.** Le compte
   gratuit doit être réactivé tous les trois mois en s'y connectant ; faute de
   quoi l'application est désactivée.
3. **Aucune sauvegarde n'est automatique.** Elles sont faites à la main, à la
   demande (voir ci-dessous).

**L'adresse porte le nom de l'hébergeur** — `…pythonanywhere.com` — parce qu'un
nom de domaine à vous suppose un hébergement payant. C'est la première chose
qui change le jour où le cabinet reprend la main.

**Si l'outil vous devient utile au quotidien, il faut le rapatrier chez vous.**
La procédure est écrite (`docs/deploiement.md`) : le cabinet ouvre son propre
compte d'hébergement — payant, quelques euros par mois, ce qui apporte une
adresse à votre nom et supprime l'incertitude — ou installe l'application sur
un poste du bureau, sans que rien ne sorte de vos locaux. La base de données
lui est transférée. Comptez une demi-journée. Le code vous appartient : il est
intégralement fourni, sans dépendance à un prestataire.

### Sauvegardes

Demandez une **copie de la base** à l'administrateur de l'outil :

- avant toute mise à jour ;
- à intervalle régulier — au minimum une fois par mois — dès que de vrais
  dossiers y sont saisis.

Conservez ces copies **ailleurs que sur l'hébergement**. Une sauvegarde qui
vit au même endroit que l'original ne protège de rien.

---

## 6. Limites connues

- **L'export PDF peut ne pas fonctionner en ligne** : il dépend de
  bibliothèques que l'hébergement gratuit ne fournit pas toujours. L'export
  Excel, lui, fonctionne dans tous les cas.
- **Serveur partagé** : les temps de réponse dépendent de la charge des autres
  applications hébergées. Ouvrez l'outil quelques minutes avant un rendez-vous
  client plutôt que devant lui.
- **Quelques conseillers à la fois**, pas des dizaines.
- **Les taux par défaut** — frais d'acquisition, imposition, revalorisation —
  sont ceux qui ont été retenus avec vous à titre d'hypothèses. **Ils restent à
  valider formellement par le cabinet**, et se modifient sans toucher au code
  (zone de marché, ou surcharge au niveau d'un dossier).

---

## 7. Ce qui vous est remis

| | |
|---|---|
| L'adresse de l'application et le code d'inscription | *(communiqués séparément)* |
| Le **code source** complet | dépôt Git, sans dépendance à un prestataire |
| Le **guide d'utilisation** | `docs/guide_utilisation.md` |
| La **procédure d'hébergement** | `docs/deploiement.md` — pour reprendre la main |
| Les **choix métier** et leurs raisons | `docs/choix_interface.md`, `docs/retour_cabinet.md` |
| Le **script de démonstration** | `docs/script_demonstration.md` |

---

*Pour toute question sur l'outil : Marius HOUNKPETOHOU et René DANSOU.*
