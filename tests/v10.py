# v0.10: HEATHER, the 6th nurse: blonde, royal blue scrubs (separate top + deeper pants, visible waist), staff-sized, fast +
# tough, own combo (hc1-3: jab, elbow, HIP CHECK) and RUNNING CLOTHESLINE special, snarky speech bubbles with Bill's exact
# lines, six-card select on desktop / phones / 4:3 (keyboard, touch, pad, 2P), HUD, tally, cutscenes, ending, Scooter Run.
# Screenshots -> tests/out/v10_*.png (+ docs/v10_select.png, docs/v10_select_phone.png)
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
ONLY = sys.argv[1:] or list('ABCDEFGHIJK')
DOWN = ('fall', 'down', 'getup', 'dead', 'thrown')
BILL = ["Your hands aren't broke, you can wipe your own ass.", "You don't like being wet? Shouldn't have pissed in your gown.",
        "Here's a rag, you can clean it up yourself.", "This isn't a restaurant. I have sick patients to take care of, your sandwich can wait."]
EXTRA = ["Call bell's for emergencies, not ice chips.", "I'm your nurse, not your waitress.", "No, you can't have more Dilaudid.", "Hospital food isn't room service."]
SAY = "(()=>{const h=__nbd.W.heroes[%d]; return {s:h.sayS, said:(__nbd.W.said||[]).slice(), st:h.st, lines:h.d.lines, until:h.sayUntil, t:__nbd.W.t, shoutT:h.shoutT||0};})()"
def say(pg, i=0): return pg.evaluate(SAY % i)
def lines(pg, ev, i=0): return pg.evaluate(f"__nbd.W.heroes[{i}].d.lines['{ev}']")
def recd(pg, i=0): pg.evaluate(f"(()=>{{const h=__nbd.W.heroes[{i}]; h.sayCd=0; h.sayS=null; __nbd.W.said=[];}})()")
def no_overlap(R, VW, VH):
    for i, a in enumerate(R):
        if a[0] < 0 or a[1] < 0 or a[0] + a[2] > VW or a[1] + a[3] > VH: return False
        for c in R[i + 1:]:
            if a[0] < c[0] + c[2] and c[0] < a[0] + a[2] and a[1] < c[1] + c[3] and c[1] < a[1] + a[3]: return False
    return True
COLS = """((sheet, an, f, cols) => { const G = __nbd.G, A = G.atlas.chars[sheet], [cw, ch] = A.cell, i = A.anims[an].s + (f || 0), sx = (i % A.cols) * cw, sy = Math.floor(i / A.cols) * ch;
  const c = document.createElement('canvas'); c.width = cw; c.height = ch; const x = c.getContext('2d', { willReadFrequently: true }); x.drawImage(G.img[sheet], sx, sy, cw, ch, 0, 0, cw, ch);
  const d = x.getImageData(0, 0, cw, ch).data, out = {}; for (const k of cols) out[k] = { n: 0, y0: 999, y1: -1 };
  for (let y = 0; y < ch; y++) for (let q = 0; q < cw; q++) { const j = (y * cw + q) * 4; const hex = '#' + [d[j], d[j + 1], d[j + 2]].map(v => v.toString(16).padStart(2, '0')).join('');
    if (d[j + 3] > 200 && out[hex]) { out[hex].n++; out[hex].y0 = Math.min(out[hex].y0, y); out[hex].y1 = Math.max(out[hex].y1, y); } }
  return out; })"""
SCREEN_COUNT = """((hex) => { const v=__nbd.G.view, c=document.createElement('canvas'); c.width=v.width; c.height=v.height; const x=c.getContext('2d', {willReadFrequently:true}); x.drawImage(v,0,0); const d=x.getImageData(0,0,c.width,c.height).data; const r=parseInt(hex.slice(1,3),16), g=parseInt(hex.slice(3,5),16), bl=parseInt(hex.slice(5,7),16); let n=0;
  for (let i=0;i<d.length;i+=4) if (d[i]===r && d[i+1]===g && d[i+2]===bl) n++; return n; })"""
UA = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36'
TOP, PANTS, HAIR = '#2448d8', '#1c38b0', '#f4d470'
def to_play(pg, press):
    pg.wait_for_function("__nbd.game.scene==='cutscene' || __nbd.game.scene==='play' || __nbd.game.scene==='intro'", timeout=20000)
    for k in range(10):
        if pg.evaluate("__nbd.game.scene") == 'play': break
        press(); time.sleep(0.6)
    pg.wait_for_function("__nbd.game.scene==='play' && __nbd.W.heroes.length>0 && __nbd.W.heroes[0].st==='idle'", timeout=30000)
with sync_playwright() as p:
    b = p.chromium.launch()
    # ================================================================ A: art + data (staff size, royal blue top + deeper pants, blonde, stats, lines)
    if 'A' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.5)
        an = pg.evaluate("(()=>{const A=__nbd.G.atlas.chars.heather; return A ? Object.fromEntries(Object.entries(A.anims).map(([k,v])=>[k,v.n])) : null})()")
        need = ['idle', 'walk', 'run', 'hc1', 'hc2', 'hc3', 'special', 'jump', 'jkick', 'grab', 'throw', 'hurt', 'down', 'win', 'jab', 'defib', 'lift', 'carry', 'ride', 'team', 'scoot', 'scootf', 'scooth']
        check('Heather sheet has every hero animation (combo hc1-3, 4-frame clothesline, scooter poses)', an and all(k in an for k in need) and an['special'] == 4 and an['hc3'] == 3, an and [k for k in need if k not in an])
        sp = pg.evaluate("['face_heather','face_heather_hurt'].map(k => !!__nbd.G.atlas.sprites.rects[k])")
        check('HUD / select portraits (normal + hurt)', all(sp), sp)
        size = lambda n: pg.evaluate(BOUNDS + f"('{n}','walk')")
        nurses = {n: size(n) for n in ('nick', 'kim', 'will', 'jackie', 'nate')}; hh = size('heather')
        avg = sum(v[1] for v in nurses.values()) / 5
        check('normal staff size: height within 0.9-1.1x the nurse average, not wider than Nick', avg * 0.9 <= hh[1] <= avg * 1.1 and hh[0] <= nurses['nick'][0] + 2, {'heather': hh[:2], 'avg': round(avg, 1), 'nick_w': nurses['nick'][0]})
        c = pg.evaluate(COLS + "('heather','idle',0,[%r,%r,%r])" % (TOP, PANTS, HAIR))
        check('royal blue top + deeper royal blue pants (two colours, top above pants = visible waist)', c[TOP]['n'] > 60 and c[PANTS]['n'] > 60 and c[TOP]['y0'] < c[PANTS]['y0'] and c[PANTS]['y1'] > c[TOP]['y1'], c)
        check('blonde hair, worn long (reaches below the head)', c[HAIR]['n'] > 30 and c[HAIR]['y1'] - c[HAIR]['y0'] > 14, c[HAIR])
        d = pg.evaluate("(async()=>{const m=await import('./src/data.js'); return {H:m.HEROES.heather, order:m.HERO_ORDER, bill:m.BILL_LINES, nick:m.HEROES.nick, will:m.HEROES.will, kim:m.HEROES.kim}})()")
        H = d['H']
        check('6th nurse in HERO_ORDER', d['order'] == ['nick', 'kim', 'will', 'jackie', 'nate', 'heather'], d['order'])
        check('own stats: fast and tough, mid power', H['walk'] > d['nick']['walk'] and H['hp'] > d['nick']['hp'] and H['power'] == 1.0 and H['stats'][1] >= 4 and H['stats'][3] >= 4 and H['stats'][0] == 3, [H['walk'], H['hp'], H['power'], H['stats']])
        check('own 3-hit combo + CLOTHESLINE special', H['combo'] == ['hc1', 'hc2', 'hc3'] and H['special'] == 'CLOTHESLINE', [H['combo'], H['special']])
        allL = sum(H['lines'].values(), [])
        check("Bill's four lines, verbatim", d['bill'] == BILL and all(x in allL for x in BILL), [x for x in BILL if x not in allL])
        check('plus snarky extras (ice chips, waitress, Dilaudid, room service, more)', all(x in allL for x in EXTRA) and len(set(allL)) >= 25, len(set(allL)))
        ev = ['spawn', 'idle', 'grab', 'ativan', 'codeblue', 'special', 'hurt', 'clear', 'zone', 'revive', 'ko', 'food']
        check('lines for spawn, idle, grabs, Ativan, Code Blue, special, damage, floor clear (+ more)', all(H['lines'].get(e) for e in ev), [e for e in ev if not H['lines'].get(e)])
        pg.close()
    # ================================================================ B: desktop select: six cards, keyboard, title line-up
    if 'B' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?noalarm=1'); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(1.0)
        n = pg.evaluate(SCREEN_COUNT + "('%s')" % TOP)
        check('title: Heather (royal blue) stands in the line-up of six', n > 20, n)
        pg.screenshot(path='tests/out/v10_title.png')
        key(pg, 'Enter', after=0.5)
        sel = pg.evaluate("[__nbd.game.scene, __nbd.G.VW, __nbd.G.VH, __nbd.game.cardRects]")
        check('select: 6 cards inside the 398x224 view, no overlaps', sel[0] == 'select' and len(sel[3]) == 6 and no_overlap(sel[3], sel[1], sel[2]), [sel[1], sel[2], [r[2] for r in sel[3]]])
        for k in range(5): key(pg, 'KeyD', after=0.12)
        c1 = pg.evaluate('__nbd.game.sel.p[0].cur'); key(pg, 'KeyD', after=0.12); c2 = pg.evaluate('__nbd.game.sel.p[0].cur'); key(pg, 'KeyA', after=0.12); c3 = pg.evaluate('__nbd.game.sel.p[0].cur')
        check('keyboard: right x5 reaches HEATHER, wraps to Nick and back', (c1, c2, c3) == (5, 0, 5), (c1, c2, c3))
        time.sleep(0.4); pg.screenshot(path='docs/v10_select.png'); pg.screenshot(path='tests/out/v10_select.png')
        key(pg, 'KeyJ', after=0.4); key(pg, 'Enter', after=0.6)
        to_play(pg, lambda: key(pg, 'KeyK', after=0.1))
        check('picking the 6th card starts the shift as Heather', pg.evaluate('__nbd.W.heroes[0].id') == 'heather')
        time.sleep(0.5); pg.screenshot(path='tests/out/v10_hud.png')
        hud = pg.evaluate(SCREEN_COUNT + "('%s')" % HAIR)
        check('HUD portrait + sprite on screen (blonde pixels)', hud > 40, hud)
        pg.close()
    # ================================================================ C: phones (+ 4:3 grid): fit, double-tap Heather, touch ATK / SP
    if 'C' in ONLY:
        for (vw, vh, mob) in ((915, 412, True), (844, 390, True), (667, 375, True), (800, 600, False)):
            ctx = b.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=2.6 if mob else 1, is_mobile=mob, has_touch=True, user_agent=UA if mob else None)
            pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg); watch(pg)
            def touch(kind, pts): cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [{'x': x, 'y': y, 'id': i} for i, x, y in pts]})
            def tapxy(x, y): touch('touchStart', [(9, x, y)]); time.sleep(0.06); touch('touchEnd', []); time.sleep(0.25)
            def L2C(lx, ly):
                r = pg.evaluate("(() => { const r = __nbd.G.view.getBoundingClientRect(); return [r.left, r.top, r.width, r.height, __nbd.G.VW, __nbd.G.VH]; })()")
                return r[0] + lx / r[4] * r[2], r[1] + ly / r[5] * r[3]
            pg.goto(U + '?noalarm=1'); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.8)
            m = pg.evaluate('__nbd.game.menu.rects[0]'); tapxy(*L2C(m[0] + m[2] / 2, m[1] + m[3] / 2)); time.sleep(0.4)
            sel = pg.evaluate("[__nbd.game.scene, __nbd.G.VW, __nbd.G.VH, __nbd.game.cardRects]")
            tag = f'{vw}x{vh}' + ('' if mob else ' (4:3, 3x2 grid)')
            check(f'{tag}: 6 cards fit on screen, no overlaps', sel[0] == 'select' and len(sel[3]) == 6 and no_overlap(sel[3], sel[1], sel[2]), [sel[1], sel[2], sel[3][5] if len(sel[3]) > 5 else None])
            c = sel[3][5]; x, y = L2C(c[0] + c[2] / 2, c[1] + c[3] / 2); tapxy(x, y)
            if vw in (915, 800): time.sleep(0.3); pg.screenshot(path=f'tests/out/v10_select_{vw}.png')
            if vw == 915: pg.screenshot(path='docs/v10_select_phone.png')
            tapxy(x, y); time.sleep(1.0)
            to_play(pg, lambda: tapxy(*L2C(150, 100)))
            check(f'{tag}: double-tap on the Heather card plays as Heather', pg.evaluate('__nbd.W.heroes[0].id') == 'heather')
            if vw == 915:
                pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2)
                def btn(name): bx = pg.locator(f'#pad .ab[data-b={name}]').bounding_box(); return bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2
                foe(pg, 'wanderer', 26, st='dizzy'); time.sleep(0.05)
                ax_, ay_ = btn('atk'); tapxy(ax_, ay_); time.sleep(0.05)
                check('touch HIT: Heather jabs', pg.evaluate("F[0].hp < F[0].maxHp || F[0].st!=='dizzy'"))
                pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2); foe(pg, 'wanderer', 70, st='dizzy')
                sx, sy = btn('sp'); tapxy(sx, sy); time.sleep(0.05)
                check('touch SP: CLOTHESLINE', pg.evaluate('__nbd.W.heroes[0].st') == 'special')
                time.sleep(0.9); check('touch SP: the patient in her path goes down', pg.evaluate("F[0].st") in DOWN, pg.evaluate("F[0].st"))
                pg.evaluate(FREEZE); time.sleep(0.2)
                # floating joystick: drag right moves her
                x0 = pg.evaluate('__nbd.W.heroes[0].x'); jx, jy = L2C(70, 170)
                touch('touchStart', [(3, jx, jy)]); time.sleep(0.05)
                for k in range(8): touch('touchMove', [(3, jx + 6 * (k + 1), jy)]); time.sleep(0.03)
                time.sleep(0.5); touch('touchEnd', []); time.sleep(0.1)
                check('touch joystick moves Heather', pg.evaluate('__nbd.W.heroes[0].x') - x0 > 20)
            ctx.close()
    # ================================================================ D: gamepad: select + play
    if 'D' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg); pg.add_init_script(MOCK)
        pg.goto(U + '?noalarm=1'); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.6); pg.evaluate('__padConnect()'); time.sleep(0.3)
        def pb(i, hold=0.1, after=0.18): pg.evaluate(f'__padSet({i}, true)'); time.sleep(hold); pg.evaluate(f'__padSet({i}, false)'); time.sleep(after)
        pg.evaluate('__nbd.toSelect(1)'); time.sleep(0.4)
        pb(14); c1 = pg.evaluate('__nbd.game.sel.p[0].cur')
        check('pad: d-pad left from Nick wraps to HEATHER (6th card)', c1 == 5, c1)
        pb(0, after=0.6); to_play(pg, lambda: pb(0, after=0.1))
        check('pad: A locks Heather in and starts', pg.evaluate('__nbd.W.heroes[0].id') == 'heather')
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2); foe(pg, 'wanderer', 26, st='dizzy')
        pb(2, after=0.15); check('pad: X attacks (hc1)', pg.evaluate("F[0].hp < F[0].maxHp"))
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2)
        pb(3, after=0.05); check('pad: Y = CLOTHESLINE', pg.evaluate('__nbd.W.heroes[0].st') == 'special')
        pg.close()
    # ================================================================ E: combo + stats in play
    if 'E' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=heather&god=1&nocut=1&noalarm=1'); ready(pg); pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2)
        foe(pg, 'sundowner', 26, st='dizzy'); pg.evaluate("F[0].hp = F[0].maxHp = 400"); time.sleep(0.05)
        pg.evaluate("window.AN=[]; window.__anT=setInterval(()=>{const h=__nbd.W.heroes[0]; if(h.st==='atk' && AN[AN.length-1]!==h.atkName) AN.push(h.atkName)},10)")
        for k in range(3): key(pg, 'KeyJ', 0.06, 0.17)
        time.sleep(0.8); an = pg.evaluate("clearInterval(__anT), AN"); f = pg.evaluate("({hp:F[0].hp, max:F[0].maxHp, st:F[0].st})")
        check('combo: jab -> elbow -> HIP CHECK', an[:3] == ['hc1', 'hc2', 'hc3'], an)
        check('the hip check knocks the patient down', f['st'] in DOWN and f['hp'] < f['max'], f)
        pg.screenshot(path='tests/out/v10_hipcheck.png')
        pg.evaluate(FREEZE); time.sleep(0.2)
        x0 = pg.evaluate('__nbd.W.heroes[0].x'); pg.keyboard.down('KeyD'); time.sleep(0.6); pg.keyboard.up('KeyD'); x1 = pg.evaluate('__nbd.W.heroes[0].x')
        d = pg.evaluate("({hp:__nbd.W.heroes[0].maxHp, walk:__nbd.W.heroes[0].d.walk})")
        check('fast walk (faster than Nick) and tough (115 HP)', d['walk'] > 72 and d['hp'] == 115 and x1 - x0 > 40, {'dx': round(x1 - x0), **d})
        pg.close()
    # ================================================================ F: the running clothesline
    if 'F' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=heather&nocut=1&noalarm=1'); ready(pg); pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2)
        pg.evaluate("__nbd.W.heroes[0].x = __nbd.W.camX + 60")
        for dx in (50, 90, 130): foe(pg, 'wanderer', dx)
        foe(pg, 'crutch', 110, dy=40)  # off her line: should stay up
        x0 = pg.evaluate('__nbd.W.heroes[0].x'); hp0 = pg.evaluate('__nbd.W.heroes[0].hp')
        pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.hp=100;})()"); hp0 = 100
        key(pg, 'KeyL', 0.05, 0.0); time.sleep(0.32)
        mid = pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; return {st:h.st, t:h.t, hittable:h.hittable(), frame:h.frameFor ? 1 : 1}})()")
        pg.screenshot(path='tests/out/v10_clothesline.png')
        check('mid-dash she can\'t be interrupted (not hittable)', mid['st'] == 'special' and not mid['hittable'], mid)
        time.sleep(1.1)
        r = pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; return {x:h.x, st:h.st, hp:h.hp, s:h.sayS, foes:F.map(e=>e.st), n:__nbd.W.stats.clotheslined}})()")
        check('dashes forward (> 110 px)', r['x'] - x0 > 110, round(r['x'] - x0))
        check('knocks down every patient in her path', all(s in DOWN for s in r['foes'][:3]), r['foes'])
        check('...but not one off her line', r['foes'][3] not in DOWN, r['foes'][3])
        check('costs 8 HP like every special', abs(hp0 - r['hp'] - 8) < 0.01, r['hp'])
        check('snarky line after the special', r['s'] in lines(pg, 'special'), r['s'])
        pg.screenshot(path='tests/out/v10_clothesline_after.png')
        pg.close()
    # ================================================================ G: speech bubbles (spawn, idle, grab, Ativan, Code Blue, hurt, zone, clear)
    if 'G' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=heather&god=1&nocut=1&noalarm=1'); ready(pg)
        r = say(pg)
        check('spawn line', any(x in lines(pg, 'spawn') for x in r['said']), r['said'])
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); recd(pg); time.sleep(0.2)
        try: pg.wait_for_function("(()=>{const h=__nbd.W.heroes[0]; return !!h.sayS && h.d.lines.idle.includes(h.sayS)})()", timeout=15000)
        except Exception: pass
        r = say(pg)
        check('idle ~6 s: a snarky line (+ her annoyed huff)', r['s'] in lines(pg, 'idle') and pg.evaluate("__nbd.W.heroes[0].d.idleSfx") == 'huff', r['s'])
        seen = set()
        for k in range(14):
            pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); recd(pg); time.sleep(0.1); foe(pg, 'wanderer', 14); time.sleep(0.05)
            key(pg, 'KeyH', after=0.15); seen.add(say(pg)['s'])
            if all(x in seen for x in BILL[:2]): break
        check('grabs: "Your hands aren\'t broke..." and "You don\'t like being wet?..." (verbatim)', all(x in seen for x in BILL[:2]), seen)
        pg.screenshot(path='tests/out/v10_grab.png')
        # every one of Bill's lines fits a bubble on screen: force each one and measure the bubble
        pg.evaluate(FREEZE); pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.sayS=null; h.x=__nbd.W.camX+60;})()"); time.sleep(0.15)
        base = pg.evaluate(SCREEN_COUNT + "('#ffffff')")
        for i, line in enumerate(BILL):
            pg.evaluate(FREEZE); time.sleep(0.1)
            pg.evaluate("(l)=>{const h=__nbd.W.heroes[0]; h.sayS=l; h.sayUntil=__nbd.W.t+3; h.x=__nbd.W.camX+60;}", line); time.sleep(0.15)
            if i == 3: pg.screenshot(path='tests/out/v10_longline.png')
            wht = pg.evaluate(SCREEN_COUNT + "('#ffffff')")
            check(f'bubble shows Bill\'s line {i + 1} ({len(line)} chars)', wht - base > 1500 and pg.evaluate("__nbd.W.heroes[0].sayS") == line, wht - base)
        pg.evaluate("__nbd.W.heroes[0].sayS=null"); time.sleep(0.1)
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); recd(pg); time.sleep(0.1)
        pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.inv=0; h.takeHit({dmg:4, dir:1, kb:10, stun:0.2})})()"); r = say(pg)
        check('taking damage: snark', r['s'] in lines(pg, 'hurt'), r['s'])
        time.sleep(0.6); pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); recd(pg); foe(pg, 'wanderer', 30, st='dizzy'); time.sleep(0.05)
        pg.evaluate("__nbd.W.heroes[0].meter = 40"); key(pg, 'KeyL', after=0.3)
        r = pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; return {st:h.st, shout:h.shoutT>__nbd.W.t, words:h.d.shout, snd:h.d.ativanSfx}})()")
        check('Ativan jab: her own shout ("NO MORE DILAUDID. HERE\'S YOUR ATIVAN!") + voice clip', r['st'] == 'ativan' and r['shout'] and 'DILAUDID' in r['words'][0] and 'ATIVAN' in r['words'][1] and r['snd'] == 'ativan_heather', r)
        pg.screenshot(path='tests/out/v10_ativan.png'); time.sleep(0.4); r = say(pg)
        check('...then a follow-up line once the shout is done', r['s'] in lines(pg, 'ativan') and r['until'] > r['shoutT'], [r['s'], r['until'], r['shoutT']])
        time.sleep(1.6); pg.screenshot(path='tests/out/v10_ativan_after.png')
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); recd(pg); time.sleep(0.2); foe(pg, 'wanderer', 60, st='dizzy')
        pg.evaluate("__nbd.W.heroes[0].meter = 100"); key(pg, 'KeyL', after=0.3); r = say(pg)
        check('Code Blue line', r['st'] == 'super' and r['s'] in lines(pg, 'codeblue'), r['s'])
        pg.screenshot(path='tests/out/v10_codeblue.png'); time.sleep(2.5)
        recd(pg); pg.evaluate("__nbd.W.heroes[0].respawn()"); r = say(pg)
        check('revive / continue line', r['s'] in lines(pg, 'revive'), r['s'])
        time.sleep(1.5)
        recd(pg); pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.say('zone');})()"); r = say(pg)
        check('zone clear line', r['s'] in lines(pg, 'zone'), r['s'])
        recd(pg); pg.evaluate("__nbd.W.cleared = true"); pg.wait_for_function("__nbd.game.scene==='tally'", timeout=10000); time.sleep(3.4)
        q = pg.evaluate("__nbd.game.tally[0].quote")
        check('floor clear: she signs off on the tally card', q in lines(pg, 'clear'), q)
        pg.screenshot(path='tests/out/v10_tally.png')
        pg.close()
    # ================================================================ H: 2P keyboard: Nick (P1) + Heather (P2)
    if 'H' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?noalarm=1'); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.8)
        key(pg, 'KeyS'); key(pg, 'Enter', after=0.4); key(pg, 'Comma', after=0.3)
        c0 = pg.evaluate('__nbd.game.sel.p.length>1 && __nbd.game.sel.p[1].cur')
        key(pg, 'KeyJ', after=0.3); key(pg, 'ArrowLeft'); key(pg, 'ArrowLeft')
        c = pg.evaluate('__nbd.game.sel.p[1].cur')
        check('2P select: P2 (arrows) wraps left to HEATHER', c0 == 1 and c == 5, (c0, c))
        pg.screenshot(path='tests/out/v10_select_2p.png')
        key(pg, 'Comma', after=1.2)
        to_play(pg, lambda: key(pg, 'KeyK', after=0.1))
        pg.wait_for_function("__nbd.W.heroes.length===2 && __nbd.W.heroes[1].st==='idle'", timeout=30000); time.sleep(0.3)
        ids = pg.evaluate('__nbd.W.heroes.map(h=>h.id)')
        check('2P: Nick (P1) + Heather (P2)', ids == ['nick', 'heather'], ids)
        pg.evaluate(FREEZE); time.sleep(0.2)
        pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[1]; const e=__nbd.spawn('wanderer','R'); e.x=h.x+26; e.y=h.y; e.tx=e.x; e.ty=e.y; e.set('dizzy'); e.cd=99; e.atkCd=99; window.F=[e];})()")
        key(pg, 'Comma', 0.06, 0.3)
        check('2P: Heather (P2, Comma) attacks', pg.evaluate("F[0].hp < F[0].maxHp"))
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2)
        key(pg, 'Slash', after=0.2); check('2P: Heather (P2, Slash) CLOTHESLINE', pg.evaluate('__nbd.W.heroes[1].st') == 'special')
        time.sleep(1.2); pg.screenshot(path='tests/out/v10_2p.png')
        pg.close()
    # ================================================================ I: Scooter Run as Heather (1P, then 2P next to Nate)
    if 'I' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?autostart=1&scene=scooter&hero=heather&god=1'); pg.wait_for_function('window.__loaded === true', timeout=30000)
        pg.wait_for_function("__nbd.game.scene==='scoot' && __nbd.SC.phase==='ride'", timeout=30000); time.sleep(0.3)
        r = pg.evaluate("({id:__nbd.W.heroes[0].id, said:(__nbd.W.said||[]).slice(), start:__nbd.W.heroes[0].d.scoot.start})")
        check('Scooter Run: Heather rides a scooter', r['id'] == 'heather', r['id'])
        check('...with her own snarky start line', any(x in r['start'] for x in r['said']), r['said'])
        pg.screenshot(path='tests/out/v10_scooter.png')
        n0 = pg.evaluate("__nbd.SC.shots ? __nbd.SC.shots.length : 0")
        pg.evaluate("__nbd.scootSpawn('wander', 120, 0, 0)"); key(pg, 'KeyJ', 0.06, 0.05)
        fire = pg.evaluate("__nbd.W.heroes[0].sc.fire")
        check('ATTACK fires an Ativan syringe (shoot pose)', fire > 0, fire)
        seat = pg.evaluate(BOUNDS + "('heather','scoot')"); stand = pg.evaluate(BOUNDS + "('heather','idle')")
        c = pg.evaluate(COLS + "('heather','scoot',0,[%r,%r,%r])" % (TOP, PANTS, HAIR))
        check('she sits on the scooter (seated frame shorter) in her royal blue top + pants', seat[1] < stand[1] * 0.92 and c[TOP]['n'] > 30 and c[PANTS]['n'] > 30 and c[HAIR]['n'] > 30, [seat[1], stand[1], {k: v['n'] for k, v in c.items()}])
        talk = pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.sayS='Ow! Incident report!'; h.sayUntil=__nbd.W.t+2; __nbd.SC.tip={s:'TEST TIP', t:0}; return 1})()"); time.sleep(0.2)
        check('tip banners wait while she is talking (no overlap with her bubble)', pg.evaluate("__nbd.SC.talk === true && __nbd.SC.tip && __nbd.SC.tip.t === 0"))
        pg.close()
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?noalarm=1'); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.6)
        pg.evaluate("(()=>{__nbd.toSelect(2); const S=__nbd.game.sel; S.p[0].cur=5; S.p[0].locked=true; S.p.push({dev:'kb2', cur:4, locked:true}); __nbd.startGame();})()")
        pg.wait_for_function("__nbd.W.heroes.length===2", timeout=20000); pg.evaluate("__nbd.game.cut=null; __nbd.game.cutDone=null; __nbd.scooter()")
        pg.wait_for_function("__nbd.game.scene==='scoot' && __nbd.SC.phase==='ride'", timeout=30000); time.sleep(0.6)
        ids = pg.evaluate("__nbd.W.heroes.map(h=>[h.id, h.sc && h.sc.col])")
        check('2P Scooter Run: Heather (red) + Nate (blue)', ids == [['heather', 'red'], ['nate', 'blue']], ids)
        pg.screenshot(path='tests/out/v10_scooter_2p.png')
        pg.close()
    # ================================================================ J: cutscenes + ending with Heather
    if 'J' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=heather&god=1&noalarm=1&cuts=1'); pg.wait_for_function("window.__loaded===true", timeout=30000)
        pg.wait_for_function("__nbd.game.scene==='cutscene'", timeout=30000)
        txt = pg.evaluate("__nbd.game.cut.panels.map(f => (f(398, 160).bubbles || []).map(b => b.s)).flat()")
        check('opening cutscene: Heather gets her own snarky line', any("not your track coach" in t for t in txt), txt[:3])
        acts = pg.evaluate("__nbd.game.cut.panels[0](398,160).acts.map(a=>a.s)")
        check('...and appears in the panel', 'heather' in acts, acts)
        pg.wait_for_function("__nbd.game.scene==='cutscene' && __nbd.game.cut.lastPanel===1", timeout=30000); time.sleep(1.6)
        pg.screenshot(path='tests/out/v10_cut.png')
        T = pg.evaluate("""(async()=>{const m=await import('./src/cutscene.js'); const o={}; for (const id of ['boss','lunch','next','mri','scoot','night','ending']) o[id]=m.makeCut(id).panels.map(f=>(f(398,160).bubbles||[]).map(b=>b.s)).flat(); return o;})()""")
        snark = {'lunch': 'ice chips', 'next': "Nobody's charting", 'scoot': 'not your chauffeur', 'night': 'ice chip', 'ending': "Here's a rag"}
        check('her takes in the lunch / Radiology / scooter / night / ending cutscenes', all(any(v in s for s in T[k]) for k, v in snark.items()), {k: [s for s in T[k] if v in s] for k, v in snark.items()})
        pg.evaluate("(()=>{__nbd.game.cut=null; __nbd.game.scene='ending'; __nbd.game.t=2;})()"); time.sleep(0.5)
        pg.screenshot(path='tests/out/v10_ending.png')
        hair = pg.evaluate(SCREEN_COUNT + "('%s')" % HAIR)
        check('THE END screen shows Heather (portrait)', hair > 20, hair)
        pg.close()
    # ================================================================ K: moves sanity (jump, kick, run/dash, grab/toss/slam, weapon) as Heather
    if 'K' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=heather&god=1&nocut=1&noalarm=1'); ready(pg); pg.evaluate(FREEZE); time.sleep(0.2)
        key(pg, 'KeyK'); time.sleep(0.1); j = pg.evaluate("__nbd.W.heroes[0].st"); key(pg, 'KeyJ', after=0.05); jk = pg.evaluate("__nbd.W.heroes[0].kicked"); time.sleep(0.9)
        check('jump + jump kick', j == 'jump' and jk, [j, jk])
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2); foe(pg, 'wanderer', 14); time.sleep(0.05)
        key(pg, 'KeyH', after=0.15); g = pg.evaluate("__nbd.W.heroes[0].st"); key(pg, 'KeyA', 0.5, 0.6)
        r = pg.evaluate("({slams:__nbd.W.stats.slams||0, st:F[0].st})")
        check('GRAB then away = body slam', g == 'grab' and r['slams'] >= 1, [g, r])
        pg.evaluate(FREEZE); time.sleep(0.2)
        pg.keyboard.down('ShiftLeft'); pg.keyboard.down('KeyD'); time.sleep(0.3); rs = pg.evaluate("__nbd.W.heroes[0].st"); key(pg, 'KeyJ', after=0.05); ds = pg.evaluate("__nbd.W.heroes[0].st"); pg.keyboard.up('KeyD'); pg.keyboard.up('ShiftLeft'); time.sleep(0.6)
        check('run + dash attack', rs == 'run' and ds == 'dash', [rs, ds])
        pg.close()
    b.close()
print('ALL PASS' if ok else 'SOME FAILED')
print('\n'.join(errs[:30]) or 'no console errors')
