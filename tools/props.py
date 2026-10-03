"""Hospital props, pickups, weapons, FX and the background pieces (all drawn in code, original)."""
from __future__ import annotations

import math
import random

from rig import INK, Raster
import tinyfont
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "vendor" / "gravewake"))
import pixel_writer as PW  # noqa: E402  (Gravewake pixel writer, vendored copy)

STEEL, STEEL_S, STEEL_H = "#b8c0cc", "#7c8696", "#e4e8f0"
WOOD, WOOD_S, WOOD_H = "#c08a58", "#8e5e36", "#dcae7c"


def box(S, x, y, w, h, c, s=None, hi=None, rim=True):
    if rim:
        S.rect(x - 1, y - 1, w + 2, h + 2, INK)
    S.rect(x, y, w, h, c)
    if hi:
        S.rect(x, y, w, 1, hi)
    if s:
        S.rect(x, y + h - 1, w, 1, s)
        S.rect(x + w - 1, y, 1, h, s)


# ------------------------------------------------------------------ background pieces
def wall_tile(seed, kind="plain"):
    """32x104 wall column: wall paint, handrail, wainscot, baseboard (wall top y=0, floor line at y=104)."""
    S = Raster(32, 104)
    base, dark, light = "#cfdccb", "#bccbb8", "#dde8da"
    # gravewake soil generator gives the paint a gentle speckle without noise
    for ty in range(0, 64, 16):
        for tx in range(0, 32, 16):
            t = PW.soil(seed * 31 + tx + ty, base, dark, light, base, (tx + ty) // 16)
            for yy in range(16):
                for xx in range(16):
                    S.set(tx + xx, ty + yy, t.p[yy][xx])
    S.rect(0, 64, 32, 2, "#9fb3a0")
    S.rect(0, 66, 32, 30, "#7fa8a2")
    S.rect(0, 66, 32, 1, "#9cc4be")
    for x in (7, 23):
        S.rect(x, 68, 1, 26, "#6e958f")
    S.rect(0, 96, 32, 8, "#3c4c56")
    S.rect(0, 96, 32, 1, "#56687a")
    # handrail
    S.rect(0, 58, 32, 3, "#d9dee6"); S.rect(0, 60, 32, 1, "#8a94a4"); S.rect(0, 58, 32, 1, "#f4f6fa")
    S.rect(14, 61, 3, 3, "#8a94a4")
    return S


def ceiling_tile(lit):
    S = Raster(32, 14)
    S.rect(0, 0, 32, 14, "#e6e6dc")
    S.rect(0, 13, 32, 1, "#9a9a90")
    S.rect(0, 0, 1, 13, "#c8c8be")
    for (x, y) in ((5, 3), (12, 8), (20, 4), (27, 9), (9, 11)):
        S.set(x, y, "#c8c8be")
    if lit:
        S.rect(4, 2, 24, 8, "#f8fbff"); S.rect(4, 2, 24, 1, "#ffffff"); S.rect(4, 9, 24, 1, "#c4ccd8")
        for x in (10, 16, 22):
            S.rect(x, 2, 1, 8, "#dce4f0")
    return S


def floor_tiles():
    """Two linoleum tiles (24x12) made with the Gravewake pixel writer's speckle generator."""
    out = []
    for i, (b, d, l) in enumerate((("#d9cfb4", "#c9bea0", "#e8dfc8"), ("#c4b898", "#b4a886", "#d2c8aa"))):
        S = Raster(24, 12)
        for tx in (0, 16):
            t = PW.soil(70 + i * 5 + tx, b, d, l, d, i + tx // 16)
            for yy in range(12):
                for xx in range(16):
                    S.set(tx + xx, yy, t.p[yy][xx])
        S.rect(0, 0, 24, 1, "#a89c80")
        S.rect(0, 0, 1, 12, "#a89c80")
        out.append(S)
    return out


def door_frames():
    """Patient room door 36x68: frame + 4 opening frames (closed .. open)."""
    out = []
    for k in range(4):
        S = Raster(36, 68)
        box(S, 1, 1, 34, 67, "#8c96a4", "#5c6676", "#c4ccd8")
        S.rect(3, 3, 30, 65, "#262a3c")  # dark room
        # inside the room: window glow, bed silhouette, curtain
        S.rect(17, 12, 12, 14, "#4a6a9a"); S.rect(18, 13, 10, 12, "#7aa0d0"); S.rect(23, 13, 1, 12, "#4a6a9a")
        S.rect(5, 40, 24, 8, "#3a3e54"); S.rect(5, 38, 8, 3, "#e8ecf4"); S.rect(5, 48, 2, 10, "#3a3e54"); S.rect(27, 48, 2, 10, "#3a3e54")
        S.rect(3, 3, 6, 65, "#4a5a7a")
        for y in range(3, 66, 3):
            S.set(5, y, "#3a4866"); S.set(7, y + 1, "#3a4866")
        w = [30, 22, 13, 4][k]
        if w:
            x0 = 3
            S.rect(x0, 3, w, 65, WOOD)
            S.rect(x0, 3, w, 1, WOOD_H)
            S.rect(x0 + w - 1, 3, 1, 65, WOOD_S)
            if w > 10:
                wx = x0 + w // 2 - 3
                S.rect(wx, 12, 6, 16, INK); S.rect(wx + 1, 13, 4, 14, "#9cc4e4"); S.set(wx + 1, 13, "#e4f4ff")
                hx = x0 + w - 4
                S.rect(hx, 36, 3, 2, STEEL_H); S.set(hx, 38, STEEL_S)
            S.rect(x0, 62, w, 6, "#9a6a40")
        out.append(S)
    return out


def elevator_frame():
    """Elevator bank opening 72x80 (doors are separate) + indicator + call buttons."""
    S = Raster(80, 82)
    box(S, 4, 10, 72, 72, "#9aa4b4", "#646e80", "#d6dce6")
    S.rect(8, 14, 64, 68, "#f2d8a0")  # warm lit car
    S.rect(8, 14, 64, 4, "#fff4d0")
    S.rect(8, 70, 64, 12, "#b08a60")
    S.rect(8, 40, 64, 2, "#d8b880")  # car handrail
    S.rect(36, 18, 8, 8, "#c0a070")
    # indicator panel above
    box(S, 22, 0, 36, 8, "#20222c")
    S.rect(30, 2, 3, 4, "#ff5a3a")
    return S


def elevator_door():
    S = Raster(32, 68)
    S.rect(0, 0, 32, 68, "#c4ccd8")
    for x in range(2, 32, 6):
        S.rect(x, 0, 1, 68, "#d8dee8")
    S.rect(0, 0, 32, 1, "#eef2f8"); S.rect(31, 0, 1, 68, "#7c8696"); S.rect(0, 0, 1, 68, "#eef2f8")
    S.rect(0, 64, 32, 4, "#8a94a4")
    return S


def call_panel():
    S = Raster(8, 18)
    box(S, 1, 1, 6, 16, "#9aa4b4", "#646e80")
    S.rect(3, 4, 2, 2, "#f4f0d0"); S.rect(3, 10, 2, 2, "#f4f0d0")
    return S


def call_panel_lit():
    S = call_panel()
    S.rect(3, 4, 2, 2, "#ffb030"); S.rect(3, 10, 2, 2, "#ffb030")
    return S


def nurses_station():
    S = Raster(132, 50)
    # counter
    box(S, 2, 18, 128, 31, "#8a9ab8", "#5a6a88", "#b4c2dc")
    S.rect(0, 14, 132, 5, "#e8e2d4"); S.rect(0, 14, 132, 1, "#ffffff"); S.rect(0, 18, 132, 1, "#a8a090")
    S.rect(6, 24, 120, 2, "#6a7a98")
    tinyfont.text(S, 30, 30, "NURSES STATION", "#f4f4f8")
    # monitors, phone, papers, coffee mug, flowers
    for mx in (14, 64):
        box(S, mx, 1, 18, 12, "#2a2e3a"); S.rect(mx + 1, 2, 16, 10, "#3aa0e0"); S.rect(mx + 2, 3, 6, 1, "#c4ecff"); S.rect(mx + 2, 5, 10, 1, "#c4ecff")
        S.rect(mx + 8, 13, 2, 1, "#2a2e3a")
    box(S, 38, 9, 8, 4, "#3a3a44"); S.rect(39, 8, 6, 1, "#3a3a44")
    S.rect(48, 11, 10, 3, "#f8f8f0"); S.rect(49, 10, 8, 1, "#f8f8f0")
    box(S, 92, 8, 5, 5, "#ff6a3a"); S.set(97, 9, "#ff6a3a")
    S.rect(108, 6, 2, 8, "#3a8a3a"); S.ellipse((109, 5), 3, 2, "#ff7ab0"); S.ellipse((105, 7), 2, 2, "#ffd84a"); S.ellipse((113, 7), 2, 2, "#8ad8ff")
    box(S, 104, 9, 10, 5, "#d8d8e0")
    return S


def window_city(seed=1):
    S = Raster(64, 40)
    box(S, 1, 1, 62, 38, "#e8ecf2", "#9aa4b4")
    S.rect(3, 3, 58, 34, "#8ec8f0")
    S.rect(3, 3, 58, 10, "#b8e0fa")
    r = random.Random(seed)
    x = 3
    while x < 61:
        w, h = r.randint(5, 10), r.randint(8, 24)
        c = r.choice(["#6a88a8", "#7a96b4", "#5a7898"])
        S.rect(x, 37 - h, min(w, 61 - x), h, c)
        for wy in range(37 - h + 2, 36, 3):
            for wx in range(x + 1, min(x + w, 61) - 1, 2):
                if r.random() < 0.6:
                    S.set(wx, wy, "#d8ecff")
        x += w + 1
    S.rect(32, 3, 1, 34, "#e8ecf2")
    for y in range(3, 15, 2):  # blinds half down
        S.rect(3, y, 58, 1, "#f4f4ee")
    S.rect(3, 15, 58, 1, "#c4c4bc")
    return S


def poster(kind):
    S = Raster(22, 28)
    if kind == "hands":
        box(S, 1, 1, 20, 26, "#fffaf0", "#c8c0b0")
        S.ellipse((8, 12), 4, 5, "#f2c8a2"); S.ellipse((14, 12), 4, 5, "#f2c8a2")
        for i in range(4):
            S.set(5 + i * 4, 6, "#7ac8ff")
        tinyfont.text(S, 3, 20, "WASH", "#2a5aa8")
    elif kind == "bingo":
        box(S, 1, 1, 20, 26, "#ffe86a", "#c8a830")
        tinyfont.text(S, 2, 3, "BINGO", "#c82a2a")
        for gy in range(3):
            for gx in range(4):
                S.rect(3 + gx * 4, 10 + gy * 4, 3, 3, "#ffffff" if (gx + gy) % 2 else "#ff8ac0")
        tinyfont.text(S, 4, 22, "7PM", "#2a2a3a")
    elif kind == "duck":
        box(S, 1, 1, 20, 18, "#c89a40", "#8a6a20")
        S.rect(3, 3, 16, 14, "#a8d8f0"); S.rect(3, 12, 16, 5, "#5aa0d0")
        S.ellipse((11, 11), 4, 3, "#ffe040"); S.ellipse((14, 8), 2, 2, "#ffe040"); S.set(16, 8, "#ff8a20"); S.set(14, 7, INK)
    elif kind == "quiet":
        box(S, 1, 1, 20, 10, "#2a5aa8", "#1a3a78")
        tinyfont.text(S, 2, 3, "QUIET", "#ffffff")
    elif kind == "board":
        box(S, 1, 1, 20, 18, "#c8a070", "#8a6a40")
        S.rect(3, 3, 7, 6, "#fff7a0"); S.rect(11, 4, 7, 5, "#a0e8ff"); S.rect(5, 10, 8, 7, "#ffb0d0"); S.rect(14, 11, 4, 5, "#ffffff")
        for (x, y) in ((6, 3), (14, 4), (8, 10), (15, 11)):
            S.set(x, y, "#e83a3a")
    elif kind == "clock":
        S.ellipse((11, 10), 8, 8, "#ffffff", "#d8d8e0")
        S.line((11, 10), (11, 4), INK); S.line((11, 10), (15, 10), INK); S.set(11, 10, "#e83a3a")
    elif kind == "sanitizer":
        box(S, 7, 4, 8, 14, "#f4f4f8", "#b8bcc8"); S.rect(9, 18, 4, 2, "#b8bcc8"); S.rect(8, 7, 6, 4, "#7ac8ff")
    elif kind == "alarm":
        box(S, 8, 6, 6, 8, "#e83a3a", "#a82020"); S.rect(10, 9, 2, 2, "#ffffff")
    elif kind == "tv":
        box(S, 1, 2, 20, 14, "#2a2a32"); S.rect(3, 4, 16, 10, "#5ab0ff"); S.rect(5, 6, 6, 2, "#c4f0ff"); S.rect(8, 16, 6, 2, "#4a4a52")
    return S


def sign(text, c="#2a5aa8", w=None):
    tw = tinyfont.width(text)
    w = w or tw + 8
    S = Raster(w, 11)
    box(S, 1, 1, w - 2, 9, c, None, None)
    tinyfont.text(S, (w - tw) // 2, 3, text, "#ffffff")
    return S


def floor_number(n):
    S = Raster(26, 24)
    box(S, 1, 1, 24, 22, "#2a5aa8", "#1a3a78")
    tinyfont.text(S, 7, 4, str(n), "#ffffff", 3)
    return S


def chairs():
    S = Raster(56, 26)
    for i in range(3):
        x = 2 + i * 18
        box(S, x, 2, 15, 12, "#5a8ad8", "#3a64a8", "#8ab4f0")
        box(S, x, 14, 15, 4, "#4a7ac8", "#3a64a8")
        S.rect(x + 1, 19, 1, 6, "#5c6676"); S.rect(x + 13, 19, 1, 6, "#5c6676")
    S.rect(1, 18, 54, 1, "#5c6676")
    return S


def wheelchair_empty():
    S = Raster(30, 30)
    S.ellipse((10, 20), 8, 8, "#3a3e4a"); S.ellipse((10, 20), 6, 6, "#9aa4b4"); S.ellipse((10, 20), 2, 2, "#3a3e4a")
    box(S, 6, 12, 14, 3, "#2a5aa8"); box(S, 4, 2, 3, 12, "#2a5aa8"); S.rect(4, 0, 2, 2, "#3a3e4a")
    S.line((18, 15), (24, 26), "#7c8696"); S.ellipse((24, 27), 2, 2, "#3a3e4a")
    return S


def gurney():
    S = Raster(52, 26)
    box(S, 2, 6, 48, 4, "#f4f6fa", "#c8ccd6")
    S.rect(4, 4, 10, 3, "#ffffff")
    S.rect(3, 10, 46, 2, "#7c8696")
    for x in (6, 44):
        S.rect(x, 12, 2, 10, "#9aa4b4"); S.ellipse((x + 1, 23), 2, 2, "#3a3e4a")
    S.rect(1, 0, 2, 10, "#9aa4b4")
    return S


def water_fountain():
    S = Raster(18, 26)
    box(S, 2, 4, 14, 10, "#c8ccd6", "#8a94a4", "#eef2f8")
    S.rect(5, 5, 8, 3, "#9ad4ff"); S.set(10, 3, "#7c8696"); S.set(10, 2, "#7c8696")
    S.rect(7, 14, 4, 11, "#8a94a4")
    return S


# ------------------------------------------------------------------ breakables
def med_cart(state):
    S = Raster(30, 32)
    if state < 2:
        box(S, 3, 4, 24, 22, "#e84a5a" if state == 0 else "#c83a4a", "#a82838", "#ff8a96")
        for y in (9, 15, 21):
            S.rect(4, y, 22, 1, "#a82838"); S.rect(13, y - 3, 4, 1, STEEL_H)
        S.rect(2, 2, 26, 3, STEEL); S.rect(2, 2, 26, 1, STEEL_H)
        S.rect(5, 0, 6, 2, "#f4f4f8"); S.rect(18, 0, 4, 2, "#7ac8ff")
        for x in (6, 22):
            S.ellipse((x + 1, 28), 2, 2, "#3a3e4a")
        if state == 1:
            S.line((6, 8), (12, 18), INK); S.line((20, 6), (24, 14), INK); S.rect(13, 15, 4, 1, "#a82838")
    else:
        S.poly([(2, 24), (12, 18), (16, 26)], "#c83a4a"); S.poly([(16, 28), (26, 20), (28, 30)], "#e84a5a")
        S.rect(4, 29, 22, 2, STEEL_S); S.ellipse((8, 29), 2, 2, "#3a3e4a")
    return S


def linen_bin(state):
    S = Raster(26, 32)
    if state < 2:
        box(S, 3, 8, 20, 18, "#4a7ac8", "#2a5aa8", "#7aa4e8")
        S.ellipse((13, 8), 10, 4, "#f4f4f8", "#c8ccd6")
        S.ellipse((9, 5), 4, 3, "#ffffff"); S.ellipse((17, 6), 4, 3, "#e8f0ff")
        S.rect(4, 26, 18, 2, STEEL_S)
        for x in (5, 19):
            S.ellipse((x + 1, 29), 2, 2, "#3a3e4a")
        tinyfont.text(S, 7, 15, "LINEN" [:3], "#ffffff")
        if state == 1:
            S.line((6, 12), (10, 22), INK); S.line((18, 10), (16, 20), INK)
    else:
        S.ellipse((7, 26), 6, 3, "#f4f4f8", "#c8ccd6"); S.ellipse((18, 27), 7, 3, "#e8f0ff", "#c8ccd6")
        S.poly([(4, 30), (10, 22), (13, 30)], "#2a5aa8")
    return S


def vending(state):
    S = Raster(36, 66)
    if state < 2:
        box(S, 2, 2, 32, 62, "#d83a4a", "#a02434", "#ff6a7a")
        S.rect(5, 5, 20, 40, "#1a2a3a" if state == 0 else "#22303e")
        cols = ["#ffd84a", "#7ad8ff", "#ff8ac0", "#8ae87a", "#ffa04a"]
        for gy in range(5):
            S.rect(6, 7 + gy * 8, 18, 1, "#7c8696")
            for gx in range(4):
                S.rect(7 + gx * 4, 3 + gy * 8 + 1, 3, 3, cols[(gx + gy) % 5])
        S.rect(27, 8, 5, 12, "#2a2a32")
        for k in range(6):
            S.set(28 + (k % 2) * 2, 9 + (k // 2) * 3, "#ffd84a")
        S.rect(27, 24, 5, 3, "#2a2a32")
        S.rect(6, 50, 18, 8, "#2a2a32")
        tinyfont.text(S, 6, 46, "SNAX", "#ffffff")
        S.rect(5, 5, 20, 1, "#5a6a7a"); S.line((6, 44), (12, 6), "#3a4a5a")
        if state == 1:
            for (a, b) in (((8, 10), (16, 22)), ((16, 22), (12, 34)), ((16, 22), (23, 26)), ((16, 22), (20, 8))):
                S.line(a, b, "#e4f4ff")
    else:
        box(S, 2, 24, 32, 40, "#a02434", "#701824", "#d83a4a")
        S.rect(5, 26, 20, 20, "#1a2a3a")
        S.poly([(2, 24), (10, 12), (18, 24)], "#d83a4a"); S.poly([(20, 24), (30, 16), (34, 24)], "#d83a4a")
        for (x, y) in ((8, 30), (14, 36), (20, 31), (11, 41)):
            S.set(x, y, "#e4f4ff")
    return S


def iv_stand(state):
    S = Raster(20, 56)
    if state == 0:
        S.rect(9, 6, 2, 46, STEEL); S.rect(9, 6, 1, 46, STEEL_H)
        S.ellipse((10, 6), 4, 5, "#cfe8ff", "#9ac4f0"); S.rect(9, 0, 2, 2, STEEL_S)
        S.rect(3, 51, 14, 2, STEEL_S)
        for x in (3, 10, 16):
            S.ellipse((x, 54), 1.5, 1.5, "#3a3e4a")
    else:
        S.rect(2, 52, 16, 2, STEEL_S); S.ellipse((14, 51), 4, 3, "#cfe8ff", "#9ac4f0")
    return S


# ------------------------------------------------------------------ pickups, weapons, projectiles
def coffee():
    S = Raster(12, 16)
    S.line((4, 0), (5, 3), "#e8e8f0"); S.line((7, 1), (6, 3), "#e8e8f0")
    S.poly([(2, 5), (10, 5), (9, 15), (3, 15)], "#f4f0e4")
    S.rect(2, 4, 8, 2, "#3a2a20")
    S.rect(3, 8, 6, 4, "#b8743a"); S.set(5, 9, "#f4f0e4"); S.set(6, 10, "#f4f0e4")
    return S


def pizza():
    S = Raster(22, 16)
    box(S, 1, 6, 20, 9, "#d8b078", "#a8804a", "#ecc894")
    S.poly([(3, 7), (19, 7), (11, 1)], "#ffcc44")
    S.rect(5, 6, 12, 1, "#e8902a")
    for (x, y) in ((8, 5), (13, 5), (11, 3)):
        S.set(x, y, "#d83a3a"); S.set(x + 1, y, "#d83a3a")
    return S


def candy():
    S = Raster(16, 10)
    S.poly([(0, 2), (3, 4), (3, 6), (0, 8)], "#ffd84a"); S.poly([(16, 2), (13, 4), (13, 6), (16, 8)], "#ffd84a")
    box(S, 3, 3, 10, 4, "#e83a8a", "#a8205a", "#ff8ac0")
    S.rect(5, 4, 6, 1, "#ffffff")
    return S


def token():
    S = Raster(14, 14)
    S.ellipse((7, 7), 6, 6, "#ffd84a", "#d8a020")
    tinyfont.text(S, 4, 5, "2X", "#8a5a10")
    S.set(4, 3, "#ffffff")
    return S


def star():
    S = Raster(14, 14)
    pts = []
    for i in range(10):
        a = math.pi * 2 * i / 10 - math.pi / 2
        r = 6 if i % 2 == 0 else 2.6
        pts.append((7 + math.cos(a) * r, 7.4 + math.sin(a) * r))
    S.poly(pts, "#ffd84a")
    S.set(6, 5, "#ffffff")
    return S


def donut():
    S = Raster(14, 12)
    S.ellipse((7, 6), 6, 5, "#c8864a")
    S.ellipse((7, 5), 5, 3.6, "#ff8ac0")
    S.ellipse((7, 5), 1.6, 1.2, "#c8864a", rim=True)
    for (x, y) in ((4, 4), (9, 3), (10, 6), (5, 7)):
        S.set(x, y, ["#ffffff", "#7ad8ff", "#ffd84a", "#8ae87a"][(x + y) % 4])
    return S


def w_clipboard():
    S = Raster(12, 16)
    box(S, 1, 2, 10, 13, "#b07a3e", "#8a5a2a")
    S.rect(2, 4, 8, 10, "#f4f0e4")
    for y in (6, 8, 10):
        S.rect(3, y, 6, 1, "#9aa4b4")
    S.rect(4, 0, 4, 3, STEEL)
    return S


def w_bedpan():
    S = Raster(18, 12)
    S.ellipse((8, 6), 7, 4.5, "#e8ecf2", "#a8b0bc")
    S.ellipse((8, 6), 4.5, 2.6, "#c4ccd8", rim=False)
    S.capsule((14, 6), (17, 6), 3, "#e8ecf2", "#a8b0bc")
    return S


def w_mop():
    S = Raster(40, 12)
    S.capsule((2, 5), (30, 5), 2.2, "#c8a070", "#8a6a40")
    S.ellipse((34, 5), 5, 5, "#f0ead0", "#c8c0a0")
    for y in range(1, 10, 2):
        S.set(38, y, "#c8c0a0")
    return S


def w_extinguisher():
    S = Raster(14, 22)
    S.capsule((6, 6), (6, 19), 7, "#e83a3a", "#a82020")
    S.rect(4, 1, 5, 3, "#2a2a32"); S.line((9, 2), (12, 6), "#2a2a32")
    S.rect(4, 10, 5, 4, "#ffffff")
    return S


def w_ivpole():
    S = Raster(50, 12)
    S.rect(4, 5, 40, 2, STEEL); S.rect(4, 5, 40, 1, STEEL_H)
    S.ellipse((46, 6), 3.5, 4.5, "#cfe8ff", "#9ac4f0")
    S.rect(1, 2, 2, 8, STEEL_S)
    return S


def remote():
    S = Raster(10, 6)
    box(S, 1, 1, 8, 4, "#4a4e5a", "#30343e")
    S.set(7, 2, "#e83a3a"); S.set(4, 2, "#c8ccd6")
    return S


def pudding():
    S = Raster(9, 9)
    S.poly([(1, 3), (8, 3), (7, 8), (2, 8)], "#f4f0e4")
    S.rect(1, 2, 7, 2, "#c8864a"); S.set(4, 1, "#ff4a4a")
    return S


def yarn(c="#ff6ab0"):
    S = Raster(10, 10)
    S.ellipse((5, 5), 4, 4, c, "#c84a8a")
    S.line((2, 3), (8, 7), "#ffd0e8"); S.line((3, 7), (7, 2), "#ffd0e8")
    return S


def wet_sign():
    S = Raster(16, 22)
    S.poly([(8, 1), (14, 20), (2, 20)], "#ffd84a")
    S.rect(5, 10, 6, 1, INK); S.set(8, 13, INK); S.set(7, 14, INK); S.set(9, 14, INK)
    return S


def puddle():
    S = Raster(28, 8)
    S.ellipse((14, 4), 13, 3, "#9ad8ff", "#6ab0e0", rim=False)
    S.rect(8, 3, 4, 1, "#e4f6ff")
    return S


def shadow():
    S = Raster(32, 8)
    S.ellipse((16, 4), 13, 3, "#000000", rim=False)
    return S


def spark(size, frame, c="#fff4a0", c2="#ffffff"):
    S = Raster(size, size)
    m = size / 2
    n = 8
    L = [0.45, 0.9, 0.7][frame] * m
    for i in range(n):
        a = math.pi * 2 * i / n + (0.2 if frame == 1 else 0)
        l = L if i % 2 == 0 else L * 0.55
        S.capsule((m, m), (m + math.cos(a) * l, m + math.sin(a) * l), 2.2 if frame < 2 else 1.4, c, rim=frame < 2)
    if frame < 2:
        S.ellipse((m, m), m * 0.28, m * 0.28, c2, rim=False)
    return S


def dust(frame):
    S = Raster(20, 12)
    for k, (x, y, r) in enumerate(((6, 7, 3), (11, 6, 4), (15, 8, 2.6))):
        rr = r * (0.7 + frame * 0.25)
        S.ellipse((x - frame * (1 if k == 0 else -1 if k == 2 else 0), y - frame), rr, rr * 0.8, "#efe8d8" if frame < 2 else "#d8d0c0", rim=frame < 3)
    return S


def smoke(frame):
    S = Raster(16, 16)
    r = 3 + frame * 1.6
    S.ellipse((8, 9 - frame), r, r, ["#a8a8b0", "#8a8a94", "#6a6a74"][frame], rim=frame < 2)
    return S


def zzz():
    S = Raster(16, 14)
    import tinyfont as tf
    tf.text(S, 1, 8, "Z", "#ffffff"); tf.text(S, 6, 4, "Z", "#ffffff", 1); tf.text(S, 10, 0, "Z", "#ffffff")
    return S


def dizzy(frame):
    S = Raster(22, 8)
    for i in range(3):
        a = frame * 0.7 + i * 2.1
        x, y = 11 + math.cos(a) * 8, 4 + math.sin(a) * 2.5
        S.set(int(x), int(y), "#ffe84a"); S.set(int(x) + 1, int(y), "#ffe84a"); S.set(int(x), int(y) - 1, "#ffffff")
    return S


def heart():
    S = Raster(9, 8)
    S.ellipse((2.5, 2.5), 2, 2, "#ff4a7a", rim=False); S.ellipse((6.5, 2.5), 2, 2, "#ff4a7a", rim=False)
    S.poly([(0.5, 3), (8.5, 3), (4.5, 7.5)], "#ff4a7a", rim=False)
    return S
