# v0.16: THE ROOF (helipad at night, after the Night Shift, before the Garage) + THE LIFE FLITE CREW.
# A level/wind/lights, P roof foes, E boss + outro, F flow + level select. Usage: python3 tests/v16.py [A P E F]
import time, sys
from playwright.sync_api import sync_playwright
U = 'http://localhost:8731/'; errs = []; fails = []
ONLY = sys.argv[1:] or list('APEF')
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
        pg = page(b, '?level=8&nocut=1&hero=nick&god=1'); ready(pg)
        st = pg.evaluate("[__nbd.W.lv.id, __nbd.W.lv.name, !!__nbd.W.lv.roof, __nbd.W.lv.music, __nbd.W.lv.zones.map(z=>z.title), (__nbd.W.roofPads||[]).length, [...new Set((__nbd.W.roofPads||[]).map(l=>l.c))].length]")
        check('THE ROOF loads (music roof, 5 zones, pad lights in 3 colors)', st[0] == 8 and st[2] and st[3] == 'roof' and len(st[4]) == 5 and st[5] >= 20 and st[6] == 3, st)
        L = pg.evaluate("(()=>{const L=[]; __nbd.roofLights && __nbd.roofLights(L); return L.length})()")
        pg.screenshot(path='tests/out/v16_roof.png')
        pg.evaluate(FREEZE)
        pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.y=176; window.Y0=h.y; __nbd.gust(1);})()"); time.sleep(3.4)
        g = pg.evaluate("[__nbd.W.heroes[0].y-Y0, __nbd.W.stats.gusts||0]")
        check('a wind gust pushes the nurse across lanes', abs(g[0]) > 12 and g[1] >= 1, g)
        r = pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; const out=[]; for(let i=0;i<6;i++){h.sayCd=0; const s=h.say('zone',true); if(s) out.push(s);} return [out, h.d.roof.zone]})()")
        check('nurses have roof lines', any(s in r[1] for s in r[0]), r)
        pg.close()
    if 'P' in ONLY:
        pg = page(b, '?level=8&nocut=1&hero=nick&god=1'); ready(pg); pg.evaluate(FREEZE)
        hs = pg.evaluate("(()=>{const s=(id)=>__nbd.spawn(id,'R').h; return {nick:__nbd.W.heroes[0].h, vaper:s('vaper'), droneguy:s('droneguy'), duke:s('duke')}})()")
        check('roof foes are nurse-sized', all(abs(hs[k] - hs['nick']) <= 8 for k in ('vaper', 'droneguy', 'duke')), hs)
        pg.evaluate(FREEZE); time.sleep(0.2)
        pg.evaluate("(()=>{const i=(" + FOE + ")('vaper',90,0); const e=__nbd.W.enemies[i]; e.face=-1; e.set('atk'); e.t=0; e.hitDone=false; e.cd=0;})()"); time.sleep(1.2)
        check('vaper: the vape cloud dizzies a nurse', pg.evaluate("__nbd.W.heroes[0].dizzyT>0||__nbd.W.heroes[0].st==='dizzy'||(__nbd.W.stats.dizzied||0)>0"), pg.evaluate("[__nbd.W.heroes[0].st, __nbd.W.shots.map(s=>s.spr)]"))
        g = pg.evaluate("(()=>{const i=(" + FOE + ")('duke',40,0); const e=__nbd.W.enemies[i]; return [e.d.ai, e.d.armor||0, e.hp]})()")
        check('duke: visitor AI with armor', g[0] == 'visitor' and g[1] >= 2, g)
        pg.close()
    if 'E' in ONLY:
        pg = page(b, '?level=8&zone=4&hero=kim&god=1&cuts=1')
        pg.wait_for_function(f"{SC}==='cutscene' || (__nbd.W.boss && __nbd.W.boss.name)", timeout=30000)
        check('intro cutscene for the Life Flite crew', pg.evaluate("__nbd.game.cut && __nbd.game.cut.id") == 'lifeflight')
        time.sleep(2.5); key(pg, 'KeyK', after=0.4); key(pg, 'KeyK', after=0.5)
        pg.wait_for_function("__nbd.W.boss && __nbd.W.boss.greeted", timeout=15000); time.sleep(0.3)
        B = pg.evaluate("(()=>{const B=window.B=__nbd.W.boss; const BD=" + BOUNDS + "; return {name:B.name, r:BD('roxy','idle')[1]/BD('nick','idle')[1], music:__nbd.W.lv.bossMusic};})()")
        check('ROXY + LIFE FLITE CREW (1.2-1.5x a nurse) with own music', 'LIFE FLITE' in B['name'] and 1.15 <= B['r'] <= 1.55 and B['music'] == 'lifeflight', B)
        pg.evaluate("(()=>{__nbd.W.enemies.forEach(e=>{e.hp=0; e.st='dead'; e.alive=false}); const h=__nbd.W.heroes[0]; h.inv=0; h.z=0; h.y=176; B.x=h.x+110; B.y=h.y; B.face=-1; B.set('zap');})()"); time.sleep(1.6)
        check('CLEAR!: paddle bolts skim the lane', pg.evaluate("(__nbd.W.stats.zaps||0)>=1"), pg.evaluate("[B.st, __nbd.W.stats.zaps]"))
        pg.evaluate("(()=>{B.set('radio'); B.hitDone=false;})()"); time.sleep(1.2)
        check('AIR SUPPORT: the chopper flies over', pg.evaluate("(__nbd.W.stats.flyovers||0)>=1"), pg.evaluate("[B.st, B.heli && B.heli.mode]"))
        time.sleep(0.5); pg.screenshot(path='tests/out/v16_boss.png')
        time.sleep(1.5)
        pg.evaluate("(()=>{B.set('chase'); B.hp=B.maxHp*0.45; B.takeHit({dmg:1, dir:1, from:__nbd.W.heroes[0], force:true}); B.cd=0;})()"); time.sleep(2.2)
        p2 = pg.evaluate("[B.phase, B.p2label, B.heli && B.heli.mode, B.dukes.length]")
        check('phase 2: HOT LOAD! (chopper hovers, Duke joins)', p2[0] == 2 and 'HOT LOAD' in p2[1] and p2[3] >= 1, p2)
        pg.screenshot(path='tests/out/v16_hotload.png')
        pg.evaluate("(()=>{B.set('chase'); B.z=0; B.hp=1; B.takeHit({dmg:5, dir:1, from:__nbd.W.heroes[0], force:true});})()"); time.sleep(0.8)
        d = pg.evaluate("({st:B.st, said:__nbd.W.fx.filter(f=>f.type==='txt').map(f=>f.s), off:__nbd.W.stats.offShift})")
        check('defeat: "Going... off... shift... zzz"', d['st'] == 'defeat' and (any('shift' in s for s in d['said']) or d['off'] == 1), d)
        time.sleep(1.5); pg.screenshot(path='tests/out/v16_ko.png')
        pg.wait_for_function(f"{SC}==='tally'", timeout=16000); time.sleep(3.4); key(pg, 'KeyJ', after=0.5)
        check('roof tally -> roof outro', pg.evaluate("__nbd.game.cut && __nbd.game.cut.id") == 'roofout')
        for _ in range(3): key(pg, 'KeyK', after=0.6)
        pg.wait_for_function("__nbd.game.cut && __nbd.game.cut.id==='garage' || (__nbd.W.lv && __nbd.W.lv.garage)", timeout=8000)
        check('-> on to the garage', True)
        pg.close()
    if 'F' in ONLY:
        pg = page(b, '?level=4&hero=nick&god=1&cuts=1'); time.sleep(2.5)
        pg.evaluate("__nbd.goRoof()"); time.sleep(0.3)
        check('night -> roof cutscene', pg.evaluate("__nbd.game.cut && __nbd.game.cut.id") == 'roof')
        time.sleep(2.0); pg.screenshot(path='tests/out/v16_cut_roof.png')
        for _ in range(3): key(pg, 'KeyK', after=0.6)
        pg.wait_for_function("__nbd.W.lv && __nbd.W.lv.id===8", timeout=10000); check('-> the roof loads', True)
        for (w, h) in ((960, 540), (800, 600)):
            pg.set_viewport_size({'width': w, 'height': h}); pg.evaluate("__nbd.toLevels()"); time.sleep(0.5)
            R = pg.evaluate("[__nbd.game.lvRects, __nbd.G.VW, __nbd.G.VH, __nbd.PICKS.map(p=>p.name)]")
            i = next((k for k, n in enumerate(R[3]) if 'ROOF' in n), -1)
            check(f'level select {w}x{h}: 10 cards fit, ROOF right after NIGHT SHIFT', len(R[0]) == 10 and i > 0 and 'NIGHT' in R[3][i-1] and all(r[0] >= 0 and r[1] >= 0 and r[0]+r[2] <= R[1] and r[1]+r[3] <= R[2] for r in R[0]), R)
            pg.screenshot(path=f'tests/out/v16_levels_{w}.png')
        pg.close()
    b.close()
print('console errors:', errs[:3] if errs else 'none'); print('ALL PASS' if not fails and not errs else 'SOME FAILED'); sys.exit(1 if fails or errs else 0)
