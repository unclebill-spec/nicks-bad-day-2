"""v0.3 kickable / breakable floor props (all original, drawn in code) + chunky debris bits.

Every prop has 3 states (0 intact, 1 banged up, 2 wrecked) except the wet-floor sign (0, 1).
Side / three-quarter view to match the hallway, 1px ink rim, short palettes.
"""
from __future__ import annotations

from rig import INK, Raster
import tinyfont

STEEL, STEEL_S, STEEL_H = "#b8c0cc", "#7c8696", "#e4e8f0"
RED, RED_S, RED_H = "#d8303c", "#a01c28", "#ff6a74"
TIRE, HUB = "#2a2e3a", "#9aa4b4"


def box(S, x, y, w, h, c, s=None, hi=None, rim=True):
    if rim:
        S.rect(x - 1, y - 1, w + 2, h + 2, INK)
    S.rect(x, y, w, h, c)
    if hi:
        S.rect(x, y, w, 1, hi)
    if s:
        S.rect(x, y + h - 1, w, 1, s)
        S.rect(x + w - 1, y, 1, h, s)


def caster(S, x, y, r=2):
    S.ellipse((x, y), r, r, TIRE); S.set(int(x), int(y), HUB)


# ------------------------------------------------------------------ crash cart (the star of the show)
def crash_cart(state):
    S = Raster(38, 44)
    if state < 2:
        lean = 0
        # push handle (left) + O2 tank strapped on the right
        S.rect(3, 12, 2, 16, STEEL_S); S.rect(3, 12, 4, 2, STEEL_S)
        box(S, 32, 14, 4, 16, "#3aa860", "#267a44", "#7ad89a"); S.rect(32, 12, 4, 2, STEEL)
        # cabinet
        box(S, 6, 14, 26, 24, RED if state == 0 else "#c42a36", RED_S, RED_H)
        for i, y in enumerate((19, 24, 29, 34)):
            S.rect(7, y, 24, 1, RED_S)
            S.rect(16, y - 3, 6, 1, "#ffd84a" if i % 2 == 0 else STEEL_H)
        # top tray + defib monitor with ECG trace
        S.rect(5, 12, 28, 3, STEEL); S.rect(5, 12, 28, 1, STEEL_H)
        box(S, 9, 3, 15, 9, "#3a3e4a", "#22262e", "#5a6070")
        S.rect(11, 5, 9, 5, "#0e2a1a")
        for x, y in ((11, 8), (12, 8), (13, 7), (14, 5), (15, 9), (16, 7), (17, 8), (18, 8), (19, 8)):
            S.set(x, y, "#5aff8a")
        S.rect(21, 5, 2, 2, "#ff5a3a"); S.rect(21, 8, 2, 2, "#ffd84a")
        S.ellipse((28, 9), 2.5, 2, "#ffd84a", "#c8a020")  # paddle
        S.rect(4, 38, 30, 2, STEEL_S)
        for x in (8, 15, 23, 30):
            caster(S, x, 41)
        if state == 1:  # dents, cracked screen, the top drawer hanging open with supplies
            S.line((8, 22), (12, 30), INK); S.line((26, 26), (29, 34), INK); S.line((22, 16), (24, 21), "#ff9aa0")
            S.line((12, 5), (17, 9), "#e4f4ff")
            box(S, 1, 16, 12, 4, RED_S, "#701420", RED)
            S.rect(2, 14, 3, 2, "#ffffff"); S.rect(6, 14, 2, 2, "#ff9a3a"); S.rect(9, 15, 3, 1, "#7ac8ff")
            S.rect(16, 29, 6, 1, RED_S)
    else:
        # crumpled cabinet on its side, monitor face-down, a drawer and a loose wheel
        S.poly([(3, 40), (8, 28), (26, 26), (34, 40)], RED_S)
        S.poly([(6, 38), (10, 30), (24, 29), (30, 38)], RED)
        S.line((12, 31), (16, 37), INK); S.line((20, 30), (22, 36), INK)
        box(S, 20, 22, 12, 6, "#3a3e4a", "#22262e"); S.line((22, 24), (28, 26), "#5aff8a")
        box(S, 2, 36, 9, 3, RED_S); S.rect(5, 36, 3, 1, "#ffd84a")
        S.rect(4, 41, 30, 1, STEEL_S); caster(S, 33, 41); caster(S, 9, 41)
        S.rect(14, 39, 3, 2, "#ffffff"); S.rect(25, 40, 2, 1, "#ff9a3a")
    return S


# ------------------------------------------------------------------ steel supply cart with boxes
def supply_cart(state):
    S = Raster(34, 40)
    BOX, BOX_S = "#c8a070", "#9a7448"
    if state < 2:
        for x in (4, 29):
            S.rect(x, 4, 2, 31, STEEL_S); S.rect(x, 4, 1, 31, STEEL_H)
        for y in (13, 23, 33):
            S.rect(3, y, 28, 2, STEEL); S.rect(3, y, 28, 1, STEEL_H)
        if state == 0:
            box(S, 7, 5, 9, 8, BOX, BOX_S); box(S, 18, 7, 9, 6, "#4a8ad8", "#2a64a8"); S.rect(20, 9, 5, 1, "#ffffff")
            box(S, 7, 16, 12, 7, "#f4f4f8", "#c8ccd6"); S.rect(9, 18, 8, 1, "#7ac8ff"); box(S, 21, 17, 6, 6, BOX, BOX_S)
            box(S, 8, 27, 18, 6, "#8ad8a0", "#5aa870"); tinyfont.text(S, 10, 28, "GLV", "#ffffff")
        else:
            box(S, 9, 7, 9, 6, BOX, BOX_S); S.poly([(18, 13), (24, 6), (29, 11)], "#4a8ad8")
            box(S, 6, 18, 12, 5, "#f4f4f8", "#c8ccd6"); S.line((20, 23), (30, 21), STEEL_S)
            box(S, 12, 28, 10, 5, "#8ad8a0", "#5aa870")
            S.line((5, 20), (10, 25), INK)
        S.rect(3, 35, 28, 1, STEEL_S)
        for x in (6, 28):
            caster(S, x, 37)
    else:
        S.line((3, 36), (31, 28), STEEL_S); S.line((3, 37), (31, 33), STEEL); S.line((6, 38), (14, 26), STEEL_S)
        box(S, 4, 30, 9, 6, "#c8a070", "#9a7448"); box(S, 18, 32, 8, 5, "#4a8ad8", "#2a64a8"); box(S, 12, 34, 8, 4, "#f4f4f8", "#c8ccd6")
        caster(S, 29, 37); caster(S, 5, 38)
    return S


# ------------------------------------------------------------------ single waiting-room chair (side view)
def chair(state):
    S = Raster(22, 28)
    B, BS, BH = "#5a8ad8", "#3a64a8", "#8ab4f0"
    if state < 2:
        if state == 0:
            box(S, 3, 2, 4, 15, B, BS, BH)            # back
        else:
            S.poly([(1, 4), (5, 2), (8, 16), (5, 17)], B); S.line((3, 6), (6, 12), INK)
        box(S, 3, 15, 15, 4, B, BS, BH)              # seat
        S.rect(5, 19, 1, 7, STEEL_S); S.rect(15, 19, 1, 7, STEEL_S); S.rect(4, 25, 13, 1, STEEL_S)
        S.rect(16, 11, 4, 1, STEEL_S); S.rect(19, 11, 1, 5, STEEL_S)  # arm rest
    else:
        box(S, 2, 22, 14, 3, B, BS, BH); S.poly([(12, 20), (19, 14), (21, 17), (15, 22)], B)
        S.line((3, 26), (9, 20), STEEL_S); S.line((14, 26), (20, 22), STEEL_S); S.rect(1, 26, 18, 1, STEEL_S)
    return S


# ------------------------------------------------------------------ trash can (swing lid)
def trash_can(state):
    S = Raster(26, 26)
    G1, G2, G3 = "#8a94a4", "#5c6676", "#b8c0cc"
    if state < 2:
        box(S, 6, 6, 13, 18, G1, G2, G3)
        for x in (9, 13):
            S.rect(x, 8, 1, 14, G2)
        if state == 0:
            box(S, 5, 2, 15, 4, G3, G2, "#e4e8f0"); S.rect(10, 3, 5, 1, G2)
        else:
            S.poly([(4, 1), (18, -0.5), (20, 3), (5, 5)], G3); S.line((7, 12), (11, 18), INK); S.line((15, 10), (17, 15), INK)
            S.rect(9, 5, 3, 2, "#f4f4f8"); S.rect(13, 5, 2, 1, "#ffd84a")
    else:
        S.poly([(2, 16), (17, 13), (19, 23), (4, 25)], G1); S.ellipse((19, 18), 3, 5, G2)
        S.rect(6, 17, 9, 1, G2)
        for x, y, c in ((21, 22, "#f4f4f8"), (23, 20, "#ffd84a"), (24, 23, "#e84a5a"), (19, 24, "#c8a070")):
            S.rect(x, y, 2, 2, c)
    return S


# ------------------------------------------------------------------ wheelchair (rolls far)
def wheelchair(state):
    S = Raster(32, 32)
    F = "#2a5aa8"
    if state < 2:
        if state == 0:
            S.ellipse((11, 21), 9, 9, TIRE); S.ellipse((11, 21), 7, 7, HUB); S.ellipse((11, 21), 2, 2, TIRE)
            S.line((11, 14), (11, 28), "#c8ccd6"); S.line((4, 21), (18, 21), "#c8ccd6")
        else:
            S.ellipse((11, 21), 9, 7, TIRE); S.ellipse((11, 21), 7, 5, HUB); S.ellipse((11, 21), 2, 2, TIRE)
        box(S, 7, 13, 15, 3, F, "#1a3a78", "#4a7ac8")      # seat
        box(S, 5, 2, 3, 13, F, "#1a3a78")                  # back
        S.rect(4, 0, 3, 2, TIRE)                            # push grip
        S.line((20, 16), (26, 27), STEEL_S); S.rect(24, 27, 5, 1, STEEL_S)  # footrest
        S.ellipse((26, 29), 2, 2, TIRE)
        if state == 1:
            S.line((6, 4), (7, 11), "#e4e8f0"); S.line((12, 13), (18, 15), INK)
    else:
        S.ellipse((8, 26), 7, 4, TIRE); S.ellipse((8, 26), 5, 2, HUB)
        box(S, 12, 24, 14, 3, "#2a5aa8", "#1a3a78"); S.line((14, 23), (22, 14), "#2a5aa8"); S.line((15, 23), (23, 15), INK)
        S.line((24, 28), (30, 26), STEEL_S); S.ellipse((28, 29), 2, 2, TIRE)
    return S


# ------------------------------------------------------------------ CAUTION wet-floor A-frame sign
def wet_floor(state):
    S = Raster(20, 28)
    Y, YS = "#ffd84a", "#d8a820"
    if state == 0:
        S.poly([(10, 1), (17, 26), (3, 26)], Y); S.line((10, 1), (17, 26), YS)
        S.rect(5, 9, 10, 3, INK)
        S.rect(6, 10, 8, 1, Y)
        # slipping stick figure
        S.set(10, 14, INK); S.line((10, 15), (9, 19), INK); S.line((9, 19), (6, 22), INK); S.line((9, 19), (12, 22), INK); S.line((10, 16), (13, 15), INK); S.line((10, 16), (7, 17), INK)
        S.rect(5, 23, 4, 1, "#7ac8ff")
    else:
        S.poly([(1, 24), (17, 21), (19, 25), (3, 27)], Y); S.line((5, 24), (14, 22), INK)
        S.poly([(12, 18), (18, 13), (19, 16), (14, 20)], YS)
    return S


# ------------------------------------------------------------------ potted plant wreck (states 0/1 come from the brileta plants)
def plant_wreck():
    S = Raster(28, 18)
    S.ellipse((14, 14), 12, 3, "#5a3a24", rim=False)
    S.poly([(3, 15), (8, 9), (11, 15)], "#c86a3a"); S.poly([(16, 16), (21, 10), (25, 15)], "#e88a5a"); S.poly([(10, 16), (13, 12), (16, 16)], "#9a4a24")
    S.ellipse((19, 6), 5, 3, "#3a8a3a", "#226a2a"); S.ellipse((12, 8), 3, 2, "#5ab04a"); S.line((14, 10), (18, 7), "#5a3a24")
    return S


def crack_pot(im):
    """State 1 for a brileta plant: add ink cracks + a chip to the clay pot (bottom 12 rows)."""
    from PIL import ImageDraw
    im = im.copy(); d = ImageDraw.Draw(im); w, h = im.size
    ink = (26, 16, 32, 255)
    d.line([(w // 2 - 3, h - 11), (w // 2 - 1, h - 7), (w // 2 - 3, h - 4)], fill=ink)
    d.line([(w // 2 + 3, h - 10), (w // 2 + 4, h - 6)], fill=ink)
    d.rectangle([w // 2 + 4, h - 12, w // 2 + 5, h - 11], fill=(0, 0, 0, 0))
    return im


# ------------------------------------------------------------------ debris bits (chunky, flung by breaks)
def bits():
    out = {}
    S = Raster(10, 6); box(S, 1, 1, 8, 4, RED, RED_S, RED_H); S.rect(4, 2, 3, 1, "#ffd84a"); out["deb_drawer"] = S
    S = Raster(6, 6); S.ellipse((3, 3), 2, 2, TIRE); S.set(3, 3, HUB); out["deb_wheel"] = S
    S = Raster(6, 5); box(S, 1, 1, 4, 3, "#ffffff", "#c8ccd6"); out["deb_gauze"] = S
    S = Raster(4, 6); box(S, 1, 2, 2, 3, "#ff9a3a", "#c86a1a"); S.rect(1, 1, 2, 1, "#ffffff"); out["deb_pill"] = S
    S = Raster(8, 3); S.rect(0, 1, 5, 1, "#e4f4ff"); S.rect(5, 1, 2, 1, "#ff9a3a"); S.set(7, 1, STEEL_S); out["deb_syringe"] = S
    S = Raster(6, 6); box(S, 1, 1, 4, 4, "#c8a070", "#9a7448"); out["deb_box"] = S
    S = Raster(6, 5); box(S, 1, 1, 4, 3, "#8ad8a0", "#5aa870"); out["deb_glove"] = S
    S = Raster(6, 5); S.poly([(1, 4), (3, 1), (5, 4)], "#c86a3a"); out["deb_shard"] = S
    S = Raster(6, 5); S.ellipse((3, 2.5), 2, 1.5, "#3a8a3a"); out["deb_leaf"] = S
    S = Raster(6, 5); box(S, 1, 1, 4, 3, "#f4f4f8", "#c8ccd6"); S.set(2, 2, "#8a94a4"); out["deb_paper"] = S
    S = Raster(5, 6); box(S, 1, 1, 3, 4, "#e84a5a", "#a82838"); S.rect(1, 1, 3, 1, STEEL_H); out["deb_can"] = S
    S = Raster(8, 5); box(S, 1, 1, 6, 3, "#f4f6fa", "#c8ccd6"); out["deb_linen"] = S
    S = Raster(7, 4); S.rect(0, 1, 7, 2, STEEL); S.rect(0, 1, 7, 1, STEEL_H); out["deb_rod"] = S
    S = Raster(6, 6); S.poly([(1, 5), (3, 1), (5, 5)], "#ffd84a"); out["deb_sign"] = S
    S = Raster(6, 5); box(S, 1, 1, 4, 3, "#5a8ad8", "#3a64a8"); out["deb_seat"] = S
    S = Raster(5, 5); box(S, 1, 1, 3, 3, "#cfe8ff", "#9ac4f0"); out["deb_glass"] = S
    return out


# ================================================================== v0.4
def gurney(state):
    """Rideable stretcher: white mattress + blue sheet on a steel frame, side rail, pillow, 3 casters."""
    S = Raster(60, 32)
    if state < 2:
        tilt = 0 if state == 0 else 1
        S.rect(4, 15, 52, 2, STEEL_S); S.rect(4, 15, 52, 1, STEEL)                     # frame
        box(S, 5, 10 + tilt, 50, 5, "#f4f6fa", "#c8ccd6", "#ffffff")                    # mattress
        box(S, 20, 9 + tilt, 34, 4, "#7ab0e8", "#4a7ac8", "#a8d0ff")                    # sheet
        box(S, 6, 7, 11, 4, "#ffffff", "#d8dce4")                                       # pillow
        S.rect(22, 5, 30, 1, STEEL_S); S.rect(22, 5, 1, 5, STEEL_S); S.rect(51, 5, 1, 5, STEEL_S)  # side rail
        for x in (10, 30, 50):
            S.rect(x, 17, 2, 9, STEEL); caster(S, x + 1, 28)
        S.rect(2, 4, 2, 12, STEEL_S); S.rect(1, 3, 4, 2, TIRE)                         # push handle
        if state == 1:
            S.line((26, 5), (34, 8), INK); S.line((40, 11), (46, 13), INK); S.rect(52, 6, 3, 1, STEEL_S)
    else:
        S.poly([(4, 24), (30, 20), (34, 27), (6, 29)], "#f4f6fa"); S.poly([(28, 26), (52, 22), (56, 28), (30, 30)], "#7ab0e8")
        S.line((4, 30), (40, 26), STEEL_S); S.line((30, 30), (56, 30), STEEL); caster(S, 54, 29); caster(S, 12, 30)
        box(S, 40, 16, 9, 4, "#ffffff", "#d8dce4")
    return S


def o2_tank(state):
    """Loose oxygen tank on its little dolly (knocked off an O2 Wanderer): kickable, rolls."""
    S = Raster(20, 32)
    if state < 2:
        S.capsule((9, 6), (9, 24), 7, "#3aa860" if state == 0 else "#2e9452", "#267a44"); S.rect(8, 1, 3, 4, "#b8c0cc"); S.rect(6, 3, 7, 1, STEEL_S)
        S.rect(6, 13, 7, 2, "#ffffff"); S.rect(7, 13, 1, 2, "#3aa860")
        S.line((3, 29), (16, 29), STEEL_S); caster(S, 5, 29); caster(S, 14, 29); S.line((16, 29), (18, 18), STEEL_S)
        if state == 1:
            S.line((7, 18), (11, 22), INK); S.set(10, 2, "#e4f4ff")
    else:
        S.capsule((3, 26), (16, 23), 6, "#2e9452", "#267a44"); S.rect(16, 21, 3, 3, "#b8c0cc"); caster(S, 6, 30)
    return S


def proj_tray():
    S = Raster(20, 9)
    S.rect(1, 4, 18, 3, INK); S.rect(2, 5, 16, 1, "#c8a070")
    S.ellipse((6, 4), 3, 1.2, "#f4f4f8", rim=False); S.rect(5, 3, 3, 1, "#c86a3a")
    S.rect(10, 1, 3, 3, "#5ad85a"); S.rect(14, 0, 3, 4, "#f4f4f8"); S.rect(14, 2, 3, 1, "#4a8ad8")
    return S


def proj_jello():
    S = Raster(10, 10)
    S.rect(1, 2, 8, 7, INK); S.rect(2, 3, 6, 5, "#5ad85a"); S.rect(2, 3, 2, 2, "#bfffbf"); S.rect(2, 7, 6, 1, "#38a838")
    return S


def jello_splat():
    S = Raster(28, 8)
    S.ellipse((14, 4), 12, 3, "#5ad85a", "#38a838", rim=False)
    S.rect(5, 3, 3, 2, "#2a8a2a"); S.rect(18, 2, 4, 2, "#bfffbf"); S.rect(11, 5, 2, 1, "#2a8a2a")
    return S


# ---- breakroom (bonus round) background pieces
def fridge(open_=False):
    S = Raster(36, 72)
    box(S, 2, 2, 32, 68, "#eef0f4", "#b8c0cc", "#ffffff")
    S.rect(3, 24, 30, 1, "#b8c0cc")
    S.rect(28, 8, 2, 12, STEEL_S); S.rect(28, 30, 2, 18, STEEL_S)
    for x, y, c in ((7, 8, "#ff5a5a"), (12, 11, "#ffd84a"), (8, 34, "#4a8ad8"), (16, 40, "#5ad85a")):
        S.rect(x, y, 3, 3, c)
    box(S, 9, 46, 14, 10, "#fff7b0", "#e0d080"); tinyfont.text(S, 10, 48, "LBL", "#c82a2a")
    if open_:
        S.rect(3, 25, 30, 44, "#cfe8ff"); S.rect(5, 38, 26, 1, STEEL); S.rect(5, 52, 26, 1, STEEL)
        S.rect(7, 30, 6, 7, "#ffd84a"); S.rect(16, 32, 5, 5, "#e84a5a"); S.rect(8, 44, 8, 7, "#c8a070"); S.rect(20, 45, 6, 6, "#5ad85a")
    return S


def counter():
    S = Raster(120, 40)
    box(S, 2, 12, 116, 26, "#b07a4a", "#8a5a30", "#d09a68")
    for x in (4, 34, 64, 94):
        S.rect(x, 18, 26, 18, "#9a6a3a"); S.rect(x + 22, 25, 2, 4, "#e4e8f0")
    S.rect(1, 10, 118, 3, "#d8d0c0"); S.rect(1, 10, 118, 1, "#f4ecdc")
    box(S, 8, 0, 24, 10, "#3a3e4a", "#22262e", "#5a6070"); S.rect(10, 2, 14, 6, "#1a1a22"); S.rect(26, 3, 4, 1, "#5aff8a"); S.rect(26, 6, 4, 1, "#e4e8f0")  # microwave
    box(S, 44, 2, 10, 8, "#2a2a32", "#14141a"); S.rect(45, 6, 8, 3, "#5a3a20"); S.rect(52, 3, 1, 1, "#ff3a3a")   # coffee maker
    S.rect(66, 8, 18, 2, STEEL); S.rect(76, 4, 1, 4, STEEL_S)  # sink
    for i, c in enumerate(("#ff8a1e", "#4a8ad8", "#ffd84a")):
        box(S, 92 + i * 7, 4, 4, 6, c)   # mugs
    return S


def cabinets():
    S = Raster(120, 22)
    for i in range(4):
        box(S, 2 + i * 29, 2, 27, 18, "#c08a58", "#8e5e36", "#dcae7c"); S.rect(2 + i * 29 + 22, 9, 2, 4, "#e4e8f0")
    return S


def table():
    S = Raster(64, 30)
    box(S, 8, 8, 48, 4, "#e4e8f0", "#b8c0cc", "#ffffff"); S.rect(30, 12, 4, 15, STEEL_S); S.rect(22, 26, 20, 2, STEEL_S)
    for x in (2, 52):
        box(S, x, 4, 4, 12, "#e84a5a", "#a82838"); box(S, x, 15, 10 if x == 2 else 10, 3, "#e84a5a", "#a82838"); S.rect(x + 1, 18, 1, 9, STEEL_S)
    S.rect(16, 5, 6, 3, "#ffffff"); S.rect(40, 4, 5, 4, "#8a5a2a")   # napkin, coffee cup
    return S


def food_note():
    S = Raster(34, 22)
    box(S, 2, 2, 30, 18, "#fff7b0", "#e0d080")
    tinyfont.text(S, 4, 4, "LABEL", "#c82a2a"); tinyfont.text(S, 4, 11, "FOOD!", "#2a2a32")
    S.rect(16, 0, 2, 3, "#e84a5a")
    return S
