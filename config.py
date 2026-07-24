"""Configuration de l'application par environnement.

Le même code tourne en local (SQLite) et en production (PostgreSQL via
DATABASE_URL). Les secrets viennent des variables d'environnement (.env).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'rentimmo.sqlite3'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


CONFIGS = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
