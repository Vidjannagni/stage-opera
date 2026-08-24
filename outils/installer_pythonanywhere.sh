#!/usr/bin/env bash
# Installation de RentImmo sur PythonAnywhere, en une commande.
#
# À lancer depuis la console Bash de PythonAnywhere (onglet Consoles → Bash) :
#
#   git clone https://github.com/Vidjannagni/stage-opera.git
#   bash stage-opera/outils/installer_pythonanywhere.sh
#
# Le script installe les dépendances, prépare une base **vierge**, crée le
# premier compte conseiller, puis affiche le contenu exact du fichier WSGI à
# recopier — clé secrète déjà engendrée. Il ne reste ensuite que trois champs à
# renseigner dans l'onglet Web.
#
# Relançable sans dommage : il ne recrée pas ce qui existe déjà.
set -euo pipefail

PROJET="$(cd "$(dirname "$0")/.." && pwd)"
VENV="${VIRTUAL_ENV:-$HOME/.virtualenvs/rentimmo}"
cd "$PROJET"

echo "════════════════════════════════════════════════════════════════════"
echo " RentImmo — installation sur PythonAnywhere"
echo " Projet : $PROJET"
echo "════════════════════════════════════════════════════════════════════"

# ── 1. Python ────────────────────────────────────────────────────────────────
# Le code utilise la syntaxe « X | None » : 3.10 au minimum. On prend la
# version la plus récente disponible plutôt qu'une version codée en dur, que
# l'image de l'hébergeur peut ne pas fournir.
if [ -z "${VIRTUAL_ENV:-}" ]; then
  PYTHON=""
  for version in 3.13 3.12 3.11 3.10; do
    if command -v "python$version" >/dev/null 2>&1; then
      PYTHON="$(command -v "python$version")"; break
    fi
  done
  if [ -z "$PYTHON" ]; then
    echo "⨯ Aucun Python 3.10+ trouvé. Vérifiez : ls /usr/bin/python3.*"
    exit 1
  fi
  echo "── Python retenu : $PYTHON"

  if [ ! -d "$VENV" ]; then
    echo "── Création de l'environnement virtuel ($VENV)…"
    "$PYTHON" -m venv "$VENV"
  fi
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
fi

# ── 2. Dépendances ───────────────────────────────────────────────────────────
# WeasyPrint (export PDF) réclame des bibliothèques système qui manquent sur
# certains hébergements. Son absence ne doit pas faire échouer l'installation :
# l'application le signale à l'écran et l'export Excel continue de fonctionner.
echo "── Dépendances…"
pip install --quiet --upgrade pip
if ! pip install --quiet -r requirements.txt; then
  echo "   ⚠  Installation complète impossible — nouvelle tentative sans WeasyPrint."
  grep -v -i 'weasyprint' requirements.txt > /tmp/rentimmo-requirements.txt
  pip install --quiet -r /tmp/rentimmo-requirements.txt
  echo "   ⚠  L'export PDF ne sera pas disponible ; l'export Excel, si."
fi

# ── 3. Base de données, vierge ───────────────────────────────────────────────
export FLASK_APP=run.py
echo "── Base de données…"
flask db upgrade
echo "── Zones de marché…"
flask seed-zones
# Pas de `flask demo-data` : l'installation remise au cabinet part vierge, pour
# qu'aucun conseiller ne prenne un dossier fictif pour un vrai.

# ── 4. Secrets ───────────────────────────────────────────────────────────────
CLE="$(python -c 'import secrets; print(secrets.token_hex(32))')"
CODE="$(python -c 'import secrets; print("choubel-" + secrets.token_urlsafe(6))')"

# ── 5. Premier compte conseiller ─────────────────────────────────────────────
echo
if [ "$(flask conseillers | grep -c '@' || true)" -eq 0 ]; then
  read -r -p "Adresse e-mail du premier conseiller : " EMAIL
  read -r -p "Son nom complet : " NOM
  flask conseiller-nouveau "$EMAIL" --nom "$NOM"
else
  echo "── Comptes déjà présents :"
  flask conseillers
fi

# ── 6. Ce qu'il reste à faire à la main ──────────────────────────────────────
# PythonAnywhere définit $USER ; le repli couvre les shells qui ne le font pas.
UTILISATEUR="${USER:-$(basename "$HOME")}"
cat <<FIN

════════════════════════════════════════════════════════════════════
 Il reste l'onglet « Web » de PythonAnywhere — trois réglages.
════════════════════════════════════════════════════════════════════

1. Add a new web app → Manual configuration → Python 3
   (surtout pas « Flask », qui créerait un projet vide).

2. Virtualenv :   $VENV

3. Static files : URL  /static/
                  Path $PROJET/app/static/

4. Code → « WSGI configuration file » : REMPLACER tout le contenu par ceci.
   La clé secrète et le code d'inscription ci-dessous sont engendrés pour vous.

┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
import os
import sys

PROJET = "$PROJET"
if PROJET not in sys.path:
    sys.path.insert(0, PROJET)

os.environ["FLASK_ENV"] = "prod"
os.environ["SECRET_KEY"] = "$CLE"
os.environ["CODE_INSCRIPTION"] = "$CODE"

from app import create_app

application = create_app()
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄

5. Cocher « Force HTTPS » dans l'onglet Web.
   Sans cela, la connexion échoue sans message : les cookies de session ne
   circulent qu'en HTTPS.

6. Reload, puis ouvrir  https://$UTILISATEUR.pythonanywhere.com

   Code d'inscription à donner aux conseillers : $CODE
   (se transmet de la main à la main, jamais dans un message public)

FIN
