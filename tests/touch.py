# Phone landscape (emulated Pixel 7 / iPhone 14 sizes) with real touch events via CDP: menu taps, card double-tap,
# floating joystick + action buttons, pause button. Screenshots for the sheet.
import time, sys
from playwright.sync_api import sync_playwright
W, H = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (915, 412)
UA = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36'
errs = []
S = "JSON.stringify({sc:__nbd.game.scene, ov:!!__nbd.game.overlay, VW:__nbd.G.VW, VH:__nbd.G.VH, k:__nbd.G.k, h:__nbd.W.heroes.map(h=>[h.id,h.st,h.x|0,h.y|0]), input:document.documentElement.dataset.input, scene:document.documentElement.dataset.scene})"
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2.6, is_mobile=True, has_touch=True, user_agent=UA)
    pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg)
    pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: errs.append(f'PAGEERROR: {e}'))
    def touch(kind, pts): cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [{'x': x, 'y': y, 'id': i} for i, x, y in pts]})
    def tapxy(x, y): touch('touchStart', [(9, x, y)]); time.sleep(0.06); touch('touchEnd', []); time.sleep(0.25)
    def L2C(lx, ly):  # logical game pixel -> CSS px
        r = pg.evaluate("(() => { const r = __nbd.G.view.getBoundingClientRect(); return [r.left, r.top, r.width, r.height, __nbd.G.VW, __nbd.G.VH]; })()")
        return r[0] + lx / r[4] * r[2], r[1] + ly / r[5] * r[3]
    def center(sel): r = pg.locator(sel).bounding_box(); return r['x'] + r['width'] / 2, r['y'] + r['height'] / 2
    pg.goto('http://localhost:8731/'); pg.wait_for_function('window.__loaded === true'); time.sleep(0.8)
    pg.screenshot(path='tests/out/t_title.png'); print('title', pg.evaluate(S))
    m = pg.evaluate('__nbd.game.menu.rects[0]'); tapxy(*L2C(m[0] + m[2] / 2, m[1] + m[3] / 2)); time.sleep(0.4)
    print('select', pg.evaluate(S)); 
    c = pg.evaluate('__nbd.game.cardRects[3]'); x, y = L2C(c[0] + c[2] / 2, c[1] + c[3] / 2); tapxy(x, y); tapxy(x, y)
    time.sleep(1); pg.screenshot(path='tests/out/t_select.png'); time.sleep(0.6); print('cutscene', pg.evaluate('__nbd.game.scene'))
    tapxy(*L2C(150, 100)); time.sleep(3.0); print('play', pg.evaluate(S))  # v0.4: a tap skips the cutscene
    # joystick: hold in the left zone and push right, while tapping HIT
    jx, jy = W * 0.18, H * 0.7
    touch('touchStart', [(1, jx, jy)]); time.sleep(0.05)
    for k in range(10): touch('touchMove', [(1, jx + k * 5, jy)]); time.sleep(0.02)
    time.sleep(1.4); print('walking', pg.evaluate(S))
    ax, ay = center('#pad .ab[data-b=atk]')
    for k in range(4):
        touch('touchStart', [(1, jx + 45, jy), (2, ax, ay)]); time.sleep(0.05); touch('touchEnd', [(1, jx + 45, jy)]); time.sleep(0.2)
    pg.screenshot(path='tests/out/t_play.png'); print('attacking', pg.evaluate(S))
    touch('touchEnd', []); time.sleep(0.3)
    jbx, jby = center('#pad .ab[data-b=jmp]'); tapxy(jbx, jby); print('jump', pg.evaluate('__nbd.W.heroes[0].st'))
    px, py = center('#pausebtn'); tapxy(px, py); print('pause', pg.evaluate(S)); pg.screenshot(path='tests/out/t_pause.png')
    m = pg.evaluate('__nbd.game.overlay.rects[0]'); tapxy(*L2C(m[0] + m[2] / 2, m[1] + m[3] / 2)); print('resume', pg.evaluate(S))
    # portrait -> rotate prompt
    pg.set_viewport_size({'width': H, 'height': W}); time.sleep(0.8); pg.screenshot(path='tests/out/t_portrait.png')
    print('rotate prompt visible:', pg.evaluate("(() => { const e = document.querySelector('#rotate, .rotate, [data-rotate]'); return e ? getComputedStyle(e).display : 'none-found'; })()"))
    b.close()
print('\n'.join(errs[:30]) or 'no console errors')
