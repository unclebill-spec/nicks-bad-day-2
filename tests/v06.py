# v0.6: nurses pick up small / medium props and throw them (golden-axe style), with keyboard / gamepad / touch / 2P,
# priorities vs grab-a-patient / weapons / gurney rides, jump-throws, depth + back throws, hits drop it, loose meal
# trays; and Turbo Tilly scaled to boss size (>= 5x a nurse) with a fair, readable charge-lane fight.
# v0.6 (part 2): Code Blue meter tiers (Ativan jab at 1/3, defib paddles at full), three-day-old pizza + SNAP STIX,
# and the Fire Alarm Yeller event (any floor, capped, never in boss fights, REDUCED FLASHING setting).
# Screenshots -> tests/out/v06_*.png
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
FREEZE = "(()=>{const W=__nbd.W; W.enemies.forEach(e=>{e.alive=false}); W.enemies.length=0; W.queue && (W.queue.length=0); W.items.length=0; W.shots.length=0; W.zone=99; W.zoneOn=false; W.lockX=W.camX; W.heroes.forEach((h,i)=>{h.x=W.camX+90; h.y=176+i*20; h.face=1; h.carry=null; h.weapon=null; h.held=null; h.ride=null; h.set('idle');}); W.props=W.props.filter(p=>p.x<W.camX-60||p.x>W.camX+__nbd.G.VW+60);})()"
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

with sync_playwright() as p:
    b = p.chromium.launch()
    # ================================================================ A: lift, carry, throw through a line of patients (keyboard)
    if 'A' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=nick&god=1&nocut=1'); ready(pg); pg.evaluate(FREEZE); time.sleep(0.2)
        n0 = pg.evaluate("__nbd.W.props.length")
        i = prop(pg, 'chair', 12)
        key(pg, 'KeyH', after=0.05); s1 = hs(pg); time.sleep(0.35); s2 = hs(pg)
        inworld = pg.evaluate(f"__nbd.W.props.includes(PP[{i}])")
        check('GRAB at a chair lifts it overhead (out of the world while carried)', s1['st'] == 'lift' and s2['carry'] == 'chair' and s2['st'] == 'idle' and not inworld, [s1, s2])
        pg.screenshot(path='tests/out/v06_carry.png')
        # carrying slows her down and she can't run
        x0 = hs(pg)['x']; pg.keyboard.down('KeyD'); time.sleep(0.6); pg.keyboard.up('KeyD'); x1 = hs(pg)['x']
        pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; window.CC=h.carry; h.carry=null;})()"); pg.evaluate("__nbd.W.heroes[0].x-=60")
        x2 = hs(pg)['x']; pg.keyboard.down('KeyD'); time.sleep(0.6); pg.keyboard.up('KeyD'); x3 = hs(pg)['x']
        pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.carry=CC; h.x=__nbd.W.camX+70;})()"); time.sleep(0.1)
        check('carrying slows the nurse (~0.75x walk)', 0.55 < (x1 - x0) / max(1, (x3 - x2)) < 0.9, [round(x1 - x0), round(x3 - x2)])
        pg.keyboard.down('ShiftLeft'); pg.keyboard.down('KeyD'); time.sleep(0.3); st = hs(pg)['st']; pg.keyboard.up('KeyD'); pg.keyboard.up('ShiftLeft')
        check('no running while carrying', st == 'walk', st)
        pg.evaluate("__nbd.W.heroes[0].x=__nbd.W.camX+60"); time.sleep(0.1)
        fs = [foe(pg, 'wanderer', d) for d in (60, 100, 140)]
        hp0 = pg.evaluate("F.map(e=>e.hp)")
        sm0 = pg.evaluate("__nbd.W.stats.props||0")
        key(pg, 'KeyJ', after=0.05); time.sleep(0.12)
        fl = pg.evaluate(f"(()=>{{const p=PP[{i}]; return {{fly:!!p.flying, z:p.z, vx:p.vx, in:__nbd.W.props.includes(p)}};}})()")
        time.sleep(0.12); pg.screenshot(path='tests/out/v06_throw.png')
        check('ATK throws it: the prop flies forward', fl['fly'] and fl['vx'] > 200 and fl['in'], fl)
        time.sleep(1.0)
        r = pg.evaluate(f"(()=>{{const p=PP[{i}]; return {{st:p.st, fly:!!p.flying, hp:F.map(e=>e.hp), est:F.map(e=>e.st), props:__nbd.W.stats.props||0, hero:__nbd.W.heroes[0].st, combo:__nbd.W.heroes[0].maxCombo}};}})()")
        check('the throw hits EVERY patient in its path (all three bowled over)', all(a < b0 for a, b0 in zip(r['hp'], hp0)) and all(s in ('fall', 'down', 'getup', 'dead', 'hurt') for s in r['est']), [hp0, r['hp'], r['est']])
        check('the prop breaks on impact with the break FX (counted as a smashed prop)', r['st'] == 2 and not r['fly'] and r['props'] == sm0 + 1, r)
        check('the nurse is back to normal after the throw', r['hero'] == 'idle')
        # Attack at a prop with nobody in reach lifts it (TMNT style)
        pg.evaluate("(()=>{F.forEach(e=>{e.alive=false}); __nbd.W.enemies.length=0;})()"); time.sleep(0.3)
        i2 = prop(pg, 'trash', 10)
        key(pg, 'KeyJ', after=0.45)
        check('ATK at a trash can with no patient in reach picks it up', hs(pg)['carry'] == 'trash', hs(pg))
        # jump-throw
        key(pg, 'KeyK', after=0.22); z = hs(pg)['z']; key(pg, 'KeyJ', after=0.05)
        jt = pg.evaluate(f"(()=>{{const p=PP[{i2}]; return {{fly:!!p.flying, air:p.flying&&p.flying.air, vz:p.vz, z:p.z}};}})()")
        check('jump + ATK = jump-throw (angled down from the air)', z > 10 and jt['fly'] and jt['air'] and jt['vz'] < 0, [z, jt])
        time.sleep(1.2)
        check('jump-thrown trash can breaks on landing', pg.evaluate(f"PP[{i2}].st") == 2)
        pg.close()
    # ================================================================ B: priorities and what can't be lifted
    if 'B' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=kim&god=1&nocut=1'); ready(pg); pg.evaluate(FREEZE); time.sleep(0.2)
        # patient + prop in reach: GRAB grabs the patient
        i = prop(pg, 'plant', 10); f = foe(pg, 'wanderer', 16)
        key(pg, 'KeyH', after=0.1)
        check('GRAB with a patient and a prop in reach grabs the patient', hs(pg)['st'] in ('grab', 'knee') and hs(pg)['carry'] is None, hs(pg))
        pg.evaluate(FREEZE); time.sleep(0.2)
        # patient in punch range + prop at feet: ATK punches
        i = prop(pg, 'plant', 8); f = foe(pg, 'wanderer', 34)
        key(pg, 'KeyJ', after=0.05)
        check('ATK with a patient in punch range punches (does not lift)', hs(pg)['st'] == 'atk' and hs(pg)['carry'] is None, hs(pg))
        pg.evaluate(FREEZE); time.sleep(0.3)
        # gurney + prop: GRAB rides the gurney
        g = prop(pg, 'gurney', 20); i = prop(pg, 'chair', 6)
        key(pg, 'KeyH', after=0.1)
        check('GRAB next to a gurney still starts a gurney ride', hs(pg)['st'] == 'ride', hs(pg))
        time.sleep(3.6); pg.evaluate(FREEZE); time.sleep(0.3)
        # weapon on the floor + prop: GRAB takes the weapon
        pg.evaluate("__nbd.drop('w:mop')"); i = prop(pg, 'chair', 10)
        key(pg, 'KeyH', after=0.4)
        check('GRAB on a weapon (with a prop next to it) picks up the weapon', hs(pg)['w'] == 'mop' and hs(pg)['carry'] is None, hs(pg))
        # with a weapon in hand: GRAB at a prop swaps to carrying (the weapon drops at her feet)
        key(pg, 'KeyH', after=0.4)
        it = pg.evaluate("__nbd.W.items.filter(i=>!i.gone&&i.weapon).map(i=>i.k)")
        check('weapon in hand + GRAB at a prop: drops the weapon and lifts the prop', hs(pg)['carry'] == 'chair' and hs(pg)['w'] is None and 'w:mop' in it, [hs(pg), it])
        # taking a hit drops it
        pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.inv=0; h.takeHit({dmg:1, dir:-1, kb:30, stun:0.2});})()"); time.sleep(0.05)
        d = pg.evaluate("(()=>{const W=__nbd.W, h=W.heroes[0]; const p=W.props.find(p=>p.kind==='chair'); return {carry:h.carry, st:h.st, back:!!p, hp:p&&p.hp};})()")
        check('taking a hit makes her drop it (it tumbles back into the world, a little damaged)', d['carry'] is None and d['back'] and d['st'] == 'hurt', d)
        pg.evaluate(FREEZE); time.sleep(0.3)
        # large props stay kick-only
        res = {}
        for k in ('crashcart', 'supplycart', 'vending', 'gurney'):
            pg.evaluate(FREEZE); time.sleep(0.1); j = prop(pg, k, 12 if k != 'gurney' else 200)
            if k == 'gurney':
                pg.evaluate(f"(()=>{{const h=__nbd.W.heroes[0]; window.CAN=h.liftTarget(); }})()"); res[k] = pg.evaluate("!!window.CAN")
            else:
                key(pg, 'KeyH', after=0.3); res[k] = hs(pg)['carry'] is not None
        check('crash carts / supply carts / vending machines / gurneys cannot be lifted', not any(res.values()), res)
        # everything small / medium can
        okk = {}
        for k in ('trash', 'chair', 'plant', 'wetfloor', 'linen', 'o2tank', 'ivstand', 'wheelchair', 'medcart', 'apronrack', 'contrastcart', 'viewer', 'mealtray'):
            pg.evaluate(FREEZE); time.sleep(0.05); prop(pg, k, 10); key(pg, 'KeyH', after=0.35); okk[k] = hs(pg)['carry'] == k
        check('every small / medium prop can be lifted', all(okk.values()), okk)
        pg.screenshot(path='tests/out/v06_mealtray.png')
        pg.close()
    # ================================================================ C: directions, back throw, loose trays, magnet
    if 'C' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=will&god=1&nocut=1'); ready(pg); pg.evaluate(FREEZE); time.sleep(0.2)
        def lift(k='chair'):
            pg.evaluate(FREEZE); pg.evaluate("__nbd.W.heroes[0].x=__nbd.W.camX+200"); time.sleep(0.05); j = prop(pg, k, 10); key(pg, 'KeyH', after=0.35); return j
        j = lift(); pg.keyboard.down('KeyA'); time.sleep(0.12); key(pg, 'KeyJ', after=0.05); pg.keyboard.up('KeyA'); time.sleep(0.1)
        check('throw left', pg.evaluate(f"PP[{j}].vx") < -200 or pg.evaluate(f"PP[{j}].st") == 2, pg.evaluate(f"[PP[{j}].vx, PP[{j}].st]"))
        j = lift(); pg.keyboard.down('KeyW'); key(pg, 'KeyJ', after=0.12); pg.keyboard.up('KeyW')
        up = pg.evaluate(f"[PP[{j}].vx, PP[{j}].vy]")
        j = lift(); pg.keyboard.down('KeyS'); key(pg, 'KeyJ', after=0.12); pg.keyboard.up('KeyS')
        dn = pg.evaluate(f"[PP[{j}].vx, PP[{j}].vy]")
        check('hold up / down to throw diagonally along the floor depth', up[1] < -50 and dn[1] > 50 and up[0] > 200, [up, dn])
        time.sleep(0.8)
        j = lift(); pg.keyboard.down('KeyJ'); pg.keyboard.down('KeyK'); time.sleep(0.06); pg.keyboard.up('KeyJ'); pg.keyboard.up('KeyK'); time.sleep(0.15)
        check('ATK+JUMP while carrying throws it behind her', pg.evaluate(f"PP[{j}].vx") < -200 or (pg.evaluate(f"PP[{j}].st") == 2 and pg.evaluate(f"PP[{j}].x") < pg.evaluate("__nbd.W.heroes[0].x")), pg.evaluate(f"[PP[{j}].vx, PP[{j}].st]"))
        time.sleep(0.8)
        # GRAB also throws while carrying
        j = lift(); key(pg, 'KeyH', after=0.15)
        check('GRAB while carrying throws too', pg.evaluate(f"!!PP[{j}].flying || PP[{j}].st===2"))
        time.sleep(0.8)
        # throwing at the wall breaks it at the screen edge
        j = lift(); pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.x=__nbd.W.camX+__nbd.G.VW-40;})()"); key(pg, 'KeyJ', after=0.6)
        check('a throw into the screen edge breaks on the wall', pg.evaluate(f"PP[{j}].st") == 2 and pg.evaluate(f"PP[{j}].x") <= pg.evaluate("__nbd.W.camX+__nbd.G.VW"))
        # loose meal trays: a missed tray lands as a carryable prop
        pg.evaluate(FREEZE); time.sleep(0.1)
        f = foe(pg, 'tray', 170, 30)
        pg.evaluate("(()=>{const W=__nbd.W, e=F[F.length-1]; W.shots.push({kind:'enemy', spr:'p_tray', x:e.x-20, y:e.y, z:10, vx:-185, vz:0, grav:60, owner:e, dmg:7, spin:10, life:2.2, t:0, hit:new Set()});})()")
        time.sleep(0.8)
        mt = pg.evaluate("__nbd.W.props.filter(p=>p.kind==='mealtray'&&p.st<2).length")
        check('a missed meal tray stays on the floor as a loose, throwable prop', mt >= 1, mt)
        pg.close()
        # MRI magnet yanks a metal prop out of her hands
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=2&zone=5&hero=jackie&god=1&nocut=1'); pg.wait_for_function("window.__loaded===true && __nbd.W.boss && __nbd.W.boss.isMRI && __nbd.W.boss.st!=='enter'", timeout=40000); time.sleep(0.3)
        r = pg.evaluate("(()=>{const W=__nbd.W, h=W.heroes[0], B=W.boss; h.set('idle'); h.x=B.front-150; h.y=176; h.face=1; const i=__nbd.prop('apronrack',0,0); const p=W.props[i]; p.x=h.x+10; p.y=h.y; h.lift(p); return [B.kind||B.name, h.carry&&h.carry.kind];})()")
        time.sleep(0.4)
        pg.evaluate("(()=>{const B=__nbd.W.boss; B.set('pull'); B.cd=0;})()"); time.sleep(0.4)
        r2 = pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; return [h.carry, __nbd.W.props.filter(p=>p.kind==='apronrack').map(p=>[p.magnet, p.st])];})()")
        check('MRI magnet tears a carried metal prop out of her hands', r[1] == 'apronrack' and r2[0] is None and len(r2[1]) > 0, [r, r2])
        pg.close()
    # ================================================================ D: touch (PICK UP / THROW button), gamepad, 2P
    if 'D' in ONLY:
        UA = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36'
        ctx = b.new_context(viewport={'width': 915, 'height': 412}, device_scale_factor=2.6, is_mobile=True, has_touch=True, user_agent=UA)
        pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg); watch(pg)
        def touch(kind, pts): cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [{'x': x, 'y': y, 'id': i} for i, x, y in pts]})
        def tap(name):
            bx = pg.locator(f'#pad .ab[data-b={name}]').bounding_box(); touch('touchStart', [(5, bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2)]); time.sleep(0.08); touch('touchEnd', []); time.sleep(0.1)
        pg.goto(U + '?level=1&hero=jackie&god=1&nocut=1'); ready(pg); pg.evaluate(FREEZE); time.sleep(0.3)
        lab0 = pg.evaluate("document.getElementById('b_grab').dataset.ctx || document.getElementById('b_grab').textContent")
        j = prop(pg, 'wetfloor', 10); time.sleep(0.2)
        lab1 = pg.evaluate("document.getElementById('b_grab').dataset.ctx")
        pg.screenshot(path='tests/out/v06_touch_pickup.png')
        tap('grab'); time.sleep(0.35)
        lab2 = pg.evaluate("document.getElementById('b_grab').dataset.ctx"); c = hs(pg)['carry']
        pg.screenshot(path='tests/out/v06_touch_throw.png')
        tap('grab'); time.sleep(0.15)
        thrown = pg.evaluate(f"!!PP[{j}].flying || PP[{j}].st===2")
        check('touch: GRAB button shows PICK UP at a prop, THROW while carrying, and does both', lab0 == 'GRAB' and lab1 == 'PICK UP' and c == 'wetfloor' and lab2 == 'THROW' and thrown, [lab0, lab1, c, lab2, thrown])
        time.sleep(0.6); pg.evaluate(FREEZE); g = prop(pg, 'gurney', 20); time.sleep(0.2)
        check('touch: next to a gurney the button still says RIDE', pg.evaluate("document.getElementById('b_grab').dataset.ctx") == 'RIDE')
        pg.evaluate(FREEZE); j = prop(pg, 'chair', 10); time.sleep(0.2); tap('atk'); time.sleep(0.4)
        check('touch: ATK at a prop lifts it too', hs(pg)['carry'] == 'chair')
        tap('atk'); time.sleep(0.15)
        check('touch: ATK throws', pg.evaluate(f"!!PP[{j}].flying || PP[{j}].st===2"))
        ctx.close()
        # gamepad: B (grab) lifts, X (attack) throws
        pg = b.new_page(viewport={'width': 960, 'height': 540}); pg.add_init_script(MOCK); watch(pg)
        pg.goto(U + '?level=1&hero=nick&god=1&nocut=1'); ready(pg); pg.evaluate('__padConnect()'); pg.evaluate(FREEZE); time.sleep(0.3)
        j = prop(pg, 'linen', 12)
        pg.evaluate('__padSet(1, true)'); time.sleep(0.1); pg.evaluate('__padSet(1, false)'); time.sleep(0.35)
        c = hs(pg)['carry']
        pg.evaluate('__padSet(2, true)'); time.sleep(0.1); pg.evaluate('__padSet(2, false)'); time.sleep(0.12)
        check('gamepad: B lifts the hamper, X throws it', c == 'linen' and pg.evaluate(f"!!PP[{j}].flying || PP[{j}].st===2"), c)
        pg.close()
        # 2P: P2 lifts with M and throws with Comma while P1 carries something else
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?god=1'); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.6)
        key(pg, 'KeyS'); key(pg, 'Enter', after=0.4); key(pg, 'Comma', after=0.3); key(pg, 'KeyJ', after=0.3); key(pg, 'ArrowRight'); key(pg, 'Comma', after=1.2)
        pg.wait_for_function(f"{SC}==='cutscene'", timeout=8000); time.sleep(0.5); key(pg, 'KeyK', after=0.4)
        pg.wait_for_function(f"{SC}==='play' && __nbd.W.heroes.length===2 && __nbd.W.heroes[1].st==='idle'", timeout=12000); pg.evaluate(FREEZE); time.sleep(0.3)
        a = prop(pg, 'chair', 10, 0, 0); bb = prop(pg, 'trash', 10, 0, 1)
        key(pg, 'KeyH', after=0.1); key(pg, 'KeyM', after=0.4)
        both = [hs(pg, 0)['carry'], hs(pg, 1)['carry']]
        key(pg, 'Comma', after=0.15)
        check('2P: each nurse lifts their own prop (H / M) and P2 throws with Comma', both == ['chair', 'trash'] and hs(pg, 1)['carry'] is None and hs(pg, 0)['carry'] == 'chair', [both, hs(pg, 1)])
        pg.screenshot(path='tests/out/v06_2p_carry.png')
        pg.close()
    # ================================================================ E: boss-sized Turbo Tilly
    if 'E' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&zone=5&hero=nick&god=1&nocut=1'); pg.wait_for_function(f"window.__loaded===true && {SC}==='play'", timeout=30000)
        pg.wait_for_function("__nbd.W.boss && __nbd.W.boss.st!=='enter'", timeout=30000); time.sleep(0.3)
        t = pg.evaluate(f"({BOUNDS})('tilly','idle')"); n = pg.evaluate(f"({BOUNDS})('nick','idle')")
        wr, ar = t[0] / n[0], t[2] / n[2]
        check("Tilly is boss-sized: >= 5x a nurse by width and by area (Bill's rule)", wr >= 5 and ar >= 5, {'tilly': t, 'nurse': n, 'width_x': round(wr, 1), 'area_x': round(ar, 1), 'height_x': round(t[1] / n[1], 1)})
        B = pg.evaluate("(()=>{const B=__nbd.W.boss; return {w:B.w, h:B.h, x:B.x, cam:__nbd.W.camX};})()")
        check('her hitbox grew with her (w >= 90, h >= 120)', B['w'] >= 90 and B['h'] >= 120, B)
        pg.screenshot(path='tests/out/v06_tilly.png')
        # lane telegraph + honest lane lock: a nurse 30px off her lane is safe; one in her lane gets hit
        r = pg.evaluate("""(()=>{const W=__nbd.W, B=W.boss, [a]=W.heroes; W.enemies.forEach(e=>e.alive=false); W.enemies.length=0;
          a.set('idle'); a.x=W.camX+60; a.y=B.y; a.inv=0; B.x=W.camX+300; B.face=-1; B.cd=0; B.honkCd=99; B.callCd=99; B.set('rev'); B.charges=1; return B.y;})()""")
        time.sleep(0.75)
        lane = pg.evaluate("(()=>{const W=__nbd.W, B=W.boss, a=W.heroes[0]; const y0=B.y; a.y = y0 + 32 > 212 ? y0 - 32 : y0 + 32; return [B.st, y0];})()")
        pg.screenshot(path='tests/out/v06_tilly_lane.png')
        time.sleep(1.6)
        r1 = pg.evaluate("(()=>{const W=__nbd.W, B=W.boss, a=W.heroes[0]; return [a.st, a.hp, B.st, B.y];})()")
        check('the charge lane locks before she goes: a nurse who steps out of the flashing lane is safe', lane[0] == 'rev' and r1[0] not in ('fall', 'down') and abs(r1[3] - lane[1]) < 1, [lane, r1])
        pg.evaluate("""(()=>{const W=__nbd.W, B=W.boss, a=W.heroes[0]; a.set('idle'); a.inv=0; a.x=W.camX+60; B.x=W.camX+300; B.face=-1; B.set('rev'); B.charges=1; a.y=B.y;})()""")
        time.sleep(0.3); pg.evaluate("(()=>{const W=__nbd.W, a=W.heroes[0]; a.y=W.boss.y;})()"); time.sleep(1.6)
        r2 = pg.evaluate("(()=>{const W=__nbd.W, B=W.boss, a=W.heroes[0]; return [a.st, B.st, B.x - W.camX];})()")
        check('a nurse standing in the lane gets run over', r2[0] in ('fall', 'down', 'getup'), r2)
        bx = pg.evaluate("(()=>{const W=__nbd.W, B=W.boss; return [B.x - W.camX, __nbd.G.VW];})()")
        check('she stays fully on screen after the charge (wall stop accounts for her size)', 50 <= bx[0] <= bx[1] - 50, bx)
        # weak point: battery open -> full damage; closed -> armour
        d = pg.evaluate("""(()=>{const W=__nbd.W, B=W.boss, a=W.heroes[0]; B.set('idle'); B.cd=99; const h0=B.hp; B.takeHit({dmg:10, dir:1, from:a}); const h1=B.hp; B.set('open'); B.takeHit({dmg:10, dir:1, from:a}); return [h0-h1, h1-B.hp];})()""")
        check('battery panel is still the weak point (armoured otherwise)', d[1] > d[0] * 2, d)
        # a thrown chair hits her (boss armour), and the solid chair keeps nurses out of her body
        pg.evaluate("(()=>{const W=__nbd.W, B=W.boss, a=W.heroes[0]; B.set('open'); B.t=0; a.set('idle'); a.x=B.x-140; a.y=B.y; a.face=1; const i=__nbd.prop('chair',0,0); const p=W.props[i]; p.x=a.x+10; p.y=a.y; a.lift(p); window.BH=B.hp;})()")
        time.sleep(0.4); key(pg, 'KeyJ', after=0.8)
        hit = pg.evaluate("window.BH - __nbd.W.boss.hp")
        check('a thrown prop hits the big boss and breaks on her', hit > 5, hit)
        pg.evaluate("(()=>{const W=__nbd.W, B=W.boss, a=W.heroes[0]; B.set('idle'); B.cd=99; a.set('idle'); a.x=B.x-10; a.y=B.y;})()"); time.sleep(0.1)
        dx = pg.evaluate("Math.abs(__nbd.W.heroes[0].x-__nbd.W.boss.x)")
        check('her chair is solid at the new size (a nurse is pushed out of it)', dx >= 50, dx)
        # finish the fight: she still goes down and the floor completes
        pg.evaluate("(()=>{const B=__nbd.W.boss; B.set('open'); B.takeHit({dmg:9999, dir:1, from:__nbd.W.heroes[0]});})()"); time.sleep(1.0)
        pg.screenshot(path='tests/out/v06_tilly_defeat.png')
        pg.wait_for_function(f"{SC}==='tally'", timeout=20000)
        check('defeating big Tilly still ends the floor (tally)', True)
        pg.close()
    # ================================================================ F: Code Blue meter tiers (Ativan jab at 1/3, defib paddles at full)
    if 'F' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=nick&god=1&nocut=1&noalarm=1'); ready(pg); pg.evaluate(FREEZE); time.sleep(0.2)
        pg.evaluate("window.F=[]")
        e = foe(pg, 'wanderer', 34)
        pg.evaluate("__nbd.W.heroes[0].meter=40"); hp0 = pg.evaluate(f"F[{e}].hp"); time.sleep(0.15)
        sp = pg.evaluate("document.getElementById('b_sp').textContent")
        key(pg, 'KeyL', after=0.05); s1 = hs(pg)
        time.sleep(0.6); pg.screenshot(path='tests/out/v06_ativan.png')
        r = pg.evaluate(f"(()=>{{const e=F[{e}],h=__nbd.W.heroes[0]; return {{st:e.st, hp:e.hp, sleep:(e.sleepT||0)-__nbd.W.t, meter:h.meter, shout:(h.shoutT||0)>__nbd.W.t}};}})()")
        check('1/3 meter: SP = the Ativan jab (not the desperation special)', s1['st'] == 'ativan', s1)
        check('"IT\'S TIME FOR SOME ATIVAN!" speech bubble is up', r['shout'], r)
        check('the jab costs exactly one third of the meter', abs(r['meter'] - (40 - 100 / 3)) < 0.5, r['meter'])
        check('the jabbed patient is knocked down hard and falls asleep', r['hp'] <= hp0 - 20 and r['st'] in ('fall', 'down') and r['sleep'] > 1.2, [hp0, r])
        time.sleep(1.2); st1 = pg.evaluate(f"F[{e}].st")
        check('...and stays down while asleep (zzz)', st1 == 'down', st1)
        pg.wait_for_function(f"F[{e}].st==='dizzy' || F[{e}].st==='getup'", timeout=8000); st2 = pg.evaluate(f"F[{e}].st")
        check('...then wakes up woozy', st2 in ('dizzy', 'getup'), st2)
        pg.evaluate("__nbd.W.heroes[0].meter=10"); key(pg, 'KeyL', after=0.1)
        check('under 1/3 meter SP is still the regular special', hs(pg)['st'] == 'special', hs(pg))
        time.sleep(0.8)
        # defib: facing direction only
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]")
        fa, fb, fc = foe(pg, 'wanderer', 70), foe(pg, 'wanderer', -60), foe(pg, 'wanderer', 210)
        pg.evaluate("__nbd.W.heroes[0].meter=100; __nbd.W.heroes[0].face=1"); time.sleep(0.15)
        sp2 = pg.evaluate("document.getElementById('b_sp').textContent")
        key(pg, 'KeyL', after=0.05); s2 = hs(pg); time.sleep(0.62)
        z = pg.evaluate(f"F.map(e=>e.st)"); pg.screenshot(path='tests/out/v06_defib.png')
        time.sleep(1.0)
        r = pg.evaluate("F.map(e=>({st:e.st, hp:e.hp}))")
        check('full meter: SP = Code Blue defib paddles', s2['st'] == 'super', s2)
        check('the lightning zaps patients in front (electrified skeleton state)', z[fa] == 'zapped' or r[fa]['hp'] < 38, [z, r])
        check('it reaches far down the hall in the facing direction', r[fc]['hp'] < 38, r)
        check('a patient BEHIND the nurse is untouched (facing direction only)', r[fb]['hp'] == pg.evaluate(f"F[{fb}].maxHp||38") or r[fb]['st'] not in ('fall', 'down', 'zapped', 'dead'), r)
        check('touch SP button shows ATIVAN / CODE BLUE by meter', sp == 'ATIVAN' or 'ATIVAN' in sp, [sp, sp2])
        check('touch SP button shows CODE BLUE at full meter', 'CODE' in sp2, sp2)
        pg.close()
        # boss stagger (Tilly)
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&zone=5&hero=nick&god=1&nocut=1'); pg.wait_for_function('window.__loaded === true', timeout=30000)
        pg.wait_for_function("window.__nbd && __nbd.W.boss && __nbd.W.boss.st!=='intro' && __nbd.game.scene==='play'", timeout=40000); time.sleep(1.0)
        pg.evaluate("(()=>{const W=__nbd.W,B=W.boss,h=W.heroes[0]; B.set('idle'); B.t=0; h.x=B.x-60; h.y=B.y; h.face=1; h.set('idle'); h.meter=40;})()"); time.sleep(0.05)
        hp0 = pg.evaluate("__nbd.W.boss.hp"); key(pg, 'KeyL', after=0.5)
        r = pg.evaluate("({hp:__nbd.W.boss.hp, stag:__nbd.W.boss.stagT, x:__nbd.W.boss.x, st:__nbd.W.boss.st})")
        time.sleep(0.25); x2 = pg.evaluate("__nbd.W.boss.x")
        check('Ativan on a boss: damage + a short stagger (no sleep)', r['hp'] < hp0 and r['stag'] > 0.1, [hp0, r])
        check('a staggered boss is frozen', abs(x2 - r['x']) < 2, [r['x'], x2])
        pg.close()
    # ================================================================ G: three-day-old pizza + SNAP STIX
    if 'G' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=nick&nocut=1&noalarm=1'); ready(pg); pg.evaluate(FREEZE); time.sleep(0.2)
        for k, heal in (('pizza', 45), ('snapstix', 30)):
            pg.evaluate(f"(()=>{{const h=__nbd.W.heroes[0]; h.hp=30; h.x=__nbd.W.camX+90; const it=__nbd.drop('{k}'); it.x=h.x+40; it.y=h.y; }})()"); time.sleep(0.2)
            if k == 'pizza': pg.screenshot(path='tests/out/v06_food.png')
            pg.keyboard.down('KeyD'); time.sleep(0.6); pg.keyboard.up('KeyD'); time.sleep(0.2)
            hp = pg.evaluate("__nbd.W.heroes[0].hp"); left = pg.evaluate(f"__nbd.W.items.filter(i=>i.k==='{k}').length")
            check(f'{k} heals {heal}', hp == 30 + heal and left == 0, [hp, left])
        t = pg.evaluate("""(async()=>{const D=await import('./src/data.js'); const has=(t,k)=>(D.LOOT[t]||[]).some(r=>r[0]===k);
          return {pc:['cart','linen','trash','small'].every(t=>has(t,'pizza')&&has(t,'snapstix')), vend:has('vending','snapstix'), pat:has('patient','pizza')&&has('patient','snapstix'), spr:!!(__nbd.G.atlas.sprites||__nbd.G.atlas).pizza||true};})()""")
        check('both foods are in the prop drop tables (carts, linen, trash, small props, vending)', t['pc'] and t['vend'], t)
        check('...and in the patient KO drop table', t['pat'], t)
        n = pg.evaluate("(()=>{let p=0,s=0; for(let i=0;i<4000;i++){const k=__nbd.rollLoot('trash'); if(k==='pizza')p++; if(k==='snapstix')s++;} return [p,s];})()")
        check('rolling trash-can loot actually produces pizza and SNAP STIX', n[0] > 0 and n[1] > 0, n)
        pg.close()
    # ================================================================ H: Fire Alarm Yeller
    if 'H' in ONLY:
        YS = "(()=>{const W=__nbd.W, y=W.enemies.find(e=>e.kind==='yeller'&&e.alive); return {y:y?y.st:null, alarm:!!W.alarm, uses:W.alarmUses||0, wet:W.wet||0, rage:W.enemies.filter(e=>e.alive&&e.rageT>W.t).length, pend:W.alarm?W.alarm.pend.length:0, zoneOn:W.zoneOn, alive:W.enemies.filter(e=>e.alive).length};})()"
        def toZone(pg):
            pg.keyboard.down('KeyD'); pg.wait_for_function("__nbd.W.zoneOn", timeout=40000); pg.keyboard.up('KeyD')
            pg.evaluate("__nbd.W.heroes[0].x=__nbd.W.camX+40")
        # H1: knock him down during the wind-up = no alarm; KO him = never
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=nick&god=1&nocut=1&yeller=1'); ready(pg); toZone(pg)
        pg.wait_for_function("__nbd.W.enemies.some(e=>e.kind==='yeller'&&e.st==='reach')", timeout=30000)
        pg.screenshot(path='tests/out/v06_yeller_reach.png')
        pg.evaluate("(()=>{const y=__nbd.W.enemies.find(e=>e.kind==='yeller'); window.Y=y; y.takeHit({dmg:4, dir:-1, kb:60, down:true, from:__nbd.W.heroes[0], force:true});})()")
        time.sleep(1.2); r = pg.evaluate(YS)
        check('knocking the Yeller down during the wind-up stops the pull', not r['alarm'] and r['uses'] == 0, r)
        pg.evaluate("Y.takeHit({dmg:999, dir:-1, kb:60, down:true, from:__nbd.W.heroes[0], force:true})"); time.sleep(3.0); r = pg.evaluate(YS)
        check('a KO\'d Yeller never pulls it', not r['alarm'] and r['uses'] == 0, r)
        pg.close()
        # H2: he pulls it: alarm, strobe, rain, wet floor, enraged, extra wave, zone can't clear early
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&hero=nick&god=1&nocut=1&yeller=1'); ready(pg); toZone(pg)
        pg.wait_for_function("!!__nbd.W.alarm", timeout=40000); time.sleep(0.6)
        r = pg.evaluate(YS); pg.screenshot(path='tests/out/v06_alarm.png')
        check('the Yeller pulls the alarm if nobody stops him', r['alarm'] and r['uses'] == 1, r)
        check('patients on screen get ENRAGED', r['rage'] >= 1, r)
        rg = pg.evaluate("(()=>{const W=__nbd.W,e=W.enemies.find(e=>e.alive&&e.rageT>W.t&&e.kind!=='yeller'); return e?{sp:e.spd?e.spd():0, k:e.kind}:null;})()")
        check('an extra wave is queued from the doors / elevators', r['pend'] >= 2, r)
        KILL = "(()=>{const W=__nbd.W; W.enemies.forEach(e=>{e.alive=false}); W.enemies.length=0; W.queue.length=0;})()"
        for i in range(8): pg.evaluate(KILL); time.sleep(0.15)
        r = pg.evaluate(YS)
        check('the zone can NOT clear while the alarm wave is still coming', r['zoneOn'] and r['pend'] >= 1 and r['alive'] == 0, r)
        time.sleep(1.5); r = pg.evaluate(YS); shots = pg.evaluate("__nbd.W.shots.filter(s=>s.kind==='puddle'&&s.wet).length")
        check('sprinklers soak the floor (wet sheen + slippery puddles)', r['wet'] > 0.8 and shots >= 1, [r, shots])
        pg.screenshot(path='tests/out/v06_alarm_rain.png')
        pg.wait_for_function("!__nbd.W.alarm", timeout=30000); r = pg.evaluate(YS)
        check('afterwards the sprinklers stop but the floor stays wet a while', r['wet'] > 0.3 and not r['alarm'], r)
        cleared = False
        for i in range(160):
            pg.evaluate(KILL); time.sleep(0.25)
            if not pg.evaluate("__nbd.W.zoneOn"): cleared = True; break
        check('...and the zone then clears normally (no softlock)', cleared, pg.evaluate(YS))
        # cap: once per wave-gap, max 2 per floor
        r = pg.evaluate("(()=>{const W=__nbd.W; W.zoneOn=true; const a=__nbd.maybeYeller(true); W.alarmUses=2; W.yellers=0; const b=__nbd.alarmAllowed(); W.alarmUses=1; W.zoneOn=false; return [a,b];})()")
        check('capped: no second yeller while one is pending this gap, and none after 2 alarms per floor', r[1] is False, r)
        pg.close()
        # H3: reduced flashing (Settings) vs full strobe: frame-to-frame brightness swing
        LUM = "(()=>{const c=document.querySelector('canvas'); const x=document.createElement('canvas'); x.width=48; x.height=27; const g=x.getContext('2d'); g.drawImage(c,0,0,48,27); const d=g.getImageData(0,0,48,27).data; let s=0; for(let i=0;i<d.length;i+=4) s+=d[i]*0.3+d[i+1]*0.59+d[i+2]*0.11; return s/(d.length/4);})()"
        swing = {}
        for mode in ('full', 'reduced'):
            pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
            pg.goto(U + '?level=1&hero=nick&god=1&nocut=1&noalarm=1'); ready(pg); pg.evaluate(FREEZE)
            pg.evaluate(f"(()=>{{__nbd.save.settings.flash='{mode}'; __nbd.applySettings(); const W=__nbd.W; W.zone=0; W.zoneOn=true; W.bossOn=false; W.noAlarm=false; const st=__nbd.stationFor(W.heroes[0]); __nbd.pullAlarm(st,null); W.alarm.pend=[];}})()")
            time.sleep(0.5); ls = []
            for i in range(24): ls.append(pg.evaluate(LUM)); time.sleep(0.04)
            swing[mode] = max(abs(a - b0) for a, b0 in zip(ls, ls[1:]))
            if mode == 'reduced':
                m = pg.evaluate("(()=>{const m=__nbd.settingsMenu(()=>{}); const it=m.items.find(i=>i.label==='FLASHING'); const v0=it.value(); it.right(); const v1=it.value(); it.left(); return [v0,v1,__nbd.save.settings.flash];})()")
                check('Settings has FLASHING: FULL / REDUCED', m[0] == 'REDUCED' and m[1] == 'FULL' and m[2] == 'reduced', m)
                pg.screenshot(path='tests/out/v06_alarm_reduced.png')
            pg.evaluate("__nbd.save.settings.flash='full'; __nbd.applySettings()")
            pg.close()
        check('REDUCED flashing swaps the strobe for a soft pulse (much smaller brightness swings)', swing['reduced'] < swing['full'] * 0.5, swing)
        # H4: never during boss fights, and it shuts off if a boss starts
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=1&zone=5&hero=nick&god=1&nocut=1&yeller=1'); pg.wait_for_function('window.__loaded === true', timeout=30000)
        pg.wait_for_function("window.__nbd && __nbd.W.boss && __nbd.game.scene==='play'", timeout=40000); time.sleep(0.5)
        r = pg.evaluate("[__nbd.alarmAllowed(), __nbd.maybeYeller(true), __nbd.W.enemies.some(e=>e.kind==='yeller'), (__nbd.W.queue||[]).some(q=>q.kind==='yeller')]")
        check('no Fire Alarm Yeller in a boss fight', r == [False, False, False, False], r)
        pg.close()
        # H5: works on every floor (Radiology, Night Shift): stations on the wall and a yeller joins
        for lv in (2, 3):
            pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
            pg.goto(U + f'?level={lv}&hero=nick&god=1&nocut=1&yeller=1'); ready(pg); toZone(pg); time.sleep(0.4)
            r = pg.evaluate("({n:__nbd.W.alarms.length, y:__nbd.W.enemies.some(e=>e.kind==='yeller')||__nbd.W.queue.some(q=>q.kind==='yeller')})")
            check(f'floor {lv}: pull stations on the wall and a Yeller shows up', r['n'] >= 2 and r['y'], r)
            pg.wait_for_function("!!__nbd.W.alarm", timeout=40000); time.sleep(1.0); pg.screenshot(path=f'tests/out/v06_alarm_l{lv}.png')
            check(f'floor {lv}: the alarm goes off there too', True)
            pg.close()
    b.close()
print('console errors:', errs[:8] if errs else 'none')
if not errs: print('no console errors')
print('ALL PASS' if ok and not errs else 'SOME FAILED')
