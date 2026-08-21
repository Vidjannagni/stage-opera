"""Construction automatique des montages à étudier pour un dossier.

Le conseiller ne saisit plus un scénario à la main : à partir du bien, du
budget du client et de son objectif, l'outil **fabrique lui-même la famille de
montages plausibles** — paiement comptant, crédit à apport minimal, crédit à
apport renforcé, sur plusieurs durées — puis les fait calculer par le moteur
existant (``core.scenario.calculer_scenario``).

Deux principes, qui expliquent la forme du code :

1. **Un candidat présente exactement la même surface qu'un ``Scenario``** de la
   base : mêmes attributs, mêmes unités. Le moteur de calcul est donc utilisé
   sans modification, et un montage retenu peut être enregistré tel quel.
2. **Rien n'est opaque.** Chaque candidat porte sa ``constitution`` : la liste
   de tous les paramètres qui le composent, avec, pour chacun, d'où vient la
   valeur (dossier, client, zone de marché, hypothèse par défaut, règle de
   génération). C'est ce qui permet d'afficher intégralement la composition
   d'un montage devant un client qui la demande.

La règle de financement retenue est explicite : **une banque prête sur le bien,
pas sur les frais**. L'apport minimal d'un dossier est donc la part que le prêt
ne couvre pas — frais d'acquisition et travaux (cf. ``hypotheses``).
"""
from dataclasses import dataclass, field

from . import hypotheses as hyp
from .acquisition import cout_acquisition, frais_acquisition
from .format_fr import montant_texte as _montant, pct_texte as _pct

#: Familles de montages, dans l'ordre de présentation.
FAMILLES = {
    "comptant": "Paiement comptant",
    "apport_minimal": "Crédit à apport minimal",
    "apport_renforce": "Crédit à apport renforcé",
    "apport_maximal": "Crédit avec tout le budget en apport",
}


@dataclass
class Candidat:
    """Montage proposé — mêmes attributs qu'un ``Scenario`` enregistré."""

    nom: str
    famille: str
    mode: str
    apport: float
    taux_interet: float
    taux_assurance: float
    duree_annees: int
    horizon_annees: int
    revalorisation_loyer_pct: float
    revalorisation_bien_pct: float
    frais_revente_pct: float
    taux_actualisation: float
    prix_revente: float | None = None

    #: Composition détaillée : [{libelle, valeur, origine}, ...]
    constitution: list[dict] = field(default_factory=list)
    #: Motif d'écartement (budget insuffisant…) ; None si le montage est tenable.
    ecarte: str | None = None

    @property
    def signature(self) -> tuple:
        """Deux montages de même signature sont le même montage."""
        return (self.mode, round(self.apport), self.duree_annees, self.horizon_annees)

    @property
    def famille_libelle(self) -> str:
        return FAMILLES.get(self.famille, self.famille)

    def champs_scenario(self) -> dict:
        """Attributs à recopier pour enregistrer ce montage en base."""
        return {
            "nom": self.nom,
            "mode": self.mode,
            "apport": self.apport,
            "taux_interet": self.taux_interet,
            "taux_assurance": self.taux_assurance,
            "duree_annees": self.duree_annees,
            "horizon_annees": self.horizon_annees,
            "revalorisation_loyer_pct": self.revalorisation_loyer_pct,
            "revalorisation_bien_pct": self.revalorisation_bien_pct,
            "frais_revente_pct": self.frais_revente_pct,
            "taux_actualisation": self.taux_actualisation,
            "prix_revente": self.prix_revente,
        }


def horizon_retenu(projet, brief) -> int:
    """L'horizon vient du client ; à défaut, du type d'opération."""
    if brief is not None and brief.horizon_annees:
        return int(brief.horizon_annees)
    return hyp.horizon_defaut(projet.est_locatif)


def apport_minimal(projet) -> float:
    """Part du coût que le prêt ne couvre pas : frais d'acquisition + travaux."""
    prix = projet.prix_bien
    finance = prix * hyp.PART_FINANCABLE_DU_PRIX / 100.0
    total = cout_acquisition(prix, projet.taux_frais_acquisition, projet.budget_travaux)
    return max(total - finance, 0.0)


def generer(
    projet,
    brief=None,
    budget_disponible: float | None = None,
    prix_revente: float | None = None,
) -> list[Candidat]:
    """Famille de montages à confronter pour ce dossier.

    ``budget_disponible`` sert à écarter les montages hors de portée du client
    (motif conservé et affiché, jamais silencieux). ``None`` = budget inconnu :
    aucun montage n'est alors écarté, et l'étude le signale.
    """
    devise = projet.zone.devise if projet.zone else ""
    prix = projet.prix_bien
    taux_frais = projet.taux_frais_acquisition
    frais = frais_acquisition(prix, taux_frais)
    cout_total = cout_acquisition(prix, taux_frais, projet.budget_travaux)
    horizon = horizon_retenu(projet, brief)
    minimal = apport_minimal(projet)

    base_commune = [
        {"libelle": "Prix du bien", "valeur": _montant(prix, devise), "origine": "dossier"},
        {"libelle": f"Frais d'acquisition ({_pct(taux_frais)} du prix)",
         "valeur": _montant(frais, devise), "origine": "zone de marché"},
        {"libelle": "Travaux / construction",
         "valeur": _montant(projet.budget_travaux, devise), "origine": "dossier"},
        {"libelle": "Coût d'entrée total",
         "valeur": _montant(cout_total, devise), "origine": "calculé"},
        {"libelle": "Horizon du client", "valeur": f"{horizon} ans",
         "origine": "brief du client" if (brief and brief.horizon_annees) else "hypothèse par défaut"},
    ]
    if projet.delai_livraison_mois:
        base_commune.append({
            "libelle": "Délai de livraison",
            "valeur": f"{projet.delai_livraison_mois} mois",
            "origine": "dossier",
        })

    candidats: list[Candidat] = []

    def ajouter(candidat: Candidat, lignes: list[dict]) -> None:
        candidat.constitution = base_commune + lignes + _lignes_projection(
            candidat, projet, devise
        )
        if budget_disponible is not None and candidat.apport > budget_disponible + 1e-6:
            manque = candidat.apport - budget_disponible
            candidat.ecarte = (
                f"apport de {_montant(candidat.apport, devise)} pour un budget "
                f"déclaré de {_montant(budget_disponible, devise)} — "
                f"il manque {_montant(manque, devise)}"
            )
        if all(candidat.signature != autre.signature for autre in candidats):
            candidats.append(candidat)

    communs = dict(
        horizon_annees=horizon,
        revalorisation_loyer_pct=hyp.REVALORISATION_LOYER if projet.est_locatif else 0.0,
        revalorisation_bien_pct=hyp.REVALORISATION_BIEN,
        frais_revente_pct=hyp.FRAIS_REVENTE,
        taux_actualisation=hyp.TAUX_ACTUALISATION,
        prix_revente=prix_revente,
    )

    # ── Paiement comptant ────────────────────────────────────────────────────
    ajouter(
        Candidat(
            nom="Achat comptant", famille="comptant", mode="cash",
            apport=cout_total, taux_interet=0.0, taux_assurance=0.0,
            duree_annees=max(horizon, 1), **communs,
        ),
        [{"libelle": "Financement", "valeur": "aucun emprunt", "origine": "règle de génération"}],
    )

    # ── Crédits : trois niveaux d'apport × trois durées ───────────────────────
    niveaux = [
        ("apport_minimal", minimal,
         "frais d'acquisition et travaux, que la banque ne finance pas"),
        ("apport_renforce", minimal + prix * hyp.SUPPLEMENT_APPORT_RENFORCE / 100.0,
         f"apport minimal augmenté de {hyp.SUPPLEMENT_APPORT_RENFORCE:.0f} % du prix"),
    ]
    if budget_disponible is not None:
        # Jamais en dessous de l'apport minimal : un budget inférieur aux frais
        # ne se rattrape pas en empruntant davantage — la banque ne prête pas
        # au-delà du prix du bien. Le montage sera alors écarté, à juste titre.
        niveaux.append(
            ("apport_maximal", max(min(budget_disponible, cout_total), minimal),
             "tout le budget disponible du client est mis en apport"),
        )

    for famille, apport, justification in niveaux:
        apport = max(min(apport, cout_total), 0.0)
        if apport >= cout_total - 1e-6:
            continue  # plus rien à emprunter : c'est le montage comptant
        for duree in hyp.DUREES:
            taux = hyp.taux_interet(duree)
            ajouter(
                Candidat(
                    nom=f"Crédit {duree} ans — {_qualificatif(famille)}",
                    famille=famille, mode="credit", apport=apport,
                    taux_interet=taux, taux_assurance=hyp.TAUX_ASSURANCE,
                    duree_annees=duree, **communs,
                ),
                [
                    {"libelle": "Apport", "valeur": _montant(apport, devise),
                     "origine": justification},
                    {"libelle": "Capital emprunté",
                     "valeur": _montant(cout_total - apport, devise), "origine": "calculé"},
                    {"libelle": "Durée du prêt", "valeur": f"{duree} ans",
                     "origine": "règle de génération"},
                    {"libelle": "Taux d'intérêt annuel", "valeur": _pct(taux),
                     "origine": "hypothèse par défaut (barème par durée)"},
                    {"libelle": "Assurance emprunteur",
                     "valeur": _pct(hyp.TAUX_ASSURANCE), "origine": "hypothèse par défaut"},
                ],
            )
    return candidats


def _qualificatif(famille: str) -> str:
    return {
        "apport_minimal": "apport minimal",
        "apport_renforce": "apport renforcé",
        "apport_maximal": "budget en apport",
    }.get(famille, famille)


def _lignes_projection(candidat: Candidat, projet, devise: str) -> list[dict]:
    """Hypothèses de projection communes à tous les montages générés."""
    lignes = []
    if projet.est_locatif:
        lignes.append({
            "libelle": "Loyer mensuel retenu",
            "valeur": _montant(projet.loyer_mensuel, devise), "origine": "dossier",
        })
        lignes.append({
            "libelle": "Revalorisation annuelle du loyer",
            "valeur": _pct(candidat.revalorisation_loyer_pct),
            "origine": "hypothèse par défaut",
        })
    if candidat.prix_revente:
        lignes.append({
            "libelle": "Prix de revente à l'horizon",
            "valeur": _montant(candidat.prix_revente, devise),
            "origine": "saisi pour l'étude",
        })
    else:
        lignes.append({
            "libelle": "Revalorisation annuelle du bien",
            "valeur": _pct(candidat.revalorisation_bien_pct),
            "origine": "hypothèse par défaut",
        })
    lignes.append({
        "libelle": "Frais de revente",
        "valeur": _pct(candidat.frais_revente_pct), "origine": "hypothèse par défaut",
    })
    lignes.append({
        "libelle": "Taux d'actualisation (VAN)",
        "valeur": _pct(candidat.taux_actualisation), "origine": "hypothèse par défaut",
    })
    return lignes
