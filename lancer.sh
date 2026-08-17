#!/usr/bin/env bash
# RentImmo — installation et lancement en une commande (poste local).
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "── Création de l'environnement virtuel…"
  python3 -m venv .venv
  .venv/bin/pip install --quiet -r requirements.txt
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "── Fichier .env créé depuis .env.example (pensez à changer SECRET_KEY)."
fi

export FLASK_APP=run.py
.venv/bin/flask db upgrade
.venv/bin/flask seed-zones

case "${1:-}" in
  --demo)       .venv/bin/flask demo-data ;;
  --demo-reset) .venv/bin/flask demo-data --reset ;;
esac

echo "── RentImmo démarre sur http://127.0.0.1:5000 (Ctrl+C pour arrêter)"
.venv/bin/flask run
