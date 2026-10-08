"""v0.13 PSYCH WARD sprites (behavioral health unit): padded vinyl wall tiles, a ceiling with fluorescent troffers, pale
linoleum, a locked double door with a buzzer, the nurses' station behind plexiglass, a TV bolted high in a cage, a call-light
strip, neon signs (Bill's gloom and glow: blue / violet / red), and the ward props: a foam chair, a puzzle table, a med cart
with a paper cup of pills; projectiles (tinfoil ball, Greg's neck pillow, Phil-in's paper orders). Side view, facing right."""
from __future__ import annotations

from rig import INK, Raster
import tinyfont
from v11_art import box, neon, paint_sign

PAD, PAD_D, PAD_L = "#b8b4d8", "#9490bc", "#d4d0ec"   # lavender vinyl padding


def pwall_tile(seed):
    """32x104: quilted padded vinyl panels (tufted diamonds), a soft bumper rail, a dusky lower band and a baseboard."""
    S = Raster(32, 104)
    S.rect(0, 0, 32, 70, PAD)
    for y in range(0, 70, 16):
        for x in range(0, 32, 16):
            ox = 8 if (y // 16) % 2 else 0
            cx, cy = (x + ox) % 32, y + 8
            S.line((cx - 7, cy), (cx, cy - 7), PAD_D); S.line((cx, cy - 7), (cx + 7, cy), PAD_L)
            S.line((cx - 7, cy), (cx, cy + 7), PAD_L); S.line((cx, cy + 7), (cx + 7, cy), PAD_D)
            S.set(cx % 32, cy, "#7a76a4")
    S.rect(0, 0, 1, 70, PAD_D)
    S.rect(0, 70, 32, 6, "#7a6ab8"); S.rect(0, 70, 32, 1, "#a898e8"); S.rect(0, 75, 32, 1, "#54488a")
    S.rect(0, 76, 32, 20, "#8c88b0"); S.rect(0, 76, 32, 1, "#6a6690")
    S.rect(0, 96, 32, 8, "#4a4670"); S.rect(0, 96, 32, 1, "#6a6690")
    if seed == 2:
        S.rect(10, 30, 6, 4, "#c8c4e4"); S.rect(11, 31, 4, 1, "#a4a0c8")  # a patched spot
    if seed == 3:
        S.rect(22, 80, 4, 2, "#6a6690")  # a scuff
    return S


def pceil_tile(lit=False):
    """32x14 drop ceiling; lit = a flickery fluorescent troffer."""
    S = Raster(32, 14)
    S.rect(0, 0, 32, 14, "#c8c8d4"); S.rect(0, 0, 32, 1, "#a8a8b8"); S.rect(15, 0, 1, 12, "#a8a8b8"); S.rect(0, 12, 32, 2, "#8a8aa0")
    for k in (4, 9, 21, 26):
        S.set(k, 6, "#b0b0c0")
    if lit:
        box(S, 3, 3, 26, 7, "#eef8ff", None, "#ffffff"); S.rect(4, 5, 24, 1, "#cfe8ff"); S.rect(4, 7, 24, 1, "#cfe8ff")
    return S


def pfloor_tiles():
    out = []
    for i in range(2):
        S = Raster(24, 12)
        S.rect(0, 0, 24, 12, "#c8dcd4" if i == 0 else "#b8ccc4"); S.rect(0, 11, 24, 1, "#a0b4ac"); S.rect(23, 0, 1, 12, "#a0b4ac")
        S.set(6 + i * 9, 4, "#dceee6"); S.set(15 - i * 6, 8, "#a8bcb4")
        out.append(S)
    return out


def dbldoor(state=0):
    """64x84 locked double door: wired-glass windows, push bars, a red/green keypad + buzzer, AUTHORIZED STAFF ONLY."""
    S = Raster(66, 84)
    box(S, 1, 1, 64, 82, "#5a5a74", None, "#7a7a94")
    for x in (3, 34):
        box(S, x, 4, 29, 78, "#8a9ac8", "#6a7aa8", "#aabae8")
        box(S, x + 8, 12, 13, 18, "#1a2440", None, None)
        for k in range(0, 18, 4):
            S.line((x + 8, 12 + k), (x + 20, 12 + k), "#4a5a80")
        S.rect(x + 3, 44, 23, 3, "#c8ccd6"); S.rect(x + 3, 46, 23, 1, "#8a94a4")
    S.rect(32, 4, 2, 78, "#3a3a54")
    S.rect(8, 56, 50, 9, "#e83a3a"); tinyfont.text(S, 10, 58, "STAFF ONLY", "#ffffff")
    return S


def buzzer():
    """A wall keypad + buzzer box with a red LOCKED light. 12x18."""
    S = Raster(12, 18)
    box(S, 1, 1, 10, 16, "#3a3a4a", None, "#5a5a6a")
    S.rect(3, 3, 6, 3, "#ff3a4a"); S.rect(4, 4, 4, 1, "#ffb0b0")
    for y in (8, 11, 14):
        for x in (3, 6):
            S.rect(x, y, 2, 2, "#c8ccd6")
    return S


def nstation():
    """112x58 nurses' station behind plexiglass: counter, glass panes with glare streaks, a pass-through slot, a monitor
    glow, a sign. Placed on the floor line."""
    S = Raster(112, 58)
    box(S, 1, 2, 110, 6, "#3a3a54", None, "#5a5a74"); tinyfont.text(S, 20, 3, "NURSES STATION", "#bfe0ff")
    for i in range(4):
        x = 2 + i * 27
        S.rect(x, 9, 26, 26, "#5a7ab0"); S.rect(x, 9, 26, 26, "#5a7ab0")
        S.rect(x + 1, 10, 24, 24, "#7a9ad0")
        S.line((x + 4, 30), (x + 16, 12), "#cfe8ff"); S.line((x + 8, 32), (x + 19, 15), "#a8c8f0")
        S.rect(x + 25, 9, 1, 26, "#c8ccd6")
    S.rect(30, 22, 18, 10, "#1a2440"); S.rect(31, 23, 16, 8, "#3aa8ff"); S.rect(32, 24, 6, 1, "#bfe8ff")  # monitor through the glass
    box(S, 1, 35, 110, 22, "#8a7ab0", "#6a5a90", "#aa9ad0")
    S.rect(46, 33, 20, 3, "#2a2a3a")  # pass-through slot
    S.rect(4, 44, 104, 1, "#6a5a90")
    return S


def tv_cage():
    """40x36 TV bolted high on the wall inside a wire cage, glowing blue (a talk show nobody asked for)."""
    S = Raster(40, 36)
    S.rect(18, 0, 4, 6, "#4a4a5a")
    box(S, 2, 6, 36, 26, "#1a1a24", None, "#3a3a48")
    S.rect(5, 9, 30, 19, "#2a7ae8"); S.rect(6, 10, 28, 4, "#7ab8ff")
    S.rect(15, 15, 10, 10, "#f0c0a0"); S.rect(15, 15, 10, 3, "#3a2a1a"); S.rect(17, 19, 2, 1, INK); S.rect(21, 19, 2, 1, INK); S.rect(18, 22, 4, 1, "#a01c28")
    for x in range(2, 39, 6):
        S.rect(x, 5, 1, 29, "#8a94a4")
    S.rect(1, 5, 38, 1, "#8a94a4"); S.rect(1, 33, 38, 1, "#8a94a4")
    return S


def callstrip():
    """64x6 call-light strip along the wall: blue / violet / red LEDs."""
    S = Raster(64, 6)
    box(S, 1, 1, 62, 4, "#2a2a3a", None, None)
    for i, x in enumerate(range(4, 62, 8)):
        S.rect(x, 2, 4, 2, ("#3aa8ff", "#a24dff", "#ff3a4a")[i % 3])
    return S


def poster_feelings():
    """HOW ARE YOU FEELING TODAY? chart (5 cartoon faces). 44x34."""
    S = Raster(44, 34)
    box(S, 1, 1, 42, 32, "#f4f0e4", None, None)
    tinyfont.text(S, 4, 3, "FEELINGS?", "#2a5ad8")
    cols = ("#3ae870", "#a8e83a", "#f4d03a", "#f4903a", "#e83a3a")
    for i, c in enumerate(cols):
        x, y = 4 + (i % 3) * 13, 11 + (i // 3) * 11
        S.ellipse((x + 4, y + 4), 4, 4, c, None, rim=True); S.set(x + 3, y + 3, INK); S.set(x + 5, y + 3, INK)
        S.rect(x + 3, y + 6 - (1 if i < 2 else 0), 3, 1, INK)
    return S


def poster_group():
    S = Raster(44, 22)
    box(S, 1, 1, 42, 20, "#3a2a6a", None, None)
    tinyfont.text(S, 4, 4, "GROUP 2PM", "#ffe84a"); tinyfont.text(S, 4, 12, "ART + SNACK", "#bfe0ff")
    return S


def foamchair(state=0):
    """A heavy molded-foam dayroom chair (rounded, no hard edges), teal. 3 states. 22x24."""
    S = Raster(22, 24)
    c, d = ("#3ab8a8", "#2a8a80") if state < 2 else ("#2a8a80", "#1e6a62")
    box(S, 2, 2, 7, 18, c, d, "#7ae8d8")
    box(S, 2, 12, 18, 8, c, d, "#7ae8d8")
    S.rect(3, 20, 16, 3, d)
    if state >= 1:
        S.rect(12, 13, 3, 2, "#e8f0a0"); S.rect(5, 6, 2, 3, "#e8f0a0")  # foam showing through
    if state == 2:
        S.rect(14, 12, 6, 3, "#00000000") if False else S.rect(15, 12, 5, 2, "#e8f0a0")
    return S


def puzzletable(state=0):
    """Dayroom puzzle table with a half-done 1000-piece puzzle (a sunset). 3 states. 44x26."""
    S = Raster(44, 26)
    box(S, 2, 6, 40, 4, "#a87a4a", "#7a5430", "#c89a6a")
    if state < 2:
        S.rect(5, 4, 22 if state == 0 else 14, 2, "#ff8a4a"); S.rect(8, 3, 12, 1, "#ffd84a"); S.rect(29, 4, 6, 2, "#3aa8ff")
        S.set(36, 4, "#a24dff"); S.set(38, 5, "#ff8a4a")
    for x in (5, 37):
        S.rect(x, 10, 3, 14 if state < 2 else 10, "#7a5430")
    if state == 2:
        S.line((20, 6), (24, 10), INK); S.rect(30, 22, 3, 2, "#7a5430")
    return S


def pillcart(state=0):
    """Med cart with a little white paper cup of pills on top (the 'meds' in med pass). 3 states. 26x32."""
    S = Raster(26, 32)
    box(S, 2, 8, 22, 18, "#e8eef4", "#b8c2d0", "#ffffff")
    for y in (12, 17, 22):
        S.rect(4, y, 18, 1, "#a8b2c0"); S.rect(11, y - 3, 4, 1, "#3aa8ff")
    S.rect(2, 8, 22, 2, "#3a8ae8")
    if state < 2:
        S.rect(15, 3, 6, 5, INK); S.rect(16, 4, 4, 4, "#ffffff"); S.set(17, 3, "#e84a5a"); S.set(18, 3, "#ffd84a"); S.set(19, 3, "#3ae870")
    if state >= 1:
        S.line((5, 14), (12, 20), "#8a94a4")
    for x in (6, 20):
        S.ellipse((x, 28), 2, 2, "#2a2a30", None, rim=True)
    return S


def bits():
    out = {}
    for i, c in enumerate(("#ff8a4a", "#3aa8ff", "#ffd84a")):
        S = Raster(6, 6); S.rect(1, 1, 4, 4, c); S.set(4, 2, "#00000000") if False else S.set(1, 4, INK); out[f"deb_puzzle{i}"] = S
    S = Raster(8, 6); box(S, 1, 1, 6, 4, "#3ab8a8", None, "#7ae8d8"); out["deb_foam"] = S
    S = Raster(6, 6); box(S, 1, 1, 4, 4, "#ffffff"); S.set(2, 1, "#e84a5a"); out["deb_cup"] = S
    return out


def proj_foil():
    S = Raster(8, 8); S.ellipse((4, 4), 3, 3, "#c8ccd6", "#8a909c", rim=True); S.set(3, 3, "#ffffff"); S.set(5, 5, "#6a707c"); return S


def proj_pillow(spin=0):
    """Greg's neck pillow spinning through the air (boomerang). 16x12."""
    S = Raster(16, 12)
    if spin % 2 == 0:
        S.ellipse((8, 6), 6.5, 4, "#8a8e96", "#5e626a"); S.ellipse((8, 5), 2.5, 1.5, "#4a4e56", None, rim=False); S.rect(13, 5, 2, 2, "#c8ccd6")
    else:
        S.ellipse((8, 6), 4, 5, "#8a8e96", "#5e626a"); S.ellipse((8, 6), 1.5, 2.5, "#4a4e56", None, rim=False); S.rect(7, 1, 2, 2, "#c8ccd6")
    return S


def proj_order():
    """A paper doctor's order, fluttering. 10x8."""
    S = Raster(10, 8); box(S, 1, 1, 8, 6, "#fff8e8"); S.rect(2, 2, 5, 1, "#2a5ad8"); S.rect(2, 4, 6, 1, "#8a94a4"); S.rect(6, 5, 2, 1, "#e83a3a"); return S


def note():
    """A music note for Greg's crooning bubble. 7x9."""
    S = Raster(7, 9); S.rect(4, 0, 1, 7, INK); S.rect(4, 0, 3, 1, INK); S.rect(5, 1, 2, 1, INK); S.ellipse((3, 7), 1.8, 1.4, INK, None, rim=False); return S


def wall_pieces():
    return {
        "pwall_door": dbldoor(), "buzzer": buzzer(), "nstation": nstation(), "tvcage": tv_cage(), "callstrip": callstrip(),
        "poster_feelings": poster_feelings(), "poster_group": poster_group(),
        "neon_dayroom": neon("DAYROOM", "#a24dff"), "neon_calm": neon("CALM ZONE", "#3aa8ff"), "neon_bhu": neon("BHU 5", "#ff3a4a"),
        "sign_bhu": paint_sign("BEHAVIORAL HEALTH UNIT", "#3a2a6a", "#ffe84a"), "sign_elope": paint_sign("ELOPEMENT RISK: CLOSE THE DOOR", "#c82a2a"),
        "sign_quiet": paint_sign("QUIET HOURS 10P-6A", "#2a5aa8"),
    }
