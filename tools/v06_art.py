"""v0.6 sprites: three-day-old pizza, SNAP STIX meat stick (parody wrapper), the Ativan syringe, an X-ray skeleton for
the defib zap flash, and the red wall-mounted fire-alarm pull station (normal / pulled)."""
from __future__ import annotations

from rig import INK, Raster
import tinyfont


def pizza():
    """Mid heal: a three-day-old pizza slice, slightly green, with stink lines (the stink lines also wiggle in-game)."""
    S = Raster(18, 18)
    S.poly([(2, 7), (16, 4), (9, 17)], "#e8c84a")                 # slice
    S.poly([(4, 8), (14.5, 5.8), (9, 15)], "#c8d86a", rim=False)    # greenish cheese
    S.capsule((2, 7), (16, 4), 2.6, "#c8803a", "#8a5224")          # crust
    for (x, y) in ((8, 9), (11, 8), (9, 12)):
        S.ellipse((x, y), 1.4, 1.2, "#b84a3a", None, rim=False)     # pepperoni
    for (x, y) in ((6, 10), (12, 10), (10, 7)):
        S.set(x, y, "#7aa83a")                                      # mould spots
    for k, x in enumerate((5, 9, 13)):                              # stink lines
        for i in range(4):
            S.set(x + (1 if (i + k) % 2 else 0), 3 - i if i < 3 else 0, "#8ae87a")
    return S


def snapstix():
    """Small-mid heal: a SNAP STIX meat stick (made-up brand, parody wrapper; no real logo)."""
    S = Raster(28, 11)
    S.capsule((3, 5), (24, 5), 8, "#d8303c", "#a01c28")            # wrapper
    S.rect(4, 2, 18, 7, "#ffd84a")                                  # label band
    tinyfont.text(S, 5, 3, "SNAP", "#a01c28")
    S.rect(25, 3, 3, 5, "#8a4a2a"); S.set(26, 4, "#b86a3a")         # torn end: the meat stick pokes out
    S.set(2, 3, "#ff6a6a")
    return S


def ativan():
    """The Ativan syringe the nurse jabs with (big, cartoony, no gore)."""
    S = Raster(22, 8)
    S.rect(5, 2, 11, 4, INK); S.rect(6, 3, 9, 2, "#e8f4ff"); S.rect(7, 3, 5, 2, "#c8a0ff")
    S.rect(2, 3, 3, 2, "#c8ccd6"); S.rect(1, 1, 1, 6, "#c8ccd6"); S.rect(0, 1, 1, 6, INK)
    S.rect(16, 3, 2, 2, "#c8ccd6"); S.rect(18, 3, 4, 1, "#e4e8f0")
    S.set(9, 2, "#ffffff")
    return S


def skeleton():
    """Cartoon X-ray skeleton (white bones on nothing) flashed over a zapped patient."""
    W_, H_ = 22, 52
    S = Raster(W_, H_)
    b = "#f4f6ff"
    S.ellipse((11, 7), 5.5, 6, b, None)                             # skull
    S.rect(8, 6, 2, 2, "#1a2a4a"); S.rect(12, 6, 2, 2, "#1a2a4a"); S.rect(10, 9, 2, 1, "#1a2a4a")
    S.rect(8, 11, 6, 1, b)                                          # jaw
    S.rect(10, 13, 2, 16, b)                                        # spine
    for i in range(4):
        S.capsule((5, 16 + i * 3), (17, 16 + i * 3), 1.2, b, None, rim=False)   # ribs
    S.capsule((6, 30), (16, 30), 2.2, b, None, rim=False)          # pelvis
    S.capsule((4, 14), (2, 26), 1.2, b, None, rim=False); S.capsule((18, 14), (20, 26), 1.2, b, None, rim=False)  # arms
    S.capsule((8, 32), (7, 49), 1.4, b, None, rim=False); S.capsule((14, 32), (15, 49), 1.4, b, None, rim=False)  # legs
    return S


def firealarm(pulled=False):
    """Red wall-mounted fire-alarm pull station. Pulled: the handle is down and the strobe lamp is lit."""
    S = Raster(20, 26)
    S.rect(5, 0, 10, 5, INK); S.rect(6, 1, 8, 3, "#ffffff" if pulled else "#c8ccd6")   # strobe lamp
    if pulled:
        S.rect(7, 2, 6, 1, "#fff8a0")
    S.rect(0, 5, 20, 20, INK); S.rect(1, 6, 18, 18, "#e8303c"); S.rect(1, 6, 18, 1, "#ff6a6a"); S.rect(1, 23, 18, 1, "#a01c28")
    tinyfont.text(S, 2, 7, "FIRE", "#ffffff")
    if pulled:
        S.rect(7, 17, 6, 5, INK); S.rect(8, 18, 4, 3, "#ffffff")    # handle pulled down
    else:
        S.rect(7, 12, 6, 5, INK); S.rect(8, 13, 4, 3, "#ffffff")
        tinyfont.text(S, 2, 18, "PULL", "#ffffff")
    return S
