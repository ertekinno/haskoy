#!/bin/sh
# Builds every Hasköy font into ../fonts (Google Fonts layout):
#   fonts/variable  Haskoy[wght].ttf, Haskoy-Italic[wght].ttf
#   fonts/ttf       static TTFs (autohinted)
#   fonts/otf       static OTFs
#   fonts/webfonts  WOFF2
set -e
cd "$(dirname "$0")"

echo "Preparing upright and italic sources from haskoy.glyphs"
python prepare_sources.py

echo "Building with gftools builder"
rm -rf ../fonts
gftools builder config.yaml

echo "Voila! Done."
