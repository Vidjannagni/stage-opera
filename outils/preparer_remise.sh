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

echo "── Code source (archive Git du dernier commit)…"
git archive --format=tar HEAD | tar -x -C "$ETAPE/code"

echo "── Documents…"
cp cahier_des_charges.pdf feuille_de_route.pdf "$ETAPE/documents/"
cp rapport_semaine1.pdf "$ETAPE/documents/rapports_hebdomadaires/"
cp rapports/rapport_semaine[2-5].pdf "$ETAPE/documents/rapports_hebdomadaires/"
cp rapports/rapport_final.pdf "$ETAPE/documents/"
cp docs/guide_utilisation.md docs/script_demonstration.md \
   docs/retour_cabinet.md docs/deploiement.md "$ETAPE/documents/"

cat > "$ETAPE/LISEZMOI.txt" <<'FIN'
RentImmo — Dossier de remise (21 août 2026)
Choubel Consulting — René DANSOU & Marius HOUNKPETOHOU

  code/       Code source complet, prêt à l'exécution :
                cd code && ./lancer.sh --demo
              puis http://127.0.0.1:5000 (demo@choubel.com / demo1234).
  documents/  Rapport final, cahier des charges, feuille de route,
              guide d'utilisation, script de démonstration,
              et les cinq rapports hebdomadaires.
FIN

echo "── Compression…"
(cd "$DESTINATION" && zip -qr RentImmo_dossier_remise.zip RentImmo)
rm -rf "$ETAPE"
echo "Dossier prêt : $DESTINATION/RentImmo_dossier_remise.zip"
unzip -l "$DESTINATION/RentImmo_dossier_remise.zip" | tail -3
