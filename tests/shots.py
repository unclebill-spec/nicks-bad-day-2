# Bot-driven run of a zone; snapshots every N seconds. usage: shots.py <query> <secs> <prefix> [w h]
import sys, time
from playwright.sync_api import sync_playwright
q, secs, pre = sys.argv[1], float(sys.argv[2]), sys.argv[3]
w, h = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (1280, 720)
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': w, 'height': h})
    pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: errs.append(f'PAGEERROR: {e}'))
    pg.goto('http://localhost:8731/?' + q); pg.wait_for_function('window.__loaded === true', timeout=30000)
    t0 = time.time(); i = 0
    while time.time() - t0 < secs:
        time.sleep(float(sys.argv[6]) if len(sys.argv) > 6 else 2.0)
        pg.screenshot(path=f'tests/out/{pre}_{i:02d}.png'); i += 1
        print(pg.evaluate("JSON.stringify({sc:__nbd.game.scene, z:__nbd.W.zone, w:__nbd.W.wave, cam:Math.round(__nbd.W.camX), lock:__nbd.W.lockX, h:__nbd.W.heroes.map(h=>[h.st,Math.round(h.x),Math.round(h.y),h.hp,h.lives]), e:__nbd.W.enemies.map(e=>[e.kind,e.st,Math.round(e.x),Math.round(e.y)]), b:__nbd.W.boss&&[__nbd.W.boss.st,__nbd.W.boss.hp,__nbd.W.boss.phase]})"))
    b.close()
print('\n'.join(errs[:30]) or 'no console errors')
