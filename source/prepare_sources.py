"""Prepare build sources for gftools builder.

Hasköy's italics are slanted romans. Glyphs.app produces them on export with
custom parameters on the "Italic" instances (Rename Glyphs, Decompose Glyphs and a
Transformations filter). fontmake can only apply those to static instances, so
Google Fonts' required `Haskoy-Italic[wght].ttf` can't be built straight from the
.glyphs file.

This script reads haskoy.glyphs and writes, into source/build/:

  Haskoy.designspace         upright masters + upright instances
  Haskoy-Italic.designspace  the same masters, slanted using the parameters of
                             the "Italic" instance in haskoy.glyphs

The .glyphs file stays the single source of truth: change the slant there and
the italic build follows.
"""

import math
import shutil
from pathlib import Path

import glyphsLib
import ufoLib2
from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.pens.pointPen import ReverseContourPointPen
from fontTools.pens.recordingPen import RecordingPointPen
from fontTools.pens.transformPen import TransformPointPen

HERE = Path(__file__).parent
SOURCE = HERE / "haskoy.glyphs"
OUT = HERE / "build"
ITALIC_TEMPLATE_INSTANCE = "Italic"


def italic_params(gsfont):
    inst = next(i for i in gsfont.instances if i.name == ITALIC_TEMPLATE_INSTANCE)
    params = {p.name: p.value for p in inst.customParameters}
    renames = []
    for item in params.get("Rename Glyphs", []):
        a, b = item.split("=")
        renames.append((a.strip(), b.strip()))
    decompose = []
    for item in params.get("Decompose Glyphs", []):
        decompose += [n.strip() for n in item.split(",") if n.strip()]
    filt = dict(
        kv.split(":") for kv in params["Filter"].split(";")[1:] if ":" in kv
    )
    return {
        "renames": renames,
        "decompose": decompose,
        "slant": float(filt.get("Slant", 0)),
        "offset_x": float(filt.get("OffsetX", 0)),
        "angle": float(params.get("italicAngle", filt.get("Slant", 0))),
    }


def swap_glyphs(layer, a, b):
    if a not in layer or b not in layer:
        return
    ga, gb = layer[a], layer[b]
    for attr in ("contours", "components", "anchors"):
        va, vb = list(getattr(ga, attr)), list(getattr(gb, attr))
        getattr(ga, attr).clear(); getattr(gb, attr).clear()
        getattr(ga, attr).extend(vb); getattr(gb, attr).extend(va)
    ga.width, gb.width = gb.width, ga.width


def draw_decomposed(layer, glyph, pen):
    """Draw `glyph` with all components flattened. Mirrored components get their
    contours reversed so the outline direction stays correct."""
    glyph.drawPoints(_ContoursOnly(pen))
    for c in glyph.components:
        xx, xy, yx, yy, dx, dy = c.transformation
        tpen = TransformPointPen(pen, c.transformation)
        if xx * yy - xy * yx < 0:
            tpen = ReverseContourPointPen(tpen)
        draw_decomposed(layer, layer[c.baseGlyph], tpen)


class _ContoursOnly:
    def __init__(self, pen):
        self.pen = pen

    def beginPath(self, **kw):
        self.pen.beginPath(**kw)

    def endPath(self):
        self.pen.endPath()

    def addPoint(self, *a, **kw):
        self.pen.addPoint(*a, **kw)

    def addComponent(self, *a, **kw):
        pass


def decompose(layer, name):
    g = layer[name]
    if not g.components:
        return
    rec = RecordingPointPen()
    draw_decomposed(layer, g, rec)
    g.clearContours(); g.clearComponents()
    rec.replay(g.getPointPen())


def needs_decompose(glyph):
    # Slanting a flipped or rotated component in place would skew it the wrong way.
    return any(tuple(c.transformation[:4]) != (1, 0, 0, 1) for c in glyph.components)


def slant_layer(layer, slant_deg, offset_x):
    t = math.tan(math.radians(slant_deg))
    xf = lambda x, y: (x + y * t + offset_x, y)
    for g in layer:
        for c in g.contours:
            for p in c.points:
                p.x, p.y = xf(p.x, p.y)
        for comp in g.components:
            xx, xy, yx, yy, dx, dy = comp.transformation
            # the base glyph is slanted already; only move the offset
            comp.transformation = (xx, xy, yx, yy, dx + dy * t, dy)
        for a in g.anchors:
            a.x, a.y = xf(a.x, a.y)


def make_italic(ufo_path, params):
    ufo = ufoLib2.Font.open(ufo_path)
    for layer in ufo.layers:
        for a, b in params["renames"]:
            swap_glyphs(layer, a, b)
        names = set(params["decompose"]) | {g.name for g in layer if needs_decompose(g)}
        for n in sorted(names):
            if n in layer:
                decompose(layer, n)
        slant_layer(layer, params["slant"], params["offset_x"])
    ufo.info.italicAngle = -params["angle"]
    ufo.info.styleMapStyleName = "bold italic" if ufo.info.styleMapStyleName == "bold" else "italic"
    ufo.info.styleName = (ufo.info.styleName + " Italic").replace("Regular Italic", "Italic")
    ufo.save(ufo_path, overwrite=True)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    gsfont = glyphsLib.GSFont(SOURCE)
    params = italic_params(gsfont)
    # write_skipexportglyphs: keep non-exporting parts (lowercase-curve...) out of the fonts
    ds = glyphsLib.to_designspace(gsfont, ufo_module=ufoLib2, write_skipexportglyphs=True)

    # Save upright master UFOs (brace layers live inside them as extra layers).
    saved = {}
    for s in ds.sources:
        path = OUT / s.filename
        if s.filename not in saved:
            s.font.save(path, overwrite=True)
            saved[s.filename] = path
        s.path, s.font = str(path), None

    is_italic = lambda i: "Italic" in (i.styleName or "")
    all_instances = ds.instances
    for i in all_instances:
        # The Glyphs-only export parameters are replaced by make_italic() below.
        i.lib.pop("com.schriftgestaltung.customParameters", None)

    italic = DesignSpaceDocument.fromstring(ds.tostring())

    ds.instances = [i for i in all_instances if not is_italic(i)]
    ds.write(OUT / "Haskoy.designspace")

    for filename, path in saved.items():
        dst = path.with_name(path.stem + "Italic.ufo")
        shutil.copytree(path, dst)
        make_italic(dst, params)
    for s in italic.sources:
        s.filename = Path(s.filename).stem + "Italic.ufo"
        s.path = str(OUT / s.filename)
        if s.layerName is None:
            s.styleName = (s.styleName + " Italic").replace("Regular Italic", "Italic")
    italic.instances = [i for i in italic.instances if is_italic(i)]
    italic.write(OUT / "Haskoy-Italic.designspace")
    print("wrote", OUT / "Haskoy.designspace", "and", OUT / "Haskoy-Italic.designspace")


if __name__ == "__main__":
    main()
