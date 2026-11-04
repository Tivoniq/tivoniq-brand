"""TIVONIQ logo, rebuilt as clean vector geometry.

Everything is drawn on one grid. 1 unit (u) = 1/10 of the stroke.
  stroke t        = 10u   crossbar height = stem width = perpendicular width of each V arm
  diagonals       = 60 deg (crossbar ends, both V arms, the T stem's bend)
  left arm        = 1.2t perpendicular: it carries the T's stem, so it is drawn heavier
  corner radii    = 4u (0.4t) on the crossbar's obtuse corners, 8u (0.8t) on the stem bend and the V point
  data pixels     = 6 squares on the integer grid, sizes 2u / 3u / 4u (ratio 2:3:4)
  notch           = one 3u pixel bitten out of the right arm's inner top corner
  fold            = the right arm ends in a round cap (radius t/2) centred level with the
                    inner vertex; it lands exactly tangent to the left arm's inner edge
  wordmark        = cap height 1.4t, one stroke weight (0.18 of cap height), O/Q are
                    rounded rectangles, the Q tail runs at 45 deg
  stacked lockup  = wordmark 1.4t cap height, 0.75t below the mark, tagline 1t below the
                    wordmark and exactly as wide as it
  horizontal      = wordmark 2t cap height, 1.5t right of the mark, centred on the V body
  one colour      = 0.08t knock-out gaps between T and V and around the fold

Run: python src/build_logo.py   (needs fontTools + uharfbuzz, see requirements.txt)
"""
import math
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "logo" / "svg"
FONTS = ROOT / "fonts"
R3 = math.sqrt(3)

# ---------------------------------------------------------------- colours
C = {
    "navy": "#072658",          # wordmark
    "teal": "#08B9B2",          # wordmark Q
    # gradient stops fitted to the original artwork's pixels
    "t0": "#063874", "t1": "#078AC9",       # T: deep navy -> blue
    "v0": "#0598B2", "v1": "#0BBBB2",       # V ribbon (left arm + round point): blue-teal -> teal
    "r0": "#068EB5", "r1": "#04D7B3",       # right arm, laid over the fold: blue-teal -> mint
    "s0": "#0391B6", "s1": "#05CBB1",       # data pixels
}


def f(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# ---------------------------------------------------------------- path helpers
def rounded_path(pts, radii):
    """Closed polygon with circular fillets of radius radii[i] at pts[i] (0 = sharp)."""
    n = len(pts)
    items = []
    for i, P in enumerate(pts):
        r = radii[i]
        if not r:
            items.append(("p", P))
            continue
        A, B = pts[i - 1], pts[(i + 1) % n]
        u1 = (A[0] - P[0], A[1] - P[1]); l1 = math.hypot(*u1); u1 = (u1[0] / l1, u1[1] / l1)
        u2 = (B[0] - P[0], B[1] - P[1]); l2 = math.hypot(*u2); u2 = (u2[0] / l2, u2[1] / l2)
        ang = math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1])))
        d = r / math.tan(ang / 2)
        T1 = (P[0] + u1[0] * d, P[1] + u1[1] * d)
        T2 = (P[0] + u2[0] * d, P[1] + u2[1] * d)
        z = (P[0] - A[0]) * (B[1] - P[1]) - (P[1] - A[1]) * (B[0] - P[0])
        items.append(("a", T1, T2, r, 1 if z > 0 else 0))
    start = items[0][1]
    d = [f"M{f(start[0])} {f(start[1])}"]
    for k, it in enumerate(items):
        if it[0] == "p":
            if k:
                d.append(f"L{f(it[1][0])} {f(it[1][1])}")
        else:
            if k:
                d.append(f"L{f(it[1][0])} {f(it[1][1])}")
            d.append(f"A{f(it[3])} {f(it[3])} 0 0 {it[4]} {f(it[2][0])} {f(it[2][1])}")
    d.append("Z")
    return "".join(d)


def poly(pts):
    return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts) + "Z"


class RRect:
    """Rounded rectangle boundary, walked clockwise (screen coords, y down)."""

    def __init__(self, x0, y0, x1, y1, r):
        self.r = r
        self.prims = [
            ("L", (x0 + r, y0), (x1 - r, y0)),
            ("A", (x1 - r, y0 + r), -90, 0),
            ("L", (x1, y0 + r), (x1, y1 - r)),
            ("A", (x1 - r, y1 - r), 0, 90),
            ("L", (x1 - r, y1), (x0 + r, y1)),
            ("A", (x0 + r, y1 - r), 90, 180),
            ("L", (x0, y1 - r), (x0, y0 + r)),
            ("A", (x0 + r, y0 + r), 180, 270),
        ]

    def point(self, i, t):
        p = self.prims[i]
        if p[0] == "L":
            (ax, ay), (bx, by) = p[1], p[2]
            return (ax + (bx - ax) * t, ay + (by - ay) * t)
        c, a = p[1], math.radians(t)
        return (c[0] + self.r * math.cos(a), c[1] + self.r * math.sin(a))

    def hits(self, c):
        """Intersections with the line x - y = c, as (prim index, param)."""
        out = []
        for i, p in enumerate(self.prims):
            if p[0] == "L":
                (ax, ay), (bx, by) = p[1], p[2]
                den = (bx - ax) - (by - ay)
                if abs(den) < 1e-12:
                    continue
                t = (c - (ax - ay)) / den
                if -1e-9 <= t <= 1 + 1e-9:
                    out.append((i, t))
            else:
                (cx, cy), a0, a1 = p[1], p[2], p[3]
                # (x-cx)^2 + (y-cy)^2 = r^2 with x = y + c
                k = c - cx
                A, B, Cc = 2, 2 * (k - cy), k * k + cy * cy - self.r ** 2
                disc = B * B - 4 * A * Cc
                if disc < 0:
                    continue
                for s in (1, -1):
                    y = (-B + s * math.sqrt(disc)) / (2 * A)
                    x = y + c
                    ang = math.degrees(math.atan2(y - cy, x - cx))
                    for cand in (ang, ang + 360, ang - 360):
                        if a0 - 1e-9 <= cand <= a1 + 1e-9:
                            out.append((i, cand))
        return out

    def walk(self, frm, to, cw=True):
        """SVG commands from position frm to position to along the boundary (excluding the M)."""
        cmds = []
        n = len(self.prims)
        i, t = frm
        j, tj = to

        def seg_end(k):
            p = self.prims[k]
            return (1.0 if p[0] == "L" else p[3]) if cw else (0.0 if p[0] == "L" else p[2])

        def emit(k, t_from, t_to):
            p = self.prims[k]
            x, y = self.point(k, t_to)
            if p[0] == "L":
                cmds.append(f"L{f(x)} {f(y)}")
            elif abs(t_to - t_from) > 1e-9:
                cmds.append(f"A{f(self.r)} {f(self.r)} 0 0 {1 if cw else 0} {f(x)} {f(y)}")

        def before(a, b):  # a comes before b along the walking direction on the same prim
            return a <= b + 1e-12 if cw else a >= b - 1e-12

        first = True
        while True:
            if i == j and before(t, tj) and not (first and False):
                emit(i, t, tj)
                return "".join(cmds)
            e = seg_end(i)
            emit(i, t, e)
            i = (i + 1) % n if cw else (i - 1) % n
            p = self.prims[i]
            t = (0.0 if p[0] == "L" else p[2]) if cw else (1.0 if p[0] == "L" else p[3])
            first = False


def rrect_path(x0, y0, x1, y1, r, cw=True):
    rr = RRect(x0, y0, x1, y1, r)
    if cw:
        s = rr.point(0, 0)
        return f"M{f(s[0])} {f(s[1])}" + rr.walk((0, 0.0), (7, 270.0), True) + "Z"
    s = rr.point(7, 270)
    return f"M{f(s[0])} {f(s[1])}" + rr.walk((7, 270.0), (0, 0.0), False) + "Z"


# ---------------------------------------------------------------- the mark
t = 10.0
W = 2 * t / R3                 # horizontal width of a 60deg arm whose perpendicular width is t
WL = 1.2 * W                   # left arm: 1.2t perpendicular
yv = 31.0                      # inner vertex height
NOTCH, STEP = 3.0, 54.0        # notch depth and the x of its vertical step
xv = (STEP - NOTCH) - (yv - NOTCH) / R3   # so the notch is exactly a 3u x 3u pixel at its foot

Ri = lambda y: xv + (yv - y) / R3          # right arm inner edge
Ro = lambda y: xv + W + (yv - y) / R3      # right arm outer edge
Li = lambda y: xv - (yv - y) / R3          # left arm inner edge
Lo = lambda y: xv - WL - (yv - y) / R3      # left arm outer edge
y_at_Li = lambda x: yv - (xv - x) * R3
y_at_Lo = lambda x: yv - (xv - WL - x) * R3

STEM0, STEM1 = 16.0, 26.0
BAR_R = 40.0                   # bottom-right x of the crossbar
r_small, r_big = 0.4 * t, 0.8 * t

T_PTS = [
    (t / R3, 0), (BAR_R + t / R3, 0), (BAR_R, t), (STEM1, t),
    (STEM1, y_at_Lo(STEM1)), (STEM0, y_at_Lo(STEM0)), (STEM0, t), (0, t),
]
T_RAD = [r_small, 0, r_small, 0, 0, r_big, 0, 0]

apex = (xv + (W - WL) / 2, yv + (W + WL) * R3 / 2)
hidden = (Lo(28.0), 28.0)       # V's left edge continues under the stem, out of sight
V_PTS = [
    (STEP, 0), (Ro(0), 0), apex, hidden, (STEM1, y_at_Li(STEM1)),
    (xv, yv), (Ri(NOTCH), NOTCH), (STEP, NOTCH),
]
V_RAD = [0, 0, r_big, 0, 0, 0, 0, 0]

# right arm with its round cap (radius t/2) centred on the arm's centre line, level with the vertex
cap_c = (xv + W / 2, yv)
nrm = (R3 / 2, 0.5)
co = (cap_c[0] + t / 2 * nrm[0], cap_c[1] + t / 2 * nrm[1])
ci = (cap_c[0] - t / 2 * nrm[0], cap_c[1] - t / 2 * nrm[1])
cm = (cap_c[0] - t / 2 * 0.5, cap_c[1] + t / 2 * R3 / 2)
RA_D = (
    f"M{f(STEP)} 0L{f(Ro(0))} 0L{f(co[0])} {f(co[1])}"
    f"A{f(t/2)} {f(t/2)} 0 0 1 {f(cm[0])} {f(cm[1])}"
    f"A{f(t/2)} {f(t/2)} 0 0 1 {f(ci[0])} {f(ci[1])}"
    f"L{f(Ri(NOTCH))} {f(NOTCH)}L{f(STEP)} {f(NOTCH)}Z"
)

# data pixels: (x, y, size) on the integer grid
SQUARES = [(49, -4, 4), (58, -4, 2), (53, -10, 4), (61, -10, 4), (58, -15, 3), (65, -17, 3)]

MONO_GAP = 0.08 * t            # knock-out width in the one-colour mark
MARK_TOP = min(y for _, y, _ in SQUARES)
MARK_BOTTOM = apex[1] - r_big                         # round point of the V
MARK_RIGHT = max(x + s for x, _, s in SQUARES)


def mark_svg(mode, gid, dx=0.0, dy=0.0):
    """mode: color | mono (single fill, given as mode='mono:#hex')."""
    tr = f' transform="translate({f(dx)} {f(dy)})"' if dx or dy else ""
    if mode == "color":
        # gradient axes in mark coordinates
        defs = (
            f'<linearGradient id="{gid}t" gradientUnits="userSpaceOnUse" x1="11" y1="18.4" x2="39.2" y2="-2.3">'
            f'<stop offset="0" stop-color="{C["t0"]}"/><stop offset="1" stop-color="{C["t1"]}"/></linearGradient>'
            f'<linearGradient id="{gid}v" gradientUnits="userSpaceOnUse" x1="26" y1="0" x2="45" y2="0">'
            f'<stop offset="0" stop-color="{C["v0"]}"/><stop offset="1" stop-color="{C["v1"]}"/></linearGradient>'
            f'<linearGradient id="{gid}r" gradientUnits="userSpaceOnUse" x1="36.8" y1="0" x2="61.6" y2="0">'
            f'<stop offset="0" stop-color="{C["r0"]}"/><stop offset="1" stop-color="{C["r1"]}"/></linearGradient>'
            f'<linearGradient id="{gid}s" gradientUnits="userSpaceOnUse" x1="49" y1="0" x2="68" y2="-17">'
            f'<stop offset="0" stop-color="{C["s0"]}"/><stop offset="1" stop-color="{C["s1"]}"/></linearGradient>'
        )
        fv, fr, ft, fs = (f"url(#{gid}{k})" for k in "vrts")
    else:
        # one colour: the V ribbon gets knock-out gaps (MONO_GAP wide) along the stem's edge
        # and around the fold's cap, so the T, the V and the fold still read as separate parts
        col = mode.split(":", 1)[1]
        g2 = f(2 * MONO_GAP)
        seam = f"M{f(STEM1)} {f(y_at_Li(STEM1) - 1)}L{f(STEM1)} {f(y_at_Lo(STEM1))}"
        fold = (f"M{f(Ri(yv - 6))} {f(yv - 6)}L{f(ci[0])} {f(ci[1])}"
                f"A{f(t/2)} {f(t/2)} 0 0 0 {f(cm[0])} {f(cm[1])}A{f(t/2)} {f(t/2)} 0 0 0 {f(co[0])} {f(co[1])}")
        defs = (
            f'<mask id="{gid}k" maskUnits="userSpaceOnUse" x="-10" y="-30" width="100" height="100">'
            f'<rect x="-10" y="-30" width="100" height="100" fill="#fff"/>'
            f'<path d="{seam}" stroke="#000" stroke-width="{g2}" fill="none"/>'
            f'<path d="{fold}" stroke="#000" stroke-width="{g2}" fill="none"/></mask>'
        )
        fv = fr = ft = fs = col
    sq = "".join(f'<rect x="{x}" y="{y}" width="{s}" height="{s}"/>' for x, y, s in SQUARES)
    vmask = f' mask="url(#{gid}k)"' if mode != "color" else ""
    body = (
        f'<path fill="{fv}"{vmask} d="{rounded_path(V_PTS, V_RAD)}"/>'
        f'<path fill="{fr}" d="{RA_D}"/>'
        f'<path fill="{ft}" d="{rounded_path(T_PTS, T_RAD)}"/>'
        f'<g fill="{fs}">{sq}</g>'
    )
    return defs, f"<g{tr}>{body}</g>"


# ---------------------------------------------------------------- the wordmark (cap height 96)
WH, S = 96.0, 17.5
GAP = 25.0


def wm_letters():
    x = 0.0
    shapes = []  # (d, kind) kind: navy|teal

    # T
    tw = 113.0
    shapes.append((poly([(x, 0), (x + tw, 0), (x + tw, S), (x + tw / 2 + S / 2, S), (x + tw / 2 + S / 2, WH),
                         (x + tw / 2 - S / 2, WH), (x + tw / 2 - S / 2, S), (x, S)]), "navy"))
    x += tw + GAP
    # I
    shapes.append((poly([(x, 0), (x + S, 0), (x + S, WH), (x, WH)]), "navy")); x += S + GAP
    # V: 122 wide at the top, flat foot as wide as the stroke
    vw = 122.0; k = (vw - S) / 2 / WH; hw = S * math.sqrt(1 + k * k)
    yi = (vw - 2 * hw) / (2 * k)
    shapes.append((poly([(x, 0), (x + hw, 0), (x + vw / 2, yi), (x + vw - hw, 0), (x + vw, 0),
                         (x + vw / 2 + S / 2, WH), (x + vw / 2 - S / 2, WH)]), "navy"))
    x += vw + 11.5               # optical: the V's open top sits closer to the O
    # O
    ow, orr = 130.0, 41.0
    shapes.append((rrect_path(x, 0, x + ow, WH, orr) + rrect_path(x + S, S, x + ow - S, WH - S, orr - S, cw=False), "navy"))
    x += ow + GAP
    # N: diagonal centre line runs corner to corner
    nw = 110.0; kn = (nw) / WH; hd = S * math.sqrt(1 + kn * kn) / 2
    a, b = x, x + nw
    yr = lambda xx: (xx - (a + hd)) / kn       # diagonal right edge: x = a + hd + kn*y
    yl = lambda xx: (xx - (a - hd)) / kn       # diagonal left edge
    shapes.append((poly([(a, 0), (a + S, 0), (a + S, yr(a + S)), (b - S, yr(b - S)), (b - S, 0), (b, 0), (b, WH),
                         (b - S, WH), (b - S, yl(b - S)), (a + S, yl(a + S)), (a + S, WH), (a, WH)]), "navy"))
    x += nw + GAP
    # I
    shapes.append((poly([(x, 0), (x + S, 0), (x + S, WH), (x, WH)]), "navy")); x += S + GAP
    # Q: the O, cut by a 45deg tail whose left edge is the line x - y = q0 (through the box's top-left corner)
    q0 = x
    outer = RRect(q0, 0, q0 + ow, WH, orr)
    inner = RRect(q0 + S, S, q0 + ow - S, WH - S, orr - S)
    gap = S / 4 * math.sqrt(2)                 # knock-out on the tail's left side, S/4 perpendicular
    pick = lambda hits: max(hits, key=lambda h: (lambda p: p[1])(None) if False else 0) if False else hits
    def bottom_right(rr, c):
        hs = rr.hits(c)
        return max(hs, key=lambda h: rr.point(*h)[1])
    Ao = bottom_right(outer, q0); Bo = bottom_right(outer, q0 - gap)
    Ai = bottom_right(inner, q0); Bi = bottom_right(inner, q0 - gap)
    pBo, pAi = outer.point(*Bo), inner.point(*Ai)
    ring = (f"M{f(pBo[0])} {f(pBo[1])}" + outer.walk(Bo, Ao, True) + f"L{f(pAi[0])} {f(pAi[1])}"
            + inner.walk(Ai, Bi, False) + "Z")
    tw2 = S * math.sqrt(2); top, bot = 61.0, WH + S / 2
    tail = poly([(q0 + top, top), (q0 + top + tw2, top), (q0 + bot + tw2, bot), (q0 + bot, bot)])
    shapes.append((ring + tail, "teal"))
    x += ow
    return shapes, x


WM_SHAPES, WM_W = wm_letters()
WM_DESC = WH + S / 2           # lowest point (Q tail)


def wordmark_svg(mode, scale, dx, dy):
    """mode: color | mono:#hex. Placed with the cap top-left at (dx, dy)."""
    parts = []
    for d, kind in WM_SHAPES:
        col = (C[kind] if mode == "color" else mode.split(":", 1)[1])
        parts.append(f'<path fill="{col}" d="{d}"/>')
    return f'<g transform="translate({f(dx)} {f(dy)}) scale({f(scale)})">{"".join(parts)}</g>'


# ---------------------------------------------------------------- tagline (Inter, outlined)
TAGLINE = "Innovate. Integrate. Elevate."


def tagline_paths(target_width):
    import uharfbuzz as hb
    path = FONTS / "Inter.ttf"
    blob = hb.Blob.from_file_path(str(path))
    face = hb.Face(blob)
    font = hb.Font(face)
    font.set_variations({"wght": 400, "opsz": 14})
    buf = hb.Buffer(); buf.add_str(TAGLINE); buf.guess_segment_properties()
    hb.shape(font, buf, {"cv11": True, "kern": True})
    tt = TTFont(path)
    tt = instantiateVariableFont(tt, {"wght": 400, "opsz": 14})
    gs = tt.getGlyphSet(); order = tt.getGlyphOrder()
    upm = tt["head"].unitsPerEm
    cap = tt["OS/2"].sCapHeight
    total = sum(p.x_advance for p in buf.glyph_positions)
    # visible ink width: drop the first glyph's left side bearing and the last glyph's right one
    from fontTools.pens.boundsPen import BoundsPen
    def bounds(gname):
        bp = BoundsPen(gs); gs[gname].draw(bp); return bp.bounds
    first, last = order[buf.glyph_infos[0].codepoint], order[buf.glyph_infos[-1].codepoint]
    lsb = bounds(first)[0]
    rsb = buf.glyph_positions[-1].x_advance - bounds(last)[2]
    ink = total - lsb - rsb
    s = target_width / ink
    pens, x = [], -lsb
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        g = order[info.codepoint]
        pen = SVGPathPen(gs)
        tp = TransformPen(pen, (s, 0, 0, -s, (x + pos.x_offset) * s, cap * s))
        gs[g].draw(tp)
        d = pen.getCommands()
        if d:
            pens.append(d)
        x += pos.x_advance
    from fontTools.pens.boundsPen import BoundsPen as BP
    ymin = 0
    x = -lsb
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        bp = BP(gs); gs[order[info.codepoint]].draw(bp)
        if bp.bounds: ymin = min(ymin, bp.bounds[1])
    return "".join(pens), cap * s, (cap - ymin) * s


# ---------------------------------------------------------------- compositions
K = 14.0 / WH                     # wordmark scale: cap height 1.4t
WM_W_U = WM_W * K
LOCK_GAP = 0.75 * t
TAG_GAP = 1.0 * t
MW = MARK_RIGHT
MH = MARK_BOTTOM - MARK_TOP


def svg_doc(w, h, defs, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(w)} {f(h)}" width="{f(w * 10)}" height="{f(h * 10)}">'
        f"<title>{title}</title>" + (f"<defs>{defs}</defs>" if defs else "") + body + "</svg>\n"
    )


def build(variant, mode):
    wm_mode = mode if mode != "color" else "color"
    if variant == "mark":
        defs, body = mark_svg(mode, "m", 0, -MARK_TOP)
        return svg_doc(MW, MH, defs, body, "TIVONIQ")
    if variant == "wordmark":
        body = wordmark_svg(wm_mode, K, 0, 0)
        return svg_doc(WM_W_U, WM_DESC * K, "", body, "TIVONIQ")
    if variant in ("stacked", "stacked-tagline"):
        W_ = WM_W_U
        mx = (W_ - MW) / 2
        defs, body = mark_svg(mode, "m", mx, -MARK_TOP)
        wy = MH + LOCK_GAP
        body += wordmark_svg(wm_mode, K, 0, wy)
        H_ = wy + WM_DESC * K
        if variant == "stacked-tagline":
            d, capu, inku = tagline_paths(W_)
            ty = wy + WH * K + TAG_GAP
            col = C["navy"] if mode == "color" else mode.split(":", 1)[1]
            body += f'<path fill="{col}" transform="translate(0 {f(ty)})" d="{d}"/>'
            H_ = ty + inku
        return svg_doc(W_, H_, defs, body, "TIVONIQ")
    if variant == "horizontal":
        defs, body = mark_svg(mode, "m", 0, -MARK_TOP)
        # wordmark cap height 2t, centred on the V body (crossbar top .. V point), 1.5t from the mark
        kh = 2 * t / WH
        body_mid = (-MARK_TOP) + (0 + MARK_BOTTOM) / 2
        wx = MW + 1.5 * t
        wy = body_mid - WH * kh / 2
        body += wordmark_svg(wm_mode, kh, wx, wy)
        return svg_doc(wx + WM_W * kh, MH, defs, body, "TIVONIQ")
    raise ValueError(variant)


if __name__ == "__main__":
    modes = {"color": "color", "navy": f"mono:{C['navy']}", "white": "mono:#FFFFFF", "black": "mono:#000000"}
    for variant in ("mark", "wordmark", "stacked", "stacked-tagline", "horizontal"):
        for name, mode in modes.items():
            (OUT / f"tivoniq-{variant}-{name}.svg").write_text(build(variant, mode))
    print("mark", f(MW), "x", f(MH), "| wordmark", f(WM_W_U), "| xv", f(xv))
