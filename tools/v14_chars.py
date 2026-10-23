"""v0.14 CAFETERIA characters on the side-view rig. Staff-sized (the nurses' build), everyday clothes with a SEPARATE top and
bottom and a visible waist. Comedic: hungry visitors and patients, not monsters.
Boss LUNCH LADY LORETTA: ~1.3x a nurse standing, hairnet, a bib apron tied at the waist over a top, belt + slacks. Flat torso."""
from __future__ import annotations

from rig import INK, P, vec
from chars import SKIN, hero_body, hero_anims, walk_cycle, hair_cap, _frame

NURSE_BUILD = dict(thigh=10.5, shin=10.5, torso=16.5, head=6.6, uarm=8, farm=8, arm_w=3.6, leg_w=5.0, torso_w=12, fist=2.0, foot=2)
STREET = dict(vneck=False, steth=False, badge=None, eye_white=True)
HOODIE = ("#c8343a", "#962228")
JEANS = ("#3a5a9a", "#28407a")
POLO = ("#2a9a8a", "#1e706a")
KHAKI = ("#c8b080", "#9a8660")
LL_TOP = ("#e88ab8", "#b8648e")     # Loretta: a pink top...
LL_PANTS = ("#3a3a4a", "#28283a")   # ...charcoal slacks
APRON = ("#f4f4f4", "#c8ccd6")


def hoodie(S, T, hip, neck, lean, b):
    """Hoodie: hood bunched at the neck, a kangaroo pocket, ribbed hem band above the jeans' belt."""
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw = b["torso_w"]
    S.line(at(neck, 0.5, -tw * 0.4), at(neck, -1, tw * 0.1), HOODIE[1])
    S.line(at(hip, 5, -tw * 0.1), at(hip, 5, tw * 0.4), HOODIE[1]); S.line(at(hip, 5, tw * 0.4), at(hip, 2.2, tw * 0.45), HOODIE[1])
    S.line(at(hip, 1.6, -tw * 0.5), at(hip, 1.6, tw * 0.5), "#7a1a20")


def polo(S, T, hip, neck, lean, b):
    """Polo shirt: a white collar, two buttons, a little parody croc-ish logo (a lizard dot)."""
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw = b["torso_w"]
    S.line(at(neck, 0.4, tw * 0.05), at(neck, 0.4, tw * 0.45), "#f4f4f4")
    for k in (2, 4):
        x, y = at(neck, -k, tw * 0.4); S.set(int(x), int(y), "#f4f4f4")
    x, y = at(neck, -5, tw * 0.05); S.set(int(x), int(y), "#ffe84a")


def apron(S, T, hip, neck, lean, b):
    """Bib apron over the top: the bib, neck strap, a pocket with a pen, and the TIE at the waist (the waist stays visible)."""
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    at, hang = _frame(up, fwd, T)
    tw = b["torso_w"]
    S.poly([at(neck, -2.0, -tw * 0.15), at(neck, -2.0, tw * 0.5), at(hip, 2.6, tw * 0.52), at(hip, 2.6, -tw * 0.3)], APRON[0], rim=False)
    S.line(at(neck, 0.5, -tw * 0.1), at(neck, -2.5, tw * 0.08), APRON[1])
    S.line(at(hip, 2.6, -tw * 0.5), at(hip, 2.6, tw * 0.5), APRON[1])
    x, y = at(hip, 2.4, -tw * 0.45); S.set(int(x) - 1, int(y) + 1, APRON[0]); S.set(int(x) - 2, int(y) + 2, APRON[0])
    px, py = at(hip, 6, tw * 0.28)
    S.rect(int(px) - 2, int(py), 5, 3, APRON[1]); S.set(int(px), int(py) - 1, "#2a5ad8")
    nx, ny = at(neck, -5, tw * 0.25)
    S.rect(int(nx) - 3, int(ny), 7, 3, "#2a5ad8"); S.rect(int(nx) - 2, int(ny) + 1, 5, 1, "#ffffff")  # name tag LORETTA


def hairnet(S, hc, r, b, pose):
    """Loretta: curly hair in a bun, all of it under a hairnet (a fine net dot pattern), a pencil tucked in."""
    hair_cap(top=-0.35, back=0.5, grow=1.4, spikes=4, seed=51)(S, hc, r, b, pose)
    S.ellipse((hc[0] - r * 1.0, hc[1] - r * 0.6), r * 0.6, r * 0.55, b["hair_c"], b["hair_s"])
    for k in range(-5, 6):
        for j in range(4):
            x, y = hc[0] + k * r * 0.22, hc[1] - r * (0.9 - j * 0.25)
            if (k + j) % 2 == 0:
                S.set(int(x), int(y), "#e8e0f0")
    S.line((hc[0] - r * 1.15, hc[1] - r * 0.15), (hc[0] + r * 0.9, hc[1] - r * 0.35), "#d8d0e4")


def cap_back(S, hc, r, b, pose):
    hair_cap(top=-0.3, back=0.3, grow=0.6, seed=53, fringe=0)(S, hc, r, b, pose)
    S.rect(int(hc[0] - r * 1.0), int(hc[1] - r * 0.95), int(r * 2.0), int(r * 0.5) + 1, "#2a5ad8")  # a ball cap...
    S.rect(int(hc[0] + r * 0.9), int(hc[1] - r * 0.6), int(r * 0.9), 2, "#1a3a98")  # ...and its brim


def cholder(kind):
    def h(S, T, hand, ang, b):
        hx, hy = T(hand)
        if kind == "tray":  # a lunch tray held flat
            S.rect(int(hx) - 7, int(hy) - 2, 15, 3, INK); S.rect(int(hx) - 6, int(hy) - 2, 13, 2, "#c8844a")
            S.rect(int(hx) - 4, int(hy) - 4, 4, 2, "#5ac83a"); S.rect(int(hx) + 1, int(hy) - 4, 4, 2, "#3ae870")
        elif kind == "cup":  # dressing cup
            S.rect(int(hx) - 1, int(hy) - 3, 4, 4, INK); S.rect(int(hx), int(hy) - 2, 2, 3, "#ffffff"); S.set(int(hx), int(hy) - 3, "#f4ecd8")
        elif kind == "ladle":  # the giant ladle, bowl down
            S.line((hx, hy), (hx + 2, hy + 20), "#c8ccd6"); S.ellipse((hx + 3, hy + 23), 5, 3.5, "#c8ccd6", "#8a94a4")
        elif kind == "ladle_up":
            S.line((hx, hy), (hx - 6, hy - 20), "#c8ccd6"); S.ellipse((hx - 7, hy - 23), 5, 3.5, "#c8ccd6", "#8a94a4"); S.rect(int(hx) - 9, int(hy) - 25, 4, 2, "#ffb04a")
        elif kind == "ladle_out":
            S.line((hx, hy), (hx + 22, hy + 2), "#c8ccd6"); S.ellipse((hx + 26, hy + 2), 5, 3.5, "#c8ccd6", "#8a94a4")
        elif kind == "meat":
            S.ellipse((hx + 1, hy - 1), 3.5, 2.5, "#8a6a5a", "#5a4038")
    return h


def bodies():
    sk = SKIN
    B = {}
    B["linecut"] = hero_body(**NURSE_BUILD, skin=sk["light"][0], skin_s=sk["light"][1], hair_c="#3a2a1a", hair_s="#1e140c", hair=cap_back,
                             shirt=HOODIE[0], shirt_s=HOODIE[1], sleeve=HOODIE[0], sleeve_s=HOODIE[1], sleeve_len=1.7, sleeve_clip=True,
                             pants=JEANS[0], pants_s=JEANS[1], belt="#2a1a12", buckle="#c8ccd6", shoe="#f4f4f4", shoe_s="#a8b2c0", pattern=hoodie, **STREET)
    B["onside"] = hero_body(**NURSE_BUILD, skin=sk["tan"][0], skin_s=sk["tan"][1], hair_c="#5a4a3a", hair_s="#3a2e24",
                            hair=hair_cap(top=-0.3, back=0.25, grow=0.5, seed=55, fringe=0), glasses="#2a2a34",
                            shirt=POLO[0], shirt_s=POLO[1], sleeve=POLO[0], sleeve_s=POLO[1], sleeve_len=0.5,
                            pants=KHAKI[0], pants_s=KHAKI[1], belt="#3a2416", buckle="#d8c060", shoe="#5a3a24", shoe_s="#3a2416", pattern=polo, **STREET)
    # LUNCH LADY LORETTA: ~1.3x a nurse. Pink top, bib apron tied at the waist, belt + charcoal slacks, hairnet, giant ladle.
    B["lunchlady"] = hero_body(thigh=14, shin=13.5, torso=21, head=8.6, uarm=10.5, farm=10.5, arm_w=4.4, leg_w=6.0, torso_w=14.5, fist=2.4, foot=2, foot_len=4.4,
                               skin=sk["brown"][0], skin_s=sk["brown"][1], hair_c="#6a5a6a", hair_s="#4a3e4a", hair=hairnet,
                               shirt=LL_TOP[0], shirt_s=LL_TOP[1], sleeve=LL_TOP[0], sleeve_s=LL_TOP[1], sleeve_len=0.55,
                               pants=LL_PANTS[0], pants_s=LL_PANTS[1], belt="#1a1a20", buckle="#d8dce4", shoe="#f4f4f4", shoe_s="#a8b2c0",
                               pattern=apron, **STREET)
    return B


def anims(kind):
    A = {}
    base = hero_anims("nick")
    if kind == "linecut":  # cuts the line holding his tray; tray-slap and scoot (escape AI)
        tr = cholder("tray")
        A["idle"] = [P(ua_f=40, fa_f=110, hold=tr, ua_b=-6, fa_b=20, face="grin"), P(ua_f=44, fa_f=116, hold=tr, ua_b=-6, fa_b=20, hy=1, face="norm")]
        A["walk"] = walk_cycle(swing=18, arm=8, lean=6)
        for f in A["walk"]:
            f.update(ua_f=40, fa_f=110, hold=tr)
        A["atk"] = [P(lean=-8, ua_f=-120, fa_f=-140, hold=tr, ua_b=-20, fa_b=30, face="grin"),
                    P(lean=16, ua_f=88, fa_f=90, hold=tr, ua_b=-20, fa_b=30, th_f=26, th_b=-24, face="yell")]
    elif kind == "onside":  # "on the side!": flicks ranch cups (tray AI)
        cp = cholder("cup")
        A["idle"] = [P(ua_f=60, fa_f=150, hold=cp, ua_b=-6, fa_b=20, face="norm"), P(ua_f=64, fa_f=156, hold=cp, ua_b=-6, fa_b=20, hy=1, head=-6, face="yell")]
        A["walk"] = walk_cycle(swing=16, arm=8)
        for f in A["walk"]:
            f.update(ua_f=60, fa_f=150, hold=cp)
        A["atk"] = [P(lean=-12, ua_f=-150, fa_f=-165, ua_b=40, fa_b=80, th_f=20, th_b=-24, hold=cp, face="yell"),
                    P(lean=14, ua_f=100, fa_f=96, ua_b=-20, fa_b=20, th_f=30, sh_f=10, th_b=-26, face="yell")]
        A["lob"] = A["atk"]
    elif kind == "lunchlady":
        ld = cholder("ladle")
        A["idle"] = [P(ua_f=20, fa_f=40, hold=ld, ua_b=-30, fa_b=-120, lean=-3, face="norm"), P(ua_f=22, fa_f=44, hold=ld, ua_b=-30, fa_b=-120, lean=-3, hy=1, face="grin")]
        A["walk"] = walk_cycle(swing=16, arm=8, lean=4)
        for f in A["walk"]:
            f.update(ua_f=20, fa_f=40, hold=ld)
        A["swing"] = [P(lean=-10, ua_f=-150, fa_f=-160, hold=cholder("ladle_up"), ua_b=-20, fa_b=40, th_f=16, th_b=-20, face="grin"),
                      P(lean=18, ua_f=88, fa_f=90, hold=cholder("ladle_out"), ua_b=-30, fa_b=30, th_f=30, sh_f=10, th_b=-26, face="yell")]
        A["scoop"] = [P(lean=10, ua_f=120, fa_f=150, hold=ld, ua_b=-20, fa_b=30, th_f=20, th_b=-20, head=10, face="norm"),
                      P(lean=-6, ua_f=-120, fa_f=-140, hold=cholder("ladle_up"), ua_b=-20, fa_b=40, face="yell")]
        A["shout"] = [P(ua_f=-40, fa_f=-120, ua_b=-40, fa_b=-120, hold=ld, lean=-8, head=-12, face="yell"), P(ua_f=-44, fa_f=-124, ua_b=-44, fa_b=-124, hold=ld, lean=-10, head=-14, hy=-1, face="yell")]
        A["fling"] = [P(lean=-12, ua_f=-160, fa_f=-175, hold=cholder("meat"), ua_b=30, fa_b=60, th_f=18, th_b=-22, face="grin"),
                      P(lean=14, ua_f=96, fa_f=92, ua_b=-20, fa_b=20, th_f=30, sh_f=10, th_b=-26, face="yell")]
    for k in ("hurt", "fall", "down", "getup", "dizzy"):
        A[k] = base[k]
    A["held"] = [P(lean=-10, head=-10, ua_f=-20, fa_f=-40, ua_b=-30, fa_b=-60, face="hurt", lift=3)]
    A["sleep"] = [{**base["down"][0], "face": "sleep"}]
    return A
