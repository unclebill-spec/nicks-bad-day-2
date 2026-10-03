# Gamepad test (mocked navigator.getGamepads): menu nav, hero select, move, attack, jump, pause; then 2P: keyboard P1 + pad P2.
import time, json
from playwright.sync_api import sync_playwright
MOCK = """
(() => { const pad = { id: 'Xbox Wireless Controller (STANDARD GAMEPAD)', index: 0, connected: true, mapping: 'standard', timestamp: 0,
  axes: [0, 0, 0, 0], buttons: Array.from({ length: 17 }, () => ({ pressed: false, value: 0, touched: false })) };
  window.__pad = pad; navigator.getGamepads = () => [window.__padOn ? pad : null, null, null, null];
  window.__padSet = (i, on) => { pad.buttons[i].pressed = on; pad.buttons[i].value = on ? 1 : 0; pad.timestamp++; };
  window.__padConnect = () => { window.__padOn = true; const e = new Event('gamepadconnected'); e.gamepad = pad; dispatchEvent(e); }; })();
"""
errs = []
def tap(pg, i, hold=0.12):
    pg.evaluate(f'__padSet({i}, true)'); time.sleep(hold); pg.evaluate(f'__padSet({i}, false)'); time.sleep(0.12)
S = "JSON.stringify({sc:__nbd.game.scene, ov:!!__nbd.game.overlay, sel:__nbd.game.sel&&__nbd.game.sel.p, h:__nbd.W.heroes.map(h=>[h.id,h.st,h.x|0,h.y|0,h.devs]), input:document.documentElement.dataset.input})"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.add_init_script(MOCK)
    pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: errs.append(f'PAGEERROR: {e}'))
    pg.goto('http://localhost:8731/'); pg.wait_for_function('window.__loaded === true'); time.sleep(0.5)
    pg.evaluate('__padConnect()'); time.sleep(0.5)
    tap(pg, 0); time.sleep(0.5); print('select', pg.evaluate(S))
    tap(pg, 15); tap(pg, 15); print('cursor', pg.evaluate(S))
    tap(pg, 2); time.sleep(1.2); print('cutscene', pg.evaluate('__nbd.game.scene')); tap(pg, 0); time.sleep(3.2); print('play', pg.evaluate(S))
    x0 = pg.evaluate('__nbd.W.heroes[0].x')
    pg.evaluate('__pad.axes[0] = 1'); time.sleep(1.2); pg.evaluate('__pad.axes[0] = 0')
    x1 = pg.evaluate('__nbd.W.heroes[0].x'); print('moved', round(x1 - x0))
    tap(pg, 2, 0.05); st = pg.evaluate('__nbd.W.heroes[0].st'); print('after X:', st)
    tap(pg, 0, 0.05); st = pg.evaluate('__nbd.W.heroes[0].st'); print('after A:', st)
    time.sleep(0.8); tap(pg, 9); print('pause', pg.evaluate(S)); pg.screenshot(path='tests/out/pad_pause.png')
    tap(pg, 9); print('unpause', pg.evaluate(S))
    pg.screenshot(path='tests/out/pad_play.png')
    # 2P: keyboard P1, pad joins as P2 on the select screen
    pg.goto('http://localhost:8731/'); pg.wait_for_function('window.__loaded === true'); time.sleep(0.5)
    pg.keyboard.down('KeyS'); time.sleep(0.1); pg.keyboard.up('KeyS'); time.sleep(0.2)
    pg.keyboard.down('Enter'); time.sleep(0.1); pg.keyboard.up('Enter'); time.sleep(0.5)
    print('2p select', pg.evaluate(S))
    pg.evaluate('__padConnect()'); time.sleep(0.3); tap(pg, 2); time.sleep(0.3); print('p2 joined', pg.evaluate(S))
    tap(pg, 15); tap(pg, 2)
    pg.keyboard.down('KeyJ'); time.sleep(0.1); pg.keyboard.up('KeyJ'); time.sleep(1)
    pg.screenshot(path='tests/out/pad_2p_select.png')
    time.sleep(0.4); tap(pg, 3); time.sleep(3.2); print('2p play', pg.evaluate(S))
    pg.keyboard.down('KeyD'); pg.evaluate('__pad.axes[0] = -1; __pad.axes[1] = 1'); time.sleep(1.0); pg.keyboard.up('KeyD'); pg.evaluate('__pad.axes[0] = 0; __pad.axes[1] = 0')
    print('2p moved', pg.evaluate(S)); pg.screenshot(path='tests/out/pad_2p_play.png')
    b.close()
print('\n'.join(errs[:30]) or 'no console errors')
