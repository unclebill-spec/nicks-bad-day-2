"""v0.13 PSYCH WARD characters (behavioral health unit), on the same side-view rig as everyone else.

Bill's rules: staff-sized (the nurses' build), everyday clothes with a SEPARATE top and bottom and a visible waist
(shirt hem, then a waistband / drawstring or belt, then pants). No onesie, no straitjacket costume, no padding or armor.
Comedic and kind: these are patients having a weird day, not monsters.
The boss "DR." PHIL-IN is a patient in a stolen white lab coat, ~1.3x a nurse standing.
"""
from __future__ import annotations

from rig import INK, P, vec
from chars import SKIN, hero_body, hero_anims, walk_cycle, holder, hair_cap, bald_ring, lab_coat, _frame

NURSE_BUILD = dict(thigh=10.5, shin=10.5, torso=16.5, head=6.6, uarm=8, farm=8, arm_w=3.6, leg_w=5.0, torso_w=12, fist=2.0, foot=2)
STREET = dict(vneck=False, steth=False, badge=None, eye_white=True)

SWEAT = ("#9aa2b0", "#747c8a")        # escapee: heather-grey sweatshirt
NAVY_SW = ("#2e3a62", "#1e2848")       # ...navy sweatpants
TEE_BLUE = ("#2a6ae8", "#1a48b0")      # cape guy: blue tee with a hand-drawn star
RED_SW = ("#c83a3a", "#962828")        # ...red sweatpants
CAPE = ("#7a3ab8", "#58248a", "#c49aff")  # violet fleece blanket cape (Bill's violet)
CARDI = ("#6a7a3a", "#4e5a28")         # tinfoil guy: olive cardigan
CORDS = ("#8a5a3a", "#64402a")
PJ_TOP = ("#9ad0f0", "#6aa8d0")        # sock-puppet guy: light-blue pajama top
PJ_PANTS = ("#3a4a8a", "#28346a")
GREG_GOWN = ("#c8d8d0", "#a4b6ae")   # GREG: pale mint-grey gown...
GREG_DOT = ("#5a6268", "#485056")    # ...with dark grey polka dots (not the olive check)
GREG_PJ = ("#9aa0a8", "#767c86")     # grey pajama bottoms under the gown (the waist tie shows: no onesie)
PHIL_SHIRT = ("#e8dc9a", "#c0b070")
PHIL_PANTS = ("#4a4a56", "#34343e")


# ---------------- tops
def sweat_top(S, T, hip, neck, lean, b):
    """Crew-neck sweatshirt: ribbed collar + a ribbed hem band over the drawstring sweatpants."""
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw = b["torso_w"]
    S.line(at(neck, 0.2, -tw * 0.1), at(neck, 0.2, tw * 0.45), SWEAT[1])
    S.line(at(hip, 1.6, -tw * 0.5), at(hip, 1.6, tw * 0.5), "#6a7280")


def star_tee(S, T, hip, neck, lean, b):
    """Blue tee with a lopsided marker star on the chest (homemade superhero)."""
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw = b["torso_w"]
    cx, cy = at(neck, -5.5, tw * 0.15)
    for dx, dy in ((0, -2), (-1, -1), (0, -1), (1, -1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (-1, 1), (1, 1), (-2, 2), (2, 2)):
        S.set(int(cx) + dx, int(cy) + dy, "#ffe84a")


def cardigan(S, T, hip, neck, lean, b):
    """Olive cardigan open over a cream tee, big buttons, a pocket full of pens and a folded map."""
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw = b["torso_w"]
    S.poly([at(neck, 0.2, tw * 0.15), at(neck, 0.2, tw * 0.42), at(hip, 1.5, tw * 0.42), at(hip, 1.5, tw * 0.2)], "#f0e6c8", rim=False)
    S.line(at(neck, 0, tw * 0.42), at(hip, 1.5, tw * 0.44), CARDI[1])
    for k in (0.3, 0.55, 0.8):
        x, y = at(neck, -b["torso"] * k, tw * 0.46)
        S.set(int(x), int(y), "#d8c060")
    px, py = at(neck, -5, -tw * 0.15)
    S.rect(int(px), int(py) - 2, 1, 2, "#e83a3a"); S.rect(int(px) + 1, int(py) - 2, 1, 2, "#2a5ad8"); S.rect(int(px) + 2, int(py) - 1, 2, 1, "#f4f4f4")


def pj_top(S, T, hip, neck, lean, b):
    """Pajama shirt: white piping on the collar and placket, three buttons."""
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw = b["torso_w"]
    S.poly([at(neck, 0.6, tw * 0.05), at(neck, 0.6, tw * 0.48), at(neck, -2.2, tw * 0.36)], "#f4f8ff", rim=False)
    S.line(at(neck, -1, tw * 0.38), at(hip, 1.5, tw * 0.38), "#f4f8ff")
    for k in (0.35, 0.6, 0.85):
        x, y = at(neck, -b["torso"] * k, tw * 0.42)
        S.set(int(x), int(y), "#2a3a6a")


def phil_coat(S, T, hip, neck, lean, b):
    """The stolen lab coat (the Lab-Coat Hugger's open coat) + a big fake gold badge that says MD in crayon."""
    lab_coat(S, T, hip, neck, lean, b)
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw = b["torso_w"]
    x, y = at(neck, -4.5, tw * 0.05)
    S.rect(int(x) - 1, int(y) - 1, 6, 5, INK); S.rect(int(x), int(y), 4, 3, "#ffd84a"); S.set(int(x) + 1, int(y) + 1, "#e83a3a"); S.set(int(x) + 2, int(y) + 1, "#e83a3a")
    # stethoscope draped round the neck, ear tips up, the bell on the chest
    S.line(at(neck, 0.5, -tw * 0.3), at(neck, -6, tw * 0.25), "#3a3f4a"); S.line(at(neck, 0.5, tw * 0.45), at(neck, -6, tw * 0.25), "#3a3f4a")
    bx, by = at(neck, -6.5, tw * 0.25)
    S.rect(int(bx) - 1, int(by), 3, 2, "#c8ccd6")


def greg_tie(S, T, hip, neck, lean, b):
    """Greg's gown: a V-neck with a soft bias edge, the back opening line, and a fabric tie knotted at the waist."""
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw = b["torso_w"]
    S.line(at(hip, 3.2, -tw * 0.5), at(hip, 3.2, tw * 0.5), GREG_GOWN[1])
    S.line(at(hip, 2.4, -tw * 0.5), at(hip, 2.4, tw * 0.5), "#8a9a92")
    x, y = at(hip, 2.8, tw * 0.3)
    S.set(int(x), int(y) + 1, "#8a9a92"); S.set(int(x) + 1, int(y) + 2, "#8a9a92")


def greg_dots(img):
    """Post-process: dark grey polka dots on every gown pixel, on a fixed staggered grid (like gown_check)."""
    hx = lambda c: tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
    b0, b1 = hx(GREG_GOWN[0]), hx(GREG_GOWN[1])
    d0, d1 = hx(GREG_DOT[0]), hx(GREG_DOT[1])
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            q = px[x, y]
            if q[3] == 0 or q[:3] not in (b0, b1):
                continue
            if y % 3 == 1 and (x + (1 if (y // 3) % 2 else 0)) % 3 == 0:
                px[x, y] = (d1 if q[:3] == b1 else d0) + (255,)
    return img


# ---------------- hair / hats / backs
def neck_pillow(S, hc, r, b, pose):
    """GREG: short swept-back grey hair, and a grey travel neck pillow worn on top of his head like a crown, snap at the front."""
    hair_cap(top=-0.35, back=0.3, grow=0.7, seed=41, fringe=0)(S, hc, r, b, pose)
    S.line((hc[0] - r * 0.7, hc[1] - r * 0.75), (hc[0] + r * 0.2, hc[1] - r * 0.95), "#c8ccd4")
    cy = hc[1] - r * 1.05
    S.ellipse((hc[0] - r * 0.1, cy), r * 1.35, r * 0.55, "#8a8e96", "#5e626a")
    S.ellipse((hc[0] - r * 0.1, cy - r * 0.12), r * 0.6, r * 0.2, "#4a4e56", None, rim=False)
    S.line((hc[0] - r * 1.1, cy - r * 0.3), (hc[0] + r * 0.7, cy - r * 0.42), "#aeb2ba")
    S.rect(int(hc[0] + r * 1.05), int(cy) - 1, 3, 3, INK); S.set(int(hc[0] + r * 1.05) + 1, int(cy), "#c8ccd6")



def foil_hat(S, hc, r, b, pose):
    """A tinfoil hat: a crinkled silver cone with a little antenna curl. Messy hair sticks out under it."""
    hair_cap(top=-0.1, back=0.45, grow=1.2, spikes=3, seed=31)(S, hc, r, b, pose)
    cx, top = hc[0] - r * 0.1, hc[1] - r * 2.3
    S.poly([(hc[0] - r * 1.05, hc[1] - r * 0.55), (hc[0] + r * 0.95, hc[1] - r * 0.55), (cx, top)], "#c8ccd6")
    for k, (dx, dy) in enumerate(((-0.5, -0.8), (0.2, -1.2), (-0.1, -1.6), (0.45, -0.75))):
        S.set(int(hc[0] + r * dx), int(hc[1] + r * dy), "#ffffff" if k % 2 else "#8a909c")
    S.line((hc[0] - r * 1.05, hc[1] - r * 0.55), (hc[0] + r * 0.95, hc[1] - r * 0.55), "#9aa0ac")
    S.line((cx, top), (cx + 2, top - 2), "#c8ccd6"); S.set(int(cx) + 3, int(top) - 2, "#ffffff")


def cape_back(S, hc, r, b, pose):
    """A violet fleece blanket tied round the neck, hanging down the back to the knees (a hero needs a cape)."""
    sw = pose.get("tail", 0)
    n = (hc[0] - r * 0.3, hc[1] + r * 1.1)
    S.poly([(n[0] + r * 0.4, n[1]), (n[0] - r * 0.6, n[1] - r * 0.1), (n[0] - r * 2.2 - sw, n[1] + r * 3.6), (n[0] - r * 0.4 - sw * 0.5, n[1] + r * 3.9)], CAPE[0])
    S.line((n[0] - r * 0.6, n[1]), (n[0] - r * 2.1 - sw, n[1] + r * 3.5), CAPE[2])
    S.line((n[0] - r * 1.4 - sw * 0.7, n[1] + r * 3.75), (n[0] - r * 0.5 - sw * 0.5, n[1] + r * 3.85), CAPE[1])
    S.rect(int(n[0] - 1), int(n[1] - 1), 3, 2, "#ffe84a")  # the knot (a hair clip)


def bedhead(S, hc, r, b, pose):
    hair_cap(top=-0.25, back=0.4, grow=1.4, spikes=5, seed=33)(S, hc, r, b, pose)


def doc_hair(S, hc, r, b, pose):
    """Phil-in: a confident grey side part and a pen behind the ear."""
    hair_cap(top=-0.25, back=0.35, grow=0.8, seed=35, fringe=0)(S, hc, r, b, pose)
    S.line((hc[0] - r * 0.2, hc[1] - r * 0.4), (hc[0] + r * 0.3, hc[1] - r * 0.1), "#2a5ad8")


# ---------------- held things
def pholder(kind):
    def h(S, T, hand, ang, b):
        hx, hy = T(hand)
        tan, buck = "#e8d8b0", "#3a8ae8"
        if kind == "strap":  # a loose soft restraint: padded cuff on the wrist, the strap dangling to the floor
            S.rect(int(hx) - 2, int(hy) - 1, 5, 3, tan); S.set(int(hx), int(hy), buck)
            S.line((hx, hy + 2), (hx - 2, hy + 10), tan); S.line((hx - 2, hy + 10), (hx + 2, hy + 16), tan)
        elif kind == "strap_up":
            S.rect(int(hx) - 2, int(hy) - 1, 5, 3, tan)
            S.line((hx, hy), (hx - 8, hy - 6), tan); S.line((hx - 8, hy - 6), (hx - 14, hy - 2), tan); S.set(int(hx) - 14, int(hy) - 2, buck)
        elif kind == "strap_out":  # cracked like a whip
            S.rect(int(hx) - 2, int(hy) - 1, 5, 3, tan)
            S.line((hx, hy), (hx + 12, hy - 3), tan); S.line((hx + 12, hy - 3), (hx + 22, hy + 1), tan); S.line((hx + 22, hy + 1), (hx + 30, hy - 1), tan)
            S.rect(int(hx) + 29, int(hy) - 2, 3, 3, buck)
        elif kind == "puppet":  # a striped sock puppet with button eyes and a red felt tongue
            S.rect(int(hx) - 2, int(hy) - 5, 7, 7, INK); S.rect(int(hx) - 1, int(hy) - 4, 5, 5, "#f4f4f4")
            S.rect(int(hx) - 1, int(hy) - 2, 5, 1, "#e83a3a"); S.rect(int(hx) - 1, int(hy), 5, 1, "#e83a3a")
            S.set(int(hx) + 1, int(hy) - 4, INK); S.set(int(hx) + 3, int(hy) - 4, INK); S.rect(int(hx) + 4, int(hy) - 1, 2, 1, "#ff6a8a")
        elif kind == "puppet_bite":
            S.rect(int(hx) - 1, int(hy) - 6, 9, 9, INK); S.rect(int(hx), int(hy) - 5, 7, 7, "#f4f4f4")
            S.rect(int(hx), int(hy) - 3, 7, 1, "#e83a3a"); S.rect(int(hx) + 4, int(hy) - 2, 4, 3, "#c81a3a")
            S.set(int(hx) + 2, int(hy) - 5, INK); S.set(int(hx) + 5, int(hy) - 5, INK)
        elif kind == "foil":  # a tinfoil ball, ready to throw
            S.ellipse((hx + 1, hy - 1), 2.2, 2.2, "#c8ccd6", "#8a909c", rim=True); S.set(int(hx), int(hy) - 2, "#ffffff")
        elif kind == "clip":  # Phil-in's clipboard (orders!)
            S.rect(int(hx) - 3, int(hy) - 8, 8, 11, INK); S.rect(int(hx) - 2, int(hy) - 7, 6, 9, "#b07a3e"); S.rect(int(hx) - 1, int(hy) - 6, 4, 7, "#f4f0e4")
            S.rect(int(hx), int(hy) - 9, 2, 2, "#c8ccd6"); S.rect(int(hx) - 1, int(hy) - 4, 4, 1, "#8a94a4"); S.rect(int(hx) - 1, int(hy) - 2, 3, 1, "#8a94a4")
        elif kind == "clip_up":
            S.rect(int(hx) - 6, int(hy) - 12, 11, 8, INK); S.rect(int(hx) - 5, int(hy) - 11, 9, 6, "#b07a3e"); S.rect(int(hx) - 4, int(hy) - 10, 7, 4, "#f4f0e4")
        elif kind == "pen":  # writing an order
            S.line((hx, hy), (hx + 3, hy - 4), "#2a5ad8"); S.set(int(hx) + 3, int(hy) - 4, "#ffffff")
        elif kind == "lasso_up":  # stethoscope twirled overhead
            S.ellipse((hx - 2, hy - 9), 6, 2.5, None, "#3a3f4a", rim=True); S.line((hx, hy), (hx - 2, hy - 7), "#3a3f4a")
            S.rect(int(hx) + 3, int(hy) - 10, 3, 2, "#c8ccd6")
        elif kind == "lasso_out":  # flung forward on its tube
            S.line((hx, hy), (hx + 14, hy - 2), "#3a3f4a"); S.line((hx + 14, hy - 2), (hx + 28, hy + 1), "#3a3f4a")
            S.ellipse((hx + 31, hy + 1), 3, 3, "#c8ccd6", "#8a909c", rim=True)
    return h


def bodies():
    sk = SKIN
    B = {}
    B["escapee"] = hero_body(**NURSE_BUILD, skin=sk["tan"][0], skin_s=sk["tan"][1], hair_c="#3a2a1a", hair_s="#1e140c", hair=bedhead, beard="#3a2a1a",
                             shirt=SWEAT[0], shirt_s=SWEAT[1], sleeve=SWEAT[0], sleeve_s=SWEAT[1], sleeve_len=1.7, sleeve_clip=True,
                             pants=NAVY_SW[0], pants_s=NAVY_SW[1], drawstring=True, drawstring_c="#f4f4f4", hem_c="#6a7280",
                             shoe="#c8d0dc", shoe_s="#8a94a4", pattern=sweat_top, **STREET)
    B["capeguy"] = hero_body(**{**NURSE_BUILD, "torso_w": 13}, skin=sk["fair"][0], skin_s=sk["fair"][1], hair_c="#e8b84a", hair_s="#b0842a",
                             hair=hair_cap(top=-0.2, back=0.3, grow=1.0, spikes=2, seed=37), hair_back=cape_back,
                             shirt=TEE_BLUE[0], shirt_s=TEE_BLUE[1], sleeve=TEE_BLUE[0], sleeve_s=TEE_BLUE[1], sleeve_len=0.5,
                             pants=RED_SW[0], pants_s=RED_SW[1], drawstring=True, drawstring_c="#ffe84a", shoe="#ffe84a", shoe_s="#c8a01a", pattern=star_tee, **STREET)
    B["tinfoil"] = hero_body(**NURSE_BUILD, skin=sk["light"][0], skin_s=sk["light"][1], hair_c="#8a6a4a", hair_s="#5a4430", hair=foil_hat, beard="#8a6a4a",
                             shirt=CARDI[0], shirt_s=CARDI[1], sleeve=CARDI[0], sleeve_s=CARDI[1], sleeve_len=1.7, sleeve_clip=True,
                             pants=CORDS[0], pants_s=CORDS[1], belt="#2a1a12", buckle="#c8ccd6", shoe="#4a3a2a", shoe_s="#2a2018", pattern=cardigan, glasses="#3a3a44", **STREET)
    B["puppet"] = hero_body(**NURSE_BUILD, skin=sk["brown"][0], skin_s=sk["brown"][1], hair_c="#1a1210", hair_s="#0c0806", hair=hair_cap(top=-0.3, back=0.2, grow=0.5, seed=39, fringe=0),
                            shirt=PJ_TOP[0], shirt_s=PJ_TOP[1], sleeve=PJ_TOP[0], sleeve_s=PJ_TOP[1], sleeve_len=1.7, sleeve_clip=True,
                            pants=PJ_PANTS[0], pants_s=PJ_PANTS[1], drawstring=True, drawstring_c="#f4f8ff", shoe="#8a5a3a", shoe_s="#5a3a24", pattern=pj_top, **STREET)
    # GREG (Bill's coworker-famous patient): older, deadpan, thick black glasses, stubble, mint-grey polka-dot gown tied at the
    # waist over grey pajama bottoms, yellow grip socks, and his travel neck pillow worn like a crown. Staff-sized.
    B["greg"] = hero_body(**NURSE_BUILD, skin="#e8b494", skin_s="#c08a6c", hair_c="#a8acb4", hair_s="#7a7e88", hair=neck_pillow, beard="#c49a86",
                          glasses="#14141a", heavy_lids=True, shirt=GREG_GOWN[0], shirt_s=GREG_GOWN[1], sleeve=GREG_GOWN[0], sleeve_s=GREG_GOWN[1], sleeve_len=0.5,
                          pants=GREG_PJ[0], pants_s=GREG_PJ[1], band="#8a9a92", drawstring=False, hem_c=GREG_GOWN[1],
                          shoe="#f6d63a", shoe_s="#c09e1a", foot_len=3.6, pattern=greg_tie, vneck=True, steth=False, badge=None, eye_white=True)
    B["greg"]["post"] = greg_dots
    # "DR." PHIL-IN: ~1.3x a nurse; stolen open lab coat over a pale-yellow shirt + tie, belt and charcoal slacks, fake badge, stethoscope.
    B["philin"] = hero_body(thigh=14.5, shin=14, torso=22, head=8.6, uarm=10.5, farm=10.5, arm_w=4.4, leg_w=6.0, torso_w=15, fist=2.4, foot=2, foot_len=4.4,
                            skin=sk["light"][0], skin_s=sk["light"][1], hair_c="#9aa0ac", hair_s="#6a707c", hair=doc_hair, glasses="#2a2a34",
                            shirt=PHIL_SHIRT[0], shirt_s=PHIL_SHIRT[1], sleeve="#f2f4f8", sleeve_s="#c4cad6", sleeve_len=1.75, sleeve_clip=True,
                            pants=PHIL_PANTS[0], pants_s=PHIL_PANTS[1], belt="#1a1a20", buckle="#d8dce4", shoe="#3a2416", shoe_s="#24160c",
                            pattern=phil_coat, **STREET)
    return B


def anims(kind):
    A = {}
    base = hero_anims("nick")
    if kind == "escapee":  # cracks the loose restraint strap like a whip (bell AI: the snap dizzies)
        st = pholder("strap")
        A["idle"] = [P(ua_f=10, fa_f=30, ua_b=-6, fa_b=20, hold=st, face="grin"), P(ua_f=10, fa_f=36, ua_b=-6, fa_b=20, hold=st, hy=1, face="grin")]
        A["walk"] = walk_cycle(swing=16, arm=8)
        for f in A["walk"]:
            f.update(ua_f=10, fa_f=30, hold=st)
        A["atk"] = [P(lean=-12, ua_f=-150, fa_f=-160, ua_b=30, fa_b=60, th_f=20, th_b=-24, hold=pholder("strap_up"), face="grin"),
                    P(lean=14, ua_f=90, fa_f=92, ua_b=-20, fa_b=30, th_f=30, sh_f=10, th_b=-26, hold=pholder("strap_out"), face="yell")]
    elif kind == "capeguy":  # fists on hips; the "flying" charge (sundowner AI), cape streaming
        A["idle"] = [P(ua_f=-30, fa_f=-120, ua_b=-30, fa_b=-120, lean=-4, face="grin", tail=0), P(ua_f=-30, fa_f=-120, ua_b=-30, fa_b=-120, lean=-4, hy=1, face="grin", tail=1)]
        A["walk"] = walk_cycle(swing=18, arm=10, lean=6)
        for i, f in enumerate(A["walk"]):
            f.update(face="grin", tail=2 + (i % 2))
        A["atk"] = walk_cycle(swing=36, arm=0, lean=34, bob=2)
        for i, f in enumerate(A["atk"]):
            f.update(ua_f=100, fa_f=96, ua_b=-70, fa_b=-50, head=-10, face="yell", tail=6 + (i % 2) * 2)
    elif kind == "tinfoil":  # rolls up tinfoil balls and lobs them (tray AI)
        fl = pholder("foil")
        A["idle"] = [P(ua_f=60, fa_f=150, hold=fl, ua_b=-6, fa_b=20, face="norm"), P(ua_f=64, fa_f=160, hold=fl, ua_b=-6, fa_b=20, hy=1, head=-6, face="yell")]
        A["walk"] = walk_cycle(swing=16, arm=8)
        for f in A["walk"]:
            f.update(ua_f=60, fa_f=150, hold=fl, head=-4)
        A["atk"] = [P(lean=-12, ua_f=-150, fa_f=-165, ua_b=40, fa_b=80, th_f=20, th_b=-24, hold=fl, face="yell"),
                    P(lean=14, ua_f=100, fa_f=96, ua_b=-20, fa_b=20, th_f=30, sh_f=10, th_b=-26, face="yell")]
        A["lob"] = A["atk"]
    elif kind == "puppet":  # chats with his sock puppet; the puppet "bites" (escape AI: slap and scoot)
        pp = pholder("puppet")
        A["idle"] = [P(ua_f=70, fa_f=150, hold=pp, ua_b=-6, fa_b=20, face="grin"), P(ua_f=74, fa_f=160, hold=pholder("puppet_bite"), ua_b=-6, fa_b=20, hy=1, face="norm")]
        A["walk"] = walk_cycle(swing=18, arm=8)
        for f in A["walk"]:
            f.update(ua_f=70, fa_f=150, hold=pp)
        A["atk"] = [P(lean=-8, ua_f=40, fa_f=80, ua_b=-20, fa_b=30, hold=pp, face="grin"),
                    P(lean=16, ua_f=88, fa_f=90, ua_b=-20, fa_b=30, th_f=26, th_b=-24, hold=pholder("puppet_bite"), face="yell")]
    elif kind == "greg":  # deadpan; whips his neck pillow off his head like a boomerang (tray-style thrower AI)
        A["idle"] = [P(ua_f=10, fa_f=20, ua_b=-6, fa_b=14, face="norm"), P(ua_f=10, fa_f=24, ua_b=-6, fa_b=16, hy=1, head=-4, face="grin")]
        A["walk"] = walk_cycle(swing=14, arm=6, lean=2)
        A["atk"] = [P(lean=-10, ua_f=-160, fa_f=-175, ua_b=30, fa_b=60, th_f=18, th_b=-22, face="yell"),
                    P(lean=14, ua_f=96, fa_f=92, ua_b=-20, fa_b=20, th_f=30, sh_f=10, th_b=-26, face="yell")]
        A["lob"] = A["atk"]
        A["sing"] = [P(ua_f=60, fa_f=120, ua_b=40, fa_b=100, head=-10, lean=-4, face="grin"), P(ua_f=70, fa_f=140, ua_b=50, fa_b=120, head=-12, lean=-6, hy=1, face="yell")]
    elif kind == "philin":
        cl = pholder("clip")
        A["idle"] = [P(ua_f=40, fa_f=130, hold=cl, ua_b=-6, fa_b=60, lean=-3, face="grin"), P(ua_f=44, fa_f=136, hold=cl, ua_b=-6, fa_b=64, lean=-3, hy=1, face="norm")]
        A["walk"] = walk_cycle(swing=18, arm=10, lean=4)
        for f in A["walk"]:
            f.update(ua_f=40, fa_f=130, hold=cl)
        A["swing"] = [P(lean=-10, ua_f=-140, fa_f=-150, hold=pholder("clip_up"), ua_b=-20, fa_b=40, th_f=16, th_b=-20, face="grin"),
                      P(lean=18, ua_f=88, fa_f=90, hold=cl, ua_b=-30, fa_b=30, th_f=30, sh_f=10, th_b=-26, face="yell")]
        A["write"] = [P(ua_f=60, fa_f=150, hold=cl, ua_b=50, fa_b=140, hold_b=pholder("pen"), lean=-2, head=8, face="norm"),
                      P(ua_f=60, fa_f=150, hold=cl, ua_b=56, fa_b=150, hold_b=pholder("pen"), lean=-2, head=10, face="grin"),
                      P(ua_f=150, fa_f=170, hold=pholder("clip_up"), ua_b=-6, fa_b=60, lean=-6, face="yell")]
        A["lasso"] = [P(lean=-8, ua_f=-160, fa_f=-170, hold=pholder("lasso_up"), ua_b=-20, fa_b=40, face="grin"),
                      P(lean=-8, ua_f=-150, fa_f=-180, hold=pholder("lasso_up"), ua_b=-20, fa_b=40, hy=1, face="grin"),
                      P(lean=16, ua_f=86, fa_f=88, hold=pholder("lasso_out"), ua_b=-30, fa_b=30, th_f=28, sh_f=8, th_b=-24, face="yell")]
        A["taunt"] = [P(ua_f=150, fa_f=176, ua_b=-6, fa_b=60, lean=-6, face="grin"), P(ua_f=140, fa_f=160, ua_b=-6, fa_b=60, lean=-6, face="yell")]
    for k in ("hurt", "fall", "down", "getup", "dizzy"):
        A[k] = base[k]
    A["held"] = [P(lean=-10, head=-10, ua_f=-20, fa_f=-40, ua_b=-30, fa_b=-60, face="hurt", lift=3)]
    A["sleep"] = [{**base["down"][0], "face": "sleep"}]
    return A
