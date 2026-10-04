# v0.4: new patients (Bed-Alarm Runner, Food-Tray Thrower, O2 Wanderer + loose tank), rideable gurney (keys: GRAB and
# ATK+JUMP, gamepad, touch RIDE button, jump bail-out), 2P Charge Nurse team-up (+ solo fallback), shift-change cutscenes
# (start / boss / lunch / next; skip by key, pad and tap), Breakroom Bonus round + tally + flow up to Floor 4 (v0.5).
# Screenshots -> tests/out/v04_*.png
import time, json
from playwright.sync_api import sync_playwright
U = 'http://localhost:8731/'
errs = []
def watch(pg):
    pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: errs.append(f'PAGEERROR: {e}'))
def key(pg, k, hold=0.08, after=0.1): pg.keyboard.down(k); time.sleep(hold); pg.keyboard.up(k); time.sleep(after)
def ready(pg):
    pg.wait_for_function('window.__loaded === true', timeout=30000)
    pg.wait_for_function("window.__nbd && __nbd.game.scene==='play' && __nbd.W.heroes.length>0 && __nbd.W.heroes[0].st==='idle'", timeout=30000); time.sleep(0.5)
CLEAR = "(()=>{const W=__nbd.W; W.enemies.forEach(e=>{e.alive=false}); W.enemies.length=0; W.queue && (W.queue.length=0); W.items.length=0; W.shots.length=0; W.zone=99; W.zoneOn=false;})()"  # zone 99: no more wave triggers
HOLD = "(()=>{const W=__nbd.W; W.lockX = W.camX; })()"
SC = "__nbd.game.scene"
ok = True
def check(name, cond, info=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name, info); ok = ok and bool(cond)
def foe(pg, kind, dx, dy=0, st='idle', extra=''):
    return pg.evaluate(f"(()=>{{const W=__nbd.W,h=W.heroes[0]; const e=__nbd.spawn('{kind}','R'); e.x=h.x+{dx}; e.y=h.y+{dy}; e.tx=e.x; e.ty=e.y; e.set('{st}'); {extra}; window.F=window.F||[]; F.push(e); return F.length-1;}})()")
def gurney(pg, dx=26, dy=0):
    return pg.evaluate(f"(()=>{{const W=__nbd.W,h=W.heroes[0]; h.face=1; return __nbd.prop('gurney',{dx},{dy});}})()")
MOCK = """(() => { const pad = { id: 'Xbox Wireless Controller (STANDARD GAMEPAD)', index: 0, connected: true, mapping: 'standard', timestamp: 0,
  axes: [0, 0, 0, 0], buttons: Array.from({ length: 17 }, () => ({ pressed: false, value: 0, touched: false })) };
  window.__pad = pad; navigator.getGamepads = () => [window.__padOn ? pad : null, null, null, null];
  window.__padSet = (i, on) => { pad.buttons[i].pressed = on; pad.buttons[i].value = on ? 1 : 0; pad.timestamp++; };
  window.__padConnect = () => { window.__padOn = true; const e = new Event('gamepadconnected'); e.gamepad = pad; dispatchEvent(e); }; })();"""

with sync_playwright() as p:
    b = p.chromium.launch()
    # ================================================================ A: new patients (keyboard, Nick)
    pg = b.new_page(viewport={'width': 1280, 'height': 720}); watch(pg)
    pg.goto(U + '?autostart=1&hero=nick&god=1'); ready(pg)
    pg.evaluate(CLEAR); pg.evaluate(HOLD); pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0]; h.x=W.camX+150; h.y=172;})()")
    # 1) Bed-Alarm Runner keeps away, beeps, and gets away if you don't catch it
    i = foe(pg, 'runner', 40)
    d0 = pg.evaluate(f"Math.abs(F[{i}].x-__nbd.W.heroes[0].x)"); time.sleep(1.2)
    d1 = pg.evaluate(f"Math.abs(F[{i}].x-__nbd.W.heroes[0].x)")
    check('runner runs away from the nurse', d1 > d0 + 20, f'{d0:.0f} -> {d1:.0f}')
    pg.screenshot(path='tests/out/v04_runner.png')
    pg.evaluate(f"F[{i}].runT = 99")
    pg.wait_for_function(f"!F[{i}].alive", timeout=8000)
    check('runner escapes off-screen after a while (no softlock)', pg.evaluate("__nbd.W.stats.escaped") == 1 and pg.evaluate("__nbd.W.enemies.length") == 0)
    # caught: knocked out -> snacks (and maybe a gold star / ZYNN) + bonus score
    i = foe(pg, 'runner', 30); s0 = pg.evaluate("__nbd.W.heroes[0].score")
    pg.evaluate(f"F[{i}].takeHit({{dmg:99, dir:1, kb:150, from:__nbd.W.heroes[0]}})"); time.sleep(1.4)
    items = pg.evaluate("__nbd.W.items.map(i=>i.k)")
    check('caught runner drops something good', 'snacks' in items and pg.evaluate("__nbd.W.stats.caught") == 1 and pg.evaluate("__nbd.W.heroes[0].score") - s0 >= 1000, items)
    pg.evaluate(CLEAR)
    # 2) Food-Tray Thrower: trays fly flat, jello lobs and leaves a slippery green splat
    i = foe(pg, 'tray', 120)
    pg.evaluate(f"(()=>{{const e=F[{i}]; e.throwKind='tray'; e.begin('windup');}})()"); time.sleep(0.6)
    t1 = pg.evaluate("__nbd.W.shots.map(s=>s.spr)")
    time.sleep(1.2)
    pg.evaluate(f"(()=>{{const e=F[{i}]; e.throwKind='jello'; e.begin('windup');}})()"); time.sleep(0.62)
    pg.screenshot(path='tests/out/v04_tray.png')
    t2 = pg.evaluate("__nbd.W.shots.map(s=>s.spr)")
    pg.wait_for_function("__nbd.W.shots.some(s=>s.spr==='puddle_g')", timeout=4000)
    check('tray thrower throws a meal tray', 'p_tray' in t1, t1)
    check('tray thrower lobs jello -> green slippery splat', 'p_jello' in t2 and pg.evaluate("__nbd.W.shots.some(s=>s.kind==='puddle'&&s.spr==='puddle_g')"), t2)
    seen = set()
    pg.evaluate(f"F[{i}].cd = 0")
    for k in range(40):
        seen |= set(pg.evaluate("__nbd.W.shots.filter(s=>s.kind==='enemy').map(s=>s.spr)")); time.sleep(0.15)
    check('tray thrower attacks on its own', seen & {'p_tray', 'p_jello'}, seen)
    pg.evaluate(CLEAR)
    # 3) O2 Wanderer: swings the tank; a hard hit knocks the tank loose -> kickable o2tank prop that breaks with a hiss
    pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0]; h.x=W.camX+120; h.y=172; h.face=1; h.set('idle'); W.props.length=0;})()")
    i = foe(pg, 'o2', 24, 0, 'idle', 'e.cd=99')
    check('O2 wanderer starts with its tank', pg.evaluate(f"F[{i}].tank") is True)
    key(pg, 'KeyK', 0.06, 0.12); key(pg, 'KeyJ', 0.05, 0.4)  # jump kick
    tank = pg.evaluate("__nbd.W.props.filter(p=>p.kind==='o2tank').map(p=>({x:Math.round(p.x), vx:Math.round(p.vx), st:p.st}))")
    pg.screenshot(path='tests/out/v04_o2.png')
    check('hard hit knocks the O2 tank loose (becomes a rolling prop)', pg.evaluate(f"F[{i}].tank") is False and len(tank) == 1, tank)
    time.sleep(1.4)
    pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0],t=W.props.find(p=>p.kind==='o2tank'); t.vx=0; t.x=W.camX+140; t.y=172; h.x=t.x-22; h.y=172; h.face=1; h.set('idle'); W.enemies.forEach(e=>{e.alive=false}); W.enemies.length=0;})()")
    key(pg, 'KeyK', 0.06, 0.12); key(pg, 'KeyJ', 0.05, 0.05)
    vmax = 0
    for k in range(10): vmax = max(vmax, pg.evaluate("Math.abs(__nbd.W.props.find(p=>p.kind==='o2tank').vx)")); time.sleep(0.03)
    check('loose O2 tank can be kicked rolling', vmax > 150, vmax)
    pg.evaluate("(()=>{const W=__nbd.W,t=W.props.find(p=>p.kind==='o2tank'); __nbd.hitProp(t, 20, {dir:1, kb:200, from:W.heroes[0]}); __nbd.hitProp(t, 20, {dir:1, kb:200, from:W.heroes[0]});})()")
    check('O2 tank breaks (hiss + smoke)', pg.evaluate("__nbd.W.props.find(p=>p.kind==='o2tank').st") == 2)
    # O2 wanderer without its tank still works (tank-less anims)
    check('tank-less O2 wanderer uses its own poses', pg.evaluate(f"F[{i}].pose()[0]") in ('idle2', 'walk2', 'atk2', 'down', 'getup', 'fall', 'hurt', 'sleep', 'dizzy'), pg.evaluate(f"F[{i}].pose()"))
    pg.evaluate(CLEAR); pg.evaluate("__nbd.W.props.length=0")
    # ================================================================ B: gurney ride (keyboard)
    def ride_run(trigger, label, bail=False, shot=None):
        pg.evaluate(CLEAR); pg.evaluate("__nbd.W.props.length=0")
        pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0]; h.x=W.camX+40; h.y=172; h.face=1; h.set('idle'); h.inv=0; h.held=null;})()")
        g = gurney(pg, 30)
        es = [foe(pg, 'wanderer', 120 + k * 36, 0, 'idle', 'e.cd=99') for k in range(3)]
        p0 = pg.evaluate(f"__nbd.W.props[{g}].x")
        trigger()
        st = pg.evaluate("__nbd.W.heroes[0].st")
        time.sleep(0.25 if not bail else 0.6)
        if shot: pg.screenshot(path=shot)
        mid = pg.evaluate(f"[__nbd.W.heroes[0].st, Math.round(__nbd.W.props[{g}].x)]")
        if bail: key(pg, 'KeyK', 0.05, 0.1); mid.append(pg.evaluate(f"[__nbd.W.props[{g}].st, Math.round(Math.abs(__nbd.W.props[{g}].vx)), __nbd.W.heroes[0].st]"))
        t0 = time.time(); downs = set()
        while time.time() - t0 < 3.4:
            for k in es:
                if pg.evaluate(f"['fall','down','getup','dead'].includes(F[{k}].st)"): downs.add(k)
            time.sleep(0.05)
        end = pg.evaluate(f"(()=>{{const W=__nbd.W,p=W.props[{g}],h=W.heroes[0]; return {{hst:h.st, gst:p.st, gx:Math.round(p.x), rider:!!p.rider}};}})()")
        return st, mid, downs, end, p0, es
    st, mid, downs, end, p0, es = ride_run(lambda: key(pg, 'KeyH', 0.06, 0.05), 'grab', shot='tests/out/v04_gurney.png')
    check('keys: GRAB next to a gurney hops on', st == 'ride', st)
    check('gurney ride plows through the crowd', len(downs) >= 2, f'{len(downs)}/3 down')
    check('ride ends in a crash (gurney breaks, nurse hops off)', end['gst'] == 2 and end['hst'] in ('idle', 'walk', 'land', 'jump') and not end['rider'] and end['gx'] - p0 > 100, end)
    st, mid, downs, end, p0, es = ride_run(lambda: (pg.keyboard.down('KeyJ'), pg.keyboard.down('KeyK'), time.sleep(0.06), pg.keyboard.up('KeyJ'), pg.keyboard.up('KeyK'), time.sleep(0.05)), 'atk+jmp')
    check('keys: ATK+JUMP next to a gurney hops on', st == 'ride' or mid[0] == 'ride', [st, mid])
    st, mid, downs, end, p0, es = ride_run(lambda: key(pg, 'KeyH', 0.06, 0.05), 'bail', bail=True)
    check('JUMP bails out early; the empty gurney rolls on', mid[0] == 'ride' and mid[2][0] < 2 and mid[2][1] > 100 and mid[2][2] == 'jump' and not end['rider'], [mid, end])
    pg.close()
    # ================================================================ C: gurney via gamepad
    pg = b.new_page(viewport={'width': 1280, 'height': 720}); pg.add_init_script(MOCK); watch(pg)
    def ptap(i, hold=0.1): pg.evaluate(f'__padSet({i}, true)'); time.sleep(hold); pg.evaluate(f'__padSet({i}, false)'); time.sleep(0.1)
    pg.goto(U + '?autostart=1&hero=kim&god=1'); ready(pg); pg.evaluate('__padConnect()'); time.sleep(0.4)
    pg.evaluate(CLEAR); pg.evaluate(HOLD); pg.evaluate("__nbd.W.props.length=0")
    pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0]; h.x=W.camX+60; h.y=172; h.face=1; h.set('idle');})()"); gurney(pg, 30)
    ptap(1); st = pg.evaluate("__nbd.W.heroes[0].st")
    check('gamepad: B (grab) next to a gurney hops on', st == 'ride', st)
    time.sleep(3.2)
    # pad ATK+JUMP too
    pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0]; W.props.length=0; h.x=W.camX+60; h.y=172; h.face=1; h.set('idle');})()"); gurney(pg, 30)
    pg.evaluate('__padSet(2, true); __padSet(0, true)'); time.sleep(0.08); pg.evaluate('__padSet(2, false); __padSet(0, false)'); time.sleep(0.1)
    st = pg.evaluate("__nbd.W.heroes[0].st")
    check('gamepad: X+A (atk+jump) next to a gurney hops on', st == 'ride', st)
    pg.close()
    # ================================================================ D: gurney via touch (RIDE context button)
    UA = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36'
    ctx = b.new_context(viewport={'width': 915, 'height': 412}, device_scale_factor=2.6, is_mobile=True, has_touch=True, user_agent=UA)
    pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg); watch(pg)
    def touch(kind, pts): cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [{'x': x, 'y': y, 'id': i} for i, x, y in pts]})
    pg.goto(U + '?autostart=1&hero=jackie&god=1'); ready(pg)
    pg.evaluate(CLEAR); pg.evaluate(HOLD); pg.evaluate("__nbd.W.props.length=0")
    lab0 = pg.inner_text('#b_grab')
    pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0]; h.x=W.camX+60; h.y=172; h.face=1; h.set('idle');})()"); gurney(pg, 30); time.sleep(0.3)
    lab1 = pg.inner_text('#b_grab'); pg.screenshot(path='tests/out/v04_touch_ride.png')
    r = pg.locator('#b_grab').bounding_box(); gx, gy = r['x'] + r['width'] / 2, r['y'] + r['height'] / 2
    touch('touchStart', [(3, gx, gy)]); time.sleep(0.06); touch('touchEnd', []); time.sleep(0.1)
    st = pg.evaluate("__nbd.W.heroes[0].st")
    check('touch: GRAB button turns into RIDE next to a gurney', lab0 == 'GRAB' and lab1 == 'RIDE', [lab0, lab1])
    check('touch: RIDE button hops on', st == 'ride', st)
    time.sleep(3.2); check('touch: button label back to GRAB after the ride', pg.inner_text('#b_grab') == 'GRAB', pg.inner_text('#b_grab'))
    # touch: tap skips a cutscene
    pg.evaluate("__nbd.cut('boss','play')"); time.sleep(1.0)
    sc0 = pg.evaluate(SC); r = pg.locator('#view, canvas').first.bounding_box()
    touch('touchStart', [(4, r['x'] + r['width'] / 2, r['y'] + r['height'] / 2)]); time.sleep(0.05); touch('touchEnd', []); time.sleep(0.3)
    check('touch: a tap skips the cutscene', sc0 == 'cutscene' and pg.evaluate(SC) == 'play', [sc0, pg.evaluate(SC)])
    ctx.close()
    # ================================================================ E: 2P Charge Nurse team-up (split keyboard)
    pg = b.new_page(viewport={'width': 1280, 'height': 720}); watch(pg)
    pg.goto(U + '?god=1'); pg.wait_for_function('window.__loaded === true'); time.sleep(0.5)
    key(pg, 'KeyS', after=0.2); key(pg, 'Enter', after=0.5)             # title: 2 PLAYERS
    key(pg, 'Comma', after=0.3); key(pg, 'KeyJ', after=0.3); key(pg, 'Comma', after=1.2)  # P2 joins, both lock in
    pg.wait_for_function(f"{SC}==='cutscene'", timeout=10000); time.sleep(1.0)
    check('2P start: the shift-change cutscene plays', pg.evaluate("__nbd.game.cut && __nbd.game.cut.id") == 'start')
    key(pg, 'KeyK', after=0.3)
    check('cutscene: a key press skips it', pg.evaluate(SC) == 'intro', pg.evaluate(SC))
    pg.wait_for_function("__nbd.game.scene==='play' && __nbd.W.heroes.length===2 && __nbd.W.heroes.every(h=>h.st==='idle')", timeout=20000); time.sleep(0.3)
    pg.evaluate(CLEAR); pg.evaluate(HOLD)
    def team_setup(m1=60, m2=60, gap=30):
        pg.evaluate(CLEAR)
        pg.evaluate(f"(()=>{{const W=__nbd.W,[a,b]=W.heroes; a.x=W.camX+110; a.y=172; b.x=a.x+{gap}; b.y=176; a.face=1; b.face=-1; a.set('idle'); b.set('idle'); a.meter={m1}; b.meter={m2}; a.hp=a.maxHp; b.hp=b.maxHp;}})()")
        for k in range(4): pg.evaluate(f"(()=>{{const e=__nbd.spawn('wanderer','R'); e.x=__nbd.W.camX+200+{k}*50; e.y=150+{k}*14; e.set('idle'); e.cd=99;}})()")
        pg.evaluate("__nbd.prop('crashcart', 160, -20)")
        time.sleep(0.2)
    team_setup()
    hp0 = pg.evaluate("__nbd.W.enemies.map(e=>e.hp)")
    pg.keyboard.down('KeyL'); time.sleep(0.12); pg.keyboard.down('Slash'); time.sleep(0.05)
    sts = pg.evaluate("__nbd.W.heroes.map(h=>h.st)"); time.sleep(0.35)
    pg.screenshot(path='tests/out/v04_teamup_a.png'); time.sleep(0.45)
    pg.screenshot(path='tests/out/v04_teamup_b.png')
    pg.keyboard.up('KeyL'); pg.keyboard.up('Slash'); time.sleep(1.2)
    res = pg.evaluate("({team:__nbd.W.stats.teamups||0, meters:__nbd.W.heroes.map(h=>Math.round(h.meter)), sts:__nbd.W.heroes.map(h=>h.st), foes:__nbd.W.enemies.map(e=>[e.st,e.hp])})")
    check('2P: both hold SP close together -> CHARGE NURSE team-up', res['team'] == 1 and 'teamup' in sts, [sts, res])
    check('team-up clears the screen and costs half a meter each', all(st in ('dead', 'down', 'fall', 'getup') or hp <= 0 for st, hp in res['foes']) and all(m <= 20 for m in res['meters']), res)
    check('team-up ends: both nurses back in control', all(s in ('idle', 'walk') for s in res['sts']), res['sts'])
    # fallback: partner too far -> the normal special
    team_setup(60, 60, 220); pg.keyboard.down('KeyL'); time.sleep(0.15); pg.keyboard.up('KeyL'); time.sleep(0.1)
    st = pg.evaluate("__nbd.W.heroes[0].st"); time.sleep(1.2)
    check('2P: partner far away -> SP is the solo special (v0.6: Ativan jab at >= 1/3 meter)', st in ('special', 'ativan') and pg.evaluate("__nbd.W.stats.teamups") == 1, st)
    # tap-only (released before the partner joins) -> normal special too, no meter spent
    team_setup(60, 60, 30); key(pg, 'KeyL', 0.05, 0.25)
    st = pg.evaluate("[__nbd.W.heroes[0].st, Math.round(__nbd.W.heroes[0].meter)]"); time.sleep(1.2)
    check('2P: a quick SP tap near the partner is still the solo special (v0.6: Ativan, one third of the meter)', st[0] in ('special', 'ativan') and st[1] >= 50 - 34 and pg.evaluate("__nbd.W.stats.teamups") == 1, st)
    pg.close()
    # ================================================================ F: boss cutscene, then the floor -> lunch -> bonus -> next -> teaser
    pg = b.new_page(viewport={'width': 1280, 'height': 720}); watch(pg)
    pg.goto(U + '?zone=5&god=1&hero=will&cuts=1'); pg.wait_for_function('window.__loaded === true')
    pg.wait_for_function(f"{SC}==='cutscene'", timeout=20000)   # ?zone=5 drops the nurses right on the boss line
    check('boss: the pre-Tilly cutscene plays', pg.evaluate("__nbd.game.cut.id") == 'boss')
    time.sleep(6.0); pg.screenshot(path='tests/out/v04_cut_boss.png')
    pg.mouse.click(640, 360); time.sleep(0.3)
    check('mouse click skips the cutscene; Tilly arrives', pg.evaluate(SC) == 'play' and pg.evaluate("!!__nbd.W.boss"), pg.evaluate(SC))
    time.sleep(2.5); pg.evaluate('__nbd.W.boss.hp = 2; __nbd.W.boss.phase = 2; __nbd.W.boss.takeHit({dmg:9, dir:1, from:__nbd.W.heroes[0], force:true})')
    pg.wait_for_function(f"{SC}==='tally'", timeout=30000); time.sleep(3.3); key(pg, 'KeyJ', after=0.4)
    check('tally -> lunch cutscene', pg.evaluate(SC) == 'cutscene' and pg.evaluate("__nbd.game.cut.id") == 'lunch', pg.evaluate(SC))
    time.sleep(6.2); pg.screenshot(path='tests/out/v04_cut_lunch.png')
    pg.wait_for_function(f"{SC}==='bonus'", timeout=8000)   # lets it time out on its own (auto-advance)
    check('lunch cutscene auto-advances into the Breakroom Bonus', True)
    time.sleep(1.0); pg.screenshot(path='tests/out/v04_bonus_intro.png')
    # play the round for real: chase thieves with the keyboard (J mash while walking toward the nearest)
    t0 = time.time(); raids = set(); fr = False
    while time.time() - t0 < 26:
        s = pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0]; const f=W.enemies.filter(e=>e.alive&&e.st!=='dead'&&e.x>W.camX&&e.x<W.camX+__nbd.G.VW).sort((a,b)=>Math.abs(a.x-h.x)-Math.abs(b.x-h.x))[0]; return {f: f?[f.x-h.x,f.y-h.y,f.st]:null, B:{...__nbd.B, spots:0}};})()")
        if s['f']:
            raids.add(s['f'][2]); dx, dy = s['f'][0], s['f'][1]
            for k, c in (('KeyD', dx > 20), ('KeyA', dx < -20), ('KeyS', dy > 4), ('KeyW', dy < -4)):
                (pg.keyboard.down if c else pg.keyboard.up)(k)
            if abs(dx) < 34 and abs(dy) < 8: key(pg, 'KeyJ', 0.04, 0.02)
        fr = fr or s['B']['fridgeOpen'] > 0
        if 12 < time.time() - t0 < 12.3: pg.screenshot(path='tests/out/v04_bonus.png')
        time.sleep(0.05)
    for k in ('KeyD', 'KeyA', 'KeyS', 'KeyW'): pg.keyboard.up(k)
    Bs = pg.evaluate("({...__nbd.B, spots:0})")
    check('bonus: thieves raid snack spots and get stopped', 'raid' in raids and Bs['stopped'] >= 2, [sorted(raids), Bs['stopped'], Bs['escaped']])
    pg.evaluate("__nbd.B.left = 0.5")
    pg.wait_for_function(f"{SC}==='btally'", timeout=12000); time.sleep(2.2)
    pg.screenshot(path='tests/out/v04_bonus_tally.png')
    bt = pg.evaluate("__nbd.game.btally.map(t=>({rows:t.rows, total:t.total}))")
    check('bonus tally: thieves stopped / snacks saved / perfect rows', len(bt) == 1 and bt[0]['rows'][0][1] == 500 * int(bt[0]['rows'][0][0].split('x')[1]), bt)
    tot = pg.evaluate("__nbd.game.tally[0].total"); sc = pg.evaluate("__nbd.W.heroes[0].score")
    time.sleep(1.2); key(pg, 'KeyJ', after=0.4)
    check('bonus tally -> "next floor" cutscene', pg.evaluate(SC) == 'cutscene' and pg.evaluate("__nbd.game.cut.id") == 'next')
    time.sleep(6.0); pg.screenshot(path='tests/out/v04_cut_next.png')
    pg.evaluate("__nbd.W && 0"); 
    pg.evaluate("(()=>{const d=__nbd.C.devs; })()")
    # gamepad-free skip with Enter
    key(pg, 'Enter', after=0.4)
    # v0.5: the "next floor" cutscene now leads up to Floor 4 Radiology (tests/v05.py covers the rest of the run)
    check('cutscene skip -> Floor 4 Radiology; the score carries the bonus', pg.evaluate(SC) in ('intro', 'play') and pg.evaluate("__nbd.W.lv.id") == 2 and pg.evaluate("__nbd.W.heroes[0].score") >= tot, [pg.evaluate(SC), tot, sc])
    pg.evaluate('__nbd.toTitle()'); time.sleep(0.3)
    check('quit -> title', pg.evaluate(SC) == 'title')
    # start cutscene on a 1P game from the title (pad press skips it)
    pg.close()
    pg = b.new_page(viewport={'width': 1280, 'height': 720}); pg.add_init_script(MOCK); watch(pg)
    pg.goto(U + '?god=1'); pg.wait_for_function('window.__loaded === true'); time.sleep(0.5)
    pg.evaluate('__padConnect()'); time.sleep(0.4); ptap(0); time.sleep(0.4); ptap(2); time.sleep(1.0)
    pg.wait_for_function(f"{SC}==='cutscene'", timeout=8000); time.sleep(5.8)
    pg.screenshot(path='tests/out/v04_cut_start.png'); ptap(3)
    time.sleep(0.2); check('gamepad press skips the start cutscene', pg.evaluate(SC) == 'intro', pg.evaluate(SC))
    pg.close()
    # ================================================================ G: bot plays the bonus round alone (no softlock), 2 runs of patients
    pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
    pg.goto(U + '?autostart=1&hero=jackie&god=1&bot=1&scene=bonus'); pg.wait_for_function('window.__loaded === true', timeout=30000)
    pg.wait_for_function(f"{SC}==='btally'", timeout=70000)
    check('bot: bonus round runs to its tally on its own', True, pg.evaluate("({s:__nbd.B.stopped, e:__nbd.B.escaped})"))
    pg.close()
    b.close()
print('ALL PASS' if ok else 'SOME FAILED')
print('\n'.join(errs[:30]) or 'no console errors')
