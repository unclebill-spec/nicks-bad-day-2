"""v0.15 LABOR & DELIVERY characters. Visitors on the nurse build, everyday clothes with a SEPARATE top and bottom and a
visible waist. Comedic: over-excited family, not monsters.
  camdad  - a screaming new dad with a camcorder (the flash dizzies)
  grandma - a grandma who WON'T LEAVE: cardigan over a blouse, slacks, a big purse to swing
  sibling - a big sibling (a teen) lobbing juice boxes
Boss THE STORK (a parody "special delivery" bird, not a mascot of any real brand): drawn directly (a bird does not fit the
human rig), ~1.5x a nurse standing. Mail-carrier cap, a satchel strap, carries a "baby" that is really a laundry sack."""
from __future__ import annotations

import math

from PIL import Image

from rig import INK, P, Raster, vec
from chars import SKIN, hero_body, hero_anims, walk_cycle, hair_cap, _frame
from v14_chars import NURSE_BUILD, STREET, JEANS, KHAKI

DAD_SHIRT = ("#5a9ad8", "#3a72b0")    # a light-blue button-up...
GMA_CARD = ("#a88ad8", "#7e64ae")    # lavender cardigan
GMA_PANTS = ("#8a8a9a", "#6a6a7a")
SIB_TEE = ("#f0b030", "#c08818")
SIB_PANTS = ("#4a4a5a", "#34343e")


def buttons(S, T, hip, neck, lean, b):
    """Button-up shirt: a placket of buttons and a pocket with a pen (dad energy)."""
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw = b["torso_w"]
    for k in range(2, 14, 3):
        x, y = at(neck, -k, tw * 0.35); S.set(int(x), int(y), "#e8f0ff")
    px, py = at(neck, -5, tw * 0.05); S.rect(int(px) - 1, int(py), 4, 3, DAD_SHIRT[1]); S.set(int(px), int(py) - 1, "#ff3a4a")


def cardigan(S, T, hip, neck, lean, b):
    """Cardigan open over a white blouse: the blouse shows down the front, big buttons, a brooch."""
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw = b["torso_w"]
    S.poly([at(neck, -0.5, tw * 0.2), at(neck, -0.5, tw * 0.5), at(hip, 2.5, tw * 0.5), at(hip, 2.5, tw * 0.3)], "#f4f0f8", rim=False)
    for k in (4, 8, 12):
        x, y = at(neck, -k, tw * 0.2); S.set(int(x), int(y), "#f4d84a")
    x, y = at(neck, -3, tw * 0.05); S.set(int(x), int(y), "#ff5a8a"); S.set(int(x) + 1, int(y), "#ffd0e0")


def tee(S, T, hip, neck, lean, b):
    """T-shirt with a little parody logo (a juice drop)."""
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw = b["torso_w"]
    x, y = at(neck, -6, tw * 0.25); S.rect(int(x) - 1, int(y), 3, 3, "#8a3ad8"); S.set(int(x), int(y) - 1, "#8a3ad8")


def gma_hair(S, hc, r, b, pose):
    """Silver curls with a bun on top."""
    hair_cap(top=-0.4, back=0.45, grow=1.2, spikes=5, seed=71)(S, hc, r, b, pose)
    S.ellipse((hc[0] - r * 0.3, hc[1] - r * 1.15), r * 0.55, r * 0.45, b["hair_c"], b["hair_s"])


def dad_hair(S, hc, r, b, pose):
    hair_cap(top=-0.3, back=0.3, grow=0.5, seed=73, fringe=0)(S, hc, r, b, pose)


def sib_hair(S, hc, r, b, pose):
    hair_cap(top=-0.5, back=0.6, grow=1.0, spikes=3, seed=75)(S, hc, r, b, pose)


def holder(kind):
    def h(S, T, hand, ang, b):
        hx, hy = T(hand)
        x, y = int(hx), int(hy)
        if kind in ("cam", "cam_flash"):  # a chunky camcorder, red REC light
            S.rect(x - 4, y - 5, 10, 6, INK); S.rect(x - 3, y - 4, 8, 4, "#3a3a44"); S.rect(x + 5, y - 4, 3, 3, INK)
            S.set(x - 2, y - 4, "#ff3a4a"); S.rect(x + 6, y - 3, 1, 1, "#bfe0ff")
            if kind == "cam_flash":
                S.ellipse((x + 10, y - 3), 4, 4, "#ffffff", None, rim=False); S.line((x + 6, y - 3), (x + 16, y - 3), "#bfe0ff")
        elif kind == "purse":  # a big boxy purse with a clasp
            S.line((x, y), (x, y + 4), "#5a2a3a"); S.rect(x - 4, y + 4, 9, 7, INK); S.rect(x - 3, y + 5, 7, 5, "#c8487a"); S.set(x, y + 5, "#f4d84a")
        elif kind == "purse_out":
            S.line((x, y), (x + 6, y), "#5a2a3a"); S.rect(x + 6, y - 4, 9, 7, INK); S.rect(x + 7, y - 3, 7, 5, "#c8487a"); S.set(x + 10, y - 3, "#f4d84a")
        elif kind == "juice":
            S.rect(x - 1, y - 4, 4, 5, INK); S.rect(x, y - 3, 2, 3, "#8a3ad8"); S.set(x + 2, y - 5, "#f4f4f4")
    return h


def bodies():
    sk = SKIN
    B = {}
    B["camdad"] = hero_body(**NURSE_BUILD, skin=sk["light"][0], skin_s=sk["light"][1], hair_c="#6a4a2a", hair_s="#4a3018", hair=dad_hair,
                            shirt=DAD_SHIRT[0], shirt_s=DAD_SHIRT[1], sleeve=DAD_SHIRT[0], sleeve_s=DAD_SHIRT[1], sleeve_len=0.5,
                            pants=KHAKI[0], pants_s=KHAKI[1], belt="#3a2416", buckle="#c8ccd6", shoe="#f4f4f4", shoe_s="#a8b2c0", pattern=buttons, **STREET)
    B["grandma"] = hero_body(**NURSE_BUILD, skin=sk["tan"][0], skin_s=sk["tan"][1], hair_c="#d8d8e4", hair_s="#a8a8b8", hair=gma_hair, glasses="#8a3a6a",
                             shirt=GMA_CARD[0], shirt_s=GMA_CARD[1], sleeve=GMA_CARD[0], sleeve_s=GMA_CARD[1], sleeve_len=1.7, sleeve_clip=True,
                             pants=GMA_PANTS[0], pants_s=GMA_PANTS[1], belt="#4a3a5a", buckle="#d8c060", shoe="#5a3a4a", shoe_s="#3a2430", pattern=cardigan, **STREET)
    B["sibling"] = hero_body(**NURSE_BUILD, skin=sk["brown"][0], skin_s=sk["brown"][1], hair_c="#1e140c", hair_s="#0e0a06", hair=sib_hair,
                             shirt=SIB_TEE[0], shirt_s=SIB_TEE[1], sleeve=SIB_TEE[0], sleeve_s=SIB_TEE[1], sleeve_len=0.45,
                             pants=SIB_PANTS[0], pants_s=SIB_PANTS[1], belt="#1a1a20", buckle="#c8ccd6", shoe="#e83a4a", shoe_s="#a8242e", pattern=tee, **STREET)
    return B


def anims(kind):
    A = {}
    base = hero_anims("nick")
    if kind == "camdad":  # camcorder up to his eye, screaming; the atk is the FLASH
        cm = holder("cam")
        A["idle"] = [P(ua_f=55, fa_f=165, hold=cm, ua_b=-6, fa_b=20, face="yell"), P(ua_f=58, fa_f=168, hold=cm, ua_b=-10, fa_b=-40, hy=1, face="grin")]
        A["walk"] = walk_cycle(swing=18, arm=8, lean=4)
        for f in A["walk"]:
            f.update(ua_f=55, fa_f=165, hold=cm)
        A["atk"] = [P(lean=-6, ua_f=60, fa_f=170, hold=cm, ua_b=-40, fa_b=-120, face="yell"),
                    P(lean=6, ua_f=85, fa_f=110, hold=holder("cam_flash"), ua_b=-40, fa_b=-120, th_f=16, th_b=-14, face="yell")]
        A["lob"] = A["atk"]
    elif kind == "grandma":  # purse swing (visitor AI)
        pu = holder("purse")
        A["idle"] = [P(ua_f=10, fa_f=60, hold=pu, ua_b=-6, fa_b=20, lean=4, face="norm"), P(ua_f=12, fa_f=64, hold=pu, ua_b=-6, fa_b=20, lean=4, hy=1, face="grin")]
        A["walk"] = walk_cycle(swing=12, arm=6, lean=6)
        for f in A["walk"]:
            f.update(ua_f=10, fa_f=60, hold=pu)
        A["atk"] = [P(lean=-10, ua_f=-150, fa_f=-160, hold=pu, ua_b=-20, fa_b=30, th_f=16, th_b=-20, face="yell"),
                    P(lean=14, ua_f=90, fa_f=92, hold=holder("purse_out"), ua_b=-20, fa_b=30, th_f=26, th_b=-24, face="yell")]
    elif kind == "sibling":  # juice box lobber (tray AI)
        jc = holder("juice")
        A["idle"] = [P(ua_f=60, fa_f=150, hold=jc, ua_b=-6, fa_b=20, face="grin"), P(ua_f=64, fa_f=156, hold=jc, ua_b=-6, fa_b=20, hy=1, head=-6, face="norm")]
        A["walk"] = walk_cycle(swing=18, arm=10)
        for f in A["walk"]:
            f.update(ua_f=60, fa_f=150, hold=jc)
        A["atk"] = [P(lean=-12, ua_f=-150, fa_f=-165, ua_b=40, fa_b=80, th_f=20, th_b=-24, hold=jc, face="yell"),
                    P(lean=14, ua_f=100, fa_f=96, ua_b=-20, fa_b=20, th_f=30, sh_f=10, th_b=-26, face="yell")]
        A["lob"] = A["atk"]
    for k in ("hurt", "fall", "down", "getup", "dizzy"):
        A[k] = base[k]
    A["held"] = [P(lean=-10, head=-10, ua_f=-20, fa_f=-40, ua_b=-30, fa_b=-60, face="hurt", lift=3)]
    A["sleep"] = [{**base["down"][0], "face": "sleep"}]
    return A


# ---------------------------------------------------------------- THE STORK (drawn directly)
SW, SH, SAX, SAY = 120, 112, 56, 106   # cell + anchor (feet on the ground line)
WHITE, WSH, BLACK, BEAK, BEAK_S, LEG = "#f8f8fc", "#c8ccdc", "#2a2a3a", "#ff8a3a", "#d0602a", "#ff6a4a"
CAP, CAP_S = "#3a5ad8", "#2a3a98"


def _wing(S, sx, sy, ang, span, spread):
    """A wing from the shoulder (sx, sy) at angle ang (deg, 0 = back/left, 90 = up). spread 0 = folded."""
    a = math.radians(ang)
    tip = (sx - math.cos(a) * span, sy - math.sin(a) * span)
    w = 5 + spread * 6
    n = (-math.sin(a) * w, math.cos(a) * w)
    S.poly([(sx, sy), (sx + n[0], sy + n[1]), (tip[0] + n[0] * 0.3, tip[1] + n[1] * 0.3), tip], WHITE)
    # black flight feathers along the outer half
    for k in range(4):
        f = 0.55 + k * 0.13
        px, py = sx + (tip[0] - sx) * f, sy + (tip[1] - sy) * f
        S.line((px, py), (px + n[0] * 1.1 - math.cos(a) * 3, py + n[1] * 1.1 - math.sin(a) * 3), BLACK)
    S.line((sx, sy), tip, WSH)


def stork_frame(pose):
    """pose: dict(leg=(l1, l2) foot x offsets, crouch, body tilt deg, neck (dx, dy) head offset, beak angle,
    wing angle/spread, eye ('n','x','sleep','dizzy'), sack 'beak'|'none'|'claw', lift (z px), honk (open beak)."""
    S = Raster(SW, SH)
    ax, ay = SAX, SAY - pose.get("lift", 0)
    cr = pose.get("crouch", 0)
    hip = (ax - 2, ay - 40 + cr)
    # legs: long thin orange-red stilts with a backward knee
    for i, fx in enumerate(pose.get("leg", (-6, 6))):
        if pose.get("tuck"):
            S.line((hip[0] + 3 * i, hip[1] + 2), (hip[0] - 12 + 3 * i, hip[1] + 14), LEG); continue
        knee = (hip[0] + fx * 0.5 - 4, hip[1] + 20 + cr * 0.3)
        foot = (ax + fx, ay - 1)
        S.line((hip[0] + 2 * i, hip[1]), knee, LEG); S.line(knee, foot, LEG)
        S.line(foot, (foot[0] + 5, foot[1]), LEG); S.line(foot, (foot[0] - 3, foot[1]), LEG)
    tilt = math.radians(pose.get("tilt", 0))
    bc = (hip[0] - 2, hip[1] - 10)
    # tail (black) then body
    tl = (bc[0] - 20 * math.cos(tilt), bc[1] + 4 + 20 * math.sin(tilt))
    S.poly([(bc[0] - 10, bc[1] - 3), tl, (tl[0] + 2, tl[1] + 5), (bc[0] - 8, bc[1] + 6)], BLACK)
    wa, wsp = pose.get("wing", (10, 0))
    back_wing = wsp > 0.3
    if back_wing:  # far wing behind the body when flapping
        _wing(S, bc[0] + 2, bc[1] - 7, wa + 14, 34 + wsp * 6, wsp * 0.8)
    S.ellipse(bc, 19, 11.5, WHITE, WSH)
    # the satchel strap (mail carrier parody) across the body
    S.line((bc[0] + 10, bc[1] - 9), (bc[0] - 4, bc[1] + 10), "#8a5a3a"); S.rect(int(bc[0]) - 8, int(bc[1]) + 7, 8, 6, "#a8743a"); S.rect(int(bc[0]) - 8, int(bc[1]) + 7, 8, 2, "#c8945a")
    # neck: a curved white S up to the head
    ndx, ndy = pose.get("neck", (10, -30))
    base_n = (bc[0] + 14, bc[1] - 5)
    head = (base_n[0] + ndx, base_n[1] + ndy)
    mid = ((base_n[0] + head[0]) / 2 - 4, (base_n[1] + head[1]) / 2 + 2)
    S.capsule(base_n, mid, 7, WHITE, WSH); S.capsule(mid, head, 6, WHITE, WSH)
    # beak (long orange wedge), open for a honk
    ba = math.radians(pose.get("beak", 10))
    bl = 24
    tip = (head[0] + 4 + math.cos(ba) * bl, head[1] + 1 + math.sin(ba) * bl)
    if pose.get("honk"):
        S.poly([(head[0] + 4, head[1] - 1), (tip[0], tip[1] - 6), (head[0] + 4, head[1] + 1)], BEAK)
        S.poly([(head[0] + 4, head[1] + 2), (tip[0], tip[1] + 3), (head[0] + 4, head[1] + 4)], BEAK_S)
    else:
        S.poly([(head[0] + 4, head[1] - 2), tip, (head[0] + 4, head[1] + 3)], BEAK)
        S.line((head[0] + 5, head[1] + 1), tip, BEAK_S)
    S.ellipse(head, 6.5, 6, WHITE, WSH)
    # red face patch + eye
    S.rect(int(head[0]) + 2, int(head[1]) - 1, 3, 3, "#ff3a4a")
    ex, ey = int(head[0]) + 2, int(head[1]) - 2
    e = pose.get("eye", "n")
    if e == "x":
        S.set(ex - 1, ey - 1, INK); S.set(ex + 1, ey + 1, INK); S.set(ex + 1, ey - 1, INK); S.set(ex - 1, ey + 1, INK); S.set(ex, ey, INK)
    elif e == "sleep":
        S.rect(ex - 1, ey, 3, 1, INK)
    elif e == "dizzy":
        S.set(ex, ey, INK); S.set(ex + 1, ey - 1, INK); S.set(ex - 1, ey + 1, INK)
    else:
        S.rect(ex - 1, ey - 1, 3, 3, "#ffffff"); S.rect(ex, ey - 1, 2, 2, INK)
    # mail-carrier cap with a brim and a stork-wing badge
    S.poly([(head[0] - 6, head[1] - 4), (head[0] + 4, head[1] - 4), (head[0] + 3, head[1] - 10), (head[0] - 5, head[1] - 10)], CAP)
    S.rect(int(head[0]) + 3, int(head[1]) - 5, 6, 2, CAP_S); S.set(int(head[0]) - 1, int(head[1]) - 8, "#ffe84a")
    # near wing (folded or flapping)
    if not back_wing:
        S.poly([(bc[0] + 12, bc[1] - 8), (bc[0] - 16, bc[1] - 4), (bc[0] - 24, bc[1] + 4), (bc[0] - 4, bc[1] + 6), (bc[0] + 10, bc[1] + 2)], WHITE)
        for k in range(4):
            S.line((bc[0] - 12 - k * 3, bc[1] - 2 + k), (bc[0] - 18 - k * 3, bc[1] + 4 + k), BLACK)
    else:
        _wing(S, bc[0] + 6, bc[1] - 6, wa, 38 + wsp * 6, wsp)
    # the "baby": a laundry sack hung from the beak tip (or claws)
    sk = pose.get("sack", "none")
    if sk in ("beak", "claw"):
        sx, sy = (tip[0] - 4, tip[1] + 2) if sk == "beak" else (hip[0] - 6, hip[1] + 16)
        S.line((sx, sy), (sx, sy + 4), "#c8ccd8")
        S.ellipse((sx, sy + 11), 7, 6, "#f4f4f8", "#c8ccd8"); S.rect(int(sx) - 3, int(sy) + 4, 7, 2, "#7ab8f0"); S.rect(int(sx) + 1, int(sy) + 14, 3, 1, "#a8d0f8")
    hand = (tip[0] - ax, tip[1] - SAY, 0, bc[0] - ax, bc[1] - SAY, head[0] - ax, head[1] - SAY)
    return S, [round(v, 1) for v in hand]


def stork_anims():
    A = {}
    A["idle"] = [dict(neck=(10, -30), beak=12, sack="beak"), dict(neck=(11, -29), beak=14, sack="beak", crouch=1)]
    A["walk"] = [dict(leg=(-12, 8), neck=(12, -28), beak=10, sack="beak"), dict(leg=(-2, 2), neck=(10, -30), beak=12, sack="beak", crouch=-1),
                 dict(leg=(8, -12), neck=(12, -28), beak=10, sack="beak"), dict(leg=(2, -2), neck=(10, -30), beak=12, sack="beak", crouch=-1)]
    A["peck"] = [dict(neck=(-2, -34), beak=-20, crouch=-2, wing=(20, 0), honk=True), dict(neck=(26, -6), beak=20, crouch=4, leg=(-14, 10))]
    A["charge"] = [dict(neck=(24, -8), beak=8, tilt=-10, leg=(-16, 12), wing=(10, 0.6)), dict(neck=(26, -6), beak=8, tilt=-10, leg=(10, -14), wing=(-10, 0.8))]
    A["flap"] = [dict(neck=(10, -28), beak=0, wing=(70, 1.0), honk=True, crouch=2), dict(neck=(10, -28), beak=0, wing=(-20, 1.0), honk=True)]
    A["fly"] = [dict(neck=(18, -18), beak=6, tilt=-14, wing=(80, 1.0), tuck=True, lift=6, sack="claw"), dict(neck=(18, -18), beak=6, tilt=-14, wing=(-30, 1.0), tuck=True, lift=6, sack="claw")]
    A["drop"] = [dict(neck=(14, -22), beak=30, tilt=-6, wing=(60, 1.0), tuck=True, lift=6), dict(neck=(14, -22), beak=30, tilt=-6, wing=(-20, 1.0), tuck=True, lift=6, honk=True)]
    A["shout"] = [dict(neck=(4, -34), beak=-30, honk=True, wing=(40, 0.7), sack="none"), dict(neck=(5, -33), beak=-34, honk=True, wing=(60, 0.9), crouch=-1)]
    A["hurt"] = [dict(neck=(-4, -28), beak=-10, eye="x", honk=True, crouch=2, tilt=10)]
    A["fall"] = [dict(neck=(-10, -20), beak=-30, eye="x", honk=True, tilt=20, wing=(40, 0.8))]
    A["down"] = [dict(neck=(18, 6), beak=30, eye="x", crouch=24, tilt=0, tuck=True, wing=(10, 0))]
    A["getup"] = [dict(neck=(10, -14), beak=10, eye="dizzy", crouch=10)]
    A["dizzy"] = [dict(neck=(6, -26), beak=24, eye="dizzy", crouch=2), dict(neck=(12, -28), beak=0, eye="dizzy", crouch=1)]
    A["sleep"] = [dict(neck=(18, 6), beak=30, eye="sleep", crouch=24, tuck=True)]
    A["held"] = A["hurt"]
    return A


def stork_sheet(path, cols=10):
    frames, meta = [], {}
    for an, poses in stork_anims().items():
        start = len(frames); hs = []
        for p in poses:
            S, h = stork_frame(p); frames.append(S.image()); hs.append(h)
        meta[an] = {"s": start, "n": len(poses), "h": hs}
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGBA", (SW * cols, SH * rows), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f, ((i % cols) * SW, (i // cols) * SH))
    sheet.save(path, optimize=True)
    return {"img": "art/stork.png", "cell": [SW, SH], "anchor": [SAX, SAY], "cols": cols, "anims": meta}


def stork_face():
    """36x36 portrait crop around the head."""
    S, h = stork_frame(dict(neck=(10, -30), beak=12, honk=True))
    im = S.image().resize((SW * 2, SH * 2), Image.NEAREST)
    hx, hy = (SAX + h[5]) * 2, (SAY + h[6]) * 2
    return im.crop((int(hx) - 22, int(hy) - 24, int(hx) + 14, int(hy) + 12))
