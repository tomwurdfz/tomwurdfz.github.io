"""Generate schematic research figures (SVG) for the website.

Usage: python -I make_figs.py <output_dir>
"""
import math
import random
import sys

OUT = sys.argv[1]
AMBER = "#f2a93b"
PALE = "#ffd38a"


def f(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


def defs(uid, w, h):
    return f"""<defs>
  <linearGradient id="sky{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0d1631"/><stop offset="1" stop-color="#17285a"/>
  </linearGradient>
  <radialGradient id="glow{uid}">
    <stop offset="0" stop-color="{AMBER}" stop-opacity=".55"/>
    <stop offset=".45" stop-color="{AMBER}" stop-opacity=".16"/>
    <stop offset="1" stop-color="{AMBER}" stop-opacity="0"/>
  </radialGradient>
  <clipPath id="clip{uid}"><rect width="{w}" height="{h}" rx="12"/></clipPath>
</defs>"""


def background(uid, w, h, n_stars, seed):
    rng = random.Random(seed)
    s = [f'<rect width="{w}" height="{h}" rx="12" fill="url(#sky{uid})"/>']
    for _ in range(n_stars):
        s.append(
            f'<circle cx="{f(rng.uniform(4, w - 4))}" cy="{f(rng.uniform(4, h - 4))}" '
            f'r="{f(rng.uniform(.3, .8))}" fill="#fff" opacity="{f(rng.uniform(.25, .7))}"/>'
        )
    return "\n".join(s)


def bh(uid, x, y, r, glow=2.6, ring=True, cls=""):
    c = f' class="{cls}"' if cls else ""
    parts = [f"<g{c}>"]
    if glow:
        parts.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * glow)}" fill="url(#glow{uid})"/>')
    stroke = f' stroke="{PALE}" stroke-width="{f(max(.6, r * .14))}"' if ring else ""
    parts.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#02040a"{stroke}/>')
    parts.append("</g>")
    return "".join(parts)


REDUCED = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"


def svg(w, h, label, body, style=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">
<title>{label}</title>
<style>{style}
{REDUCED}</style>
{body}
</svg>
"""


# ---------------------------------------------------------------- cluster
def cluster():
    uid, W, H = "c", 320, 240
    rng = random.Random(7)
    cx, cy, a = 160, 120, 40
    stars = []
    while len(stars) < 760:
        u = rng.random() * 0.985
        R = a * math.sqrt(u / (1 - u))  # projected Plummer: M(<R) = R^2/(R^2+a^2)
        th = rng.uniform(0, 2 * math.pi)
        x, y = cx + R * math.cos(th), cy + R * math.sin(th) * 0.92
        if 3 < x < W - 3 and 3 < y < H - 3:
            col = rng.choices(["#ffffff", "#ffe2ad", "#cddcff", "#ffc48a"], [5, 3, 3, 1])[0]
            r = rng.choice([.45, .55, .65, .8, 1.0, 1.25]) * (1.1 if R < a else 1)
            stars.append(
                f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{col}" opacity="{f(rng.uniform(.45, 1))}"/>'
            )
    # stellar-mass BHs, mass-segregated toward the centre
    small = []
    for (R, th) in [(24, .4), (36, 2.2), (46, 3.6), (20, 4.6), (56, 5.5), (40, 1.2), (30, 3.0)]:
        small.append(bh(uid, cx + R * math.cos(th), cy + R * math.sin(th) * .92, 2.6, glow=2.4))
    # one dashed orbit of a BH around the central massive BH
    orbit = (f'<ellipse cx="{cx}" cy="{cy}" rx="64" ry="24" fill="none" stroke="{AMBER}" '
             f'stroke-opacity=".45" stroke-width=".8" stroke-dasharray="2 3" transform="rotate(-22 {cx} {cy})"/>')
    halo = (f'<circle cx="{cx}" cy="{cy}" r="105" fill="url(#glow{uid})" opacity=".4"/>')
    body = f"""{defs(uid, W, H)}
<g clip-path="url(#clip{uid})">
{background(uid, W, H, 40, 11)}
{halo}
{''.join(stars)}
{orbit}
{''.join(small)}
<g class="orbiter">{bh(uid, cx + 64, cy, 2.8, glow=2.4)}</g>
{bh(uid, cx, cy, 11, glow=3.2)}
</g>"""
    style = f""".orbiter {{ transform-box: view-box; transform-origin: {cx}px {cy}px;
  animation: none; }}"""
    # keep the orbiter on its (rotated, flattened) ellipse with a Kepler-ish loop
    frames = []
    n = 48
    for i in range(n + 1):
        t = i / n
        ang = 2 * math.pi * t
        x0, y0 = 64 * math.cos(ang), 24 * math.sin(ang)
        rot = math.radians(-22)
        x = x0 * math.cos(rot) - y0 * math.sin(rot)
        y = x0 * math.sin(rot) + y0 * math.cos(rot)
        frames.append(f"{f(t * 100)}% {{ transform: translate({f(x - 64)}px, {f(y)}px); }}")
    style = (f""".orbiter {{ animation: orbit 9s linear infinite; transform: translate({f(64*math.cos(math.radians(-22))-64)}px, {f(64*math.sin(math.radians(-22)))}px); }}
@keyframes orbit {{ {' '.join(frames)} }}""")
    return svg(W, H, "Schematic of a dense star cluster hosting a central massive black hole", body, style)


# ---------------------------------------------------------------- binary BH
def binary():
    uid, W, H = "b", 120, 120
    c = 60
    arms = []
    for k in (0, math.pi):
        pts = []
        th = 0
        while th < 4.2 * math.pi:
            r = 16 + 6.2 * th
            ang = -th + k
            pts.append(f"{f(c + r * math.cos(ang))},{f(c + r * math.sin(ang))}")
            th += 0.08
        arms.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="url(#fade{uid})" stroke-width="1.6" stroke-linecap="round"/>')
    fade = f"""<radialGradient id="fade{uid}" gradientUnits="userSpaceOnUse" cx="{c}" cy="{c}" r="62">
  <stop offset=".2" stop-color="{AMBER}" stop-opacity=".75"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/>
</radialGradient>"""
    body = f"""{defs(uid, W, H).replace('</defs>', fade + '</defs>')}
<g clip-path="url(#clip{uid})">
{background(uid, W, H, 14, 3)}
<g class="spin">
{''.join(arms)}
<circle cx="{c}" cy="{c}" r="13.5" fill="none" stroke="#fff" stroke-opacity=".18" stroke-width=".6" stroke-dasharray="1.5 2"/>
{bh(uid, c - 12, c, 6.2)}
{bh(uid, c + 14, c, 5.2)}
</g>
</g>"""
    style = f""".spin {{ transform-box: view-box; transform-origin: {c}px {c}px; animation: spin 3.2s linear infinite; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}"""
    return svg(W, H, "Two black holes orbiting each other and emitting gravitational waves", body, style)


# ---------------------------------------------------------------- IMBH-BH plunge
def plunge():
    uid, W, H = "p", 120, 120
    bx, by, R = 30, 64, 10
    a, e = 44, 0.8
    b = a * math.sqrt(1 - e * e)
    # dashed eccentric orbit, large BH at the (left) focus
    ell = (f'<ellipse cx="{f(bx + a * e)}" cy="{by}" rx="{a}" ry="{f(b)}" fill="none" stroke="#fff" '
           f'stroke-opacity=".28" stroke-width=".7" stroke-dasharray="1.6 2.4"/>')
    # Kepler motion from apocentre (E = pi) to pericentre (E = 2 pi): uniform in mean anomaly
    frames = []
    n = 44
    end_pct = 80
    for i in range(n + 1):
        M = math.pi + math.pi * i / n
        E = M
        for _ in range(30):
            E -= (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
        x = bx - a * (math.cos(E) - e)
        y = by + b * math.sin(E)
        pct = end_pct * i / n
        op = 1 if math.hypot(x - bx, y - by) > R + 1 else 0
        frames.append(f"{f(pct)}% {{ transform: translate({f(x)}px, {f(y)}px); opacity: {op}; }}")
    frames.append(f"100% {{ transform: translate({bx}px, {by}px); opacity: 0; }}")
    body = f"""{defs(uid, W, H)}
<g clip-path="url(#clip{uid})">
{background(uid, W, H, 14, 5)}
<g transform="rotate(-12 60 60)">
{ell}
<circle class="burst" cx="{bx}" cy="{by}" r="{R}" fill="none" stroke="{AMBER}" stroke-width="1.4" vector-effect="non-scaling-stroke"/>
{bh(uid, bx, by, R, glow=2.8)}
<g class="mover">{bh(uid, 0, 0, 3.2, glow=2.4)}</g>
</g>
</g>"""
    style = f""".mover {{ animation: plunge 4.2s linear infinite; transform: translate({f(bx + a * e)}px, {f(by - b)}px); }}
@keyframes plunge {{ {' '.join(frames)} }}
.burst {{ transform-box: fill-box; transform-origin: center; opacity: 0; animation: burst 4.2s ease-out infinite; }}
@keyframes burst {{ 0%, {end_pct - 1}% {{ transform: scale(1); opacity: 0; }} {end_pct + 1}% {{ opacity: .9; }} 100% {{ transform: scale(4.2); opacity: 0; }} }}"""
    return svg(W, H, "A small black hole on a highly eccentric orbit plunging into an intermediate-mass black hole", body, style)


# ---------------------------------------------------------------- EMRI
def emri():
    uid, W, H = "e", 120, 120
    c, R = 60, 12
    r0, r1, incl = 44, 20, .5   # start/end orbital radius; vertical squash for an inclined view
    # Time-uniform samples of a slow, near-circular inspiral: r shrinks steadily while the
    # orbital angular frequency follows Kepler (omega ~ r^-3/2), so the orbit speeds up.
    n = 260
    om0 = 2 * math.pi / 62   # rad per sample at r0
    th, samples = 0.0, []
    for i in range(n + 1):
        r = r0 - (r0 - r1) * (i / n) ** 1.6
        samples.append((c + r * math.cos(th), c + r * math.sin(th) * incl, r))
        th += om0 * (r0 / r) ** 1.5
    trail = " ".join(f"{f(x)},{f(y)}" for x, y, _ in samples)
    spiral = (f'<polyline points="{trail}" fill="none" stroke="{AMBER}" stroke-opacity=".28" '
              f'stroke-width=".7" stroke-linejoin="round"/>')
    frames = []
    for i, (x, y, _) in enumerate(samples):
        pct = 100 * i / n
        op = 0 if i == 0 or i == n else 1
        frames.append(f"{f(pct)}% {{ transform: translate({f(x)}px, {f(y)}px); opacity: {op}; }}")
    sx, sy, _ = samples[n // 3]
    # orbiter is drawn in front of the big BH only on the near (lower) half of the orbit;
    # keep it simple and always draw it in front.
    body = f"""{defs(uid, W, H)}
<g clip-path="url(#clip{uid})">
{background(uid, W, H, 14, 9)}
{spiral}
{bh(uid, c, c, R, glow=2.8)}
<g class="mover">{bh(uid, 0, 0, 2.8, glow=2.4)}</g>
</g>"""
    style = f""".mover {{ animation: emri 11s linear infinite; transform: translate({f(sx)}px, {f(sy)}px); }}
@keyframes emri {{ {' '.join(frames)} }}"""
    return svg(W, H, "A small black hole slowly inspiraling on a near-circular orbit around a much more massive black hole", body, style)


for name, fn in [("fig-cluster", cluster), ("fig-bbh", binary), ("fig-plunge", plunge), ("fig-emri", emri)]:
    with open(f"{OUT}/{name}.svg", "w", newline="\n", encoding="utf-8") as fh:
        fh.write(fn())
    print(name, "ok")
