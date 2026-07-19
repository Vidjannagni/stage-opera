"""Fixtures partagées : application de test avec zones seedées, client HTTP."""
import json
from pathlib import Path

import pytest

from app import create_app
from app.extensions import db
from app.models import ZonePreset


@pytest.fixture()
def app():
    app = create_app("test")
    with app.app_context():
        db.create_all()
        zones = json.loads(
            (Path(app.root_path).parent / "data" / "zones.json").read_text("utf-8")
        )
        db.session.add_all([ZonePreset(**z) for z in zones])
        db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture()
def http(app):
    return app.test_client()
