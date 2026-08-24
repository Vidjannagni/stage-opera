"""Factory de l'application RentImmo — outil d'analyse de rentabilité
d'investissement immobilier (Choubel Consulting)."""
import json
import os
from pathlib import Path

import click
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

    if config_name == "prod":
        # Un SECRET_KEY laissé par défaut rendrait les sessions falsifiables :
        # mieux vaut refuser de démarrer que de servir une application ouverte.
        if app.config["SECRET_KEY"] == "dev-change-me":
            raise RuntimeError(
                "SECRET_KEY doit être défini en production "
                "(variable d'environnement)."
            )
        # Derrière le proxy de l'hébergeur : conserve le schéma et l'hôte
        # d'origine, sans quoi les redirections repassent en http.
        from werkzeug.middleware.proxy_fix import ProxyFix

        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

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
    from .blueprints.etudes import bp as etudes_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(clients_bp, url_prefix="/clients")
    app.register_blueprint(projets_bp, url_prefix="/projets")
    app.register_blueprint(scenarios_bp, url_prefix="/scenarios")
    app.register_blueprint(exports_bp, url_prefix="/exports")
    app.register_blueprint(etudes_bp, url_prefix="/etudes")

    @app.context_processor
    def injecter_suggestions():
        """Rend les listes de suggestions disponibles dans tous les gabarits."""
        from .suggestions import TOUTES

        return {"SUGGESTIONS": TOUTES}

    @app.template_filter("pourcent")
    def pourcent(valeur, decimales: int = 2) -> str:
        """Pourcentage à la française : 5.27 → « 5,27 % ».

        Les montants étaient déjà écrits à la française (espace de milliers),
        les pourcentages non : « 5.27 % » au milieu d'une phrase française est
        une faute de composition, et l'écart sautait aux yeux dès qu'un même
        écran affichait les deux.
        """
        from .core.format_fr import pct_texte

        return "—" if valeur is None else pct_texte(valeur, decimales)

    @app.template_filter("montant")
    def montant(valeur, decimales: int = 0) -> str:
        """Format monétaire français : 1 234 567 — ou 7 752,15 avec décimales.

        Les mensualités sont les seuls montants affichés au centime : c'est ce
        que la banque prélève, l'arrondir donnerait un chiffre invérifiable.
        """
        if valeur is None:
            return "—"
        texte = f"{valeur:,.{decimales}f}".replace(",", " ").replace("−", "-")
        return texte.replace(".", ",") if decimales else texte

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
    @click.option("--reset", is_flag=True,
                  help="Efface le jeu de démonstration existant et le recrée.")
    def demo_data(reset: bool) -> None:
        """Crée le jeu de démonstration (compte demo@choubel.com / demo1234)."""
        from .models import (
            Brief, Client, LigneTravaux, Projet, Scenario, User, ZonePreset,
        )

        existant = User.query.filter_by(email="demo@choubel.com").first()
        if existant and not reset:
            print(
                "Le jeu de démonstration existe déjà (demo@choubel.com / demo1234).\n"
                "Pour le régénérer : flask demo-data --reset"
            )
            return
        if existant:
            # Les dossiers du compte démo d'abord (la cascade emporte projets,
            # scénarios, travaux et brief), puis le compte lui-même. Les autres
            # conseillers ne sont pas touchés.
            for dossier in existant.clients.all():
                db.session.delete(dossier)
            db.session.delete(existant)
            db.session.commit()
            print("Ancien jeu de démonstration supprimé.")

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
            situation_professionnelle="Chef d'entreprise",
            nationalite="Marocaine", budget_disponible=1_500_000,
            notes="Premier investissement locatif ; objectif de cash-flow neutre.",
        )
        db.session.add(client)
        db.session.flush()

        db.session.add(Brief(
            client_id=client.id, type_bien="Appartement", standing="Moyen standing",
            zone_recherchee="Casablanca — Gauthier, Maârif", superficie_min=70,
            superficie_max=100, nb_chambres=2, nb_salles_bains=1, nb_salons=1,
            etage="À partir du 2e", orientation="Sud",
            commodites="Transports, écoles primaires, commerces de proximité",
            type_acquisition="existant", budget_min=1_000_000, budget_max=1_500_000,
            mode_financement="pret", objectif="revenu", horizon_annees=20,
        ))

        projet = Projet(
            client_id=client.id, zone_id=zone_maroc.id,
            nom="Appartement Gauthier — Casablanca",
            adresse="Quartier Gauthier, Casablanca", surface_m2=85,
            type_operation="locatif", statut="visites",
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

        # Second client : une opération sans loyer, pour montrer que la valeur
        # peut venir entièrement de la plus-value (cas type du cabinet). C'est
        # bien un second dossier client, et pas un second bien du premier : le
        # brief de M. Alaoui dit qu'il cherche un appartement, et l'outil
        # signalerait — à raison — qu'un terrain ne répond pas à sa demande.
        cliente = Client(
            user_id=demo.id, nom="Mme Benali", email="s.benali@example.com",
            telephone="+212 6 11 11 11 11",
            situation_professionnelle="Profession libérale",
            nationalite="Marocaine", budget_disponible=1_200_000,
            notes="Portage foncier ; pas de besoin de revenu immédiat.",
        )
        db.session.add(cliente)
        db.session.flush()

        db.session.add(Brief(
            client_id=cliente.id, type_bien="Terrain",
            zone_recherchee="Axe Casablanca — Berrechid",
            superficie_min=20_000, superficie_max=30_000,
            viabilisation="Voirie goudronnée", topographie="Plat",
            zone_urbanisme="Zone villa", constructibilite="Constructible",
            commodites="Accès routier goudronné, Quartier en développement",
            type_acquisition="terrain_nu", budget_min=900_000, budget_max=1_200_000,
            mode_financement="comptant", objectif="plus_value", horizon_annees=10,
        ))

        terrain = Projet(
            client_id=cliente.id, zone_id=zone_maroc.id,
            nom="Terrain 3 ha — périphérie de Casablanca",
            adresse="Axe Casablanca — Berrechid", surface_m2=30_000,
            type_operation="terrain", statut="compromis",
            prix_bien=1_000_000, budget_travaux=0, loyer_mensuel=0,
        )
        db.session.add(terrain)
        db.session.flush()
        db.session.add(Scenario(
            projet_id=terrain.id, nom="Portage 10 ans", mode="cash", apport=0,
            taux_interet=0, taux_assurance=0, duree_annees=10,
            horizon_annees=10, revalorisation_loyer_pct=0,
            revalorisation_bien_pct=0, frais_revente_pct=0,
            taux_actualisation=3.0, prix_revente=16_070_000,
        ))

        db.session.commit()
        print("Jeu de démonstration créé — connexion : demo@choubel.com / demo1234")
