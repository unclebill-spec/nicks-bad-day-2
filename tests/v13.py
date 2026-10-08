# v0.13: FLOOR 5, THE PSYCH WARD (after the Scooter Run, before the Night Shift) + GREG + "DR." PHIL-IN.
# A data/art/sizes + Bill's Greg lines, B level look + blackouts + props, C ward patients + Greg (croon, pillow boomerang,
# grab line), D nurses' ward lines, E boss, F flow + cutscenes + level select, G drops/Ativan/Code Blue/grab/fire alarm,
# H 2P + pad + phone. Usage: python3 tests/v13.py [A B ...]. Screenshots -> tests/out/v13_*.png
import time, sys
from playwright.sync_api import sync_playwright
U = 'http://localhost:8731/'; errs = []; fails = []
ONLY = sys.argv[1:] or list('ABCDEFGH')
def check(n, c, info=''):
    print(('PASS ' if c else 'FAIL ') + n, '' if c else info); (None if c else fails.append(n))
def key(pg, k, hold=0.08, after=0.12): pg.keyboard.down(k); time.sleep(hold); pg.keyboard.up(k); time.sleep(after)
def page(b, q, w=960, h=540):
    pg = b.new_page(viewport={'width': w, 'height': h}); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.goto(U + q); pg.wait_for_function('window.__loaded === true', timeout=30000); return pg
SC = '__nbd.game.scene'
FREEZE = "(()=>{const W=__nbd.W; W.enemies.forEach(e=>{e.alive=false}); W.enemies.length=0; W.queue && (W.queue.length=0); W.items.length=0; W.shots.length=0; W.zone=99; W.zoneOn=false; W.lockX=W.camX; W.cars=[]; W.carAlarms=[]; W.carNext=999; W.heroes.forEach((h,i)=>{h.x=W.camX+150; h.y=176+i*20; h.z=0; h.vz=0; h.inv=0; h.face=1; h.carry=null; h.weapon=null; h.held=null; h.ride=null; h.set('idle');}); W.props=W.props.filter(p=>p.x<W.camX-60||p.x>W.camX+__nbd.G.VW+60);})()"
UA = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36'
DOWN = ('fall', 'down', 'getup', 'dead', 'thrown')
MOCK = """(() => { const pad = { id: 'Xbox Wireless Controller (STANDARD GAMEPAD)', index: 0, connected: true, mapping: 'standard', timestamp: 0,
  axes: [0, 0, 0, 0], buttons: Array.from({ length: 17 }, () => ({ pressed: false, value: 0, touched: false })) };
  window.__pad = pad; navigator.getGamepads = () => [window.__padOn ? pad : null, null, null, null];
  window.__padSet = (i, on) => { pad.buttons[i].pressed = on; pad.buttons[i].value = on ? 1 : 0; pad.timestamp++; };
  window.__padConnect = () => { window.__padOn = true; const e = new Event('gamepadconnected'); e.gamepad = pad; dispatchEvent(e); }; })();"""
def ready(pg):
    pg.wait_for_function(f"window.__nbd && {SC}==='play' && __nbd.W.heroes.length>0 && __nbd.W.heroes[0].st==='idle'", timeout=30000); time.sleep(0.3)
def foe(pg, kind, dx, dy=0, st='idle'):
    return pg.evaluate(f"(()=>{{const W=__nbd.W,h=W.heroes[0]; const e=__nbd.spawn('{kind}','R'); e.x=h.x+{dx}; e.y=h.y+{dy}; e.tx=e.x; e.ty=e.y; e.set('{st}'); e.cd=99; e.atkCd=99; window.F=window.F||[]; F.push(e); return F.length-1;}})()")
def prop(pg, kind, dx, dy=0):
    return pg.evaluate(f"(()=>{{const W=__nbd.W,h=W.heroes[0]; const i=__nbd.prop('{kind}',0,0); const p=W.props[i]; p.x=h.x+{dx}; p.y=Math.max(136,Math.min(212,h.y+{dy})); return i;}})()")
BOUNDS = """((sheet, an) => { const G = __nbd.G, A = G.atlas.chars[sheet], [cw, ch] = A.cell, i = A.anims[an].s, sx = (i % A.cols) * cw, sy = Math.floor(i / A.cols) * ch;
  const c = document.createElement('canvas'); c.width = cw; c.height = ch; const x = c.getContext('2d'); x.drawImage(G.img[sheet], sx, sy, cw, ch, 0, 0, cw, ch);
  const d = x.getImageData(0, 0, cw, ch).data; let x0 = cw, x1 = 0, y0 = ch, y1 = 0, n = 0;
  for (let y = 0; y < ch; y++) for (let k = 0; k < cw; k++) if (d[(y * cw + k) * 4 + 3] > 20) { n++; x0 = Math.min(x0, k); x1 = Math.max(x1, k); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
  return [x1 - x0 + 1, y1 - y0 + 1, n]; })"""
FOE = "((k,dx,dy)=>{const h=__nbd.W.heroes[0]; const e=__nbd.spawn(k,'R'); e.x=h.x+dx; e.y=h.y+(dy||0); e.tx=e.x; e.ty=e.y; e.set('idle'); return __nbd.W.enemies.length-1;})"
with sync_playwright() as p:
    b = p.chromium.launch()
    if 'A' in ONLY:
        pg = page(b, '?level=5&hero=nick&god=1'); time.sleep(3.2)
        A = pg.evaluate("""(async()=>{const a=await (await fetch('art/atlas.json')).json(); const H=(n)=>{const c=a.chars[n]; return c? c.cell[1]:0};
          const m = await import('./src/data.js'); return {chars:['escapee','capeguy','tinfoil','puppet','greg','philin'].filter(n=>a.chars[n]),
          spr:['pwall0','pceil_lit','pfloor0','pwall_door','buzzer','nstation','tvcage','callstrip','foamchair0','puzzletable0','pillcart0','p_pillow','p_foil','face_philin','face_greg'].filter(n=>a.sprites.rects[n]).length,
          bill: m.GREG_BILL, greg: [...m.ENEMIES.greg.lines, ...m.ENEMIES.greg.grabLines], sing: m.ENEMIES.greg.sing, lv: m.LEVELS[4].name, ward: Object.keys(m.WARD_LINES)}})()""")
        check('six new sheets (5 ward patients incl. GREG + Dr. Phil-in)', len(A['chars']) == 6, A['chars'])
        check('ward tiles, wall pieces, props, projectiles, faces in the atlas', A['spr'] == 15, A['spr'])
        check("Bill's Greg lines are verbatim", all(l in A['greg'] for l in A['bill']) and len(A['bill']) == 5, A['greg'])
        check('Greg croons with music notes, no real lyric lines', all('\u266a' in s for s in A['sing']) and len(A['sing']) >= 4)
        check('LEVELS[4] is the psych ward, every nurse has ward lines', 'PSYCH WARD' in A['lv'] and len(A['ward']) == 6, A)
        hs = pg.evaluate("""(()=>{const s=(id)=>{const e=__nbd.spawn(id,'R'); return e.h};  return {nick: __nbd.W.heroes[0].h, greg: s('greg'), cape: s('capeguy')}})()""")
        check('Greg and the ward patients are staff-sized', abs(hs['greg'] - hs['nick']) <= 6 and abs(hs['cape'] - hs['nick']) <= 6, hs)
        pg.close()
    if 'B' in ONLY:
        pg = page(b, '?level=5&hero=jackie&god=1'); time.sleep(3.2)
        st = pg.evaluate("[__nbd.W.lv.id, __nbd.W.lv.ward, __nbd.W.lights.length, (__nbd.W.alarms||[]).length, __nbd.W.props.map(p=>p.kind)]")
        check('the ward loads (id 5) with glow lights and fire-alarm stations', st[0] == 5 and st[1] and st[2] > 20 and st[3] > 0, st[:4])
        check('props: foam chairs, puzzle tables, pill carts, linen hampers', all(k in st[4] for k in ('foamchair', 'puzzletable', 'pillcart', 'linen')))
        base = pg.evaluate("__nbd.W.dark"); pg.evaluate("__nbd.ward.blackout()"); time.sleep(0.9)
        dk = pg.evaluate("__nbd.W.dark"); pg.screenshot(path='tests/out/v13_blackout.png'); time.sleep(2.6)
        check('flicker blackout: the ward goes dark, then the lights come back', dk > 0.8 and pg.evaluate("__nbd.W.dark") <= base + 0.01, [base, dk, pg.evaluate("__nbd.W.dark")])
        i = pg.evaluate(f"(()=>{{const h=__nbd.W.heroes[0]; const p=__nbd.prop('puzzletable', 30, 0); for(let k=0;k<6;k++) __nbd.hitProp(__nbd.W.props[p], 9, {{dir:1, kb:160, from:h}}); return __nbd.W.props[p].st}})()")
        check('kick the puzzle table to pieces', i >= 2, i)
        pg.close()
    if 'C' in ONLY:
        pg = page(b, '?level=5&hero=will&god=1'); time.sleep(3.2)
        pg.evaluate("__nbd.W.enemies.length=0; __nbd.W.queue.length=0")
        gi = pg.evaluate(FOE + "('greg', 60)")
        s = pg.evaluate(f"__nbd.W.enemies[{gi}].croon()"); check('Greg croons a music-note bubble (+ synth hum)', '\u266a' in s, s)
        pg.evaluate(f"(()=>{{const g=__nbd.W.enemies[{gi}]; g.x=__nbd.W.heroes[0].x+110; g.throwKind='jello'; g.set('atk'); g.hitDone=false; g.t=0.05}})()"); time.sleep(0.25)
        sh = pg.evaluate("__nbd.W.shots.filter(s=>s.boom).map(s=>[s.spr, Math.round(s.vx)])")
        check('Greg throws his neck pillow (boomerang)', len(sh) >= 1 and sh[0][0] == 'p_pillow', sh)
        time.sleep(0.9); back = pg.evaluate(f"__nbd.W.shots.filter(s=>s.boom).map(s=>Math.sign(s.vx)===Math.sign(__nbd.W.enemies[{gi}].x-s.x))")
        check('...and it curves back to him', not back or all(back), back)
        pg.evaluate(f"(()=>{{const g=__nbd.W.enemies[{gi}], h=__nbd.W.heroes[0]; g.x=h.x+16; g.y=h.y; g.set('idle'); __nbd.W.said=[];}})()"); time.sleep(0.1)
        key(pg, 'KeyH', after=0.4)
        said = pg.evaluate("__nbd.W.said"); check("grab Greg -> \"Don't touch my dick!\"", "Don't touch my dick!" in said, said)
        for k in ('escapee', 'capeguy', 'tinfoil', 'puppet'):
            n = pg.evaluate(f"(()=>{{const i={FOE}('{k}', 70); const e=__nbd.W.enemies[i]; return [e.kind, e.d.lines.length, e.d.ko.length]}})()")
            check(f'{k}: AI {n[0]}, lines + sleepy KO lines', n[1] >= 3 and n[2] >= 2, n)
        pg.screenshot(path='tests/out/v13_patients.png'); pg.close()
    if 'D' in ONLY:
        res = {}
        for hero in ('nick', 'kim', 'will', 'jackie', 'nate', 'heather'):
            pg = page(b, f'?level=5&hero={hero}&god=1'); time.sleep(3.0)
            res[hero] = pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; const out=[]; for (let i=0;i<8;i++){ h.sayCd=0; const s=h.say('zone', true); if (s) out.push(s);} return [out, h.d.ward.zone]})()")
            check(f'{hero}: ward lines on the ward', any(s in res[hero][1] for s in res[hero][0]), res[hero])
            pg.close()
    if 'E' in ONLY:
        pg = page(b, '?level=5&zone=4&hero=kim&god=1&cuts=1')
        pg.wait_for_function(f"{SC}==='cutscene' || (__nbd.W.boss && __nbd.W.boss.name)", timeout=30000)
        check('a comic intro cutscene for Dr. Phil-in', pg.evaluate("__nbd.game.cut && __nbd.game.cut.id") == 'philin')
        time.sleep(3.4); pg.screenshot(path='tests/out/v13_cut_philin.png'); key(pg, 'KeyK', after=0.5)
        pg.wait_for_function("__nbd.W.boss && __nbd.W.boss.greeted", timeout=10000); time.sleep(0.3)
        B = pg.evaluate("(()=>{const B=window.B=__nbd.W.boss; const BD=" + BOUNDS + "; return {name:B.name, r:BD('philin','idle')[1]/BD('nick','idle')[1], said:__nbd.W.fx.filter(f=>f.type==='txt').map(f=>f.s), music:__nbd.W.lv.bossMusic};})()")
        check('"DR." PHIL-IN walks in: "I\'m the doctor here!" (1.2-1.5x a nurse)', 'PHIL-IN' in B['name'] and "I'm the doctor here!" in B['said'] and 1.2 <= B['r'] <= 1.5 and B['music'] == 'philin', B)
        pg.screenshot(path='tests/out/v13_philin_enter.png')
        n0 = pg.evaluate("__nbd.W.enemies.length")
        pg.evaluate("(()=>{B.set('write'); B.hitDone=false;})()"); time.sleep(1.4)
        w = pg.evaluate(f"[__nbd.W.stats.orders||0, __nbd.W.enemies.length-{n0}]")
        check('he writes orders and patients come running', w[0] >= 1 and w[1] >= 1, w)
        pg.evaluate("(()=>{__nbd.W.enemies.forEach(e=>{e.hp=0; e.st='dead'; e.alive=false}); const h=__nbd.W.heroes[0]; B.x=h.x+75; B.y=h.y; B.face=-1; B.set('lasso'); B.hitDone=false;})()"); time.sleep(1.1)
        check('stethoscope lasso yanks a nurse', pg.evaluate("__nbd.W.stats.lassoed||0") >= 1)
        pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; B.set('chase'); B.x=h.x+30; B.y=h.y; h.inv=0; B.set('swing'); B.hitDone=false;})()"); time.sleep(0.8)
        pg.evaluate("(()=>{B.hp=B.maxHp*0.45; B.takeHit({dmg:1, dir:1, from:__nbd.W.heroes[0], force:true}); B.set('chase'); B.cd=0;})()"); time.sleep(0.6)
        check('phase 2: STAT!', pg.evaluate("B.phase===2 && B.p2label==='STAT!'"))
        pg.evaluate("(()=>{B.set('chase'); B.hp=1; B.takeHit({dmg:5, dir:1, from:__nbd.W.heroes[0], force:true});})()"); time.sleep(0.8)
        d = pg.evaluate("({st:B.st, said:__nbd.W.fx.filter(f=>f.type==='txt').map(f=>f.s)})")
        check('defeat: he naps ("Discharge... me... zzz")', d['st'] == 'defeat' and any('Discharge' in s for s in d['said']), d)
        time.sleep(1.0); pg.screenshot(path='tests/out/v13_philin_ko.png')
        pg.wait_for_function(f"{SC}==='tally'", timeout=14000); time.sleep(3.4); key(pg, 'KeyJ', after=0.5)
        check('ward tally -> Phil-in outro cutscene', pg.evaluate("__nbd.game.cut && __nbd.game.cut.id") == 'psychout')
        time.sleep(2.5); pg.screenshot(path='tests/out/v13_cut_out.png')
        for _ in range(3): key(pg, 'KeyK', after=0.6)
        pg.wait_for_function("__nbd.game.cut && __nbd.game.cut.id==='night' || (__nbd.W.lv && __nbd.W.lv.id===3)", timeout=8000)
        check('-> on to the night shift', True)
        pg.close()
    if 'F' in ONLY:
        pg = page(b, '?level=2&hero=nick&god=1&cuts=1'); time.sleep(2.5)
        T = pg.evaluate("(async()=>{const m=await import('./src/cutscene.js'); const o={}; for (const id of ['psych','philin','psychout']) o[id]=m.makeCut(id).panels.map(f=>(f(398,160).bubbles||[]).map(b=>b.s)).flat(); return o;})()")
        check('psych intro: Greg asks "Wanna get outta here?"', 'Wanna get outta here?' in T['psych'], T['psych'])
        check('boss intro: "Nurse, I\'m ordering 10 of Dilaudid!"', "Nurse, I'm ordering 10 of Dilaudid!" in T['philin'], T['philin'])
        pg.evaluate("__nbd.goPsych()"); time.sleep(0.3)
        check('scooter tally -> psych cutscene', pg.evaluate("__nbd.game.cut && __nbd.game.cut.id") == 'psych')
        time.sleep(3.6); pg.screenshot(path='tests/out/v13_cut_psych.png')
        for _ in range(4): key(pg, 'KeyK', after=0.6)
        pg.wait_for_function("__nbd.W.lv && __nbd.W.lv.id===5", timeout=8000)
        check('-> the psych ward loads', pg.evaluate("__nbd.W.lv.name").startswith('FLOOR 5'))
        pg.close()
    if 'G' in ONLY:
        pg = page(b, '?level=5&nocut=1&hero=nick'); ready(pg); pg.evaluate(FREEZE); time.sleep(0.2)
        got = []
        for k in ('pizza', 'jerky', 'energy', 'snacks', 'zynn'):
            pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.hp=20; window.L0=h.lives;})()"); pg.evaluate(f"__nbd.drop('{k}')"); time.sleep(0.4)
            r = pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; return {hp:h.hp, lives:h.lives};})()")
            got.append([k, r['hp'] > 20 or r['lives'] > pg.evaluate('L0')]); pg.evaluate("__nbd.W.items.length=0")
        check('all five drops work on the ward', all(g[1] for g in got), got)
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2); foe(pg, 'capeguy', 26)
        pg.evaluate("__nbd.W.heroes[0].meter=40"); key(pg, 'KeyL', after=0.7)
        check('Ativan puts the blanket-cape hero to sleep', pg.evaluate("F[0].sleepT > __nbd.W.t || F[0].st==='down' || F[0].st==='sleep'"), pg.evaluate("F[0].st"))
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2); foe(pg, 'tinfoil', 60); foe(pg, 'greg', 120)
        pg.evaluate("__nbd.W.heroes[0].meter=100"); key(pg, 'KeyL', after=1.6)
        check('Code Blue zaps the tinfoil guy and Greg', all(s in DOWN or s == 'zapped' for s in pg.evaluate("F.map(e=>e.st)")), pg.evaluate("F.map(e=>e.st)"))
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2); foe(pg, 'puppet', 18, st='dizzy'); time.sleep(0.05)
        key(pg, 'KeyH', after=0.3); g = pg.evaluate("!!__nbd.W.heroes[0].held"); key(pg, 'KeyD', 0.05, 0.0); key(pg, 'KeyJ', after=0.8)
        check('grab + toss the sock-puppet guy', g and pg.evaluate("F[0].st") in DOWN, [g, pg.evaluate("F[0].st")])
        pg.evaluate(FREEZE); time.sleep(0.2); prop(pg, 'linen', 16); time.sleep(0.05)
        key(pg, 'KeyH', after=0.4); c = pg.evaluate("__nbd.W.heroes[0].carry ? __nbd.W.heroes[0].carry.kind : null")
        check('pick up a linen hamper to throw', c == 'linen', c)
        pg.close()
        pg = page(b, '?level=5&nocut=1&hero=kim&god=1'); ready(pg)
        a = pg.evaluate("(async()=>{const m=await import('./src/alarm.js'); const W=__nbd.W; const ok=m.pullAlarm(W.alarms[0], W.heroes[0]); await new Promise(r=>setTimeout(r,1500)); return [ok, !!W.alarm, W.alarms.length];})()")
        check('the fire alarm works on the ward (pull -> alarm)', a[0] is not False and a[1] and a[2] > 0, a)
        pg.screenshot(path='tests/out/v13_alarm.png'); pg.close()
    if 'H' in ONLY:
        pg = page(b, '?level=5&nocut=1'); time.sleep(0.5)
        pg.evaluate("(()=>{__nbd.toSelect(2); const S=__nbd.game.sel; S.p[0].cur=1; S.p[0].locked=true; S.p.push({dev:'kb2', cur:3, locked:true}); __nbd.startGame();})()")
        pg.wait_for_function(f"{SC}==='play' && __nbd.W.heroes.length===2 && __nbd.W.heroes[1].st==='idle'", timeout=30000); time.sleep(0.3)
        ids = pg.evaluate("[__nbd.W.lv.id, ...__nbd.W.heroes.map(h=>h.id)]"); check('2P on the ward', ids[0] == 5 and len(ids) == 3, ids)
        pg.evaluate(FREEZE); time.sleep(0.2)
        pg.evaluate("(()=>{const h=__nbd.W.heroes[1]; const e=__nbd.spawn('escapee','R'); e.x=h.x+26; e.y=h.y; e.tx=e.x; e.ty=e.y; e.set('dizzy'); e.cd=99; window.F=[e];})()")
        key(pg, 'Comma', 0.06, 0.3); check('P2 fights on the ward', pg.evaluate("F[0].hp < F[0].maxHp"))
        pg.close()
        pg = b.new_page(viewport={'width': 960, 'height': 540}); pg.on('pageerror', lambda e: errs.append(str(e))); pg.add_init_script(MOCK)
        pg.goto(U + '?level=5&nocut=1&hero=heather'); pg.wait_for_function('window.__loaded === true', timeout=30000); ready(pg); pg.evaluate('__padConnect()'); time.sleep(0.3)
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2); foe(pg, 'tinfoil', 26, st='dizzy')
        pg.evaluate('__padSet(2, true)'); time.sleep(0.1); pg.evaluate('__padSet(2, false)'); time.sleep(0.25)
        check('pad: X attacks on the ward', pg.evaluate("F[0].hp < F[0].maxHp")); pg.close()
        ctx = b.new_context(viewport={'width': 915, 'height': 412}, device_scale_factor=2.6, is_mobile=True, has_touch=True, user_agent=UA)
        pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg); pg.on('pageerror', lambda e: errs.append(str(e)))
        def touch(kind, pts): cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [{'x': x, 'y': y, 'id': i} for i, x, y in pts]})
        pg.goto(U + '?level=5&nocut=1&hero=kim&god=1'); pg.wait_for_function('window.__loaded === true', timeout=30000); ready(pg); time.sleep(0.5)
        lay = pg.evaluate("(()=>{const pad=document.getElementById('pad'); return {VW:__nbd.G.VW, pad:!!pad && getComputedStyle(pad).display!=='none'};})()")
        jx, jy = 915 * 0.18, 412 * 0.7; x0 = pg.evaluate("__nbd.W.heroes[0].x")
        touch('touchStart', [(1, jx, jy)]); time.sleep(0.05)
        for k in range(10): touch('touchMove', [(1, jx + k * 5, jy)]); time.sleep(0.02)
        time.sleep(0.8); touch('touchEnd', []); time.sleep(0.2)
        check('phone: wide view + touch pad moves the nurse on the ward', lay['VW'] >= 400 and lay['pad'] and pg.evaluate("__nbd.W.heroes[0].x") > x0 + 20, lay)
        pg.screenshot(path='tests/out/v13_phone.png'); ctx.close()
        ctx = b.new_context(viewport={'width': 915, 'height': 412}, has_touch=True, is_mobile=True); pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(U + '?nocut=1'); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.6); pg.evaluate("__nbd.toLevels()"); time.sleep(0.5)
        R = pg.evaluate("[__nbd.game.lvRects, __nbd.G.VW, __nbd.G.VH, __nbd.PICKS[4].name]")
        fit = all(r[0] >= 0 and r[1] >= 0 and r[0] + r[2] <= R[1] and r[1] + r[3] <= R[2] for r in R[0]) and len(R[0]) == 7
        check('level select (phone): FLOOR 5 PSYCH WARD card, all cards fit', fit and 'PSYCH' in R[3], R)
        pg.screenshot(path='tests/out/v13_levels_phone.png')
        box = pg.evaluate("(()=>{const c=document.querySelector('canvas').getBoundingClientRect();return [c.left,c.top,c.width/__nbd.G.VW,c.height/__nbd.G.VH]})()")
        r = R[0][4]; tap = lambda: pg.touchscreen.tap(box[0] + (r[0] + r[2] / 2) * box[2], box[1] + (r[1] + r[3] / 2) * box[3])
        tap(); time.sleep(0.3); tap(); time.sleep(0.3)
        check('tap, tap: the psych ward card is picked', pg.evaluate("__nbd.game.lvCur") == 4 and pg.evaluate("!!__nbd.game.overlay"), pg.evaluate("[__nbd.game.lvCur, !!__nbd.game.overlay]"))
        ctx.close()
    b.close()
print('console errors:', errs[:3] if errs else 'none'); print('ALL PASS' if not fails and not errs else 'SOME FAILED'); sys.exit(1 if fails or errs else 0)
