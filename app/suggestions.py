"""Suggestions proposées à la saisie dans les formulaires.

Ce sont des **suggestions, pas des contraintes** : les champs concernés
restent libres. Techniquement, elles alimentent un ``<datalist>`` HTML — le
conseiller choisit dans la liste ou saisit autre chose.

Deux raisons de les avoir : accélérer le remplissage pendant un rendez-vous,
et homogénéiser le vocabulaire d'un conseiller à l'autre, ce qui rend les
dossiers comparables. Elles reprennent les catégories citées par le cabinet
lors du cadrage métier (cf. docs/retour_cabinet.md).

Les listes fermées — type de bien, standing, mode de financement, objectif —
ne sont pas ici : ce sont des ``SelectField``, car leur ensemble de valeurs
est arrêté et sert aux calculs.

Ne sont pas ici non plus les suggestions qui dépendent du bien recherché —
commodités, réseaux, zonage : une vitrine sur rue se propose pour un local,
pas pour un terrain. Elles vivent dans ``core.profil_bien``, avec le reste de
ce qui s'ajuste au type de bien.
"""

SITUATIONS_PROFESSIONNELLES = [
    "Salarié(e) du privé",
    "Fonctionnaire",
    "Profession libérale",
    "Chef d'entreprise",
    "Commerçant(e)",
    "Artisan(e)",
    "Cadre dirigeant(e)",
    "Retraité(e)",
    "Marocain(e) résidant à l'étranger",
]

# Le cabinet exerce au Maroc ; la nationalité conditionne l'accès au crédit
# local et le rapatriement des fonds, d'où sa présence dans la fiche client.
NATIONALITES = [
    "Marocaine", "Française", "Algérienne", "Tunisienne", "Sénégalaise",
    "Ivoirienne", "Béninoise", "Espagnole", "Belge", "Canadienne",
    "Britannique", "Américaine",
]

ZONES_RECHERCHE = [
    "Casablanca — Gauthier", "Casablanca — Maârif", "Casablanca — Ain Diab",
    "Casablanca — Californie", "Casablanca — Sidi Maârouf", "Bouskoura",
    "Rabat — Agdal", "Rabat — Hay Riad", "Rabat — Souissi",
    "Marrakech — Guéliz", "Marrakech — Hivernage", "Marrakech — Palmeraie",
    "Tanger — Malabata", "Tanger — Centre-ville",
    "Agadir — Founty", "Fès — Saïss", "Berrechid", "Mohammedia",
]

ETAGES = [
    "Rez-de-chaussée", "1er étage", "2e étage", "3e étage",
    "4e étage ou plus", "Dernier étage", "Avec ascenseur", "Indifférent",
]

ORIENTATIONS = [
    "Sud", "Sud-Est", "Sud-Ouest", "Est", "Ouest",
    "Nord", "Nord-Est", "Nord-Ouest", "Traversant", "Indifférente",
]

POSTES_TRAVAUX = [
    "Cuisine équipée", "Salle de bain", "Peinture et enduits",
    "Électricité — mise aux normes", "Plomberie", "Menuiserie aluminium",
    "Climatisation", "Étanchéité de la terrasse", "Carrelage et revêtements",
    "Faux plafonds", "Chauffe-eau", "Portes et serrurerie",
]

# Noms de scénarios les plus courants, pour que deux dossiers restent
# comparables d'un conseiller à l'autre.
NOMS_SCENARIOS = [
    "Achat comptant", "Crédit 15 ans", "Crédit 20 ans", "Crédit 25 ans",
    "Apport renforcé", "Portage 10 ans", "Construction-revente",
]

TOUTES = {
    "situations_professionnelles": SITUATIONS_PROFESSIONNELLES,
    "nationalites": NATIONALITES,
    "zones_recherche": ZONES_RECHERCHE,
    "etages": ETAGES,
    "orientations": ORIENTATIONS,
    "postes_travaux": POSTES_TRAVAUX,
    "noms_scenarios": NOMS_SCENARIOS,
}
