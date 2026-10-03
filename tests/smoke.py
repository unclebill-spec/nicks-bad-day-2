# Desktop smoke test: load, title, select, play a bit, screenshot; prints console errors.
import sys, time, json
from playwright.sync_api import sync_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8731/'
out = 'tests/out'
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required', '--use-gl=swiftshader', '--enable-unsafe-swiftshader'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: errs.append(f'PAGEERROR: {e}'))
    pg.goto(URL); pg.wait_for_function('window.__loaded === true', timeout=30000)
    time.sleep(1); pg.screenshot(path=f'{out}/s_title.png')
    pg.keyboard.press('Enter'); time.sleep(0.6); pg.screenshot(path=f'{out}/s_select.png')
    pg.keyboard.press('KeyD'); time.sleep(0.2); pg.keyboard.press('KeyJ'); time.sleep(2.0)
    pg.screenshot(path=f'{out}/s_cutscene.png'); print('cutscene:', pg.evaluate('__nbd.game.scene'))
    pg.keyboard.press('KeyK'); time.sleep(1.2)  # v0.4: any button skips the shift-change cutscene
    pg.screenshot(path=f'{out}/s_intro.png')
    time.sleep(2.0)
    pg.keyboard.down('KeyD'); time.sleep(2.5); pg.keyboard.up('KeyD')
    for i in range(14): pg.keyboard.press('KeyJ'); time.sleep(0.12)
    pg.screenshot(path=f'{out}/s_play.png')
    print(pg.evaluate('JSON.stringify({scene: __nbd.game.scene, heroes: __nbd.W.heroes.map(h=>[h.id,h.st,Math.round(h.x),Math.round(h.y),h.hp]), en: __nbd.W.enemies.length, cam: __nbd.W.camX, zone: __nbd.W.zone, VW: __nbd.G.VW, k: __nbd.G.k})'))
    b.close()
print('\n'.join(errs[:30]) or 'no console errors')
