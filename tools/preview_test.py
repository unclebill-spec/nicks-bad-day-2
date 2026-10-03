import sys; sys.path.insert(0, '.')
from PIL import Image
from rig import figure
from chars import bodies, hero_anims, enemy_anims
B = bodies()
rows = []
names = sys.argv[1:] or ["nick", "kim", "will", "jackie"]
for n in names:
    A = hero_anims(n) if n in ("nick", "kim", "will", "jackie") else enemy_anims(n)
    frames = []
    for k, fs in A.items():
        for f in fs:
            frames.append(figure(B[n], f)[0].image())
    rows.append(frames)
W = max(len(r) for r in rows)
im = Image.new("RGBA", (W * 88, len(rows) * 80), (200, 200, 210, 255))
for j, r in enumerate(rows):
    for i, f in enumerate(r):
        im.alpha_composite(f, (i * 88, j * 80))
im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
im.save('/workspace/games/nicks-bad-day-2/tests/out_preview.png')
print(im.size)
