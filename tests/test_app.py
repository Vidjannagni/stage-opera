"""Tests de fumée du squelette (semaine 1) — les tests du moteur arrivent en semaine 2."""
import pytest

from app import create_app
from app.extensions import db
from app.models import ZonePreset


@pytest.fixture()
def app():
    app = create_app("test")
    with app.app_context():
        db.create_all()
        db.session.add(ZonePreset(nom="Maroc", devise="MAD", taux_enregistrement=4.0,
                                  taux_publicite_fonciere=1.5, taux_notaire=1.0,
                                  taux_frais_divers=0.5, taux_imposition_defaut=15.0,
                                  par_defaut=True))
        db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def test_accueil_repond(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "rentabilit" in response.get_data(as_text=True)


def test_zone_par_defaut_maroc(app):
    with app.app_context():
        zone = ZonePreset.query.filter_by(par_defaut=True).one()
        assert zone.nom == "Maroc"
        assert zone.devise == "MAD"
        assert zone.taux_frais_total == pytest.approx(7.0)
