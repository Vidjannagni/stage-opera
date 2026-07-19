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

    @app.template_filter("montant")
    def montant(valeur) -> str:
        """Format monétaire : 1 234 567 (arrondi à l'unité, séparateur espace)."""
        if valeur is None:
            return "—"
        return f"{valeur:,.0f}".replace(",", " ").replace("−", "-")

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

    @app.cli.command("demo-data")
    def demo_data() -> None:
        """Crée le jeu de démonstration (compte demo@choubel.com / demo1234)."""
        from .models import Client, LigneTravaux, Projet, Scenario, User, ZonePreset

        if User.query.filter_by(email="demo@choubel.com").first():
            print("Le jeu de démonstration existe déjà (demo@choubel.com / demo1234).")
            return
        zone_maroc = ZonePreset.query.filter_by(nom="Maroc").first()
        if zone_maroc is None:
            print("Lancez d'abord : flask seed-zones")
            return

        demo = User(email="demo@choubel.com", nom="Conseiller Démo")
        demo.set_password("demo1234")
        db.session.add(demo)
        db.session.flush()

        client = Client(
            user_id=demo.id, nom="M. Alaoui", email="k.alaoui@example.com",
            telephone="+212 6 00 00 00 00",
            notes="Premier investissement locatif ; objectif de cash-flow neutre.",
        )
        db.session.add(client)
        db.session.flush()

        projet = Projet(
            client_id=client.id, zone_id=zone_maroc.id,
            nom="Appartement Gauthier — Casablanca",
            adresse="Quartier Gauthier, Casablanca", surface_m2=85,
            prix_bien=1_200_000, budget_travaux=150_000, loyer_mensuel=8_500,
            charges_copro_annuelles=7_200, assurance_annuelle=1_800,
            frais_gestion_pct=5.0, vacance_pct=5.0, entretien_annuel=3_000,
            taxe_annuelle=4_500,
        )
        db.session.add(projet)
        db.session.flush()

        db.session.add_all([
            LigneTravaux(projet_id=projet.id, libelle="Cuisine équipée",
                         categorie="Cuisine / Salle de bain", montant=80_000),
            LigneTravaux(projet_id=projet.id, libelle="Rafraîchissement peinture",
                         categorie="Décoration", montant=40_000),
            LigneTravaux(projet_id=projet.id, libelle="Mise aux normes électricité",
                         categorie="Électricité / Plomberie", montant=30_000),
        ])

        communs = dict(
            projet_id=projet.id, horizon_annees=20,
            revalorisation_loyer_pct=1.5, revalorisation_bien_pct=2.0,
            frais_revente_pct=2.5, taux_actualisation=3.0,
        )
        db.session.add_all([
            Scenario(nom="Crédit 20 ans", mode="credit", apport=300_000,
                     taux_interet=4.9, taux_assurance=0.35, duree_annees=20, **communs),
            Scenario(nom="Crédit 25 ans", mode="credit", apport=200_000,
                     taux_interet=5.2, taux_assurance=0.35, duree_annees=25, **communs),
            Scenario(nom="Achat cash", mode="cash", apport=0,
                     taux_interet=0, taux_assurance=0, duree_annees=20, **communs),
        ])
        db.session.commit()
        print("Jeu de démonstration créé — connexion : demo@choubel.com / demo1234")
