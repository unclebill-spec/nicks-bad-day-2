"""v0.16 ROOFTOP HELIPAD AT NIGHT sprites: a deep night sky over a neon city skyline and a concrete parapet, a dark gravel
roof, HVAC units / vent stacks / a windsock / a radio mast, neon (blue / violet / red), an equipment-case prop, projectiles
(vape cloud, toy drone), the parody LIFE FLITE helicopter and a stretcher. Side view, facing right. Parody brands only."""
from __future__ import annotations

import random

from rig import INK, Raster
import tinyfont
from v11_art import box, neon, paint_sign

SKY = ("#0a0a24", "#14103a", "#22145a", "#341a6a")   # top -> horizon (violet glow over the city)
CONC, CONC_D, CONC_L = "#4a4a5e", "#36364a", "#62627a"
NEON = ("#3aa8ff", "#a24dff", "#ff3a4a")


def _sky(S, h, seed):
    bands = len(SKY)
    for y in range(h):
        S.rect(0, y, S.w, 1, SKY[min(bands - 1, y * bands // h)])
    r = random.Random(seed)
    for _ in range(5):
        x, y = r.randrange(0, S.w), r.randrange(0, max(1, h - 20))
        S.set(x, y, r.choice(("#ffffff", "#bfe0ff", "#d8c8ff")))


def rwall_tile(seed):
    """32x104: night sky with stars, a skyline slice (lit windows in neon colours), a concrete parapet with a coping."""
    S = Raster(32, 104)
    _sky(S, 84, 300 + seed)
    r = random.Random(40 + seed)
    # far skyline (dim violet), then near buildings (near-black with lit windows)
    x = -r.randrange(0, 8)
    while x < 32:
        w = r.randrange(7, 13); top = r.randrange(40, 62)
        S.rect(x, top, w, 84 - top, "#1c1638")
        x += w + 1
    x = -r.randrange(0, 6)
    while x < 32:
        w = r.randrange(8, 15); top = r.randrange(52, 74)
        S.rect(x, top, w, 84 - top, "#0e0c1c"); S.rect(x, top, w, 1, "#2a2448")
        for wy in range(top + 3, 82, 4):
            for wx in range(x + 2, x + w - 1, 3):
                if r.random() < 0.35:
                    S.set(wx, wy, r.choice(("#3aa8ff", "#a24dff", "#ff3a4a", "#ffe8a8", "#ffe8a8")))
        if seed == 2 and top < 60:
            S.rect(x + w // 2, top - 6, 1, 6, "#2a2448"); S.set(x + w // 2, top - 7, "#ff3a4a")  # a rooftop aviation light
        x += w
    # the parapet: concrete coping, block wall, drip line
    S.rect(0, 84, 32, 3, CONC_L); S.rect(0, 84, 32, 1, "#8a8aa4"); S.rect(0, 87, 32, 1, INK)
    S.rect(0, 88, 32, 16, CONC); S.rect(0, 95, 32, 1, CONC_D); S.rect(15 if seed % 2 else 7, 88, 1, 7, CONC_D); S.rect(23, 96, 1, 8, CONC_D)
    S.rect(0, 102, 32, 2, "#22222e")
    return S


def rceil_tile(lit=False):
    """32x14: open sky (the very top of the frame). lit = a brighter star with a twinkle."""
    S = Raster(32, 14)
    S.rect(0, 0, 32, 14, SKY[0])
    S.set(6, 4, "#bfe0ff"); S.set(25, 9, "#d8c8ff")
    if lit:
        S.set(16, 6, "#ffffff"); S.set(15, 6, "#8ab8ff"); S.set(17, 6, "#8ab8ff"); S.set(16, 5, "#8ab8ff"); S.set(16, 7, "#8ab8ff")
    return S


def rfloor_tiles():
    """Dark roof concrete with gravel specks and a seam."""
    out = []
    for i in range(2):
        S = Raster(24, 12)
        S.rect(0, 0, 24, 12, "#2c2c3c" if i == 0 else "#30303f")
        r = random.Random(70 + i)
        for _ in range(10):
            S.set(r.randrange(24), r.randrange(12), r.choice(("#44445a", "#24242e", "#3a3a4c")))
        S.rect(0, 11, 24, 1, "#20202a"); S.rect(23 if i else 11, 0, 1, 12, "#24242f")
        out.append(S)
    return out


def hvac():
    """64x42 rooftop HVAC unit: a steel box with a fan grille on top, louvres, a warning sticker. Sits on the floor line."""
    S = Raster(64, 42)
    box(S, 2, 10, 60, 30, "#6a7086", "#4a5064", "#8a90a8")
    for y in range(16, 36, 3):
        S.rect(6, y, 26, 1, "#3e4458")
    box(S, 38, 14, 20, 20, "#3e4458", None, "#5a6078")
    S.ellipse((48, 24), 8, 8, "#24283a", "#1a1e2c")
    for a in range(4):
        S.line((48, 24), (48 + (6, 0, -6, 0)[a], 24 + (0, 6, 0, -6)[a]), "#8a90a8")
    S.rect(10, 4, 44, 6, "#4a5064"); S.rect(10, 4, 44, 1, "#8a90a8")
    box(S, 8, 30, 10, 6, "#ffd84a", None, None); S.rect(12, 31, 2, 3, INK)
    S.rect(4, 40, 4, 2, "#24242e"); S.rect(56, 40, 4, 2, "#24242e")
    return S


def vent():
    """18x38 vent stack with a rain cap (mushroom vent)."""
    S = Raster(18, 38)
    box(S, 5, 10, 8, 26, "#7a8098", "#5a6078", "#a0a6bc")
    S.poly([(1, 10), (17, 10), (13, 4), (5, 4)], "#8a90a8"); S.rect(1, 10, 16, 1, "#4a5064")
    S.rect(6, 36, 6, 2, "#24242e")
    return S


def windsock():
    """40x70 windsock on a pole: striped red/white sock streaming right, a red light on top."""
    S = Raster(40, 70)
    S.rect(6, 6, 2, 64, "#a0a6bc"); S.rect(7, 6, 1, 64, "#6a7086")
    S.ellipse((7, 5), 2, 2, "#ff3a4a", None, rim=True)
    pts = [(8, 10), (8, 22), (38, 19), (38, 15)]
    S.poly(pts, "#ff6a3a")
    for k, x in enumerate(range(14, 38, 6)):
        if k % 2:
            S.poly([(x, 10 + (x - 8) * 4 // 30 // 1), (x, 22 - (x - 8) * 3 // 30), (x + 6, 21 - (x - 2) * 3 // 30), (x + 6, 11 + (x - 2) * 4 // 30)], "#f4f4f8", rim=False)
    S.rect(5, 9, 4, 2, INK)
    return S


def mast():
    """14x84 radio mast (lattice) with a red aviation light on top."""
    S = Raster(14, 84)
    S.line((3, 82), (6, 6), "#6a7086"); S.line((10, 82), (7, 6), "#6a7086")
    for y in range(12, 82, 8):
        S.line((3 + (82 - y) * 3 // 76, y), (10 - (82 - y) * 3 // 76, y + 8), "#4a5064")
    S.ellipse((7, 4), 2.5, 2.5, "#ff3a4a", None, rim=True); S.set(7, 3, "#ffd0d0")
    return S


def flightcase(state=0):
    """A rolling flight-equipment case (orange, with a cross). Breakable, 3 states. 30x26."""
    S = Raster(30, 26)
    box(S, 2, 4, 26, 18, "#e8722a", "#b0501c", "#ff9a4a")
    S.rect(13, 8, 4, 10, "#ffffff"); S.rect(10, 11, 10, 4, "#ffffff")
    S.rect(2, 12, 26, 1, "#8a3a14"); S.rect(11, 2, 8, 2, INK)
    if state >= 1:
        S.line((5, 6), (12, 14), INK); S.line((22, 18), (26, 10), INK)
    if state == 2:
        S.rect(4, 4, 22, 3, "#2a2a34")  # lid sprung
    for x in (6, 24):
        S.ellipse((x, 23), 2.5, 2.5, "#2a2a34", None, rim=True)
    return S


def proj_vape(k=0):
    """A big puffy vape cloud (faintly violet). 20x14, two frames."""
    S = Raster(20, 14)
    for (x, y, r) in ((6, 8, 5), (11, 6, 6 - k), (15, 8, 4 + k)):
        S.ellipse((x, y), r, r * 0.8, "#d8d0f0", "#a89ac8", rim=False)
    S.set(9, 4, "#ffffff"); S.set(13, 5, "#ffffff")
    return S


def proj_drone(k=0):
    """A little quad-copter toy drone with a blinking light. 20x10, two frames (rotor blur)."""
    S = Raster(20, 10)
    box(S, 6, 4, 8, 4, "#3a3a4a", None, "#5a5a6e")
    S.line((2, 3), (18, 3), "#6a6a7e")
    for x in (2, 17):
        S.rect(x - 2 + k, 1, 4 - k * 2 + 1, 1, "#c8ccd8")
    S.set(10, 5, "#ff3a4a" if k else "#3aa8ff")
    return S


def chopper(k=0, pilot="awake"):
    """150x66 the parody LIFE FLITE air-ambulance helicopter, side view facing right: a white + blue fuselage with a red
    stripe, a bubble canopy with Captain ACE (aviator shades), skids, a tail boom with a tail rotor. k = rotor frame (0-1).
    pilot: 'awake' | 'sleep' (head tipped, the off-shift nap)."""
    S = Raster(150, 66)
    # main rotor (blur): a long thin bar, two frames
    if k == 0:
        S.rect(10, 4, 130, 2, "#c8ccd8"); S.rect(10, 4, 130, 1, "#ffffff")
    else:
        S.rect(30, 4, 90, 2, "#a0a6bc"); S.rect(60, 3, 30, 4, "#c8ccd8")
    S.rect(84, 6, 6, 8, "#4a5064")
    # tail boom + fin + tail rotor
    S.poly([(4, 22), (60, 26), (60, 34), (6, 30)], "#e8ecf4")
    S.rect(6, 26, 54, 2, "#ff3a4a")
    S.poly([(2, 10), (12, 10), (14, 30), (4, 30)], "#2a5ad8")
    S.ellipse((6, 18), 6 - k * 3, 6, "#c8ccd8" if k else "#a0a6bc", None, rim=False)
    # fuselage
    S.ellipse((92, 32), 40, 18, "#f4f6fc", "#c8ccdc")
    S.rect(54, 34, 78, 5, "#2a5ad8"); S.rect(54, 39, 74, 2, "#ff3a4a")
    # canopy + pilot
    S.ellipse((118, 26), 16, 12, "#1a2a5a", "#0e1838")
    S.line((106, 20), (126, 34), "#5a7ad8")
    hx, hy = (116, 26) if pilot == "awake" else (114, 29)
    S.ellipse((hx, hy), 5, 5, "#e8b088", "#b8805a")
    S.rect(hx - 5, hy - 6, 10, 3, "#ffffff"); S.rect(hx - 5, hy - 4, 10, 1, "#3a5ad8")  # flight helmet
    if pilot == "awake":
        S.rect(hx - 1, hy - 1, 7, 2, INK); S.set(hx + 5, hy - 1, "#8ad8ff")   # aviator shades
        S.rect(hx, hy + 2, 4, 1, "#7a3a2a")   # a smirk
    else:
        S.line((hx, hy), (hx + 4, hy), INK)
    # door with the parody logo
    tw = tinyfont.width("FLITE")
    box(S, 66, 19, tw + 6, 14, "#ffffff", "#c8ccdc", None)
    tinyfont.text(S, 69 + (tw - tinyfont.width("LIFE")) // 2, 21, "LIFE", "#ff3a4a"); tinyfont.text(S, 69, 27, "FLITE", "#2a5ad8")
    # landing light (glows in game) + skids
    S.ellipse((128, 42), 2.5, 2, "#fff4c8", None, rim=True)
    S.rect(70, 50, 4, 8, "#6a7086"); S.rect(110, 50, 4, 8, "#6a7086")
    S.rect(56, 58, 76, 3, "#8a90a8"); S.rect(56, 58, 76, 1, "#c8ccd8"); S.poly([(132, 58), (138, 54), (138, 56), (132, 61)], "#8a90a8")
    return S


def stretcher():
    """56x22 a flight stretcher (wheeled cot) with a pillow and a blanket folded at the foot."""
    S = Raster(56, 22)
    box(S, 2, 8, 52, 4, "#e8ecf4", "#a8b0c4", "#ffffff")
    box(S, 4, 4, 12, 4, "#ffffff", "#c8ccdc", None)
    box(S, 40, 5, 12, 3, "#3a5ad8", None, "#5a7ad8")
    for x in (8, 46):
        S.line((x, 12), (x + 4, 18), "#8a90a8"); S.line((x + 4, 12), (x, 18), "#8a90a8")
        S.ellipse((x + 2, 19), 2, 2, "#2a2a34", None, rim=True)
    return S


def proj_spark(k=0):
    """The defib CLEAR! arc: a crackling blue-white bolt. 22x12, two frames."""
    S = Raster(22, 12)
    pts = [(0, 6), (5, 2 + k * 6), (10, 9 - k * 5), (15, 3 + k * 4), (21, 6)]
    for a, b in zip(pts, pts[1:]):
        S.line(a, b, "#8ad8ff"); S.line((a[0], a[1] + 1), (b[0], b[1] + 1), "#3a7aff")
    S.ellipse((21, 6), 1.5, 1.5, "#ffffff", None, rim=False)
    return S


def landing_light(c):
    """6x4 a flush pad light (the dome), lit."""
    S = Raster(6, 4)
    S.ellipse((3, 2), 2.5, 1.6, c, None, rim=True); S.set(2, 1, "#ffffff")
    return S


def bits():
    out = {}
    S = Raster(8, 6); box(S, 1, 1, 6, 4, "#e8722a", None, "#ff9a4a"); out["deb_case"] = S
    S = Raster(6, 4); S.rect(1, 1, 4, 2, "#6a7086"); out["deb_metal"] = S
    for i, c in enumerate(NEON):
        out[f"padlight{i}"] = landing_light(c)
    S = Raster(16, 3); S.rect(0, 1, 16, 1, "#d8e0ff"); S.rect(10, 0, 6, 1, "#ffffff"); out["windline"] = S
    return out


def wall_pieces():
    return {
        "hvac": hvac(), "vent": vent(), "windsock": windsock(), "mast": mast(),
        "neon_helipad": neon("HELIPAD", "#3aa8ff"), "neon_flite": neon("LIFE FLITE", "#ff3a4a"), "neon_roof": neon("ROOF", "#a24dff"),
        "sign_noroof": paint_sign("AUTHORIZED PERSONNEL ONLY", "#c84a4a"), "sign_rotor": paint_sign("STAY CLEAR OF ROTOR", "#d8a020", "#1a1020"),
        "sign_pad": paint_sign("HELIPAD H1", "#3a5ad8"),
    }
