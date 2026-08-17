"""Configuration de l'application par environnement.

Le même code tourne en local (SQLite) et en production (PostgreSQL via
DATABASE_URL). Les secrets viennent des variables d'environnement (.env en
local, variables de l'hébergeur en ligne).
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Chargé ici, et non dans create_app : les classes ci-dessous lisent
# os.environ au moment de l'import du module. Sous Gunicorn ou un serveur
# WSGI — qui, contrairement à la commande `flask`, ne lit pas le .env —
# un chargement plus tardif arriverait trop tard et les valeurs du fichier
# seraient silencieusement ignorées.
load_dotenv(BASE_DIR / ".env")


def uri_base_de_donnees() -> str:
    """URI de la base, avec les corrections attendues par les hébergeurs.

    Render, Railway et Heroku exposent une URL en ``postgres://`` que
    SQLAlchemy 2 ne reconnaît plus, et n'imposent pas de pilote. On normalise
    donc vers ``postgresql+psycopg://`` (psycopg 3).
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        return f"sqlite:///{BASE_DIR / 'instance' / 'rentimmo.sqlite3'}"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me")
    SQLALCHEMY_DATABASE_URI = uri_base_de_donnees()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Les connexions PostgreSQL des offres gratuites sont coupées après un
    # temps d'inactivité : on vérifie la connexion avant de la réutiliser.
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False
    # L'application n'est servie qu'en HTTPS une fois déployée.
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    WTF_CSRF_ENABLED = False


CONFIGS = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
