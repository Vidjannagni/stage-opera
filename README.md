# RentImmo — Outil d'analyse de rentabilité d'investissement immobilier

Application Flask de conseil en investissement immobilier développée pour
**Choubel Consulting** par René DANSOU et Marius HOUNKPETOHOU
(projet de 6 semaines, 13 juillet – 21 août 2026).

Fonctionnalités cibles : coût d'acquisition et travaux, rendement locatif
(brut / net / net-net), simulation de financement, comparaison de scénarios,
cash-flow, TRI, VAN, exports PDF / Excel. **Paramétrable par zone de marché**
(Maroc par défaut, France, zone personnalisée) : frais d'acquisition,
fiscalité et devise s'actualisent selon la zone.

## Installation (local)

Le plus simple — installe, migre, seed et lance en une commande :

```bash
./lancer.sh          # ou ./lancer.sh --demo pour inclure le jeu de démonstration
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
flask --app run.py demo-data  # connexion : demo@choubel.com / demo1234
```

## Documentation

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

## Déploiement (optionnel)

Le même code se déploie derrière Gunicorn avec PostgreSQL :

```bash
export DATABASE_URL=postgresql://user:password@host:5432/rentimmo
export FLASK_ENV=prod
gunicorn "app:create_app()"
```

## Structure

```
app/
├── core/        # moteur de calcul financier (Python pur, testé)
├── models/      # User, Client, Projet, Scenario, ZonePreset, LigneTravaux
├── blueprints/  # auth, clients, projets, scenarios, exports
├── templates/   # Jinja2 + Bootstrap 5
└── static/      # CSS, JS (Chart.js)
data/zones.json  # préréglages des zones de marché
tests/           # tests pytest du moteur et des routes
```
