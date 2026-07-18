"""Factory de l'application RentImmo — outil d'analyse de rentabilité
d'investissement immobilier (Choubel Consulting)."""
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from config import CONFIGS
from .extensions import csrf, db, login_manager, migrate


def create_app(config_name: str | None = None) -> Flask:
    load_dotenv()
    config_name = config_name or os.environ.get("FLASK_ENV", "dev")

    app = Flask(__name__)
    app.config.from_object(CONFIGS.get(config_name, CONFIGS["dev"]))
    Path(app.instance_path).mkdir(exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from . import models  # noqa: F401 — enregistre les modèles pour Alembic

    from .blueprints.main import bp as main_bp
    from .blueprints.auth import bp as auth_bp
    from .blueprints.clients import bp as clients_bp
    from .blueprints.projets import bp as projets_bp
    from .blueprints.scenarios import bp as scenarios_bp
    from .blueprints.exports import bp as exports_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(clients_bp, url_prefix="/clients")
    app.register_blueprint(projets_bp, url_prefix="/projets")
    app.register_blueprint(scenarios_bp, url_prefix="/scenarios")
    app.register_blueprint(exports_bp, url_prefix="/exports")

    register_cli(app)
    return app


def register_cli(app: Flask) -> None:
    @app.cli.command("seed-zones")
    def seed_zones() -> None:
        """Charge les préréglages de zones de marché depuis data/zones.json."""
        from .models import ZonePreset

        zones_file = Path(app.root_path).parent / "data" / "zones.json"
        zones = json.loads(zones_file.read_text(encoding="utf-8"))
        created, updated = 0, 0
        for data in zones:
            zone = ZonePreset.query.filter_by(nom=data["nom"]).first()
            if zone is None:
                db.session.add(ZonePreset(**data))
                created += 1
            else:
                for key, value in data.items():
                    setattr(zone, key, value)
                updated += 1
        db.session.commit()
        print(f"Zones : {created} créée(s), {updated} mise(s) à jour.")
