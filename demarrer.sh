#!/usr/bin/env bash
# Démarrage en production (hébergeur). Applique les migrations et charge les
# zones de marché avant de servir l'application, pour qu'un déploiement sur
# une base vierge soit immédiatement utilisable.
set -euo pipefail

export FLASK_APP=run.py
export FLASK_ENV=prod

echo "── Migrations…"
flask db upgrade

echo "── Zones de marché…"
flask seed-zones

# Les offres gratuites n'ouvrent pas d'accès shell : définir JEU_DE_DEMO=1 dans
# les variables de l'hébergeur permet de créer le dossier de démonstration.
if [ "${JEU_DE_DEMO:-0}" = "1" ]; then
  echo "── Jeu de démonstration…"
  flask demo-data
fi

echo "── Démarrage de Gunicorn sur le port ${PORT:-8000}…"
exec gunicorn "app:create_app()" \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
