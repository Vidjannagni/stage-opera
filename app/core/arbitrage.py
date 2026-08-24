"""Confrontation des montages générés et proposition motivée.

Ce module répond à la question « lequel proposer au client ? » sans jamais
inventer de seuil universel — le cabinet a été clair sur ce point : *« un
investissement peut être rentable pour une personne et ne pas l'être pour une
autre »*. Le classement est donc **relatif à un client donné** :

- il ne compare que des montages portant sur **le même bien** et le **même
  horizon**, celui déclaré par le client ;
- il pondère les critères selon l'**objectif** déclaré (revenu locatif,
  plus-value, patrimoine) ;
- il écarte les montages **hors budget**, en disant lesquels et pourquoi ;
- il rend visible la pondération employée, pour que la proposition reste
  discutable. Ce n'est pas un verdict : c'est un point de départ de discussion.

Chaque critère est normalisé entre le meilleur et le moins bon des montages
étudiés (0 à 1), puis pondéré. Un score n'a donc de sens **qu'à l'intérieur
d'une étude** : il classe, il ne note pas.
"""
from .format_fr import annees_texte, montant_texte, pct_texte
from .generation import generer
from .scenario import calculer_scenario

#: Critères de classement. ``sens`` = +1 si « plus c'est grand, mieux c'est ».
CRITERES = {
    "cashflow": {
        "libelle": "Cash-flow mensuel", "sens": 1, "locatif_seulement": False,
    },
    "rendement_net": {
        "libelle": "Rendement net", "sens": 1, "locatif_seulement": True,
    },
    "valeur_creee": {
        "libelle": "Valeur créée sur l'horizon", "sens": 1, "locatif_seulement": False,
    },
    "tri": {
        "libelle": "TRI", "sens": 1, "locatif_seulement": False,
    },
    "effort_initial": {
        "libelle": "Argent immobilisé au départ", "sens": -1, "locatif_seulement": False,
    },
}

#: Pondération des critères selon l'objectif déclaré par le client.
#: Somme = 1 pour chaque objectif. Ces poids traduisent une intention, pas une
#: vérité de marché : ils sont affichés à l'écran et modifiables ici seulement.
POIDS = {
    "revenu": {
        "cashflow": 0.40, "rendement_net": 0.25,
        "valeur_creee": 0.20, "effort_initial": 0.15,
    },
    "plus_value": {
        "valeur_creee": 0.40, "tri": 0.30,
        "cashflow": 0.15, "effort_initial": 0.15,
    },
    "patrimoine": {
        "valeur_creee": 0.30, "cashflow": 0.25,
        "tri": 0.20, "effort_initial": 0.25,
    },
}

OBJECTIFS_LIBELLES = {
    "revenu": "revenu locatif régulier",
    "plus_value": "plus-value à la revente",
    "patrimoine": "constitution de patrimoine",
}


def poids_effectifs(objectif: str, est_locatif: bool) -> dict:
    """Poids applicables : sans loyer, le rendement locatif n'existe pas."""
    poids = dict(POIDS.get(objectif, POIDS["revenu"]))
    if not est_locatif:
        poids = {
            cle: valeur for cle, valeur in poids.items()
            if not CRITERES[cle]["locatif_seulement"]
        }
    total = sum(poids.values())
    return {cle: valeur / total for cle, valeur in poids.items()}


def _criteres_du_calcul(r: dict, est_locatif: bool) -> dict:
    return {
        "cashflow": r["indicateurs"]["cashflow_mensuel"],
        "rendement_net": r["rendements"]["net"] if est_locatif else None,
        "valeur_creee": r["indicateurs"]["valeur_creee"],
        "tri": r["indicateurs"]["tri"],
        "effort_initial": r["projection"]["investissement_initial"],
    }


def _normaliser(valeurs: list, sens: int) -> list[float]:
    """Ramène une colonne de critère entre 0 (le moins bon) et 1 (le meilleur).

    Une valeur absente (TRI non calculable) reçoit 0 : elle ne peut pas être
    créditée d'un avantage qu'on n'a pas su mesurer.
    """
    connues = [v for v in valeurs if v is not None]
    if not connues:
        return [0.0] * len(valeurs)
    bas, haut = min(connues), max(connues)
    if haut - bas < 1e-9:
        return [1.0 if v is not None else 0.0 for v in valeurs]
    return [
        0.0 if v is None
        else ((v - bas) if sens > 0 else (haut - v)) / (haut - bas)
        for v in valeurs
    ]


def etudier(
    projet,
    brief=None,
    budget_disponible: float | None = None,
    prix_revente: float | None = None,
) -> dict:
    """Génère, calcule, classe et explique. Point d'entrée unique du module."""
    est_locatif = projet.est_locatif
    devise = projet.zone.devise if projet.zone else ""
    objectif = (brief.objectif if brief else None) or "revenu"
    poids = poids_effectifs(objectif, est_locatif)

    candidats = generer(projet, brief, budget_disponible, prix_revente)
    etudies = []
    for candidat in candidats:
        r = calculer_scenario(projet, candidat)
        etudies.append({
            "candidat": candidat,
            "r": r,
            "criteres": _criteres_du_calcul(r, est_locatif),
            "ecarte": candidat.ecarte,
        })

    retenus = [e for e in etudies if not e["ecarte"]]
    ecartes = [e for e in etudies if e["ecarte"]]
    # Le classement se fait entre montages tenables ; s'il n'y en a aucun, on
    # classe quand même l'ensemble pour ne pas rendre une page vide.
    a_classer = retenus or etudies

    for cle, poids_critere in poids.items():
        colonne = _normaliser(
            [e["criteres"][cle] for e in a_classer], CRITERES[cle]["sens"]
        )
        for etude, note in zip(a_classer, colonne):
            etude.setdefault("notes", {})[cle] = note

    for etude in a_classer:
        etude["score"] = 100.0 * sum(
            poids[cle] * etude["notes"][cle] for cle in poids
        )
    a_classer.sort(key=lambda e: e["score"], reverse=True)
    for rang, etude in enumerate(a_classer, start=1):
        etude["rang"] = rang

    meilleur = a_classer[0] if a_classer else None
    second = a_classer[1] if len(a_classer) > 1 else None

    return {
        "projet": projet,
        "brief": brief,
        "devise": devise,
        "objectif": objectif,
        "objectif_libelle": OBJECTIFS_LIBELLES.get(objectif, objectif),
        "horizon": meilleur["candidat"].horizon_annees if meilleur else 0,
        "budget_disponible": budget_disponible,
        "poids": poids,
        "criteres": CRITERES,
        "classement": a_classer,
        "ecartes": ecartes,
        "aucun_tenable": not retenus,
        "meilleur": meilleur,
        "second": second,
        "explication": (
            expliquer(meilleur, second, projet, brief, budget_disponible, devise)
            if meilleur else None
        ),
    }


# ═══════════════════════════════════════════════════════════════════════════
#  Mise en mots : ce que le conseiller lit au client
# ═══════════════════════════════════════════════════════════════════════════

def expliquer(meilleur, second, projet, brief, budget_disponible, devise) -> dict:
    """Traduit le classement en phrases dites en rendez-vous.

    Aucun jargon non explicité : les montants sont en clair, les pourcentages
    aussi, et chaque affirmation renvoie à un chiffre de la page.
    """
    candidat, r = meilleur["candidat"], meilleur["r"]
    est_locatif = projet.est_locatif
    horizon = candidat.horizon_annees
    cashflow = r["indicateurs"]["cashflow_mensuel"]
    valeur = r["indicateurs"]["valeur_creee"]
    apport = r["projection"]["investissement_initial"]

    argumentaire = _arguments(meilleur, second, projet, devise)

    return {
        "titre": candidat.nom,
        "resume": _resume(candidat, r, projet, brief, devise),
        "arguments": argumentaire["avantages"],
        "nuances": argumentaire["nuances"],
        "vigilance": _vigilance(meilleur, projet, brief, budget_disponible, devise),
        "comparaison": _comparaison(meilleur, second, projet, devise),
        "chiffres_cles": _chiffres_cles(
            est_locatif, apport, cashflow, valeur, horizon, r, devise
        ),
    }


def _resume(candidat, r, projet, brief, devise) -> str:
    horizon = candidat.horizon_annees
    apport = r["projection"]["investissement_initial"]
    cashflow = r["indicateurs"]["cashflow_mensuel"]
    valeur = r["indicateurs"]["valeur_creee"]
    client = projet.client.nom if projet.client else "le client"

    if candidat.mode == "cash":
        entree = f"En payant comptant ({montant_texte(apport, devise)})"
    else:
        entree = (
            f"Avec un apport de {montant_texte(apport, devise)} et un crédit sur "
            f"{annees_texte(candidat.duree_annees)}"
        )

    if projet.est_locatif and cashflow >= 0:
        milieu = (
            f", le bien paie ses charges, ses impôts et sa mensualité, et laisse "
            f"encore {montant_texte(cashflow, devise)} par mois à {client}"
        )
    elif projet.est_locatif:
        milieu = (
            f", les loyers ne couvrent pas tout : {client} complète "
            f"{montant_texte(abs(cashflow), devise)} par mois"
        )
    elif cashflow < 0:
        milieu = (
            f", l'opération coûte {montant_texte(abs(cashflow), devise)} par mois "
            f"à {client} tant qu'elle n'est pas revendue"
        )
    else:
        milieu = f", {client} n'a rien à décaisser d'ici la revente"

    fin = (
        f". Au bout de {annees_texte(horizon)}, revente comprise, l'opération lui "
        f"aura {'rapporté' if valeur >= 0 else 'coûté'} "
        f"{montant_texte(abs(valeur), devise)}."
    )
    return entree + milieu + fin


def _chiffres_cles(est_locatif, apport, cashflow, valeur, horizon, r, devise) -> list[dict]:
    chiffres = [
        {"libelle": "Argent à sortir au départ",
         "valeur": montant_texte(apport, devise), "ton": ""},
        {"libelle": "Cash-flow mensuel" if est_locatif else "Effort mensuel",
         "valeur": montant_texte(cashflow, devise),
         "ton": "positif" if cashflow >= 0 else "negatif"},
        {"libelle": f"Valeur créée sur {annees_texte(horizon)}",
         "valeur": montant_texte(valeur, devise),
         "ton": "positif" if valeur >= 0 else "negatif"},
    ]
    if est_locatif:
        chiffres.append({
            "libelle": "Rendement net",
            "valeur": pct_texte(r["rendements"]["net"]), "ton": "",
        })
    return chiffres


def _arguments(meilleur, second, projet, devise) -> dict:
    """Ce qui distingue le montage retenu — et ce que l'autre fait mieux.

    Les deux listes sont rendues séparément : présenter les avantages sans
    nommer ce qu'on perd serait un argumentaire de vente, pas un conseil.
    """
    avantages: list[str] = []
    nuances: list[str] = []
    criteres = meilleur["criteres"]
    candidat = meilleur["candidat"]

    if second is None:
        return {
            "avantages": [
                "Un seul montage est finançable dans les conditions du dossier : "
                "il n'y a pas d'alternative à comparer."
            ],
            "nuances": [],
        }

    autres = second["criteres"]
    nom_second = second["candidat"].nom

    ecart = criteres["cashflow"] - autres["cashflow"]
    if abs(ecart) >= 1:
        mensuel = "laisse" if projet.est_locatif else "coûte"
        if ecart > 0:
            avantages.append(
                f"Il {mensuel} {montant_texte(abs(ecart), devise)} de "
                f"{'plus' if projet.est_locatif else 'moins'} par mois que "
                f"« {nom_second} », le montage classé juste après."
            )
        else:
            nuances.append(
                f"« {nom_second} » est plus léger de "
                f"{montant_texte(abs(ecart), devise)} par mois."
            )

    ecart_valeur = criteres["valeur_creee"] - autres["valeur_creee"]
    if abs(ecart_valeur) >= 1:
        if ecart_valeur > 0:
            avantages.append(
                f"Sur l'horizon du client, il crée "
                f"{montant_texte(ecart_valeur, devise)} de valeur de plus que "
                f"« {nom_second} »."
            )
        else:
            nuances.append(
                f"« {nom_second} » crée {montant_texte(abs(ecart_valeur), devise)} "
                "de valeur de plus sur le même horizon."
            )

    ecart_apport = criteres["effort_initial"] - autres["effort_initial"]
    if abs(ecart_apport) >= 1:
        if ecart_apport < 0:
            avantages.append(
                f"Il immobilise {montant_texte(abs(ecart_apport), devise)} de moins "
                "au départ, ce qui laisse de la trésorerie au client."
            )
        else:
            nuances.append(
                f"Il demande {montant_texte(ecart_apport, devise)} de plus au "
                "départ : c'est le prix des écarts ci-dessus."
            )

    if criteres["tri"] is not None and autres["tri"] is not None:
        ecart_tri = criteres["tri"] - autres["tri"]
        if ecart_tri >= 0.05:
            avantages.append(
                f"Rapporté à l'argent réellement engagé, il rend "
                f"{pct_texte(criteres['tri'])} par an, contre "
                f"{pct_texte(autres['tri'])} pour « {nom_second} »."
            )
        elif ecart_tri <= -0.05:
            nuances.append(
                f"Rapporté à l'argent engagé, « {nom_second} » rend mieux : "
                f"{pct_texte(autres['tri'])} par an contre "
                f"{pct_texte(criteres['tri'])}. L'écart vient de l'effet de "
                "levier du crédit, qui fait travailler l'argent de la banque."
            )

    if candidat.mode == "cash":
        avantages.append(
            "Sans emprunt, le client ne paie ni intérêts ni assurance, et aucun "
            "accord bancaire n'est nécessaire."
        )
    return {"avantages": avantages, "nuances": nuances}


def _vigilance(meilleur, projet, brief, budget_disponible, devise) -> list[str]:
    """Ce qu'il faut dire au client avant qu'il signe."""
    points: list[str] = []
    candidat, r = meilleur["candidat"], meilleur["r"]
    cashflow = r["indicateurs"]["cashflow_mensuel"]
    apport = r["projection"]["investissement_initial"]
    horizon = candidat.horizon_annees

    if cashflow < 0:
        duree = min(candidat.duree_annees, horizon) if candidat.mode == "credit" else horizon
        points.append(
            f"Le client doit pouvoir sortir {montant_texte(abs(cashflow), devise)} "
            f"par mois pendant {annees_texte(duree)} : à valider avec lui avant tout engagement."
        )
    if budget_disponible and apport > 0.8 * budget_disponible:
        points.append(
            f"L'apport mobilise {pct_texte(100 * apport / budget_disponible, 0)} du budget "
            "déclaré : il ne restera presque pas de réserve pour les imprévus."
        )
    # Le brief dit comment le client comptait payer. L'étude construit quand
    # même toute la famille de montages — écarter un crédit sans l'avoir chiffré
    # reviendrait à décider à sa place — mais le dire est un dû.
    finance = getattr(brief, "mode_financement", None) if brief else None
    if finance == "comptant" and candidat.mode == "credit":
        points.append(
            "Le client a annoncé vouloir payer comptant, et le montage le mieux "
            "placé passe par un crédit : la comparaison est faite, la décision "
            "lui revient."
        )
    elif finance == "pret" and candidat.mode != "credit":
        points.append(
            "Le client envisageait un prêt bancaire, et c'est le paiement "
            "comptant qui ressort ici — au regard de son objectif et de son horizon."
        )
    if candidat.mode == "credit" and horizon < candidat.duree_annees:
        crd = r["revente"]["capital_restant_du"]
        points.append(
            f"La revente intervient avant la fin du prêt : "
            f"{montant_texte(crd, devise)} de capital restant dû seront remboursés "
            "sur le prix de vente."
        )
    if projet.delai_livraison_mois:
        points.append(
            f"Le bien n'est livré que dans {projet.delai_livraison_mois} mois. "
            "D'ici là il ne rapporte rien, alors que les mensualités courent déjà."
        )
    if r["indicateurs"]["tri"] is None:
        points.append(
            "Le TRI n'est pas calculable sur ces flux : ils ne changent jamais de "
            "signe. Ce n'est pas une anomalie, seulement une limite de l'indicateur."
        )
    if not r["revente"]["prix_revente_saisi"]:
        points.append(
            f"Le prix de sortie n'est pas connu : il est déduit d'une revalorisation "
            f"de {pct_texte(candidat.revalorisation_bien_pct)} par an. C'est "
            "l'hypothèse la plus discutable de l'étude."
        )
    return points


def _comparaison(meilleur, second, projet, devise) -> list[dict]:
    """Tableau des écarts avec le montage classé juste après."""
    if second is None:
        return []
    lignes = []
    for cle, definition in CRITERES.items():
        if definition["locatif_seulement"] and not projet.est_locatif:
            continue
        valeur_a = meilleur["criteres"][cle]
        valeur_b = second["criteres"][cle]
        lignes.append({
            "libelle": definition["libelle"],
            "meilleur": _valeur_texte(cle, valeur_a, devise),
            "second": _valeur_texte(cle, valeur_b, devise),
            "avantage": _avantage(cle, valeur_a, valeur_b, definition["sens"]),
        })
    return lignes


def _valeur_texte(cle: str, valeur, devise: str) -> str:
    if valeur is None:
        return "—"
    if cle in ("rendement_net", "tri"):
        return pct_texte(valeur)
    return montant_texte(valeur, devise)


def _avantage(cle: str, valeur_a, valeur_b, sens: int) -> str:
    if valeur_a is None or valeur_b is None:
        return ""
    ecart = (valeur_a - valeur_b) * sens
    if abs(ecart) < 1e-9:
        return "égalité"
    return "au montage retenu" if ecart > 0 else "à l'autre montage"
