"""Build every sprite sheet for Nick's Very Bad, Terrible Bad Day Part II.

    python3 tools/make_art.py      -> art/*.png + art/atlas.json

All art is drawn in code (no external images): characters on the side-view rig (tools/rig.py, built on the
Gravewake sprite writer), floor / wall speckle from the Gravewake pixel writer, potted plants from brileta-sprites.
"""
from __future__ import annotations

import base64
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
ROOT = HERE.parent
OUT = ROOT / "art"
sys.path.insert(0, str(HERE))

from rig import INK, Raster, figure  # noqa: E402
import chars  # noqa: E402
import boss  # noqa: E402
import props as PR  # noqa: E402

OUT.mkdir(exist_ok=True)
atlas = {"chars": {}, "sprites": {}}
COLS = 10


def char_sheet(name, anims, body, cell=(88, 80), anchor=(44, 76)):
    frames, meta = [], {}
    post = chars.gown_check if body.get("check") else None
    if body.get("plaid"):  # flannel: same fixed-grid check, its own colours and a wider period
        pl = body["plaid"]; post = lambda im: chars.gown_check(im, base=pl[0], check=pl[1], period=4)
    for an, poses in anims.items():
        start = len(frames)
        hands = []
        for p in poses:
            img, m = figure(body, p, W=cell[0], H=cell[1], ax=anchor[0], ay=anchor[1])
            frames.append(post(img.image()) if post else img.image())
            hands.append(m["hand"] + m["hand_b"][:2] + m["head"][:2])
        meta[an] = {"s": start, "n": len(poses), "h": hands}
    rows = (len(frames) + COLS - 1) // COLS
    sheet = Image.new("RGBA", (cell[0] * COLS, cell[1] * rows), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f, ((i % COLS) * cell[0], (i // COLS) * cell[1]))
    sheet.save(OUT / f"{name}.png", optimize=True)
    atlas["chars"][name] = {"img": f"art/{name}.png", "cell": list(cell), "anchor": list(anchor), "cols": COLS, "anims": meta}


B = chars.bodies()
for h in ("nick", "kim", "will", "jackie", "nate"):
    char_sheet(h, chars.hero_anims(h), B[h])
PATIENTS = ("wanderer", "spammer", "escape", "ivswing", "sundowner", "crutch", "bell", "elite", "runner", "tray", "o2", "barium", "apron", "lou", "yeller")
for e in PATIENTS + ("visitor",):
    big = e == "visitor"
    cell, anchor = ((96, 88), (48, 84)) if big else ((120, 104), (60, 100)) if e == "lou" else ((88, 80), (44, 76))
    char_sheet(e, chars.enemy_anims(e), B[e], cell=cell, anchor=anchor)
# runtime recolour palettes (src/gfx.js tintSheet): every patient gets random hair + skin, a green or olive gown,
# and elites get red or blue socks. Lists are [from colours..] -> the game picks matching [to colours..].
for e in PATIENTS:
    b = B[e]
    atlas["chars"][e]["pal"] = {"hair": [b["hair_c"], b["hair_s"]], "skin": [b["skin"], b["skin_s"]],
                                "gown": [chars.GOWN[0], chars.GOWN[1], *chars.GOWN_CHECK], "sock": [b["shoe"], b["shoe_s"]]}
    if e == "apron":  # v0.7.1: lab coat + brown shoes, no gown or grip socks to recolour
        atlas["chars"][e]["pal"]["gown"] = []; atlas["chars"][e]["pal"]["sock"] = []
atlas["palettes"] = {"hair": chars.HAIRS, "skin": [list(v) for v in chars.SKIN.values()],
                     "gown": [[chars.GOWN[0], chars.GOWN[1], *chars.GOWN_CHECK], list(chars.GOWN_OLIVE)],
                     "sock": [list(chars.SOCK)], "sock_elite": [list(chars.SOCK_ELITE), ["#4a7ae8", "#2a4aa8"]]}

# ---- boss
fr, meta = [], {}
for an, (st, n) in boss.ANIMS.items():
    meta[an] = {"s": len(fr), "n": n, "h": []}
    for k in range(n):
        fr.append(boss.frame(st, k).image())
cols = 6
sheet = Image.new("RGBA", (boss.W * cols, boss.H * ((len(fr) + cols - 1) // cols)), (0, 0, 0, 0))
for i, f in enumerate(fr):
    sheet.paste(f, ((i % cols) * boss.W, (i // cols) * boss.H))
sheet.save(OUT / "tilly.png", optimize=True)
atlas["chars"]["tilly"] = {"img": "art/tilly.png", "cell": [boss.W, boss.H], "anchor": [boss.AX, boss.AY], "cols": cols, "anims": meta}
# ---- v0.5 MRI magnet boss (MAGNA-SCAN 3000)
import radiology as RA  # noqa: E402
fr, meta = [], {}
for an, (st, n) in RA.MRI_ANIMS.items():
    meta[an] = {"s": len(fr), "n": n, "h": []}
    for k in range(n):
        fr.append(RA.mri_frame(st, k).image())
sheet = Image.new("RGBA", (RA.MW * 4, RA.MH * ((len(fr) + 3) // 4)), (0, 0, 0, 0))
for i, f in enumerate(fr):
    sheet.paste(f, ((i % 4) * RA.MW, (i // 4) * RA.MH))
sheet.save(OUT / "mri.png", optimize=True)
atlas["chars"]["mri"] = {"img": "art/mri.png", "cell": [RA.MW, RA.MH], "anchor": [RA.MAX, RA.MAY], "cols": 4, "anims": meta}

# ---- brileta potted plants (MIT, vendored): small sapling / deciduous crowns snapped to a 1-bit alpha and a short palette
def brileta(reqs):
    js = HERE / "vendor" / "brileta" / "dump.mjs"
    try:
        out = subprocess.run(["node", str(js), json.dumps(reqs)], capture_output=True, text=True, check=True).stdout
        return json.loads(out)
    except Exception as e:  # node missing: fall back to a hand-drawn fern
        print("brileta unavailable:", e)
        return []


PLANT_PAL = ["#1e4a2a", "#2e6a34", "#3e8a3e", "#5aaa48", "#7ac85a", "#5a3a20", "#7a5a30"]


def snap(c):
    r, g, b = c
    best = min(PLANT_PAL, key=lambda h: (int(h[1:3], 16) - r) ** 2 + (int(h[3:5], 16) - g) ** 2 + (int(h[5:7], 16) - b) ** 2)
    return best


plants = []
for i, t in enumerate(brileta([{"kind": "tree", "seed": 11 + i * 7, "size": 22, "arch": "deciduous"} for i in range(3)])):
    raw = base64.b64decode(t["data"])
    w, h = t["w"], t["h"]
    S = Raster(w + 4, h + 14)
    for y in range(h):
        for x in range(w):
            r, g, b, a = raw[(y * w + x) * 4:(y * w + x) * 4 + 4]
            if a >= 128:
                S.set(x + 2, y, snap((r, g, b)))
    S.outline(INK)
    px = (w + 4) // 2
    PR.box(S, px - 6, h - 1, 12, 12, "#c86a3a", "#9a4a24", "#e88a5a")
    S.rect(px - 7, h - 2, 14, 2, "#9a4a24")
    plants.append(S)

# ---- sprite atlas (shelf packer)
SPR = {}
def add(name, S):
    SPR[name] = S.image() if hasattr(S, "image") else S

for i in range(4):
    add(f"wall{i}", PR.wall_tile(i))
add("ceil", PR.ceiling_tile(False)); add("ceil_lit", PR.ceiling_tile(True))
for i, t in enumerate(PR.floor_tiles()):
    add(f"floor{i}", t)
for i, d in enumerate(PR.door_frames()):
    add(f"door{i}", d)
add("elevator", PR.elevator_frame()); add("elev_door", PR.elevator_door()); add("callpanel", PR.call_panel()); add("callpanel_lit", PR.call_panel_lit())
add("station", PR.nurses_station())
for i in range(3):
    add(f"window{i}", PR.window_city(i + 1))
for k in ("hands", "bingo", "duck", "quiet", "board", "clock", "sanitizer", "alarm", "tv"):
    add(f"poster_{k}", PR.poster(k))
add("sign_elev", PR.sign("ELEVATORS >")); add("sign_dayroom", PR.sign("DAYROOM", "#7a3ab8")); add("sign_medsurg", PR.sign("3 WEST  MED-SURG"))
add("sign_exit", PR.sign("EXIT", "#c82a2a")); add("sign_lounge", PR.sign("FAMILY LOUNGE", "#2a8a5a")); add("sign_rooms1", PR.sign("301-309 >"))
add("floornum3", PR.floor_number(3))
add("chairs", PR.chairs()); add("wheelchair", PR.wheelchair_empty()); add("gurney", PR.gurney()); add("fountain", PR.water_fountain())
for i, p in enumerate(plants):
    add(f"plant{i}", p)
for st in range(3):
    add(f"medcart{st}", PR.med_cart(st)); add(f"linen{st}", PR.linen_bin(st)); add(f"vending{st}", PR.vending(st))
for st in range(2):
    add(f"ivstand{st}", PR.iv_stand(st))
# v0.3 kickable / breakable floor props + debris bits
import breakables as BR  # noqa: E402
for st in range(3):
    add(f"crashcart{st}", BR.crash_cart(st)); add(f"supplycart{st}", BR.supply_cart(st)); add(f"chair{st}", BR.chair(st))
    add(f"trash{st}", BR.trash_can(st)); add(f"wheelchair{st}", BR.wheelchair(st))
for st in range(2):
    add(f"wetfloor{st}", BR.wet_floor(st))
add("potplant0", plants[1]); add("potplant1", BR.crack_pot(SPR["plant1"])); add("potplant2", BR.plant_wreck())
for k, S in BR.bits().items():
    add(k, S)
# v0.4: gurney, loose O2 tank, tray/jello projectiles, breakroom pieces
for st in range(3):
    add(f"gurneyp{st}", BR.gurney(st)); add(f"o2tank{st}", BR.o2_tank(st))
add("p_tray", BR.proj_tray()); add("p_jello", BR.proj_jello()); add("puddle_g", BR.jello_splat())
add("fridge", BR.fridge()); add("fridge_open", BR.fridge(True)); add("counter", BR.counter()); add("cabinets", BR.cabinets()); add("btable", BR.table())
add("note_food", BR.food_note()); add("sign_breakroom", PR.sign("BREAKROOM", "#c86a1a")); add("vend_wall", PR.vending(0))
# v0.5 Floor 4 Radiology + the night shift
for i in range(4):
    add(f"rwall{i}", RA.rwall_tile(i))
add("rceil", RA.rceil_tile(False)); add("rceil_lit", RA.rceil_tile(True))
for i, t in enumerate(RA.rfloor_tiles()):
    add(f"rfloor{i}", t)
for i, ks in enumerate((("chest", "hand"), ("skull", "chest"), ("hand", "duck"), ("chest", "skull"))):
    add(f"lightbox{i}", RA.lightbox(ks, i + 1))
add("warnlamp", RA.warn_lamp(True)); add("warnlamp_off", RA.warn_lamp(False)); add("trefoil", RA.trefoil()); add("poster_nometal", RA.poster_nometal())
add("sign_radiology", PR.sign("4 RADIOLOGY", "#2a5ad8")); add("sign_mri", PR.sign("MRI SUITE: NO METAL!", "#7a3ab8")); add("sign_xray", PR.sign("X-RAY  CT  ULTRASOUND >", "#1a6a9a"))
add("sign_imaging", PR.sign("IMAGING WAITING", "#2a8a7a")); add("floornum4", PR.floor_number(4))
for i in range(3):
    add(f"nwindow{i}", RA.night_window(i + 1))
add("calllamp", RA.call_lamp(True)); add("calllamp_off", RA.call_lamp(False)); add("monitor", RA.vitals_monitor())
for st in range(3):
    add(f"apronrack{st}", RA.apron_rack(st)); add(f"contrastcart{st}", RA.contrast_cart(st)); add(f"viewer{st}", RA.film_viewer(st))
for k, S in RA.rbits().items():
    add(k, S)
import v06_art as V6  # noqa: E402  (v0.6: old pizza, BEEF JERKY bag (v0.7), Ativan syringe, zap skeleton, fire-alarm pull station)
add("pizza", V6.pizza()); add("jerky", V6.jerky()); add("ativan", V6.ativan()); add("skel", V6.skeleton())
add("firealarm0", V6.firealarm(False)); add("firealarm1", V6.firealarm(True))
import v08_art as V8  # noqa: E402  (v0.8: Nasty Nate's rolling office chair)
add("chair0", V8.office_chair(0)); add("chair1", V8.office_chair(1))
add("p_cup", RA.proj_cup()); add("puddle_w", RA.barium_splat()); add("p_film", RA.proj_film()); add("mri_wave0", RA.mri_wave(0)); add("mri_wave1", RA.mri_wave(1)); add("mri_table", RA.mri_table())
for k, f in (("energy", PR.energy_drink), ("snacks", PR.fruit_snacks), ("zynn", PR.zynn_tin), ("candy", PR.candy), ("star", PR.star), ("donut", PR.donut),
             ("w_crutch", PR.w_crutch), ("w_callbell", PR.w_callbell), ("w_cane", PR.w_cane), ("syringe", PR.syringe), ("urinal", PR.urinal), ("puddle_y", PR.puddle_y),
             ("w_clipboard", PR.w_clipboard), ("w_bedpan", PR.w_bedpan), ("w_mop", PR.w_mop), ("w_extinguisher", PR.w_extinguisher),
             ("w_ivpole", PR.w_ivpole), ("remote", PR.remote), ("pudding", PR.pudding), ("wetsign", PR.wet_sign), ("puddle", PR.puddle),
             ("shadow", PR.shadow), ("zzz", PR.zzz), ("heart", PR.heart)):
    add(k, f())
add("yarn0", PR.yarn("#ff6ab0")); add("yarn1", PR.yarn("#7ad8ff"))
for i in range(3):
    add(f"spark{i}", PR.spark(16, i)); add(f"bigspark{i}", PR.spark(28, i, "#ffe84a")); add(f"bluespark{i}", PR.spark(20, i, "#8ad8ff", "#ffffff"))
    add(f"smoke{i}", PR.smoke(i)); add(f"dizzy{i}", PR.dizzy(i))
for i in range(4):
    add(f"dust{i}", PR.dust(i))
for i in range(3):
    add(f"splash{i}", PR.splash(i))

# ---- comic words + logo (Luckiest Guy, Apache-2.0) quantised to hard pixels
LG = ROOT / "fonts" / "LuckiestGuy-Regular.ttf"
PS = ROOT / "fonts" / "PressStart2P-Regular.ttf"


def word(text, size, fill, fill2, ink="#1a1020", stroke=2, shadow=True):
    f = ImageFont.truetype(str(LG), size)
    bb = f.getbbox(text)
    w, h = bb[2] - bb[0] + stroke * 2 + 4, bb[3] - bb[1] + stroke * 2 + 5
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    d.fontmode = "1"
    d.text((stroke + 2 - bb[0], stroke + 2 - bb[1]), text, font=f, fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px, mp = out.load(), m.load()
    def hx(c):
        return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
    for y in range(h):
        for x in range(w):
            if mp[x, y] > 127:
                t = y / h
                px[x, y] = hx(fill if t < 0.55 else fill2)
    # stroke
    src = out.copy(); sp = src.load()
    for y in range(h):
        for x in range(w):
            if sp[x, y][3]:
                continue
            if any(0 <= x + dx < w and 0 <= y + dy < h and sp[x + dx, y + dy][3] for dx in range(-stroke, stroke + 1) for dy in range(-stroke, stroke + 1)
                   if abs(dx) + abs(dy) <= stroke + 0):
                px[x, y] = hx(ink)
    if shadow:
        sh = Image.new("RGBA", (w + 2, h + 2), (0, 0, 0, 0))
        dark = Image.new("RGBA", out.size, hx(ink))
        sh.paste(dark, (2, 2), out)
        sh.alpha_composite(out, (0, 0))
        out = sh
    return out


for k, t, c1, c2 in (("w_pow", "POW!", "#ffe84a", "#ff9a1e"), ("w_wham", "WHAM!", "#ff8ac0", "#e83a6a"), ("w_bonk", "BONK!", "#8ae8ff", "#3aa0e8"),
                     ("w_clang", "CLANG!", "#e4e8f0", "#9aa4b4"), ("w_smack", "SMACK!", "#ffe84a", "#ff5a3a"), ("w_clear", "CLEAR!", "#8ad8ff", "#3a7aff"),
                     ("w_honk", "HONK!", "#ffe84a", "#ff8a1e"), ("w_go", "GO!", "#ffe84a", "#ff9a1e"), ("w_ko", "K.O.!", "#ffffff", "#ffd84a"),
                     ("w_turbo", "TURBO!", "#8ad8ff", "#a24dff"), ("w_slam", "SLAM!", "#ffe84a", "#ff5a3a"),
                     ("w_sploosh", "SPLOOSH!", "#fff27a", "#e8c82a"), ("w_ding", "DING!", "#ffffff", "#c8d0dc"), ("w_poke", "POKE!", "#8ae8ff", "#3aa0e8")):
    SPR[k] = word(t, 16, c1, c2)
SPR["w_codeblue"] = word("CODE BLUE!", 26, "#9ae0ff", "#3a6aff", stroke=3)
SPR["w_charge"] = word("CHARGE NURSE!", 28, "#ffffff", "#ffd84a", stroke=3)
SPR["w_bonus"] = word("BREAKROOM BONUS!", 22, "#ffe84a", "#ff8a1e", stroke=3)
SPR["w_stopped"] = word("STOPPED!", 16, "#8ae87a", "#3aa860")
SPR["w_crash"] = word("CRASH!", 18, "#ffe84a", "#ff5a3a")
SPR["w_beep"] = word("BEEP!", 14, "#ff8a8a", "#e83a3a")
SPR["w_splat"] = word("SPLAT!", 16, "#aaff8a", "#3aa83a")
SPR["w_caught"] = word("CAUGHT!", 18, "#ffe84a", "#ff8a1e")
# v0.5 words
SPR["w_magnet"] = word("MAGNET ON!", 22, "#bfeaff", "#3aa8ff", stroke=3)
SPR["w_quench"] = word("QUENCH!", 22, "#ffffff", "#8ad8ff", stroke=3)
SPR["w_knock"] = word("KNOCK!", 16, "#ffffff", "#bfeaff")
SPR["w_clunk"] = word("CLUNK!", 16, "#e4e8f0", "#9aa4b4")
SPR["w_hike"] = word("HIKE!", 22, "#ffe84a", "#ff8a1e", stroke=3)
SPR["w_lightsout"] = word("LIGHTS OUT!", 26, "#bfeaff", "#3a68c8", stroke=3)
SPR["w_power"] = word("POWER'S BACK!", 24, "#ffe84a", "#ff8a1e", stroke=3)
SPR["w_superc"] = word("SUPERCONDUCTING!", 20, "#e8c8ff", "#a24dff", stroke=3)
SPR["w_theend"] = word("THE END", 40, "#ffe84a", "#ff8a1e", stroke=3)
SPR["w_timeup"] = word("TIME UP!", 30, "#ff8ac0", "#e83a6a", stroke=3)
SPR["w_ready"] = word("CLOCK IN!", 30, "#ffe84a", "#ff8a1e", stroke=3)
SPR["w_clear_stage"] = word("FLOOR CLEARED!", 26, "#ffe84a", "#ff8a1e", stroke=3)
SPR["w_gameover"] = word("SHIFT OVER", 30, "#ff8ac0", "#e83a6a", stroke=3)
SPR["logo1"] = word("NICK'S VERY BAD,", 28, "#ffffff", "#c8e4ff", stroke=3)
SPR["logo2"] = word("TERRIBLE BAD DAY", 34, "#ffe84a", "#ff8a1e", stroke=3)
SPR["logo3"] = word("PART II", 26, "#8ad8ff", "#3a7aff", stroke=3)

# ---- HUD portraits: the same bodies at 2x detail, head crop
def portrait(body, pose_face="norm", k=2):
    big = {n: (v * k if isinstance(v, (int, float)) and not isinstance(v, bool) and n not in ("belly",) else v) for n, v in body.items()}
    big["belly"] = body.get("belly", 0) * k if body.get("belly") else 0
    from rig import P
    img, m = figure(big, P(lean=0, head=0, face=pose_face, ua_f=-5, fa_f=-5, ua_b=5, fa_b=5), W=176, H=170, ax=88, ay=166)
    hx = 88 + m["head"][0]
    im = img.image()
    top = min(y for y in range(im.height) if any(im.getpixel((x, y))[3] for x in range(im.width)))
    return im.crop((int(hx - 18), top - 2, int(hx - 18) + 36, top + 34))


for h in ("nick", "kim", "will", "jackie", "nate"):
    SPR[f"face_{h}"] = portrait(B[h])
    SPR[f"face_{h}_hurt"] = portrait(B[h], "hurt")
SPR["face_tilly"] = portrait(boss.tilly_body(), "grin")
SPR["face_lou"] = portrait(B["lou"], "grin", k=1.4)  # v0.7.1: Lou himself (bigger head, so drawn at 1.4x not 2x)

# ---- bitmap font (Press Start 2P, OFL) 8x8, ASCII 32..126, 16 per row
f = ImageFont.truetype(str(PS), 8)
font = Image.new("RGBA", (16 * 8, 6 * 8), (0, 0, 0, 0))
d = ImageDraw.Draw(font)
d.fontmode = "1"
for i in range(95):
    d.text(((i % 16) * 8, (i // 16) * 8), chr(32 + i), font=f, fill=(255, 255, 255, 255))
font.save(OUT / "font8.png")

# pack
items = sorted(SPR.items(), key=lambda kv: -kv[1].height)
W = 512
x = y = rowh = 0
pos = {}
for k, im in items:
    if x + im.width > W:
        x, y, rowh = 0, y + rowh + 1, 0
    pos[k] = (x, y, im.width, im.height)
    x += im.width + 1
    rowh = max(rowh, im.height)
sheet = Image.new("RGBA", (W, y + rowh + 1), (0, 0, 0, 0))
for k, im in items:
    p = pos[k]
    sheet.paste(im, (p[0], p[1]))
sheet.save(OUT / "sprites.png", optimize=True)
atlas["sprites"] = {"img": "art/sprites.png", "rects": pos}
(OUT / "atlas.json").write_text(json.dumps(atlas, separators=(",", ":")))

# ---- app icons: Nick's portrait on navy with the "II"
for size in (192, 512, 180):
    ic = Image.new("RGBA", (size, size), (26, 36, 80, 255))
    dd = ImageDraw.Draw(ic)
    dd.rectangle([0, int(size * 0.78), size, size], fill=(255, 138, 30, 255))
    face = SPR["face_nick"].resize((int(size * 0.8), int(size * 0.8)), Image.NEAREST)
    ic.alpha_composite(face, (int(size * 0.1), int(size * 0.02)))
    tag = word("II", 30, "#ffe84a", "#ff8a1e", stroke=3)
    tag = tag.resize((int(tag.width * size / 128), int(tag.height * size / 128)), Image.NEAREST)
    ic.alpha_composite(tag, (size - tag.width - int(size * 0.04), size - tag.height - int(size * 0.02)))
    name = "apple-touch-icon.png" if size == 180 else f"icon-{size}.png"
    ic.convert("RGB").save(ROOT / "icons" / name)
print("sheets:", sorted(p.name for p in OUT.glob("*.png")), "sprites", sheet.size, len(pos))
