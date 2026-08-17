"""Informations publiques du cabinet, affichées sur la page vitrine.

Elles sont regroupées ici pour être modifiables à un seul endroit, sans
toucher aux gabarits.

⚠ Rien n'est inventé ici. Une coordonnée non communiquée vaut ``None`` et
n'apparaît tout simplement pas sur la page — jamais un numéro fictif. Il suffit
de renseigner la valeur ci-dessous, ou la variable d'environnement
correspondante, pour qu'elle s'affiche.

Tout le reste de la page vitrine (métier, étapes, règle de décision, questions
fréquentes) provient des réponses du cabinet consignées dans
``docs/retour_cabinet.md``.
"""
import os

NOM = "Choubel Consulting"
ACTIVITE = "Conseil en investissement immobilier"

TELEPHONE = os.environ.get("CABINET_TELEPHONE")
EMAIL = os.environ.get("CABINET_EMAIL", "choubel.ma@gmail.com")
#: Communiquée plus tard par le cabinet.
ADRESSE = os.environ.get("CABINET_ADRESSE")


def coordonnees() -> dict:
    """Coordonnées publiables, et indicateur de complétude pour le gabarit."""
    valeurs = {"telephone": TELEPHONE, "email": EMAIL, "adresse": ADRESSE}
    return {**valeurs, "renseignees": any(valeurs.values())}


#: Questions réellement posées en rendez-vous, avec la réponse du cabinet.
QUESTIONS_FREQUENTES = [
    (
        "À partir de quel rendement un investissement est-il intéressant ?",
        "Il n'existe pas de seuil. Un même bien peut convenir à une personne et "
        "pas à une autre : tout dépend de votre objectif et de votre horizon. "
        "Nous chiffrons l'opération, vous arbitrez.",
    ),
    (
        "D'où viennent les frais d'acquisition annoncés ?",
        "Au Maroc, ils se décomposent en droits d'enregistrement (4 %), "
        "conservation foncière (1,5 %), notaire (1 %) et frais divers (0,5 %), "
        "soit 7 % du prix. Ils sont ajustables si votre dossier diffère.",
    ),
    (
        "J'achète sur plan : à partir de quand le bien rapporte-t-il ?",
        "Rien avant la livraison. Pendant le chantier, le bien ne produit ni "
        "loyer ni charges, alors que les mensualités d'emprunt courent déjà. "
        "Nous vous montrons cet effort année par année avant que vous vous engagiez.",
    ),
    (
        "Et si le logement reste vide plusieurs mois ?",
        "La vacance locative est un paramètre de l'analyse. Nous la faisons "
        "varier devant vous pour que vous voyiez l'effet sur votre trésorerie.",
    ),
    (
        "Pourquoi demandez-vous ma nationalité et ma situation professionnelle ?",
        "Elles conditionnent l'accès au crédit local et les modalités de "
        "transfert des fonds. Les connaître dès le premier entretien évite de "
        "vous présenter des biens que le financement ne suivrait pas.",
    ),
    (
        "Que se passe-t-il après la signature ?",
        "Nous vous accompagnons jusqu'au bout : compromis, acte devant notaire, "
        "puis livraison du bien.",
    ),
]
