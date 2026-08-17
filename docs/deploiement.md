# Mise en ligne de RentImmo

Objectif : une adresse web que le cabinet peut ouvrir depuis n'importe quel
navigateur, sans rien installer.

L'application est déjà une application web ; la mettre en ligne consiste à la
faire tourner sur un serveur avec une base PostgreSQL au lieu de la base SQLite
locale. Tout est prêt dans le dépôt : il reste à créer un compte chez un
hébergeur et à lui désigner le dépôt.

---

## 1. Ce que contient le dépôt pour le déploiement

| Fichier | Rôle |
|---|---|
| `demarrer.sh` | Commande de démarrage : applique les migrations, charge les zones de marché, puis lance Gunicorn |
| `Procfile` | Indique `./demarrer.sh` aux hébergeurs qui lisent ce format |
| `render.yaml` | Décrit à Render le service web **et** la base PostgreSQL à créer |
| `.python-version` | Version de Python (3.12.3) |
| `requirements.txt` | Inclut `gunicorn` et le pilote `psycopg` |
| `config.py` | Bascule sur PostgreSQL dès que `DATABASE_URL` est présente |

Le code ne change pas entre le local et la production : seules les variables
d'environnement diffèrent.

---

## 2. Variables d'environnement

| Variable | Obligatoire | Rôle |
|---|---|---|
| `SECRET_KEY` | **oui** | Signature des sessions et des jetons CSRF. En production, l'application **refuse de démarrer** si elle vaut encore la valeur de développement. |
| `DATABASE_URL` | oui | Fournie automatiquement par l'hébergeur quand la base est rattachée au service. |
| `FLASK_ENV` | oui | `prod` — désactive le mode debug et impose les cookies sécurisés. |
| `CODE_INSCRIPTION` | recommandé | Si définie, la création de compte exige ce code. **Sans elle, n'importe qui connaissant l'adresse peut créer un compte.** |
| `JEU_DE_DEMO` | facultatif | `1` pour créer le dossier de démonstration au démarrage (utile car les offres gratuites n'ouvrent pas d'accès shell). |

---

## 3. Déploiement sur Render

Render lit `render.yaml` et crée tout seul le service et la base.

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

## 4. Points de vigilance sur une offre gratuite

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

## 5. Sécurité de la mise en ligne

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

## 6. Autre solution : sur le réseau du cabinet

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
