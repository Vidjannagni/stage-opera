"""Garde-fous de la mise en ligne.

Ces réglages ne s'activent que par variable d'environnement : sans elles,
le comportement local reste identique.
"""
from app.models import User
from helpers import inscrire_et_connecter


def test_inscription_libre_sans_code_configure(http, app):
    """Sans CODE_INSCRIPTION, l'inscription reste ouverte comme en local."""
    reponse = inscrire_et_connecter(http, email="libre@choubel.com")
    assert reponse.status_code == 200
    with app.app_context():
        assert User.query.filter_by(email="libre@choubel.com").count() == 1


def test_inscription_refusee_sans_le_bon_code(http, app, monkeypatch):
    monkeypatch.setenv("CODE_INSCRIPTION", "choubel-2026")

    refus = http.post(
        "/auth/register",
        data={"nom": "Intrus", "email": "intrus@example.com",
              "password": "motdepasse", "confirm": "motdepasse",
              "code_inscription": "au-hasard"},
    )
    assert "Code d&#39;inscription invalide" in refus.get_data(as_text=True)
    with app.app_context():
        assert User.query.filter_by(email="intrus@example.com").count() == 0

    http.post(
        "/auth/register",
        data={"nom": "Conseiller", "email": "conseiller@choubel.com",
              "password": "motdepasse", "confirm": "motdepasse",
              "code_inscription": "choubel-2026"},
        follow_redirects=True,
    )
    with app.app_context():
        assert User.query.filter_by(email="conseiller@choubel.com").count() == 1
