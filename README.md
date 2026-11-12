# Hasköy

[![Cover](cover.png)](https://haskoy.ertekinn.com/)

Hasköy is an open-source variable sans-serif typeface family. Designed with powerful opentype features and each weight includes latin-extended language support, stylistic alternates, fractions, tabular figures, arrows and more. Currently, the family includes Latin Vietnamese, Pinyin, and all Western, Central, and South-Eastern European language support.

All weights, styles and opentype features of the Hasköy family can be tested on [haskoy.ertekinn.com](https://haskoy.ertekinn.com/)


## Building the Fonts

The source is `source/haskoy.glyphs` (Glyphs 3). The fonts are built with [gftools builder](https://github.com/googlefonts/gftools), the same toolchain Google Fonts uses.

The italics are slanted versions of the upright masters. `source/prepare_sources.py` creates the upright and italic designspaces from the `.glyphs` file, using the Rename Glyphs, Decompose Glyphs and Transformations parameters of the "Italic" instance. To change the italic, edit those parameters in Glyphs.

Set up a virtual environment once (Python 3.10–3.12):

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then build:

```
sh source/build.sh
```

Output goes to `fonts/`:

- `fonts/variable`: `Haskoy[wght].ttf` and `Haskoy-Italic[wght].ttf`
- `fonts/ttf`: static TTFs
- `fonts/otf`: static OTFs
- `fonts/webfonts`: WOFF2

To check the fonts against Google Fonts' requirements:

```
fontbakery check-googlefonts fonts/variable/*.ttf
```

## License

Hasköy is licensed under the SIL Open Font License v1.1, see [OFL.txt](OFL.txt) for details.
