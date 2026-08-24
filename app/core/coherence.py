"""Le bien chiffré, confronté à ce que le client a demandé.

Deux objets se répondent dans l'outil, et il faut les distinguer :

- le **brief** dit ce que le client cherche — un type de bien, une fourchette
  de superficie, une fourchette de budget, un objectif, un horizon. Il y en a
  un par client, et il ne contient aucun chiffre de calcul ;
- le **dossier** (projet) chiffre **un bien précis** qu'on lui propose — un
  prix, des travaux, un loyer. Il y en a autant que de biens étudiés.

Le premier est la demande, le second une réponse possible. Rien n'obligeait
jusqu'ici la seconde à ressembler à la première : on pouvait chiffrer un
appartement de 45 m² à trois millions pour un client venu chercher un terrain
à un million, sans que rien ne le signale.

Ce module met des mots sur la distance entre les deux. **Il ne bloque rien** :
proposer un bien un peu plus grand ou un peu plus cher est un acte de conseil
légitime, et c'est même souvent le métier. Mais l'écart doit être dit par le
conseiller, pas découvert par le client.
"""
from . import profil_bien
from .format_fr import montant_texte

#: Un dossier « en recherche » n'a pas encore de bien arrêté : son adresse et
#: sa superficie ne sont pas connues, et ne sont donc pas demandées.
STATUT_SANS_BIEN = "recherche"


def _nombre(valeur) -> str:
    return montant_texte(valeur)


def ecarts(brief, projet, cout_total: float | None = None) -> list[dict]:
    """Les écarts entre le brief du client et le bien chiffré.

    ``cout_total`` : coût d'entrée réel (prix + frais + travaux) si l'appelant
    l'a déjà calculé ; à défaut, le prix seul sert de base, ce qui sous-estime
    l'écart mais ne le fausse jamais dans le sens rassurant.
    """
    if brief is None:
        return []

    releves: list[dict] = []
    devise = projet.zone.devise if projet.zone else ""

    def noter(champ: str, phrase: str) -> None:
        releves.append({"champ": champ, "phrase": phrase})

    # ── L'objectif du client ─────────────────────────────────────────────────
    # Le rapprochement se fait sur l'objectif, non sur le type de bien : un
    # appartement acheté pour être revendu se chiffre légitimement sans loyer,
    # et comparer « appartement recherché » à « opération de revente » ferait
    # crier au loup sur un dossier parfaitement cohérent. Ce qui ne colle pas,
    # c'est un dossier sans loyer proposé à qui vient chercher un revenu.
    if brief.objectif == "revenu" and not projet.est_locatif:
        noter("type_operation",
              f"Le client attend un revenu locatif régulier, et ce dossier "
              f"n'en produit aucun : toute sa valeur vient de la revente. "
              f"Il cherche {profil_bien.designation(brief.type_bien)}.")

    # ── La superficie ────────────────────────────────────────────────────────
    if projet.surface_m2:
        if brief.superficie_min and projet.surface_m2 < brief.superficie_min:
            noter("surface_m2",
                  f"{_nombre(projet.surface_m2)} m² : sous les "
                  f"{_nombre(brief.superficie_min)} m² demandés au minimum.")
        elif brief.superficie_max and projet.surface_m2 > brief.superficie_max:
            noter("surface_m2",
                  f"{_nombre(projet.surface_m2)} m² : au-dessus des "
                  f"{_nombre(brief.superficie_max)} m² demandés au maximum.")

    # ── Le budget ────────────────────────────────────────────────────────────
    # Ce que le client compare à son budget est ce qu'il sort de sa poche :
    # le coût d'entrée, frais et travaux compris — pas le seul prix affiché.
    engage = cout_total if cout_total is not None else projet.prix_bien
    if engage:
        if brief.budget_max and engage > brief.budget_max:
            noter("prix_bien",
                  f"Coût d'entrée {montant_texte(engage, devise)} : au-dessus "
                  f"du budget maximal annoncé ({montant_texte(brief.budget_max, devise)}).")
        elif brief.budget_min and engage < brief.budget_min:
            noter("prix_bien",
                  f"Coût d'entrée {montant_texte(engage, devise)} : sous le "
                  f"budget minimal annoncé ({montant_texte(brief.budget_min, devise)}) "
                  "— le client visait plus haut.")

    # ── L'achat sur plan ─────────────────────────────────────────────────────
    if brief.type_acquisition == "vefa" and not projet.delai_livraison_mois:
        noter("delai_livraison_mois",
              "Le client cherche un achat sur plan, et aucun délai de "
              "livraison n'est saisi : le bien est donc chiffré comme livré "
              "le jour de l'achat.")

    return releves


def resume(brief) -> list[tuple[str, str]]:
    """Ce que le client cherche, en quelques lignes — pour le rappeler à côté
    du bien qu'on chiffre."""
    if brief is None:
        return []
    lignes = [("Bien recherché", brief.type_bien
               + (f" — {brief.standing}" if brief.standing else "")
               + (f" — {brief.etat_local}" if brief.etat_local else ""))]
    if brief.zone_recherchee:
        lignes.append(("Zone", brief.zone_recherchee))
    if brief.superficie_min or brief.superficie_max:
        lignes.append(("Superficie", _bornes(brief.superficie_min, brief.superficie_max, "m²")))
    if brief.budget_min or brief.budget_max:
        lignes.append(("Budget", _bornes(brief.budget_min, brief.budget_max)))
    lignes.append(("Objectif", f"{brief.objectif_libelle}, sur {brief.horizon_annees} ans"))
    return lignes


def _bornes(bas, haut, unite: str = "") -> str:
    if bas and haut:
        texte = f"{_nombre(bas)} à {_nombre(haut)}"
    elif haut:
        texte = f"jusqu'à {_nombre(haut)}"
    else:
        texte = f"à partir de {_nombre(bas)}"
    return f"{texte} {unite}".strip()
