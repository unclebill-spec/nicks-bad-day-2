# Records the v0.3 breakables clip for docs/props.gif: Nick kicks a crash cart into a line of patients, it bounces off
# the screen edge, he smashes it apart, then boots a trash can, a wet-floor sign and a plant. Usage:
#   python3 tests/props_video.py [base_url]   -> tests/out/vid/props.webm
import time, os, shutil, sys
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8731/'
os.makedirs('tests/out/vid', exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 960, 'height': 540}, record_video_dir='tests/out/vid', record_video_size={'width': 960, 'height': 540})
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(U + '?autostart=1&hero=nick&god=1'); pg.wait_for_function('window.__loaded === true', timeout=30000)
    pg.wait_for_function("__nbd.game.scene==='play' && __nbd.W.heroes.length && __nbd.W.heroes[0].st==='idle'", timeout=30000)
    pg.evaluate("""(()=>{const W=__nbd.W; __nbd.Director.update=()=>{}; W.enemies.length=0; W.lockX=0; W.camX=0; W.rnd=(()=>{let s=7;return()=>(s=(s*16807)%2147483647)/2147483647;})();
      const h=W.heroes[0]; h.x=150; h.y=150; h.face=1;
      for (const [x,y] of [[300,150],[330,156],[362,146]]) { __nbd.spawn('wanderer','R'); const e=W.enemies[W.enemies.length-1]; e.x=x; e.y=y; e.st='idle'; e.cd=99; e.d={...e.d, speed:8}; e.hp=12; }
    })()""")
    T0 = time.time()
    def hx(): return pg.evaluate("[__nbd.W.heroes[0].x, __nbd.W.heroes[0].y]")
    def walk_to(x, y, tmax=2.0):
        t = time.time()
        while time.time() - t < tmax:
            cx, cy = hx(); kx = 'KeyD' if x > cx + 3 else 'KeyA' if x < cx - 3 else None; ky = 'KeyS' if y > cy + 3 else 'KeyW' if y < cy - 3 else None
            for k in ('KeyA', 'KeyD', 'KeyW', 'KeyS'):
                (pg.keyboard.down if k in (kx, ky) else pg.keyboard.up)(k)
            if not kx and not ky: break
            time.sleep(0.03)
        for k in ('KeyA', 'KeyD', 'KeyW', 'KeyS'): pg.keyboard.up(k)
    def face(d): k = 'KeyD' if d > 0 else 'KeyA'; pg.keyboard.down(k); time.sleep(0.04); pg.keyboard.up(k)
    def hit(n=1, gap=0.17):
        for i in range(n): pg.keyboard.down('KeyJ'); time.sleep(0.05); pg.keyboard.up('KeyJ'); time.sleep(gap)
    def jkick():
        pg.keyboard.down('KeyK'); time.sleep(0.06); pg.keyboard.up('KeyK'); time.sleep(0.12); hit(1, 0.5)
    P = lambda k: pg.evaluate(f"(()=>{{const p=__nbd.W.props.find(p=>p.kind==='{k}' && p.x<420); return p?[p.x,p.y,p.st]:null}})()")
    time.sleep(0.6)
    # 1) jump-kick the crash cart into the patients
    cx, cy, _ = P('crashcart'); walk_to(cx - 26, cy); face(1); time.sleep(0.15); jkick(); time.sleep(1.6)
    # 2) it bounced back: meet it and smash it apart
    for i in range(4):
        cx, cy, st = P('crashcart')
        if st >= 2: break
        walk_to(cx - 24, cy, 1.2); face(1); hit(4, 0.22); time.sleep(0.35)
    time.sleep(0.9)
    # 3) boot the trash can, the wet-floor sign and the plant
    for k in ('trash', 'wetfloor', 'plant'):
        q = P(k)
        if not q or q[2] >= 2: continue
        walk_to(q[0] - 24, q[1], 1.6); face(1)
        if k == 'trash': jkick(); time.sleep(0.5)   # boot it across the floor first
        for t in range(3):
            q = P(k)
            if not q or q[2] >= 2: break
            walk_to(q[0] - 22, q[1], 1.2); face(1); hit(2, 0.22)
        time.sleep(0.3)
    time.sleep(1.4)
    pg.screenshot(path='tests/out/props_video_end.png')
    path = pg.video.path(); ctx.close(); shutil.move(path, 'tests/out/vid/props.webm'); b.close()
    print('clip secs', round(time.time() - T0, 1), 'errors', errs)
