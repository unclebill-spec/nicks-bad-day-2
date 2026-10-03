# Will's look check: title, hero select (cursor on Will), in-game + HUD portrait, floor-cleared tally portrait.
import time
from playwright.sync_api import sync_playwright
errs = []
def key(pg, k): pg.keyboard.down(k); time.sleep(0.1); pg.keyboard.up(k); time.sleep(0.15)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: errs.append(f'PAGEERROR: {e}'))
    pg.goto('http://localhost:8731/'); pg.wait_for_function('window.__loaded === true'); time.sleep(1)
    pg.screenshot(path='tests/out/w_title.png')
    key(pg, 'Enter'); time.sleep(0.4); key(pg, 'KeyD'); key(pg, 'KeyD'); time.sleep(0.3)
    print('cursor on', pg.evaluate("__nbd.game.sel.p[0].cur"), '(2 = Will)')
    pg.screenshot(path='tests/out/w_select.png')
    key(pg, 'KeyJ'); time.sleep(1.2); key(pg, 'KeyK'); time.sleep(3.3)  # skip the v0.4 cutscene
    print('playing as', pg.evaluate("__nbd.W.heroes[0].id"), pg.evaluate("__nbd.W.heroes[0].sheet"))
    pg.keyboard.down('KeyD'); time.sleep(1.2); pg.keyboard.up('KeyD'); key(pg, 'KeyJ'); key(pg, 'KeyJ')
    pg.screenshot(path='tests/out/w_game.png')
    pg.goto('http://localhost:8731/?zone=5&bot=1&god=1&hero=will'); pg.wait_for_function('window.__loaded === true'); time.sleep(4)
    pg.evaluate('__nbd.W.boss.hp = 3; __nbd.W.boss.phase = 2')
    pg.wait_for_function("__nbd.game.scene === 'tally'", timeout=40000); time.sleep(3.5)
    pg.screenshot(path='tests/out/w_tally.png')
    b.close()
print('\n'.join(errs[:20]) or 'no console errors')
