# v0.7: dedicated GRAB (keyboard / pad / touch, P1 + P2): toss forward and over-the-shoulder body slam behind, both
# bowl over other patients; context priority (patient > gurney > weapon > prop); how-to-play pages; BEEF JERKY;
# patients the same size as the nurses; bosses only modestly bigger (Bill's v0.7 override: ~1.2-1.5x height).
# Screenshots -> tests/out/v07_*.png
import time, sys
from playwright.sync_api import sync_playwright
U = 'http://localhost:8731/'
errs = []
def watch(pg):
    pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: errs.append(f'PAGEERROR: {e}'))
def key(pg, k, hold=0.08, after=0.1): pg.keyboard.down(k); time.sleep(hold); pg.keyboard.up(k); time.sleep(after)
SC = "__nbd.game.scene"
def ready(pg):
    pg.wait_for_function('window.__loaded === true', timeout=30000)
    pg.wait_for_function(f"window.__nbd && {SC}==='play' && __nbd.W.heroes.length>0 && __nbd.W.heroes[0].st==='idle'", timeout=30000); time.sleep(0.3)
FREEZE = "(()=>{const W=__nbd.W; W.enemies.forEach(e=>{e.alive=false}); W.enemies.length=0; W.queue && (W.queue.length=0); W.items.length=0; W.shots.length=0; W.zone=99; W.zoneOn=false; W.lockX=W.camX; W.heroes.forEach((h,i)=>{h.x=W.camX+150; h.y=176+i*20; h.face=1; h.carry=null; h.weapon=null; h.held=null; h.ride=null; h.set('idle');}); W.props=W.props.filter(p=>p.x<W.camX-60||p.x>W.camX+__nbd.G.VW+60);})()"
ok = True
def check(name, cond, info=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name, info); sys.stdout.flush(); ok = ok and bool(cond)
def prop(pg, kind, dx, dy=0, who=0):
    return pg.evaluate(f"(()=>{{const W=__nbd.W,h=W.heroes[{who}]; const i=__nbd.prop('{kind}',0,0); const p=W.props[i]; p.x=h.x+{dx}; p.y=Math.max(136,Math.min(212,h.y+{dy})); window.PP=window.PP||[]; PP.push(p); return PP.length-1;}})()")
def foe(pg, kind, dx, dy=0, st='idle'):
    return pg.evaluate(f"(()=>{{const W=__nbd.W,h=W.heroes[0]; const e=__nbd.spawn('{kind}','R'); e.x=h.x+{dx}; e.y=h.y+{dy}; e.tx=e.x; e.ty=e.y; e.set('{st}'); e.cd=99; e.atkCd=99; window.F=window.F||[]; F.push(e); return F.length-1;}})()")
HS = "(()=>{const h=__nbd.W.heroes[%d]; return {st:h.st, carry:h.carry?h.carry.kind:null, x:h.x, z:h.z, face:h.face, w:h.weapon?h.weapon.k:null};})()"
def hs(pg, i=0): return pg.evaluate(HS % i)
BOUNDS = """((sheet, an) => { const G = __nbd.G, A = G.atlas.chars[sheet], [cw, ch] = A.cell, i = A.anims[an].s, sx = (i % A.cols) * cw, sy = Math.floor(i / A.cols) * ch;
  const c = document.createElement('canvas'); c.width = cw; c.height = ch; const x = c.getContext('2d'); x.drawImage(G.img[sheet], sx, sy, cw, ch, 0, 0, cw, ch);
  const d = x.getImageData(0, 0, cw, ch).data; let x0 = cw, x1 = 0, y0 = ch, y1 = 0, n = 0;
  for (let y = 0; y < ch; y++) for (let k = 0; k < cw; k++) if (d[(y * cw + k) * 4 + 3] > 20) { n++; x0 = Math.min(x0, k); x1 = Math.max(x1, k); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
  return [x1 - x0 + 1, y1 - y0 + 1, n]; })"""
MOCK = """(() => { const pad = { id: 'Xbox Wireless Controller (STANDARD GAMEPAD)', index: 0, connected: true, mapping: 'standard', timestamp: 0,
  axes: [0, 0, 0, 0], buttons: Array.from({ length: 17 }, () => ({ pressed: false, value: 0, touched: false })) };
  window.__pad = pad; navigator.getGamepads = () => [window.__padOn ? pad : null, null, null, null];
  window.__padSet = (i, on) => { pad.buttons[i].pressed = on; pad.buttons[i].value = on ? 1 : 0; pad.timestamp++; };
  window.__padConnect = () => { window.__padOn = true; const e = new Event('gamepadconnected'); e.gamepad = pad; dispatchEvent(e); }; })();"""
ONLY = sys.argv[1:] or list('ABCD')
GS = "(()=>{const W=__nbd.W,h=W.heroes[%d]; return {st:h.st, held:h.held?h.held.kind:null, face:h.face, x:h.x, slams:W.stats.slams||0, tosses:W.stats.tosses||0, grabs:W.stats.grabs||0, foes:(window.F||[]).map(e=>({st:e.st, hp:e.hp, dx:Math.round(e.x-h.x), y:Math.round(e.y)}))};})()"
def gs(pg, i=0): return pg.evaluate(GS % i)
def grabbed(pg, i=0): return pg.wait_for_function(f"__nbd.W.heroes[{i}].st==='grab' && !!__nbd.W.heroes[{i}].held", timeout=3000)
DOWN = ('fall', 'down', 'getup', 'dead', 'thrown')
with sync_playwright() as p:
    b = p.chromium.launch()
    # ================================================================ A: grab, toss forward, body slam behind (keyboard P1)
    if 'A' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=nick&god=1&nocut=1&noalarm=1'); ready(pg); pg.evaluate(FREEZE); pg.evaluate("window.F=[]")
        # no more walk-in grabs: walking into a patient just pushes against him
        foe(pg, 'wanderer', 30); pg.keyboard.down('KeyD'); time.sleep(0.9); pg.keyboard.up('KeyD'); r = gs(pg)
        check('walking into a patient no longer grabs (GRAB is a dedicated button)', r['st'] in ('idle', 'walk') and not r['held'] and r['grabs'] == 0, r)
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); foe(pg, 'wanderer', 14)
        key(pg, 'KeyH', after=0.15); r = gs(pg)
        lab = pg.evaluate("document.getElementById('b_grab').dataset.ctx")
        check('GRAB next to a patient grabs him', r['st'] == 'grab' and r['held'] == 'wanderer', r)
        check('while holding, the GRAB button reads TOSS', lab == 'TOSS', lab)
        pg.screenshot(path='tests/out/v07_hold_hint.png')
        # 1) just the direction toward where you face = toss forward, and he bowls over the patient in the way
        foe(pg, 'crutch', 80); time.sleep(0.05)
        key(pg, 'KeyD', 0.12, 0.05); r1 = gs(pg); time.sleep(0.9); r = gs(pg)
        check('FORWARD (just the direction) tosses him forward', r1['st'] == 'throw' and r['tosses'] == 1 and r['foes'][0]['dx'] > 60, [r1['st'], r])
        check('the tossed patient knocks down + damages the patient he hits', r['foes'][1]['hp'] < 42 and r['foes'][1]['st'] in DOWN, r['foes'])
        # 2) the direction AWAY from where you face = over-the-shoulder body slam behind you
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); foe(pg, 'wanderer', 14); foe(pg, 'bell', -44)
        key(pg, 'KeyH', after=0.15); hp0 = pg.evaluate("F[0].hp")
        key(pg, 'KeyA', 0.12, 0.0); time.sleep(0.12); mid = pg.evaluate("({st:__nbd.W.heroes[0].st, z:F[0].z, rot:F[0].rot||0, face:__nbd.W.heroes[0].face})")
        pg.screenshot(path='tests/out/v07_slam_mid.png'); time.sleep(0.8); r = gs(pg)
        check('AWAY (just the direction) = body slam: he goes up over her shoulder', mid['st'] == 'slam' and mid['z'] > 20 and abs(mid['rot']) > 0.3, mid)
        check('...she keeps facing forward and he lands BEHIND her', r['face'] == 1 and r['foes'][0]['dx'] < -8 and r['slams'] == 1, r)
        check('the slam hits hard (more than a toss landing)', hp0 - r['foes'][0]['hp'] >= 24 or r['foes'][0]['st'] == 'dead', [hp0, r['foes'][0]])
        check('the slam landing knocks down the patient behind her too', r['foes'][1]['st'] in DOWN and r['foes'][1]['hp'] < 40, r['foes'][1])
        # 3) direction + ATK works too (both ways), immediately
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); foe(pg, 'escape', 14)
        key(pg, 'KeyH', after=0.15); pg.keyboard.down('KeyD'); key(pg, 'KeyJ', 0.06, 0.05); pg.keyboard.up('KeyD'); time.sleep(0.6); r = gs(pg)
        check('FORWARD + ATK = toss', r['tosses'] == 2 and r['foes'][0]['dx'] > 40, r)
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); foe(pg, 'escape', 14)
        key(pg, 'KeyH', after=0.15); pg.keyboard.down('KeyA'); key(pg, 'KeyJ', 0.06, 0.05); pg.keyboard.up('KeyA'); time.sleep(0.8); r = gs(pg)
        check('AWAY + ATK = body slam', r['slams'] == 2 and r['foes'][0]['dx'] < -8, r)
        # 4) ATK alone = knees; the third ATK tosses. GRAB again = toss. JUMP = toss.
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); foe(pg, 'ivswing', 14)
        key(pg, 'KeyH', after=0.15); hp0 = pg.evaluate("F[0].hp")
        key(pg, 'KeyJ', 0.05, 0.32); key(pg, 'KeyJ', 0.05, 0.32); k2 = gs(pg); key(pg, 'KeyJ', 0.05, 0.5); r = gs(pg)
        check('ATK alone knees him (twice), the third ATK tosses', k2['held'] == 'ivswing' and k2['foes'][0]['hp'] < hp0 and r['tosses'] == 3, [hp0, k2, r])
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); foe(pg, 'wanderer', 14)
        key(pg, 'KeyH', after=0.15); key(pg, 'KeyH', after=0.6); r = gs(pg)
        check('GRAB again = toss forward', r['tosses'] == 4 and r['foes'][0]['dx'] > 40, r)
        # 5) holding the direction you walked in with: still works after a short beat (no instant accidental toss)
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); foe(pg, 'wanderer', 14)
        pg.keyboard.down('KeyD'); key(pg, 'KeyH', 0.06, 0.0); time.sleep(0.15); early = gs(pg); time.sleep(0.6); pg.keyboard.up('KeyD'); r = gs(pg)
        check('grabbing while already pushing forward does not toss instantly...', early['st'] == 'grab', early)
        check('...but keeping it held tosses', r['tosses'] == 5, r)
        # 6) hint text + help pages
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]")
        pg.keyboard.press('Escape'); time.sleep(0.3)
        pg.evaluate("(()=>{const o=__nbd.game.overlay; o.items.find(i=>i.label==='HOW TO PLAY').act();})()"); time.sleep(0.3)
        p0 = pg.evaluate("__nbd.game.overlay.page"); pg.screenshot(path='tests/out/v07_help1.png')
        key(pg, 'ArrowRight', 0.1, 0.3); p1 = pg.evaluate("__nbd.game.overlay.page"); pg.screenshot(path='tests/out/v07_help2.png')
        check('how-to-play has 2 pages (controls, moves) and flips with left/right', p0 == 0 and p1 == 1, [p0, p1])
        key(pg, 'Escape', 0.1, 0.3); key(pg, 'Escape', 0.1, 0.3)
        pg.close()
    # ================================================================ B: context priority, gamepad, P2, touch
    if 'B' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=kim&god=1&nocut=1&noalarm=1'); ready(pg); pg.evaluate(FREEZE); pg.evaluate("window.F=[]; window.PP=[]")
        i = prop(pg, 'chair', 12); foe(pg, 'wanderer', 16)
        key(pg, 'KeyH', after=0.2); r = gs(pg)
        check('priority: a patient in reach beats a prop', r['held'] == 'wanderer' and hs(pg)['carry'] is None, r)
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]; window.PP=[]"); i = prop(pg, 'trash', 12)
        key(pg, 'KeyH', after=0.45); check('with no patient, GRAB still lifts the prop', hs(pg)['carry'] == 'trash', hs(pg))
        pg.evaluate(FREEZE); pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; const it=__nbd.drop('w:mop'); it.x=h.x; it.y=h.y;})()"); time.sleep(0.1)
        key(pg, 'KeyH', after=0.5); check('GRAB on a weapon picks it up', hs(pg)['w'] == 'w:mop' or pg.evaluate("!!__nbd.W.heroes[0].weapon"), hs(pg))
        pg.evaluate(FREEZE); prop(pg, 'gurney', 20); time.sleep(0.1); key(pg, 'KeyH', after=0.3)
        check('GRAB next to a gurney still rides it', hs(pg)['st'] == 'ride', hs(pg))
        pg.close()
        # gamepad: B grabs, stick away slams
        pg = b.new_page(viewport={'width': 960, 'height': 540}); pg.add_init_script(MOCK); watch(pg)
        pg.goto(U + '?level=1&hero=will&god=1&nocut=1&noalarm=1'); ready(pg); pg.evaluate('__padConnect()'); pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.3)
        foe(pg, 'wanderer', 16)
        pg.evaluate('__padSet(1, true)'); time.sleep(0.1); pg.evaluate('__padSet(1, false)'); time.sleep(0.15); g1 = gs(pg)
        pg.evaluate('__pad.axes[0]=-1; __pad.timestamp++'); time.sleep(0.15); pg.evaluate('__pad.axes[0]=0; __pad.timestamp++'); time.sleep(0.8); r = gs(pg)
        check('gamepad: B grabs, stick AWAY body-slams', g1['st'] == 'grab' and r['slams'] == 1 and r['foes'][0]['dx'] < -8, [g1['st'], r])
        foe(pg, 'wanderer', 16); pg.evaluate("__nbd.W.heroes[0].face=1"); time.sleep(0.2)
        pg.evaluate('__padSet(1, true)'); time.sleep(0.1); pg.evaluate('__padSet(1, false)'); time.sleep(0.15)
        pg.evaluate('__pad.axes[0]=1; __pad.timestamp++'); time.sleep(0.15); pg.evaluate('__pad.axes[0]=0; __pad.timestamp++'); time.sleep(0.6); r = gs(pg)
        check('gamepad: stick FORWARD tosses', r['tosses'] == 1, r)
        pg.close()
        # 2P keyboard: P2 grabs with M and slams with the arrow away
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?god=1&noalarm=1'); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.6)
        key(pg, 'KeyS'); key(pg, 'Enter', after=0.4); key(pg, 'Comma', after=0.3); key(pg, 'KeyJ', after=0.3); key(pg, 'ArrowRight'); key(pg, 'Comma', after=1.2)
        pg.wait_for_function(f"{SC}==='cutscene'", timeout=8000); time.sleep(0.5); key(pg, 'KeyK', after=0.4)
        pg.wait_for_function(f"{SC}==='play' && __nbd.W.heroes.length===2 && __nbd.W.heroes[1].st==='idle'", timeout=12000); pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.3)
        pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[1]; const e=__nbd.spawn('wanderer','R'); e.x=h.x+16; e.y=h.y; e.tx=e.x; e.ty=e.y; e.set('idle'); e.cd=99; F.push(e);})()")
        key(pg, 'KeyM', after=0.15); g = gs(pg, 1); key(pg, 'ArrowLeft', 0.12, 0.8); r = gs(pg, 1)
        check('2P: P2 grabs with M and body-slams with the arrow away', g['st'] == 'grab' and r['slams'] == 1, [g['st'], r])
        pg.close()
        # touch: GRAB button + floating joystick away = slam, toward = toss
        UA = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36'
        ctx = b.new_context(viewport={'width': 915, 'height': 412}, device_scale_factor=2.6, is_mobile=True, has_touch=True, user_agent=UA)
        pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg); watch(pg)
        def touch(kind, pts): cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [{'x': x, 'y': y, 'id': i} for i, x, y in pts]})
        def btn(name): bx = pg.locator(f'#pad .ab[data-b={name}]').bounding_box(); return bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2
        pg.goto(U + '?level=1&hero=jackie&god=1&nocut=1&noalarm=1'); ready(pg); pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.3)
        foe(pg, 'wanderer', 16); time.sleep(0.1)
        gx, gy = btn('grab'); touch('touchStart', [(5, gx, gy)]); time.sleep(0.08); touch('touchEnd', []); time.sleep(0.15)
        g = gs(pg); lab = pg.evaluate("document.getElementById('b_grab').dataset.ctx"); pg.screenshot(path='tests/out/v07_touch_hold.png')
        jx, jy = 915 * 0.18, 412 * 0.7
        touch('touchStart', [(1, jx, jy)]); time.sleep(0.05)
        for k in range(8): touch('touchMove', [(1, jx - k * 6, jy)]); time.sleep(0.02)
        time.sleep(0.3); touch('touchEnd', []); time.sleep(0.6); r = gs(pg)
        check('touch: GRAB button grabs (label TOSS), joystick AWAY slams', g['st'] == 'grab' and lab == 'TOSS' and r['slams'] == 1, [g['st'], lab, r])
        foe(pg, 'wanderer', 16); pg.evaluate("__nbd.W.heroes[0].face=1"); time.sleep(0.2)
        touch('touchStart', [(5, gx, gy)]); time.sleep(0.08); touch('touchEnd', []); time.sleep(0.15)
        touch('touchStart', [(1, jx, jy)]); time.sleep(0.05)
        for k in range(8): touch('touchMove', [(1, jx + k * 6, jy)]); time.sleep(0.02)
        time.sleep(0.3); touch('touchEnd', []); time.sleep(0.5); r = gs(pg)
        check('touch: joystick FORWARD tosses', r['tosses'] == 1, r)
        # every touch button sits on screen without overlapping another
        bb = pg.evaluate("[...document.querySelectorAll('#pad .ab')].map(e=>{const r=e.getBoundingClientRect(); return [e.dataset.b, r.left, r.top, r.right, r.bottom];})")
        ov = [(a[0], c[0]) for i, a in enumerate(bb) for c in bb[i + 1:] if a[1] < c[3] and c[1] < a[3] and a[2] < c[4] and c[2] < a[4]]
        check('touch buttons all fit on the phone screen with no overlaps', not ov and all(0 <= x0 and x1 <= 915 and 0 <= y0 and y1 <= 412 for _, x0, y0, x1, y1 in bb), [bb, ov])
        pg.screenshot(path='tests/out/v07_touch_layout.png')
        ctx.close()
    # ================================================================ C: BEEF JERKY
    if 'C' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=nick&nocut=1&noalarm=1'); ready(pg); pg.evaluate(FREEZE)
        pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.hp=40; const it=__nbd.drop('jerky'); it.x=h.x+40; it.y=h.y;})()"); time.sleep(0.2)
        pg.keyboard.down('KeyD'); time.sleep(0.6); pg.keyboard.up('KeyD'); time.sleep(0.1)
        r = pg.evaluate("(async()=>{const D=await import('./src/data.js'); const all=JSON.stringify([D.ITEMS, D.LOOT]); return {hp:__nbd.W.heroes[0].hp, j:D.ITEMS.jerky, snap:/snap/i.test(all), spr:!!__nbd.G.atlas.sprites.rects.jerky, old:!!__nbd.G.atlas.sprites.rects.snapstix};})()")
        check('BEEF JERKY drop: heals 30 with the BEEF JERKY! pickup text', r['hp'] == 70 and r['j']['msg'] == 'BEEF JERKY!', r)
        check('no SNAP STIX left in items, loot tables or the sprite atlas', not r['snap'] and r['spr'] and not r['old'], r)
        pg.close()
    # ================================================================ D: sizes (Bill's v0.7 override) + boss fights still winnable
    if 'D' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=nick&god=1&nocut=1&noalarm=1'); ready(pg); pg.evaluate(FREEZE)
        size = lambda sheet, an='idle': pg.evaluate(BOUNDS + f"('{sheet}', '{an}')")
        nurses = {n: size(n) for n in ('nick', 'kim', 'will', 'jackie')}
        NH = sum(v[1] for v in nurses.values()) / 4; NW = sum(v[0] for v in nurses.values()) / 4
        pats = {k: size(k) for k in ('wanderer', 'spammer', 'escape', 'ivswing', 'sundowner', 'crutch', 'bell', 'elite', 'runner', 'tray', 'o2', 'barium', 'apron', 'yeller', 'visitor')}
        bad = {k: round(v[1] / NH, 2) for k, v in pats.items() if not 0.88 <= v[1] / NH <= (1.16 if k == 'visitor' else 1.12)}
        check('every patient type, elite and variant is nurse height (within ~10%)', not bad, [round(NH, 1), {k: v[1] for k, v in pats.items()}, bad])
        wide = {k: round(v[0] / NW, 2) for k, v in pats.items() if not 0.75 <= v[0] / NW <= 1.45}
        check('patients have a nurse-like build (width)', not wide, [round(NW, 1), {k: v[0] for k, v in pats.items()}, wide])
        boss = {'tilly': size('tilly'), 'mri': size('mri'), 'lou': size('lou')}
        ratio = {k: round(v[1] / NH, 2) for k, v in boss.items()}
        check('bosses are only modestly bigger: 1.2-1.5x a nurse\'s height (Tilly, MRI, Lou)', all(1.2 <= r <= 1.5 for r in ratio.values()), [round(NH, 1), boss, ratio])
        hb = pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0]; const e=__nbd.spawn('wanderer','R'), v=__nbd.spawn('visitor','R'); const r={hero:h.h, pat:e.h, vis:v.h}; e.alive=false; v.alive=false; return r;})()")
        check('patient hitboxes match the staff (h within 10% of a nurse)', abs(hb['pat'] - hb['hero']) <= 6 and hb['vis'] <= hb['hero'] * 1.15, hb)
        pg.close()
        for name, url, cls in (('Turbo Tilly', 'level=1&zone=5', 'tilly'), ('Lead-Apron Lou', 'level=2&zone=2', 'lou'), ('MAGNA-SCAN 3000', 'level=2&zone=5', 'mri')):
            pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
            pg.goto(U + f'?{url}&hero=will&god=1&bot=1&nocut=1&noalarm=1')
            pg.wait_for_function('window.__loaded === true', timeout=30000)
            pg.wait_for_function("window.__nbd && __nbd.W.boss && __nbd.W.boss.isBoss", timeout=90000)
            r = pg.evaluate("(()=>{const B=__nbd.W.boss,h=__nbd.W.heroes[0]; return {w:B.w, h:B.h, hh:h.h};})()")
            check(f'{name}: hitbox scaled down with the art (h {r["h"]} vs nurse {r["hh"]})', 1.15 <= r['h'] / 54 <= 1.6, r)
            t0 = time.time(); hurt = 0
            while time.time() - t0 < 240:
                st = pg.evaluate("(()=>{const B=__nbd.W.boss, h=__nbd.W.heroes[0]; return {dead: !B || B.st==='defeat' || B.hp<=0 || !B.alive, hp: B?B.hp:0, hits: h.hitsTaken||0, scene: __nbd.game.scene};})()")
                if st['dead'] or st['scene'] != 'play': break
                time.sleep(2)
            pg.screenshot(path=f'tests/out/v07_{cls}_fight.png')
            check(f'{name}: the bot still wins the fight (god mode) in {int(time.time() - t0)} s', st['dead'] or st['scene'] != 'play', st)
            pg.close()
    b.close()
print('console errors:', errs[:8] if errs else 'none')
if not errs: print('no console errors')
print('ALL PASS' if ok and not errs else 'SOME FAILED')
