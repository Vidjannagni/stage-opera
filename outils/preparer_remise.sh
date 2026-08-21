#!/usr/bin/env bash
# Constitue le dossier de remise du 21 août 2026 :
#   remise/RentImmo_dossier_remise.zip
# contenant le code source (archive Git propre), les documents PDF
# (cahier des charges, feuille de route, rapports hebdomadaires et final)
# et la documentation d'usage.
set -euo pipefail
cd "$(dirname "$0")/.."

DESTINATION="remise"
ETAPE="$DESTINATION/RentImmo"
rm -rf "$DESTINATION"
mkdir -p "$ETAPE/code" "$ETAPE/documents/rapports_hebdomadaires"

# L'archive est prise sur le dernier commit : ce qui n'est pas commité ne
# partirait pas dans la remise, et le silence sur ce point coûterait cher.
if [ -n "$(git status --porcelain)" ]; then
  echo "⚠  Des modifications ne sont pas commitées — elles ne seront PAS dans"
  echo "   l'archive, qui est prise sur le dernier commit :"
  git status --short | sed 's/^/     /'
  read -r -p "   Continuer quand même ? [o/N] " reponse
  [ "$reponse" = "o" ] || [ "$reponse" = "O" ] || { echo "Abandon."; exit 1; }
fi

echo "── Code source (archive Git du dernier commit)…"
git archive --format=tar HEAD | tar -x -C "$ETAPE/code"

echo "── Documents…"
cp cahier_des_charges.pdf feuille_de_route.pdf "$ETAPE/documents/"
cp rapport_semaine1.pdf "$ETAPE/documents/rapports_hebdomadaires/"
cp rapports/rapport_semaine[2-5].pdf "$ETAPE/documents/rapports_hebdomadaires/"
cp rapports/rapport_final.pdf "$ETAPE/documents/"
cp docs/guide_utilisation.md docs/script_demonstration.md \
   docs/retour_cabinet.md docs/deploiement.md \
   docs/choix_interface.md docs/etude_automatique.md "$ETAPE/documents/"

cat > "$ETAPE/LISEZMOI.txt" <<'FIN'
RentImmo — Dossier de remise (21 août 2026)
Choubel Consulting — René DANSOU & Marius HOUNKPETOHOU

  code/       Code source complet, prêt à l'exécution :
                cd code && ./lancer.sh --demo
              puis http://127.0.0.1:5000 (demo@choubel.com / demo1234).
  documents/  Rapport final, cahier des charges, feuille de route,
              guide d'utilisation, script de démonstration, notes de
              déploiement, et les notes d'analyse (retour du cabinet,
              choix d'interface, méthode de l'étude automatique).
              Les cinq rapports hebdomadaires sont dans leur sous-dossier.
FIN

echo "── Compression…"
(cd "$DESTINATION" && zip -qr RentImmo_dossier_remise.zip RentImmo)
rm -rf "$ETAPE"
echo "Dossier prêt : $DESTINATION/RentImmo_dossier_remise.zip"
unzip -l "$DESTINATION/RentImmo_dossier_remise.zip" | tail -3
