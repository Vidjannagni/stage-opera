# RentImmo — Outil d'analyse de rentabilité d'investissement immobilier

Application Flask de conseil en investissement immobilier développée pour
**Choubel Consulting** par René DANSOU et Marius HOUNKPETOHOU
(projet de 6 semaines, 13 juillet – 21 août 2026).

L'outil suit l'accompagnement réel d'un investisseur : **brief de recherche**
(type de bien, standing, superficie, commodités, budget, financement, objectif
et horizon), **suivi du dossier** de la recherche à la livraison, puis analyse
chiffrée du bien retenu — coût d'acquisition et travaux, rendement locatif
(net, net-net, brut), financement, cash-flow, plus-value et valeur créée, TRI,
VAN, comparaison de scénarios et exports PDF / Excel.

Deux types d'opération sont pris en charge : **locatif** et **terrain /
revente** (sans loyer, la valeur venant de la plus-value). L'**achat sur plan**
diffère la mise en exploitation. **Paramétrable par zone de marché** (Maroc par
défaut, France, zone personnalisée) : frais d'acquisition, fiscalité et devise
s'actualisent selon la zone.

L'application **n'affiche aucun seuil ni verdict** : les indicateurs se lisent
au regard de l'objectif et de l'horizon du client (cf.
`docs/retour_cabinet.md`).

## Installation (local)

Le plus simple — installe, migre, seed et lance en une commande :

```bash
./lancer.sh                # installe, migre, seed et démarre
./lancer.sh --demo         # idem, en ajoutant le jeu de démonstration
./lancer.sh --demo-reset   # idem, en régénérant le jeu de démonstration
```

Ou manuellement :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # puis adapter SECRET_KEY

flask --app run.py db upgrade      # crée la base (SQLite dans instance/)
flask --app run.py seed-zones      # charge les zones de marché par défaut
```

## Lancement

```bash
flask --app run.py run        # http://127.0.0.1:5000
```

Pour découvrir l'outil avec un dossier pré-rempli (client, bien à Casablanca,
trois scénarios) :

```bash
flask --app run.py demo-data            # connexion : demo@choubel.com / demo1234
flask --app run.py demo-data --reset    # régénère le jeu (après mise à jour)
```

Le jeu contient le brief de recherche de M. Alaoui et **deux dossiers** : un
appartement locatif à Casablanca (3 scénarios) et un terrain en portage sur
10 ans, qui illustre une opération sans loyer.

## Documentation

- `docs/retour_cabinet.md` — entretien de cadrage métier avec le cabinet, écarts
  constatés et modifications apportées.
- `docs/choix_interface.md` — justification des choix visuels et ergonomiques.
- `docs/guide_utilisation.md` — guide du conseiller, dans l'ordre d'un rendez-vous.
- `docs/script_demonstration.md` — déroulé de démonstration face à un investisseur.
- `cahier_des_charges.pdf` — périmètre, formules et conventions de calcul.
- `feuille_de_route.pdf` — planning des six semaines.
- `rapports/` — rapports hebdomadaires 2 à 5 et rapport final (LaTeX + PDF).

## Dossier de remise

```bash
./outils/preparer_remise.sh   # produit remise/RentImmo_dossier_remise.zip
```

## Tests

```bash
pytest tests/ -v
```

## Mise en ligne

Le dépôt contient tout le nécessaire : `deploiement/pythonanywhere_wsgi.py` pour
**PythonAnywhere** (offre gratuite sans carte bancaire, base SQLite), et
`demarrer.sh` / `Procfile` / `render.yaml` pour un hébergeur de type Render
(Gunicorn + PostgreSQL, migrations et zones jouées au démarrage).

**Marche à suivre complète : `docs/deploiement.md`.**

Variables d'environnement attendues en production : `FLASK_ENV=prod`,
`SECRET_KEY` (l'application refuse de démarrer sans), `DATABASE_URL` (fournie
par l'hébergeur), et `CODE_INSCRIPTION` pour réserver la création de compte.

## Structure

```
app/
├── core/        # moteur de calcul financier (Python pur, testé)
├── models/      # User, Client, Brief, Projet, Scenario, ZonePreset, LigneTravaux
├── blueprints/  # auth, clients, projets, scenarios, exports
├── templates/   # Jinja2 + Bootstrap 5
└── static/      # CSS, JS (Chart.js)
data/zones.json  # préréglages des zones de marché
tests/           # tests pytest du moteur et des routes
```
