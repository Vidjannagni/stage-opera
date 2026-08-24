"""Garde-fous de la mise en ligne.

L'outil part vivre sur une adresse publique, avec les dossiers de vrais
clients dedans. Ces tests couvrent ce qui n'existe que pour ce moment-là :
le verrou d'inscription, les pages d'erreur, le compte du conseiller, et le
refus d'être indexé.

Les réglages qui n'ont de sens qu'en ligne s'activent par variable
d'environnement : sans elles, le comportement local reste identique.
"""
import pytest

from app import create_app
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


# ── Refus de démarrer sans les deux secrets ──────────────────────────────────
def test_la_production_refuse_de_demarrer_sans_secret_key(monkeypatch):
    """Les classes de configuration lisent l'environnement à l'import : c'est
    donc l'attribut, et non la variable, qu'il faut ramener à sa valeur de
    développement pour rejouer la situation."""
    from config import ProdConfig

    monkeypatch.setattr(ProdConfig, "SECRET_KEY", "dev-change-me")
    monkeypatch.setenv("CODE_INSCRIPTION", "choubel-2026")

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app("prod")


def test_la_production_refuse_de_demarrer_sans_code_dinscription(monkeypatch):
    """Une adresse publique sans code, c'est un outil où n'importe qui crée un
    compte. La variable s'ajoute en une ligne ; la fuite ne se rattrape pas."""
    from config import ProdConfig

    monkeypatch.setattr(ProdConfig, "SECRET_KEY", "une-cle-de-test-assez-longue")
    monkeypatch.delenv("CODE_INSCRIPTION", raising=False)

    with pytest.raises(RuntimeError, match="CODE_INSCRIPTION"):
        create_app("prod")


def test_une_inscription_ouverte_doit_etre_assumee(monkeypatch):
    """Ouvrir l'inscription reste possible — à condition de l'écrire."""
    from config import ProdConfig

    monkeypatch.setattr(ProdConfig, "SECRET_KEY", "une-cle-de-test-assez-longue")
    monkeypatch.setenv("CODE_INSCRIPTION", "ouvert")

    assert create_app("prod") is not None


# ── Pages d'erreur ───────────────────────────────────────────────────────────
def test_une_adresse_inconnue_rend_une_page_de_l_application(http):
    """Sans gestionnaire, le conseiller tombait sur la page blanche de
    Werkzeug : il croit l'outil cassé et n'a aucun chemin de retour."""
    reponse = http.get("/une-adresse-qui-nexiste-pas")
    page = reponse.get_data(as_text=True)

    assert reponse.status_code == 404
    assert "Cette page n&#39;existe pas" in page
    assert "RentImmo" in page                      # la charte, pas une page nue
    assert "Retour à l'accueil" in page            # et toujours une sortie


def test_le_dossier_d_un_autre_conseiller_rend_la_page_403(http, app):
    """Le cloisonnement répond 404 (l'existence même ne se devine pas) ; c'est
    la page de l'application qui s'affiche, pas une trace technique."""
    inscrire_et_connecter(http, email="premier@choubel.com")
    reponse = http.get("/clients/999")

    assert reponse.status_code == 404
    assert "Traceback" not in reponse.get_data(as_text=True)


# ── Le compte du conseiller ──────────────────────────────────────────────────
def test_le_conseiller_change_son_mot_de_passe(http, app):
    """Sans cet écran, le mot de passe provisoire attribué en console resterait
    le mot de passe définitif — connu de l'administrateur."""
    inscrire_et_connecter(http, email="rene@choubel.com")

    http.post("/auth/mon-compte", data={
        "actuel": "motdepasse", "nouveau": "nouveau-mot-de-passe",
        "confirm": "nouveau-mot-de-passe",
    }, follow_redirects=True)

    with app.app_context():
        compte = User.query.filter_by(email="rene@choubel.com").one()
        assert compte.check_password("nouveau-mot-de-passe")
        assert not compte.check_password("motdepasse")


def test_un_mauvais_mot_de_passe_actuel_ne_change_rien(http, app):
    inscrire_et_connecter(http, email="rene@choubel.com")

    reponse = http.post("/auth/mon-compte", data={
        "actuel": "ce-nest-pas-le-bon", "nouveau": "nouveau-mot-de-passe",
        "confirm": "nouveau-mot-de-passe",
    })

    assert "Mot de passe actuel incorrect" in reponse.get_data(as_text=True)
    with app.app_context():
        assert User.query.filter_by(email="rene@choubel.com").one().check_password("motdepasse")


def test_mon_compte_exige_d_etre_connecte(http):
    assert http.get("/auth/mon-compte").status_code == 302


# ── Ni moteur de recherche, ni promesse de courriel ──────────────────────────
def test_loutil_refuse_detre_indexe(http):
    """Des dossiers de clients réels n'ont rien à faire dans un moteur de
    recherche — et une vitrine hébergée sur un compte d'étudiant n'a pas à
    passer pour le site officiel du cabinet."""
    robots = http.get("/robots.txt")
    assert robots.status_code == 200
    assert "Disallow: /" in robots.get_data(as_text=True)
    assert 'name="robots" content="noindex' in http.get("/").get_data(as_text=True)


def test_la_page_de_connexion_dit_quoi_faire_sans_mot_de_passe(http):
    """L'outil n'envoie pas de courriel : chercher un lien « mot de passe
    oublié » qui n'existe pas est une impasse silencieuse."""
    page = http.get("/auth/login").get_data(as_text=True)
    assert "n'envoie pas de courriel" in page


# ── L'adresse de la base fournie par l'hébergeur ─────────────────────────────
def test_l_url_postgres_de_l_hebergeur_est_normalisee(monkeypatch):
    """Render, Railway et Heroku annoncent leur base en « postgres:// », que
    SQLAlchemy 2 ne reconnaît plus, et sans nommer de pilote. Sans cette
    normalisation, l'application ne se connecte pas — et l'erreur ne dit pas
    pourquoi."""
    from config import uri_base_de_donnees

    for annoncee in ("postgres://u:p@hote:5432/rentimmo",
                     "postgresql://u:p@hote:5432/rentimmo"):
        monkeypatch.setenv("DATABASE_URL", annoncee)
        assert uri_base_de_donnees() == "postgresql+psycopg://u:p@hote:5432/rentimmo"


def test_sans_base_declaree_l_application_reste_sur_sqlite(monkeypatch):
    """Un poste local n'a pas de PostgreSQL : le repli est silencieux et voulu."""
    from config import uri_base_de_donnees

    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert uri_base_de_donnees().startswith("sqlite:///")


# ── Ce que l'hébergement gratuit ne sait pas faire ───────────────────────────
def test_l_export_pdf_absent_se_dit_au_lieu_de_planter(http, app, monkeypatch):
    """WeasyPrint dépend de bibliothèques système que les hébergements gratuits
    ne fournissent pas toujours. Sans rattrapage, le conseiller obtient une page
    d'erreur muette et croit l'outil cassé."""
    import builtins

    from helpers import creer_parcours_complet

    inscrire_et_connecter(http)
    _, _, scenario_id = creer_parcours_complet(http, app)

    importer = builtins.__import__

    def sans_weasyprint(nom, *args, **kwargs):
        if nom == "weasyprint":
            raise OSError("libpango introuvable")
        return importer(nom, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", sans_weasyprint)
    reponse = http.get(f"/exports/scenario/{scenario_id}/pdf", follow_redirects=True)

    page = reponse.get_data(as_text=True)
    assert reponse.status_code == 200
    assert "L&#39;export PDF n&#39;est pas disponible" in page
    assert "export Excel" in page
