"""v0.5 art: Floor 4 Radiology (dark slate walls, neon-blue X-ray lightboxes, warning lamps), its kickable props
(lead-apron rack, contrast injector cart, rolling film viewer), the MRI magnet boss (front view; v0.7: ~1.45x a nurse's
height), projectiles (barium cup + puddle, X-ray film, MRI knock wave, patient table) and the
night-shift extras (night windows, call-light lamps, vitals monitors). All original, drawn in code.
"""
from __future__ import annotations

import math
import random

from rig import INK, Raster
import tinyfont
import pixel_writer as PW  # vendored Gravewake pixel writer (speckle)
from breakables import box, caster, STEEL, STEEL_S, STEEL_H, TIRE

NEON, NEON_S, NEON_H = "#3aa8ff", "#1a68c8", "#bfeaff"
FILM, BONE = "#1c3a66", "#d8f4ff"


# ------------------------------------------------------------------ tiles
def rwall_tile(seed):
    """32x104 radiology wall: dark slate paint, a neon-blue trim strip under the rail, lead-lined wainscot."""
    S = Raster(32, 104)
    base, dark, light = "#3a4766", "#33405c", "#44547a"
    for ty in range(0, 64, 16):
        for tx in range(0, 32, 16):
            t = PW.soil(seed * 37 + tx + ty + 400, base, dark, light, base, (tx + ty) // 16)
            for yy in range(16):
                for xx in range(16):
                    S.set(tx + xx, ty + yy, t.p[yy][xx])
    S.rect(0, 62, 32, 2, NEON_S); S.rect(0, 63, 32, 1, NEON)            # neon trim
    S.rect(0, 66, 32, 30, "#262f48"); S.rect(0, 66, 32, 1, "#34405e")
    for x in (7, 23):
        S.rect(x, 68, 1, 26, "#20283e")
    S.rect(0, 96, 32, 8, "#141a2a"); S.rect(0, 96, 32, 1, "#2a3450")
    S.rect(0, 56, 32, 3, "#8a94a4"); S.rect(0, 58, 32, 1, "#4a5468"); S.rect(0, 56, 32, 1, "#b8c0cc"); S.rect(14, 59, 3, 3, "#4a5468")
    return S


def rceil_tile(lit):
    S = Raster(32, 14)
    S.rect(0, 0, 32, 14, "#262c40"); S.rect(0, 13, 32, 1, "#161a28"); S.rect(0, 0, 1, 13, "#20263a")
    if lit:
        S.rect(4, 2, 24, 8, "#9ad8ff"); S.rect(4, 2, 24, 1, "#d8f4ff"); S.rect(4, 9, 24, 1, "#5aa8e0")
    return S


def rfloor_tiles():
    out = []
    for i, (b, d, l) in enumerate((("#454d68", "#3c435c", "#4f5874"), ("#3a4058", "#323850", "#444c66"))):
        S = Raster(24, 12)
        for tx in (0, 16):
            t = PW.soil(170 + i * 5 + tx, b, d, l, d, i + tx // 16)
            for yy in range(12):
                for xx in range(16):
                    S.set(tx + xx, yy, t.p[yy][xx])
        S.rect(0, 0, 24, 1, "#262c40"); S.rect(0, 0, 1, 12, "#262c40")
        out.append(S)
    return out


# ------------------------------------------------------------------ wall pieces
def _film(S, x, y, w, h, kind, r):
    S.rect(x, y, w, h, NEON_H)
    S.rect(x + 1, y + 1, w - 2, h - 2, FILM)
    cx = x + w // 2
    if kind == "chest" or kind == "duck":
        S.rect(cx, y + 2, 1, h - 4, BONE)                                # spine
        for k in range(5):
            yy = y + 4 + k * 3
            S.line((cx - 1, yy), (x + 2, yy + 2), BONE); S.line((cx + 1, yy), (x + w - 3, yy + 2), BONE)
        S.line((x + 2, y + 3), (cx - 2, y + 2), BONE); S.line((cx + 2, y + 2), (x + w - 3, y + 3), BONE)  # collarbones
        if kind == "duck":  # somebody swallowed a rubber duck. Again.
            S.ellipse((cx + 2, y + h - 6), 3, 2.2, "#ffe84a", rim=False); S.ellipse((cx + 4, y + h - 9), 1.8, 1.8, "#ffe84a", rim=False)
            S.set(cx + 6, y + h - 9, "#ff9a3a"); S.set(cx + 4, y + h - 10, INK)
    elif kind == "hand":
        S.rect(cx - 3, y + h - 7, 7, 5, BONE)
        for k, (dx, ln) in enumerate(((-4, 6), (-2, 8), (0, 9), (2, 8), (5, 5))):
            S.rect(cx + dx, y + h - 7 - ln, 1, ln, BONE)
            S.set(cx + dx, y + h - 7 - ln // 2, FILM)
    elif kind == "skull":
        S.ellipse((cx, y + h // 2 - 1), w / 2 - 3, h / 2 - 3, BONE, rim=False)
        S.ellipse((cx - 3, y + h // 2 - 1), 2, 2, FILM, rim=False); S.ellipse((cx + 3, y + h // 2 - 1), 2, 2, FILM, rim=False)
        S.rect(cx - 3, y + h - 6, 7, 1, FILM); S.set(cx, y + h // 2 + 2, FILM)
    for _ in range(4):
        S.set(x + 1 + r.randint(0, w - 3), y + 1 + r.randint(0, h - 3), "#2c5288")


def lightbox(kinds=("chest", "hand"), seed=1):
    """Wall-mounted X-ray viewer: steel frame, two glowing panes with films clipped on."""
    r = random.Random(seed)
    S = Raster(44, 32)
    box(S, 1, 1, 42, 28, "#8a94a4", "#5c6676", "#c8d0dc")
    for i, k in enumerate(kinds):
        _film(S, 3 + i * 20, 3, 18, 24, k, r)
        S.rect(10 + i * 20, 2, 4, 2, "#ffe84a")                          # film clip
    S.rect(20, 29, 4, 2, "#5c6676"); S.set(21, 30, "#5aff8a")             # switch + pilot light
    return S


def warn_lamp(lit=True):
    """"X-RAY IN USE" warning light box above an exam room door."""
    S = Raster(52, 11)
    box(S, 1, 1, 50, 9, "#e8303c" if lit else "#5a2028", None, None)
    tinyfont.text(S, 4, 3, "X-RAY IN USE", "#ffffff" if lit else "#a8707a")
    return S


def trefoil():
    S = Raster(14, 14)
    S.ellipse((7, 7), 6, 6, "#ffd83a", "#c8a020")
    for a in (90, 210, 330):
        ra = math.radians(a)
        S.poly([(7, 7), (7 + 5 * math.cos(ra - 0.5), 7 - 5 * math.sin(ra - 0.5)), (7 + 5 * math.cos(ra + 0.5), 7 - 5 * math.sin(ra + 0.5))], INK, rim=False)
    S.ellipse((7, 7), 1.6, 1.6, "#ffd83a", rim=False); S.set(7, 7, INK)
    return S


def poster_nometal():
    S = Raster(30, 34)
    box(S, 1, 1, 28, 32, "#ffd83a", "#c8a020")
    S.poly([(15, 4), (26, 22), (4, 22)], INK, rim=False); S.poly([(15, 7), (23, 20), (7, 20)], "#ffd83a", rim=False)
    S.rect(11, 12, 2, 6, "#e8303c"); S.rect(17, 12, 2, 6, "#e8303c"); S.rect(11, 16, 8, 2, "#e8303c")   # horseshoe magnet
    S.rect(11, 12, 2, 1, "#e4e8f0"); S.rect(17, 12, 2, 1, "#e4e8f0")
    tinyfont.text(S, 5, 25, "NO", INK); tinyfont.text(S, 5, 29, "METAL!", INK)
    return S


def night_window(seed=1):
    """Same frame as the day windows, but the night sky: stars, a moon, lit-up windows in the city."""
    S = Raster(64, 40)
    box(S, 1, 1, 62, 38, "#5a6478", "#3a4254")
    S.rect(3, 3, 58, 34, "#0e1430"); S.rect(3, 3, 58, 8, "#141c44")
    r = random.Random(seed)
    for _ in range(9):
        S.set(r.randint(4, 59), r.randint(4, 16), "#d8e4ff")
    if seed % 2:
        S.ellipse((50, 9), 4, 4, "#f4f0d0", rim=False); S.ellipse((52, 8), 3, 3, "#0e1430", rim=False)
    x = 3
    while x < 61:
        w, h = r.randint(5, 10), r.randint(8, 22)
        S.rect(x, 37 - h, min(w, 61 - x), h, r.choice(["#1c2440", "#222a4a", "#181e38"]))
        for yy in range(37 - h + 2, 36, 3):
            for xx in range(x + 1, min(x + w, 61) - 1, 2):
                if r.random() < 0.28:
                    S.set(xx, yy, r.choice(["#ffd86a", "#ffe8a0", "#8ad8ff"]))
        x += w + 1
    S.rect(32, 3, 1, 34, "#5a6478")
    return S


def call_lamp(lit):
    S = Raster(10, 6)
    S.ellipse((5, 4), 4, 3, "#ff4a3a" if lit else "#5a2a2a", "#a82828" if lit else "#3a1a1a")
    S.rect(1, 5, 8, 1, "#5c6676")
    return S


def vitals_monitor():
    S = Raster(20, 16)
    box(S, 1, 1, 18, 12, "#2a2e3a", "#1a1c24", "#4a5060")
    S.rect(3, 3, 14, 8, "#06140c")
    for x, y in ((3, 7), (4, 7), (5, 7), (6, 6), (7, 3), (8, 9), (9, 7), (10, 7), (11, 7), (12, 7), (13, 6), (14, 4), (15, 8), (16, 7)):
        S.set(x, y, "#5aff8a")
    S.rect(13, 3, 3, 1, "#ffd84a"); S.rect(9, 14, 2, 2, "#5c6676")
    return S


# ------------------------------------------------------------------ kickable props
APRONS = (("#3a6ad8", "#2a4aa8", "#6a9aff"), ("#8a4ad8", "#5e2ea8", "#b07aff"), ("#2aa8a0", "#1a7a74", "#5ad8d0"))


def _apron(S, x, y, c, s, h, ln=18):
    S.poly([(x, y), (x + 9, y), (x + 11, y + ln), (x - 2, y + ln)], c)
    S.rect(x + 1, y + 1, 7, 1, h); S.line((x + 9, y + 1), (x + 10, y + ln - 1), s)
    S.rect(x + 3, y + 6, 3, 3, "#ffd83a"); S.set(x + 4, y + 7, INK)    # radiation tag


def apron_rack(state):
    """Lead aprons hanging on a rolling steel rack."""
    S = Raster(34, 48)
    if state < 2:
        S.rect(4, 6, 2, 36, STEEL_S); S.rect(28, 6, 2, 36, STEEL_S); S.rect(3, 5, 28, 2, STEEL); S.rect(3, 5, 28, 1, STEEL_H)
        S.rect(2, 41, 30, 2, STEEL_S)
        hang = APRONS if state == 0 else APRONS[:2]
        for i, (c, s, h) in enumerate(hang):
            S.rect(8 + i * 8, 7, 1, 3, STEEL_S); _apron(S, 4 + i * 8, 9, c, s, h)
        if state == 1:
            S.line((3, 5), (16, 8), STEEL_S); _apron(S, 20, 30, *APRONS[2], ln=10)
        for x in (5, 16, 29):
            caster(S, x, 44)
    else:
        S.line((2, 44), (30, 36), STEEL_S); S.line((2, 45), (30, 37), STEEL)
        for i, (c, s, h) in enumerate(APRONS):
            S.poly([(3 + i * 9, 46), (8 + i * 9, 36 + i), (14 + i * 9, 38 + i), (12 + i * 9, 46)], c)
        caster(S, 6, 45); caster(S, 30, 44)
    return S


def contrast_cart(state):
    """Contrast power-injector cart: steel cart, injector head on an arm, amber screen, contrast bottles."""
    S = Raster(32, 46)
    if state < 2:
        box(S, 4, 22, 24, 16, STEEL if state == 0 else "#a8b0bc", STEEL_S, STEEL_H)
        S.rect(5, 29, 22, 1, STEEL_S)
        for i in range(3):
            box(S, 7 + i * 7, 31, 4, 6, "#f4f6fa", "#c8ccd6"); S.rect(7 + i * 7, 33, 4, 2, "#3a6ad8")
        S.rect(15, 6, 2, 16, STEEL_S)                                     # pole
        box(S, 9, 2, 16, 7, "#e4e8f0", "#9aa4b4", "#ffffff")             # injector head
        S.rect(11, 4, 9, 3, "#ffb03a"); S.rect(12, 5, 4, 1, "#fff0a0")   # amber screen
        S.capsule((24, 8), (30, 14), 3, "#cfe8ff", "#8ab0d0")             # syringe barrel
        S.rect(2, 38, 28, 2, STEEL_S)
        for x in (6, 16, 26):
            caster(S, x, 42)
        if state == 1:
            S.line((8, 24), (12, 30), INK); S.line((12, 4), (17, 7), "#ffffff"); S.rect(27, 12, 3, 2, "#ffffff")
    else:
        S.poly([(3, 44), (6, 32), (24, 30), (30, 44)], STEEL_S); S.poly([(6, 42), (9, 34), (22, 33), (26, 42)], STEEL)
        box(S, 18, 24, 12, 6, "#e4e8f0", "#9aa4b4"); S.rect(20, 26, 6, 2, "#7a5a20")
        box(S, 3, 40, 4, 5, "#f4f6fa"); S.rect(12, 43, 6, 2, "#f4f6fa"); caster(S, 28, 44)
    return S


def film_viewer(state):
    """Rolling film viewer: a glowing lightbox on a wheeled stand (it lights the floor around it)."""
    S = Raster(28, 48)
    if state < 2:
        box(S, 2, 2, 24, 20, "#8a94a4", "#5c6676", "#c8d0dc")
        _film(S, 4, 4, 20, 16, "chest", random.Random(3))
        if state == 1:
            S.line((5, 5), (14, 19), "#ffffff"); S.line((14, 19), (22, 8), "#ffffff")
        S.rect(13, 22, 2, 18, STEEL_S); S.rect(5, 40, 18, 2, STEEL_S)
        caster(S, 6, 44); caster(S, 22, 44)
    else:
        S.poly([(2, 44), (6, 30), (26, 33), (24, 46)], "#5c6676"); S.poly([(5, 43), (8, 33), (23, 35), (21, 44)], "#16243e")
        S.line((8, 35), (20, 42), "#9ab8d8"); S.line((14, 34), (12, 43), "#9ab8d8")
        S.line((2, 46), (26, 46), STEEL_S); caster(S, 22, 46)
    return S


def rbits():
    out = {}
    S = Raster(8, 6); S.poly([(1, 1), (5, 1), (6, 5), (0, 5)], APRONS[0][0]); out["deb_apron"] = S
    S = Raster(5, 7); box(S, 1, 1, 3, 5, "#f4f6fa"); S.rect(1, 3, 3, 1, "#3a6ad8"); out["deb_bottle"] = S
    S = Raster(7, 6); S.poly([(0, 0), (6, 1), (5, 5), (1, 4)], NEON_H); S.line((1, 1), (5, 4), FILM); out["deb_film"] = S
    return out


# ------------------------------------------------------------------ projectiles
def proj_cup():
    S = Raster(10, 12)
    S.poly([(1, 2), (8, 2), (7, 11), (2, 11)], "#f4f6fa"); S.rect(2, 3, 6, 2, "#e8eef4"); S.rect(3, 6, 4, 2, "#3a6ad8")
    S.line((6, 0), (8, 3), "#ff6ab0")                                     # bendy straw
    return S


def barium_splat():
    S = Raster(30, 10)
    S.ellipse((15, 5), 13, 3.6, "#e8eef4", "#b8c2d0"); S.ellipse((9, 4), 4, 1.6, "#ffffff", rim=False); S.ellipse((22, 6), 3, 1.2, "#ffffff", rim=False)
    return S


def proj_film():
    S = Raster(16, 13)
    box(S, 1, 1, 14, 11, NEON_H, NEON_S); S.rect(2, 2, 12, 9, "#2a5aa0")
    S.rect(8, 3, 1, 7, BONE); S.line((3, 4), (7, 5), BONE); S.line((9, 5), (13, 4), BONE); S.line((3, 7), (7, 8), BONE); S.line((9, 8), (13, 7), BONE)
    return S


def mri_wave(k=0):
    """The MRI's knock: nested crescent sound waves rolling along the floor."""
    S = Raster(20, 30)
    cols = ("#ffffff", NEON_H, NEON) if k == 0 else ("#ffd0ff", "#d88aff", "#a24dff")
    for i, c in enumerate(cols):
        r = 13 - i * 4
        for a in range(-70, 71, 6):
            ra = math.radians(a)
            x, y = 4 + r * math.cos(ra) * 0.55 + i * 3, 15 + r * math.sin(ra)
            S.rect(int(x), int(y), 2, 2, c)
    return S


def mri_table():
    """The MRI patient table, launched out of the bore along a lane."""
    S = Raster(70, 18)
    box(S, 2, 3, 64, 5, "#f4f6fa", "#c8ccd6", "#ffffff")                 # pad
    S.rect(4, 2, 12, 2, "#ffffff"); S.rect(46, 4, 18, 3, "#7ab0e8")       # pillow + strap
    S.rect(3, 8, 62, 3, "#5c6676"); S.rect(3, 8, 62, 1, STEEL)            # rail
    S.rect(30, 11, 10, 3, "#3a4258"); caster(S, 33, 15); caster(S, 39, 15)
    S.rect(64, 4, 3, 3, NEON)
    return S


# ------------------------------------------------------------------ MRI boss: MAGNA-SCAN 3000 (front view)
# The layout below is in base units (the v0.5/v0.6 184x158 machine). v0.7 (Bill's boss-size override for this game:
# bosses only ~1.2-1.5x a nurse) draws it at MS = 0.56, so the whole machine stands ~1.45x a nurse's height.
# src/mri.js mirrors MS for the live LCD face.
MS = 0.56
BMW, BMH, BMAX, BMAY = 184, 158, 92, 154
MW, MH, MAX, MAY = int(BMW * MS) + 1, int(BMH * MS) + 1, round(BMAX * MS), round(BMAY * MS)


class MSR:
    """Scaled raster for the MRI: Raster calls in base units, rims stay a crisp 1px."""

    def __init__(self, R):
        self.R = R

    @staticmethod
    def _p(p):
        return (p[0] * MS, p[1] * MS)

    def _r(self, x, y, w, h):
        x0, y0 = int(round(x * MS)), int(round(y * MS))
        return x0, y0, max(1, int(round((x + w) * MS)) - x0), max(1, int(round((y + h) * MS)) - y0)

    def rect(self, x, y, w, h, c):
        self.R.rect(*self._r(x, y, w, h), c)

    def set(self, x, y, c):
        self.rect(x, y, 1, 1, c)

    def ellipse(self, c, rx, ry, col, shade=None, rim=True):
        self.R.ellipse(self._p(c), rx * MS, ry * MS, col, shade, rim)

    def poly(self, pts, col, rim=True):
        self.R.poly([self._p(p) for p in pts], col, rim)

    def line(self, a, b, col):
        self.R.line(self._p(a), self._p(b), col)

    def box(self, x, y, w, h, c, s=None, hi=None):
        x0, y0, w0, h0 = self._r(x, y, w, h)
        self.R.rect(x0 - 1, y0 - 1, w0 + 2, h0 + 2, INK); self.R.rect(x0, y0, w0, h0, c)
        if hi:
            self.R.rect(x0, y0, w0, 1, hi)
        if s:
            self.R.rect(x0, y0 + h0 - 1, w0, 1, s)


def mri_frame(state="idle", k=0):
    S = MSR(Raster(MW, MH))
    sh = (1 if k % 2 else -1) if state == "pull" else 0
    ox = 2 + sh
    # plinth + floor rail
    S.box(ox + 18, 134, 144, 16, "#3a4258", "#262c3e", "#56607a")
    for x in range(ox + 24, ox + 158, 12):
        S.rect(x, 140, 6, 1, "#262c3e")
    # housing (rounded, cut corners)
    body = [(ox + 22, 22), (ox + 36, 8), (ox + 144, 8), (ox + 158, 22), (ox + 158, 134), (ox + 22, 134)]
    S.poly(body, "#dfe5ee")
    S.poly([(ox + 146, 14), (ox + 158, 24), (ox + 158, 134), (ox + 146, 134)], "#b4bccb", rim=False)
    S.poly([(ox + 36, 9), (ox + 144, 9), (ox + 148, 13), (ox + 32, 13)], "#f6f8fc", rim=False)
    S.rect(ox + 22, 118, 136, 2, "#b4bccb")
    # LCD face band (the face is drawn live in src/mri.js)
    S.box(ox + 52, 16, 76, 20, "#0c1430", "#060a18", "#1c2850")
    # bore
    cx, cy = ox + 90, 82
    hot = state == "vent"
    S.ellipse((cx, cy), 44, 40, "#c4ccd8", "#9aa4b4")
    ring_c = "#ff6a3a" if hot else ("#bfeaff" if state == "pull" else NEON)
    if state == "dead":
        ring_c = "#5c6676"
    S.ellipse((cx, cy), 37, 34, ring_c, rim=False)
    S.ellipse((cx, cy), 33, 30, "#0a1028" if state != "dead" else "#10131c", rim=False)
    for r, c in ((25, "#121c40"), (18, "#182a5c"), (11, "#1e3876")):
        S.ellipse((cx, cy), r, r * 0.9, c if state != "dead" else "#14161e", rim=False)
    if state != "dead":
        S.ellipse((cx, cy), 6, 5.4, "#ffb03a" if hot else ("#ffffff" if state == "pull" else "#9ae8ff"), rim=False)
    if state == "pull":  # swirling field lines spiralling into the bore
        for i in range(8):
            a0 = i / 8 * 2 * math.pi + k * 0.4
            for j in range(10):
                rr = 31 - j * 2.6
                a = a0 + j * 0.22
                S.rect(int(cx + rr * math.cos(a)), int(cy + rr * 0.9 * math.sin(a)), 2, 1, "#bfeaff" if j < 5 else NEON)
    if hot:  # exposed superconducting coil, glowing (the weak point) + hazard stripes on the bezel
        for i in range(-24, 25, 6):
            S.rect(cx + i - 1, cy - 26, 3, 52, "#ffb03a" if (i // 6 + k) % 2 else "#ff6a3a")
        S.ellipse((cx, cy), 9, 8, "#fff0a0", rim=False)
        for a in range(0, 360, 20):
            ra = math.radians(a + k * 10)
            S.rect(int(cx + 41 * math.cos(ra)), int(cy + 37 * math.sin(ra)), 3, 3, "#ffd83a" if (a // 20) % 2 else INK)
    # vent hatch on top: closed, or flipped open with a frost plume
    if hot:
        S.poly([(ox + 118, 8), (ox + 142, 8), (ox + 146, -2 + 2), (ox + 122, 0)], "#9aa4b4")
        for i, (fx, fy, fr) in enumerate(((ox + 130, 5, 6), (ox + 124, 2, 4), (ox + 138, 3, 4))):
            S.ellipse((fx + (k % 2) * (1 if i % 2 else -1), fy), fr, fr * 0.7, "#e8f8ff", rim=False)
    else:
        S.rect(ox + 120, 5, 22, 4, "#9aa4b4"); S.rect(ox + 120, 5, 22, 1, "#c8d0dc")
    # side details: control buttons (left), NO METAL sticker (right), feet
    S.box(ox + 28, 60, 12, 30, "#c8d0dc", "#9aa4b4")
    for i, c in enumerate(("#5aff8a", "#ffd84a", "#ff5a3a")):
        S.rect(ox + 31, 64 + i * 8, 6, 4, c if state != "dead" else "#5c6676")
    S.poly([(ox + 146, 60), (ox + 154, 74), (ox + 138, 74)], "#ffd83a"); S.rect(ox + 145, 64, 2, 6, INK); S.set(ox + 145, 72, INK)
    S.rect(ox + 26, 150, 12, 4, "#262c3e"); S.rect(ox + 142, 150, 12, 4, "#262c3e")
    # the name plate lives on the plinth at this size (native-size font so it stays readable)
    label = "MAGNA-SCAN 3000"
    tinyfont.text(S.R, int(round((ox + 90) * MS)) - tinyfont.width(label) // 2, int(round(137 * MS)), label, "#9aa4b4" if state != "dead" else "#5c6676")
    return S.R


MRI_ANIMS = {"idle": ("idle", 2), "pull": ("pull", 2), "vent": ("vent", 2), "dead": ("dead", 1)}
