"""Modèle de données — dérivé des formules du cahier des charges (semaine 1).

Principe : les résultats (rendements, TRI, VAN…) ne sont JAMAIS stockés,
ils sont recalculés à la volée pour rester cohérents avec les hypothèses.
"""
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db, login_manager


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    """Consultant du cabinet — chaque consultant ne voit que ses clients."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    nom = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    clients = db.relationship("Client", back_populates="conseiller", lazy="dynamic")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


class ZonePreset(db.Model):
    """Zone de marché : taux de frais d'acquisition, fiscalité et devise.

    Tous les taux sont exprimés en pourcentage du prix du bien (ex : 4.0 = 4 %).
    Le taux d'imposition est un taux effectif appliqué au revenu locatif net.
    """

    __tablename__ = "zone_presets"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), unique=True, nullable=False)
    devise = db.Column(db.String(8), nullable=False, default="MAD")
    taux_enregistrement = db.Column(db.Float, nullable=False, default=0.0)
    taux_publicite_fonciere = db.Column(db.Float, nullable=False, default=0.0)
    taux_notaire = db.Column(db.Float, nullable=False, default=0.0)
    taux_frais_divers = db.Column(db.Float, nullable=False, default=0.0)
    taux_imposition_defaut = db.Column(db.Float, nullable=False, default=0.0)
    par_defaut = db.Column(db.Boolean, nullable=False, default=False)
    personnalisable = db.Column(db.Boolean, nullable=False, default=False)

    projets = db.relationship("Projet", back_populates="zone", lazy="dynamic")

    @property
    def taux_frais_total(self) -> float:
        """Somme des taux de frais d'acquisition de la zone (en %)."""
        return (
            self.taux_enregistrement
            + self.taux_publicite_fonciere
            + self.taux_notaire
            + self.taux_frais_divers
        )


class Client(db.Model):
    """Dossier client (investisseur) suivi par un conseiller."""

    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    nom = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255))
    telephone = db.Column(db.String(40))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    conseiller = db.relationship("User", back_populates="clients")
    projets = db.relationship(
        "Projet", back_populates="client", lazy="dynamic",
        cascade="all, delete-orphan",
    )


class Projet(db.Model):
    """Le bien étudié : acquisition, travaux et exploitation locative.

    Les taux hérités de la zone peuvent être surchargés au niveau du projet
    (colonnes *_override, NULL = utiliser la valeur de la zone).
    """

    __tablename__ = "projets"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    zone_id = db.Column(db.Integer, db.ForeignKey("zone_presets.id"), nullable=False)
    nom = db.Column(db.String(160), nullable=False)
    adresse = db.Column(db.String(255))
    surface_m2 = db.Column(db.Float)

    # Acquisition
    prix_bien = db.Column(db.Float, nullable=False, default=0.0)
    budget_travaux = db.Column(db.Float, nullable=False, default=0.0)
    taux_frais_override = db.Column(db.Float)  # % du prix ; NULL = taux de la zone

    # Exploitation
    loyer_mensuel = db.Column(db.Float, nullable=False, default=0.0)
    charges_copro_annuelles = db.Column(db.Float, nullable=False, default=0.0)
    assurance_annuelle = db.Column(db.Float, nullable=False, default=0.0)
    frais_gestion_pct = db.Column(db.Float, nullable=False, default=0.0)  # % du loyer
    vacance_pct = db.Column(db.Float, nullable=False, default=0.0)  # % du loyer
    entretien_annuel = db.Column(db.Float, nullable=False, default=0.0)
    taxe_annuelle = db.Column(db.Float, nullable=False, default=0.0)
    taux_imposition_override = db.Column(db.Float)  # NULL = taux de la zone

    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    client = db.relationship("Client", back_populates="projets")
    zone = db.relationship("ZonePreset", back_populates="projets")
    lignes_travaux = db.relationship(
        "LigneTravaux", back_populates="projet", lazy="dynamic",
        cascade="all, delete-orphan",
    )
    scenarios = db.relationship(
        "Scenario", back_populates="projet", lazy="dynamic",
        cascade="all, delete-orphan",
    )

    @property
    def taux_frais_acquisition(self) -> float:
        """Taux de frais applicable (en %) : surcharge projet, sinon zone."""
        if self.taux_frais_override is not None:
            return self.taux_frais_override
        return self.zone.taux_frais_total

    @property
    def taux_imposition(self) -> float:
        """Taux d'imposition effectif (en %) : surcharge projet, sinon zone."""
        if self.taux_imposition_override is not None:
            return self.taux_imposition_override
        return self.zone.taux_imposition_defaut


class LigneTravaux(db.Model):
    """Poste de travaux détaillé (module de la semaine 4)."""

    __tablename__ = "lignes_travaux"

    id = db.Column(db.Integer, primary_key=True)
    projet_id = db.Column(db.Integer, db.ForeignKey("projets.id"), nullable=False)
    libelle = db.Column(db.String(160), nullable=False)
    categorie = db.Column(db.String(80))
    montant = db.Column(db.Float, nullable=False, default=0.0)

    projet = db.relationship("Projet", back_populates="lignes_travaux")


class Scenario(db.Model):
    """Hypothèse de financement et de projection pour un projet.

    Un même bien peut être confronté à plusieurs montages (cash, crédit,
    durées/taux variables) : la comparaison de scénarios est native.
    """

    __tablename__ = "scenarios"

    MODES = ("cash", "credit")

    id = db.Column(db.Integer, primary_key=True)
    projet_id = db.Column(db.Integer, db.ForeignKey("projets.id"), nullable=False)
    nom = db.Column(db.String(120), nullable=False)
    mode = db.Column(db.String(10), nullable=False, default="credit")

    # Financement (mode crédit)
    apport = db.Column(db.Float, nullable=False, default=0.0)
    taux_interet = db.Column(db.Float, nullable=False, default=0.0)  # % annuel
    taux_assurance = db.Column(db.Float, nullable=False, default=0.0)  # % annuel
    duree_annees = db.Column(db.Integer, nullable=False, default=20)

    # Projection
    horizon_annees = db.Column(db.Integer, nullable=False, default=20)
    revalorisation_loyer_pct = db.Column(db.Float, nullable=False, default=0.0)
    revalorisation_bien_pct = db.Column(db.Float, nullable=False, default=0.0)
    frais_revente_pct = db.Column(db.Float, nullable=False, default=0.0)
    taux_actualisation = db.Column(db.Float, nullable=False, default=3.0)

    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    projet = db.relationship("Projet", back_populates="scenarios")
