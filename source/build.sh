#!/bin/sh

set -e


echo "Generating fonts"

mkdir -p ./fonts/otf ./fonts/ttf ./fonts/ttf/static ./fonts/woff2 ./fonts/woff2/static
echo "Made font directories"
 
echo "Generating static TTFs"
fontmake -g source/haskoy.glyphs -i -o ttf --output-dir ./fonts/ttf/static/
echo "Made static TTFs"

echo "Post processing static TTFs"
ttfs=$(ls ./fonts/ttf/static/*.ttf)
for ttf in $ttfs
do
 	gftools fix-dsig -f $ttf;
 	ttfautohint $ttf $ttf.fix;
 	mv "$ttf.fix" $ttf;
 	gftools fix-hinting $ttf;
 	mv "$ttf.fix" $ttf;
	fonttools ttLib.woff2 compress $ttf;
done

echo "Generating VFs"
fontmake -g source/haskoy.glyphs -o variable --output-path ./fonts/ttf/Haskoy\[ital,wght\].ttf

python source/gen_stat.py ./fonts/ttf/Haskoy\[ital,wght\].ttf

fonttools varLib.instancer ./fonts/ttf/Haskoy\[ital,wght\].ttf ital=0 wght=100:800 --update-name-table -o ./fonts/ttf/Haskoy\[wght\].ttf
fonttools varLib.instancer ./fonts/ttf/Haskoy\[ital,wght\].ttf ital=1 wght=100:800 --update-name-table -o ./fonts/ttf/Haskoy-Italic\[wght\].ttf
python source/set_italic.py ./fonts/ttf/Haskoy-Italic\[wght\].ttf

rm ./fonts/ttf/Haskoy\[ital,wght\].ttf

echo "Made VFs"

echo "Post processing VFs"

vfs=$(ls ./fonts/ttf/*.ttf)
for vf in $vfs
do
	gftools fix-dsig -f $vf;
	gftools fix-unwanted-tables --tables MVAR $vf;
	gftools fix-nonhinting $vf "$vf.fix";
	mv "$vf.fix" $vf;
	fonttools ttLib.woff2 compress $vf;
done

echo "Generating static OTFs"
fontmake -g source/haskoy.glyphs -i -o otf --output-dir ./fonts/otf/

echo "Post processing static OTFs"
otf=$(ls ./fonts/otf/*.otf)
for otf in $otf
do
	gftools fix-dsig -f $otf;
done

echo "Woff2 static and VFs"

mv ./fonts/ttf/*.woff2 ./fonts/woff2
mv ./fonts/ttf/static/*.woff2 ./fonts/woff2/static

rm ./fonts/ttf/*backup*.ttf
rm -rf master_ufo/ instance_ufo/

echo "Build completed!"
