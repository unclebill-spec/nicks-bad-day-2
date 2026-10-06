# quick viewer: python3 pv.py name [anim,anim] -> tests/pv.png (3x)
import sys; sys.path.insert(0, '.')
from PIL import Image
from rig import figure
from chars import bodies, hero_anims, enemy_anims
B = bodies()
names = sys.argv[1].split(',')
only = sys.argv[2].split(',') if len(sys.argv) > 2 else None
rows = []
for n in names:
    A = hero_anims(n) if n in ("nick", "kim", "will", "jackie", "nate", "heather") else enemy_anims(n)
    fr = [figure(B[n], f)[0].image() for k, fs in A.items() if not only or k in only for f in fs]
    rows.append(fr)
W = max(len(r) for r in rows)
im = Image.new("RGBA", (W * 88, len(rows) * 80), (190, 196, 206, 255))
for j, r in enumerate(rows):
    for i, f in enumerate(r):
        im.alpha_composite(f, (i * 88, j * 80))
sc = int(sys.argv[3]) if len(sys.argv) > 3 else 3
im = im.resize((im.width * sc, im.height * sc), Image.NEAREST)
import time; fn='/workspace/games/nicks-bad-day-2/tests/pv_%d.png' % int(time.time()*10); im.save(fn); print(fn)
