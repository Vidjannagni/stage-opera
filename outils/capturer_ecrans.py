#!/usr/bin/env python3
"""Régénère les captures d'écran de l'application pour le rapport de stage.

Pourquoi un script plutôt que des captures à la main : les figures d'un rapport
doivent pouvoir être **refaites à l'identique** après une évolution de
l'interface. Le jeu de données est celui de la démonstration (`flask
demo-data`), la largeur et la définition sont fixées ici, et le cadrage ne
dépend donc pas de la taille de la fenêtre de celui qui capture.

Fonctionnement :

1. l'application est montée sur une base en mémoire, remplie avec le jeu de
   démonstration, et interrogée par le client de test de Flask — pas de serveur
   à lancer ni de session à ouvrir à la main ;
2. chaque page est écrite sur disque, les liens `/static/` étant réécrits en
   chemins absolus pour que la feuille de style suive ;
3. Chrome (mode « headless ») mesure la hauteur réelle de la page, puis la
   photographie en entier, à deux pixels par point pour rester net à
   l'impression ;
4. les captures sont enfin recadrées pour le rapport (figures trop hautes) et
   pour la soutenance (`img/slides/`, le haut de l'écran au format du cadre).

Usage :

    .venv/bin/python outils/capturer_ecrans.py [dossier_de_sortie]

Par défaut : `Rapport_stage_acad/img/`.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models import Projet, Scenario, ZonePreset  # noqa: E402

#: Largeur de rendu, en points CSS. 1440 est la largeur d'un écran de portable
#: courant : les captures montrent donc l'application telle qu'un conseiller la
#: voit, pas une version étirée.
LARGEUR = 1440
#: Deux pixels par point : les captures restent nettes une fois imprimées.
DENSITE = 2
#: Hauteur des captures « au-dessus de la ligne de flottaison ».
HAUTEUR_ECRAN = 900
#: Garde-fou : au-delà, une page est tronquée plutôt que d'occuper 20 Mo.
HAUTEUR_MAX = 5600

NAVIGATEURS = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")

#: Script injecté pour que Chrome nous rende la hauteur réelle de la page :
#: elle atterrit dans le titre du document, que `--dump-dom` nous renvoie.
MESURE = """
<script>
  window.addEventListener("load", function () {
    setTimeout(function () {
      document.title = "HAUTEUR:" + document.documentElement.scrollHeight;
    }, 600);
  });
</script>
"""


def navigateur() -> str:
    for nom in NAVIGATEURS:
        chemin = subprocess.run(["which", nom], capture_output=True, text=True)
        if chemin.returncode == 0:
            return chemin.stdout.strip()
    raise SystemExit(
        "Aucun navigateur Chrome/Chromium trouvé — installez-en un, ou prenez "
        "les captures à la main aux mêmes URL."
    )


def preparer_application():
    """Application de test, zones chargées, jeu de démonstration créé."""
    app = create_app("test")
    with app.app_context():
        db.create_all()
        zones = json.loads((RACINE / "data" / "zones.json").read_text("utf-8"))
        db.session.add_all([ZonePreset(**z) for z in zones])
        db.session.commit()
    app.test_cli_runner().invoke(args=["demo-data"])
    return app


def pages(app) -> dict[str, str]:
    """URL à photographier → nom de fichier, dans l'ordre du rapport."""
    with app.app_context():
        locatif = Projet.query.filter_by(type_operation="locatif").first()
        terrain = Projet.query.filter_by(type_operation="terrain").first()
        client_id = locatif.client_id
        scenarios = Scenario.query.filter_by(projet_id=locatif.id).all()
        ids = "&".join(f"ids={s.id}" for s in scenarios[:3])
        resultat_locatif = scenarios[0].id
        resultat_terrain = Scenario.query.filter_by(projet_id=terrain.id).first().id
        return {
            "app_vitrine": "/",
            "app_tableau_de_bord": "/",
            "app_clients": "/clients/",
            "app_client_detail": f"/clients/{client_id}",
            "app_brief": f"/clients/{client_id}/brief",
            "app_projets": "/projets/",
            "app_projet_locatif": f"/projets/{locatif.id}",
            "app_projet_terrain": f"/projets/{terrain.id}",
            "app_form_projet": f"/projets/{locatif.id}/modifier",
            "app_etude": f"/etudes/{locatif.id}",
            "app_etude_terrain": f"/etudes/{terrain.id}",
            "app_form_scenario": f"/scenarios/nouveau/{locatif.id}",
            "app_resultats_locatif": f"/scenarios/{resultat_locatif}/resultats",
            "app_resultats_terrain": f"/scenarios/{resultat_terrain}/resultats",
            "app_comparaison": f"/scenarios/comparer?{ids}",
        }


#: Recadrages produits après coup : une capture pleine hauteur ne tient pas
#: toujours sur une page de rapport. Les bornes sont en pixels de l'image
#: produite (donc à la densité ci-dessus) et suivent l'ordre gauche, haut,
#: droite, bas. Elles sont à revoir si la mise en page de l'écran change.
RECADRAGES = {
    "app_etude_carte": ("app_etude", (0, 0, LARGEUR * DENSITE, 2000)),
    "app_resultats_haut": ("app_resultats_locatif", (0, 0, LARGEUR * DENSITE, 1450)),
}

#: Recadrages destinés à la soutenance. Une diapositive ne montre jamais une
#: page entière : elle montre le haut de l'écran, dans le format du cadre qui
#: l'accueille — 2,44 pour les deux images côte à côte du gabarit, 3,20 pour
#: une image pleine largeur. La valeur est donc le rapport largeur/hauteur
#: attendu, et non des bornes en pixels : si la page s'allonge, le cadrage
#: reste le bon.
DIAPOSITIVES = {
    "app_vitrine": 2.44,
    "app_tableau_de_bord": 2.44,
    "app_client_detail": 2.44,
    "app_brief": 3.20,
    "app_projet_terrain": 2.44,
    "app_etude": 2.44,
    "app_form_scenario": 2.44,
    "app_resultats_locatif": 2.44,
    "app_comparaison": 2.44,
}

#: Largeur des images de diapositive, en pixels. Une diapositive 16:9 est
#: projetée en 1920 px de large au plus : au-delà, le fichier pèse pour rien.
LARGEUR_DIAPO = 1600

#: Pages photographiées à hauteur d'écran (elles servent d'illustration
#: d'ensemble) plutôt qu'en pleine hauteur.
CADRAGE_ECRAN = {"app_vitrine", "app_clients", "app_projets", "app_tableau_de_bord"}


def html_autonome(page: str) -> str:
    """Réécrit les liens de l'application en chemins absolus du dépôt."""
    statique = f"file://{RACINE / 'app' / 'static'}/"
    page = page.replace('href="/static/', f'href="{statique}')
    page = page.replace('src="/static/', f'src="{statique}')
    return page.replace("</head>", MESURE + "</head>")


def hauteur_page(chrome: str, fichier: Path) -> int:
    """Demande à Chrome la hauteur réelle de la page, via son titre."""
    sortie = subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
         f"--window-size={LARGEUR},{HAUTEUR_ECRAN}",
         "--virtual-time-budget=8000", "--dump-dom", f"file://{fichier}"],
        capture_output=True, text=True, timeout=120,
    ).stdout
    trouve = re.search(r"HAUTEUR:(\d+)", sortie)
    return min(int(trouve.group(1)), HAUTEUR_MAX) if trouve else HAUTEUR_ECRAN


def photographier(chrome: str, fichier: Path, sortie: Path, hauteur: int) -> None:
    subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--hide-scrollbars", f"--force-device-scale-factor={DENSITE}",
         f"--window-size={LARGEUR},{hauteur}",
         "--virtual-time-budget=8000",
         f"--screenshot={sortie}", f"file://{fichier}"],
        capture_output=True, timeout=180,
    )


def diapositives(destination: Path) -> None:
    """Écrit dans `slides/` le haut de chaque écran, au format des cadres."""
    from PIL import Image

    dossier = destination / "slides"
    dossier.mkdir(exist_ok=True)
    for nom, rapport in DIAPOSITIVES.items():
        origine = destination / f"{nom}.png"
        if not origine.exists():
            print(f"  ⨯ slides/{nom}.png — {origine.name} manquante")
            continue
        with Image.open(origine) as image:
            hauteur = min(round(image.width / rapport), image.height)
            vignette = image.crop((0, 0, image.width, hauteur))
            largeur = min(LARGEUR_DIAPO, vignette.width)
            vignette = vignette.resize(
                (largeur, round(largeur * hauteur / vignette.width)),
                Image.LANCZOS,
            )
            vignette.save(dossier / f"{nom}.png")
        print(f"  ✓ slides/{nom}.png — {vignette.width}×{vignette.height} px")


def main() -> None:
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else RACINE / "Rapport_stage_acad" / "img"
    destination.mkdir(parents=True, exist_ok=True)
    chrome = navigateur()
    app = preparer_application()
    http = app.test_client()

    with tempfile.TemporaryDirectory() as travail:
        travail = Path(travail)
        adresses = pages(app)
        # La vitrine se photographie déconnecté : c'est la seule page publique.
        vitrine = html_autonome(http.get("/").get_data(as_text=True))
        http.post("/auth/login",
                  data={"email": "demo@choubel.com", "password": "demo1234"},
                  follow_redirects=True)

        for nom, url in adresses.items():
            source = travail / f"{nom}.html"
            if nom == "app_vitrine":
                source.write_text(vitrine, encoding="utf-8")
            else:
                reponse = http.get(url)
                if reponse.status_code != 200:
                    print(f"  ⨯ {nom} — HTTP {reponse.status_code}, ignorée")
                    continue
                source.write_text(
                    html_autonome(reponse.get_data(as_text=True)), encoding="utf-8"
                )
            hauteur = (
                HAUTEUR_ECRAN if nom in CADRAGE_ECRAN
                else hauteur_page(chrome, source)
            )
            cible = destination / f"{nom}.png"
            photographier(chrome, source, cible, hauteur)
            poids = cible.stat().st_size // 1024 if cible.exists() else 0
            print(f"  ✓ {cible.name} — {LARGEUR}×{hauteur} pt, {poids} Ko")

    for nom, (source, bornes) in RECADRAGES.items():
        origine = destination / f"{source}.png"
        if not origine.exists():
            continue
        from PIL import Image

        with Image.open(origine) as image:
            image.crop(bornes).save(destination / f"{nom}.png")
        print(f"  ✓ {nom}.png — recadrage de {source}.png")

    diapositives(destination)

    print(f"\nCaptures écrites dans {destination}")


if __name__ == "__main__":
    main()
