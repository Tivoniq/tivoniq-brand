"""TIVONIQ logo guidelines sheet: construction, proportions, clear space, colours, minimum sizes.
Writes guidelines/TIVONIQ-logo-guidelines.pdf and .png via headless Chromium.
Run after build_logo.py."""
import math
import subprocess
from pathlib import Path

import build_logo as B

OUT = B.OUT
GD = B.ROOT / "guidelines"; GD.mkdir(exist_ok=True)
f = B.f
ACC = "#E5484D"      # annotation colour
t = B.t


def construction_svg():
    x0, y0, x1, y1 = -14, -26, 84, 58
    W, H = x1 - x0, y1 - y0
    g = []
    # grid: 1u fine, t (10u) strong
    for x in range(x0, x1 + 1):
        c = "#C5D0DE" if x % 10 == 0 else "#E9EEF4"
        g.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{c}" stroke-width="{0.16 if x % 10 == 0 else 0.08}"/>')
    for y in range(y0, y1 + 1):
        c = "#C5D0DE" if y % 10 == 0 else "#E9EEF4"
        g.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{c}" stroke-width="{0.16 if y % 10 == 0 else 0.08}"/>')
    defs, mark = B.mark_svg("color", "c")
    g.append(f'<g opacity=".9">{mark}</g>')
    R3 = B.R3

    def line(a, b, dash=True, w=0.18, col=ACC):
        da = ' stroke-dasharray="1 .8"' if dash else ""
        return f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" stroke="{col}" stroke-width="{w}"{da}/>'

    def label(x, y, s, anchor="start", size=2.1, col=ACC):
        return (f'<text x="{f(x)}" y="{f(y)}" font-size="{size}" fill="{col}" text-anchor="{anchor}" '
                f'font-family="Inter" font-weight="600">{s}</text>')

    # 60deg construction lines, extended
    for fn, ya, yb in ((B.Lo, 12, 50), (B.Li, 8, 40), (B.Ri, -6, 40), (B.Ro, -6, 40)):
        g.append(line((fn(ya), ya), (fn(yb), yb)))
    # crossbar slant lines
    g.append(line((10 / R3 + 3 / R3, -3), (-2 / R3 * 1, 12)))
    g.append(line((B.BAR_R + t / R3 + 3 / R3, -3), (B.BAR_R - 2 / R3, 12)))
    # angle marker at the V's right arm outer edge foot
    # dimension: crossbar height t
    g.append(line((-6, 0), (-6, 10), dash=False)); g.append(line((-7, 0), (-5, 0), dash=False)); g.append(line((-7, 10), (-5, 10), dash=False))
    g.append(label(-7.5, 5.8, "t", "end", 2.6))
    # stem width t
    g.append(line((16, 13), (26, 13), dash=False)); g.append(label(21, 12.2, "t", "middle", 2.4))
    # right arm perpendicular t
    pa = (B.Ri(18), 18); n = (R3 / 2, 0.5); pb = (pa[0] + t * n[0], pa[1] + t * n[1])
    g.append(line(pa, pb, dash=False)); g.append(label(pb[0] + 1, pb[1] + 1, "t", "start", 2.4))
    # left arm 1.2t
    qa = (B.Li(30), 30); nl = (-R3 / 2, 0.5); qb = (qa[0] + 1.2 * t * nl[0], qa[1] + 1.2 * t * nl[1])
    g.append(line(qa, qb, dash=False)); g.append(label(qb[0] - 1, qb[1] + 2.4, "1.2t", "end", 2.4))
    # 60 deg
    g.append(label(B.Ro(30) + 3.5, 31, "60°", "start", 2.4))
    # fillet circles
    def fillet_circle(P, A, Bp, r):
        u1 = ((A[0] - P[0]), (A[1] - P[1])); l1 = math.hypot(*u1); u1 = (u1[0] / l1, u1[1] / l1)
        u2 = ((Bp[0] - P[0]), (Bp[1] - P[1])); l2 = math.hypot(*u2); u2 = (u2[0] / l2, u2[1] / l2)
        bis = (u1[0] + u2[0], u1[1] + u2[1]); lb = math.hypot(*bis); bis = (bis[0] / lb, bis[1] / lb)
        ang = math.acos(u1[0] * u2[0] + u1[1] * u2[1])
        dc = r / math.sin(ang / 2)
        c = (P[0] + bis[0] * dc, P[1] + bis[1] * dc)
        return f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(r)}" fill="none" stroke="{ACC}" stroke-width=".16" stroke-dasharray=".6 .5"/>', c
    T, V = B.T_PTS, B.V_PTS
    for i, lab in ((0, "r 0.4t"), (2, "r 0.4t"), (5, "r 0.8t")):
        s, c = fillet_circle(T[i], T[i - 1], T[(i + 1) % len(T)], B.T_RAD[i]); g.append(s)
    s, c = fillet_circle(V[2], V[1], V[3], B.V_RAD[2]); g.append(s)
    g.append(label(3.2, -1.6, "r 0.4t", "middle", 1.9))
    g.append(label(B.BAR_R + 2, 13.6, "r 0.4t", "middle", 1.9))
    g.append(label(9.5, 24, "r 0.8t", "end", 1.9))
    g.append(label(B.apex[0], B.MARK_BOTTOM + 3.6, "r 0.8t", "middle", 1.9))
    # cap circle, tangent to the left arm's inner edge
    cc = B.cap_c
    g.append(f'<circle cx="{f(cc[0])}" cy="{f(cc[1])}" r="5" fill="none" stroke="{ACC}" stroke-width=".18"/>')
    g.append(f'<circle cx="{f(cc[0])}" cy="{f(cc[1])}" r=".45" fill="{ACC}"/>')
    g.append(line((B.Li(40), 40), (B.Li(46), 46)))
    g.append(label(cc[0] + 6.5, cc[1] + 7.5, "cap r 0.5t", "start", 1.9))
    g.append(label(cc[0] + 6.5, cc[1] + 10, "tangent to left arm", "start", 1.6))
    # notch
    g.append(f'<rect x="{f(B.STEP - 3)}" y="0" width="3" height="3" fill="none" stroke="{ACC}" stroke-width=".18"/>')
    g.append(label(B.STEP + 1.4, 6.8, "notch 3u", "start", 1.9))
    # pixel sizes
    for x, y, s_ in B.SQUARES:
        g.append(f'<rect x="{x}" y="{y}" width="{s_}" height="{s_}" fill="none" stroke="{ACC}" stroke-width=".14"/>')
        g.append(label(x + s_ + 0.5, y + s_ / 2 + 0.7, f"{s_}u", "start", 1.6))
    # scale note
    g.append(label(x0 + 1.5, y1 - 1.5, "1 square = 1u  ·  t = 10u", "start", 1.9, "#5B6B80"))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {W} {H}" width="100%">'
            f'<defs>{defs}</defs>{"".join(g)}</svg>')


def inline(path):
    s = (OUT / path).read_text()
    return s.replace('<svg ', '<svg style="display:block;width:100%;height:auto" ', 1)


def clearspace(path, _unused=None, bg="#fff"):
    """Logo inside its clear space of 2t on every side (padding % is relative to the box width)."""
    import re
    s = inline(path)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
    pad_frac = 100 * 2 * t / (vb[2] + 4 * t)
    return (f'<div class="cs" style="padding:{pad_frac}%;background:{bg}"><div class="cs-in">{s}</div></div>')


COLORS = [
    ("Navy", B.C["navy"], "Wordmark, tagline, one-colour logo"),
    ("Teal", B.C["teal"], "The Q"),
    ("T gradient", f'{B.C["t0"]} → {B.C["t1"]}', "Crossbar and stem", (B.C["t0"], B.C["t1"])),
    ("V gradient", f'{B.C["v0"]} → {B.C["v1"]}', "Left arm and point", (B.C["v0"], B.C["v1"])),
    ("Arm gradient", f'{B.C["r0"]} → {B.C["r1"]}', "Right arm over the fold", (B.C["r0"], B.C["r1"])),
    ("Pixel gradient", f'{B.C["s0"]} → {B.C["s1"]}', "The six data pixels", (B.C["s0"], B.C["s1"])),
]


def swatches():
    out = []
    for item in COLORS:
        name, code, use = item[:3]
        bg = f"linear-gradient(90deg,{item[3][0]},{item[3][1]})" if len(item) > 3 else code
        out.append(f'<div class="sw"><div class="chip" style="background:{bg}"></div>'
                   f'<div><b>{name}</b><code>{code}</code><span>{use}</span></div></div>')
    return "".join(out)


html = f"""<!doctype html><html><head><meta charset="utf-8"><title>TIVONIQ logo guidelines</title><style>
@font-face {{ font-family: Inter; src: url(../fonts/Inter.ttf); font-weight: 100 900; }}
@page {{ size: 1600px 2680px; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: 1600px; font-family: Inter, sans-serif; color: #0B2447; background: #fff; padding: 72px 80px; }}
h1 {{ font-size: 40px; font-weight: 700; letter-spacing: -.01em; }}
h2 {{ font-size: 15px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: #5B6B80; margin: 0 0 18px; }}
p, li {{ font-size: 16px; line-height: 1.55; color: #33465E; }}
.lead {{ margin-top: 8px; font-size: 18px; color: #5B6B80; }}
section {{ margin-top: 56px; }}
.row {{ display: grid; gap: 40px; }}
.c2 {{ grid-template-columns: 1.55fr 1fr; }}
.c3 {{ grid-template-columns: repeat(3, 1fr); }}
.card {{ border: 1px solid #E3E9F1; border-radius: 14px; padding: 28px; }}
ul {{ padding-left: 18px; }} li {{ margin: 4px 0; }} li b {{ color: #0B2447; }}
.cs {{ position: relative; outline: 1.5px dashed {ACC}; outline-offset: -1px; }}
.cs-in {{ outline: 1px solid #E3E9F1; }}
.dark {{ background: #0B2447; }}
.tile {{ border-radius: 14px; padding: 44px; display: grid; place-items: center; min-height: 260px; }}
.tile > * {{ width: 100%; }}
.sw {{ display: flex; gap: 16px; align-items: center; }}
.sw .chip {{ width: 64px; height: 64px; border-radius: 12px; flex: none; }}
.sw b {{ display: block; font-size: 16px; }} .sw code {{ display: block; font: 500 14px/1.4 ui-monospace, monospace; color: #0B2447; }}
.sw span {{ font-size: 13px; color: #5B6B80; }}
.grid6 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px 32px; }}
.cap {{ font-size: 13px; color: #5B6B80; margin-top: 12px; }}
.min {{ display: flex; align-items: end; gap: 48px; }}
</style></head><body>
<h1>TIVONIQ logo</h1>
<p class="lead">Construction, proportions and use. Every dimension comes from the stroke <b>t</b>; the grid unit u is t/10.</p>

<section class="row c2">
  <div class="card">{construction_svg()}</div>
  <div>
    <h2>Construction</h2>
    <ul>
      <li><b>Stroke t</b> — crossbar height, stem width and the right arm's perpendicular width.</li>
      <li><b>Left arm 1.2t</b> — it carries the T's stem, so it is drawn heavier.</li>
      <li><b>All diagonals 60°</b> — both crossbar ends, both arms of the V, the stem's bend.</li>
      <li><b>Two radii, 1:2</b> — 0.4t on the crossbar's obtuse corners, 0.8t on the stem bend and the V point. Acute corners stay sharp.</li>
      <li><b>Fold</b> — the right arm ends in a round cap of radius t/2, centred level with the inner vertex; the cap lands exactly tangent to the left arm.</li>
      <li><b>Data pixels</b> — six true squares on the 1u grid, sizes 2u, 3u and 4u (2:3:4). The notch in the right arm is one 3u pixel.</li>
      <li><b>Mark</b> — 68u × 62u (aspect 1.097 : 1).</li>
    </ul>
    <h2 style="margin-top:36px">Wordmark</h2>
    <ul>
      <li>Drawn letters, one stroke weight (0.18 of the cap height).</li>
      <li>O and Q are rounded rectangles, outer radius 0.43 of the cap height.</li>
      <li>The Q's tail runs at 45°, with a knock-out on its left side.</li>
      <li>Q in teal, the rest in navy.</li>
    </ul>
  </div>
</section>

<section>
  <h2>Lockups and clear space</h2>
  <div class="row c3">
    <div>{clearspace("tivoniq-stacked-color.svg", 9)}<p class="cap">Stacked (primary). Wordmark cap height 1.4t, 0.75t below the mark, mark centred. Clear space: 2t on every side (dashed).</p></div>
    <div>{clearspace("tivoniq-stacked-tagline-color.svg", 9)}<p class="cap">With tagline. Tagline set in Inter Regular, 1t below the wordmark and exactly as wide as it.</p></div>
    <div style="display:grid;gap:24px;align-content:start">{clearspace("tivoniq-horizontal-color.svg", 6)}<p class="cap">Horizontal. Wordmark cap height 2t, 1.5t from the mark, centred on the T–V body (the pixels rise above).</p>
      <div style="width:42%">{clearspace("tivoniq-mark-color.svg", 15)}</div><p class="cap">Mark alone: app icons, favicons, avatars.</p></div>
  </div>
</section>

<section>
  <h2>Colour</h2>
  <div class="grid6">{swatches()}</div>
</section>

<section>
  <h2>Versions</h2>
  <div class="row c3">
    <div class="tile" style="background:#fff;border:1px solid #E3E9F1">{inline("tivoniq-stacked-color.svg")}</div>
    <div class="tile dark">{inline("tivoniq-stacked-white.svg")}</div>
    <div class="tile" style="background:#F2F5F9">{inline("tivoniq-stacked-navy.svg")}</div>
  </div>
  <p class="cap">Full colour on white or light backgrounds. White on navy, photos or any dark colour. One-colour navy (or black) for print, stamps, engraving and embroidery; the one-colour mark keeps 0.08t gaps between the T, the V and the fold.</p>
</section>

<section class="row c2">
  <div>
    <h2>Minimum size</h2>
    <div class="min">
      <div style="width:28px">{inline("tivoniq-mark-color.svg")}</div>
      <div style="width:110px">{inline("tivoniq-stacked-color.svg")}</div>
      <div style="width:180px">{inline("tivoniq-stacked-tagline-color.svg")}</div>
      <div style="width:150px">{inline("tivoniq-horizontal-color.svg")}</div>
    </div>
    <p class="cap">Mark 24 px / 6 mm wide · Stacked 96 px / 20 mm · With tagline 160 px / 35 mm · Horizontal 140 px / 30 mm. Below these, drop the tagline first, then use the mark alone.</p>
  </div>
  <div>
    <h2>Don't</h2>
    <ul>
      <li>Stretch, skew or rotate the logo; scale it only proportionally.</li>
      <li>Redraw, re-space or retype the wordmark.</li>
      <li>Recolour parts, or put the colour logo on a busy or mid-tone background (use white).</li>
      <li>Add shadows, outlines or glows.</li>
      <li>Crowd it inside the clear space.</li>
    </ul>
  </div>
</section>
</body></html>"""

page = GD / "TIVONIQ-logo-guidelines.html"
page.write_text(html)
common = ["chromium", "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-pdf-header-footer",
          "--allow-file-access-from-files"]
subprocess.run(common + [f"--print-to-pdf={GD / 'TIVONIQ-logo-guidelines.pdf'}", page.as_uri()],
               check=True, capture_output=True)
subprocess.run(common + ["--window-size=1600,2680", f"--screenshot={GD / 'TIVONIQ-logo-guidelines.png'}", page.as_uri()],
               check=True, capture_output=True)
print("ok")
