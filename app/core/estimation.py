"""Estimation des charges courantes d'un bien locatif.

Objet : réduire ce qu'il faut saisir en rendez-vous. Un conseiller connaît
toujours le prix et le loyer ; il connaît rarement, devant le client, le
montant exact du syndic, de la taxe ou de l'assurance. Plutôt que de laisser
ces champs à zéro — ce qui gonfle artificiellement le rendement — l'outil sait
en proposer un ordre de grandeur, que le conseiller garde ou corrige.

Trois précautions, sans lesquelles une estimation serait malhonnête :

1. **Rien n'est estimé en silence.** L'estimation ne s'applique que sur demande
   explicite, remplit des champs visibles, et la règle employée est affichée.
2. **Une valeur saisie n'est jamais écrasée**, y compris un zéro : « pas de
   frais de gestion » est une information, pas une case oubliée.
3. **Les coefficients sont calibrés sur le marché marocain** et regroupés ici
   pour qu'une révision par le cabinet tienne en une ligne.
"""

#: Base de calcul de chaque estimation.
LOYER_ANNUEL = "loyer_annuel"
PRIX = "prix"
CONSTANTE = "constante"

#: Champ du formulaire → règle d'estimation.
#: ``taux`` s'entend en % de la base ; pour une constante, c'est la valeur même.
REGLES = {
    "charges_copro_annuelles": {
        "base": LOYER_ANNUEL, "taux": 8.0,
        "libelle": "Charges de copropriété",
        "regle": "8 % du loyer annuel — ordre de grandeur d'un syndic de "
                 "moyen standing (gardiennage, ascenseur, parties communes).",
    },
    "taxe_annuelle": {
        "base": LOYER_ANNUEL, "taux": 10.5,
        "libelle": "Taxe annuelle",
        "regle": "10,5 % du loyer annuel — taux de la taxe de services "
                 "communaux appliqué à la valeur locative, en zone urbaine.",
    },
    "assurance_annuelle": {
        "base": PRIX, "taux": 0.15,
        "libelle": "Assurance",
        "regle": "0,15 % du prix du bien — multirisque habitation d'un "
                 "propriétaire non occupant.",
    },
    "entretien_annuel": {
        "base": PRIX, "taux": 0.5,
        "libelle": "Entretien",
        "regle": "0,5 % du prix du bien et par an — provision d'usage pour "
                 "l'entretien courant et le renouvellement des équipements.",
    },
    "frais_gestion_pct": {
        "base": CONSTANTE, "taux": 5.0,
        "libelle": "Frais de gestion",
        "regle": "5 % du loyer — tarif courant d'une agence de gestion "
                 "locative. À mettre à zéro si le client gère lui-même.",
    },
    "vacance_pct": {
        "base": CONSTANTE, "taux": 5.0,
        "libelle": "Vacance locative",
        "regle": "5 % du loyer, soit environ trois semaines de vide par an "
                 "entre deux locataires.",
    },
}


def estimer(prix_bien: float, loyer_mensuel: float) -> dict[str, dict]:
    """Ordres de grandeur des charges, champ par champ.

    Renvoie ``{champ: {"valeur": float, "regle": str, "libelle": str}}``.
    Les montants sont arrondis à la centaine : afficher « 8 160 » donnerait à
    une estimation une précision qu'elle n'a pas.
    """
    bases = {
        LOYER_ANNUEL: 12.0 * (loyer_mensuel or 0.0),
        PRIX: prix_bien or 0.0,
    }
    estimations = {}
    for champ, regle in REGLES.items():
        if regle["base"] == CONSTANTE:
            valeur = regle["taux"]
        else:
            valeur = _arrondi(bases[regle["base"]] * regle["taux"] / 100.0)
        estimations[champ] = {
            "valeur": valeur, "regle": regle["regle"], "libelle": regle["libelle"],
        }
    return estimations


def _arrondi(montant: float) -> float:
    """Arrondi à la centaine (à la dizaine sous 1 000)."""
    if montant <= 0:
        return 0.0
    pas = 100.0 if montant >= 1000 else 10.0
    return round(montant / pas) * pas
