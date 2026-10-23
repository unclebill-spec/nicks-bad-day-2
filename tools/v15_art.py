"""v0.15 LABOR & DELIVERY sprites: peach wall over a baby-blue wainscot, a pastel (mint / peach / baby blue) tile floor,
a nursery window with bassinets, balloon bunches, IT'S A ...! banners, neon (blue / violet / red), a gift cart prop, and
projectiles (camcorder flash, juice box, the stork's laundry bundle). Side view, facing right. Parody brands only."""
from __future__ import annotations

from rig import INK, Raster
import tinyfont
from v11_art import box, neon, paint_sign

MINT, PEACH, BABY = "#a8e8c8", "#f8c8a8", "#a8d0f8"


def lwall_tile(seed):
    """32x104: peach paint, a mint chair rail, baby-blue wainscot with little stork-and-star stencils, a baseboard."""
    S = Raster(32, 104)
    S.rect(0, 0, 32, 58, "#f4d4c0"); S.rect(0, 0, 32, 1, "#dcb8a4")
    S.rect(0, 58, 32, 4, "#5ac8a0"); S.rect(0, 58, 32, 1, "#a8f0d0"); S.rect(0, 61, 32, 1, "#2a8a6a")
    S.rect(0, 62, 32, 34, "#bcd8f4")
    for y in range(66, 96, 10):
        S.rect(0, y, 32, 1, "#a0c0e4")
    if seed % 2 == 0:
        for (x, y) in ((8, 76), (24, 86)):
            S.set(x, y, "#ffffff"); S.set(x - 1, y, "#fff4a8"); S.set(x + 1, y, "#fff4a8"); S.set(x, y - 1, "#fff4a8"); S.set(x, y + 1, "#fff4a8")
    if seed == 3:
        S.rect(10, 20, 3, 3, "#f8b0c8"); S.rect(18, 30, 3, 3, BABY)  # little polka dots
    S.rect(0, 96, 32, 8, "#8a6a8a"); S.rect(0, 96, 32, 1, "#a88aa8")
    return S


def lceil_tile(lit=False):
    S = Raster(32, 14)
    S.rect(0, 0, 32, 14, "#ecdcd4"); S.rect(0, 0, 32, 1, "#ccbcb4"); S.rect(15, 0, 1, 12, "#ccbcb4"); S.rect(0, 12, 32, 2, "#a8989a")
    if lit:
        box(S, 3, 3, 26, 7, "#fff4f0", None, "#ffffff"); S.rect(4, 5, 24, 1, "#ffe0e8")
    return S


def lfloor_tiles():
    """Pastel tiles: mint, peach and baby blue, staggered."""
    out = []
    order = ((MINT, PEACH), (BABY, MINT), (PEACH, BABY))
    for i, (a, b) in enumerate(order):
        S = Raster(24, 12)
        S.rect(0, 0, 12, 12, a); S.rect(12, 0, 12, 12, b)
        S.rect(0, 11, 24, 1, "#c8b8c8"); S.rect(23, 0, 1, 12, "#c8b8c8"); S.rect(11, 0, 1, 12, "#d8c8d8")
        S.set(4 + i * 5, 3, "#ffffff"); S.set(16, 7 - i, "#ffffff")
        out.append(S)
    return out


def nursery():
    """112x50 NURSERY window: a big glass pane with glare, four bassinets with little blanket bundles (pink / blue / mint /
    yellow) and a sign. Wall-mounted."""
    S = Raster(112, 50)
    box(S, 1, 1, 110, 48, "#e8e0ec", "#b8b0c4", "#ffffff")
    S.rect(4, 10, 104, 36, "#d8ecf8")
    for x in range(10, 104, 30):
        S.line((x, 44), (x + 12, 12), "#f4fcff"); S.line((x + 2, 44), (x + 14, 12), "#eef8ff")
    for i, c in enumerate(("#f8b0c8", BABY, MINT, "#fff0a0")):
        x = 10 + i * 25
        S.rect(x, 34, 18, 8, "#f4f4f8"); S.rect(x, 34, 18, 1, "#c8c8d8"); S.rect(x + 2, 42, 2, 3, "#a8a8b8"); S.rect(x + 14, 42, 2, 3, "#a8a8b8")
        S.ellipse((x + 9, 32), 6, 3, c, None, rim=True); S.ellipse((x + 13, 31), 2.2, 2, "#f8d8c0", None, rim=True)
    tinyfont.text(S, 36, 3, "NURSERY", "#5a6aa8")
    return S


def balloons(seed=0):
    """30x56 balloon bunch tied to a weight: three balloons (pink / baby blue / mint), curly ribbons."""
    S = Raster(30, 56)
    cols = (("#f88ab8", "#c86a90"), ("#7ab8f0", "#4a88c8"), ("#6ad8a8", "#3aa878")) if seed == 0 else (("#7ab8f0", "#4a88c8"), ("#fff07a", "#d8c04a"), ("#f88ab8", "#c86a90"))
    for (x, y), (c, s) in zip(((9, 10), (20, 8), (15, 20)), cols):
        S.line((x, y + 8), (15, 50), "#c8c8d8")
        S.ellipse((x, y), 6, 7.5, c, s); S.set(x - 2, y - 4, "#ffffff"); S.set(x - 3, y - 3, "#ffffff")
    S.rect(12, 49, 7, 6, "#a8a8b8"); S.rect(12, 49, 7, 1, "#d8d8e8")
    return S


def banner(text, c):
    """A bunting banner: triangle flags under a lettered strip."""
    tw = tinyfont.width(text)
    w = tw + 14
    S = Raster(w, 22)
    box(S, 1, 1, w - 2, 9, c, None, None)
    tinyfont.text(S, (w - tw) // 2, 3, text, "#ffffff")
    cols = ("#f88ab8", "#7ab8f0", "#6ad8a8", "#fff07a")
    for i, x in enumerate(range(3, w - 6, 8)):
        S.poly([(x, 12), (x + 6, 12), (x + 3, 19)], cols[i % 4])
    return S


def giftcart(state=0):
    """A gift-shop cart (flowers, a teddy bear, a balloon). Rolls when hit. 3 states. 30x34."""
    S = Raster(30, 34)
    if state < 2:
        S.line((22, 20), (24, 4 + state * 2), "#c8c8d8"); S.ellipse((24, 4 + state * 2), 4, 4.5, "#f88ab8", "#c86a90")
        S.ellipse((10, 18), 4, 4, "#c8945a", "#9a6a3a"); S.ellipse((10, 13), 3, 3, "#c8945a", "#9a6a3a"); S.set(9, 13, INK); S.set(11, 13, INK)
        for k, c in enumerate(("#ff5a7a", "#ffe84a", "#a24dff")):
            S.ellipse((17 + k * 3, 17 - k % 2), 1.8, 1.8, c, None, rim=True)
    box(S, 2, 21, 26, 6, "#f4f4f8", "#c8c8d8", "#ffffff")
    if state >= 1:
        S.line((8, 21), (14, 26), INK)
    if state == 2:
        S.ellipse((10, 19), 4, 3, "#c8945a", "#9a6a3a")
    for x in (6, 24):
        S.ellipse((x, 30), 2.5, 2.5, "#3a3a44", None, rim=True)
    return S


def bits():
    out = {}
    S = Raster(8, 8); S.ellipse((4, 4), 3, 3.5, "#f88ab8", "#c86a90"); out["deb_balloon"] = S
    S = Raster(8, 6); box(S, 1, 1, 6, 4, "#f4f4f8", None, "#ffffff"); out["deb_gift"] = S
    S = Raster(6, 6); S.ellipse((3, 3), 2, 2, "#ff5a7a", None, rim=True); out["deb_flower"] = S
    return out


def proj_flash(k=0):
    """The camcorder flash: a white-hot star burst with a blue halo. 16x14, two frames."""
    S = Raster(16, 14)
    S.ellipse((8, 7), 6 - k, 5 - k, "#bfe0ff", None, rim=False)
    S.line((1, 7), (15, 7), "#ffffff"); S.line((8, 1), (8, 13), "#ffffff")
    S.ellipse((8, 7), 2.5, 2.5, "#ffffff", None, rim=False)
    return S


def proj_juice():
    """A grape juice box with a bendy straw, mid-flight. 8x10."""
    S = Raster(8, 10); box(S, 1, 3, 6, 6, "#8a3ad8", None, "#b46af8"); S.rect(2, 5, 4, 2, "#ffffff"); S.line((5, 3), (6, 0), "#f4f4f4"); return S


def proj_bundle():
    """The stork's "baby": really a knotted sack of hospital laundry. 18x16."""
    S = Raster(18, 16)
    S.ellipse((9, 10), 7.5, 5.5, "#f4f4f8", "#c8ccd8")
    S.poly([(6, 5), (12, 5), (14, 1), (4, 1)], "#f4f4f8")
    S.rect(6, 4, 7, 2, "#7ab8f0")  # baby-blue tie
    S.set(5, 11, "#c8ccd8"); S.set(12, 9, "#c8ccd8"); S.rect(10, 12, 3, 1, "#a8d0f8")  # a sock poking out
    return S


def juice_splat():
    """A purple, slippery grape-juice puddle with the squashed box."""
    S = Raster(34, 10)
    S.ellipse((17, 5), 15, 4, "#6a2aa8", None, rim=False); S.ellipse((14, 4), 9, 2.4, "#8a4ad8", None, rim=False)
    S.rect(9, 3, 3, 1, "#c8a0f8"); S.rect(23, 4, 5, 3, "#8a3ad8"); S.rect(24, 5, 3, 1, "#ffffff")
    return S


def wall_pieces():
    return {
        "nursery": nursery(), "balloons": balloons(0), "balloons2": balloons(1),
        "banner_boy": banner("IT'S A BOY!", "#4a88d8"), "banner_girl": banner("IT'S A GIRL!", "#d85a9a"), "banner_q": banner("IT'S A ...!", "#8a5ad8"),
        "neon_ld": neon("L&D", "#ff3a4a"), "neon_nursery": neon("NURSERY", "#3aa8ff"), "neon_baby": neon("WELCOME BABY", "#a24dff"),
        "sign_quiet": paint_sign("QUIET PLEASE", "#5a6aa8"), "sign_visit": paint_sign("VISITING HOURS ARE OVER", "#c84a6a"),
        "sign_ld": paint_sign("LABOR & DELIVERY", "#8a5ad8", "#fff4a8"),
    }
