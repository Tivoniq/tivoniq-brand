"""TIVONIQ Academy: the TIVONIQ logo with an ACADEMY descriptor.

The mark, the wordmark, the colours and the lockup spacing are imported unchanged from
build_logo.py; this file only adds the descriptor and places it.

  descriptor      = "ACADEMY" in Inter SemiBold caps, converted to outlines, cap height half
                    the wordmark's, tracked so its ink is exactly as wide as the wordmark
                    (the same width rule as the tagline)
  stacked         = the stacked lockup, descriptor 1t below the wordmark baseline
                    (the tagline's spacing)
  horizontal      = wordmark 2t cap height, descriptor below it; the two-line block is
                    centred on the T-V body, 1.5t right of the mark
  wordmark        = wordmark + descriptor, no mark (where the mark already appears nearby)
  colour          = descriptor in teal, the colour of the Q; one colour = everything one colour

Run: python src/build_academy.py   (needs fonts/Inter.ttf, see fonts/README.md)
"""
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from build_logo import (
    C, FONTS, K, LOCK_GAP, MARK_BOTTOM, MARK_TOP, MH, MW, ROOT, TAG_GAP, WH, WM_DESC, WM_W,
    WM_W_U, f, mark_svg, svg_doc, t, wordmark_svg,
)

OUT = ROOT / "academy" / "svg"
WORD = "ACADEMY"
WGHT = 600                     # Inter SemiBold
DESC_CAP = 0.5                 # descriptor cap height, as a fraction of the wordmark's
NAME = "TIVONIQ Academy"


def descriptor_paths(target_width, cap_height):
    """WORD outlined in Inter, cap top at y=0, baseline at y=cap_height, ink exactly target_width wide."""
    import uharfbuzz as hb

    path = FONTS / "Inter.ttf"
    axes = {"wght": WGHT, "opsz": 14}
    font = hb.Font(hb.Face(hb.Blob.from_file_path(str(path))))
    font.set_variations(axes)
    buf = hb.Buffer(); buf.add_str(WORD); buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True})

    tt = instantiateVariableFont(TTFont(path), axes)
    gs, order = tt.getGlyphSet(), tt.getGlyphOrder()
    s = cap_height / tt["OS/2"].sCapHeight

    glyphs = []                  # (name, pen x of origin in font units, ink x0, ink x1)
    x = 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        g = order[info.codepoint]
        bp = BoundsPen(gs); gs[g].draw(bp)
        x0, _, x1, _ = bp.bounds
        glyphs.append((g, x + pos.x_offset, x0, x1))
        x += pos.x_advance
    first, last = glyphs[0], glyphs[-1]
    natural = (last[1] + last[3]) - (first[1] + first[2])
    track = (target_width / s - natural) / (len(glyphs) - 1)   # equal extra space between letters

    d = []
    for i, (g, gx, x0, _) in enumerate(glyphs):
        ox = gx - (first[1] + first[2]) + i * track
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, ox * s, cap_height)))
        d.append(pen.getCommands())
    return "".join(d), track * s


def desc_color(mode):
    return C["teal"] if mode == "color" else mode.split(":", 1)[1]


def build(variant, mode):
    if variant in ("stacked", "wordmark"):
        w = WM_W_U
        cap = DESC_CAP * WH * K
        defs, body, wy = "", "", 0.0
        if variant == "stacked":
            defs, body = mark_svg(mode, "m", (w - MW) / 2, -MARK_TOP)
            wy = MH + LOCK_GAP
        body += wordmark_svg(mode, K, 0, wy)
        dy = wy + WH * K + TAG_GAP
        d, _ = descriptor_paths(w, cap)
        body += f'<path fill="{desc_color(mode)}" transform="translate(0 {f(dy)})" d="{d}"/>'
        return svg_doc(w, dy + cap, defs, body, NAME)

    if variant == "horizontal":
        kh = 2 * t / WH                     # wordmark cap height 2t, as in the horizontal logo
        cap = DESC_CAP * 2 * t
        gap = TAG_GAP * kh / K              # the stacked spacing, scaled with the wordmark
        block = 2 * t + gap + cap
        body_mid = -MARK_TOP + MARK_BOTTOM / 2
        wx = MW + 1.5 * t
        wy = body_mid - block / 2
        ww = WM_W * kh
        defs, body = mark_svg(mode, "m", 0, -MARK_TOP)
        body += wordmark_svg(mode, kh, wx, wy)
        d, _ = descriptor_paths(ww, cap)
        body += f'<path fill="{desc_color(mode)}" transform="translate({f(wx)} {f(wy + 2 * t + gap)})" d="{d}"/>'
        return svg_doc(wx + ww, MH, defs, body, NAME)

    raise ValueError(variant)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    modes = {"color": "color", "navy": f"mono:{C['navy']}", "white": "mono:#FFFFFF", "black": "mono:#000000"}
    for variant in ("stacked", "horizontal", "wordmark"):
        for name, mode in modes.items():
            (OUT / f"tivoniq-academy-{variant}-{name}.svg").write_text(build(variant, mode))
    _, tr = descriptor_paths(WM_W_U, DESC_CAP * WH * K)
    print("academy: 12 files | stacked descriptor tracking", f(tr), "u")
