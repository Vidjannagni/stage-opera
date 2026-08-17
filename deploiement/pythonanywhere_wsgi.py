"""Modèle de fichier WSGI pour PythonAnywhere.

À recopier dans le fichier WSGI que PythonAnywhere crée pour vous
(onglet *Web* → *Code* → lien « WSGI configuration file », chemin du type
``/var/www/<utilisateur>_pythonanywhere_com_wsgi.py``), en remplaçant son
contenu d'origine et en adaptant les trois valeurs signalées ci-dessous.

Les variables d'environnement sont définies **avant** l'import de
l'application : la configuration les lit au moment de l'import.
"""
import os
import sys
from pathlib import Path

# ── 1. À adapter : votre nom d'utilisateur PythonAnywhere ────────────────────
UTILISATEUR = "VOTRE_UTILISATEUR"

PROJET = Path(f"/home/{UTILISATEUR}/stage-opera")
if str(PROJET) not in sys.path:
    sys.path.insert(0, str(PROJET))

os.environ["FLASK_ENV"] = "prod"

# ── 2. À adapter : clé secrète, à générer une fois et à ne jamais publier ────
#     python -c "import secrets; print(secrets.token_hex(32))"
os.environ["SECRET_KEY"] = "REMPLACEZ_PAR_LA_CLE_GENEREE"

# ── 3. À adapter : réserve la création de compte aux porteurs du code ────────
#     Sans cette ligne, quiconque connaît l'adresse peut s'inscrire.
os.environ["CODE_INSCRIPTION"] = "REMPLACEZ_PAR_UNE_PHRASE_A_VOUS"

# La base SQLite du dossier instance/ suffit pour quelques conseillers ;
# décommenter pour utiliser une base externe.
# os.environ["DATABASE_URL"] = "postgresql://utilisateur:motdepasse@hote:5432/rentimmo"

from app import create_app  # noqa: E402 — après la définition des variables

application = create_app()
