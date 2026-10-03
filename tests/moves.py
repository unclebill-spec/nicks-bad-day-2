# Per-hero move check (keyboard): jump, jump-kick, run+dash attack, special (costs HP), Code Blue super, pickups/weapon.
import time
from playwright.sync_api import sync_playwright
errs = []
def key(pg, k, hold=0.08): pg.keyboard.down(k); time.sleep(hold); pg.keyboard.up(k)
st = lambda pg: pg.evaluate('__nbd.W.heroes[0].st')
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: errs.append(f'PAGEERROR: {e}'))
    for hero in ['nick', 'kim', 'will', 'jackie']:
        pg.goto(f'http://localhost:8731/?autostart=1&hero={hero}'); pg.wait_for_function('window.__loaded === true'); time.sleep(3.2)
        r = {'hero': pg.evaluate('__nbd.W.heroes[0].id')}
        key(pg, 'KeyK'); time.sleep(0.12); r['jump'] = st(pg); key(pg, 'KeyJ'); time.sleep(0.05); r['jkick'] = st(pg); time.sleep(1)
        hp0 = pg.evaluate('__nbd.W.heroes[0].hp'); key(pg, 'KeyL'); time.sleep(0.1); r['special'] = st(pg); time.sleep(1.4)
        r['spCost'] = hp0 - pg.evaluate('__nbd.W.heroes[0].hp')
        pg.evaluate('__nbd.W.heroes[0].meter = 100'); key(pg, 'KeyL'); time.sleep(0.15); r['super'] = st(pg); time.sleep(2.5)
        pg.keyboard.down('ShiftLeft'); pg.keyboard.down('KeyD'); time.sleep(0.4); r['run'] = st(pg); key(pg, 'KeyJ'); time.sleep(0.05); r['dash'] = st(pg)
        pg.keyboard.up('KeyD'); pg.keyboard.up('ShiftLeft'); time.sleep(1)
        # drop a weapon at her feet and pick it up, then swing
        pg.evaluate("__nbd.drop('w:extinguisher' if False else 'w:mop')".replace("'w:extinguisher' if False else ", ''))
        time.sleep(0.1); key(pg, 'KeyH'); time.sleep(0.5); r['weapon'] = pg.evaluate('__nbd.W.heroes[0].weapon && __nbd.W.heroes[0].weapon.k'); key(pg, 'KeyJ'); time.sleep(0.05); r['swing'] = st(pg)
        print(r)
    pg.screenshot(path='tests/out/m_last.png')
    b.close()
print('\n'.join(errs[:30]) or 'no console errors')
