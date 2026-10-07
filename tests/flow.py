# Flow test: boss defeat -> tally -> Breakroom Bonus (bot) -> bonus tally -> Radiology -> v0.9 Scooter Run (the bot rides it all the way,
# Marv included) -> scooter tally -> Night Shift -> v0.11 Parking Garage -> ending -> scores -> title; then a game over -> scores.
# (?bot=1 auto-skips the v0.4 cutscenes; tests/v04.py covers them.)
import time
from playwright.sync_api import sync_playwright
errs = []
J = "JSON.stringify({sc:__nbd.game.scene, hi:__nbd.save.hi})"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: errs.append(f'PAGEERROR: {e}'))
    pg.goto('http://localhost:8731/?zone=5&bot=1&god=1&hero=jackie'); pg.wait_for_function('window.__loaded === true')
    time.sleep(4); pg.evaluate('__nbd.W.boss.hp = 3; __nbd.W.boss.phase = 2')
    pg.wait_for_function("__nbd.game.scene === 'tally'", timeout=40000); time.sleep(3.5)
    pg.screenshot(path='tests/out/f_tally.png'); print(pg.evaluate(J))
    pg.keyboard.down('KeyJ'); time.sleep(0.1); pg.keyboard.up('KeyJ'); time.sleep(0.5)
    pg.wait_for_function("__nbd.game.scene === 'bonus'", timeout=5000); time.sleep(6); pg.screenshot(path='tests/out/f_bonus.png')
    pg.evaluate('__nbd.B.left = Math.min(__nbd.B.left, 4)'); print(pg.evaluate(J))
    pg.wait_for_function("__nbd.game.scene === 'btally'", timeout=20000); time.sleep(3.3)
    pg.screenshot(path='tests/out/f_btally.png'); print(pg.evaluate(J))
    pg.keyboard.down('KeyJ'); time.sleep(0.1); pg.keyboard.up('KeyJ'); time.sleep(2)
    # v0.5: the bonus leads up to Floor 4 Radiology, then the night shift, then THE END
    print('radiology', pg.evaluate("JSON.stringify([__nbd.game.scene, __nbd.W.lv.id, __nbd.W.heroes[0].score])"))
    pg.screenshot(path='tests/out/f_radiology.png')
    for lv in (2, 3, 4):
        pg.wait_for_function(f"__nbd.W.lv.id === {lv} && __nbd.game.scene === 'play'", timeout=10000); pg.evaluate('__nbd.W.cleared = true')
        pg.wait_for_function("__nbd.game.scene === 'tally'", timeout=5000); time.sleep(3.3)
        pg.keyboard.down('KeyJ'); time.sleep(0.1); pg.keyboard.up('KeyJ'); time.sleep(1)
        print('after floor', lv, pg.evaluate(J))
        if lv == 2:  # v0.9: Radiology -> the Scooter Run, played for real by the test bot (~80 s), then its tally -> the night shift
            pg.wait_for_function("__nbd.game.scene === 'scoot'", timeout=5000); t0 = time.time()
            pg.wait_for_function("__nbd.SC.phase === 'boss'", timeout=150000); time.sleep(4); pg.screenshot(path='tests/out/f_scooter_boss.png')
            pg.wait_for_function("__nbd.game.scene === 'stally'", timeout=150000); ride = round(time.time() - t0)
            time.sleep(3.3); pg.screenshot(path='tests/out/f_scooter_tally.png')
            print('scooter run', ride, 's', pg.evaluate("JSON.stringify({beat:__nbd.SC.bossBeat, sed:__nbd.SC.sedated, score:__nbd.W.heroes[0].score})"))
            if not (55 <= ride <= 100): print('FAIL scooter run length', ride)
            pg.keyboard.down('KeyJ'); time.sleep(0.1); pg.keyboard.up('KeyJ'); time.sleep(1)
    time.sleep(1); pg.screenshot(path='tests/out/f_ending.png')
    pg.keyboard.down('KeyJ'); time.sleep(0.1); pg.keyboard.up('KeyJ'); time.sleep(1); print(pg.evaluate(J))
    pg.keyboard.down('KeyJ'); time.sleep(0.1); pg.keyboard.up('KeyJ'); time.sleep(1); print(pg.evaluate(J))
    # game over
    pg.goto('http://localhost:8731/?zone=1&hero=nick'); pg.wait_for_function('window.__loaded === true'); time.sleep(1)
    pg.evaluate("const h=__nbd.W.heroes[0]; h.lives=1; h.hp=1")
    pg.wait_for_function("__nbd.W.heroes[0].st === 'out'", timeout=60000); time.sleep(1)
    pg.screenshot(path='tests/out/f_continue.png')
    pg.keyboard.down('Enter'); time.sleep(0.1); pg.keyboard.up('Enter'); time.sleep(0.5)
    print('after continue', pg.evaluate("JSON.stringify([__nbd.W.heroes[0].st, __nbd.W.heroes[0].lives, __nbd.game.continuesLeft()])"))
    pg.evaluate("__nbd.game.creditsUsed = 99; const h=__nbd.W.heroes[0]; h.lives=1; h.hp=1")
    pg.wait_for_function("__nbd.game.scene === 'gameover'", timeout=60000); time.sleep(1.6)
    pg.screenshot(path='tests/out/f_gameover.png')
    pg.keyboard.down('KeyJ'); time.sleep(0.1); pg.keyboard.up('KeyJ'); time.sleep(1)
    pg.screenshot(path='tests/out/f_scores.png'); print(pg.evaluate(J))
    b.close()
print('\n'.join(errs[:30]) or 'no console errors')
