"""Side-view pixel puppet for Nick's Very Bad, Terrible Bad Day Part II.

Builds on the Gravewake sprite writer's `Sprite` (one colour per pixel, hard 1px ink outline, no blending):
each body part is a capsule / ellipse rasterised with an ink rim first and the colour inside, so overlapping
limbs stay readable. Angles are degrees: 0 points straight down, +90 points forward (the way the figure faces),
180 points up, -90 points backward.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "vendor" / "gravewake"))
from sprite_writer import Sprite  # noqa: E402  (Master Builder's Gravewake writer, vendored copy)

INK = "#1a1020"


def vec(a, l):
    r = math.radians(a)
    return (math.sin(r) * l, math.cos(r) * l)


def add(p, q):
    return (p[0] + q[0], p[1] + q[1])


class Raster(Sprite):
    """Sprite plus filled primitives. Coordinates are floats; pixel centres are at +0.5."""

    def capsule(self, a, b, w, color, shade=None, rim=True, light=(0.6, -0.8)):
        r = w / 2.0
        x0, x1 = int(min(a[0], b[0]) - r - 2), int(max(a[0], b[0]) + r + 2)
        y0, y1 = int(min(a[1], b[1]) - r - 2), int(max(a[1], b[1]) + r + 2)
        dx, dy = b[0] - a[0], b[1] - a[1]
        L2 = dx * dx + dy * dy or 1e-6
        nx, ny = -dy, dx
        nl = math.hypot(nx, ny) or 1
        nx, ny = nx / nl, ny / nl
        if nx * light[0] + ny * light[1] < 0:
            nx, ny = -nx, -ny
        passes = ([(r + 1.0, INK)] if rim else []) + [(r, color)]
        for rr, col in passes:
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    px, py = x + 0.5, y + 0.5
                    t = max(0.0, min(1.0, ((px - a[0]) * dx + (py - a[1]) * dy) / L2))
                    cx, cy = a[0] + t * dx, a[1] + t * dy
                    d = math.hypot(px - cx, py - cy)
                    if d <= rr:
                        c = col
                        if col != INK and shade and ((px - cx) * nx + (py - cy) * ny) < -rr * 0.25:
                            c = shade
                        self.set(x, y, c)

    def ellipse(self, c, rx, ry, color, shade=None, rim=True):
        for rr, col in ([(1.0, INK)] if rim else []) + [(0.0, color)]:
            ax, ay = rx + rr, ry + rr
            for y in range(int(c[1] - ay - 1), int(c[1] + ay + 2)):
                for x in range(int(c[0] - ax - 1), int(c[0] + ax + 2)):
                    px, py = x + 0.5 - c[0], y + 0.5 - c[1]
                    if (px / ax) ** 2 + (py / ay) ** 2 <= 1.0:
                        cc = col
                        if col != INK and shade and (px * 0.5 - py * 0.85) < -0.45 * max(rx, ry):
                            cc = shade
                        self.set(x, y, cc)

    def poly(self, pts, color, rim=True):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        def inside(px, py, grow):
            # point in polygon, optionally grown by `grow` px via distance to edges
            n = len(pts)
            c = False
            for i in range(n):
                (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
                if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / ((y2 - y1) or 1e-9) + x1:
                    c = not c
            if c or not grow:
                return c
            for i in range(n):
                (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
                dx, dy = x2 - x1, y2 - y1
                L2 = dx * dx + dy * dy or 1e-9
                t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / L2))
                if math.hypot(px - x1 - t * dx, py - y1 - t * dy) <= grow:
                    return True
            return False
        for grow, col in ([(1.0, INK)] if rim else []) + [(0, color)]:
            for y in range(int(min(ys)) - 2, int(max(ys)) + 3):
                for x in range(int(min(xs)) - 2, int(max(xs)) + 3):
                    if inside(x + 0.5, y + 0.5, grow):
                        self.set(x, y, col)

    def line(self, a, b, color):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
        for i in range(n + 1):
            t = i / n
            self.set(int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t), color)

    def mirror(self):
        for row in self.p:
            row.reverse()

    def bbox(self):
        ys = [y for y in range(self.h) if any(self.p[y])]
        xs = [x for x in range(self.w) if any(self.p[y][x] for y in range(self.h))]
        if not ys:
            return None
        return min(xs), min(ys), max(xs), max(ys)

    def shifted(self, dx, dy):
        out = Raster(self.w, self.h)
        for y in range(self.h):
            for x in range(self.w):
                c = self.p[y][x]
                if c:
                    out.set(x + dx, y + dy, c)
        return out


DEFAULT_POSE = dict(hx=0, hy=0, lean=4, head=0, ua_f=18, fa_f=125, ua_b=-8, fa_b=115, th_f=14, sh_f=4, th_b=-14, sh_b=-6,
                    rot=0, face="norm", flip=False, plant=True, hold=None, hold_b=None, lift=0)


def P(**kw):
    d = dict(DEFAULT_POSE)
    d.update(kw)
    return d


def figure(body: dict, pose: dict, W=88, H=80, ax=44, ay=76):
    """Rasterise one frame. Returns (Raster, meta) where meta has the front hand / back hand / head points
    relative to the anchor (feet centre)."""
    pose = {**DEFAULT_POSE, **pose}
    b = body
    BIG = 2  # oversize temp canvas to allow rotation / planting
    S = Raster(W * BIG, H * BIG)
    AX, AY = W * BIG / 2, H * BIG - 8 * BIG
    rot = pose["rot"]
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def T(p):  # pose space (anchor-relative) -> temp canvas, with global rotation about the hip
        x, y = p[0] - hip[0], p[1] - hip[1]
        x, y = x * cr - y * sr, x * sr + y * cr
        return (AX + hip[0] + x, AY + hip[1] + y)

    th, sh = b["thigh"], b["shin"]
    def leg_drop(ta, sa):
        return math.cos(math.radians(ta)) * th + math.cos(math.radians(sa)) * sh
    drop = max(leg_drop(pose["th_f"], pose["sh_f"]), leg_drop(pose["th_b"], pose["sh_b"]))
    hip = (pose["hx"], -(drop + b.get("foot", 2)) + pose["hy"] - pose["lift"])
    if not pose["plant"]:
        hip = (pose["hx"], -(th + sh + b.get("foot", 2)) + pose["hy"] - pose["lift"])
    lean = pose["lean"]
    neck = add(hip, vec(180 - lean, b["torso"]))
    shoulder = add(neck, vec(-lean, b.get("sh_drop", 2.5)))
    head_c = add(neck, vec(180 - lean - pose["head"], b["head"] + 0.5))
    head_c = (head_c[0] + b.get("head_fwd", 1), head_c[1])
    meta = {}

    def arm(ua, fa, front):
        s0 = add(shoulder, (0.8 if front else -0.8, 0))
        el = add(s0, vec(ua, b["uarm"]))
        hd = add(el, vec(fa, b["farm"]))
        skin, sks = b["skin"], b["skin_s"]
        sleeve, sls = b["sleeve"], b["sleeve_s"]
        if not front:
            skin, sks, sleeve, sls = sks, sks, sls, sls
        S.capsule(T(el), T(hd), b["arm_w"], skin, sks)
        S.capsule(T(s0), T(el), b["arm_w"] + 0.6, skin, sks)
        sl = b.get("sleeve_len", 0.55)
        if sl > 0:
            sa, sf = b.get("sleeve_add", 1.4), b.get("sleeve_add_fa", 1.2)  # v0.10.3: Will's knit sleeves sit closer to the arm
            # v0.10.3: long sleeves used to run 0.8 x uarm past the elbow (a round lump at Will's belly); "sleeve_clip" stops them at the elbow
            usl = min(sl, 1.0) if b.get("sleeve_clip") else sl
            S.capsule(T(s0), T(add(s0, vec(ua, b["uarm"] * usl))), b["arm_w"] + sa, sleeve, sls)
            if sl > 1.0:  # long sleeves go down the forearm too
                S.capsule(T(el), T(add(el, vec(fa, b["farm"] * (sl - 1.0)))), b["arm_w"] + sf, sleeve, sls)
                if b.get("cuff"):  # v0.10.1 Will's sweater: a ribbed cuff at the end of the long sleeve
                    cc, ccs = b["cuff"]
                    S.capsule(T(add(el, vec(fa, b["farm"] * (sl - 1.0) - 1.6))), T(add(el, vec(fa, b["farm"] * (sl - 1.0)))), b["arm_w"] + sf,
                              cc if front else ccs, ccs)
        S.ellipse(T(hd), b.get("fist", 1.6), b.get("fist", 1.6), skin, None)
        return hd, fa

    def leg(ta, sa, front):
        hs = b.get("hip_sep", 1.2 if b.get("gown_len") else 1.9)  # v0.8.1: hip joints further apart so the legs part right under the seat
        h0 = add(hip, (hs if front else -hs, 0))
        kn = add(h0, vec(ta, th))
        an = add(kn, vec(sa, sh))
        pc, ps = b["pants"], b["pants_s"]
        lc, lcs = b.get("leg_skin", pc), b.get("leg_skin_s", ps)
        shoe, shoe_s = b["shoe"], b["shoe_s"]
        if not front:
            pc, lc, shoe = ps, lcs, shoe_s
        S.capsule(T(kn), T(an), b["leg_w"], lc, lcs)
        S.capsule(T(h0), T(kn), b["leg_w"] + b.get("thigh_add", 0.4), pc, ps)
        if b.get("pant_len", 1.0) > 0.5 and lc != pc:
            S.capsule(T(kn), T(add(kn, vec(sa, sh * (b["pant_len"] - 1.0)))), b["leg_w"] + 0.4, pc, ps) if b["pant_len"] > 1.0 else None
        toe = add(an, vec(sa + 90, b.get("foot_len", 3.2)))
        heel = add(an, vec(sa - 90, 0.8))
        S.capsule(T(heel), T(toe), b.get("foot_w", 2.6), shoe, b["shoe_s"])
        if b.get("sock"):
            S.capsule(T(an), T(add(an, vec(sa + 180, 1.5))), b["leg_w"], b["sock"], b["sock"], rim=False)
        return an

    # ---- back limbs
    hb = arm(pose["ua_b"], pose["fa_b"], False)
    leg(pose["th_b"], pose["sh_b"], False)
    # ---- torso
    tw = b["torso_w"]
    # v0.8.1 (Bill: "they look like they have a onesie or a diaper on ... no waist"): the torso is no longer one capsule
    # whose round bottom swallowed the hips. It is a shaped top (shoulders -> narrower waist -> slight flare at the hips,
    # ending in a hem just below the hip joint), with the pants' seat + waistband/drawstring peeking out under the hem
    # and the legs hanging separately from it, so the crotch reads as a gap, not a nappy.
    T_ = b["torso"]
    hw = tw / 2
    gown = bool(b.get("gown_len"))
    wst = b.get("waist", 0.4 if gown else 2.0)        # waist inset per side
    hem = b.get("hem", 0.5 if gown else -1.2)         # where the top ends (along the torso, 0 = hip joint)
    flare = b.get("hip_flare", 0.2 if gown else 0.9)  # hips a touch wider than the waist
    def up(u, sd):
        return add(add(hip, vec(180 - lean, u)), vec(90 - lean, sd))
    if not gown:  # seat of the pants + waistband just below the hem
        band = b.get("belt") or b.get("band", b["pants_s"])
        seat = [up(hem + 2.5, -hw + 1.0), up(hem + 2.5, hw - 1.0), up(hem - 1.4, hw - 0.6), up(hem - 3.4, 1.4), up(hem - 3.6, -0.6), up(hem - 1.6, -hw + 0.6)]
        S.poly([T(q) for q in seat], b["pants"])
        S.poly([T(up(hem + 0.4, -hw + 0.9)), T(up(hem + 0.4, hw - 0.7)), T(up(hem - 1.2, hw - 0.7)), T(up(hem - 1.2, -hw + 0.9))], band, rim=False)
        if b.get("drawstring", not b.get("belt")):
            ds = b.get("drawstring_c", "#e8eef4")
            for k in (0.0, 1.0, 2.0):
                S.set(*map(int, T(up(hem - 0.6 - k, hw * 0.35 + (0.6 if k > 1 else 0)))), ds)
        if b.get("belt"):
            S.set(*map(int, T(up(hem - 0.5, hw * 0.45))), b.get("buckle", "#c8b070"))
    top = [up(hem, -hw - flare + 0.3), up(T_ * 0.38, -hw + wst), up(T_ * 0.72, -hw - 0.1), up(T_ - 1.4, -hw + 0.5),
           up(T_ + 0.5, -hw * 0.45), up(T_ + 0.5, hw * 0.4), up(T_ - 1.4, hw - 0.3), up(T_ * 0.72, hw + 0.1),
           up(T_ * 0.38, hw - wst + 0.3), up(hem, hw + flare)]
    S.poly([T(q) for q in top], b["shirt"])
    S.poly([T(q) for q in (up(hem + 1.2, -hw - flare + 1.4), up(T_ * 0.38, -hw + wst + 1.0), up(T_ * 0.72, -hw + 1.0), up(T_ - 1.6, -hw + 1.6),
                           up(T_ - 1.6, -hw + 2.8), up(T_ * 0.72, -hw + 2.3), up(T_ * 0.38, -hw + wst + 2.2), up(hem + 1.2, -hw - flare + 2.6))], b["shirt_s"], rim=False)
    if not gown:  # hem line: a darker stitch row just above the top's bottom edge
        S.line(T(up(hem + 1.1, -hw - flare + 1.2)), T(up(hem + 1.1, hw + flare - 1.0)), b.get("hem_c", b["shirt_s"]))
    if b.get("belly"):
        bc = add(hip, vec(180 - lean, b["torso"] * 0.42))
        S.ellipse(T((bc[0] + b["belly"] * 0.5, bc[1])), tw / 2 + b["belly"] * 0.5, b["torso"] * 0.36, b["shirt"], b["shirt_s"])
    if b.get("gown_len"):  # hospital gown / robe skirt over the thighs
        g0 = add(hip, vec(180 - lean, 3))
        gl = b["gown_len"]
        fl, bl = add(g0, vec(pose["th_f"] * 0.7, gl)), add(g0, vec(pose["th_b"] * 0.7, gl))
        S.poly([T(add(g0, (-tw / 2, 0))), T(add(g0, (tw / 2, 0))), T(add(fl, (tw / 2 + 1, 0))), T(add(bl, (-tw / 2 - 1, 0)))], b["shirt"])
    pat = b.get("pattern")
    S_hip, S_neck = T(hip), T(neck)
    if pat:
        pat(S, T, hip, neck, lean, b)
    # neckline / stethoscope / badge
    if b.get("vneck"):
        n0 = add(neck, vec(180 - lean, 0.5))
        S.poly([T(add(n0, (-1.5, 0))), T(add(n0, (2.5, 0))), T(add(n0, vec(-lean, 3.5)))], b["skin"], rim=False)
    if b.get("steth"):
        a1, a2 = add(neck, vec(-lean + 40, 4)), add(neck, vec(-lean - 30, 3))
        S.line(T(add(neck, (2.0, 0.5))), T(a1), "#3a3f4a")
        S.set(*map(int, T(add(a1, (0, 1)))), "#c8ccd6")
    if b.get("badge"):
        bp = T(add(hip, vec(180 - lean, b["torso"] * 0.62)))
        S.rect(int(bp[0] + 1), int(bp[1]), 2, 2, b["badge"])
    # ---- head
    hc = T(head_c)
    r = b["head"]
    hair_back = b.get("hair_back")
    if hair_back:
        hair_back(S, hc, r, b, pose)
    S.ellipse(hc, r, r * 1.02, b["skin"], b["skin_s"])
    face(S, hc, r, b, pose)
    hair = b.get("hair")
    if hair:
        hair(S, hc, r, b, pose)
    # ---- front limbs
    leg(pose["th_f"], pose["sh_f"], True)
    hf = arm(pose["ua_f"], pose["fa_f"], True)
    for key, hp in (("hold", hf), ("hold_b", hb)):
        if pose.get(key):
            pose[key](S, T, hp[0], hp[1], b)
    meta["hand"] = T(hf[0]) + (hf[1],)
    meta["hand_b"] = T(hb[0]) + (hb[1],)
    meta["head"] = hc
    if pose["flip"]:
        S.mirror()
        for k in ("hand", "hand_b", "head"):
            v = meta[k]
            meta[k] = (S.w - v[0],) + tuple(v[1:2]) + ((-v[2],) if len(v) > 2 else ())
    # ---- plant + crop into the cell
    bb = S.bbox()
    dy = 0
    if bb and pose["plant"]:
        dy = int(round(AY - 1 - bb[3]))
        if pose.get("lift"):
            dy -= int(pose["lift"])
    ox, oy = int(AX - ax), int(AY - ay)
    out = Raster(W, H)
    for y in range(H):
        for x in range(W):
            sy = y + oy - dy
            sx = x + ox
            if 0 <= sy < S.h and 0 <= sx < S.w:
                c = S.p[sy][sx]
                if c:
                    out.p[y][x] = c
    for k in ("hand", "hand_b", "head"):
        v = meta[k]
        meta[k] = [round(v[0] - ox - ax, 1), round(v[1] - oy + dy - ay, 1)] + ([round(v[2] if not pose["flip"] else v[2], 1)] if len(v) > 2 else [])
    return out, meta


def face(S, hc, r, b, pose):
    f = pose["face"]
    k = max(1, int(round(r / 6.6)))  # feature scale: 1 in game, 2 for HUD portraits
    ex, ey = int(hc[0] + r * 0.42), int(hc[1] - r * 0.05)
    S.rect(int(hc[0] - r * 0.25), int(hc[1] + 0.5), k, k, b["skin_s"])  # ear
    S.rect(int(hc[0] + r + 0.6), int(hc[1] + 0.6), k, k, b["skin"])  # nose
    S.rect(int(hc[0] + r + 0.6), int(hc[1] + 0.6 + k), k, 1, INK)
    if f == "sleep":
        S.rect(ex - (k - 1), ey + k, 2 * k, 1 if k == 1 else 2, INK)
    elif f == "hurt":
        for i in range(-1, 2):
            S.rect(ex + (1 - abs(i)) * k, ey + i * k, k, k, INK)
    elif b.get("heavy_lids") and f != "yell":  # v0.8 Nate: half-closed, bored eyes under a heavy lid
        S.rect(ex, ey + k, k, k, INK)
        S.rect(ex - k, ey, 2 * k, k, b["skin_s"])
        if b.get("eye_white"):
            S.rect(ex - k, ey + k, k, k, "#f4f4f4")
        if k > 1:
            S.rect(ex - k, ey - k - 1, 3 * k, 1, b.get("hair_s", INK))
    else:
        S.rect(ex, ey, k, 2 * k, INK)
        if b.get("eye_white"):
            S.rect(ex - k, ey, k, 2 * k if k > 1 else 1, "#f4f4f4")
        if k > 1:
            S.set(ex + 1, ey, "#ffffff")
            S.rect(ex - k, ey - k - 1, 3 * k, 1, b.get("hair_s", INK))  # brow
    my = int(hc[1] + r * 0.62)
    if f in ("yell", "hurt"):
        S.rect(ex - k, my - k, 2 * k, 2 * k, "#5a1020")
    elif f == "grin":
        S.rect(ex - k, my, 3 * k, 1 if k == 1 else 2, INK)
        S.rect(ex + 2 * k - 1, my - k, k, k, INK)
    else:
        S.rect(ex - (k - 1), my, k * 2 - 1, 1 if k == 1 else 2, b.get("mouth", "#a8505a"))
    if b.get("glasses"):
        gc = b["glasses"]
        x0, x1, y0, y1 = ex - k, ex + k * 2 - (1 if k > 1 else 0), ey - k, ey + 2 * k + (1 if k > 1 else 0)
        S.rect(x0, y0, x1 - x0 + 1, 1, gc); S.rect(x0, y1, x1 - x0 + 1, 1, gc)
        S.rect(x0 - 1, y0, 1, y1 - y0 + 1, gc); S.rect(x1 + 1, y0, 1, y1 - y0 + 1, gc)
        S.line((x0 - 1, y0 + 1), (hc[0] - r * 0.3, y0), gc)
    if b.get("freckles"):
        S.rect(ex - k, ey + 2 * k + 1, k, k, b["freckles"]); S.rect(ex + k, ey + 3 * k + 1, k, k, b["freckles"])
    if b.get("beard"):
        for yy in range(int(hc[1] + r * 0.35), int(hc[1] + r + 1.5)):
            for xx in range(int(hc[0] - r * 0.1), int(hc[0] + r + 0.5)):
                if (xx + 0.5 - hc[0]) ** 2 + (yy + 0.5 - hc[1]) ** 2 <= (r + 0.6) ** 2 and S.p[yy][xx] not in (None, INK, "#5a1020"):
                    S.set(xx, yy, b["beard"])
        S.rect(ex - (k - 1), my, 2 * k - 1, k, "#5a1020")
    if b.get("blush"):
        S.rect(ex - 2 * k, my - k, k, k, b["blush"])


def in_head(hc, r, x, y, grow=0):
    return (x + 0.5 - hc[0]) ** 2 + (y + 0.5 - hc[1]) ** 2 <= (r + grow) ** 2


def hair_cap(top=-0.15, back=0.2, grow=0.9, spikes=0, fringe=1, bumps=0, seed=1):
    """Generic hair: covers the head above `top`*r and behind `back`*r."""
    def draw(S, hc, r, b, pose):
        c, s = b["hair_c"], b["hair_s"]
        R = r + grow
        for y in range(int(hc[1] - R - 3), int(hc[1] + R + 2)):
            for x in range(int(hc[0] - R - 3), int(hc[0] + R + 3)):
                dx, dy = x + 0.5 - hc[0], y + 0.5 - hc[1]
                rr = R
                if bumps:
                    a = math.atan2(dy, dx)
                    rr = R + bumps * (0.5 + 0.5 * math.sin(a * 11 + seed))
                if dx * dx + dy * dy > rr * rr:
                    continue
                if dy < top * r or dx < -back * r and dy < r * 0.55:
                    col = s if (dy > top * r - 1.4 and dx > -back * r) or dx < -r * 0.75 else c
                    if bumps and (x * 2 + y * 3) % 7 == 0:
                        col = s
                    S.set(x, y, col)
        # ink rim on the top of the hair
        for y in range(int(hc[1] - R - 4), int(hc[1] + 2)):
            for x in range(int(hc[0] - R - 4), int(hc[0] + R + 4)):
                if S.p[y][x] is None and any(S.p[y + dy][x + dx] in (c, s) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                                             if 0 <= y + dy < S.h and 0 <= x + dx < S.w):
                    S.set(x, y, INK)
        for i in range(spikes):
            sx = int(hc[0] - r * 0.6 + i * r * 0.55)
            S.set(sx, int(hc[1] - R - 1), c); S.set(sx, int(hc[1] - R - 2), INK); S.set(sx + 1, int(hc[1] - R - 1), INK)
        if fringe:
            fx = int(hc[0] + r * 0.55)
            S.set(fx, int(hc[1] + top * r), c); S.set(fx + 1, int(hc[1] + top * r), c)
    return draw
