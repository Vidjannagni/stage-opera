"""Ce qu'il est logique de demander, selon le type de bien recherché.

Un même brief sert pour un terrain, un appartement, un immeuble de rapport ou
un local commercial. Or les questions ne se recouvrent pas : le standing ne
veut rien dire pour un terrain, la VEFA n'existe pas pour un terrain nu, un
local se juge sur son état et son flux de passage, un immeuble de rapport sur
son nombre de lots.

Poser une question sans objet, c'est la faire remplir au hasard — et un brief
rempli au hasard oriente une recherche pour rien. Ce module tient donc en un
seul endroit ce qui est demandé pour chaque type de bien :

- le formulaire s'en sert pour n'exiger, ne valider et n'enregistrer que les
  champs qui s'appliquent — côté serveur, seule barrière qui compte ;
- la page du brief s'en sert pour masquer les autres à la volée, sans
  rechargement, quand le conseiller change de type en cours de saisie ;
- la fiche client s'en sert pour n'afficher que ce qui a été demandé.

Ajouter un type de bien, c'est ajouter une entrée dans ``PROFILS`` : rien
d'autre n'est à toucher.
"""

#: Types de biens proposés au brief. Les quatre premiers sont ceux cités par
#: le cabinet lors du cadrage (cf. docs/retour_cabinet.md).
TYPES_BIEN = ("Terrain", "Villa", "Appartement", "Immeuble", "Local commercial", "Autre")

#: Trois niveaux de standing. Le cabinet en citait davantage, mais « social »
#: et « luxe » se plaidaient toujours par rapport aux trois autres : garder
#: cinq nuances, c'était surtout garantir que deux conseillers classent le même
#: bien différemment.
STANDINGS = ("Économique", "Moyen standing", "Haut standing")

#: Pour un local commercial, l'état remplace le standing : ce qui se négocie
#: n'est pas le niveau de gamme mais le montant des travaux à prévoir.
ETATS_LOCAL = ("Neuf", "Bon état", "À rafraîchir", "À rénover entièrement")

TOPOGRAPHIES = ("Plat", "Légère pente", "Forte pente", "Accidenté")

#: Ce qui décide de ce qu'on a le droit de bâtir — donc de la valeur du terrain.
CONSTRUCTIBILITES = (
    "À vérifier au plan d'aménagement", "Constructible",
    "Constructible sous conditions", "Non constructible",
)

ZONES_URBANISME = [
    "Zone villa", "Zone immeuble", "Zone économique", "Zone industrielle",
    "Zone touristique", "Zone agricole", "Hors périmètre urbain",
]

#: Réseaux dont la présence change le coût d'entrée d'un terrain : les amener
#: se chiffre, et se chiffre lourdement.
RESEAUX = [
    "Eau potable", "Électricité", "Assainissement", "Voirie goudronnée",
    "Téléphone et fibre",
]

#: Catalogue des modes d'acquisition — ce sont les valeurs enregistrées. Chaque
#: type de bien n'en propose qu'une partie, sous un libellé qui lui parle.
ACQUISITIONS = {
    "existant": "Bien déjà construit",
    "neuf": "Neuf, jamais habité",
    "vefa": "Achat sur plan (VEFA)",
    "terrain_nu": "Terrain nu",
    "terrain_viabilise": "Terrain viabilisé",
    "lot_lotissement": "Lot en lotissement",
    "bail": "Bail commercial",
}

_DISTRIBUTION = ("nb_chambres", "nb_salles_bains", "nb_salons", "etage", "orientation")
_TERRAIN = ("viabilisation", "topographie", "zone_urbanisme", "constructibilite")

#: Tous les champs qui n'apparaissent que pour certains types. Les autres —
#: zone, superficie, budget, financement, objectif, horizon — sont demandés
#: quel que soit le bien.
CHAMPS_OPTIONNELS = ("standing", "etat_local", "nb_lots") + _DISTRIBUTION + _TERRAIN

_COMMODITES_RESIDENTIELLES = [
    "Transports en commun", "Écoles et crèches", "Commerces de proximité",
    "Centre commercial", "Cliniques et pharmacies", "Espaces verts",
    "Mosquée", "Bord de mer", "Accès autoroute", "Parking privatif",
    "Gardiennage",
]

PROFILS = {
    "Appartement": {
        "designation": "un appartement",
        "champs": ("standing",) + _DISTRIBUTION,
        "acquisitions": ("existant", "neuf", "vefa"),
        "acquisitions_libelles": {"existant": "Ancien, déjà habité"},
        "libelles": {
            "superficie_min": "Superficie habitable minimale (m²)",
            "superficie_max": "Superficie habitable maximale (m²)",
            "type_acquisition": "Type d'acquisition",
        },
        "commodites": _COMMODITES_RESIDENTIELLES + ["Ascenseur", "Balcon ou terrasse"],
        "note": "Standing, distribution et commodités du quartier : "
                "c'est le confort d'usage qui se décrit ici.",
    },
    "Villa": {
        "designation": "une villa",
        # Une villa n'a pas d'étage à choisir, et l'ascenseur n'a pas de sens.
        "champs": ("standing", "nb_chambres", "nb_salles_bains", "nb_salons", "orientation"),
        "acquisitions": ("existant", "neuf", "vefa"),
        "acquisitions_libelles": {"existant": "Ancienne, déjà habitée"},
        "libelles": {
            "superficie_min": "Superficie minimale (m², terrain compris)",
            "superficie_max": "Superficie maximale (m², terrain compris)",
            "type_acquisition": "Type d'acquisition",
        },
        "commodites": _COMMODITES_RESIDENTIELLES + ["Jardin", "Piscine", "Résidence fermée"],
        "note": "Pour une villa, la superficie s'entend terrain compris ; "
                "ni étage ni ascenseur.",
    },
    "Immeuble": {
        "designation": "un immeuble de rapport",
        # Un immeuble de rapport ne se décrit pas pièce par pièce : ce qui
        # compte est le nombre de lots et l'attrait locatif du quartier.
        "champs": ("standing", "nb_lots"),
        "acquisitions": ("existant", "neuf"),
        "acquisitions_libelles": {"existant": "Ancien, déjà exploité"},
        "libelles": {
            "superficie_min": "Superficie totale minimale (m²)",
            "superficie_max": "Superficie totale maximale (m²)",
            "type_acquisition": "Type d'acquisition",
        },
        "commodites": [
            "Transports en commun", "Commerces de proximité", "Écoles et crèches",
            "Axe passant", "Quartier locatif recherché", "Parking",
            "Gardiennage", "Accès autoroute",
        ],
        "note": "Un immeuble de rapport se décrit par ses lots, pas par ses "
                "pièces ; la VEFA ne s'y pratique pas.",
    },
    "Local commercial": {
        "designation": "un local commercial",
        "champs": ("etat_local",),
        "acquisitions": ("existant", "neuf", "bail"),
        "acquisitions_libelles": {"existant": "Local déjà construit",
                                  "neuf": "Local neuf, jamais exploité"},
        "libelles": {
            "superficie_min": "Surface utile minimale (m²)",
            "superficie_max": "Surface utile maximale (m²)",
            "type_acquisition": "Mode d'occupation",
        },
        "commodites": [
            "Vitrine sur rue", "Fort flux piéton", "Axe passant",
            "Parking clients", "Accès PMR", "Accès livraisons",
            "Zone d'activité", "Centre commercial", "Transports en commun",
        ],
        "note": "Un local se juge sur son état, son passage et son "
                "accessibilité — pas sur un niveau de standing.",
    },
    "Terrain": {
        "designation": "un terrain",
        "champs": _TERRAIN,
        "acquisitions": ("terrain_nu", "terrain_viabilise", "lot_lotissement"),
        "libelles": {
            "superficie_min": "Superficie du terrain, minimale (m²)",
            "superficie_max": "Superficie du terrain, maximale (m²)",
            "type_acquisition": "Nature du terrain",
        },
        "commodites": [
            "Accès routier goudronné", "Transports en commun",
            "Commerces de proximité", "Écoles et crèches", "Accès autoroute",
            "Bord de mer", "Vue dégagée", "Quartier en développement",
        ],
        "note": "Ni standing ni distribution pour un terrain : ce qui se "
                "chiffre, c'est la viabilisation, le relief et le zonage.",
    },
    "Autre": {
        "designation": "un bien",
        "champs": ("standing",) + _DISTRIBUTION,
        "acquisitions": ("existant", "neuf", "vefa"),
        "libelles": {
            "superficie_min": "Superficie minimale (m²)",
            "superficie_max": "Superficie maximale (m²)",
            "type_acquisition": "Type d'acquisition",
        },
        "commodites": _COMMODITES_RESIDENTIELLES,
        "note": "Type non standard : tous les champs restent ouverts, "
                "précisez le reste dans les notes du client.",
    },
}


def designation(type_bien: str | None) -> str:
    """« un terrain », « une villa » — de quoi écrire une phrase correcte."""
    return profil(type_bien)["designation"]


def profil(type_bien: str | None) -> dict:
    """Le profil d'un type de bien ; « Autre » sert de repli, jamais d'erreur."""
    return PROFILS.get(type_bien or "", PROFILS["Autre"])


def champs(type_bien: str | None) -> tuple:
    """Les champs optionnels qui ont un sens pour ce type de bien."""
    return tuple(profil(type_bien)["champs"])


def demande(type_bien: str | None, champ: str) -> bool:
    return champ in profil(type_bien)["champs"]


def acquisitions(type_bien: str | None) -> list[tuple[str, str]]:
    """Les modes d'acquisition proposés, sous le libellé propre au type."""
    p = profil(type_bien)
    precises = p.get("acquisitions_libelles", {})
    return [(v, precises.get(v, ACQUISITIONS[v])) for v in p["acquisitions"]]


def libelle_acquisition(type_bien: str | None, valeur: str | None) -> str:
    """Libellé d'une valeur enregistrée, même si le type a changé depuis."""
    for cle, libelle in acquisitions(type_bien):
        if cle == valeur:
            return libelle
    return ACQUISITIONS.get(valeur or "", valeur or "—")
