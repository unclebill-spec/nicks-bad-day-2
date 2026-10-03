"""Hero and patient bodies + every animation as rig poses."""
from __future__ import annotations

import math

from rig import INK, P, hair_cap, vec, add

SKIN = {"light": ("#f2c8a2", "#d29a76"), "fair": ("#f6d2b6", "#dba88a"), "tan": ("#dca274", "#b27a52"),
        "brown": ("#b07448", "#875432"), "old": ("#efc6aa", "#c99a82")}
NAVY, NAVY_S = "#283a7a", "#1b2756"
# Traditional checked hospital gown: pale green base, darker check lines. The runtime swaps these for the faded-olive set.
GOWN = ("#bcd6a6", "#92ae7e")              # base, shade (the rig fills with these)
GOWN_CHECK = ("#9cba88", "#78946a", "#86a274", "#647e58")   # line on base, line on shade, crossing on base, crossing on shade
GOWN_OLIVE = ("#c6c89c", "#9ea074", "#a8aa80", "#82845e", "#949670", "#70724e")
SOCK = ("#f6d63a", "#c09e1a")              # yellow grip socks
SOCK_ELITE = ("#e84848", "#a82828")        # elites: red (runtime also makes blue)
GRIP = "#ffffff"
HAIRS = [("#2a1a12", "#140c08"), ("#6b4a2a", "#4a3018"), ("#f0d070", "#c0a040"), ("#d0582a", "#983a1a"), ("#9a9aa6", "#6a6a78"),
         ("#eef0f4", "#b8bcc8"), ("#8a3a2a", "#5a2418"), ("#3a2a4a", "#22162e"), ("#c8a882", "#9a7a58")]


def gown_check(img, base=GOWN, check=GOWN_CHECK, period=3):
    """Post-process a rendered frame (PIL RGBA): every gown pixel gets a gingham check on a fixed grid."""
    hx = lambda c: tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
    b0, b1 = hx(base[0]), hx(base[1])
    l0, l1, c0, c1 = (hx(c) for c in check)
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            q = px[x, y]
            if q[3] == 0:
                continue
            rgb = q[:3]
            if rgb not in (b0, b1):
                continue
            on_x, on_y = x % period == 0, y % period == 0
            if not (on_x or on_y):
                continue
            sh = rgb == b1
            col = (c1 if sh else c0) if (on_x and on_y) else (l1 if sh else l0)
            px[x, y] = col + (255,)
    return img


def gown_dots(S, T, hip, neck, lean, b):
    for k in range(5):
        p = add(hip, vec(180 - lean, b["torso"] * (0.1 + k * 0.2)))
        for dx in (-2.5, 1.5):
            x, y = T((p[0] + dx + (k % 2), p[1]))
            x, y = int(x), int(y)
            if 0 <= y < S.h and 0 <= x < S.w and S.p[y][x] in (b["shirt"], b["shirt_s"]):
                S.set(x, y, b["dots"])
    # gown below hip too
    for k in range(3):
        x, y = T((hip[0] - 2 + k * 2.5, hip[1] + 3 + (k % 2) * 3))
        x, y = int(x), int(y)
        if 0 <= y < S.h and 0 <= x < S.w and S.p[y][x] in (b["shirt"], b["shirt_s"]):
            S.set(x, y, b["dots"])


def stripes(S, T, hip, neck, lean, b):
    for k in range(int(b["torso"])):
        p = add(hip, vec(180 - lean, k))
        x, y = T((p[0] + b["torso_w"] / 2 - 1.5, p[1]))
        if S.p[int(y)][int(x)] in (b["shirt"], b["shirt_s"]):
            S.set(int(x), int(y), "#f0f0f4")


WILL_BLUE = ("#2f86f6", "#1c5ec4")
FLANNEL = ("#4a7a6a", "#33584c")                                   # visitor's flannel shirt: muted green/teal
FLANNEL_CHECK = ("#2e4a6a", "#22384e", "#c8d4c0", "#8a9a88")       # dark blue lines, light crossings   # Will: plain bright blue shirt (Bill, 2026-10-03)


def bald_shine(S, hc, r, b, pose):
    """Clean bald head (skin tone only) with a small shine highlight on the crown."""
    x, y = int(hc[0] + r * 0.05), int(hc[1] - r * 0.72)
    S.set(x, y, "#fff4e6"); S.set(x + 1, y, "#fff4e6"); S.set(x - 1, y + 1, "#ffe2c8")


def ponytail(S, hc, r, b, pose):
    sw = pose.get("tail", 0)
    a = (hc[0] - r * 0.9, hc[1] - r * 0.35)
    tip = (a[0] - 4 - sw, a[1] + 6 - abs(sw) * 0.5)
    S.capsule(a, tip, 3.4, b["hair_c"], b["hair_s"])
    S.set(int(a[0] + 0.5), int(a[1]), "#3aa0e8")


def nightcap(S, hc, r, b, pose):
    c, s = "#4a6ad8", "#2e48a8"
    S.poly([(hc[0] - r - 1, hc[1] - r * 0.15), (hc[0] + r * 0.9, hc[1] - r * 0.25), (hc[0] - r * 1.6, hc[1] - r * 2.1)], c)
    S.ellipse((hc[0] - r * 1.9, hc[1] - r * 1.8), 1.6, 1.6, "#f4f4f4")
    S.capsule((hc[0] - r - 0.5, hc[1] - r * 0.15), (hc[0] + r * 0.9, hc[1] - r * 0.25), 2.2, "#f4f4f4", rim=True)


def cap_back(S, hc, r, b, pose):
    c, s = "#d83a3a", "#a02626"
    for y in range(int(hc[1] - r - 2), int(hc[1] - r * 0.15)):
        for x in range(int(hc[0] - r - 2), int(hc[0] + r + 2)):
            if (x + 0.5 - hc[0]) ** 2 + (y + 0.5 - hc[1]) ** 2 <= (r + 0.8) ** 2:
                S.set(x, y, c if y < hc[1] - r * 0.5 else s)
    S.capsule((hc[0] - r - 0.5, hc[1] - r * 0.25), (hc[0] - r - 4, hc[1] - r * 0.05), 2.2, c, s)


def bald_ring(S, hc, r, b, pose):
    c = b["hair_c"]
    for y in range(int(hc[1] - r * 0.5), int(hc[1] + r * 0.5)):
        for x in range(int(hc[0] - r - 1), int(hc[0] - r * 0.1)):
            if (x + 0.5 - hc[0]) ** 2 + (y + 0.5 - hc[1]) ** 2 <= (r + 0.9) ** 2:
                S.set(x, y, c)
    S.set(int(hc[0] + r * 0.2), int(hc[1] - r - 0.8), c); S.set(int(hc[0] + r * 0.5), int(hc[1] - r - 1.5), c)


def beehive(S, hc, r, b, pose):
    """Tall beehive with pink curlers (elite patients)."""
    c, sh = b["hair_c"], b["hair_s"]
    S.ellipse((hc[0] - 1.5, hc[1] - r * 1.25), r * 0.95, r * 1.05, c, sh)
    S.ellipse((hc[0] - 0.5, hc[1] - r * 2.05), r * 0.6, r * 0.55, c, sh)
    for dx, dy in ((-r * 0.7, -r * 1.2), (r * 0.3, -r * 1.6), (-r * 0.2, -r * 2.2)):
        x, y = int(hc[0] + dx), int(hc[1] + dy)
        S.set(x, y, "#ff8ac0"); S.set(x + 1, y, "#ff8ac0"); S.set(x, y + 1, "#c8508a"); S.set(x + 1, y + 1, "#c8508a")


def holder(kind):
    def h(S, T, hand, ang, b):
        hx, hy = T(hand)
        if kind == "remote":
            S.capsule((hx - 1, hy + 1), (hx + 2.5, hy - 2.5), 2.6, "#4a4e5a", "#30343e")
            S.set(int(hx + 2), int(hy - 2), "#e83a3a")
        elif kind == "ivpole":  # pole held upright, bag at the top, wheels at the bottom
            S.line((hx, hy - 24), (hx, hy + 22), "#c8ccd6")
            S.line((hx + 1, hy - 24), (hx + 1, hy + 22), "#8a90a0")
            S.ellipse((hx + 0.5, hy - 25), 3, 4, "#cfe8ff", "#9ac4f0")
            S.capsule((hx - 4, hy + 23), (hx + 5, hy + 23), 2, "#5a5e6a")
        elif kind == "ivpole_h":  # held horizontal (sweep)
            S.line((hx - 18, hy), (hx + 26, hy), "#c8ccd6")
            S.line((hx - 18, hy + 1), (hx + 26, hy + 1), "#8a90a0")
            S.ellipse((hx + 27, hy - 1), 4, 3, "#cfe8ff", "#9ac4f0")
            S.capsule((hx - 19, hy - 3), (hx - 19, hy + 4), 2, "#5a5e6a")
        elif kind == "ivpole_up":  # raised back over the shoulder
            S.line((hx + 8, hy + 14), (hx - 16, hy - 20), "#c8ccd6")
            S.line((hx + 9, hy + 14), (hx - 15, hy - 20), "#8a90a0")
            S.ellipse((hx - 17, hy - 22), 3, 4, "#cfe8ff", "#9ac4f0")
        elif kind == "crutch":  # underarm crutch planted on the floor beside the patient
            S.line((hx + 1, hy - 14), (hx + 1, hy + 24), "#b8bcc8"); S.line((hx + 2, hy - 14), (hx + 2, hy + 24), "#7a8090")
            S.capsule((hx - 2, hy - 15), (hx + 5, hy - 15), 2.2, "#3a3e4a"); S.rect(int(hx), int(hy), 4, 2, "#3a3e4a")
            S.capsule((hx + 1, hy + 24), (hx + 2, hy + 25), 2.2, "#2a2a30")
        elif kind == "crutch_h":  # thrust forward like a lance
            S.line((hx - 12, hy), (hx + 30, hy), "#b8bcc8"); S.line((hx - 12, hy + 1), (hx + 30, hy + 1), "#7a8090")
            S.capsule((hx - 13, hy - 3), (hx - 13, hy + 4), 2.2, "#3a3e4a"); S.capsule((hx + 30, hy), (hx + 32, hy), 2.6, "#2a2a30")
        elif kind == "crutch_up":
            S.line((hx + 10, hy + 12), (hx - 14, hy - 22), "#b8bcc8"); S.line((hx + 11, hy + 12), (hx - 13, hy - 22), "#7a8090")
            S.capsule((hx + 8, hy + 14), (hx + 13, hy + 10), 2.2, "#3a3e4a"); S.capsule((hx - 14, hy - 22), (hx - 15, hy - 23), 2.6, "#2a2a30")
        elif kind in ("bell", "bell_up", "bell_out"):  # silver call bell on a coiled cord
            if kind == "bell":
                bx, by = hx + 2, hy + 12
                for k in range(6):
                    S.set(int(hx + (k % 2)), int(hy + 2 + k * 1.6), "#e8e8f0")
            elif kind == "bell_up":
                bx, by = hx - 12, hy - 14
                S.line((hx, hy), (bx, by), "#e8e8f0")
            else:
                bx, by = hx + 34, hy - 2
                for k in range(0, 34, 2):
                    S.set(int(hx + k), int(hy + math.sin(k * 0.7) * 1.5 - k * 0.06), "#e8e8f0")
            S.ellipse((bx, by), 4.2, 3.4, "#e0e4ec", "#9aa0ae")
            S.rect(int(bx - 4), int(by + 2), 9, 2, "#6a6e7a"); S.set(int(bx), int(by - 4), "#3a3e4a"); S.set(int(bx - 1), int(by - 1), "#ffffff")
        elif kind == "cane":
            S.line((hx + 1, hy), (hx + 1, hy + 26), "#8a5a2a"); S.line((hx + 2, hy), (hx + 2, hy + 26), "#5a3a18")
            S.capsule((hx - 3, hy - 1), (hx + 1, hy - 2), 2.4, "#8a5a2a", "#5a3a18")
        elif kind == "cane_h":
            S.line((hx - 4, hy), (hx + 26, hy - 4), "#8a5a2a"); S.line((hx - 4, hy + 1), (hx + 26, hy - 3), "#5a3a18")
            S.capsule((hx + 26, hy - 4), (hx + 29, hy), 2.4, "#8a5a2a", "#5a3a18")
        elif kind == "cane_up":
            S.line((hx + 4, hy + 6), (hx - 12, hy - 20), "#8a5a2a"); S.line((hx + 5, hy + 6), (hx - 11, hy - 20), "#5a3a18")
            S.capsule((hx - 12, hy - 20), (hx - 15, hy - 18), 2.4, "#8a5a2a", "#5a3a18")
        elif kind == "syringe":
            S.capsule((hx - 3, hy), (hx + 5, hy), 2.4, "#e8f4ff", "#9ac4e8"); S.line((hx + 6, hy), (hx + 9, hy), "#c8ccd6")
        elif kind == "urinal":
            S.capsule((hx - 3, hy - 2), (hx + 4, hy + 2), 4.2, "#e8eef4", "#a8b2c0"); S.rect(int(hx - 2), int(hy - 1), 4, 2, "#f2e070")
        elif kind == "paddles":
            S.capsule((hx - 1, hy), (hx + 3, hy), 4, "#e0e4ec", "#9aa0ae")
            S.set(int(hx + 1), int(hy - 2), "#f2d24a")
        # ---- v0.4 patients
        elif kind == "alarm":  # bed-alarm pad clipped on, cord dangling, red light
            S.capsule((hx - 2, hy + 1), (hx + 2, hy + 1), 4.2, "#d8dce4", "#9aa0ae"); S.rect(int(hx), int(hy - 1), 2, 2, "#ff3a3a")
            for k in range(7):
                S.set(int(hx - 1 - (k % 2)), int(hy + 4 + k * 1.7), "#e8e8f0")
        elif kind in ("tray", "tray_up", "tray_out"):  # meal tray: plate, jello cup, milk carton
            if kind == "tray":
                x0, y0 = hx - 3, hy - 1
            elif kind == "tray_up":
                x0, y0 = hx - 10, hy - 4
            else:
                x0, y0 = hx + 1, hy - 2
            S.rect(int(x0) - 1, int(y0) - 1, 18, 4, INK); S.rect(int(x0), int(y0), 16, 2, "#c8a070"); S.rect(int(x0), int(y0) + 1, 16, 1, "#9a7448")
            S.ellipse((x0 + 4, y0 - 1), 3, 1.2, "#f4f4f8", rim=False); S.rect(int(x0 + 3), int(y0 - 2), 3, 1, "#c86a3a")
            S.rect(int(x0 + 8), int(y0 - 3), 3, 3, "#5ad85a"); S.set(int(x0 + 8), int(y0 - 3), "#aaffaa")
            S.rect(int(x0 + 12), int(y0 - 5), 3, 5, "#f4f4f8"); S.rect(int(x0 + 12), int(y0 - 3), 3, 1, "#4a8ad8")
        elif kind == "cup":  # v0.5 barium contrast cup with a bendy straw
            S.rect(int(hx - 2), int(hy - 4), 6, 7, INK); S.rect(int(hx - 1), int(hy - 3), 4, 5, "#f4f6fa"); S.rect(int(hx - 1), int(hy - 1), 4, 1, "#3a6ad8")
            S.line((hx + 1, hy - 4), (hx + 3, hy - 7), "#ff6ab0")
        elif kind == "film":  # v0.5 X-ray film sheet (Lou's frisbee)
            S.rect(int(hx - 6), int(hy - 8), 12, 10, INK); S.rect(int(hx - 5), int(hy - 7), 10, 8, "#2a5aa0"); S.rect(int(hx), int(hy - 6), 1, 6, "#d8f4ff")
        elif kind == "jello":
            S.rect(int(hx - 2), int(hy - 3), 6, 6, INK); S.rect(int(hx - 1), int(hy - 2), 4, 4, "#5ad85a"); S.set(int(hx - 1), int(hy - 2), "#bfffbf")
        elif kind == "o2drag":  # oxygen tank on a little two-wheel dolly, dragged behind by its handle
            S.line((hx, hy), (hx - 6, hy + 10), "#7c8696")
            S.capsule((hx - 9, hy + 9), (hx - 9, hy + 24), 6, "#3aa860", "#267a44"); S.rect(int(hx - 10), int(hy + 6), 3, 3, "#b8c0cc")
            S.rect(int(hx - 12), int(hy + 15), 7, 1, "#ffffff")
            S.line((hx - 13, hy + 26), (hx - 4, hy + 26), "#7c8696"); S.ellipse((hx - 7, hy + 28), 2.2, 2.2, "#2a2e3a")
        elif kind == "o2_up":  # tank hoisted over the shoulder
            S.capsule((hx - 14, hy - 12), (hx + 2, hy + 2), 6, "#3aa860", "#267a44"); S.rect(int(hx - 17), int(hy - 15), 3, 3, "#b8c0cc")
        elif kind == "o2_h":  # swung out in front
            S.capsule((hx - 2, hy), (hx + 18, hy - 2), 6, "#3aa860", "#267a44"); S.rect(int(hx + 19), int(hy - 4), 3, 3, "#b8c0cc")
        elif kind == "clipboard":
            S.poly([(hx - 2, hy - 6), (hx + 4, hy - 6), (hx + 4, hy + 2), (hx - 2, hy + 2)], "#b07a3e")
            S.rect(int(hx - 1), int(hy - 5), 4, 6, "#f4f0e4")
            S.rect(int(hx), int(hy - 7), 2, 1, "#c8ccd6")
    return h


# ---------------- bodies
def hero_body(**kw):
    base = dict(thigh=11, shin=11, torso=17, head=6.6, uarm=8, farm=8, arm_w=3.6, leg_w=5.0, torso_w=12.5, fist=2.0, foot=2, foot_len=3.4,
                sleeve_len=0.6, shirt=NAVY, shirt_s=NAVY_S, sleeve=NAVY, sleeve_s=NAVY_S, pants=NAVY, pants_s=NAVY_S,
                shoe="#e8eef4", shoe_s="#a8b2c0", vneck=True, steth=True, badge="#f4f4f4", eye_white=True)
    base.update(kw)
    return base


def bodies():
    sk = SKIN
    B = {}
    B["nick"] = hero_body(skin=sk["fair"][0], skin_s=sk["fair"][1], hair_c="#f6dc72", hair_s="#c9a640", glasses="#2a2a36",
                          hair=hair_cap(top=-0.2, back=0.25, spikes=3), shoe="#ff8a1e", shoe_s="#c45a10")
    B["kim"] = hero_body(thigh=9, shin=9, torso=15, head=6.6, uarm=7, farm=7, torso_w=11, arm_w=3.3, leg_w=4.6, skin=sk["fair"][0], skin_s=sk["fair"][1],
                         hair_c="#d8462a", hair_s="#9c2c1a", hair=hair_cap(top=-0.1, back=0.4), hair_back=ponytail,
                         freckles="#d08a6a", shoe="#ffffff", shoe_s="#b8c2d0", mouth="#c0505e")
    # Will (v0.2.2): regular guy proportions, a fitted bright blue t-shirt with short sleeves (skin-tone forearms), belt, navy pants
    B["will"] = hero_body(thigh=9, shin=8.5, torso=16, head=7, uarm=7, farm=7, arm_w=3.8, leg_w=5.2, torso_w=13, belly=1, fist=2.1,
                          skin=sk["light"][0], skin_s=sk["light"][1], hair=bald_shine, shirt=WILL_BLUE[0], shirt_s=WILL_BLUE[1], sleeve=WILL_BLUE[0], sleeve_s=WILL_BLUE[1],
                          vneck=False, crew="#1c5ec4", steth=True, belt="#4a3220", pants="#2a3658", pants_s="#1c2440",
                          shoe="#3a2a22", shoe_s="#22160e", badge="#f4f4f4", sleeve_len=0.42)
    B["jackie"] = hero_body(thigh=12, shin=11.5, torso=17.5, head=6.4, uarm=8.5, farm=8.5, torso_w=11, arm_w=3.3, leg_w=4.7, skin=sk["tan"][0], skin_s=sk["tan"][1],
                            hair_c="#4a2a18", hair_s="#2e180c", hair=hair_cap(top=0.05, back=0.2, grow=2.2, bumps=1.3, fringe=0, seed=2),
                            shoe="#9a5ae0", shoe_s="#6a34a8", mouth="#b04a5a")
    gown = dict(shirt=GOWN[0], shirt_s=GOWN[1], sleeve=GOWN[0], sleeve_s=GOWN[1], check=True,
                vneck=False, steth=False, badge=None, eye_white=True, gown_len=9, sleeve_len=0.45)
    socks = dict(shoe=SOCK[0], shoe_s=SOCK[1], sock=SOCK[0], foot_len=3.6)
    sock = dict(pants=sk["old"][0], pants_s=sk["old"][1], **socks)
    B["wanderer"] = hero_body(thigh=10, shin=10, torso=16, skin=sk["old"][0], skin_s=sk["old"][1], hair_c="#eef0f4", hair_s="#b8bcc8",
                              hair=hair_cap(top=0.0, back=0.4, grow=1.6, bumps=1.6, seed=3, fringe=0), **gown, **sock)
    B["spammer"] = hero_body(thigh=10, shin=10, torso=15, torso_w=10, belly=1.5, skin=sk["light"][0], skin_s=sk["light"][1], hair_c="#9a9aa6",
                             hair_s="#6a6a78", hair=bald_ring, glasses="#5a4a3a",
                             **gown, pants=sk["light"][0], pants_s=sk["light"][1], **socks)
    B["escape"] = hero_body(thigh=10.5, shin=10.5, torso=15, torso_w=8, skin=sk["brown"][0], skin_s=sk["brown"][1], hair_c="#2a1a12",
                            hair_s="#140c08", hair=hair_cap(top=-0.25, back=0.3, spikes=4),
                            **{**gown, "gown_len": 6}, pants=sk["brown"][0], pants_s=sk["brown"][1], **socks)
    B["ivswing"] = hero_body(thigh=10.5, shin=10.5, torso=17, torso_w=10, skin=sk["tan"][0], skin_s=sk["tan"][1], hair_c="#5a5a64",
                             hair_s="#3a3a44", hair=hair_cap(top=-0.3, back=0.3, grow=0.5), beard="#7a7a84", **gown,
                             pants=sk["tan"][0], pants_s=sk["tan"][1], **socks)
    B["sundowner"] = hero_body(thigh=10, shin=10, torso=15, skin=sk["old"][0], skin_s=sk["old"][1], hair_c="#eef0f4", hair_s="#b8bcc8",
                               hair=nightcap, **{**gown, "gown_len": 11}, **sock)
    # weapon-carrying patients: crutch and call bell on a cord
    B["crutch"] = hero_body(thigh=10.5, shin=10.5, torso=16, torso_w=11, skin=sk["light"][0], skin_s=sk["light"][1], hair_c="#6b4a2a", hair_s="#4a3018",
                            hair=hair_cap(top=-0.2, back=0.35, grow=1.0, seed=5), **gown, pants=sk["light"][0], pants_s=sk["light"][1], **socks,
                            cast="#f4f4f4")
    B["bell"] = hero_body(thigh=10, shin=10, torso=15, torso_w=10.5, belly=1, skin=sk["tan"][0], skin_s=sk["tan"][1], hair_c="#2a1a12", hair_s="#140c08",
                          hair=hair_cap(top=-0.05, back=0.45, grow=1.4, bumps=1.0, seed=7, fringe=0), **gown, pants=sk["tan"][0], pants_s=sk["tan"][1], **socks)
    # elite "Frequent Flyer": beehive with curlers, red (or blue) grip socks, a cane, and a stash of things to throw
    B["elite"] = hero_body(thigh=11, shin=11, torso=17, torso_w=12, head=6.8, skin=sk["fair"][0], skin_s=sk["fair"][1], hair_c="#d0582a", hair_s="#983a1a",
                           hair=hair_cap(top=-0.1, back=0.4, grow=1.0, seed=9), hair_back=beehive, glasses="#8a2a6a",
                           **{**gown, "gown_len": 10}, pants=sk["fair"][0], pants_s=sk["fair"][1], shoe=SOCK_ELITE[0], shoe_s=SOCK_ELITE[1], sock=SOCK_ELITE[0], foot_len=3.6)
    # Belligerent Visitor (v0.2.2): a regular big guy in street clothes: blue/green flannel with rolled sleeves (skin forearms),
    # open collar, belt, blue jeans, white sneakers, short brown hair + beard. No cap, no tracksuit.
    B["visitor"] = hero_body(thigh=12, shin=12, torso=20, head=7.6, uarm=9.5, farm=9, arm_w=4.6, leg_w=5.8, torso_w=16, belly=1.5,
                             skin=sk["light"][0], skin_s=sk["light"][1], hair_c="#5a3a20", hair_s="#3a2410", hair=hair_cap(top=-0.4, back=0.25, grow=0.4, spikes=2, seed=4),
                             shirt=FLANNEL[0], shirt_s=FLANNEL[1], sleeve=FLANNEL[0], sleeve_s=FLANNEL[1], sleeve_len=0.62, plaid=(FLANNEL, FLANNEL_CHECK),
                             pants="#4a6a9a", pants_s="#344e78", belt="#3a2a1a", vneck=True, steth=False, badge="#f2d24a", shoe="#f4f4f4", shoe_s="#b0b8c4",
                             beard="#5a3a20", fist=2.2, foot_len=4.4, foot_w=3.0)
    # v0.4 patients (gown + grip socks, random hair at runtime)
    B["runner"] = hero_body(thigh=10.5, shin=10.5, torso=15, torso_w=9, skin=sk["fair"][0], skin_s=sk["fair"][1], hair_c="#f0d070", hair_s="#c0a040",
                            hair=hair_cap(top=-0.3, back=0.3, spikes=5, seed=6), **{**gown, "gown_len": 7}, pants=sk["fair"][0], pants_s=sk["fair"][1], **socks)
    B["tray"] = hero_body(thigh=10, shin=10, torso=16, torso_w=12, belly=2, skin=sk["light"][0], skin_s=sk["light"][1], hair_c="#9a9aa6", hair_s="#6a6a78",
                          hair=hair_cap(top=0.05, back=0.4, grow=1.8, bumps=1.4, seed=8, fringe=0), glasses="#3a3a44", mouth="#9a3a3a",
                          **gown, pants=sk["light"][0], pants_s=sk["light"][1], **socks)
    B["o2"] = hero_body(thigh=10, shin=10, torso=15, torso_w=10.5, skin=sk["old"][0], skin_s=sk["old"][1], hair_c="#eef0f4", hair_s="#b8bcc8",
                        hair=bald_ring, **{**gown, "gown_len": 10}, **sock)
    # v0.5 Radiology patients: the Contrast Chugger (barium cup + bendy straw) and the Lead-Apron Hugger (heavy apron)
    B["barium"] = hero_body(thigh=10, shin=10, torso=15, torso_w=11, belly=1.5, skin=sk["tan"][0], skin_s=sk["tan"][1], hair_c="#2a1a12", hair_s="#140c08",
                            hair=hair_cap(top=-0.1, back=0.35, grow=1.2, spikes=2, seed=12), mouth="#f4f6fa", **gown, pants=sk["tan"][0], pants_s=sk["tan"][1], **socks)
    B["apron"] = hero_body(thigh=10.5, shin=10, torso=17, torso_w=13, belly=1.5, skin=sk["light"][0], skin_s=sk["light"][1], hair_c="#6b4a2a", hair_s="#4a3018",
                           hair=hair_cap(top=-0.25, back=0.3, grow=0.7, seed=13), beard="#6b4a2a",
                           **{**gown, "shirt": "#3a6ad8", "shirt_s": "#2a4aa8", "gown_len": 12}, pants=sk["light"][0], pants_s=sk["light"][1], **socks)
    # v0.5 mini-boss LEAD-APRON LOU: a gentle giant ex-linebacker wearing three lead aprons like shoulder pads, ~2.2x a nurse's height
    B["lou"] = hero_body(thigh=24, shin=23, torso=46, head=15.4, uarm=19, farm=18, arm_w=12.6, leg_w=16, torso_w=50, fist=6.2, foot=4.8, foot_len=9, belly=8.4,
                         skin=sk["brown"][0], skin_s=sk["brown"][1], hair_c="#2a1a12", hair_s="#140c08", hair=hair_cap(top=-0.35, back=0.2, grow=0.5, seed=14),
                         **{**gown, "shirt": "#2a6a9a", "shirt_s": "#1c4c74", "gown_len": 10}, pants=sk["brown"][0], pants_s=sk["brown"][1],
                         shoe=SOCK[0], shoe_s=SOCK[1], sock=SOCK[0])
    return B


# ---------------- animations
def walk_cycle(n=4, swing=24, arm=22, lean=6, base=None, bob=1):
    base = base or {}
    out = []
    for i in range(n):
        ph = i / n * 2 * math.pi
        s = math.sin(ph)
        c = math.cos(ph)
        out.append(P(**{**dict(lean=lean, th_f=swing * s, sh_f=swing * s - max(0, -c) * 28 * (1 if s < 0 else 0.4),
                               th_b=-swing * s, sh_b=-swing * s - max(0, c) * 28 * (1 if s > 0 else 0.4),
                               ua_f=-arm * s + 10, fa_f=60 - arm * s, ua_b=arm * s - 6, fa_b=50 + arm * s, hy=bob * abs(c)), **base}))
    return out


def hero_anims(name):
    A = {}
    guard = dict(ua_f=22, fa_f=128, ua_b=-6, fa_b=118)
    A["idle"] = [P(**guard), P(**{**guard, "fa_f": 122}, hy=1)]
    A["walk"] = walk_cycle(swing=22, arm=18)
    for f in A["walk"]:
        f.update(ua_f=f["ua_f"] + 10, fa_f=110 + f["fa_f"] * 0.2)
    A["run"] = walk_cycle(swing=38, arm=40, lean=16, bob=2)
    for f in A["run"]:
        f.update(fa_f=f["ua_f"] + 80, fa_b=f["ua_b"] + 80)
    A["atk1"] = [P(lean=6, ua_f=40, fa_f=110, ua_b=-10, fa_b=120), P(lean=12, ua_f=86, fa_f=90, ua_b=-14, fa_b=125, th_f=20, th_b=-18)]
    A["atk2"] = [P(lean=4, ua_f=10, fa_f=130, ua_b=-30, fa_b=100), P(lean=16, ua_f=10, fa_f=135, ua_b=84, fa_b=90, th_f=22, th_b=-22, head=-4)]
    A["atk3"] = [P(lean=-4, ua_f=-20, fa_f=60, ua_b=-40, fa_b=40, th_f=40, sh_f=-30, th_b=-6, sh_b=-6),
                 P(lean=-14, ua_f=-60, fa_f=-20, ua_b=-90, fa_b=-60, th_f=96, sh_f=92, th_b=-10, sh_b=-8, face="yell"),
                 P(lean=-6, ua_f=-30, fa_f=40, ua_b=-50, fa_b=20, th_f=50, sh_f=10, th_b=-8, sh_b=-6)]
    A["atk4"] = [P(lean=20, ua_f=110, fa_f=150, ua_b=110, fa_b=160, th_f=20, th_b=-20, hy=2, face="yell"),   # overhead double-hand smash
                 P(lean=26, ua_f=80, fa_f=40, ua_b=78, fa_b=38, th_f=30, sh_f=10, th_b=-26, hy=4, face="yell")]
    A["jump"] = [P(plant=False, lean=6, th_f=70, sh_f=-20, th_b=30, sh_b=-50, ua_f=140, fa_f=160, ua_b=120, fa_b=150),
                 P(plant=False, lean=4, th_f=30, sh_f=0, th_b=-10, sh_b=-20, ua_f=60, fa_f=120, ua_b=40, fa_b=100)]
    A["jkick"] = [P(plant=False, lean=-16, th_f=88, sh_f=88, th_b=40, sh_b=-60, ua_f=-40, fa_f=10, ua_b=-90, fa_b=-50, face="yell")]
    A["dash"] = [P(lean=34, th_f=80, sh_f=-10, th_b=-40, sh_b=-60, ua_f=70, fa_f=150, ua_b=-70, fa_b=-30, face="yell")]
    A["grab"] = [P(lean=10, ua_f=74, fa_f=84, ua_b=70, fa_b=80)]
    A["knee"] = [P(lean=10, ua_f=74, fa_f=60, ua_b=70, fa_b=60, th_f=86, sh_f=-10, th_b=-6, sh_b=-6, face="yell")]
    A["throw"] = [P(lean=-12, ua_f=150, fa_f=170, ua_b=146, fa_b=168, th_f=24, th_b=-24, face="yell"),
                  P(lean=24, ua_f=100, fa_f=95, ua_b=96, fa_b=92, th_f=30, sh_f=10, th_b=-28, sh_b=-20)]
    A["back"] = [P(lean=-8, head=-6, ua_f=10, fa_f=120, ua_b=-86, fa_b=-110, th_f=10, th_b=-24, face="yell")]
    A["hurt"] = [P(lean=-18, head=-14, ua_f=-26, fa_f=-50, ua_b=-46, fa_b=-80, th_f=20, sh_f=10, th_b=-6, face="hurt"),
                 P(lean=24, head=14, ua_f=40, fa_f=10, ua_b=20, fa_b=0, th_f=10, th_b=-16, hy=2, face="hurt")]
    A["fall"] = [P(rot=-55, lean=-10, ua_f=-120, fa_f=-140, ua_b=-150, fa_b=-170, th_f=40, sh_f=10, th_b=10, sh_b=-10, face="hurt")]
    A["down"] = [P(rot=-90, lean=0, head=-10, ua_f=-160, fa_f=-160, ua_b=-140, fa_b=-150, th_f=10, sh_f=0, th_b=-4, sh_b=-6, face="hurt")]
    A["getup"] = [P(lean=40, hy=8, th_f=86, sh_f=0, th_b=-40, sh_b=-110, ua_f=40, fa_f=10, ua_b=20, fa_b=0)]
    A["win"] = [P(lean=-2, ua_f=170, fa_f=176, ua_b=-30, fa_b=40, face="grin"), P(lean=-2, ua_f=166, fa_f=170, ua_b=-30, fa_b=40, face="grin", hy=-1)]
    A["dizzy"] = [P(lean=-4, head=10, ua_f=-10, fa_f=10, ua_b=-20, fa_b=0, face="hurt"), P(lean=6, head=-10, ua_f=10, fa_f=20, ua_b=0, fa_b=10, face="hurt")]
    A["pickup"] = [P(lean=50, hy=7, th_f=70, sh_f=-10, th_b=-30, sh_b=-80, ua_f=60, fa_f=20, ua_b=30, fa_b=10)]
    A["swing"] = [P(lean=-4, ua_f=-150, fa_f=-170, ua_b=-20, fa_b=60, th_f=10, th_b=-20), P(lean=18, ua_f=95, fa_f=96, ua_b=-20, fa_b=90, th_f=28, th_b=-24, face="yell")]
    A["spray"] = [P(lean=8, ua_f=80, fa_f=90, ua_b=60, fa_b=96, th_f=20, th_b=-24)]
    # hero specials
    if name == "nick":
        pad = holder("paddles")
        A["special"] = [P(lean=4, ua_f=50, fa_f=120, ua_b=40, fa_b=130, hold=pad, hold_b=pad),
                        P(lean=-10, ua_f=150, fa_f=160, ua_b=-150, fa_b=-160, hold=pad, hold_b=pad, face="yell"),
                        P(lean=40, hy=6, ua_f=60, fa_f=20, ua_b=50, fa_b=10, th_f=60, sh_f=-10, th_b=-40, sh_b=-60, hold=pad, hold_b=pad, face="yell")]
    elif name == "kim":
        A["special"] = [P(lean=-6, th_f=94, sh_f=94, th_b=-6, ua_f=-80, fa_f=-80, ua_b=-100, fa_b=-110, face="yell"),
                        P(lean=0, th_f=10, sh_f=10, th_b=-94, sh_b=-94, ua_f=100, fa_f=110, ua_b=60, fa_b=90, face="yell", flip=True),
                        P(lean=-6, th_f=94, sh_f=94, th_b=-6, ua_f=-80, fa_f=-80, ua_b=-100, fa_b=-110, face="yell", flip=True),
                        P(lean=0, th_f=10, sh_f=10, th_b=-94, sh_b=-94, ua_f=100, fa_f=110, ua_b=60, fa_b=90, face="yell")]
    elif name == "will":
        A["special"] = [P(lean=20, hy=6, th_f=60, sh_f=-30, th_b=-40, sh_b=-80, ua_f=-40, fa_f=0, ua_b=-60, fa_b=-20),
                        P(plant=False, lean=-20, th_f=40, sh_f=-10, th_b=10, sh_b=-30, ua_f=160, fa_f=170, ua_b=150, fa_b=170, face="yell"),
                        P(lean=34, hy=8, th_f=70, sh_f=0, th_b=-60, sh_b=-90, ua_f=80, fa_f=10, ua_b=70, fa_b=0, face="yell")]
    else:  # jackie
        cb = holder("clipboard")
        A["special"] = [P(lean=-10, ua_f=-130, fa_f=-160, ua_b=40, fa_b=110, th_f=26, th_b=-26, hold=cb),
                        P(lean=18, ua_f=96, fa_f=90, ua_b=-30, fa_b=40, th_f=34, sh_f=10, th_b=-28, face="yell"),
                        P(lean=10, ua_f=60, fa_f=40, ua_b=-20, fa_b=40, th_f=26, th_b=-20)]
    # v0.4: riding a gurney (crouched surf, arms out) and the Charge Nurse team-up pose
    A["ride"] = [P(lean=22, hy=6, th_f=56, sh_f=-34, th_b=-34, sh_b=-76, ua_f=84, fa_f=96, ua_b=-70, fa_b=-30, face="yell"),
                 P(lean=18, hy=5, th_f=50, sh_f=-30, th_b=-30, sh_b=-72, ua_f=96, fa_f=110, ua_b=-80, fa_b=-40, face="grin")]
    A["team"] = [P(lean=-6, ua_f=176, fa_f=178, ua_b=150, fa_b=160, th_f=20, th_b=-20, face="yell")]
    # v0.6: carrying a prop overhead (golden-axe style) and walking with it
    up = dict(ua_f=146, fa_f=186, ua_b=140, fa_b=182)
    A["lift"] = [P(lean=-2, th_f=12, th_b=-12, **up), P(lean=-2, th_f=12, th_b=-12, hy=1, **{**up, "fa_f": 180})]
    A["carry"] = walk_cycle(swing=16, arm=0)
    for f in A["carry"]:
        f.update(lean=-1, **up)
    if name == "kim":  # Kim's quick 4th hit: spinning back kick
        A["atk4"] = [P(lean=0, th_f=10, sh_f=10, th_b=-96, sh_b=-96, ua_f=100, fa_f=110, ua_b=60, fa_b=90, face="yell", flip=True),
                     P(lean=-12, th_f=96, sh_f=94, th_b=-6, ua_f=-70, fa_f=-80, ua_b=-100, fa_b=-110, face="yell")]
    return A


def enemy_anims(kind):
    A = {}
    if kind == "wanderer":
        zomb = dict(ua_f=84, fa_f=88, ua_b=80, fa_b=86, lean=8, face="sleep")
        A["idle"] = [P(**zomb), P(**zomb, hy=1, head=6)]
        A["walk"] = walk_cycle(swing=12, arm=0, lean=8)
        for f in A["walk"]:
            f.update(zomb)
        A["atk"] = [P(lean=-4, ua_f=130, fa_f=140, ua_b=124, fa_b=136, face="norm"), P(lean=16, ua_f=80, fa_f=110, ua_b=78, fa_b=108, th_f=26, th_b=-20, face="grin")]
        A["hug"] = [P(lean=12, ua_f=78, fa_f=120, ua_b=76, fa_b=118, face="grin"), P(lean=14, ua_f=80, fa_f=124, ua_b=78, fa_b=122, face="grin", hy=1)]
    elif kind == "spammer":
        rm = holder("remote")
        A["idle"] = [P(ua_f=40, fa_f=130, hold=rm, ua_b=-6, fa_b=20), P(ua_f=40, fa_f=136, hold=rm, ua_b=-6, fa_b=20, hy=1)]
        A["walk"] = walk_cycle(swing=16, arm=10)
        for f in A["walk"]:
            f.update(ua_f=40, fa_f=130, hold=rm)
        A["atk"] = [P(lean=-12, ua_f=-150, fa_f=-170, hold=rm, ua_b=40, fa_b=80, th_f=20, th_b=-24),
                    P(lean=14, ua_f=110, fa_f=100, ua_b=-20, fa_b=20, th_f=30, sh_f=10, th_b=-26, face="yell")]
    elif kind == "escape":
        A["idle"] = [P(ua_f=30, fa_f=120, ua_b=-20, fa_b=90, face="grin", hy=0), P(ua_f=30, fa_f=120, ua_b=-20, fa_b=90, face="grin", hy=-1, lift=1)]
        A["walk"] = walk_cycle(swing=40, arm=44, lean=18, bob=2)
        for f in A["walk"]:
            f.update(fa_f=f["ua_f"] + 80, fa_b=f["ua_b"] + 80, face="grin")
        A["atk"] = [P(lean=-6, ua_f=170, fa_f=176, ua_b=-20, fa_b=30, face="grin"), P(lean=16, ua_f=86, fa_f=70, ua_b=-30, fa_b=20, th_f=20, th_b=-20, face="grin")]
    elif kind == "ivswing":
        A["idle"] = [P(ua_f=36, fa_f=100, ua_b=30, fa_b=90, hold=holder("ivpole")), P(ua_f=36, fa_f=104, ua_b=30, fa_b=92, hy=1, hold=holder("ivpole"))]
        A["walk"] = walk_cycle(swing=16, arm=4)
        for f in A["walk"]:
            f.update(ua_f=36, fa_f=100, ua_b=30, fa_b=90, hold=holder("ivpole"))
        A["atk"] = [P(lean=-10, ua_f=-140, fa_f=-150, ua_b=-150, fa_b=-160, hold=holder("ivpole_up")),
                    P(lean=14, ua_f=86, fa_f=92, ua_b=80, fa_b=90, th_f=26, th_b=-24, hold=holder("ivpole_h"), face="yell"),
                    P(lean=20, ua_f=70, fa_f=80, ua_b=60, fa_b=76, th_f=30, th_b=-26, hold=holder("ivpole_h"), face="yell")]
    elif kind == "sundowner":
        hunch = dict(lean=18, head=-10, ua_f=10, fa_f=40, ua_b=-10, fa_b=20)
        A["idle"] = [P(**hunch), P(**{**hunch, "head": -4}, hy=1)]
        A["walk"] = walk_cycle(swing=14, arm=8, lean=18)
        A["atk"] = walk_cycle(swing=40, arm=0, lean=44, bob=2)  # head-down charge
        for f in A["atk"]:
            f.update(ua_f=-60, fa_f=-40, ua_b=-70, fa_b=-50, head=-20, face="yell")
    elif kind == "crutch":
        cr = holder("crutch")
        A["idle"] = [P(ua_f=20, fa_f=60, ua_b=-6, fa_b=20, hold=cr, lean=4), P(ua_f=20, fa_f=60, ua_b=-6, fa_b=20, hold=cr, lean=4, hy=1)]
        A["walk"] = walk_cycle(n=4, swing=10, arm=4, lean=6)
        for i, f in enumerate(A["walk"]):  # hop-along gait
            f.update(ua_f=20, fa_f=60, hold=cr, th_b=-30, sh_b=-80, hy=1 if i % 2 else 0)
        A["atk"] = [P(lean=-10, ua_f=-140, fa_f=-150, ua_b=-20, fa_b=40, th_b=-30, sh_b=-80, hold=holder("crutch_up")),
                    P(lean=16, ua_f=86, fa_f=90, ua_b=-20, fa_b=40, th_f=26, th_b=-24, hold=holder("crutch_h"), face="yell")]
    elif kind == "bell":
        bl = holder("bell")
        A["idle"] = [P(ua_f=20, fa_f=70, ua_b=-6, fa_b=20, hold=bl), P(ua_f=20, fa_f=76, ua_b=-6, fa_b=20, hold=bl, hy=1)]
        A["walk"] = walk_cycle(swing=16, arm=8)
        for f in A["walk"]:
            f.update(ua_f=20, fa_f=70, hold=bl)
        A["atk"] = [P(lean=-12, ua_f=-150, fa_f=-160, ua_b=30, fa_b=60, th_f=20, th_b=-24, hold=holder("bell_up"), face="grin"),
                    P(lean=14, ua_f=90, fa_f=92, ua_b=-20, fa_b=30, th_f=30, sh_f=10, th_b=-26, hold=holder("bell_out"), face="yell")]
    elif kind == "elite":
        cn = holder("cane")
        A["idle"] = [P(ua_f=16, fa_f=40, ua_b=-6, fa_b=60, hold=cn, lean=6), P(ua_f=16, fa_f=40, ua_b=-6, fa_b=60, hold=cn, lean=6, hy=1)]
        A["walk"] = walk_cycle(swing=16, arm=6, lean=6)
        for f in A["walk"]:
            f.update(ua_f=16, fa_f=40, hold=cn)
        A["atk"] = [P(lean=-10, ua_f=-130, fa_f=-150, ua_b=-10, fa_b=60, th_f=16, th_b=-20, hold=holder("cane_up"), face="yell"),
                    P(lean=18, ua_f=84, fa_f=86, ua_b=-20, fa_b=40, th_f=30, sh_f=10, th_b=-26, hold=holder("cane_h"), face="yell")]
        A["toss"] = [P(lean=-12, ua_f=16, fa_f=40, hold=cn, ua_b=-150, fa_b=-170, hold_b=holder("syringe"), th_f=20, th_b=-24),
                     P(lean=14, ua_f=16, fa_f=40, hold=cn, ua_b=110, fa_b=100, th_f=30, sh_f=10, th_b=-26, face="grin")]
        A["lob"] = [P(lean=-14, ua_f=16, fa_f=40, hold=cn, ua_b=-160, fa_b=-175, hold_b=holder("urinal"), th_f=20, th_b=-24, face="grin"),
                    P(lean=8, ua_f=16, fa_f=40, hold=cn, ua_b=150, fa_b=140, th_f=24, th_b=-20, face="grin")]
    elif kind == "visitor":
        A["idle"] = [P(ua_f=30, fa_f=130, ua_b=-6, fa_b=120, lean=6), P(ua_f=30, fa_f=126, ua_b=-6, fa_b=116, lean=6, hy=1)]
        A["walk"] = walk_cycle(swing=18, arm=16, lean=8)
        A["atk"] = [P(lean=-10, ua_f=20, fa_f=130, ua_b=-120, fa_b=-150, th_f=16, th_b=-20, face="yell"),
                    P(lean=22, ua_f=10, fa_f=130, ua_b=92, fa_b=90, th_f=34, sh_f=10, th_b=-28, face="yell")]
    elif kind == "runner":  # bed-alarm runner: sprints away, alarm pad flapping
        al = holder("alarm")
        A["idle"] = [P(ua_f=30, fa_f=120, ua_b=-20, fa_b=40, hold_b=al, face="grin"), P(ua_f=30, fa_f=120, ua_b=-20, fa_b=40, hold_b=al, face="grin", hy=-1, lift=1)]
        A["walk"] = walk_cycle(swing=44, arm=46, lean=20, bob=2)
        for f in A["walk"]:
            f.update(fa_f=f["ua_f"] + 80, fa_b=f["ua_b"] + 60, hold_b=al, face="grin")
        A["atk"] = [P(lean=-6, ua_f=60, fa_f=90, ua_b=-20, fa_b=30, hold_b=al, face="grin"), P(lean=16, ua_f=86, fa_f=80, ua_b=-30, fa_b=20, th_f=20, th_b=-20, hold_b=al, face="yell")]
    elif kind == "tray":  # food-tray thrower: cranky, hurls trays and jello
        tr = holder("tray")
        A["idle"] = [P(ua_f=40, fa_f=100, ua_b=30, fa_b=96, hold=tr, face="yell"), P(ua_f=40, fa_f=104, ua_b=30, fa_b=98, hold=tr, face="norm", hy=1)]
        A["walk"] = walk_cycle(swing=16, arm=6)
        for f in A["walk"]:
            f.update(ua_f=40, fa_f=100, hold=tr)
        A["atk"] = [P(lean=-12, ua_f=-150, fa_f=-165, ua_b=40, fa_b=80, th_f=20, th_b=-24, hold=holder("tray_up"), face="yell"),
                    P(lean=14, ua_f=100, fa_f=96, ua_b=-20, fa_b=20, th_f=30, sh_f=10, th_b=-26, face="yell")]
        A["lob"] = [P(lean=-12, ua_f=40, fa_f=100, hold=tr, ua_b=-160, fa_b=-175, hold_b=holder("jello"), th_f=20, th_b=-24, face="grin"),
                    P(lean=8, ua_f=40, fa_f=100, hold=tr, ua_b=150, fa_b=140, th_f=24, th_b=-20, face="yell")]
    elif kind == "o2":  # O2 wanderer: drags the tank dolly, swings it; *2 = after the tank is knocked loose
        dr = holder("o2drag")
        A["idle"] = [P(ua_f=20, fa_f=60, ua_b=-20, fa_b=10, hold_b=dr, lean=8, face="sleep"), P(ua_f=20, fa_f=64, ua_b=-20, fa_b=10, hold_b=dr, lean=8, hy=1, face="sleep")]
        A["walk"] = walk_cycle(swing=12, arm=4, lean=10)
        for f in A["walk"]:
            f.update(ua_b=-20, fa_b=10, hold_b=dr)
        A["atk"] = [P(lean=-12, ua_f=-140, fa_f=-150, ua_b=-150, fa_b=-160, hold=holder("o2_up"), th_f=16, th_b=-20, face="yell"),
                    P(lean=18, ua_f=86, fa_f=92, ua_b=80, fa_b=90, th_f=28, th_b=-24, hold=holder("o2_h"), face="yell"),
                    P(lean=22, ua_f=70, fa_f=80, ua_b=60, fa_b=76, th_f=30, th_b=-26, hold=holder("o2_h"), face="yell")]
        A["idle2"] = [P(ua_f=20, fa_f=60, ua_b=-6, fa_b=20, lean=8, face="hurt"), P(ua_f=20, fa_f=64, ua_b=-6, fa_b=20, lean=8, hy=1, face="norm")]
        A["walk2"] = walk_cycle(swing=12, arm=12, lean=10)
        A["atk2"] = [P(lean=-6, ua_f=170, fa_f=176, ua_b=-20, fa_b=30, face="yell"), P(lean=16, ua_f=86, fa_f=70, ua_b=-30, fa_b=20, th_f=20, th_b=-20, face="yell")]
    elif kind == "barium":  # contrast chugger: sips, then lobs the cup
        cp = holder("cup")
        A["idle"] = [P(ua_f=60, fa_f=150, hold=cp, ua_b=-6, fa_b=20, face="grin"), P(ua_f=64, fa_f=160, hold=cp, ua_b=-6, fa_b=20, hy=1, face="norm")]
        A["walk"] = walk_cycle(swing=16, arm=8)
        for f in A["walk"]:
            f.update(ua_f=60, fa_f=150, hold=cp)
        A["atk"] = [P(lean=-12, ua_f=-150, fa_f=-165, ua_b=40, fa_b=80, th_f=20, th_b=-24, hold=cp, face="grin"),
                    P(lean=14, ua_f=100, fa_f=96, ua_b=-20, fa_b=20, th_f=30, sh_f=10, th_b=-26, face="yell")]
        A["lob"] = A["atk"]
    elif kind == "apron":
        return {**enemy_anims("wanderer")}
    elif kind == "lou":  # mini-boss: stance, lumbering walk, linebacker charge, stomp, film throw, winded
        A["idle"] = [P(lean=10, ua_f=40, fa_f=110, ua_b=30, fa_b=100, th_f=18, th_b=-16, face="grin"), P(lean=10, ua_f=40, fa_f=114, ua_b=30, fa_b=104, th_f=18, th_b=-16, hy=1, face="grin")]
        A["walk"] = walk_cycle(swing=18, arm=14, lean=10)
        A["charge"] = walk_cycle(swing=40, arm=0, lean=38, bob=2)
        for f in A["charge"]:
            f.update(ua_f=-50, fa_f=-20, ua_b=-60, fa_b=-30, head=-14, face="yell")
        A["stomp"] = [P(lean=-6, th_f=80, sh_f=10, ua_f=-140, fa_f=-150, ua_b=-140, fa_b=-150, face="yell", lift=4),
                      P(lean=18, th_f=20, sh_f=0, th_b=-20, ua_f=60, fa_f=60, ua_b=50, fa_b=50, face="yell", hy=3)]
        A["throw"] = [P(lean=-12, ua_f=-150, fa_f=-170, hold=holder("film"), ua_b=40, fa_b=80, th_f=20, th_b=-24, face="grin"),
                      P(lean=16, ua_f=100, fa_f=96, ua_b=-20, fa_b=20, th_f=30, sh_f=10, th_b=-26, face="yell")]
        A["tired"] = [P(lean=34, head=10, ua_f=60, fa_f=30, ua_b=50, fa_b=24, th_f=20, sh_f=10, th_b=-10, sh_b=-6, face="hurt", hy=3),
                      P(lean=36, head=12, ua_f=62, fa_f=30, ua_b=52, fa_b=24, th_f=20, sh_f=10, th_b=-10, sh_b=-6, face="sleep", hy=4)]
    base = hero_anims("nick")
    for k in ("hurt", "fall", "down", "getup", "dizzy"):
        A[k] = base[k]
    A["held"] = [P(lean=-10, head=-10, ua_f=-20, fa_f=-40, ua_b=-30, fa_b=-60, face="hurt", lift=3)]
    A["sleep"] = [{**base["down"][0], "face": "sleep"}]
    return A
