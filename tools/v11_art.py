"""v0.11 PARKING GARAGE AT SHIFT CHANGE sprites: concrete garage tiles and wall pieces (open-air gaps onto a dawn sky,
pillars with the level paint, sodium wall packs, fluorescent tubes, neon PARKING / STAIRS / VALET signs, a ticket booth and
a striped gate arm, a ramp), parody cars (no real brands: ZIPPY HATCH, COMMUTER LX, FAMILY HAULER, WOODY WAGON) in two
colours and three damage states, traffic cones, shopping carts, the pay station, coffee + parking-ticket projectiles and
VINNIE THE VALET's golf cart. All side view, facing right (the game flips)."""
from __future__ import annotations

import random
import sys
from pathlib import Path

from rig import INK, Raster
import tinyfont
from v09_art import _wheel

sys.path.insert(0, str(Path(__file__).parent / "vendor" / "gravewake"))
import pixel_writer as PW  # noqa: E402

CONC, CONC_D, CONC_L = "#8a909c", "#767c88", "#9ea4ae"
LEVEL_PAINT = ("#7a3ad8", "#5a24a8")   # this level's colour code: violet (Bill's gloom-and-glow)


def box(S, x, y, w, h, c, s=None, hi=None, rim=True):
    if rim:
        S.rect(x - 1, y - 1, w + 2, h + 2, INK)
    S.rect(x, y, w, h, c)
    if hi:
        S.rect(x, y, w, 1, hi)
    if s:
        S.rect(x, y + h - 1, w, 1, s)
        S.rect(x + w - 1, y, 1, h, s)


def _speckle(S, x0, y0, w, h, seed, b=CONC, d=CONC_D, l=CONC_L):
    for ty in range(0, h, 16):
        for tx in range(0, w, 16):
            t = PW.soil(seed * 37 + tx * 3 + ty, b, d, l, b, (tx + ty) // 16)
            for yy in range(min(16, h - ty)):
                for xx in range(min(16, w - tx)):
                    S.set(x0 + tx + xx, y0 + ty + yy, t.p[yy][xx])


# ------------------------------------------------------------------ background tiles
def gwall_tile(seed):
    """32x104 garage back wall: board-formed concrete, a violet level stripe, a dark kick band and a yellow curb."""
    S = Raster(32, 104)
    _speckle(S, 0, 0, 32, 66, seed)
    for y in (10, 26, 42, 58):
        S.rect(0, y, 32, 1, CONC_D)
    S.rect(0, 64, 32, 7, LEVEL_PAINT[0]); S.rect(0, 64, 32, 1, "#a46aff"); S.rect(0, 70, 32, 1, LEVEL_PAINT[1])
    _speckle(S, 0, 71, 32, 25, seed + 9, "#6e7480", "#5e6470", "#7a808c")
    S.rect(0, 96, 32, 8, "#e8c02a"); S.rect(0, 96, 32, 1, "#fff08a"); S.rect(0, 102, 32, 2, "#a8861a")
    for x in (6, 22):
        S.rect(x, 97, 4, 5, "#2a2a30")  # scuffs on the curb paint
    if seed == 2:  # rust drip from a tie hole
        S.rect(9, 12, 2, 2, "#4a4e58"); S.rect(10, 14, 1, 18, "#9a6a4a")
    if seed == 3:  # a crack
        for i, (x, y) in enumerate(((20, 30), (21, 33), (21, 36), (23, 38), (23, 42), (24, 45))):
            S.set(x, y, "#4a4e58"); S.set(x, y + 1, "#4a4e58")
    return S


def gceil_tile(lit=False):
    """32x14 concrete deck underside: a beam lip and a conduit run."""
    S = Raster(32, 14)
    S.rect(0, 0, 32, 14, "#4e525e"); S.rect(0, 9, 32, 5, "#3e424c"); S.rect(0, 9, 32, 1, "#5e626e"); S.rect(0, 13, 32, 1, "#2a2c34")
    S.rect(0, 4, 32, 2, "#7c8696"); S.rect(0, 4, 32, 1, "#a8b0bc")
    S.rect(30, 3, 2, 4, "#5a6070")
    if lit:
        S.rect(10, 10, 12, 3, "#ffd8a0")
    return S


def gfloor_tiles():
    """Two 24x12 concrete floor tiles (oil-stained grey)."""
    out = []
    for i, (b, d, l) in enumerate((("#6c7078", "#60646c", "#787c84"), ("#666a72", "#5a5e66", "#72767e"))):
        S = Raster(24, 12)
        _speckle(S, 0, 0, 24, 12, 80 + i * 7, b, d, l)
        if i:
            S.rect(0, 0, 24, 1, "#5a5e66")
        out.append(S)
    return out


def opening(seed=1, sun=False):
    """An open-air gap in the wall onto the dawn: violet sky to a hot pink / orange horizon, a city skyline (a few windows
    still lit), cable barrier across. 72x52, on the wall at y=24."""
    S = Raster(72, 52)
    rng = random.Random(seed)
    sky = ["#2a2050", "#3a2a6a", "#5a3080", "#8a3a8a", "#c04a80", "#e86a6a", "#ff9a5a", "#ffc070"]
    for y in range(52):
        S.rect(0, y, 72, 1, sky[min(len(sky) - 1, y * len(sky) // 46)])
    for _ in range(6):
        S.set(rng.randrange(2, 70), rng.randrange(1, 10), "#d8d0ff")
    if sun:
        S.ellipse((50, 44), 9, 9, "#ffe08a", None, rim=False); S.ellipse((50, 44), 6, 6, "#fff4c0", None, rim=False)
    x = 0
    while x < 72:  # skyline
        w = rng.randrange(6, 14); h = rng.randrange(10, 30)
        S.rect(x, 52 - h, w, h, "#2a1a3a" if rng.random() < 0.6 else "#34224a")
        for wy in range(52 - h + 3, 50, 4):
            for wx in range(x + 2, x + w - 1, 3):
                if rng.random() < 0.18:
                    S.set(wx, wy, "#ffd86a")
        if rng.random() < 0.3:
            S.rect(x + w // 2, 52 - h - 4, 1, 4, "#2a1a3a"); S.set(x + w // 2, 52 - h - 5, "#ff3a4a")
        x += w
    # concrete reveal around the gap + the cable barrier
    S.rect(0, 0, 72, 3, "#5e646e"); S.rect(0, 0, 2, 52, "#5e646e"); S.rect(70, 0, 2, 52, "#5e646e")
    for y in (20, 30, 40):
        S.rect(2, y, 68, 1, "#b8c0cc")
    for x in (2, 69):
        S.rect(x, 18, 1, 26, "#7c8696")
    return S


def pillar():
    """22x104 square concrete column on the wall plane: level paint band with 'P3', hazard stripes at the base."""
    S = Raster(22, 104)
    _speckle(S, 2, 0, 18, 104, 41, "#a2a8b2", "#8e949e", "#b4bac4")
    S.rect(0, 0, 2, 104, INK); S.rect(20, 0, 2, 104, INK); S.rect(15, 0, 5, 104, "#7c828c")
    S.rect(2, 30, 18, 16, LEVEL_PAINT[0]); S.rect(15, 30, 5, 16, LEVEL_PAINT[1]); S.rect(2, 30, 18, 1, "#a46aff")
    tinyfont.text(S, 3, 33, "P3", "#ffffff", 2)
    for y in range(86, 104):
        for x in range(2, 20):
            S.set(x, y, "#ffd02a" if ((x + y) // 4) % 2 else "#1a1a20")
    return S


def sodium():
    """A sodium wall pack (orange) on a short bracket. 14x10."""
    S = Raster(14, 10)
    box(S, 1, 1, 12, 7, "#3a3e48", "#2a2c34", "#5a5e6a")
    S.rect(3, 5, 8, 3, "#ffb04a"); S.rect(3, 5, 8, 1, "#ffe0a0")
    return S


def tube():
    """A bare fluorescent strip hanging from the deck on two chains. 34x8."""
    S = Raster(34, 8)
    for x in (6, 27):
        S.rect(x, 0, 1, 3, "#7c8696")
    box(S, 1, 3, 32, 4, "#c8ccd6", None, "#e4e8f0")
    S.rect(2, 5, 30, 2, "#f0fbff"); S.rect(2, 6, 30, 1, "#bfe8ff")
    return S


def neon(text, col, core="#ffffff", w=None, scale=2):
    """Neon letters on a dark backboard: a coloured outline round a white-hot core."""
    tw = tinyfont.width(text, scale)
    w = w or tw + 10
    h = 5 * scale + 8
    S = Raster(w, h)
    box(S, 1, 1, w - 2, h - 2, "#14121e", None, "#2a2638")
    x0, y0 = (w - tw) // 2, 4
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        tinyfont.text(S, x0 + dx, y0 + dy, text, col, scale)
    tinyfont.text(S, x0, y0, text, core, scale)
    return S


def paint_sign(text, c, fg="#ffffff", w=None):
    tw = tinyfont.width(text)
    w = w or tw + 8
    S = Raster(w, 11)
    box(S, 1, 1, w - 2, 9, c, None, None)
    tinyfont.text(S, (w - tw) // 2, 3, text, fg)
    return S


def clearance():
    """Yellow + black clearance bar hanging from the deck: MAX HT 6'8."""
    S = Raster(64, 14)
    for x in (8, 55):
        S.rect(x, 0, 1, 4, "#7c8696")
    box(S, 1, 4, 62, 9, "#ffd02a")
    for x in range(2, 62, 8):
        S.rect(x, 5, 3, 7, "#1a1a20")
    S.rect(20, 5, 24, 7, "#ffd02a")
    tinyfont.text(S, 21, 6, "6'8", "#1a1a20")
    return S


def booth():
    """The pay booth: a little white kiosk with a sliding window, a PAY sign on the roof, a coffee mug on the sill. 50x64."""
    S = Raster(50, 64)
    box(S, 3, 12, 44, 51, "#e8e4d8", "#b8b4a8", "#ffffff")
    box(S, 0, 8, 50, 5, "#d0243a", "#981a2a", "#ff6a6a")
    box(S, 14, 0, 22, 8, "#ffd02a"); tinyfont.text(S, 19, 2, "PAY", "#1a1a20")
    box(S, 8, 18, 34, 20, "#3a5a8a"); S.rect(9, 19, 32, 6, "#6a8ac0"); S.rect(25, 19, 1, 18, "#c8ccd6")
    S.rect(12, 30, 6, 6, "#2a2c34")  # stool back in the dark
    S.rect(6, 38, 38, 2, "#9a968a"); S.rect(32, 34, 4, 4, INK); S.rect(33, 35, 2, 2, "#e8f4ff")
    S.rect(8, 44, 34, 1, "#c8c4b8"); S.rect(8, 52, 34, 1, "#c8c4b8")
    tinyfont.text(S, 10, 46, "CASH", "#6a6a7a")
    return S


def gate_arm(up=False):
    """Exit gate: a yellow control box with a red / white striped arm. 70x40."""
    S = Raster(70, 40)
    box(S, 2, 14, 12, 25, "#ffd02a", "#c8a01a", "#fff08a")
    S.rect(5, 18, 6, 4, "#1a1a20"); S.rect(6, 19, 2, 2, "#3ae86a")
    if not up:
        box(S, 12, 15, 56, 4, "#f4f4f4")
        for x in range(16, 68, 10):
            S.rect(x, 15, 5, 4, "#e83a3a")
        S.rect(66, 13, 2, 8, "#e83a3a")
    else:
        for i in range(30):
            S.rect(13 + i // 6, 14 - i, 4, 1, "#f4f4f4" if (i // 5) % 2 else "#e83a3a")
    return S


def ramp():
    """A concrete ramp climbing to the next level along the back wall, with a pipe rail and a painted UP arrow. 130x70."""
    S = Raster(130, 70)
    S.poly([(0, 69), (128, 22), (128, 30), (8, 69)], "#9ea4ae")
    S.poly([(8, 69), (128, 30), (128, 69)], "#5e646e", rim=False)
    _speckle(S, 60, 46, 60, 22, 51, "#5e646e", "#545a64", "#686e78")
    S.poly([(8, 69), (128, 30), (128, 69)], "#5e646e", rim=False)
    S.line((0, 69), (128, 22), "#c8ccd6")
    for k in range(0, 128, 16):
        S.rect(k, int(69 - k * 47 / 128) - 14, 1, 14, "#b8c0cc")
    S.line((0, 55), (128, 8), "#d8dce4"); S.line((0, 56), (128, 9), "#7c8696")
    for i in range(5):
        x = 70 + i * 2
        S.set(x, int(69 - x * 47 / 128) + 4, "#ffffff")
    tinyfont.text(S, 92, 50, "UP", "#d8dce4", 2)
    return S


def valet_stand():
    """The valet podium with a key cabinet on the wall behind it. 40x40."""
    S = Raster(40, 40)
    box(S, 4, 2, 32, 14, "#3a2a20", "#2a1a14", "#5a4030")
    for i in range(12):
        x, y = 7 + (i % 6) * 5, 5 + (i // 6) * 5
        S.rect(x, y, 2, 2, "#d8dce4"); S.set(x + 1, y + 2, "#d0243a")
    box(S, 10, 20, 20, 19, "#d0243a", "#981a2a", "#ff6a6a")
    tinyfont.text(S, 11, 25, "VALET", "#ffffff")
    S.rect(8, 18, 24, 3, "#1a1a20")
    return S


# ------------------------------------------------------------------ cars (parody models, no brands)
CAR_MODELS = {
    "hatch": ("ZIPPY HATCH", (("#8ad83a", "#5aa01e", "#c8ff8a"), ("#3ab8e8", "#1e80b0", "#9ae4ff"))),
    "sedan": ("COMMUTER LX", (("#d8343a", "#9a1e28", "#ff7a6a"), ("#b8c0cc", "#7c8696", "#e4e8f0"))),
    "van": ("FAMILY HAULER", (("#d8c8a0", "#a8987a", "#f4e8c8"), ("#7a2a4a", "#521a30", "#b45a7a"))),
    "wagon": ("WOODY WAGON", (("#e8dcb8", "#b8ac8a", "#fff4d8"), ("#2a8a8a", "#1a5a5a", "#6ad0c8"))),
}
CAR_W, CAR_H = 78, 38


def car(model="sedan", ci=0, st=0, spin=0):
    """A parked / moving car seen side-on, front to the right. Canvas 78x38, anchor (39, 37) = ground under the middle.
    st 0 = fine, 1 = dented (crease + starred windshield), 2 = wrecked (windows out, hood up, hanging bumper, flat tyre).
    Light positions are shared by every model so the game can blink them: head (73, 24), tail (3, 23), reverse (4, 26)."""
    c, s, hi = CAR_MODELS[model][1][ci]
    S = Raster(CAR_W, CAR_H)
    glass, glass_h = ("#5a7ab0", "#9ac0f0") if st < 2 else ("#1a1a24", "#e8f0ff")
    wy = 32  # wheel centre
    if model == "hatch":
        body = [(6, 33), (6, 22), (9, 19), (14, 18), (60, 20), (68, 22), (71, 25), (71, 33)]
        cab = [(8, 19), (12, 10), (44, 10), (55, 20)]
        wins = [[(12, 18), (15, 12), (28, 12), (28, 18)], [(30, 12), (43, 12), (51, 18), (30, 18)]]
        wheels = (17, 60)
    elif model == "van":
        body = [(3, 33), (3, 13), (6, 7), (50, 6), (60, 13), (70, 18), (73, 22), (74, 33)]
        cab = None
        wins = [[(6, 9), (20, 9), (20, 16), (6, 16)], [(22, 9), (40, 9), (40, 16), (22, 16)], [(42, 9), (50, 9), (58, 16), (42, 16)]]
        wheels = (16, 62)
    elif model == "wagon":
        body = [(2, 33), (2, 22), (5, 19), (64, 19), (71, 22), (73, 25), (73, 33)]
        cab = [(3, 19), (6, 10), (46, 10), (56, 19)]
        wins = [[(6, 18), (8, 12), (20, 12), (20, 18)], [(22, 12), (33, 12), (33, 18), (22, 18)], [(35, 12), (45, 12), (52, 18), (35, 18)]]
        wheels = (15, 61)
    else:  # sedan
        body = [(2, 33), (2, 23), (5, 20), (20, 19), (58, 20), (69, 21), (73, 24), (74, 33)]
        cab = [(16, 20), (24, 11), (46, 11), (56, 20)]
        wins = [[(21, 19), (26, 13), (35, 13), (35, 19)], [(37, 13), (45, 13), (51, 19), (37, 19)]]
        wheels = (16, 61)
    if cab:
        S.poly(cab, c)
    S.poly(body, c)
    # lower body shade + rocker + highlight line
    S.rect(4, 28, 69, 4, s); S.rect(3, 31, 71, 2, "#2a2c34")
    if cab:
        S.line(cab[1], cab[2], hi)
    else:
        S.line((7, 7), (49, 7), hi)
    S.line((4, 22 if model != "van" else 17), (70, 22 if model != "van" else 17), hi)
    for w in wins:
        S.poly(w, glass, rim=False)
        S.line(w[0], w[1], glass_h)
    # door seams + handles
    for x in (30, 46) if model != "van" else (21, 41):
        S.rect(x, 21 if model != "van" else 17, 1, 9 if model != "van" else 13, s)
    for x in (26, 42) if model != "van" else (36,):
        S.rect(x, 23 if model != "van" else 20, 3, 1, "#2a2c34")
    if model == "wagon":  # wood panel + roof rack
        S.rect(5, 23, 64, 5, "#9a5a2a"); S.rect(5, 23, 64, 1, "#c88a4a"); S.rect(5, 27, 64, 1, "#6a3a18")
        for x in range(10, 68, 9):
            S.rect(x, 24, 1, 3, "#7a4420")
        S.rect(8, 8, 36, 1, "#2a2c34"); S.rect(10, 7, 1, 2, "#2a2c34"); S.rect(40, 7, 1, 2, "#2a2c34")
    if model == "van":  # sliding-door track + a stick-figure family on the back glass
        S.rect(22, 18, 20, 1, "#2a2c34")
        for i, h in enumerate((6, 5, 3, 3)):
            x = 8 + i * 3
            S.rect(x, 16 - h, 1, h, "#ffffff"); S.set(x, 15 - h, "#ffffff")
    if model == "hatch":  # little rear spoiler
        S.rect(8, 9, 6, 2, s)
    # mirror, bumpers, lights, made-up badge
    S.rect(52 if model != "van" else 58, 18 if model != "van" else 14, 3, 2, s)
    S.rect(0, 29, 6, 3, "#2a2c34"); S.rect(71, 29, 7, 3, "#2a2c34"); S.rect(72, 29, 5, 1, "#c8ccd6")
    S.rect(72, 23, 4, 3, "#fff4b0" if st < 2 else "#6a6a5a"); S.rect(1, 22, 3, 3, "#e83a3a" if st < 2 else "#6a2a2a")
    S.rect(3, 26, 2, 2, "#d8dce4")
    S.set(67, 25, "#e8ecf2")
    # wheels with dark arches
    for wx in wheels:
        S.ellipse((wx, wy - 1), 7, 6, "#1a1a20", None, rim=False)
    for k, wx in enumerate(wheels):
        if st == 2 and k == 1:
            S.ellipse((wx, wy + 1), 6.5, 3.5, "#1c1c24", None, rim=True)
        else:
            _wheel(S, wx, wy, 5.2, spin + k, hub="#c8ccd6")
    if st >= 1:  # dents + a starred windshield
        S.ellipse((38, 25), 4, 2, s, None, rim=False); S.line((34, 24), (42, 27), "#2a2c34")
        w = wins[-1]
        cx, cy = (w[1][0] + w[2][0]) // 2, (w[1][1] + w[2][1]) // 2
        for dx, dy in ((-3, -2), (3, -2), (-2, 3), (3, 2), (0, -3)):
            S.line((cx, cy), (cx + dx, cy + dy), "#e8f0ff")
    if st == 2:  # hood popped, bumper hanging, scrape marks
        S.poly([(58, 20), (72, 14), (73, 16), (60, 22)], c)
        S.rect(70, 31, 8, 2, "#2a2c34"); S.line((70, 32), (77, 36), "#2a2c34")
        for x, y in ((12, 25), (50, 26), (56, 24)):
            S.rect(x, y, 4, 1, "#3a2a2a")
    return S


# ------------------------------------------------------------------ props
def cone(state=0):
    """Orange traffic cone with a white reflective band. state 1 = squashed / bent. 14x20."""
    S = Raster(14, 20)
    if state == 0:
        S.poly([(5, 2), (8, 2), (11, 16), (2, 16)], "#ff7a1a")
        S.rect(4, 8, 6, 3, "#f4f4f4"); S.line((6, 3), (4, 14), "#ffb060")
    else:
        S.poly([(3, 9), (9, 6), (11, 16), (2, 16)], "#e8641a")
        S.rect(4, 11, 6, 2, "#d8d8d8")
    box(S, 1, 16, 12, 3, "#c8500e")
    return S


def shopcart(state=0, spin=0):
    """A runaway shopping cart (wire basket, red handle, child seat flap). 36x30; state 2 = mangled."""
    S = Raster(36, 30)
    wire = "#b8c0cc" if state < 2 else "#8a94a4"
    top = 6 if state < 2 else 9
    S.poly([(3, top), (33, top), (29, 21), (7, 21)], "#00000000", rim=True) if False else None
    S.line((3, top), (33, top), wire); S.line((3, top), (7, 21), wire); S.line((33, top), (29, 21), wire); S.line((7, 21), (29, 21), wire)
    for x in range(7, 32, 4):
        S.line((x - 1, top + 1), (x + (2 if x < 18 else -2) - 1, 20), "#8a94a4")
    for y in range(top + 4, 21, 4):
        S.line((4 + (y - top) // 4, y), (32 - (y - top) // 4, y), "#8a94a4")
    S.rect(0, top - 3, 6, 3, INK); S.rect(1, top - 2, 4, 1, "#e83a3a")  # handle
    S.line((2, top - 1), (5, top + 2), wire)
    S.rect(8, 22, 22, 2, "#7c8696")  # bottom rack
    if state >= 1:
        S.line((14, top + 2), (20, top + 6), "#5a6070"); S.rect(22, top - 1, 4, 2, wire)
    for k, x in enumerate((9, 28)):
        if state == 2 and k:
            S.rect(x - 2, 26, 4, 2, "#1a1a20")
        else:
            S.rect(x - 1, 24, 2, 2, "#7c8696"); S.ellipse((x, 27), 1.8, 1.8, "#1a1a20", None, rim=True)
            S.set(x + (1 if spin % 2 else -1), 27, "#7c8696")
    return S


def paystation(state=0):
    """PAY STATION: a pay-on-foot ticket machine (screen, coin slot, ticket slot, a blue PAY HERE topper). 26x52."""
    S = Raster(26, 52)
    box(S, 3, 8, 20, 43, "#3a4a6a", "#26324a", "#5a6a8a")
    box(S, 4, 1, 18, 7, "#2a7ae8", "#1a50a8", "#7ab4ff")
    tinyfont.text(S, 7, 2, "PAY", "#ffffff")
    S.rect(6, 12, 14, 9, "#1a1a20")
    if state < 2:
        S.rect(7, 13, 12, 7, "#3ae8a0" if state == 0 else "#e8a03a"); tinyfont.text(S, 7, 14, "$$$", "#0a3a2a")
    else:
        S.line((7, 13), (18, 19), "#8a94a4"); S.line((18, 13), (8, 20), "#8a94a4")
    S.rect(7, 25, 5, 2, "#1a1a20"); S.rect(14, 24, 6, 4, "#d8dce4"); S.rect(15, 25, 4, 1, "#1a1a20")
    S.rect(7, 31, 12, 3, "#1a1a20"); S.rect(8, 32, 10, 1, "#fff8d8")  # ticket slot
    S.rect(6, 40, 14, 6, "#2a3448")
    if state >= 1:
        S.line((4, 18), (10, 30), "#1a1a20"); S.rect(22, 30, 1, 10, "#ffd02a")
    if state == 2:
        S.rect(4, 38, 18, 2, "#1a1a20"); S.rect(8, 46, 3, 3, "#ffd84a"); S.rect(14, 47, 2, 2, "#ffd84a")
    return S


def bits():
    out = {}
    S = Raster(8, 6); box(S, 1, 1, 6, 4, "#fff8d8"); S.rect(2, 2, 3, 1, "#e83a3a"); out["deb_ticket"] = S
    S = Raster(6, 6); S.ellipse((3, 3), 2, 2, "#ffd84a", "#c8a01a"); out["deb_coin"] = S
    S = Raster(8, 8); S.poly([(1, 7), (4, 1), (7, 7)], "#ff7a1a"); out["deb_cone"] = S
    S = Raster(10, 6); box(S, 1, 1, 8, 4, "#d8dce4"); S.line((2, 2), (8, 4), "#8a94a4"); out["deb_wire"] = S
    S = Raster(10, 6); box(S, 1, 1, 8, 3, "#2a2c34"); S.rect(2, 2, 6, 1, "#c8ccd6"); out["deb_bumper"] = S
    return out


def proj_coffee():
    """A to-go cup in flight (lid popping off)."""
    S = Raster(10, 12)
    box(S, 2, 3, 6, 8, "#f4f4f4"); S.rect(2, 6, 6, 2, "#8a5a2a"); S.rect(1, 1, 6, 2, "#3a3a44"); S.set(8, 1, "#c08a5a")
    return S


def proj_ticket():
    """A parking ticket, spinning (flat)."""
    S = Raster(12, 8)
    box(S, 1, 1, 10, 6, "#fff8d8"); S.rect(2, 2, 6, 1, "#e83a3a"); S.rect(2, 4, 8, 1, "#6a6a7a")
    return S


def coffee_splat():
    """A brown, slippery coffee puddle (with a floating lid)."""
    S = Raster(34, 10)
    S.ellipse((17, 5), 15, 4, "#7a4a22", None, rim=False); S.ellipse((14, 4), 9, 2.4, "#9a6232", None, rim=False)
    S.rect(9, 3, 3, 1, "#c89a6a"); S.rect(24, 5, 4, 2, "#3a3a44")
    return S


# ------------------------------------------------------------------ VINNIE THE VALET's golf cart
def _valet_cart80(state=0):
    """The valet golf cart (rider drawn between this and valet_roof()): cream body with a red stripe and VALET on the side,
    black bench seat, steering column, a rear basket of orange cones, a yellow beacon on the roof. state 0/1 = rolling,
    2 = wrecked (dented, flat tyre, steam). Canvas 88x80, anchor (44, 79). Seat top 26 px above the floor at x=36."""
    S = Raster(88, 80)
    wreck = state == 2
    c, s, hi = ("#f0ead8", "#c4bca4", "#ffffff") if not wreck else ("#c8c0a8", "#9a927a", "#e0d8c0")
    # rear posts (behind)
    S.rect(14, 22, 3, 46, "#3a3e48")
    # rear cargo basket with cones
    S.rect(2, 52, 18, 3, "#3a3e48")
    for x in (5, 12):
        S.poly([(x + 2, 40), (x + 4, 40), (x + 6, 52), (x, 52)], "#ff7a1a"); S.rect(x + 1, 46, 4, 2, "#f4f4f4")
    # body
    S.poly([(4, 70), (4, 56), (12, 54), (24, 54), (28, 60), (58, 60), (62, 52), (76, 52), (84, 58), (85, 70)], c)
    S.rect(5, 63, 79, 3, "#d0243a"); S.rect(5, 66, 79, 1, "#981a2a")
    S.line((13, 55), (24, 55), hi); S.line((62, 53), (76, 53), hi)
    S.rect(4, 68, 81, 2, s)
    # floorboard + seat + seat back
    S.rect(26, 58, 34, 3, "#2a2c34")
    S.rect(20, 46, 26, 6, INK); S.rect(21, 47, 24, 4, "#1c1c24"); S.rect(21, 47, 24, 1, "#3a3a44")
    S.rect(18, 30, 6, 18, INK); S.rect(19, 31, 4, 16, "#1c1c24"); S.rect(19, 31, 1, 16, "#3a3a44")
    S.rect(24, 52, 20, 2, "#3a3e48")
    # steering column + wheel
    S.line((66, 54), (58, 38), "#3a3e48"); S.line((67, 54), (59, 38), "#5a5e6a")
    S.rect(54, 36, 9, 3, INK); S.rect(55, 37, 7, 1, "#5a5e6a")
    # head light + bumper
    S.rect(81, 57, 3, 3, "#fff4b0" if not wreck else "#6a6a5a"); S.rect(84, 66, 4, 3, "#2a2c34")
    S.rect(1, 58, 3, 3, "#e83a3a")
    # wheels
    _wheel(S, 18, 72, 6.5, state, hub="#e8ecf2")
    if not wreck:
        _wheel(S, 70, 72, 6.5, state + 1, hub="#e8ecf2")
    else:
        S.ellipse((70, 74), 7, 4, "#1c1c24", None, rim=True)
        for x, y in ((40, 64), (52, 62), (74, 60)):
            S.rect(x, y, 4, 1, "#3a2a2a")
    return S


CART_LIFT = 14  # v0.11: the canopy sits this much higher than first drawn, so Vinnie's cap clears it


def valet_cart(state=0, left=False):
    """The cart body on the tall canvas (88x94, anchor (44, 93)); left=True is the mirrored cart with VALET still readable."""
    S0 = _valet_cart80(state)
    S = Raster(88, 80 + CART_LIFT)
    for y in range(S0.h):
        for x in range(S0.w):
            if S0.p[y][x]:
                S.set(x, y + CART_LIFT, S0.p[y][x])
    S.rect(14, 22 + CART_LIFT - 2, 3, 2, "#3a3e48")
    if left:
        S.mirror()
    tinyfont.text(S, 7 if left else 62, 56 + CART_LIFT, "VALET", "#d0243a" if state < 2 else "#9a2a3a")
    return S


def valet_roof(state=0):
    """Canopy + front posts of the golf cart, drawn over the rider. Same canvas / anchor as valet_cart (88x94, (44, 93))."""
    S = Raster(88, 80 + CART_LIFT)
    wreck = state == 2
    S.rect(72, 10, 3, 44 + CART_LIFT, "#3a3e48")
    S.rect(14, 22, 3, 2 + CART_LIFT, "#3a3e48")
    if not wreck:
        S.poly([(8, 12), (80, 8), (82, 12), (10, 16)], "#f0ead8"); S.line((10, 15), (81, 11), "#c4bca4")
        S.rect(40, 6, 6, 4, INK); S.rect(41, 7, 4, 2, "#ffd02a")
    else:
        S.poly([(8, 16), (78, 6), (80, 10), (10, 20)], "#c8c0a8")
        S.rect(40, 9, 6, 3, "#5a4a1a")
    S.line((15, 22), (12, 15), "#3a3e48")
    return S
