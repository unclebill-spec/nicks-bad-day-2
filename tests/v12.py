# v0.12: LEVEL SELECT from the title menu. Every stage starts from the select screen (keyboard), with fresh HP; touch double-tap,
# gamepad d-pad + A, BACK, and the phone layouts (915x412, 844x390, 667x375). Screenshots -> tests/out/v12_*.png
import time, sys
from playwright.sync_api import sync_playwright
U = 'http://localhost:8731/'; errs = []; fails = []
def check(n, c, info=''):
    print(('PASS ' if c else 'FAIL ') + n, info if not c else ''); (None if c else fails.append(n))
def key(pg, k, after=0.15): pg.keyboard.down(k); time.sleep(0.08); pg.keyboard.up(k); time.sleep(after)
SC = '__nbd.game.scene'
EXPECT = [('play', 1), ('bonus', None), ('play', 2), ('scoot', None), ('play', 5), ('play', 3), ('play', 4)]  # v0.13: + the psych ward
PAD = """(()=>{const b=(i)=>({pressed:window.__pb===i,value:window.__pb===i?1:0});navigator.getGamepads=()=>[{id:'mock',index:0,connected:true,mapping:'standard',axes:[0,0,0,0],buttons:Array.from({length:17},(_,i)=>b(i)),timestamp:performance.now()}];})()"""
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 960, 'height': 540}); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(U + '?nocut=1'); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.6)
    labels = pg.evaluate("__nbd.game.menu.items.map(i=>i.label)")
    check('title menu has LEVEL SELECT next to 1P / 2P', labels[:3] == ['1 PLAYER', '2 PLAYERS', 'LEVEL SELECT'], labels)
    names = pg.evaluate("__nbd.PICKS.map(p=>p.name+' / '+p.boss)"); print(names)
    check('seven stages listed in order', len(names) == 7 and 'MED-SURG' in names[0] and 'GARAGE' in names[6] and 'PSYCH' in names[4])
    for i, (scene, lvid) in enumerate(EXPECT):
        pg.evaluate("__nbd.toTitle()"); time.sleep(0.3)
        key(pg, 'ArrowDown'); key(pg, 'ArrowDown'); key(pg, 'KeyJ', after=0.5)
        check(f'[{i+1}] keyboard: title -> level select', pg.evaluate(SC) == 'levels')
        if i == 0: pg.screenshot(path='tests/out/v12_levels.png')
        for _ in range((i - pg.evaluate('__nbd.game.lvCur')) % 7): key(pg, 'ArrowRight', after=0.08)
        key(pg, 'KeyJ', after=0.3); key(pg, 'KeyJ', after=0.4)  # pick -> 1 PLAYER
        check(f'[{i+1}] -> nurse select', pg.evaluate(SC) == 'select' and pg.evaluate("__nbd.game.pick") == i)
        key(pg, 'KeyJ', after=1.2)
        try: pg.wait_for_function(f"{SC}==='{scene}' || ({SC}==='intro' && '{scene}'==='play')", timeout=8000)
        except Exception: pass
        st = pg.evaluate("[__nbd.game.scene, __nbd.W.lv && __nbd.W.lv.id, __nbd.W.heroes.map(h=>[h.hp,h.maxHp])]")
        ok = (st[0] == scene or (scene == 'play' and st[0] == 'intro')) and (lvid is None or st[1] == lvid) and all(a == m for a, m in st[2])
        check(f'[{i+1}] {names[i]} starts with fresh HP', ok, st)
    # carries on normally: the garage tally -> ending; the night shift -> garage
    pg.evaluate("__nbd.W.cleared = true"); pg.wait_for_function(f"{SC}==='tally'", timeout=8000); time.sleep(3.3); key(pg, 'KeyJ', after=0.5)
    check('garage pick -> tally -> THE END', pg.evaluate(SC) == 'ending')
    # BACK
    pg.evaluate("__nbd.toLevels()"); time.sleep(0.4); key(pg, 'Escape', after=0.3)
    check('Escape = BACK to the title', pg.evaluate(SC) == 'title')
    # gamepad
    pg.evaluate("__nbd.toLevels(); __nbd.game.lvCur = 0"); pg.evaluate(PAD); time.sleep(0.4)
    pg.evaluate("window.__pb=15"); time.sleep(0.15); pg.evaluate("window.__pb=-1"); time.sleep(0.2)
    pg.evaluate("window.__pb=0"); time.sleep(0.15); pg.evaluate("window.__pb=-1"); time.sleep(0.3)
    check('gamepad: d-pad right + A picks card 2', pg.evaluate("__nbd.game.lvCur") == 1 and pg.evaluate("!!__nbd.game.overlay"), pg.evaluate("[__nbd.game.lvCur, !!__nbd.game.overlay]"))
    pg.close()
    for (w, h) in [(915, 412), (844, 390), (667, 375)]:
        ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=True, is_mobile=True); pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(U + '?nocut=1'); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.6)
        pg.evaluate("__nbd.toLevels()"); time.sleep(0.5)
        R = pg.evaluate("[__nbd.game.lvRects, __nbd.game.lvBack, __nbd.G.VW, __nbd.G.VH]")
        fit = all(r[0] >= 0 and r[1] >= 0 and r[0] + r[2] <= R[2] and r[1] + r[3] <= R[3] for r in R[0] + [R[1]]) and len(R[0]) == 7
        check(f'phone {w}x{h}: all seven cards + BACK fit on screen', fit, R)
        if w == 915: pg.screenshot(path='tests/out/v12_levels_phone.png')
        box = pg.evaluate("(()=>{const c=document.querySelector('canvas').getBoundingClientRect();return [c.left,c.top,c.width/__nbd.G.VW,c.height/__nbd.G.VH]})()")
        tap = lambda r: pg.touchscreen.tap(box[0] + (r[0] + r[2] / 2) * box[2], box[1] + (r[1] + r[3] / 2) * box[3])
        tap(R[0][6]); time.sleep(0.3)
        check(f'phone {w}: first tap selects', pg.evaluate("__nbd.game.lvCur") == 6 and not pg.evaluate("!!__nbd.game.overlay"))
        tap(R[0][6]); time.sleep(0.3)
        check(f'phone {w}: second tap confirms', pg.evaluate("!!__nbd.game.overlay"))
        pg.evaluate("__nbd.game.overlay=null"); tap(R[1]); time.sleep(0.3)
        check(f'phone {w}: BACK button', pg.evaluate(SC) == 'title')
        ctx.close()
    b.close()
print('console errors:', errs[:3] if errs else 'none'); print('ALL PASS' if not fails and not errs else 'SOME FAILED'); sys.exit(1 if fails or errs else 0)
