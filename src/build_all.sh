#!/usr/bin/env bash
# Rebuild every logo file, PNG export, README preview and the guidelines sheet.
# Needs: python3 with fonttools + uharfbuzz, rsvg-convert (librsvg), ImageMagick, Chromium.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 src/build_logo.py
python3 src/build_guide.py
rm -f guidelines/TIVONIQ-logo-guidelines.html
mkdir -p logo/png previews
for f in logo/svg/*.svg; do
  n=$(basename "${f%.svg}")
  case $n in *mark*) w=1024 ;; *) w=2400 ;; esac
  rsvg-convert -w "$w" "$f" -o "logo/png/$n.png"
  case $n in
    *-white) bg="#0B2447" ;;
    *) bg="#FFFFFF" ;;
  esac
  case $n in *horizontal*|*wordmark*) h=150 ;; *) h=300 ;; esac
  rsvg-convert -h "$h" -b "$bg" "$f" -o /tmp/tivoniq-preview.png
  magick /tmp/tivoniq-preview.png -bordercolor "$bg" -border 48 "previews/$n.png"
done
rm -f /tmp/tivoniq-preview.png
echo "done"
