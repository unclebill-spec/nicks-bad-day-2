"""v0.11 PARKING GARAGE AT SHIFT CHANGE characters, on the same side-view rig as everyone else.

Garage enemies are angry visitors who couldn't find a parking spot. Bill's rules: staff-sized (the nurses' build), normal
street clothes with a SEPARATE top and bottom and a visible waist (shirt hem, then a belt / waistband, then pants). No onesie,
no padding, no armor. The boss VINNIE THE VALET is ~1.25x a nurse standing (and ~1.3x in his golf cart with the canopy).
"""
from __future__ import annotations

import math

from rig import INK, P, vec, add
from chars import SKIN, hero_body, hero_anims, walk_cycle, holder, hair_cap, bald_ring, _frame

NURSE_BUILD = dict(thigh=10.5, shin=10.5, torso=16.5, head=6.6, uarm=8, farm=8, arm_w=3.6, leg_w=5.0, torso_w=12, fist=2.0, foot=2)
STREET = dict(vneck=False, steth=False, badge=None, eye_white=True, drawstring=False)

POLO = ("#e0a628", "#a8781a")       # road-rage visitor: mustard polo
KHAKI = ("#c8b088", "#9a8462")
MOM_TOP = ("#f0786a", "#c0544a")    # minivan mom: coral long-sleeve top
MOM_JEANS = ("#7a9ac8", "#5a78a4")
HOODIE = ("#8a8e9a", "#62666e")     # coffee guy: grey hoodie
DARK_JEANS = ("#2e3a58", "#1e2840")
DRESS = ("#bcd4f0", "#8eaad0")      # big shot: pale blue dress shirt
SLACKS = ("#3a3c48", "#26282f")
VALET_SHIRT = ("#f4f6fa", "#c4cad6")
VALET_RED = ("#d0243a", "#981a2a", "#ff6a6a")
VALET_PANTS = ("#22232a", "#141418")


# ---------------- tops (patterns drawn over the rig's torso)
def polo(S, T, hip, neck, lean, b):
    """Polo collar + a two-button placket; a little logo-free chest stitch."""
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw = b["torso_w"]
    S.poly([at(neck, 0.6, -tw * 0.05), at(neck, 0.6, tw * 0.5), at(neck, -2.2, tw * 0.42)], "#f4e2a0", rim=False)
    S.line(at(neck, -0.5, tw * 0.36), at(neck, -4.5, tw * 0.36), b["shirt_s"])
    for k in (1.6, 3.4):
        x, y = at(neck, -k, tw * 0.4)
        S.set(int(x), int(y), "#f4f4f4")


def mom_top(S, T, hip, neck, lean, b):
    """Scoop neck, a long cardigan-ish edge down the front."""
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw = b["torso_w"]
    S.poly([at(neck, 0.4, tw * 0.05), at(neck, 0.4, tw * 0.48), at(neck, -2.5, tw * 0.3)], b["skin"], rim=False)
    S.line(at(neck, -2.5, tw * 0.46), at(hip, 1.2, tw * 0.48), "#ffb0a4")


def hoodie(S, T, hip, neck, lean, b):
    """Hood bunched behind the neck, two drawstrings and a front kangaroo pocket; ribbed hem band over the jeans."""
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw = b["torso_w"]
    S.poly([at(neck, 2.5, -tw * 0.55), at(neck, 2.0, tw * 0.05), at(neck, -3.5, -tw * 0.05), at(neck, -3.0, -tw * 0.6)], HOODIE[1])
    for dx in (0.2, 0.38):
        S.line(at(neck, -0.5, tw * dx), at(neck, -5.5, tw * dx), "#f4f4f4")
    S.poly([at(hip, 6.5, -tw * 0.05), at(hip, 6.5, tw * 0.5), at(hip, 2.0, tw * 0.5), at(hip, 2.0, -tw * 0.05)], HOODIE[1], rim=False)
    S.line(at(hip, 6.5, -tw * 0.05), at(hip, 6.5, tw * 0.5), "#6e727c")


def dress_tie(S, T, hip, neck, lean, b):
    """Dress shirt: collar points, a red tie, a pen in the pocket, sleeves rolled once."""
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw = b["torso_w"]
    S.poly([at(neck, 0.6, tw * 0.1), at(neck, 0.6, tw * 0.5), at(neck, -1.8, tw * 0.35)], "#f4f8ff", rim=False)
    S.poly([at(neck, -0.8, tw * 0.36), at(neck, -0.8, tw * 0.48), at(hip, 3.0, tw * 0.5), at(hip, 2.0, tw * 0.42), at(hip, 3.0, tw * 0.34)], "#c8243a", rim=False)
    S.line(at(neck, -1.0, tw * 0.37), at(neck, -1.0, tw * 0.48), "#7a1020")
    x, y = at(neck, -5, -tw * 0.15)
    S.rect(int(x), int(y) - 1, 1, 3, "#2a2a30")


def valet_vest(S, T, hip, neck, lean, b):
    """Red valet vest (two front panels, gold buttons, a V showing the white shirt), black bow tie, gold name pin."""
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw, L = b["torso_w"], b["torso"]
    S.poly([at(neck, -0.5, -tw / 2 - 0.4), at(neck, -0.5, tw * 0.12), at(neck, -L * 0.42, tw * 0.42),
            at(hip, 1.4, tw / 2 + 0.6), at(hip, 1.4, -tw / 2 - 0.6)], VALET_RED[0])
    S.poly([at(neck, -0.5, -tw / 2 + 0.6), at(neck, -0.5, -tw * 0.05), at(hip, 2.2, -tw * 0.05), at(hip, 2.2, -tw / 2 + 0.6)], VALET_RED[1], rim=False)
    S.line(at(neck, -1.5, tw * 0.15), at(neck, -L * 0.42, tw * 0.42), VALET_RED[2])
    for k in (0.5, 0.65, 0.8):
        x, y = at(neck, -L * k, tw * 0.44)
        S.set(int(x), int(y), "#ffd84a")
    # bow tie
    bx, by = at(neck, -1.2, tw * 0.42)
    S.rect(int(bx) - 2, int(by) - 1, 5, 3, INK); S.rect(int(bx) - 1, int(by), 3, 1, "#1a1a22"); S.set(int(bx), int(by), "#3a3a44")
    px, py = at(neck, -L * 0.36, -tw * 0.12)
    S.rect(int(px), int(py), 3, 1, "#ffd84a")


# ---------------- hair / hats
def top_bun(S, hc, r, b, pose):
    """Messy top bun + sunglasses pushed up on the head (minivan mom)."""
    hair_cap(top=-0.1, back=0.4, grow=1.0, seed=17, fringe=1)(S, hc, r, b, pose)
    S.ellipse((hc[0] - r * 0.35, hc[1] - r * 1.25), r * 0.5, r * 0.42, b["hair_c"], b["hair_s"])
    S.set(int(hc[0] - r * 0.6), int(hc[1] - r * 1.55), b["hair_c"])
    y = int(hc[1] - r * 0.78)
    S.rect(int(hc[0] + r * 0.05), y, int(r * 0.9), 2, "#1a1a22"); S.set(int(hc[0] + r * 0.4), y, "#7ad8ff")


def beanie(S, hc, r, b, pose):
    """Orange knit beanie with a fold-up cuff (coffee guy)."""
    c, s = "#e8742a", "#b04e14"
    for y in range(int(hc[1] - r - 2), int(hc[1] - r * 0.2)):
        for x in range(int(hc[0] - r - 2), int(hc[0] + r + 2)):
            if (x + 0.5 - hc[0]) ** 2 + (y + 0.5 - hc[1]) ** 2 <= (r + 1.0) ** 2:
                S.set(x, y, c if (x + y) % 3 else s)
    S.rect(int(hc[0] - r - 0.5), int(hc[1] - r * 0.45), int(2 * r + 1.5), 2, s)
    S.set(int(hc[0] - r * 0.2), int(hc[1] - r - 2), INK)
    for x in range(int(hc[0] - r * 1.1), int(hc[0] + r * 1.1)):
        y = int(hc[1] - r - 1.4)
        if S.p[y][x] is None:
            pass
    # a bit of hair under the cuff at the back
    S.rect(int(hc[0] - r - 0.5), int(hc[1] - r * 0.2), 2, 3, b["hair_c"])


def slick(S, hc, r, b, pose):
    """Slicked-back executive hair with a shine streak (big shot)."""
    hair_cap(top=-0.3, back=0.35, grow=0.8, seed=19, fringe=0)(S, hc, r, b, pose)
    S.line((hc[0] - r * 0.6, hc[1] - r * 0.95), (hc[0] + r * 0.4, hc[1] - r * 1.1), "#7a7a8a")


def comb_over(S, hc, r, b, pose):
    """Balding ring + three heroic strands combed over (road-rage visitor)."""
    bald_ring(S, hc, r, b, pose)
    for k in range(3):
        S.line((hc[0] - r * 0.7, hc[1] - r * (0.55 + k * 0.15)), (hc[0] + r * 0.5, hc[1] - r * (0.85 + k * 0.08)), b["hair_c"])


def valet_cap(S, hc, r, b, pose):
    """Red valet cap: flat crown, gold band, black brim forward; a neat mustache under the nose."""
    c, s = VALET_RED[0], VALET_RED[1]
    for y in range(int(hc[1] - r - 1.5), int(hc[1] - r * 0.3)):
        for x in range(int(hc[0] - r - 1), int(hc[0] + r + 1)):
            if (x + 0.5 - hc[0]) ** 2 + (y + 0.5 - hc[1]) ** 2 <= (r + 1.2) ** 2 or y < hc[1] - r + 1:
                if hc[0] - r - 1 <= x <= hc[0] + r + 0.5:
                    S.set(x, y, c if y < hc[1] - r * 0.6 else s)
    top = int(hc[1] - r - 1.5)
    S.rect(int(hc[0] - r - 1), top - 1, int(2 * r + 2), 1, INK)
    S.rect(int(hc[0] - r - 1), int(hc[1] - r * 0.55), int(2 * r + 2), 1, "#ffd84a")
    S.rect(int(hc[0] + r * 0.2), int(hc[1] - r * 0.35), int(r * 1.1), 2, "#14141a")   # brim
    S.rect(int(hc[0] - r - 1), int(hc[1] - r * 0.3), 2, int(r * 0.7), b["hair_c"])      # hair at the back of the neck
    # mustache
    k = max(1, int(round(r / 6.6)))
    S.rect(int(hc[0] + r * 0.35), int(hc[1] + r * 0.42), int(r * 0.7), k, b["hair_c"])


# ---------------- held things
def gholder(kind):
    def h(S, T, hand, ang, b):
        hx, hy = T(hand)
        if kind == "ticket":  # a parking ticket waved overhead / in the fist
            S.rect(int(hx) - 1, int(hy) - 8, 6, 9, INK); S.rect(int(hx), int(hy) - 7, 4, 7, "#fff8d8")
            S.rect(int(hx), int(hy) - 5, 4, 1, "#e83a3a"); S.rect(int(hx), int(hy) - 3, 3, 1, "#6a6a7a")
        elif kind == "dbag":  # diaper bag on its strap (pastel mint, a duck patch)
            S.line((hx, hy), (hx - 1, hy + 5), "#4a4a5a")
            S.rect(int(hx) - 5, int(hy) + 5, 10, 8, INK); S.rect(int(hx) - 4, int(hy) + 6, 8, 6, "#9ae8c8"); S.rect(int(hx) - 4, int(hy) + 6, 8, 1, "#d4fff0")
            S.rect(int(hx) - 1, int(hy) + 8, 2, 2, "#ffe84a")
        elif kind == "dbag_up":
            S.line((hx, hy), (hx - 6, hy - 6), "#4a4a5a")
            S.rect(int(hx) - 13, int(hy) - 14, 10, 8, INK); S.rect(int(hx) - 12, int(hy) - 13, 8, 6, "#9ae8c8"); S.rect(int(hx) - 9, int(hy) - 11, 2, 2, "#ffe84a")
        elif kind == "dbag_h":
            S.line((hx, hy), (hx + 10, hy), "#4a4a5a")
            S.rect(int(hx) + 9, int(hy) - 4, 10, 8, INK); S.rect(int(hx) + 10, int(hy) - 3, 8, 6, "#9ae8c8"); S.rect(int(hx) + 13, int(hy) - 1, 2, 2, "#ffe84a")
        elif kind == "coffee":  # a big to-go cup: white, brown sleeve, lid
            S.rect(int(hx) - 2, int(hy) - 7, 6, 9, INK); S.rect(int(hx) - 1, int(hy) - 6, 4, 7, "#f4f4f4"); S.rect(int(hx) - 1, int(hy) - 3, 4, 2, "#8a5a2a")
            S.rect(int(hx) - 2, int(hy) - 8, 6, 1, "#3a3a44")
        elif kind == "phone":  # phone held to the ear
            S.rect(int(hx) - 1, int(hy) - 5, 3, 6, "#1c1c24"); S.set(int(hx), int(hy) - 4, "#6ad8ff")
        elif kind == "keys":  # the valet's key ring on a red lanyard
            S.line((hx, hy), (hx + 1, hy + 4), "#d0243a")
            S.ellipse((hx + 1, hy + 6), 2.2, 2.2, "#d8dce4", None, rim=True)
            S.rect(int(hx) + 2, int(hy) + 7, 3, 1, "#ffd84a"); S.rect(int(hx) - 1, int(hy) + 8, 2, 2, "#b8c0cc")
        elif kind == "keys_up":
            S.line((hx, hy), (hx - 8, hy - 8), "#d0243a")
            S.ellipse((hx - 9, hy - 9), 2.4, 2.4, "#d8dce4", None, rim=True); S.rect(int(hx) - 13, int(hy) - 10, 3, 1, "#ffd84a")
        elif kind == "keys_out":  # whipped out on the lanyard
            S.line((hx, hy), (hx + 14, hy - 1), "#d0243a"); S.line((hx, hy + 1), (hx + 14, hy), "#981a2a")
            S.ellipse((hx + 16, hy - 1), 2.6, 2.6, "#d8dce4", None, rim=True)
            S.rect(int(hx) + 18, int(hy) - 3, 3, 1, "#ffd84a"); S.rect(int(hx) + 17, int(hy) + 1, 2, 2, "#b8c0cc")
    return h


def bodies():
    sk = SKIN
    B = {}
    B["ragevisitor"] = hero_body(**{**NURSE_BUILD, "torso_w": 13}, belly=1.0, skin="#f0a890", skin_s="#c87a64", hair_c="#7a5a3a", hair_s="#4a3420",
                                 hair=comb_over, mouth="#a01c28", shirt=POLO[0], shirt_s=POLO[1], sleeve=POLO[0], sleeve_s=POLO[1], sleeve_len=0.55,
                                 pants=KHAKI[0], pants_s=KHAKI[1], belt="#4a3220", buckle="#d8c060", shoe="#6a4a2a", shoe_s="#4a3018", foot_len=3.8,
                                 pattern=polo, **STREET)
    B["vanmom"] = hero_body(**NURSE_BUILD, skin=sk["fair"][0], skin_s=sk["fair"][1], hair_c="#f0d070", hair_s="#c0a040", hair=top_bun,
                            shirt=MOM_TOP[0], shirt_s=MOM_TOP[1], sleeve=MOM_TOP[0], sleeve_s=MOM_TOP[1], sleeve_len=1.6, sleeve_clip=True,
                            pants=MOM_JEANS[0], pants_s=MOM_JEANS[1], belt="#c89a5a", buckle="#f4f4f4", shoe="#f4f6fa", shoe_s="#b8c2d0",
                            mouth="#c0505e", pattern=mom_top, **STREET)
    B["coffeeguy"] = hero_body(**NURSE_BUILD, skin=sk["brown"][0], skin_s=sk["brown"][1], hair_c="#2a1a12", hair_s="#140c08", hair=beanie, beard="#2a1a12",
                               shirt=HOODIE[0], shirt_s=HOODIE[1], sleeve=HOODIE[0], sleeve_s=HOODIE[1], sleeve_len=1.8, sleeve_clip=True,
                               pants=DARK_JEANS[0], pants_s=DARK_JEANS[1], belt="#1a1a20", buckle="#b8c0cc", hem_c="#5a5e68",
                               shoe="#e84a3a", shoe_s="#a82a20", pattern=hoodie, **STREET)
    B["bigshot"] = hero_body(**NURSE_BUILD, skin=sk["light"][0], skin_s=sk["light"][1], hair_c="#2a2a34", hair_s="#14141a", hair=slick,
                             shirt=DRESS[0], shirt_s=DRESS[1], sleeve=DRESS[0], sleeve_s=DRESS[1], sleeve_len=0.95,
                             pants=SLACKS[0], pants_s=SLACKS[1], belt="#14141a", buckle="#ffd84a", shoe="#1a1a20", shoe_s="#0e0e12", foot_len=3.8,
                             pattern=dress_tie, **STREET)
    # VINNIE THE VALET: ~1.25x a nurse; white long-sleeve shirt, red vest, bow tie, black slacks + belt, valet cap, mustache.
    B["valet"] = hero_body(thigh=13.5, shin=13, torso=21, head=8.4, uarm=10, farm=10, arm_w=4.4, leg_w=6.0, torso_w=15, fist=2.4, foot=2, foot_len=4.4,
                           skin=sk["tan"][0], skin_s=sk["tan"][1], hair_c="#2a1a12", hair_s="#140c08", hair=valet_cap,
                           shirt=VALET_SHIRT[0], shirt_s=VALET_SHIRT[1], sleeve=VALET_SHIRT[0], sleeve_s=VALET_SHIRT[1], sleeve_len=1.7, sleeve_clip=True,
                           pants=VALET_PANTS[0], pants_s=VALET_PANTS[1], belt="#0e0e12", buckle="#d8dce4", shoe="#14141a", shoe_s="#0a0a0e",
                           pattern=valet_vest, **STREET)
    return B


def anims(kind):
    A = {}
    base = hero_anims("nick")
    if kind == "ragevisitor":  # waves the ticket overhead, then a big haymaker (visitor AI)
        tk = gholder("ticket")
        A["idle"] = [P(ua_f=160, fa_f=170, hold=tk, ua_b=-6, fa_b=60, lean=4, face="yell"), P(ua_f=150, fa_f=160, hold=tk, ua_b=-6, fa_b=60, lean=4, hy=1, face="yell")]
        A["walk"] = walk_cycle(swing=18, arm=10, lean=8)
        for i, f in enumerate(A["walk"]):
            f.update(ua_f=150 + (i % 2) * 14, fa_f=168, hold=tk, face="yell")
        A["atk"] = [P(lean=-10, ua_f=160, fa_f=170, hold=tk, ua_b=-120, fa_b=-150, th_f=16, th_b=-20, face="yell"),
                    P(lean=22, ua_f=160, fa_f=170, hold=tk, ua_b=92, fa_b=90, th_f=34, sh_f=10, th_b=-28, face="yell")]
    elif kind == "vanmom":  # swings the diaper bag (sweep AI)
        A["idle"] = [P(ua_f=10, fa_f=30, hold=gholder("dbag"), ua_b=-6, fa_b=100, lean=4), P(ua_f=10, fa_f=34, hold=gholder("dbag"), ua_b=-6, fa_b=104, lean=4, hy=1)]
        A["walk"] = walk_cycle(swing=18, arm=6, lean=6)
        for f in A["walk"]:
            f.update(ua_f=10, fa_f=30, hold=gholder("dbag"))
        A["atk"] = [P(lean=-10, ua_f=-140, fa_f=-150, ua_b=-30, fa_b=40, hold=gholder("dbag_up"), face="yell"),
                    P(lean=14, ua_f=86, fa_f=90, ua_b=-20, fa_b=40, th_f=26, th_b=-24, hold=gholder("dbag_h"), face="yell"),
                    P(lean=20, ua_f=70, fa_f=80, ua_b=-20, fa_b=40, th_f=30, th_b=-26, hold=gholder("dbag_h"), face="yell")]
    elif kind == "coffeeguy":  # sips, then lobs the coffee (tray AI)
        cf = gholder("coffee")
        A["idle"] = [P(ua_f=60, fa_f=150, hold=cf, ua_b=-6, fa_b=20, face="norm"), P(ua_f=64, fa_f=160, hold=cf, ua_b=-6, fa_b=20, hy=1, face="grin")]
        A["walk"] = walk_cycle(swing=16, arm=8)
        for f in A["walk"]:
            f.update(ua_f=60, fa_f=150, hold=cf)
        A["atk"] = [P(lean=-12, ua_f=-150, fa_f=-165, ua_b=40, fa_b=80, th_f=20, th_b=-24, hold=cf, face="yell"),
                    P(lean=14, ua_f=100, fa_f=96, ua_b=-20, fa_b=20, th_f=30, sh_f=10, th_b=-26, face="yell")]
        A["lob"] = A["atk"]
    elif kind == "bigshot":  # on the phone; head-down charge (sundowner AI)
        ph = gholder("phone")
        A["idle"] = [P(ua_f=150, fa_f=-150, hold=ph, ua_b=-10, fa_b=40, lean=-2, face="yell"), P(ua_f=150, fa_f=-146, hold=ph, ua_b=-10, fa_b=44, lean=-2, hy=1, face="norm")]
        A["walk"] = walk_cycle(swing=18, arm=10, lean=4)
        for f in A["walk"]:
            f.update(ua_f=150, fa_f=-150, hold=ph)
        A["atk"] = walk_cycle(swing=40, arm=0, lean=40, bob=2)
        for f in A["atk"]:
            f.update(ua_f=-60, fa_f=-40, ua_b=-70, fa_b=-50, head=-16, face="yell")
    elif kind == "valet":
        ky = gholder("keys")
        A["idle"] = [P(ua_f=30, fa_f=120, hold=ky, ua_b=-6, fa_b=40, lean=4, face="grin"), P(ua_f=36, fa_f=130, hold=ky, ua_b=-6, fa_b=44, lean=4, hy=1, face="grin")]
        A["walk"] = walk_cycle(swing=20, arm=10, lean=8)
        for f in A["walk"]:
            f.update(ua_f=30, fa_f=120, hold=ky)
        A["swing"] = [P(lean=-10, ua_f=-140, fa_f=-150, hold=gholder("keys_up"), ua_b=-20, fa_b=40, th_f=16, th_b=-20, face="grin"),
                      P(lean=18, ua_f=88, fa_f=90, hold=gholder("keys_out"), ua_b=-30, fa_b=30, th_f=30, sh_f=10, th_b=-26, face="yell")]
        A["throw"] = [P(lean=-12, ua_f=-150, fa_f=-170, hold=gholder("ticket"), ua_b=40, fa_b=80, th_f=20, th_b=-24, face="grin"),
                      P(lean=16, ua_f=100, fa_f=96, ua_b=-20, fa_b=20, th_f=30, sh_f=10, th_b=-26, face="yell")]
        A["taunt"] = [P(ua_f=150, fa_f=176, ua_b=-6, fa_b=60, lean=-4, face="grin"), P(ua_f=140, fa_f=160, ua_b=-6, fa_b=60, lean=-4, face="yell")]
        A["hop"] = [P(plant=False, lean=6, th_f=70, sh_f=-20, th_b=30, sh_b=-50, ua_f=140, fa_f=160, ua_b=120, fa_b=150, face="yell")]
        sit = dict(plant=False, hy=8, th_f=84, sh_f=6, th_b=80, sh_b=2)
        A["drive"] = [P(**sit, lean=6, ua_f=58, fa_f=96, ua_b=52, fa_b=92, face="grin"), P(**{**sit, "hy": 9}, lean=8, head=2, ua_f=60, fa_f=98, ua_b=54, fa_b=94, face="grin")]
        A["honk"] = [P(**sit, lean=10, ua_f=70, fa_f=130, ua_b=52, fa_b=92, face="yell"), P(**sit, lean=-6, ua_f=60, fa_f=96, ua_b=160, fa_b=170, face="yell")]
        A["churt"] = [P(**{**sit, "sh_f": 30}, lean=-20, head=-12, ua_f=150, fa_f=170, ua_b=-140, fa_b=-160, face="hurt")]
        A["csleep"] = [P(**sit, lean=24, head=24, ua_f=10, fa_f=20, ua_b=4, fa_b=14, face="sleep")]
    for k in ("hurt", "fall", "down", "getup", "dizzy"):
        A[k] = base[k]
    A["held"] = [P(lean=-10, head=-10, ua_f=-20, fa_f=-40, ua_b=-30, fa_b=-60, face="hurt", lift=3)]
    A["sleep"] = [{**base["down"][0], "face": "sleep"}]
    sit = dict(plant=False, hy=8, th_f=84, sh_f=4, th_b=80, sh_b=0)
    A["wheel"] = [P(**sit, lean=10, ua_f=20, fa_f=50, ua_b=10, fa_b=44, face="grin"), P(**sit, lean=16, ua_f=50, fa_f=70, ua_b=40, fa_b=64, face="yell")]
    return A
