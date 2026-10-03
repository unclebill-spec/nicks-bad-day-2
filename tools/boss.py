"""Turbo Tilly, the Electric Wheelchair Lady (Level 1 boss). Chair drawn in code, Tilly herself on the rig."""
from __future__ import annotations

import math

from rig import INK, P, Raster, figure, hair_cap
from chars import SKIN

# v0.6: Bill's rule is bosses >= 5x a nurse, so Tilly is drawn at SC x her old size (same layout, every
# coordinate below is in "base units" and SR scales it to real pixels).
SC = 1.8
BW, BH, BAX, BAY = 120, 100, 60, 96
W, H, AX, AY = int(BW * SC), int(BH * SC), int(BAX * SC), int(BAY * SC)


class SR:
    """Scaled raster: same calls as Raster but in base units; strokes and single pixels grow with the scale."""

    def __init__(self, s):
        self.s = s
        self.R = Raster(W, H)

    def _p(self, p):
        return (p[0] * self.s, p[1] * self.s)

    def rect(self, x, y, w, h, c):
        s = self.s
        x0, y0 = int(round(x * s)), int(round(y * s))
        self.R.rect(x0, y0, max(1, int(round((x + w) * s)) - x0), max(1, int(round((y + h) * s)) - y0), c)

    def set(self, x, y, c):
        self.rect(x, y, 1, 1, c)

    def ellipse(self, c, rx, ry, col, shade=None, rim=True):
        self.R.ellipse(self._p(c), rx * self.s, ry * self.s, col, shade, rim)

    def poly(self, pts, col, rim=True):
        self.R.poly([self._p(p) for p in pts], col, rim)

    def line(self, a, b, col):
        self.R.capsule(self._p(a), self._p(b), self.s * 0.9, col, rim=False)


def tilly_body():
    from chars import hero_body
    return hero_body(thigh=9, shin=9, torso=15, head=7.4, uarm=7, farm=7, arm_w=3.4, leg_w=4.6, torso_w=13, belly=1.5,
                     skin=SKIN["old"][0], skin_s=SKIN["old"][1], hair_c="#b88ae0", hair_s="#8a5ab8",
                     hair=hair_cap(top=0.15, back=0.15, grow=2.6, bumps=1.6, fringe=0, seed=5), glasses="#c83a8a",
                     shirt="#e898c0", shirt_s="#b86a94", sleeve="#e898c0", sleeve_s="#b86a94", sleeve_len=1.7,
                     pants="#5a3a8a", pants_s="#3e2668", shoe="#f4f4f8", shoe_s="#b8bcc8", vneck=False, steth=False,
                     badge=None, blush="#f08aa0", mouth="#c83a5a")


def pearls(S, T, hip, neck, lean, b):
    nx, ny = T(neck)
    k = int(round(b.get("pscale", 1)))
    for i in range(5):
        S.rect(int(nx + (i - 2) * k * 1.4) - k // 2, int(ny + (2 + (1 if i in (0, 4) else 2 if i == 2 else 1.5)) * k), k, k, "#ffffff")


def wheel(S, c, r, spin, col="#2a2a34", hub="#c8ccd6"):
    S.ellipse(c, r, r, col)
    S.ellipse(c, r - 2.2, r - 2.2, "#8a94a4", rim=False)
    S.ellipse(c, r - 3.4, r - 3.4, "#5a6474", rim=False)
    for k in range(4):
        a = spin + k * math.pi / 4
        S.line((c[0] - math.cos(a) * (r - 3), c[1] - math.sin(a) * (r - 3)), (c[0] + math.cos(a) * (r - 3), c[1] + math.sin(a) * (r - 3)), "#d8dee8")
    S.ellipse(c, 1.6, 1.6, hub)


def frame(state="idle", k=0):
    S = SR(SC)
    g = BAY  # ground y
    shake = (1 if k % 2 else -1) if state == "rev" else 0
    bob = 1 if (state in ("idle", "drive") and k % 2) else 0
    ox = BAX + shake
    spin = k * math.pi / 8 * (3 if state in ("drive", "rev") else 0.4)
    # flag pole + flag
    fx = ox - 26
    S.line((fx, g - 18), (fx - 4, g - 92), "#7c8696")
    wave = [0, 1, 2, 1][k % 4]
    S.poly([(fx - 4, g - 92), (fx - 18, g - 88 + wave), (fx - 4, g - 82)], "#ff8a1e")
    S.set(int(fx - 9), int(g - 88), "#ffd84a")
    # rear drive wheel (far side, darker)
    wheel(S, (ox - 14, g - 13), 12, spin + 0.4, "#1a1a22", "#8a94a4")
    # chair body: base + battery box
    S.poly([(ox - 30, g - 20), (ox + 26, g - 20), (ox + 30, g - 12), (ox - 30, g - 12)], "#3a3e4a")
    S.rect(ox - 29, g - 19, 55, 2, "#5a6070")
    # battery pack (the weak point)
    S.rect(ox - 21, g - 31, 26, 12, INK)
    S.rect(ox - 20, g - 30, 24, 10, "#4a5262")
    S.rect(ox - 20, g - 30, 24, 1, "#6a7282")
    if state == "open":
        S.rect(ox - 19, g - 29, 22, 8, "#1a1a22")
        for i in range(4):
            S.rect(ox - 17 + i * 5, g - 27, 3, 5, ["#ffd84a", "#ff5a3a", "#3aa0ff", "#8ae87a"][i])
        S.poly([(ox - 21, g - 31), (ox + 5, g - 31), (ox + 1, g - 44 - k), (ox - 25, g - 42 - k)], "#6a7282")  # lid flipped up
        S.rect(ox - 10, g - 25, 3, 2, "#ffffff" if k % 2 else "#ffe84a")
    else:
        S.rect(ox - 15, g - 27, 14, 4, "#2a2e3a")
        S.rect(ox - 14, g - 26, 4, 2, "#8ae87a" if state != "defeat" else "#ff3a3a")
        S.rect(ox - 9, g - 26, 4, 2, "#8ae87a" if state not in ("defeat", "hurt") else "#3a3e4a")
        S.rect(ox - 4, g - 26, 2, 2, "#8ae87a" if state in ("idle", "drive", "rev") else "#3a3e4a")
    # seat + backrest
    S.rect(ox - 24, g - 38, 30, 8, INK); S.rect(ox - 23, g - 37, 28, 6, "#7a3ab8"); S.rect(ox - 23, g - 37, 28, 1, "#a46ae0")
    S.rect(ox - 28, g - 66, 8, 36, INK); S.rect(ox - 27, g - 65, 6, 34, "#7a3ab8"); S.rect(ox - 27, g - 65, 1, 34, "#a46ae0")
    S.rect(ox - 29, g - 68, 4, 4, "#3a3e4a")  # push handle
    # Tilly (seated on the rig)
    pose = dict(plant=False, th_f=86, sh_f=6, th_b=82, sh_b=2, lean=-2, ua_f=60, fa_f=96, ua_b=50, fa_b=92, face="norm")
    if state == "drive":
        pose.update(lean=8, face="grin", head=4)
    elif state == "rev":
        pose.update(lean=12, face="yell", ua_f=70, fa_f=80)
    elif state == "honk":
        pose.update(lean=6, face="yell", ua_f=80, fa_f=60, head=6)
    elif state == "call":
        pose.update(ua_f=150, fa_f=176, face="yell", lean=-6)
    elif state == "open":
        pose.update(lean=-10, face="hurt", ua_f=10, fa_f=-20, ua_b=-10, fa_b=-30, head=-10)
    elif state == "hurt":
        pose.update(lean=-14, face="hurt", ua_f=-30, fa_f=-60, head=-14)
    elif state == "defeat":
        pose.update(lean=-16, face="sleep", ua_f=20, fa_f=10, ua_b=10, fa_b=0, head=-20)
    elif state == "laugh":
        pose.update(lean=-8, face="grin", ua_f=120, fa_f=150, head=-8)
    s = SC
    b = {k: (v * s if isinstance(v, (int, float)) and not isinstance(v, bool) else v) for k, v in tilly_body().items()}
    b["pattern"] = pearls
    b["pscale"] = s
    fw, fh, fax, fay = int(88 * s), int(80 * s), int(44 * s), int(76 * s)
    fig, meta = figure(b, P(**pose), W=fw, H=fh, ax=fax, ay=fay)
    # paste so her hips sit on the seat (hip in figure space is -(thigh+shin+foot) above the anchor)
    hip_y = -(9 + 9 + 2) * s
    px, py = int((ox - 8) * s - fax), int((g - 34) * s - (fay + hip_y) - bob * s)
    for y in range(fig.h):
        for x in range(fig.w):
            c = fig.p[y][x]
            if c:
                S.R.set(px + x, py + y, c)
    # armrest + joystick + horn on the front
    S.rect(ox - 6, g - 46, 18, 3, INK); S.rect(ox - 5, g - 45, 16, 1, "#3a3e4a")
    S.rect(ox + 10, g - 50, 2, 5, "#2a2a34"); S.ellipse((ox + 11, g - 51), 1.6, 1.6, "#ff3a3a")
    bulb = 2.4 if state == "honk" and k % 2 else 3.4
    S.ellipse((ox + 15, g - 47), bulb, bulb, "#ff3a3a", "#c82020")
    S.poly([(ox + 18, g - 48), (ox + 26, g - 52), (ox + 26, g - 42), (ox + 18, g - 46)], "#ffcc44")
    # basket with yarn
    S.rect(ox + 14, g - 34, 14, 9, INK); S.rect(ox + 15, g - 33, 12, 7, "#c8a060")
    for x in range(16, 27, 3):
        S.rect(ox + x, g - 33, 1, 7, "#a07a40")
    S.ellipse((ox + 18, g - 35), 3, 3, "#ff6ab0"); S.ellipse((ox + 24, g - 35), 3, 3, "#7ad8ff")
    # front frame + footrest + caster
    S.line((ox + 4, g - 20), (ox + 22, g - 8), "#3a3e4a"); S.line((ox + 5, g - 20), (ox + 23, g - 8), "#5a6070")
    S.rect(ox + 16, g - 9, 12, 2, "#3a3e4a")
    wheel(S, (ox + 24, g - 5), 5, spin * 1.6)
    # near drive wheel
    wheel(S, (ox - 8, g - 13), 13, spin)
    # front bumper sticker
    S.rect(ox - 28, g - 17, 9, 3, "#ffd84a"); S.set(ox - 26, g - 16, INK); S.set(ox - 23, g - 16, INK)
    if state == "defeat" and k % 2:
        for (x, y) in ((ox - 14, g - 40), (ox - 10, g - 44)):
            S.ellipse((x, y), 2.5, 2.5, "#9a9aa4", rim=False)
    return S.R


ANIMS = {"idle": ("idle", 2), "drive": ("drive", 4), "rev": ("rev", 2), "honk": ("honk", 2), "call": ("call", 1),
         "open": ("open", 2), "hurt": ("hurt", 1), "defeat": ("defeat", 2), "laugh": ("laugh", 2)}
