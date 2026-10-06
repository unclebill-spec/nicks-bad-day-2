# v0.5: Floor 4 Radiology (dark floor + neon-blue lightboxes, radiology props, Contrast Chugger + Lab-Coat Hugger, v0.5's Lead-Apron Hugger),
# Lead-Apron Lou (mini-boss), MAGNA-SCAN 3000 (MRI magnet boss: pull / quench weak point / knock waves / table, 2 phases),
# the Night Shift (lights out, flashlights, glowing eyes, lights back on at the end), and the full flow
# L1 -> bonus -> Radiology -> Night -> ending -> scores with 2P / continues / pad / touch, plus bot playthroughs of the new floors.
# Screenshots -> tests/out/v05_*.png
import time, sys
from playwright.sync_api import sync_playwright
U = 'http://localhost:8731/'
errs = []
def watch(pg):
    pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: errs.append(f'PAGEERROR: {e}'))
def key(pg, k, hold=0.08, after=0.1): pg.keyboard.down(k); time.sleep(hold); pg.keyboard.up(k); time.sleep(after)
SC = "__nbd.game.scene"
def ready(pg, st='idle'):
    pg.wait_for_function('window.__loaded === true', timeout=30000)
    pg.wait_for_function(f"window.__nbd && {SC}==='play' && __nbd.W.heroes.length>0", timeout=30000); time.sleep(0.4)
CLEAR = "(()=>{const W=__nbd.W; W.enemies.forEach(e=>{e.alive=false}); W.enemies.length=0; W.queue && (W.queue.length=0); W.items.length=0; W.shots.length=0;})()"
ok = True
SKIP_SCOOT = "(()=>{const S=__nbd.SC; S.phase='finish'; S.endT=0; S.bossBeat=true;})()"  # v0.9: fast-forward the Scooter Run to its finish line
def check(name, cond, info=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name, info); sys.stdout.flush(); ok = ok and bool(cond)
def foe(pg, kind, dx, dy=0, st='idle'):
    return pg.evaluate(f"(()=>{{const W=__nbd.W,h=W.heroes[0]; const e=__nbd.spawn('{kind}','R'); e.x=h.x+{dx}; e.y=h.y+{dy}; e.tx=e.x; e.ty=e.y; e.set('{st}'); window.F=window.F||[]; F.push(e); return F.length-1;}})()")
# opaque pixel height/width of a character frame (true on-screen size, not the cell)
BOUNDS = """((sheet, an) => { const G = __nbd.G, A = G.atlas.chars[sheet], [cw, ch] = A.cell, i = A.anims[an].s, sx = (i % A.cols) * cw, sy = Math.floor(i / A.cols) * ch;
  const c = document.createElement('canvas'); c.width = cw; c.height = ch; const x = c.getContext('2d'); x.drawImage(G.img[sheet], sx, sy, cw, ch, 0, 0, cw, ch);
  const d = x.getImageData(0, 0, cw, ch).data; let x0 = cw, x1 = 0, y0 = ch, y1 = 0, n = 0;
  for (let y = 0; y < ch; y++) for (let k = 0; k < cw; k++) if (d[(y * cw + k) * 4 + 3] > 20) { n++; x0 = Math.min(x0, k); x1 = Math.max(x1, k); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
  return [x1 - x0 + 1, y1 - y0 + 1, n]; })"""
LUM = """((lx, ly) => { const src = __nbd.G.ctx.canvas, t = document.createElement('canvas'); t.width = 7; t.height = 7; const c = t.getContext('2d', { willReadFrequently: true });
  c.drawImage(src, Math.round(lx) - 3, Math.round(ly) - 3, 7, 7, 0, 0, 7, 7); const d = c.getImageData(0, 0, 7, 7).data; let s = 0; for (let i = 0; i < d.length; i += 4) s += d[i] + d[i + 1] + d[i + 2]; return s / (d.length / 4) / 3; })"""
MOCK = """(() => { const pad = { id: 'Xbox Wireless Controller (STANDARD GAMEPAD)', index: 0, connected: true, mapping: 'standard', timestamp: 0,
  axes: [0, 0, 0, 0], buttons: Array.from({ length: 17 }, () => ({ pressed: false, value: 0, touched: false })) };
  window.__pad = pad; navigator.getGamepads = () => [window.__padOn ? pad : null, null, null, null];
  window.__padSet = (i, on) => { pad.buttons[i].pressed = on; pad.buttons[i].value = on ? 1 : 0; pad.timestamp++; };
  window.__padConnect = () => { window.__padOn = true; const e = new Event('gamepadconnected'); e.gamepad = pad; dispatchEvent(e); }; })();"""
ONLY = sys.argv[1:] or list('ABCDEFG')

with sync_playwright() as p:
    b = p.chromium.launch()
    # ================================================================ A: Floor 4 Radiology basics (keyboard, Nick)
    if 'A' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=2&hero=nick&god=1'); ready(pg)
        L = pg.evaluate("(()=>{const W=__nbd.W; return {id:W.lv.id, name:W.lv.name, dark:W.dark, lights:W.lights.length, blue:W.lights.filter(l=>l.col==='#3aa8ff').length, music:W.lv.music, props:W.props.map(p=>p.kind)};})()")
        check('Radiology loads: dark floor with neon-blue lights', L['id'] == 2 and 0.3 < L['dark'] < 0.8 and L['blue'] >= 10 and L['music'] == 'radiology', {k: L[k] for k in ('name', 'dark', 'lights', 'blue')})
        check('radiology props on the floor (apron racks, contrast carts, film viewers, wheelchairs)', all(k in L['props'] for k in ('apronrack', 'contrastcart', 'viewer', 'wheelchair')))
        time.sleep(0.8); pg.screenshot(path='tests/out/v05_radiology.png')
        pg.evaluate(CLEAR); pg.evaluate("(()=>{const W=__nbd.W; W.zone=99; W.zoneOn=false; W.lockX=W.camX; const h=W.heroes[0]; h.x=W.camX+120; h.y=172;})()")
        # Contrast Chugger lobs a barium cup -> chalky white puddle
        i = foe(pg, 'barium', 130)
        pg.evaluate(f"(()=>{{const e=F[{i}]; e.face=-1; e.throwKind='jello'; e.begin('windup');}})()"); time.sleep(0.6)
        s1 = pg.evaluate("__nbd.W.shots.map(s=>s.spr)"); time.sleep(1.4)
        s2 = pg.evaluate("__nbd.W.shots.map(s=>s.kind+':'+(s.spr||''))")
        check('Contrast Chugger: barium cup -> white puddle', 'p_cup' in s1 and 'puddle:puddle_w' in s2, [s1, s2])
        pg.screenshot(path='tests/out/v05_barium.png'); pg.evaluate(CLEAR)
        # Lab-Coat Hugger (v0.7.1; was the Lead-Apron Hugger) shrugs off jabs (armor), then goes down to a kick
        i = foe(pg, 'apron', 26)
        r = pg.evaluate(f"(()=>{{const e=F[{i}], h=__nbd.W.heroes[0]; const a0=e.armor; e.takeHit({{dmg:4, dir:1, kb:20, from:h}}); const st1=e.st, a1=e.armor; e.takeHit({{dmg:8, dir:1, kb:150, down:true, from:h}}); return [a0, a1, st1, e.st, e.type, e.kind];}})()")
        check('Lab-Coat Hugger: the starchy coat absorbs jabs, kick knocks him down', r[0] == 2 and r[1] == 1 and r[2] != 'hurt' and r[3] == 'fall' and r[4] == 'apron', r)
        pg.evaluate(CLEAR)
        # radiology props break into their own debris; the viewer glows; metal flag set
        r = pg.evaluate("""(()=>{const W=__nbd.W, h=W.heroes[0], out={}; for (const k of ['apronrack','contrastcart','viewer']) { const i=__nbd.prop(k, 40, 0); const p=W.props[i]; let n=0; while (p.st<2 && n<12) { __nbd.hitProp(p, 20, {dir:1, kb:20, from:h}); n++; } out[k]=[p.st, n, !!p.def.metal, p.def.glow||'']; } return out;})()""")
        check('apron rack / contrast cart / film viewer all break (metal, viewer glows blue)', all(v[0] == 2 and v[2] for v in r.values()) and r['viewer'][3] == '#3aa8ff', r)
        # kicking a prop sends it rolling (the existing kick system)
        r = pg.evaluate("(()=>{const W=__nbd.W, h=W.heroes[0]; const i=__nbd.prop('apronrack', 30, 0); const p=W.props[i]; __nbd.hitProp(p, 8, {dir:1, kb:160, from:h}); return p.vx;})()")
        check('a kick sends an apron rack rolling', r > 150, r)
        pg.close()
    # ================================================================ B: Lead-Apron Lou (mini-boss)
    if 'B' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=2&zone=2&hero=jackie&god=1'); ready(pg)
        pg.wait_for_function("__nbd.W.boss && __nbd.W.boss.mini && __nbd.W.boss.st==='idle'", timeout=15000)
        lou = pg.evaluate(BOUNDS + "('lou','idle')"); nurse = pg.evaluate(BOUNDS + "('jackie','idle')")
        ratio = lou[1] / nurse[1]
        check('Lou is only modestly bigger: 1.2-1.5x a nurse (height; Bill\'s v0.7 override)', 1.2 <= ratio <= 1.5 and pg.evaluate("__nbd.W.boss.name") == 'LEAD-APRON LOU', f'{lou[1]}px vs {nurse[1]}px = {ratio:.2f}x')
        pg.screenshot(path='tests/out/v05_lou.png')
        pg.evaluate("(()=>{const W=__nbd.W,b=W.boss,h=W.heroes[0]; h.x=b.x-120; h.y=b.y; b.face=-1; b.cd=99;})()")
        # charge: telegraph stance, then a charge across the screen, then winded (his weak point)
        pg.evaluate("(()=>{const b=__nbd.W.boss; b.set('set'); b.face=-1;})()"); time.sleep(0.4)
        st0 = pg.evaluate("__nbd.W.boss.st")
        pg.wait_for_function("__nbd.W.boss.st==='charge'", timeout=3000)
        pg.wait_for_function("__nbd.W.boss.st==='tired'", timeout=5000)
        hit = pg.evaluate("(()=>{const b=__nbd.W.boss,h=__nbd.W.heroes[0]; const a=b.hp; b.takeHit({dmg:10, dir:1, from:h}); const tired=a-b.hp; b.set('idle'); b.cd=99; const c=b.hp; b.takeHit({dmg:10, dir:1, from:h}); return [tired, c-b.hp];})()")
        check('Lou: stance telegraph -> charge -> winded; full damage only when winded', st0 == 'set' and hit[0] == 10 and hit[1] <= 5, [st0, hit])
        # stomp ring and film frisbees
        pg.evaluate("(()=>{const b=__nbd.W.boss; b.set('stomp');})()"); time.sleep(0.65)
        rings = pg.evaluate("__nbd.W.shots.filter(s=>s.kind==='shock'&&s.hostile).length")
        time.sleep(0.6); pg.evaluate("(()=>{const b=__nbd.W.boss; b.set('throw'); b.thrown=0;})()"); time.sleep(0.6)
        films = pg.evaluate("__nbd.W.shots.filter(s=>s.spr==='p_film').length")
        check('Lou: stomp shock ring + X-ray film frisbee', rings >= 1 and films >= 1, [rings, films])
        pg.screenshot(path='tests/out/v05_lou_film.png')
        # phase 2 at half health calls help ("HIKE!")
        n0 = pg.evaluate("__nbd.W.enemies.length")
        pg.evaluate("(()=>{const b=__nbd.W.boss,h=__nbd.W.heroes[0]; b.set('tired'); b.hp=b.maxHp*0.52; b.takeHit({dmg:20, dir:1, from:h});})()"); time.sleep(0.3)
        check('Lou phase 2: FOURTH QUARTER + two helpers', pg.evaluate("__nbd.W.boss.phase") == 2 and pg.evaluate("__nbd.W.enemies.length") >= n0 + 2)
        pg.evaluate(CLEAR)
        pg.evaluate("(()=>{const b=__nbd.W.boss,h=__nbd.W.heroes[0]; b.set('tired'); b.hp=3; b.takeHit({dmg:20, dir:1, from:h});})()")
        check('Lou defeated: naps, drops snacks + a gold star', pg.evaluate("__nbd.W.boss.st") == 'defeat' and set(pg.evaluate("__nbd.W.items.map(i=>i.k)")) >= {'snacks', 'star'})
        pg.wait_for_function("!__nbd.W.boss && !__nbd.W.zoneOn", timeout=8000)
        check('after Lou the floor opens up (GO), he stays asleep as scenery', pg.evaluate("__nbd.W.decor.length") == 1 and pg.evaluate("__nbd.W.go") > 0)
        time.sleep(0.4); pg.screenshot(path='tests/out/v05_lou_nap.png')
        pg.close()
    # ================================================================ C: MAGNA-SCAN 3000 (MRI boss)
    if 'C' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=2&zone=5&hero=will&god=1'); ready(pg)
        pg.wait_for_function("__nbd.W.boss && __nbd.W.boss.isMRI", timeout=15000)
        check('MRI boots up (not hittable while booting)', pg.evaluate("__nbd.W.boss.st") == 'enter' and not pg.evaluate("__nbd.W.boss.hittable()"))
        time.sleep(1.2); pg.screenshot(path='tests/out/v05_mri_boot.png')
        pg.wait_for_function("__nbd.W.boss.st!=='enter'", timeout=6000)
        mri = pg.evaluate(BOUNDS + "('mri','idle')"); nurse = pg.evaluate(BOUNDS + "('nick','idle')")
        hr, wr, ar = mri[1] / nurse[1], mri[0] / nurse[0], mri[2] / nurse[2]
        check('MRI boss is only modestly bigger: 1.2-1.5x a nurse\'s height (v0.7 override), still a wide machine', 1.2 <= hr <= 1.5 and wr >= 3, f'h {hr:.1f}x  w {wr:.1f}x  area {ar:.1f}x')
        SET = "(()=>{const W=__nbd.W,b=W.boss; b.cd=99; b.set('idle'); W.shots.length=0; W.heroes.forEach((h,i)=>{h.x=b.front-130; h.y=160+i*20; h.set('idle'); h.z=0;});})()"
        pg.evaluate(SET)
        # MAGNET ON: pulls nurses in, yanks the IV pole out of her hands, metal on the floor and metal carts slide in
        pg.evaluate("""(()=>{const W=__nbd.W,b=W.boss,h=W.heroes[0]; const it=__nbd.drop('w:ivpole'); W.items.splice(W.items.indexOf(it),1); h.weapon=it;
          const c=__nbd.drop('w:crutch'); c.x=h.x-30; c.y=200; const i=__nbd.prop('wheelchair', -70, 30); window.WC=W.props[i]; window.X0=h.x; b.set('pullWarn');})()""")
        time.sleep(0.5); pg.screenshot(path='tests/out/v05_mri_pull0.png')
        time.sleep(1.2); pg.screenshot(path='tests/out/v05_mri_pull.png')
        r = pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0]; return {dx:h.x-X0, weapon:!!h.weapon, crutch:W.items.filter(i=>i.k==='w:crutch').length, wc:[WC.x|0, WC.st], st:W.boss.st};})()")
        check('MAGNET ON: nurse dragged in + IV pole yanked out of her hands', r['dx'] > 25 and not r['weapon'], r)
        pg.wait_for_function("__nbd.W.boss.st==='vent'", timeout=5000)
        r2 = pg.evaluate("(()=>{const W=__nbd.W; return {crutch:W.items.filter(i=>i.k==='w:crutch').length, wc:WC.st};})()")
        check('metal crutch on the floor and a wheelchair fly into the magnet', r2['crutch'] == 0 and r2['wc'] == 2, r2)
        # QUENCH vent = weak point: full damage, otherwise 20%
        pg.screenshot(path='tests/out/v05_mri_vent.png')
        d = pg.evaluate("(()=>{const b=__nbd.W.boss,h=__nbd.W.heroes[0]; const a=b.hp; b.takeHit({dmg:20, dir:1, from:h}); const v=a-b.hp; b.set('idle'); b.cd=99; const c=b.hp; b.takeHit({dmg:20, dir:1, from:h}); return [v, c-b.hp];})()")
        check('QUENCH vent is the weak point (full damage vs 20%)', d[0] == 20 and abs(d[1] - 4) < 0.01, d)
        # a real punch from the nurse connects at any depth (the machine fills the floor)
        pg.evaluate(SET); pg.evaluate("(()=>{const W=__nbd.W,b=W.boss; W.heroes[0].x=b.front-22; W.heroes[0].y=210; W.heroes[0].face=1; b.set('vent'); b.t=0; window.HP=b.hp;})()")
        for _ in range(3): key(pg, 'KeyJ', 0.05, 0.15)
        check('a punch at the far lane still hits the machine', pg.evaluate("__nbd.W.boss.hp") < pg.evaluate("HP"))
        # KNOCK waves roll along the floor; TABLE shoots down your lane after a red flash
        pg.evaluate(SET); pg.evaluate("__nbd.W.boss.set('bang')"); time.sleep(1.6)
        waves = pg.evaluate("__nbd.W.shots.filter(s=>s.spr==='mri_wave0').length")
        pg.screenshot(path='tests/out/v05_mri_knock.png')
        check('KNOCK: sound waves roll along the floor lanes', waves >= 2, waves)
        # jump the table (no god mode effect on state: watch for a knockdown)
        pg.evaluate(SET); pg.evaluate("(()=>{const b=__nbd.W.boss,h=__nbd.W.heroes[0]; b.lane=h.y; b.set('tableWarn');})()"); time.sleep(0.3)
        pg.screenshot(path='tests/out/v05_mri_tablewarn.png')
        pg.wait_for_function("__nbd.W.shots.some(s=>s.spr==='mri_table')", timeout=3000)
        key(pg, 'KeyK', 0.12, 0.0)
        hurt = False
        for _ in range(12):
            st = pg.evaluate("__nbd.W.heroes[0].st"); hurt = hurt or st in ('fall', 'down', 'hurt'); time.sleep(0.05)
        check('TABLE: red-lane telegraph, then the table can be jumped', not hurt)
        pg.evaluate(SET); pg.evaluate("(()=>{const b=__nbd.W.boss,h=__nbd.W.heroes[0]; b.lane=h.y; b.set('tableWarn');})()")
        pg.wait_for_function("__nbd.W.shots.some(s=>s.spr==='mri_table')", timeout=3000)
        pg.wait_for_function("['fall','down'].includes(__nbd.W.heroes[0].st)", timeout=2000)
        check('...and it knocks you down if you stand there', True)
        # phase 2: SUPERCONDUCTING (violet), stronger pull ending in a REPEL blast, calls patients
        pg.evaluate(SET); time.sleep(1.2)
        pg.evaluate("(()=>{const b=__nbd.W.boss,h=__nbd.W.heroes[0]; b.set('vent'); b.hp=b.maxHp*0.51; b.takeHit({dmg:20, dir:1, from:h});})()")
        check('phase 2 at half health: SUPERCONDUCTING', pg.evaluate("__nbd.W.boss.phase") == 2 and pg.evaluate("__nbd.W.boss.st") == 'super')
        time.sleep(0.6); pg.screenshot(path='tests/out/v05_mri_phase2.png')
        pg.wait_for_function("__nbd.W.boss.st==='idle'", timeout=4000)
        pg.evaluate(SET); pg.evaluate("(()=>{window.X0=__nbd.W.heroes[0].x; __nbd.W.boss.set('pull');})()"); time.sleep(1.0)
        dx2 = pg.evaluate("__nbd.W.heroes[0].x - X0")
        pg.wait_for_function("__nbd.W.boss.st==='repel'", timeout=4000); time.sleep(0.2)
        rep = pg.evaluate("__nbd.W.shots.filter(s=>s.kind==='shock'&&s.hostile).length")
        check('phase 2: stronger pull, then a REPEL shock ring', dx2 > 60 and rep >= 1, [round(dx2), rep])
        pg.evaluate(CLEAR); pg.evaluate("(()=>{const b=__nbd.W.boss; b.callCd=0; b.cd=0; b.set('idle');})()"); time.sleep(0.3)
        check('phase 2: "NEXT PATIENT, PLEASE!" pages in backup', pg.evaluate("__nbd.W.enemies.length") >= 2)
        # beat it: power down, minions nap, tally
        pg.evaluate("(()=>{const b=__nbd.W.boss,h=__nbd.W.heroes[0]; b.set('vent'); b.hp=3; b.takeHit({dmg:20, dir:1, from:h});})()"); time.sleep(0.9)
        pg.screenshot(path='tests/out/v05_mri_down.png')
        check('MRI defeated: powers down, the paged patients nap', pg.evaluate("__nbd.W.boss.st") == 'defeat' and pg.evaluate("__nbd.W.enemies.filter(e=>e.hp>0).length") == 0)
        pg.wait_for_function(f"{SC}==='tally'", timeout=8000)
        check('-> floor tally', True)
        pg.close()
    # ================================================================ D: Night shift (lights out, flashlights, eyes, lights back on)
    if 'D' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=3&hero=kim&god=1'); pg.wait_for_function('window.__loaded === true', timeout=30000)
        pg.wait_for_function(f"{SC}==='intro'", timeout=10000)
        d0 = pg.evaluate("__nbd.W.dark")
        pg.wait_for_function("__nbd.W.dark > 0.85", timeout=6000); ready(pg)
        check('night shift: the lights go out during the intro', d0 < 0.1 and pg.evaluate("__nbd.W.lv.flashlight"), d0)
        k = pg.evaluate("(()=>{const W=__nbd.W; const c={}; for (const l of W.lights) c[l.col]=(c[l.col]||0)+1; return c;})()")
        check('only exit signs, call lights, monitors and windows glow', k.get('#ff3a4a', 0) >= 3 and k.get('#ff4a3a', 0) >= 6 and k.get('#3aa8ff', 0) >= 6, k)
        pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0]; W.enemies.forEach(e=>e.alive=false); W.enemies.length=0; W.queue.length=0; W.zone=99; W.zoneOn=false; W.lockX=W.camX; h.x=W.camX+200; h.y=180; h.face=1;})()"); time.sleep(0.3)
        lum = pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0],o=__nbd.W.camX, Y=h.y+(__nbd.G.VH-224)/2-6; const f=" + LUM + "; return [f(h.x-o+70, Y), f(h.x-o-70, Y)];})()")
        check('the flashlight throws a pool of light in front of the nurse', lum[0] > lum[1] * 2 + 10, [round(v) for v in lum])
        # patients emerge from the dark (eyes glow)
        foe(pg, 'wanderer', 150, -20, 'walk'); foe(pg, 'sundowner', -120, 20, 'idle'); foe(pg, 'escape', 190, 26, 'idle')
        time.sleep(0.6); pg.screenshot(path='tests/out/v05_night.png')
        pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.face=-1;})()"); time.sleep(0.3); pg.screenshot(path='tests/out/v05_night2.png')
        pg.close()
        # last zone: when the last patient is tucked in, the power comes back, then the tally
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=3&zone=3&hero=kim&god=1'); ready(pg)
        check('starting mid-floor: already dark', pg.evaluate("__nbd.W.dark") > 0.85)
        pg.wait_for_function("__nbd.W.zoneOn", timeout=5000)
        pg.evaluate("(()=>{const W=__nbd.W; W.wave=W.lv.zones[W.zone].waves.length-1; W.queue.length=0; W.enemies.forEach(e=>e.alive=false); W.enemies.length=0;})()")
        pg.wait_for_function("__nbd.W.finalT > 0.5", timeout=6000); pg.screenshot(path='tests/out/v05_power.png')
        pg.wait_for_function("__nbd.W.finalT > 1.5", timeout=4000)
        check("LAST CALL cleared: POWER'S BACK (lights up)", pg.evaluate("__nbd.W.dark") < 0.2)
        pg.wait_for_function(f"{SC}==='tally'", timeout=5000)
        check('-> night tally', True)
        pg.close()
    # ================================================================ E: full flow with cutscenes, 1P keyboard: L1 -> bonus -> Radiology -> Night -> THE END
    if 'E' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?zone=5&hero=nick&god=1&cuts=1'); pg.wait_for_function('window.__loaded === true', timeout=30000)
        pg.evaluate("localStorage.removeItem('nbd2.save')")
        pg.wait_for_function(f"{SC}==='cutscene'", timeout=20000); key(pg, 'KeyK', after=0.4)
        pg.wait_for_function("__nbd.W.boss && __nbd.W.boss.st!=='enter'", timeout=10000)
        pg.evaluate("(()=>{const b=__nbd.W.boss; b.hp=2; b.phase=2; b.takeHit({dmg:9, dir:1, from:__nbd.W.heroes[0], force:true});})()")
        pg.wait_for_function(f"{SC}==='tally'", timeout=20000); time.sleep(3.3)
        t1 = pg.evaluate("__nbd.game.tally[0].total"); key(pg, 'KeyJ', after=0.4)
        check('L1 tally -> lunch cutscene; the tally total carries', pg.evaluate("__nbd.game.cut.id") == 'lunch' and pg.evaluate("__nbd.W.heroes[0].score") == t1, t1)
        time.sleep(0.6); key(pg, 'KeyK', after=0.4); pg.wait_for_function(f"{SC}==='bonus'", timeout=5000); time.sleep(2.5)
        pg.evaluate("__nbd.B.left = 0.3"); pg.wait_for_function(f"{SC}==='btally'", timeout=12000); time.sleep(3.3)
        s_b = pg.evaluate("__nbd.W.heroes[0].score"); key(pg, 'KeyJ', after=0.4)
        check('bonus tally -> "next floor" cutscene', pg.evaluate("__nbd.game.cut.id") == 'next')
        time.sleep(6.5); pg.screenshot(path='tests/out/v05_cut_next.png'); key(pg, 'Enter', after=0.5)
        check('-> Floor 4 Radiology, score carried', pg.evaluate("__nbd.W.lv.id") == 2 and pg.evaluate("__nbd.W.heroes[0].score") == s_b, [pg.evaluate(SC), s_b])
        pg.wait_for_function(f"{SC}==='play'", timeout=6000)
        # straight to the MRI line: the boss cutscene for this floor is the MRI one
        pg.evaluate("(()=>{const W=__nbd.W, z=W.lv.zones[5]; W.zone=4; W.zoneOn=false; W.enemies.length=0; W.queue.length=0; W.camX=W.camMin=z.lock-60; W.camMax=z.lock; W.heroes[0].x=z.at+6; W.heroes[0].y=172;})()")
        pg.wait_for_function(f"{SC}==='cutscene'", timeout=8000)
        check('MRI cutscene before the boss', pg.evaluate("__nbd.game.cut.id") == 'mri')
        time.sleep(7.0); pg.screenshot(path='tests/out/v05_cut_mri.png'); key(pg, 'KeyJ', after=0.4)
        pg.wait_for_function("__nbd.W.boss && __nbd.W.boss.isMRI && __nbd.W.boss.st!=='enter'", timeout=8000)
        pg.evaluate("(()=>{const b=__nbd.W.boss; b.set('vent'); b.hp=2; b.takeHit({dmg:9, dir:1, from:__nbd.W.heroes[0]});})()")
        pg.wait_for_function(f"{SC}==='tally'", timeout=10000); time.sleep(3.3); key(pg, 'KeyJ', after=0.4)
        check('Radiology tally -> v0.9 scooter cutscene', pg.evaluate("__nbd.game.cut.id") == 'scoot')
        time.sleep(1.0); key(pg, 'KeyK', after=0.6); pg.wait_for_function(f"{SC}==='scoot'", timeout=6000); time.sleep(1.0)
        pg.evaluate(SKIP_SCOOT); pg.wait_for_function(f"{SC}==='stally'", timeout=8000); time.sleep(3.3); key(pg, 'KeyJ', after=0.4)
        check('scooter tally -> night cutscene', pg.evaluate("__nbd.game.cut.id") == 'night')
        time.sleep(6.6); pg.screenshot(path='tests/out/v05_cut_night.png'); key(pg, 'KeyK', after=0.4)
        check('-> Night Shift', pg.evaluate("__nbd.W.lv.id") == 3 and pg.evaluate(SC) in ('intro', 'play'))
        pg.wait_for_function(f"{SC}==='play'", timeout=6000); pg.evaluate("__nbd.W.cleared = true")
        pg.wait_for_function(f"{SC}==='tally'", timeout=5000); time.sleep(3.3); fin = pg.evaluate("__nbd.game.tally[0].total"); key(pg, 'KeyJ', after=0.4)
        check('night tally -> ending cutscene', pg.evaluate("__nbd.game.cut.id") == 'ending')
        time.sleep(6.5); pg.screenshot(path='tests/out/v05_cut_ending.png'); key(pg, 'KeyK', after=0.5)
        check('-> THE END with a new high score', pg.evaluate(SC) == 'ending' and pg.evaluate("__nbd.game.newHi") and pg.evaluate("__nbd.save.hi[0].s") == fin and pg.evaluate("__nbd.save.best") == 3, [fin, pg.evaluate("__nbd.save.hi[0]")])
        time.sleep(1.7); pg.screenshot(path='tests/out/v05_ending.png'); key(pg, 'KeyJ', after=0.5)
        check('ending -> high scores -> title', pg.evaluate(SC) == 'scores'); time.sleep(0.6); key(pg, 'KeyJ', after=0.5)
        check('...title', pg.evaluate(SC) == 'title')
        pg.close()
    # ================================================================ F: 2P carry-over + continues, gamepad, touch
    if 'F' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?god=1'); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.6)
        key(pg, 'KeyS'); key(pg, 'Enter', after=0.4); key(pg, 'Comma', after=0.3); key(pg, 'KeyJ', after=0.3); key(pg, 'ArrowRight'); key(pg, 'Comma', after=1.2)
        pg.wait_for_function(f"{SC}==='cutscene'", timeout=8000); key(pg, 'KeyK', after=0.4)
        pg.wait_for_function(f"{SC}==='play'", timeout=8000)
        check('2P game started', pg.evaluate("__nbd.W.heroes.length") == 2)
        pg.evaluate("(()=>{const W=__nbd.W; W.heroes[0].score=1000; W.heroes[1].score=2000; W.cleared=true;})()")
        pg.wait_for_function(f"{SC}==='tally'", timeout=5000); time.sleep(3.3); key(pg, 'KeyJ', after=0.9); key(pg, 'KeyK', after=0.4)
        pg.wait_for_function(f"{SC}==='bonus'", timeout=6000); time.sleep(2.4); pg.evaluate("__nbd.B.left = 0.3")
        pg.wait_for_function(f"{SC}==='btally'", timeout=12000); time.sleep(3.3)
        sc = pg.evaluate("__nbd.W.heroes.map(h=>h.score)"); key(pg, 'KeyJ', after=0.9); key(pg, 'KeyK', after=0.6)
        pg.wait_for_function(f"__nbd.W.lv.id===2 && {SC}==='play'", timeout=8000)
        r = pg.evaluate("__nbd.W.heroes.map(h=>[h.score, h.st, h.devs])")
        check('2P carries into Radiology (both nurses, scores, devices)', len(r) == 2 and [x[0] for x in r] == sc and r[1][2], r)
        x0 = pg.evaluate("__nbd.W.heroes[1].x"); pg.keyboard.down('ArrowRight'); time.sleep(0.5); pg.keyboard.up('ArrowRight')
        check('P2 still drives with the arrows on Floor 4', pg.evaluate("__nbd.W.heroes[1].x") > x0 + 10)
        pg.screenshot(path='tests/out/v05_2p_radiology.png')
        # P2 is KO'd with no lives: at the next floor they can still continue in
        pg.evaluate("(()=>{const h=__nbd.W.heroes[1]; h.lives=0; h.hp=0; h.set('out'); h.continueT=0; __nbd.W.cleared=true;})()")
        pg.wait_for_function(f"{SC}==='tally'", timeout=5000); time.sleep(3.3); key(pg, 'KeyJ', after=0.9); key(pg, 'KeyK', after=0.6)
        pg.wait_for_function(f"{SC}==='scoot'", timeout=6000); time.sleep(1.0)  # v0.9: through the Scooter Run (fast-forwarded)
        pg.evaluate(SKIP_SCOOT); pg.wait_for_function(f"{SC}==='stally'", timeout=8000); time.sleep(3.3); key(pg, 'KeyJ', after=0.9); key(pg, 'KeyK', after=0.6)
        pg.wait_for_function(f"__nbd.W.lv.id===3 && {SC}==='play'", timeout=8000)
        check("night: the KO'd partner gets a continue countdown", pg.evaluate("__nbd.W.heroes[1].st") == 'out' and pg.evaluate("__nbd.W.heroes[1].continueT") > 0)
        key(pg, 'Comma', after=0.5)
        check('P2 continues back onto the night shift', pg.evaluate("__nbd.W.heroes[1].st") != 'out' and pg.evaluate("__nbd.game.creditsUsed") == 1)
        time.sleep(2.0); pg.screenshot(path='tests/out/v05_2p_night.png')
        pg.close()
        # gamepad on Radiology
        pg = b.new_page(viewport={'width': 960, 'height': 540}); pg.add_init_script(MOCK); watch(pg)
        pg.goto(U + '?level=2&hero=jackie&god=1'); ready(pg); pg.evaluate('__padConnect()'); time.sleep(0.3)
        x0 = pg.evaluate("__nbd.W.heroes[0].x"); pg.evaluate("__pad.axes[0]=1; __pad.timestamp++"); time.sleep(0.6); pg.evaluate("__pad.axes[0]=0; __pad.timestamp++"); time.sleep(0.1)
        pg.evaluate('__padSet(0, true)'); time.sleep(0.1); pg.evaluate('__padSet(0, false)'); time.sleep(0.05); jz = pg.evaluate("__nbd.W.heroes[0].z")
        check('gamepad moves and jumps on Radiology', pg.evaluate("__nbd.W.heroes[0].x") > x0 + 20 and jz > 0, jz)
        pg.close()
        # touch on the night shift
        UA = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36'
        ctx = b.new_context(viewport={'width': 915, 'height': 412}, device_scale_factor=2.6, is_mobile=True, has_touch=True, user_agent=UA)
        pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg); watch(pg)
        def touch(kind, pts): cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [{'x': x, 'y': y, 'id': i} for i, x, y in pts]})
        pg.goto(U + '?level=3&hero=kim&god=1'); ready(pg); time.sleep(0.5)
        jx, jy = 915 * 0.18, 412 * 0.7; x0 = pg.evaluate("__nbd.W.heroes[0].x")
        touch('touchStart', [(1, jx, jy)]); time.sleep(0.05)
        for k in range(10): touch('touchMove', [(1, jx + k * 5, jy)]); time.sleep(0.02)
        time.sleep(0.8); touch('touchEnd', []); time.sleep(0.2)
        bx = pg.locator('#pad .ab[data-b=jmp]').bounding_box(); touch('touchStart', [(2, bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2)]); time.sleep(0.08); touch('touchEnd', []); time.sleep(0.1)
        check('touch joystick + JUMP work on the night shift', pg.evaluate("__nbd.W.heroes[0].x") > x0 + 20 and pg.evaluate("__nbd.W.heroes[0].z") > 0)
        pg.screenshot(path='tests/out/v05_touch_night.png')
        ctx.close()
    # ================================================================ G: bot plays Radiology and the night shift start to finish (no softlocks)
    if 'G' in ONLY:
        # real-time bot run: on a loaded machine this takes a while, so it waits on progress (fails only if nothing moves for 120 s)
        def run_floor(lv, limit):
            t0 = time.time(); seen = set(); last = None; lastT = time.time(); s = None
            while time.time() - t0 < limit:
                s = pg.evaluate("(()=>{const W=__nbd.W; return [__nbd.game.scene, W.lv.id, W.zone, W.boss?W.boss.name+':'+Math.round(W.boss.hp):'', W.heroes[0].x|0, W.camX|0, W.enemies.length, W.dark];})()")
                seen.add(s[3].split(':')[0])
                if s[0] == 'tally' and s[1] == lv: break
                sig = (s[2], s[3], s[4] // 40, s[5], s[6])
                if sig != last: last = sig; lastT = time.time()
                elif time.time() - lastT > 120: break  # softlock
                time.sleep(1)
            return s, seen, round(time.time() - t0)
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=2&hero=will&god=1&bot=1'); pg.wait_for_function('window.__loaded === true', timeout=30000)
        s, seen, dt = run_floor(2, 1500)
        check('bot: Radiology start to finish (Lou + MRI) without a softlock', s[0] == 'tally' and s[1] == 2 and 'LEAD-APRON LOU' in seen and 'MAGNA-SCAN 3000' in seen, [s, dt])
        pg.wait_for_function(f"{SC}==='tally' && __nbd.game.t > 3.2", timeout=20000); key(pg, 'KeyJ', after=0.6)
        pg.wait_for_function(f"{SC}==='stally' && __nbd.game.t > 3.2", timeout=240000); key(pg, 'KeyJ', after=0.6)  # v0.9: the bot rides the Scooter Run too
        pg.wait_for_function("__nbd.W.lv.id === 3", timeout=10000)
        s, seen, dt = run_floor(3, 1200)
        check('bot: Night Shift start to finish without a softlock', s[0] == 'tally' and s[1] == 3, [s, dt])
        pg.wait_for_function(f"{SC}==='tally' && __nbd.game.t > 3.2", timeout=20000); key(pg, 'KeyJ', after=0.6)
        check('-> THE END', pg.evaluate(SC) == 'ending')
        pg.close()
    b.close()
print('ALL PASS' if ok else 'SOME FAILED')
print('\n'.join(errs[:30]) or 'no console errors')
