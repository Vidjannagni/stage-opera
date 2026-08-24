# Mise en ligne de RentImmo

Objectif : une adresse web que le cabinet peut ouvrir depuis n'importe quel
navigateur, sans rien installer.

L'application est déjà une application web ; la mettre en ligne consiste à la
faire tourner sur un serveur plutôt que sur votre poste. Tout est prêt dans le
dépôt : il reste à créer un compte chez un hébergeur.

**Voie retenue : PythonAnywhere (section 3)** — le seul hébergeur capable de
faire tourner cette application sans réclamer de carte bancaire. L'adresse y
est `https://<utilisateur>.pythonanywhere.com` : **choisissez donc le nom
d'utilisateur avec soin le jour de l'inscription, car il devient l'adresse.**
Un nom de domaine à soi (`.com`) est réservé aux offres payantes ; la section 5
décrit ce chemin, le jour où le cabinet y met un budget.

> **Ce qui ne peut pas héberger cette application : Netlify, Vercel, GitHub
> Pages, Google AI Studio.** Les trois premiers servent des fichiers déjà
> fabriqués — du HTML, du JavaScript — et, pour certains, de petites fonctions
> sans mémoire. Google AI Studio n'est pas un hébergeur du tout : c'est un
> atelier pour essayer des modèles Gemini. Chez Google, ce qui saurait faire
> tourner RentImmo est **Cloud Run** — mais il exige un compte de facturation,
> carte comprise, même pour rester dans le palier gratuit.
>
> RentImmo est un serveur Python qui tient une base de données, des sessions et
> des migrations : il lui faut un hébergeur qui exécute un processus en continu.

---

## 1. Ce que contient le dépôt pour le déploiement

| Fichier | Rôle |
|---|---|
| `demarrer.sh` | Commande de démarrage : applique les migrations, charge les zones de marché, puis lance Gunicorn |
| `Procfile` | Indique `./demarrer.sh` aux hébergeurs qui lisent ce format |
| `render.yaml` | Décrit à Render le service web **et** la base PostgreSQL à créer |
| `.python-version` | Version de Python (3.12.3) |
| `requirements.txt` | Inclut `gunicorn` et le pilote `psycopg` |
| `config.py` | Bascule sur PostgreSQL dès que `DATABASE_URL` est présente, sinon SQLite |
| `outils/installer_pythonanywhere.sh` | Installation complète en une commande : dépendances, base vierge, premier compte, et le fichier WSGI déjà rempli |
| `deploiement/pythonanywhere_wsgi.py` | Modèle commenté du fichier WSGI, pour comprendre ce que le script produit |

Le code ne change pas entre le local et la production : seules les variables
d'environnement diffèrent.

---

## 2. Variables d'environnement

| Variable | Obligatoire | Rôle |
|---|---|---|
| `SECRET_KEY` | **oui** | Signature des sessions et des jetons CSRF. En production, l'application **refuse de démarrer** si elle vaut encore la valeur de développement. |
| `DATABASE_URL` | non | Fournie par l'hébergeur quand une base PostgreSQL est rattachée. Absente, l'application utilise sa base SQLite — ce qui est le cas sur PythonAnywhere. |
| `FLASK_ENV` | oui | `prod` — désactive le mode debug et impose les cookies sécurisés. |
| `CODE_INSCRIPTION` | **oui** | La création de compte exige ce code. **En production, l'application refuse de démarrer sans lui** : une adresse publique sans code, c'est un outil où n'importe qui crée un compte et voit ses dossiers à côté de ceux du cabinet. Pour ouvrir délibérément l'inscription, lui donner la valeur `ouvert`. |
| `JEU_DE_DEMO` | facultatif | `1` pour créer le dossier de démonstration au démarrage, sur les hébergeurs sans accès shell. **À laisser vide pour une remise au cabinet** : la base part vierge. |
| `MOT_DE_PASSE_A_REINITIALISER` | ponctuelle | L'adresse d'un conseiller qui a perdu son mot de passe, sur un hébergement sans console. Le nouveau mot de passe s'affiche dans les journaux de déploiement. **À retirer aussitôt après.** |

Ces variables se définissent dans le fichier WSGI sur PythonAnywhere, dans
l'interface de l'hébergeur ailleurs, et dans le fichier `.env` en local.

---

## 3. Déploiement sur PythonAnywhere

PythonAnywhere ne demande aucune carte bancaire, et fournit une **console** —
ce que les offres gratuites concurrentes n'offrent pas, et sans laquelle un
mot de passe perdu devient un problème. L'application y tourne sur sa base
SQLite : aucun PostgreSQL n'est nécessaire pour quelques conseillers.

En contrepartie, l'adresse reste `https://<utilisateur>.pythonanywhere.com`.
Elle se termine bien par `.com`, mais c'est un sous-domaine de l'hébergeur, pas
un domaine à vous. **Le nom d'utilisateur choisi à l'inscription devient
l'adresse** : `choubelconsulting.pythonanywhere.com` se présente mieux devant un
client que `marius2026.pythonanywhere.com`. C'est un choix qu'on ne refait pas.

### 3.1 Le compte, puis une seule commande

1. Créer un compte **Beginner** (gratuit) sur
   [pythonanywhere.com](https://www.pythonanywhere.com).

   > **Le nom d'utilisateur devient l'adresse de l'outil**, et ne se change
   > pas ensuite. `choubelconsulting` donne
   > `https://choubelconsulting.pythonanywhere.com` ; un pseudonyme personnel
   > donnera une adresse qu'on n'ose pas montrer à un client.

2. Onglet **Consoles → Bash**, puis :

   ```bash
   git clone https://github.com/Vidjannagni/stage-opera.git
   bash stage-opera/outils/installer_pythonanywhere.sh
   ```

   Le script fait tout ce qui peut l'être sans interface : il choisit la
   version de Python disponible, crée l'environnement virtuel, installe les
   dépendances, applique les migrations, charge les zones de marché, demande
   l'adresse du premier conseiller et lui attribue un mot de passe provisoire.

   La base part **vierge** : le jeu de démonstration n'a pas sa place sur
   l'installation remise au cabinet — un conseiller finirait par prendre
   « M. Alaoui » pour un vrai dossier. Servez-vous-en sur votre poste, pas ici.

   Si l'export PDF ne peut pas s'installer (bibliothèques système absentes), le
   script le dit et poursuit : l'application le signalera à l'écran, et l'export
   Excel continuera de fonctionner.

3. **Le script se termine en affichant le contenu exact du fichier WSGI**, clé
   secrète et code d'inscription déjà engendrés. Gardez cette sortie sous les
   yeux : la suite consiste à la recopier.

### 3.2 Déclarer l'application web

Quatre réglages dans l'onglet **Web**, tous dictés par la sortie du script.

1. **Add a new web app → Manual configuration → Python 3**
   (surtout pas « Flask », qui créerait un projet vide — et la même version de
   Python que celle annoncée par le script).

2. **Virtualenv** : le chemin affiché, du type
   `/home/<utilisateur>/.virtualenvs/rentimmo`

3. **Code → WSGI configuration file** : **remplacer tout le contenu** par le
   bloc affiché par le script. Rien à adapter — il est déjà rempli.
   *(Le modèle commenté reste dans `deploiement/pythonanywhere_wsgi.py` pour
   qui veut comprendre chaque ligne.)*

4. **Static files** : URL `/static/` → Directory
   `/home/<utilisateur>/stage-opera/app/static/`

5. Cocher **Force HTTPS**. Sans cela, la connexion échoue **sans message** :
   les cookies de session ne circulent qu'en HTTPS, le formulaire de connexion
   est refusé et rien à l'écran ne dit pourquoi.

6. **Reload**, puis ouvrir l'adresse et se connecter avec le compte créé par le
   script. Changer le mot de passe provisoire depuis *Mon compte*.

### 3.3 Mettre à jour ensuite

```bash
cd ~/stage-opera
flask sauvegarder            # toujours avant une mise à jour
git pull && flask db upgrade
```
puis **Reload** dans l'onglet *Web*.

### 3.4 Limites de l'offre gratuite

- **L'export PDF peut ne pas fonctionner.** WeasyPrint dépend de bibliothèques
  système (Pango, Cairo) qui ne sont pas garanties. L'import étant différé dans
  le code, seul le bouton *Export PDF* serait affecté : **le reste de
  l'application, y compris l'export Excel, continue de fonctionner.** À tester
  après le déploiement ; en cas d'échec, présenter l'export Excel en
  démonstration et le PDF depuis le poste local.
- Le compte gratuit doit être **prolongé tous les trois mois** en se connectant,
  sinon l'application est désactivée.
- Un seul processus web, sans montée en charge : suffisant pour une
  démonstration et quelques conseillers.
- Les conditions des offres gratuites changent : vérifiez sur place.

---

---

## 4. Exploitation courante

**L'outil n'envoie aucun courriel.** Il n'a ni serveur de messagerie ni adresse
d'expédition, et en installer un pour trois conseillers coûterait plus à
administrer qu'il ne rendrait service. Un conseiller qui perd son mot de passe
s'en voit donc attribuer un provisoire par l'administrateur, et le change
lui-même depuis *Mon compte* — de sorte que personne d'autre que lui ne
connaisse son mot de passe définitif. La page de connexion le dit, pour que
personne ne cherche un lien « mot de passe oublié » qui n'existe pas.

Reste à savoir **comment** l'administrateur lance cette commande. Cela dépend de
l'hébergeur, et c'est le seul point où les deux voies diffèrent vraiment.

### 4.1 Là où il y a une console (PythonAnywhere, poste du cabinet)

Depuis **Consoles → Bash**, après `cd ~/stage-opera` et `export FLASK_APP=run.py` :

| Situation | Commande |
|---|---|
| Voir les comptes existants | `flask conseillers` |
| Ajouter un conseiller | `flask conseiller-nouveau <email> --nom "..."` |
| **Un conseiller a perdu son mot de passe** | `flask conseiller-mot-de-passe <email>` |
| Sauvegarder la base | `flask sauvegarder` |
| Effacer le jeu de démonstration | `flask demo-data --supprimer` |

### 4.2 Là où il n'y en a pas (Render gratuit)

Aucune commande ne s'y lance à la main. Deux variables d'environnement en
tiennent lieu : on les ajoute dans *Environment*, ce qui provoque un
redéploiement, **puis on les retire**.

| Situation | Marche à suivre |
|---|---|
| Ajouter un conseiller | il s'inscrit lui-même avec le code d'inscription |
| **Un conseiller a perdu son mot de passe** | `MOT_DE_PASSE_A_REINITIALISER = <son adresse>` — le nouveau mot de passe s'affiche dans les journaux de déploiement, que seul le titulaire du compte d'hébergement peut lire. **Retirer la variable ensuite** : laissée en place, elle réinitialiserait le mot de passe à chaque redémarrage. |
| Jeu de démonstration | `JEU_DE_DEMO = 1` — à ne pas définir sur l'installation remise au cabinet |

### 4.3 Sauvegardes

**Elles ne se font pas toutes seules**, et aucune offre gratuite n'en fait à
votre place.

- **Base SQLite** (PythonAnywhere, poste du cabinet) : `flask sauvegarder` écrit
  une copie datée dans `sauvegardes/`. Téléchargez-la.
- **Base PostgreSQL** (Render, Neon) : depuis votre poste, avec l'URL de
  connexion externe fournie par l'hébergeur :
  ```bash
  pg_dump "postgresql://…" > rentimmo-$(date +%F).sql
  ```

Dans les deux cas, conservez la copie **ailleurs que sur l'hébergement** : une
sauvegarde qui vit au même endroit que l'original ne protège de rien. À faire
avant chaque mise à jour, et régulièrement dès que le cabinet y saisit de vrais
dossiers.

> **Si vous testez la configuration de production sur votre poste**, la
> connexion échouera en `http://` : les cookies de session sont marqués
> `Secure` et ne circulent qu'en HTTPS. Ce n'est pas une panne — c'est le
> réglage qui protège la session en ligne. Testez en local avec `FLASK_ENV=dev`.

---

---

## 5. Le jour où il y a un budget : Render et un domaine à vous

Render lit `render.yaml` et crée tout seul le service web et sa base
PostgreSQL. Le service web est gratuit, mais **une carte bancaire est demandée
à l'inscription** pour vérifier l'identité : c'est ce qui écarte cette voie
tant qu'aucun budget n'existe. Elle reste décrite ici parce qu'elle apporte
deux choses que PythonAnywhere gratuit ne donne pas — un **nom de domaine à
vous** et une base PostgreSQL — et que le passage se fait sans toucher au code.

### 5.1 Mettre en ligne

1. **Pousser le code sur GitHub.**
   ```bash
   git add -A
   git commit -m "Mise en ligne : configuration de déploiement"
   git push origin main
   ```

2. **Créer un compte** sur [render.com](https://render.com) et autoriser
   l'accès au dépôt `Vidjannagni/stage-opera`.

3. **New → Blueprint**, sélectionner le dépôt. Render détecte `render.yaml`,
   affiche le service `rentimmo` et la base `rentimmo-db`, et génère lui-même
   `SECRET_KEY`. Il **demande la valeur de `CODE_INSCRIPTION`** : donnez une
   phrase que vous seuls connaissez. Sans elle, l'application refuse de
   démarrer — un code d'inscription versionné n'en serait plus un.

4. **Attendre le premier déploiement** (5 à 10 minutes). Les journaux doivent
   montrer, dans l'ordre : `Migrations…`, `Zones de marché…`, puis
   `Listening at: http://0.0.0.0:...`.

5. **Ouvrir l'adresse** fournie (`https://rentimmo-xxxx.onrender.com`) et créer
   le premier compte conseiller via *Créer un compte*, avec le code
   d'inscription. La base part **vierge** : ne définissez pas `JEU_DE_DEMO`.

Pour mettre à jour ensuite, `git push` suffit : Render redéploie et rejoue les
migrations.

### 5.2 Le nom de domaine

Un `.com` **n'est pas gratuit** : comptez **10 à 15 € par an** chez un
registrar (Cloudflare, Porkbun, OVH, Namecheap). C'est la seule dépense de
l'installation. Aucun hébergeur ne fournit de `.com` gratuit ; les adresses
gratuites sont toujours des sous-domaines de l'hébergeur.

1. **Acheter le domaine** chez le registrar de votre choix. Un nom court et
   prononçable au téléphone vaut mieux qu'un nom exhaustif.
2. Dans Render : **Settings → Custom Domains → Add Custom Domain**, saisir
   `rentimmo.example.com` (ou le domaine nu).
3. Render affiche l'enregistrement DNS à créer. Chez le registrar :
   - un **CNAME** vers `rentimmo-xxxx.onrender.com` pour un sous-domaine ;
   - un **ALIAS/ANAME** (ou les adresses IP indiquées par Render) pour le
     domaine nu, tous les registrars ne le permettant pas.
4. Attendre la propagation (de quelques minutes à quelques heures). Render
   émet **le certificat HTTPS tout seul**, gratuitement : rien à installer.

Le domaine vous appartient et suit l'application : le jour où le cabinet
reprend l'hébergement, l'adresse ne change pas — seul l'enregistrement DNS est
repointé. C'est le principal intérêt d'en avoir un.

### 5.3 Ce que Render gratuit ne permet pas

- **Pas de console.** Aucune commande ne se lance à la main : le premier compte
  se crée par l'écran d'inscription, et une réinitialisation de mot de passe
  passe par la variable décrite en section 5.
- **Mise en veille.** Le service s'endort après une quinzaine de minutes sans
  visite ; la première page demandée ensuite met 30 à 60 secondes à répondre.
  Ouvrez l'application quelques minutes avant une démonstration.
- **La base gratuite est limitée dans le temps.** Render annonce une échéance à
  la création : **notez-la**, et lisez la section suivante.

### 5.4 Une base qui survit : PostgreSQL externe

Les bases gratuites de Render expirent. Pour un outil qui contiendra de vrais
dossiers, mieux vaut une base indépendante de l'hébergeur — chez
[Neon](https://neon.tech) ou [Supabase](https://supabase.com), dont les offres
gratuites sont durables :

1. Créer un projet, récupérer l'URL de connexion (`postgresql://…`).
2. Dans Render : **Environment**, remplacer `DATABASE_URL` par cette URL.
3. Redéployer. Les migrations s'appliquent seules sur la base neuve.

L'application accepte les deux formes d'URL (`postgres://` comme
`postgresql://`) et choisit le pilote elle-même : rien d'autre à changer. La
base vit alors chez un tiers, et survit à la disparition du service Render.

---

## 6. Points de vigilance sur une offre gratuite

- **Mise en veille.** Un service gratuit s'endort après une quinzaine de minutes
  sans visite ; la première page demandée ensuite met 30 à 60 secondes à
  répondre. **Ouvrez l'application quelques minutes avant une démonstration.**
- **Durée de vie de la base.** Les bases PostgreSQL gratuites sont souvent
  limitées dans le temps. Vérifiez l'échéance annoncée par l'hébergeur au moment
  de la création, et prévoyez une sauvegarde (`pg_dump`) si les données doivent
  survivre.
- **Pas d'accès shell** sur Render gratuit : d'où les variables d'environnement
  de la section 4.2, qui tiennent lieu de commandes.
- **Le nom de domaine, lui, se paie** — 10 à 15 € par an. C'est la seule
  dépense, et c'est ce qui rend l'adresse indépendante de l'hébergeur : le jour
  où le cabinet reprend la main, elle ne change pas.
- **Les conditions changent souvent.** Ce qui précède décrit la démarche ; les
  détails d'écran, les quotas et les échéances sont à vérifier sur place.

---

## 7. Sécurité de la mise en ligne

Ce qui est déjà en place :

- mots de passe hachés (jamais stockés en clair) ;
- protection CSRF sur tous les formulaires ;
- **cloisonnement strict** : un conseiller ne voit que ses propres dossiers,
  vérifié par les tests ;
- cookies de session `Secure`, `HttpOnly` et `SameSite=Lax` en production ;
- HTTPS fourni par l'hébergeur ;
- refus de démarrer sans `SECRET_KEY` propre.

- **refus de démarrer sans `CODE_INSCRIPTION`** : l'inscription ne peut pas
  rester ouverte par oubli ;
- **pages d'erreur de l'application** : une adresse erronée ou une panne
  n'expose aucune trace technique ;
- **`noindex` et `robots.txt`** : l'outil contient des dossiers de clients, il
  n'a rien à faire dans un moteur de recherche — et une page hébergée sur un
  compte d'étudiant n'a pas à passer pour le site officiel du cabinet.

Ce à quoi il faut penser :

- **Données réelles de clients.** Dès que de vrais dossiers sont saisis, il
  s'agit de données personnelles : n'y mettez que le nécessaire, et prévenez le
  cabinet que l'hébergement est celui d'un projet d'étude, pas un service
  contractuel (cf. `docs/remise_cabinet.md`, remis au cabinet).
- **Sauvegardes.** Aucune n'est automatique sur une offre gratuite :
  `flask sauvegarder`, puis téléchargement hors de l'hébergement.
- **Le compte d'hébergement est personnel.** Tant que l'application vit sur le
  compte de l'étudiant, elle disparaît avec lui. La reprise par le cabinet est
  décrite dans le document de remise.

---

## 8. Autre solution : sur le réseau du cabinet

Si le cabinet préfère que rien ne sorte de ses locaux, l'application tourne
telle quelle sur un poste du bureau :

```bash
export FLASK_ENV=prod
export SECRET_KEY="une-longue-phrase-secrete"
gunicorn "app:create_app()" --bind 0.0.0.0:8000
```

Les autres postes du réseau y accèdent par `http://<adresse-ip-du-poste>:8000`.
Aucune base PostgreSQL n'est nécessaire : la base SQLite du dossier `instance/`
suffit pour quelques conseillers.
