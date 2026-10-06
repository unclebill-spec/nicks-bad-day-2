# v0.8: NASTY NATE, the 5th nurse: five-card select on desktop + phones (keyboard / touch / pad / 2P), tall-but-staff-sized,
# plain scrubs, lazy stats (long reach, slow), his own combo (lz1-3) and ROLLING CHAIR special, speech bubbles with Bill's exact
# lines (spawn / idle / grab / items / hurt / Ativan / Code Blue / revive / floor clear), cutscene, MRI frost-puff headroom.
# Screenshots -> tests/out/v08_*.png (+ docs/v08_select.png, docs/v08_select_phone.png)
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
ONLY = sys.argv[1:] or list('ABCDEFGH')
DOWN = ('fall', 'down', 'getup', 'dead', 'thrown')
EXACT = ['You made me get up from my chair.', 'I was playing a game on my phone.', 'Oh btw, your IVs are all blown.']
SAY = "(()=>{const h=__nbd.W.heroes[%d]; return {s:h.sayS, said:(__nbd.W.said||[]).slice(), st:h.st, lines:h.d.lines};})()"
def say(pg, i=0): return pg.evaluate(SAY % i)
def lines(pg, ev): return pg.evaluate(f"__nbd.W.heroes[0].d.lines['{ev}']")
def recd(pg): pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.sayCd=0; h.sayS=null; __nbd.W.said=[];})()")
def no_overlap(R, VW, VH):
    for i, a in enumerate(R):
        if a[0] < 0 or a[1] < 0 or a[0] + a[2] > VW or a[1] + a[3] > VH: return False
        for c in R[i + 1:]:
            if a[0] < c[0] + c[2] and c[0] < a[0] + a[2] and a[1] < c[1] + c[3] and c[1] < a[1] + a[3]: return False
    return True
UA = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36'
with sync_playwright() as p:
    b = p.chromium.launch()
    # ================================================================ A: five-card select (desktop, keyboard), title with 5 nurses
    if 'A' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(1.0)
        n = pg.evaluate("__nbd.game.scene==='title' && (()=>{const c=document.querySelector('canvas'); return 1})()")
        teal = pg.evaluate("""(()=>{const c=__nbd.G.view, x=c.getContext('2d'), d=x.getImageData(0,0,c.width,c.height).data; let n=0;
            for (let i=0;i<d.length;i+=4) if (d[i]===0x1f && d[i+1]===0x7a && d[i+2]===0x80) n++; return n;})()""")
        check('title: Nate (teal scrubs) stands with the other four nurses', teal > 20, teal)
        pg.screenshot(path='tests/out/v08_title.png')
        key(pg, 'Enter', after=0.5)
        sel = pg.evaluate("[__nbd.game.scene, __nbd.G.VW, __nbd.G.VH, __nbd.game.cardRects]")
        check('select shows 5+ cards inside the 398x224 view, no overlaps (v0.10: 6)', sel[0] == 'select' and len(sel[3]) >= 5 and no_overlap(sel[3], sel[1], sel[2]), sel)
        for k in range(4): key(pg, 'KeyD', after=0.12)
        c1 = pg.evaluate('__nbd.game.sel.p[0].cur'); key(pg, 'KeyD', after=0.12); c2 = pg.evaluate('__nbd.game.sel.p[0].cur'); key(pg, 'KeyA', after=0.12); c3 = pg.evaluate('__nbd.game.sel.p[0].cur')
        check('keyboard: right x4 reaches NASTY NATE, on to the next card and back (v0.10: Heather is 6th)', (c1, c2, c3) == (4, 5, 4), (c1, c2, c3))
        time.sleep(0.4); pg.screenshot(path='docs/v08_select.png'); pg.screenshot(path='tests/out/v08_select.png')
        key(pg, 'KeyJ', after=0.4); key(pg, 'Enter', after=0.6)
        pg.wait_for_function("__nbd.game.scene==='cutscene' || __nbd.game.scene==='play'", timeout=20000); time.sleep(1.5)
        pg.screenshot(path='tests/out/v08_cut.png')
        for k in range(8):
            if pg.evaluate("__nbd.game.scene") == 'play': break
            key(pg, 'KeyK', after=0.6)
        pg.wait_for_function("__nbd.game.scene==='play' && __nbd.W.heroes.length>0", timeout=30000)
        check('picking the 5th card starts the shift as Nate', pg.evaluate('__nbd.W.heroes[0].id') == 'nate')
        pg.close()
    # ================================================================ B: phone: 5 cards fit, tap Nate's card twice, touch SP / GRAB
    if 'B' in ONLY:
        for (vw, vh) in ((915, 412), (844, 390), (667, 375)):
            ctx = b.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=2.6, is_mobile=True, has_touch=True, user_agent=UA)
            pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg); watch(pg)
            def touch(kind, pts): cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [{'x': x, 'y': y, 'id': i} for i, x, y in pts]})
            def tapxy(x, y): touch('touchStart', [(9, x, y)]); time.sleep(0.06); touch('touchEnd', []); time.sleep(0.25)
            def L2C(lx, ly):
                r = pg.evaluate("(() => { const r = __nbd.G.view.getBoundingClientRect(); return [r.left, r.top, r.width, r.height, __nbd.G.VW, __nbd.G.VH]; })()")
                return r[0] + lx / r[4] * r[2], r[1] + ly / r[5] * r[3]
            pg.goto(U); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.8)
            m = pg.evaluate('__nbd.game.menu.rects[0]'); tapxy(*L2C(m[0] + m[2] / 2, m[1] + m[3] / 2)); time.sleep(0.4)
            sel = pg.evaluate("[__nbd.game.scene, __nbd.G.VW, __nbd.G.VH, __nbd.game.cardRects]")
            check(f'phone {vw}x{vh}: 5+ cards fit on screen, no overlaps', sel[0] == 'select' and len(sel[3]) >= 5 and no_overlap(sel[3], sel[1], sel[2]), sel[1:3] + [sel[3][4] if len(sel[3]) > 4 else None])
            c = sel[3][4]; x, y = L2C(c[0] + c[2] / 2, c[1] + c[3] / 2); tapxy(x, y)
            if vw == 915: time.sleep(0.3); pg.screenshot(path='tests/out/v08_select_phone.png'); pg.screenshot(path='docs/v08_select_phone.png')
            tapxy(x, y); time.sleep(1.0)
            for k in range(6):
                if pg.evaluate("__nbd.game.scene") == 'play': break
                tapxy(*L2C(150, 100)); time.sleep(0.8)
            pg.wait_for_function("__nbd.game.scene==='play' && __nbd.W.heroes.length>0 && __nbd.W.heroes[0].st==='idle'", timeout=30000)
            check(f'phone {vw}x{vh}: double-tap on the Nate card plays as Nate', pg.evaluate('__nbd.W.heroes[0].id') == 'nate')
            if vw == 915:
                pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2)
                def btn(name): bx = pg.locator(f'#pad .ab[data-b={name}]').bounding_box(); return bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2
                foe(pg, 'wanderer', 40, st='dizzy'); time.sleep(0.05)
                ax_, ay_ = btn('atk'); tapxy(ax_, ay_); time.sleep(0.05)
                f = pg.evaluate("F[0].hp < F[0].maxHp || F[0].st!=='dizzy'")
                check('touch ATK: Nate\'s long backhand reaches a patient 40 px away', f)
                pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2)
                sx, sy = btn('sp'); tapxy(sx, sy); time.sleep(0.05)
                check('touch SP: ROLLING CHAIR', pg.evaluate('__nbd.W.heroes[0].st') == 'special')
            ctx.close()
    # ================================================================ C: gamepad select + pad play
    if 'C' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg); pg.add_init_script(MOCK)
        pg.goto(U); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.6); pg.evaluate('__padConnect()'); time.sleep(0.3)
        def pb(i, hold=0.1, after=0.18): pg.evaluate(f'__padSet({i}, true)'); time.sleep(hold); pg.evaluate(f'__padSet({i}, false)'); time.sleep(after)
        pg.evaluate('__nbd.toSelect(1)'); time.sleep(0.4)
        pb(14); pb(14); c1 = pg.evaluate('__nbd.game.sel.p[0].cur')  # d-pad left from Nick wraps to the last card (v0.10 Heather), once more = Nate
        check('pad: d-pad left from Nick wraps round to NASTY NATE', c1 == 4, c1)
        pb(0, after=0.6)
        pg.wait_for_function("__nbd.game.scene==='cutscene' || __nbd.game.scene==='play'", timeout=20000)
        for k in range(8):
            if pg.evaluate("__nbd.game.scene") == 'play': break
            pb(0, after=0.6)
        pg.wait_for_function("__nbd.game.scene==='play' && __nbd.W.heroes.length>0 && __nbd.W.heroes[0].st==='idle'", timeout=30000)
        check('pad: A locks Nate in and starts', pg.evaluate('__nbd.W.heroes[0].id') == 'nate')
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2)
        pb(3, after=0.05); check('pad: Y = ROLLING CHAIR', pg.evaluate('__nbd.W.heroes[0].st') == 'special')
        pg.close()
    # ================================================================ D: size, art, stats (tall but staff-sized, plain scrubs)
    if 'D' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=nate&god=1&nocut=1&noalarm=1'); ready(pg)
        size = lambda n: pg.evaluate(BOUNDS + f"('{n}','walk')")
        nurses = {n: size(n) for n in ('nick', 'kim', 'will', 'jackie')}; nate = size('nate')
        avg = sum(v[1] for v in nurses.values()) / 4; mx = max(v[1] for v in nurses.values())
        check('Nate is the tallest nurse but still staff-sized (<= 1.15x the nurse average)', mx < nate[1] <= avg * 1.15, {'nate': nate[1], 'max': mx, 'avg': round(avg, 1)})
        check('Nate is slim (not wider than Nick: plain scrubs, no padding)', nate[0] <= nurses['nick'][0] + 2, {'nate_w': nate[0], 'nick_w': nurses['nick'][0]})
        sp = pg.evaluate("['face_nate','face_nate_hurt','chair0','chair1'].map(k => !!__nbd.G.atlas.sprites.rects[k])")
        check('HUD portraits + chair sprites exist', all(sp), sp)
        d = pg.evaluate("(()=>{const H=__nbd.W.heroes[0].d, N=%s; return {walk:H.walk, reach:H.reach, atkK:H.atkK, combo:H.combo, special:H.special, nick:N}})()" % "({walk:72, reach:1.0})")
        check('lazy stats: longest reach, slowest walk, slower swings', d['reach'] >= 1.4 and d['walk'] < 58 and d['atkK'] > 1.1, d)
        check('own combo and special', d['combo'] == ['lz1', 'lz2', 'lz3'] and d['special'] == 'ROLLING CHAIR', d)
        hud = pg.evaluate("__nbd.W.heroes[0].d.short")
        check('HUD name fits (NATE)', hud == 'NATE', hud)
        pg.close()
    # ================================================================ E: combo, reach, special (keyboard)
    if 'E' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=nate&god=1&nocut=1&noalarm=1'); ready(pg); pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2)
        foe(pg, 'wanderer', 44, st='dizzy'); time.sleep(0.05)
        pg.evaluate("window.AN=[]; window.__anT=setInterval(()=>{const h=__nbd.W.heroes[0]; if(h.st==='atk' && AN[AN.length-1]!==h.atkName) AN.push(h.atkName)},10)")
        for k in range(3): key(pg, 'KeyJ', 0.06, 0.2)
        time.sleep(0.9); an = pg.evaluate("clearInterval(__anT), AN"); f = pg.evaluate("({hp:F[0].hp, max:F[0].maxHp, st:F[0].st})")
        check('combo: lazy backhand -> palm shove -> push-kick', an[:3] == ['lz1', 'lz2', 'lz3'], an)
        check('reach: hits land from 44 px away (Nick reaches ~30)', f['hp'] < f['max'], f)
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2)
        foe(pg, 'crutch', 70, st='dizzy'); foe(pg, 'wanderer', 110, st='dizzy'); time.sleep(0.05)
        x0 = pg.evaluate('__nbd.W.heroes[0].x'); hp0 = pg.evaluate('__nbd.W.heroes[0].hp')
        key(pg, 'KeyL', after=0.4); st = pg.evaluate('__nbd.W.heroes[0].st')
        pg.screenshot(path='tests/out/v08_chair.png'); time.sleep(1.0)
        r = pg.evaluate("({x:__nbd.W.heroes[0].x, st:__nbd.W.heroes[0].st, hp:__nbd.W.heroes[0].hp, foes:F.map(e=>e.st)})")
        check('special: ROLLING CHAIR rolls him forward', st == 'special' and r['x'] - x0 > 90, {'st': st, 'dx': round(r['x'] - x0)})
        check('special: plows both patients over', all(s in DOWN for s in r['foes']), r['foes'])
        pg.close()
    # ================================================================ F: speech bubbles + Bill's exact lines + lazy Ativan + Code Blue
    if 'F' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=nate&god=1&nocut=1&noalarm=1'); ready(pg)
        r = say(pg)
        check('spawn: "You made me get up from my chair."', EXACT[0] in r['said'], r['said'])
        allL = sum(r['lines'].values(), [])
        check("all of Bill's exact lines are in Nate's script", all(e in allL for e in EXACT), [e for e in EXACT if e not in allL])
        extra = ['Is it time for my break yet?', "I'm not charting that.", 'Ugh, call bells.']
        check('plus the lazy extras', all(e in allL for e in extra))
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); recd(pg); time.sleep(0.2)
        try: pg.wait_for_function("(()=>{const h=__nbd.W.heroes[0]; return !!h.sayS && h.d.lines.idle.includes(h.sayS)})()", timeout=15000)
        except Exception: pass
        r = say(pg); r['idleT'] = pg.evaluate('__nbd.W.heroes[0].idleT')
        check('idle ~6 s: a lazy line (phone / break / call bells)', r['s'] in lines(pg, 'idle'), [r['s'], r['st'], r['idleT']])
        pg.screenshot(path='tests/out/v08_idle.png')
        # grab: both grab lines show up over a few grabs (one is "Oh btw, your IVs are all blown.")
        seen = set()
        for k in range(6):
            pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); recd(pg); time.sleep(0.1); foe(pg, 'wanderer', 14); time.sleep(0.05)
            key(pg, 'KeyH', after=0.15); seen.add(say(pg)['s'])
            if EXACT[2] in seen: break
        check('grab: "Oh btw, your IVs are all blown."', EXACT[2] in seen, seen)
        pg.screenshot(path='tests/out/v08_grab.png')
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); recd(pg); time.sleep(0.1)
        pg.evaluate("__nbd.drop('jerky')"); time.sleep(0.3); r = say(pg)
        check('food pickup: break / snack line', r['s'] in lines(pg, 'food'), r['s'])
        recd(pg); pg.evaluate("__nbd.drop('w:mop')"); time.sleep(0.1); key(pg, 'KeyH', after=0.5); r = say(pg)
        check('weapon pickup: "I\'m not charting that." / "Ugh, fine."', r['s'] in lines(pg, 'weapon'), r['s'])
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); recd(pg); time.sleep(0.1)
        pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.inv=0; h.takeHit({dmg:4, dir:1, kb:10, stun:0.2})})()"); r = say(pg)
        check('taking damage: a lazy complaint', r['s'] in lines(pg, 'hurt'), r['s'])
        time.sleep(0.6); recd(pg); foe(pg, 'wanderer', 30, st='dizzy'); time.sleep(0.05)
        pg.evaluate("__nbd.W.heroes[0].meter = 40"); key(pg, 'KeyL', after=0.3)
        r = pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; return {st:h.st, shout:h.shoutT>__nbd.W.t, words:h.d.shout, snd:h.d.ativanSfx, buf:!!(__nbd.sound ? 1 : 1)}})()")
        check('Ativan: his own lazy shout bubble + slower voice clip', r['st'] == 'ativan' and r['shout'] and 'ATIVAN' in ' '.join(r['words']) and 'UGH' in r['words'][0] and r['snd'] == 'ativan_nate', r)
        pg.screenshot(path='tests/out/v08_ativan.png'); time.sleep(1.6)
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); recd(pg); time.sleep(0.2); foe(pg, 'wanderer', 60, st='dizzy')
        pg.evaluate("__nbd.W.heroes[0].meter = 100"); key(pg, 'KeyL', after=0.3); r = say(pg)
        check('Code Blue: "Fine. CODE BLUE. Happy?"-style line', r['st'] == 'super' and r['s'] in lines(pg, 'codeblue'), r)
        pg.screenshot(path='tests/out/v08_codeblue.png'); time.sleep(2.5)
        recd(pg); pg.evaluate("__nbd.W.heroes[0].respawn()"); r = say(pg)
        check('revive / continue: back in the chair line', r['s'] in lines(pg, 'revive'), r['s'])
        time.sleep(1.5)
        recd(pg); pg.evaluate("__nbd.W.cleared = true"); pg.wait_for_function("__nbd.game.scene==='tally'", timeout=10000); time.sleep(1.2)
        q = pg.evaluate("__nbd.game.tally[0].quote")
        check('floor clear: he signs off on the tally card', q in lines(pg, 'clear'), q)
        pg.screenshot(path='tests/out/v08_tally.png')
        pg.close()
    # ================================================================ G: 2P keyboard with Nate as P2
    if 'G' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?noalarm=1'); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.8)
        key(pg, 'KeyS'); key(pg, 'Enter', after=0.4); key(pg, 'Comma', after=0.3)
        c0 = pg.evaluate('__nbd.game.sel.p.length>1 && __nbd.game.sel.p[1].cur')
        key(pg, 'KeyJ', after=0.3); key(pg, 'ArrowLeft'); key(pg, 'ArrowLeft'); key(pg, 'ArrowLeft')
        c = pg.evaluate('__nbd.game.sel.p[1].cur')
        check('2P select: P2 (arrows) wraps left to NASTY NATE', c0 == 1 and c == 4, (c0, c))
        pg.screenshot(path='tests/out/v08_select_2p.png')
        key(pg, 'Comma', after=1.2)
        for k in range(8):
            if pg.evaluate("__nbd.game.scene") == 'play': break
            key(pg, 'KeyK', after=0.6)
        pg.wait_for_function("__nbd.game.scene==='play' && __nbd.W.heroes.length===2 && __nbd.W.heroes[1].st==='idle'", timeout=30000); time.sleep(0.3)
        ids = pg.evaluate('__nbd.W.heroes.map(h=>h.id)')
        check('2P: Nick (P1) + Nate (P2)', ids == ['nick', 'nate'], ids)
        check('2P: Nate says his spawn line', EXACT[0] in (pg.evaluate('__nbd.W.said') or []))
        pg.evaluate(FREEZE); time.sleep(0.2)
        pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[1]; const e=__nbd.spawn('wanderer','R'); e.x=h.x+44; e.y=h.y; e.tx=e.x; e.ty=e.y; e.set('dizzy'); e.cd=99; e.atkCd=99; window.F=[e];})()")
        key(pg, 'Comma', 0.06, 0.4)
        check('2P: Nate (P2, Comma) attacks with his reach', pg.evaluate("F[0].hp < F[0].maxHp"))
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2)
        key(pg, 'Slash', after=0.2); check('2P: Nate (P2, Slash) ROLLING CHAIR', pg.evaluate('__nbd.W.heroes[1].st') == 'special')
        time.sleep(1.4); pg.screenshot(path='tests/out/v08_2p.png')
        pg.close()
    # ================================================================ H: cutscene + MRI frost puff headroom
    if 'H' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=nate&god=1&noalarm=1&cuts=1'); pg.wait_for_function("window.__loaded===true", timeout=30000)
        pg.wait_for_function("__nbd.game.scene==='cutscene'", timeout=30000)
        txt = pg.evaluate("__nbd.game.cut.panels.map(f => (f(398, 160).bubbles || []).map(b => b.s)).flat()")
        check('opening cutscene: Nate gets his lazy line', any('I was playing a game on my phone' in t for t in txt), txt[:3])
        pg.wait_for_function("__nbd.game.scene==='cutscene' && __nbd.game.cut.lastPanel===1", timeout=30000); time.sleep(1.6)
        pg.screenshot(path='tests/out/v08_cut_nate.png')
        top = pg.evaluate("""(()=>{const G=__nbd.G, A=G.atlas.chars.mri, [cw,ch]=A.cell, i=A.anims.vent.s, sx=(i%A.cols)*cw, sy=Math.floor(i/A.cols)*ch;
          const c=document.createElement('canvas'); c.width=cw; c.height=ch; const x=c.getContext('2d'); x.drawImage(G.img.mri, sx, sy, cw, ch, 0, 0, cw, ch);
          const d=x.getImageData(0,0,cw,ch).data; for (let y=0;y<ch;y++) for (let k=0;k<cw;k++) if (d[(y*cw+k)*4+3]>20) return y; return -1;})()""")
        check('MRI vent frost puff has headroom (not cut off at the top of its cell)', top >= 2, top)
        pg.close()
    b.close()
print('ALL PASS' if ok else 'SOME FAILED')
print('\n'.join(errs[:30]) or 'no console errors')
