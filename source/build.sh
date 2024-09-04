#!/bin/sh
set -e

# Create output directories in the current directory
mkdir -p ../fonts/otf ../fonts/ttf ../fonts/ttf/static ../fonts/woff2 ../fonts/woff2/static

# Generate Variable Font directly from the .glyphs file
echo "Generating VFs"
VF_File=../fonts/ttf/Haskoy-variable.ttf
fontmake -g haskoy.glyphs -o variable --output-path $VF_File

# Post-processing for Variable Fonts
echo "Post processing VFs"
gftools fix-nonhinting $VF_File $VF_File.fix
mv $VF_File.fix $VF_File
gftools fix-unwanted-tables $VF_File -t MVAR
fonttools ttLib.woff2 compress $VF_File

# Generate Static TTFs from the .glyphs file
echo "Generating static TTFs"
fontmake -g haskoy.glyphs -i -o ttf --output-dir ../fonts/ttf/static/ -a

# Post-processing for Static TTFs
ttfs=$(ls ../fonts/ttf/static/*.ttf)
for ttf in $ttfs
do
	gftools fix-hinting $ttf
	mv "$ttf.fix" $ttf
	fonttools ttLib.woff2 compress $ttf
done

# Generate Static OTFs from the .glyphs file
echo "Generating static OTFs"
fontmake -g haskoy.glyphs -i -o otf --output-dir ../fonts/otf/ -a

# Move WOFF2 static and VF fonts
echo "Woff2 static and vf"
mv ../fonts/ttf/*.woff2 ../fonts/woff2
mv ../fonts/ttf/static/*.woff2 ../fonts/woff2/static

# Cleanup
rm -rf master_ufo/ instance_ufo/ ../fonts/ttf/*backup*.ttf *.ufo instance_ufo

echo "Voila! Done."
