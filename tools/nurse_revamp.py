"""Nurse revamp (branch nurse-revamp): in-between frames for the six heroes plus a palette-locked
pixel cleanup pass. No new colours are introduced: every pixel ends up as a colour the body already uses."""
from PIL import Image

HEROES = ("nick", "kim", "will", "jackie", "nate", "heather")
ATK = ("atk1", "atk2", "atk3", "atk4", "lz1", "lz2", "lz3", "hc1", "hc2", "hc3")


def lerp(a, b, t):
    out = dict(a if t < 0.5 else b)
    for k, v in a.items():
        w = b.get(k)
        if isinstance(v, (int, float)) and isinstance(w, (int, float)) and not isinstance(v, bool) and not isinstance(w, bool):
            out[k] = v + (w - v) * t
    return out


def smooth(A):
    """Insert in-betweens. Frame layouts must match src/hero.js pose()."""
    A = dict(A)
    g = A["idle"][0]
    if len(A["idle"]) == 2:
        a, b = A["idle"]; A["idle"] = [a, lerp(a, b, .5), b, lerp(a, b, .5)]
    for k in ATK:
        f = A.get(k)
        if not f:
            continue
        if len(f) == 2:      # wind, mid, hit, recover
            A[k] = [f[0], lerp(f[0], f[1], .5), f[1], lerp(f[1], g, .45)]
        elif len(f) == 3:    # wind, mid, hit, follow, recover
            A[k] = [f[0], lerp(f[0], f[1], .5), f[1], f[2], lerp(f[2], g, .45)]
    if len(A["jump"]) == 2:  # launch, rise, apex, fall
        a, b = A["jump"]; A["jump"] = [lerp(g, a, .6), a, lerp(a, b, .5), b]
    if len(A["throw"]) == 2:
        a, b = A["throw"]; A["throw"] = [a, lerp(a, b, .5), b]
    if len(A["grab"]) == 1:
        a = A["grab"][0]; A["grab"] = [a, dict(a, hy=a.get("hy", 0) + 1)]
    if len(A["hurt"]) == 2:
        a, b = A["hurt"]; A["hurt"] = [a, lerp(a, b, .5), b]
    return A


def _pal(body):
    pairs = {}
    for base in ("shirt", "pants", "skin", "hair_c", "sleeve", "shoe", "sock", "cuff", "top"):
        if isinstance(body.get(base), str) and isinstance(body.get(base + "_s"), str):
            pairs[body[base]] = body[base + "_s"]
    if body.get("hair_c") and body.get("hair_s"):
        pairs[body["hair_c"]] = body["hair_s"]
    return {_rgb(k): _rgb(v) for k, v in pairs.items()}


def _rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def cleanup(img, body):
    """1) selective outline: interior ink seams between two filled areas become the darker area's own shade,
    so only the silhouette keeps the hard ink line (reads crisper, less 'outlined blob');
    2) orphan pixels (one stray pixel surrounded by a single other colour) are absorbed."""
    shade = _pal(body)
    im = img.convert("RGBA"); W, H = im.size; px = im.load(); src = im.copy().load()
    ink = None
    cnt = {}
    for y in range(H):
        for x in range(W):
            c = src[x, y]
            if c[3] and sum(c[:3]) < 90:
                cnt[c] = cnt.get(c, 0) + 1
    if cnt:
        ink = max(cnt, key=cnt.get)
    solid = lambda c: c[3] > 0 and c != ink
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            c = src[x, y]
            if c != ink:
                continue
            n4 = [src[x - 1, y], src[x + 1, y], src[x, y - 1], src[x, y + 1]]
            if not all(n[3] for n in n4):
                continue  # silhouette edge: keep ink
            ring = [src[x + dx, y + dy] for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
            if any(r[3] == 0 for r in ring):
                continue
            fill = [n for n in n4 if solid(n)]
            if len(fill) < 2:
                continue
            darkest = min(fill, key=lambda n: sum(n[:3]))
            rgb = darkest[:3]
            new = shade.get(rgb, rgb)
            px[x, y] = new + (255,)
    src = im.copy().load()
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            c = src[x, y]
            if not c[3] or c == ink:
                continue
            n4 = [src[x - 1, y], src[x + 1, y], src[x, y - 1], src[x, y + 1]]
            if all(n == n4[0] for n in n4) and n4[0] != c and n4[0][3] and n4[0] != ink:
                px[x, y] = n4[0]
    return im
