# Before/after art sheet: patients (idle + attack frame) and nurse drops. usage: before_after.py <before_dir> <out.png>
import json, sys
from PIL import Image, ImageDraw, ImageFont
BEF, OUT = sys.argv[1], sys.argv[2]
F = ImageFont.truetype('fonts/PressStart2P-Regular.ttf', 8)
def frames(d, name, anims=('idle', 'atk')):
    A = json.load(open(f'{d}/atlas.json')); c = A['chars'].get(name)
    if not c: return []
    im = Image.open(f'{d}/{name}.png'); cw, ch = c['cell']; out = []
    for a in anims:
        if a not in c['anims']: continue
        m = c['anims'][a]; i = m['s'] + (m['n'] - 1 if a != 'idle' else 0)
        out.append(im.crop(((i % c['cols']) * cw, (i // c['cols']) * ch, (i % c['cols'] + 1) * cw, (i // c['cols'] + 1) * ch)))
    return out
def sprite(d, n):
    A = json.load(open(f'{d}/atlas.json')); r = A['sprites']['rects'].get(n)
    return Image.open(f'{d}/sprites.png').crop((r[0], r[1], r[0] + r[2], r[1] + r[3])) if r else None
before = ['wanderer', 'wanderer2', 'spammer', 'escape', 'escape2', 'ivswing', 'sundowner']
after = ['wanderer', 'spammer', 'escape', 'ivswing', 'sundowner', 'crutch', 'bell', 'elite']
cell = 88
W = cell * 2 * max(len(before), len(after)) // 2 + 40
rowsH = 18 + 80
img = Image.new('RGBA', (cell * 16 + 20, 18 + 2 * (rowsH * 2) + 70), (196, 202, 212, 255)); d = ImageDraw.Draw(img)
def row(y, names, src, label):
    d.text((6, y), label, fill=(26, 36, 80), font=F); x = 6; y += 12
    for n in names:
        fr = frames(src, n)
        for f in fr: img.alpha_composite(f, (x, y)); x += 70
        d.text((x - 70 * len(fr) + 4, y + 80), n.upper()[:10], fill=(26, 36, 80), font=F); x += 6
    return y + 96
y = 6
y = row(y, before[:4], BEF, 'BEFORE (v0.1)'); y = row(y, before[4:], BEF, '')
y = row(y, after[:4], 'art', 'AFTER (v0.2): checked gowns, yellow grip socks, crutch / call bell / elite with cane'); y = row(y, after[4:], 'art', '')
d.text((6, y), 'DROPS  before: coffee, pizza, 2X token   after: energy drink, fruit snacks, ZYNN tin  + new weapons/projectiles', fill=(26, 36, 80), font=F); y += 14
x = 6
for n in ['coffee', 'pizza', 'token']:
    s = sprite(BEF, n); s = s.resize((s.width * 2, s.height * 2), Image.NEAREST); img.alpha_composite(s, (x, y)); x += s.width + 10
x += 40
for n in ['energy', 'snacks', 'zynn', 'w_crutch', 'w_callbell', 'w_cane', 'syringe', 'urinal', 'splash1']:
    s = sprite('art', n); s = s.resize((s.width * 2, s.height * 2), Image.NEAREST); img.alpha_composite(s, (x, y)); x += s.width + 10
img = img.crop((0, 0, img.width, y + 50))
img.resize((img.width * 2, img.height * 2), Image.NEAREST).save(OUT)
print(img.size)
