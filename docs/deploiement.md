# Mise en ligne de RentImmo

Objectif : une adresse web que le cabinet peut ouvrir depuis n'importe quel
navigateur, sans rien installer.

L'application est déjà une application web ; la mettre en ligne consiste à la
faire tourner sur un serveur plutôt que sur votre poste. Tout est prêt dans le
dépôt : il reste à créer un compte chez un hébergeur.

**Voie retenue : PythonAnywhere (section 3)**, seul hébergeur de la liste à ne
pas réclamer de carte bancaire. La base SQLite y suffit ; PostgreSQL n'est
nécessaire que sur les hébergements de la section 4.

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
| `deploiement/pythonanywhere_wsgi.py` | Modèle de fichier WSGI à recopier sur PythonAnywhere |

Le code ne change pas entre le local et la production : seules les variables
d'environnement diffèrent.

---

## 2. Variables d'environnement

| Variable | Obligatoire | Rôle |
|---|---|---|
| `SECRET_KEY` | **oui** | Signature des sessions et des jetons CSRF. En production, l'application **refuse de démarrer** si elle vaut encore la valeur de développement. |
| `DATABASE_URL` | non | Fournie par l'hébergeur quand une base PostgreSQL est rattachée. Absente, l'application utilise sa base SQLite — ce qui est le cas sur PythonAnywhere. |
| `FLASK_ENV` | oui | `prod` — désactive le mode debug et impose les cookies sécurisés. |
| `CODE_INSCRIPTION` | recommandé | Si définie, la création de compte exige ce code. **Sans elle, n'importe qui connaissant l'adresse peut créer un compte.** |
| `JEU_DE_DEMO` | facultatif | `1` pour créer le dossier de démonstration au démarrage, sur les hébergeurs sans accès shell. Inutile sur PythonAnywhere, qui fournit une console. |

Ces variables se définissent dans le fichier WSGI sur PythonAnywhere, dans
l'interface de l'hébergeur ailleurs, et dans le fichier `.env` en local.

---

## 3. Déploiement sur PythonAnywhere (sans carte bancaire)

Render exige une carte bancaire, même sur son offre gratuite. PythonAnywhere
n'en demande pas : c'est la voie retenue. L'application y tourne sur sa base
SQLite, aucun PostgreSQL n'est nécessaire pour quelques conseillers.

### 3.1 Créer le compte et récupérer le code

1. Créer un compte **Beginner** (gratuit) sur
   [pythonanywhere.com](https://www.pythonanywhere.com). L'adresse sera du type
   `https://<utilisateur>.pythonanywhere.com`.

2. Onglet **Consoles → Bash**, puis :
   ```bash
   git clone https://github.com/Vidjannagni/stage-opera.git
   cd stage-opera
   ```

3. Créer l'environnement virtuel et installer les dépendances :
   ```bash
   mkvirtualenv --python=/usr/bin/python3.12 rentimmo
   pip install -r requirements.txt
   ```

4. Préparer la base :
   ```bash
   export FLASK_APP=run.py
   flask db upgrade
   flask seed-zones
   flask demo-data        # facultatif : le dossier de démonstration
   ```

### 3.2 Déclarer l'application web

1. Onglet **Web → Add a new web app → Manual configuration → Python 3.12**
   (surtout pas « Flask », qui créerait un projet vide).

2. Dans **Virtualenv**, saisir : `/home/<utilisateur>/.virtualenvs/rentimmo`

3. Dans **Code**, ouvrir le lien *WSGI configuration file* et **remplacer tout
   son contenu** par celui de `deploiement/pythonanywhere_wsgi.py`, en adaptant
   les trois valeurs signalées (utilisateur, `SECRET_KEY`, `CODE_INSCRIPTION`).

4. Dans **Static files**, ajouter la correspondance :

   | URL | Directory |
   |---|---|
   | `/static/` | `/home/<utilisateur>/stage-opera/app/static/` |

5. Cliquer sur **Reload**, puis ouvrir l'adresse.

### 3.3 Mettre à jour ensuite

```bash
cd ~/stage-opera && git pull && flask db upgrade
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

## 4. Autre solution : déploiement sur Render

Render exige une carte bancaire même sur l'offre gratuite. Cette section reste
valable le jour où le cabinet dispose d'un hébergement payant : Render lit
`render.yaml` et crée tout seul le service et la base.

1. **Pousser le code sur GitHub.** Le dépôt distant est déjà configuré :
   ```bash
   git add -A
   git commit -m "Mise en ligne : configuration de déploiement"
   git push origin main
   ```

2. **Créer un compte** sur [render.com](https://render.com) et autoriser l'accès
   au dépôt `Vidjannagni/stage-opera`.

3. **New → Blueprint**, sélectionner le dépôt. Render détecte `render.yaml`,
   affiche le service `rentimmo` et la base `rentimmo-db`, et génère lui-même
   `SECRET_KEY`. Valider.

4. **Ajouter les deux variables manquantes** dans *Environment* :
   - `CODE_INSCRIPTION` — une phrase que vous seuls connaissez ;
   - `JEU_DE_DEMO = 1` si vous voulez le dossier de démonstration en ligne.

5. **Attendre le premier déploiement** (5 à 10 minutes). Les journaux doivent
   montrer, dans l'ordre : `Migrations…`, `Zones de marché…`, puis
   `Listening at: http://0.0.0.0:...`.

6. **Ouvrir l'adresse** fournie (`https://rentimmo-xxxx.onrender.com`) et créer
   votre compte conseiller via *Créer un compte*, avec le code d'inscription.

Pour mettre à jour ensuite : `git push` suffit, Render redéploie et rejoue les
migrations.

---

## 5. Points de vigilance sur une offre gratuite

- **Mise en veille.** Un service gratuit s'endort après une quinzaine de minutes
  sans visite ; la première page demandée ensuite met 30 à 60 secondes à
  répondre. **Ouvrez l'application quelques minutes avant une démonstration.**
- **Durée de vie de la base.** Les bases PostgreSQL gratuites sont souvent
  limitées dans le temps. Vérifiez l'échéance annoncée par l'hébergeur au moment
  de la création, et prévoyez une sauvegarde (`pg_dump`) si les données doivent
  survivre.
- **Pas d'accès shell** sur les offres gratuites : d'où la variable
  `JEU_DE_DEMO` plutôt qu'une commande lancée à la main.
- **Les conditions changent souvent.** Ce qui précède décrit la démarche ; les
  détails d'écran et les quotas sont à vérifier sur place.

---

## 6. Sécurité de la mise en ligne

Ce qui est déjà en place :

- mots de passe hachés (jamais stockés en clair) ;
- protection CSRF sur tous les formulaires ;
- **cloisonnement strict** : un conseiller ne voit que ses propres dossiers,
  vérifié par les tests ;
- cookies de session `Secure`, `HttpOnly` et `SameSite=Lax` en production ;
- HTTPS fourni par l'hébergeur ;
- refus de démarrer sans `SECRET_KEY` propre.

Ce à quoi il faut penser :

- **Définir `CODE_INSCRIPTION`.** Sans cette variable, l'inscription est
  ouverte à quiconque connaît l'adresse.
- **Données réelles de clients.** Dès que de vrais dossiers sont saisis, il
  s'agit de données personnelles : n'y mettez que le nécessaire, et prévenez le
  cabinet que l'hébergement est celui d'un projet d'étude, pas un service
  contractuel.
- **Sauvegardes.** Aucune n'est automatique sur une offre gratuite.

---

## 7. Autre solution : sur le réseau du cabinet

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
