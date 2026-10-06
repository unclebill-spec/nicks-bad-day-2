"""v0.9 sprites for the SCOOTER RUN driving level: the nurses' mobility scooters, the jumpable floor junk (a knocked-over
trash can, a mop bucket), and Motorcart Marv's souped-up hot-rod scooter. All side view, facing right (the game flips).
Marv himself is a normal rig character (chars.marv_body / chars.marv_anims), sized by Bill's boss rule: modestly bigger
than a nurse (his cart + him ~1.2-1.3x a nurse's height)."""
from __future__ import annotations

from rig import INK, Raster

SCOOT_COLS = {"red": ("#d8343a", "#9a1e28", "#ff7a6a"), "blue": ("#2f74d8", "#1c4a9a", "#7ab4ff")}


def _wheel(S, cx, cy, r, spin, tyre="#1c1c24", hub="#b4bcc8"):
    S.ellipse((cx, cy), r, r, tyre, None, rim=True)
    S.ellipse((cx, cy), max(1.2, r * 0.45), max(1.2, r * 0.45), hub, None, rim=False)
    # a spoke highlight that hops between two spots so the wheel reads as rolling
    dx, dy = ((1, -1), (-1, 1))[spin % 2]
    S.set(int(cx + dx * r * 0.62), int(cy + dy * r * 0.62), "#6a6e7a")
    S.set(int(cx - dy * r * 0.62), int(cy + dx * r * 0.62), "#6a6e7a")


def scooter(color="red", spin=0):
    """A hospital mobility scooter: rear shroud, low footboard, front shroud with a headlight, raked tiller with a
    wire basket (a sharps box of Ativan syringes in it), black seat + backrest, and the classic orange safety flag.
    Canvas 50x44. Anchor (22, 43) = floor under the seat; the seat top is 17 px above the floor."""
    c, s, hi = SCOOT_COLS[color]
    S = Raster(50, 44)
    # safety flag on a whip behind the seat
    S.line((4, 30), (4, 2), "#d8dce4"); S.poly([(5, 2), (13, 5), (5, 8)], "#ff8a1e")
    S.set(7, 4, "#ffc04a"); S.set(6, 5, "#ffc04a")
    # rear wheel + shroud
    _wheel(S, 11, 39, 4.2, spin)
    S.poly([(2, 38), (3, 31), (8, 28.5), (20, 28.5), (21, 38)], c)
    S.rect(3, 31, 17, 1, hi); S.rect(3, 36, 18, 2, s)
    S.rect(2, 33, 2, 2, "#ff5a2a")                                         # tail reflector
    # footboard / deck
    S.rect(17, 34, 23, 5, INK); S.rect(18, 35, 21, 3, "#4a4e5a"); S.rect(18, 35, 21, 1, "#6a6e7a")
    # front wheel + shroud with headlight
    _wheel(S, 41, 39, 4.2, spin + 1)
    S.poly([(34, 38), (35, 30), (40, 27), (46, 28), (48, 33), (47, 38)], c)
    S.rect(37, 29, 8, 1, hi); S.rect(35, 36, 12, 2, s)
    S.rect(45, 30, 2, 3, "#fff4b0"); S.set(47, 31, "#ffffff")
    # seat post, cushion, backrest, armrest
    S.rect(13, 25, 4, 5, INK); S.rect(14, 25, 2, 5, "#7c8696")
    S.rect(5, 23, 18, 4, INK); S.rect(6, 24, 16, 2, "#2a2c34"); S.rect(6, 24, 16, 1, "#4a4c58")
    S.rect(4, 12, 5, 13, INK); S.rect(5, 13, 3, 11, "#2a2c34"); S.rect(5, 13, 1, 11, "#4a4c58")
    S.rect(17, 20, 6, 2, INK); S.rect(18, 20, 4, 1, "#5a5e6a")
    # tiller column raked back towards the rider, handlebar + grips
    S.capsule((38, 29), (33, 13), 2.0, "#5a5e6a", "#3a3e4a")
    S.rect(29, 11, 9, 3, INK); S.rect(30, 12, 7, 1, "#9aa4b4"); S.rect(29, 12, 2, 1, "#1c1c24")
    # wire basket on the front of the tiller with a red sharps box of syringes
    S.rect(37, 15, 9, 7, INK); S.rect(38, 16, 7, 5, "#c8ccd6")
    for x in (40, 42): S.rect(x, 16, 1, 5, "#8a94a4")
    S.rect(39, 13, 5, 3, "#e83a3a"); S.rect(39, 13, 5, 1, "#ff8a8a"); S.set(41, 12, "#ffe84a")
    return S


def tipped_can(lid=True):
    """A grey hospital trash can knocked over on its side, trash spilling out of the open end: lies on the floor,
    12 px tall, so a scooter can JUMP it. Canvas 34x16, anchor (17, 15)."""
    S = Raster(34, 16)
    S.rect(3, 3, 20, 11, INK); S.rect(4, 4, 18, 9, "#8a94a4"); S.rect(4, 4, 18, 2, "#b4bcc8"); S.rect(4, 11, 18, 2, "#6a7484")
    for x in (8, 13, 18): S.rect(x, 4, 1, 9, "#6a7484")
    S.ellipse((23, 8.5), 2.6, 5.4, "#2a2c34", None, rim=True)                    # the open mouth
    # spilled trash: paper ball, crumpled cup, banana peel, a tin can
    S.ellipse((27, 12), 2.2, 2, "#f4f4f4", None, rim=True)
    S.rect(29, 9, 3, 4, INK); S.rect(30, 10, 1, 2, "#e83a3a")
    S.poly([(24, 14), (26, 12), (28, 14.5)], "#ffe84a")
    S.rect(31, 13, 2, 2, "#c8ccd6")
    if lid: S.rect(0, 12, 6, 3, INK); S.rect(1, 13, 4, 1, "#9aa4b4")
    return S


def mop_bucket():
    """A yellow janitor's mop bucket with its wringer, the mop lying across it. 16 px tall: jumpable.
    Canvas 34x20, anchor (16, 19)."""
    S = Raster(34, 20)
    S.rect(5, 7, 18, 10, INK); S.rect(6, 8, 16, 8, "#ffcf2a"); S.rect(6, 8, 16, 1, "#fff08a"); S.rect(6, 14, 16, 2, "#d8a010")
    S.rect(8, 10, 10, 2, "#1a1020"); S.rect(9, 10, 8, 1, "#e8ecf2")                # little "CAUTION" label stripe
    S.rect(15, 3, 7, 5, INK); S.rect(16, 4, 5, 3, "#7c8696"); S.rect(16, 4, 5, 1, "#b4bcc8")   # wringer
    for x in (8, 19): S.ellipse((x, 18), 1.6, 1.6, "#1c1c24", None, rim=True)
    S.line((0, 6), (30, 2), "#c8925a"); S.line((0, 7), (30, 3), "#8a5a2a")         # mop handle
    S.ellipse((30.5, 5), 3, 2.6, "#d8dce4", None, rim=True)
    for i in range(4): S.set(28 + i, 7 + (i % 2), "#b4bcc8")
    return S


def marv_cart(state=0):
    """Motorcart Marv's souped-up mobility scooter: candy-red with flame decals, chrome twin exhausts, a fat rear
    tyre, a rear spoiler, twin headlights, bull-horn handlebars, a bike horn and a checkered whip flag.
    state 0/1 = rolling (wheel + exhaust flicker), 2 = wrecked (scuffed, flat front tyre, bent spoiler).
    Canvas 84x50, anchor (34, 49) = floor under the seat; the raised racing seat's top is 27 px above the floor."""
    S = Raster(84, 50)
    wreck = state == 2
    c, s, hi = ("#e8243a", "#9a1426", "#ff7a7a") if not wreck else ("#a8323a", "#6a1a22", "#c86a6a")
    # whip flag (checkered)
    S.line((6, 30), (6, 1), "#d8dce4")
    for i in range(3):
        for j in range(2): S.rect(7 + i * 3, 1 + j * 3, 3, 3, "#f4f4f4" if (i + j) % 2 == 0 else "#1a1020")
    # spoiler on struts
    if not wreck: S.rect(1, 20, 18, 4, INK); S.rect(2, 21, 16, 2, c); S.rect(2, 21, 16, 1, hi)
    else: S.poly([(1, 25), (17, 19), (18, 22), (2, 27)], c)
    S.rect(5, 24, 2, 6, "#7c8696"); S.rect(14, 24, 2, 6, "#7c8696")
    # chrome twin exhausts out the back
    S.rect(0, 37, 12, 3, INK); S.rect(1, 38, 10, 1, "#d8dce4"); S.rect(0, 41, 10, 3, INK); S.rect(1, 42, 8, 1, "#b4bcc8")
    if not wreck and state == 1: S.rect(0, 37, 1, 3, "#ffb020"); S.rect(0, 41, 1, 3, "#ff6a1a")
    # fat rear tyre
    _wheel(S, 18, 43, 6.5, state, hub="#e8ecf2")
    # long low body
    S.poly([(3, 44), (4, 33), (12, 29), (30, 29), (36, 34), (62, 34), (70, 30), (78, 32), (81, 38), (80, 44)], c)
    S.rect(5, 33, 25, 1, hi); S.rect(36, 35, 26, 1, hi)
    S.rect(4, 42, 76, 2, s)
    if not wreck:  # flame decals licking back along the side
        for k, x0 in enumerate((44, 54, 64)):
            S.poly([(x0 + 10, 37), (x0, 36), (x0 - 7, 38), (x0, 39), (x0 + 10, 40)], "#ffb020", rim=False)
            S.poly([(x0 + 10, 37.5), (x0 + 2, 37.4), (x0 - 3, 38.2), (x0 + 2, 39), (x0 + 10, 39.5)], "#ffe84a", rim=False)
    else:
        for x, y in ((40, 37), (52, 39), (66, 36)): S.rect(x, y, 3, 1, "#3a2a2a")
    # footboard
    S.rect(30, 38, 34, 3, "#2a2c34")
    # front fairing: twin headlights + chrome bumper
    S.rect(78, 34, 3, 2, "#fff4b0" if not wreck else "#6a6a5a"); S.rect(78, 37, 3, 2, "#fff4b0" if not wreck else "#5a5a4a")
    S.rect(80, 41, 4, 2, INK); S.rect(81, 41, 2, 1, "#d8dce4")
    # front wheel
    if not wreck: _wheel(S, 70, 44, 4.6, state + 1, hub="#e8ecf2")
    else: S.ellipse((70, 46), 5.2, 3, "#1c1c24", None, rim=True)
    # seat post + racing seat with a tall back
    S.rect(30, 24, 5, 10, INK); S.rect(31, 24, 3, 10, "#7c8696")
    S.rect(21, 20, 22, 5, INK); S.rect(22, 21, 20, 3, "#2a2c34"); S.rect(22, 21, 20, 1, "#4a4c58")
    S.rect(19, 3, 6, 19, INK); S.rect(20, 4, 4, 17, "#2a2c34"); S.rect(20, 4, 1, 17, "#4a4c58"); S.rect(20, 7, 4, 2, c)
    # tiller with bull-horn handlebars and a bulb horn
    S.capsule((66, 32), (60, 12), 2.4, "#7c8696", "#4a4e5a")
    S.rect(53, 9, 10, 3, INK); S.rect(54, 10, 8, 1, "#d8dce4")
    S.line((53, 10), (51, 6), INK); S.line((62, 10), (64, 6), INK)
    S.ellipse((66, 13), 2.6, 2.2, "#1a1020", None, rim=True); S.rect(63, 13, 3, 1, "#ffcf2a")
    return S
