"""v0.16 ROOFTOP HELIPAD characters. Everyday / work clothes with a SEPARATE top and bottom and a visible waist.
  vaper     - a patient who snuck up to the roof for a vape (hoodie + joggers); puffs a cloud that DIZZIES
  droneguy  - a storm-chaser visitor with a toy drone (rain shell + cargo pants), flies the drone at you
Boss: the rogue LIFE FLITE crew (a parody air-ambulance; no real brand). Flight suits are a SEPARATE flight jacket over
belted cargo pants, never a onesie.
  roxy  - FLIGHT NURSE ROXY, crew lead, ~1.35x a nurse; defib paddles ("CLEAR!")
  duke  - FLIGHT MEDIC DUKE, her partner, ~1.25x; swings the jump bag
  ace   - CAPTAIN ACE, the pilot (aviator shades); flies the chopper (drawn in v16_art), his sheet is for cutscenes"""
from __future__ import annotations

from rig import INK, P, vec
from chars import SKIN, hero_body, hero_anims, walk_cycle, hair_cap, _frame
from v14_chars import NURSE_BUILD, STREET

HOOD = ("#5a3ad8", "#3e28a0")
JOG = ("#3a3a48", "#2a2a34")
SHELL = ("#e8c82a", "#b89a18")
CARGO = ("#6a6a4a", "#4e4e36")
FJ_NAVY = ("#24306a", "#18204a")      # Roxy's flight jacket
FJ_SAGE = ("#5a6a4a", "#424e36")      # Duke's flight jacket
FJ_PANTS = ("#3a3a44", "#28282e")     # charcoal cargo pants
ACE_JKT = ("#6a4a2a", "#4a321c")      # a brown bomber jacket
BOSS_BUILD = dict(thigh=14, shin=13.5, torso=21, head=8.4, uarm=10.5, farm=10.5, arm_w=4.4, leg_w=6.0, torso_w=14.5, fist=2.4, foot=2, foot_len=4.4)
DUKE_BUILD = dict(thigh=13, shin=12.5, torso=20, head=8.0, uarm=10, farm=10, arm_w=4.4, leg_w=6.0, torso_w=14.5, fist=2.4, foot=2, foot_len=4.2)


def _at(T, lean):
    up, fwd = vec(180 - lean, 1), vec(90 - lean, 1)
    return _frame(up, fwd, T)[0]


def hoodie(S, T, hip, neck, lean, b):
    at = _at(T, lean); tw = b["torso_w"]
    S.poly([at(hip, 5, tw * 0.1), at(hip, 5, tw * 0.48), at(hip, 1.5, tw * 0.48), at(hip, 1.5, tw * 0.1)], b["shirt_s"], rim=False)  # kangaroo pocket
    for k in (0.2, 0.35):
        x, y = at(neck, -2, tw * k); S.line((x, y), (x, y + 5), "#f4f4f8")  # drawstrings


def rainshell(S, T, hip, neck, lean, b):
    at = _at(T, lean); tw = b["torso_w"]
    x0, y0 = at(neck, -1, tw * 0.3); x1, y1 = at(hip, 2, tw * 0.3); S.line((x0, y0), (x1, y1), "#8a7a10")  # zip
    x, y = at(neck, -6, tw * 0.05); S.rect(int(x), int(y), 3, 2, "#ff3a4a")  # a storm-chaser patch


def flightjacket(name_c):
    def pat(S, T, hip, neck, lean, b):
        at = _at(T, lean); tw = b["torso_w"]
        x0, y0 = at(neck, -1, tw * 0.32); x1, y1 = at(hip, 2.5, tw * 0.32); S.line((x0, y0), (x1, y1), "#c8ccd6")  # zip
        x, y = at(neck, -4, tw * 0.02); S.rect(int(x), int(y), 5, 2, "#f4f4f8"); S.set(int(x) + 1, int(y), name_c)  # name tape
        x, y = at(neck, -7, tw * 0.02); S.rect(int(x), int(y), 3, 3, "#ff3a4a"); S.set(int(x) + 1, int(y) + 1, "#ffffff")  # cross patch
        x, y = at(hip, 3.5, tw * 0.05)
        S.rect(int(x), int(y), int(tw * 0.55), 1, b["shirt_s"])  # the jacket's hem band, above the belt
    return pat


def bomber(S, T, hip, neck, lean, b):
    at = _at(T, lean); tw = b["torso_w"]
    x, y = at(neck, -0.5, tw * 0.1); S.rect(int(x) - 1, int(y), 6, 2, "#e8dcc0")  # shearling collar
    x0, y0 = at(neck, -2, tw * 0.3); x1, y1 = at(hip, 2.5, tw * 0.3); S.line((x0, y0), (x1, y1), "#c8a060")


def helmet_hair(seed, tail=False):
    def h(S, hc, r, b, pose):
        hair_cap(top=-0.4, back=0.5, grow=0.8, spikes=2, seed=seed, fringe=0)(S, hc, r, b, pose)
        if tail:
            S.ellipse((hc[0] - r * 1.2, hc[1] + r * 0.2), r * 0.35, r * 0.75, b["hair_c"], b["hair_s"])
    return h


def holder(kind):
    def h(S, T, hand, ang, b):
        hx, hy = T(hand); x, y = int(hx), int(hy)
        if kind in ("pads", "pads_zap"):  # defib paddles, one per hand look (drawn as a pair at the front hand)
            S.rect(x - 2, y - 3, 6, 5, INK); S.rect(x - 1, y - 2, 4, 3, "#ffd84a"); S.rect(x + 3, y - 2, 3, 3, "#c8ccd6")
            if kind == "pads_zap":
                for k in range(3):
                    S.line((x + 6, y - 1), (x + 12 + k * 2, y - 6 + k * 5), "#8ad8ff")
                S.ellipse((x + 8, y), 3, 3, "#ffffff", None, rim=False)
        elif kind == "bag":  # an orange jump bag on its strap
            S.line((x, y), (x, y + 4), "#3a2416"); S.rect(x - 5, y + 4, 11, 7, INK); S.rect(x - 4, y + 5, 9, 5, "#e8722a"); S.rect(x - 1, y + 6, 3, 3, "#ffffff")
        elif kind == "bag_out":
            S.line((x, y), (x + 7, y), "#3a2416"); S.rect(x + 7, y - 4, 11, 7, INK); S.rect(x + 8, y - 3, 9, 5, "#e8722a"); S.rect(x + 11, y - 2, 3, 3, "#ffffff")
        elif kind == "vape":
            S.rect(x - 1, y - 4, 2, 5, "#2a2a34"); S.set(x - 1, y - 5, "#a24dff")
        elif kind == "remote":  # drone controller with two sticks + an antenna
            S.rect(x - 4, y - 3, 9, 4, INK); S.rect(x - 3, y - 2, 7, 2, "#4a4a5a"); S.line((x + 3, y - 3), (x + 5, y - 8), "#c8ccd6"); S.set(x - 2, y - 2, "#3aa8ff")
        elif kind == "headset":
            S.rect(x - 2, y - 2, 4, 4, "#2a2a34")
    return h


def bodies():
    sk = SKIN
    B = {}
    B["vaper"] = hero_body(**NURSE_BUILD, skin=sk["tan"][0], skin_s=sk["tan"][1], hair_c="#2a1a10", hair_s="#140c06", hair=hair_cap(top=-0.5, back=0.5, grow=1.0, spikes=4, seed=81),
                           shirt=HOOD[0], shirt_s=HOOD[1], sleeve=HOOD[0], sleeve_s=HOOD[1], sleeve_len=1.7, sleeve_clip=True,
                           pants=JOG[0], pants_s=JOG[1], belt="#1a1a22", buckle="#8a8a9a", shoe="#f4f4f4", shoe_s="#a8b2c0", pattern=hoodie, **STREET)
    B["droneguy"] = hero_body(**NURSE_BUILD, skin=sk["light"][0], skin_s=sk["light"][1], hair_c="#c8a050", hair_s="#9a7a30", hair=hair_cap(top=-0.3, back=0.3, grow=0.6, seed=83, fringe=0),
                              glasses="#2a2a34", shirt=SHELL[0], shirt_s=SHELL[1], sleeve=SHELL[0], sleeve_s=SHELL[1], sleeve_len=1.7, sleeve_clip=True,
                              pants=CARGO[0], pants_s=CARGO[1], belt="#2a1a12", buckle="#c8ccd6", shoe="#5a3a24", shoe_s="#3a2416", pattern=rainshell, **STREET)
    B["roxy"] = hero_body(**BOSS_BUILD, skin=sk["brown"][0], skin_s=sk["brown"][1], hair_c="#1a0e08", hair_s="#0a0604", hair=helmet_hair(85, tail=True),
                          shirt=FJ_NAVY[0], shirt_s=FJ_NAVY[1], sleeve=FJ_NAVY[0], sleeve_s=FJ_NAVY[1], sleeve_len=1.7, sleeve_clip=True,
                          pants=FJ_PANTS[0], pants_s=FJ_PANTS[1], belt="#14141a", buckle="#ffd84a", shoe="#1a1a22", shoe_s="#0e0e14", pattern=flightjacket("#3a5ad8"), **STREET)
    B["duke"] = hero_body(**DUKE_BUILD, skin=sk["light"][0], skin_s=sk["light"][1], hair_c="#8a4a1e", hair_s="#5a2e10", hair=helmet_hair(87),
                          shirt=FJ_SAGE[0], shirt_s=FJ_SAGE[1], sleeve=FJ_SAGE[0], sleeve_s=FJ_SAGE[1], sleeve_len=1.7, sleeve_clip=True,
                          pants=FJ_PANTS[0], pants_s=FJ_PANTS[1], belt="#14141a", buckle="#c8ccd6", shoe="#1a1a22", shoe_s="#0e0e14", pattern=flightjacket("#ff3a4a"), **STREET)
    B["ace"] = hero_body(**DUKE_BUILD, skin=sk["tan"][0], skin_s=sk["tan"][1], hair_c="#3a2a1a", hair_s="#1e140c", hair=hair_cap(top=-0.2, back=0.3, grow=0.6, seed=89, fringe=0),
                         glasses="#1a1a22", shirt=ACE_JKT[0], shirt_s=ACE_JKT[1], sleeve=ACE_JKT[0], sleeve_s=ACE_JKT[1], sleeve_len=1.7, sleeve_clip=True,
                         pants=FJ_PANTS[0], pants_s=FJ_PANTS[1], belt="#14141a", buckle="#ffd84a", shoe="#3a2416", shoe_s="#1e140c", pattern=bomber, **STREET)
    return B


def _common(A, base):
    for k in ("hurt", "fall", "down", "getup", "dizzy"):
        A[k] = base[k]
    A["held"] = [P(lean=-10, head=-10, ua_f=-20, fa_f=-40, ua_b=-30, fa_b=-60, face="hurt", lift=3)]
    A["sleep"] = [{**base["down"][0], "face": "sleep"}]


def anims(kind):
    A = {}
    base = hero_anims("nick")
    if kind == "vaper":  # (tray AI) a straight cloud puff
        vp = holder("vape")
        A["idle"] = [P(ua_f=120, fa_f=170, hold=vp, ua_b=-6, fa_b=20, face="norm"), P(ua_f=118, fa_f=168, hold=vp, ua_b=-6, fa_b=20, hy=1, head=-6, face="grin")]
        A["walk"] = walk_cycle(swing=14, arm=6, lean=2)
        for f in A["walk"]:
            f.update(ua_f=40, fa_f=100, hold=vp)
        A["atk"] = [P(lean=-6, ua_f=130, fa_f=175, hold=vp, ua_b=-10, fa_b=20, head=-10, face="norm"),
                    P(lean=8, ua_f=60, fa_f=80, hold=vp, ua_b=-10, fa_b=20, head=8, face="yell")]
        A["lob"] = A["atk"]
    elif kind == "droneguy":  # (tray AI) flies the drone at you
        rc = holder("remote")
        A["idle"] = [P(ua_f=50, fa_f=120, hold=rc, ua_b=40, fa_b=120, head=-8, face="grin"), P(ua_f=52, fa_f=122, hold=rc, ua_b=42, fa_b=122, hy=1, head=-10, face="yell")]
        A["walk"] = walk_cycle(swing=16, arm=6)
        for f in A["walk"]:
            f.update(ua_f=50, fa_f=120, hold=rc)
        A["atk"] = [P(lean=-4, ua_f=60, fa_f=140, hold=rc, ua_b=50, fa_b=130, head=-12, face="yell"),
                    P(lean=6, ua_f=80, fa_f=100, hold=rc, ua_b=60, fa_b=110, th_f=14, th_b=-12, face="grin")]
        A["lob"] = A["atk"]
    elif kind in ("roxy", "duke"):
        hd = holder("pads" if kind == "roxy" else "bag")
        A["idle"] = [P(ua_f=30, fa_f=70, hold=hd, ua_b=-20, fa_b=-60, lean=-2, face="norm"), P(ua_f=32, fa_f=74, hold=hd, ua_b=-20, fa_b=-60, lean=-2, hy=1, face="grin")]
        A["walk"] = walk_cycle(swing=18, arm=8, lean=4)
        for f in A["walk"]:
            f.update(ua_f=30, fa_f=70, hold=hd)
        A["run"] = walk_cycle(swing=28, arm=14, lean=12)
        for f in A["run"]:
            f.update(ua_f=60, fa_f=80, hold=hd, face="yell")
        if kind == "roxy":
            A["charge"] = [P(lean=-6, ua_f=-120, fa_f=-150, ua_b=-120, fa_b=-150, hold=hd, face="yell"),
                           P(lean=-8, ua_f=-124, fa_f=-154, ua_b=-124, fa_b=-154, hold=holder("pads_zap"), hy=-1, face="yell")]
            A["zap"] = [P(lean=16, ua_f=88, fa_f=90, ua_b=80, fa_b=84, hold=holder("pads_zap"), th_f=28, sh_f=8, th_b=-24, face="yell")]
        A["atk"] = [P(lean=-10, ua_f=-150, fa_f=-160, hold=hd, ua_b=-20, fa_b=40, th_f=16, th_b=-20, face="grin"),
                    P(lean=18, ua_f=88, fa_f=90, hold=holder("bag_out") if kind == "duke" else holder("pads_zap"), ua_b=-30, fa_b=30, th_f=30, sh_f=10, th_b=-26, face="yell")]
        A["radio"] = [P(ua_f=150, fa_f=10, hold=holder("headset"), ua_b=-20, fa_b=-40, lean=-4, head=-8, face="yell"), P(ua_f=152, fa_f=12, hold=holder("headset"), ua_b=-20, fa_b=-40, lean=-4, head=-10, hy=-1, face="grin")]
    elif kind == "ace":
        A["idle"] = [P(ua_f=-30, fa_f=-120, ua_b=-30, fa_b=-120, lean=-4, face="grin"), P(ua_f=-32, fa_f=-122, ua_b=-32, fa_b=-122, lean=-4, hy=1, face="grin")]
        A["walk"] = walk_cycle(swing=14, arm=6, lean=-2)
    _common(A, base)
    return A
