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

# Les offres gratuites n'ouvrent pas d'accès shell : ces deux variables sont le
# seul moyen d'y lancer une commande. Elles s'ajoutent dans l'interface de
# l'hébergeur, provoquent un redéploiement, puis se retirent.

if [ "${JEU_DE_DEMO:-0}" = "1" ]; then
  echo "── Jeu de démonstration…"
  flask demo-data
fi

# Un conseiller a perdu son mot de passe et l'hébergement n'a pas de console :
# MOT_DE_PASSE_A_REINITIALISER=<son adresse> lui en attribue un nouveau, affiché
# dans les journaux de déploiement — que seul le titulaire du compte
# d'hébergement peut lire. Le conseiller le change ensuite depuis « Mon compte »,
# et la variable se retire aussitôt : laissée en place, elle réinitialiserait le
# mot de passe à chaque redémarrage.
if [ -n "${MOT_DE_PASSE_A_REINITIALISER:-}" ]; then
  echo "── Réinitialisation du mot de passe…"
  flask conseiller-mot-de-passe "$MOT_DE_PASSE_A_REINITIALISER"
  echo "   ⚠  Retirez maintenant la variable MOT_DE_PASSE_A_REINITIALISER."
fi

echo "── Démarrage de Gunicorn sur le port ${PORT:-8000}…"
exec gunicorn "app:create_app()" \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
