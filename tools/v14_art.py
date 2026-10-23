"""v0.14 CAFETERIA LUNCH RUSH sprites: cream wall over white subway-tile wainscot, a drop ceiling, red/cream quarry-tile
floor, the serving line (sneeze guard + steam trays), a salad bar, a soda fountain, a menu board, neon (blue / violet / red)
and the cafe props: round table, plastic chair, a stack of trays that topples; projectiles (soup wave, mystery meat, ranch
cup). Side view, facing right. Parody brands only."""
from __future__ import annotations

from rig import INK, Raster
import tinyfont
from v11_art import box, neon, paint_sign


def cwall_tile(seed):
    """32x104: cream paint, an orange chair rail, white subway tile wainscot, a dark baseboard."""
    S = Raster(32, 104)
    S.rect(0, 0, 32, 58, "#e8dcc0"); S.rect(0, 0, 32, 1, "#d0c4a8")
    S.rect(0, 58, 32, 4, "#e87a2a"); S.rect(0, 58, 32, 1, "#ffb070"); S.rect(0, 61, 32, 1, "#a8501a")
    S.rect(0, 62, 32, 34, "#f0f2f4")
    for r, y in enumerate(range(62, 96, 6)):
        S.rect(0, y + 5, 32, 1, "#b8c0c8")
        for x in range(8 if r % 2 else 0, 32, 16):
            S.rect(x, y, 1, 5, "#b8c0c8")
    S.rect(0, 96, 32, 8, "#5a3a2a"); S.rect(0, 96, 32, 1, "#7a5a44")
    if seed == 2:
        S.rect(12, 24, 5, 3, "#d8a868")  # a ketchup-coloured mystery smudge
    if seed == 3:
        S.rect(20, 70, 3, 2, "#c8ccd2")
    return S


def cceil_tile(lit=False):
    S = Raster(32, 14)
    S.rect(0, 0, 32, 14, "#d8d4c8"); S.rect(0, 0, 32, 1, "#b8b4a8"); S.rect(15, 0, 1, 12, "#b8b4a8"); S.rect(0, 12, 32, 2, "#9a968a")
    if lit:
        box(S, 3, 3, 26, 7, "#fff8e8", None, "#ffffff"); S.rect(4, 5, 24, 1, "#ffe8c0")
    return S


def cfloor_tiles():
    out = []
    for i in range(2):
        S = Raster(24, 12)
        S.rect(0, 0, 12, 12, "#b84a3a" if i == 0 else "#e8dcc4"); S.rect(12, 0, 12, 12, "#e8dcc4" if i == 0 else "#b84a3a")
        S.rect(0, 11, 24, 1, "#8a3a2e"); S.rect(23, 0, 1, 12, "#8a3a2e"); S.rect(11, 0, 1, 12, "#9a8a74")
        S.set(5 + i * 9, 4, "#ffffff")
        out.append(S)
    return out


def serveline():
    """128x60 serving line: a sneeze guard (glass + glare), five steam trays (peas, mac, mystery meat, jello, mash) with
    steam, a tray slide rail. Placed on the floor line."""
    S = Raster(128, 60)
    S.rect(4, 2, 120, 2, "#c8ccd6")
    for x in (6, 64, 120):
        S.rect(x, 2, 2, 18, "#c8ccd6")
    S.rect(6, 4, 116, 14, "#9ad0f0"); S.rect(6, 4, 116, 14, "#9ad0f0")
    for x in range(10, 120, 28):
        S.line((x, 16), (x + 8, 6), "#e8f8ff")
    foods = ("#5ac83a", "#ffb02a", "#8a5a3a", "#3ae870", "#f4ecd8")
    for i, c in enumerate(foods):
        x = 6 + i * 24
        S.rect(x, 22, 22, 6, "#8a94a4"); S.rect(x + 1, 22, 20, 3, c); S.set(x + 5, 22, "#ffffff"); S.set(x + 14, 23, "#ffffff")
        for k in range(3):
            S.set(x + 6 + k * 5, 19 - k % 2, "#ffffff"); S.set(x + 7 + k * 5, 17, "#e8f0f8")
    box(S, 1, 28, 126, 30, "#c8ccd6", "#8a94a4", "#eef2f8")
    S.rect(0, 30, 128, 3, "#5a6270"); S.rect(0, 30, 128, 1, "#8a94a4")  # tray slide
    for x in range(8, 124, 20):
        S.rect(x, 40, 12, 10, "#a8b2c0"); S.rect(x + 1, 41, 10, 1, "#eef2f8")
    return S


def saladbar():
    """76x50 salad bar: a sneeze-guard hood, lettuce / tomato / croutons / suspicious olives, ice under it."""
    S = Raster(76, 50)
    S.poly([(4, 14), (72, 14), (64, 2), (12, 2)], "#9ad0f0"); S.line((14, 12), (22, 3), "#e8f8ff")
    for i, c in enumerate(("#5ac83a", "#e83a3a", "#d8a85a", "#2a2a30", "#f4ecd8")):
        x = 5 + i * 13
        S.rect(x, 16, 12, 5, "#e8f0f8"); S.rect(x + 1, 16, 10, 3, c)
    box(S, 2, 21, 72, 27, "#3a8a5a", "#28684a", "#5aaa7a"); tinyfont.text(S, 10, 30, "SALAD BAR", "#ffffff")
    return S


def soda():
    """36x54 soda fountain: FIZZCO and DR. PEPPY parody labels, glowing nozzles, a drip tray."""
    S = Raster(36, 54)
    box(S, 1, 1, 34, 52, "#2a2a3a", None, "#4a4a5a")
    S.rect(3, 3, 30, 18, "#e83a3a"); tinyfont.text(S, 5, 5, "FIZZ", "#ffffff"); tinyfont.text(S, 5, 12, "CO", "#ffe84a")
    for i, c in enumerate(("#e83a3a", "#7a2a3a", "#3aa8ff", "#a24dff")):
        S.rect(4 + i * 7, 24, 5, 4, c); S.rect(5 + i * 7, 28, 3, 3, "#c8ccd6")
    S.rect(3, 40, 30, 3, "#8a94a4"); S.rect(3, 43, 30, 1, "#3aa8ff")
    return S


def menuboard():
    """68x34 menu board: TODAY: MYSTERY MEAT, PUDDING (while it lasts)."""
    S = Raster(68, 34)
    box(S, 1, 1, 66, 32, "#1a2a24", None, "#3a4a44")
    tinyfont.text(S, 4, 3, "TODAY:", "#ffe84a"); tinyfont.text(S, 4, 11, "MYSTERY MEAT", "#ffffff")
    tinyfont.text(S, 4, 19, "PUDDING $1", "#ff8ac0"); tinyfont.text(S, 4, 26, "(WHILE IT LASTS)", "#8a9a94")
    return S


def roundtable(state=0):
    """A round cafe table (side view: pedestal) with a lunch tray. 3 states. 40x26."""
    S = Raster(40, 26)
    box(S, 2, 8, 36, 3, "#f0f2f4", "#c8ccd2", "#ffffff")
    if state < 2:
        S.rect(10, 5, 14 if state == 0 else 9, 3, "#e87a2a"); S.rect(12, 4, 4, 1, "#5ac83a"); S.rect(26, 4, 4, 4, "#ffffff")
    S.rect(18, 11, 4, 12 if state < 2 else 8, "#8a94a4"); S.rect(11, 23, 18, 2, "#5a6270")
    if state == 2:
        S.line((14, 8), (20, 11), INK)
    return S


def plchair(state=0):
    """Molded plastic cafe chair (violet). 3 states. 18x24."""
    S = Raster(18, 24)
    c, d = ("#7a3ab8", "#58248a") if state < 2 else ("#58248a", "#3e1a62")
    box(S, 2, 2, 4, 12, c, d, "#a46ae8"); box(S, 2, 12, 13, 3, c, d, "#a46ae8")
    for x in (3, 13):
        S.rect(x, 15, 1, 8 if state < 2 else 5, "#8a94a4")
    if state >= 1:
        S.rect(8, 12, 2, 1, INK)
    return S


def traystack(state=0):
    """A tall wobbly stack of brown lunch trays on a cart. state 0 tidy, 1 leaning, 2 toppled flat. 22x34."""
    S = Raster(22, 34)
    if state < 2:
        lean = 0 if state == 0 else 1
        for i in range(9):
            x = 2 + (i * lean) // 2
            S.rect(x, 26 - i * 3, 17, 2, "#a8643a" if i % 2 else "#c8844a"); S.rect(x, 26 - i * 3, 17, 1, "#e8a46a")
    else:
        for i in range(4):
            S.rect(1 + i * 2, 26 - i * 2, 19, 2, "#a8643a"); S.rect(1 + i * 2, 26 - i * 2, 19, 1, "#e8a46a")
    S.rect(2, 28, 18, 2, "#8a94a4")
    for x in (4, 17):
        S.ellipse((x, 31), 2, 2, "#2a2a30", None, rim=True)
    return S


def bits():
    out = {}
    S = Raster(12, 4); box(S, 1, 1, 10, 2, "#c8844a", None, "#e8a46a"); out["deb_tray"] = S
    S = Raster(4, 4); S.ellipse((2, 2), 1.4, 1.4, "#5ac83a", None, rim=True); out["deb_pea"] = S
    S = Raster(8, 6); box(S, 1, 1, 6, 4, "#7a3ab8", None, "#a46ae8"); out["deb_chair"] = S
    return out


def proj_soup(k=0):
    """The soup splash wave rolling down a lane. 28x16, two frames."""
    S = Raster(28, 16)
    S.ellipse((14, 12), 13, 4, "#e8902a", "#b8601a")
    S.ellipse((18 - k * 3, 7), 6, 6, "#ffb04a", "#e8902a")
    S.set(8 + k * 4, 6, "#5ac83a"); S.set(20 - k * 2, 4, "#ffffff"); S.set(5, 9, "#ffe0a0"); S.set(23, 8 - k, "#e83a3a")
    return S


def proj_meat():
    """Mystery meat: a grey-brown slab with grill marks, mid-flight. 12x8."""
    S = Raster(12, 8); S.ellipse((6, 4), 5, 3, "#8a6a5a", "#5a4038"); S.line((3, 2), (6, 6), "#3a2620"); S.line((6, 2), (9, 6), "#3a2620"); return S


def proj_ranch():
    """A little paper cup of ranch dressing (on the side!). 7x8."""
    S = Raster(7, 8); S.poly([(1, 2), (6, 2), (5, 7), (2, 7)], "#ffffff"); S.rect(2, 1, 3, 2, "#f4ecd8"); S.set(3, 1, "#c8e8a0"); return S


def ladle():
    """The giant ladle as a floor weapon icon / held prop. 10x30."""
    S = Raster(12, 30); S.rect(5, 0, 2, 22, "#c8ccd6"); S.rect(5, 0, 1, 22, "#eef2f8"); S.ellipse((6, 25), 5, 4, "#c8ccd6", "#8a94a4"); return S


def wall_pieces():
    return {
        "serveline": serveline(), "saladbar": saladbar(), "soda": soda(), "menuboard": menuboard(),
        "neon_cafe": neon("CAFE", "#ff3a4a"), "neon_eat": neon("EAT", "#3aa8ff"), "neon_dessert": neon("DESSERT", "#a24dff"),
        "sign_cafe": paint_sign("CAFETERIA", "#c84a2a", "#ffe84a"), "sign_nocut": paint_sign("NO CUTTING IN LINE", "#c82a2a"),
        "sign_trays": paint_sign("TRAYS HERE", "#2a5aa8"),
    }
