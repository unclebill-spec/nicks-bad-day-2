# v0.11: LEVEL P3, THE PARKING GARAGE AT SHIFT CHANGE (after the night shift, before the ending) + VINNIE THE VALET.
# Art sizes (staff-sized visitors, the Valet ~1.25x), placement + flow, lane cars that hit nurses AND visitors (jump to
# dodge, BAITED! when they hit someone you were fighting), back-outs, car alarms, cones / carts / pay stations, Coffee
# Guy's latte, visitors' lines ("I've been circling for 40 minutes!", "Do you know who I am?"), every nurse's garage lines
# (Bill's four verbatim), the Valet's phases + defeat, no fire alarm in the open-air garage, drops, Ativan / Code Blue,
# grabs + throws, keyboard 2P, gamepad, touch + phone layout. Screenshots -> tests/out/v11_*.png
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
# like the other suites' FREEZE, and no surprise traffic
FREEZE = "(()=>{const W=__nbd.W; W.enemies.forEach(e=>{e.alive=false}); W.enemies.length=0; W.queue && (W.queue.length=0); W.items.length=0; W.shots.length=0; W.zone=99; W.zoneOn=false; W.lockX=W.camX; W.cars=[]; W.carAlarms=[]; W.carNext=999; W.heroes.forEach((h,i)=>{h.x=W.camX+150; h.y=176+i*20; h.z=0; h.vz=0; h.inv=0; h.face=1; h.carry=null; h.weapon=null; h.held=null; h.ride=null; h.set('idle');}); W.props=W.props.filter(p=>p.x<W.camX-60||p.x>W.camX+__nbd.G.VW+60);})()"
ok = True
def check(name, cond, info=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name, info); sys.stdout.flush(); ok = ok and bool(cond)
def foe(pg, kind, dx, dy=0, st='idle'):
    return pg.evaluate(f"(()=>{{const W=__nbd.W,h=W.heroes[0]; const e=__nbd.spawn('{kind}','R'); e.x=h.x+{dx}; e.y=h.y+{dy}; e.tx=e.x; e.ty=e.y; e.set('{st}'); e.cd=99; e.atkCd=99; window.F=window.F||[]; F.push(e); return F.length-1;}})()")
def prop(pg, kind, dx, dy=0):
    return pg.evaluate(f"(()=>{{const W=__nbd.W,h=W.heroes[0]; const i=__nbd.prop('{kind}',0,0); const p=W.props[i]; p.x=h.x+{dx}; p.y=Math.max(136,Math.min(212,h.y+{dy})); window.PP=window.PP||[]; PP.push(p); return PP.length-1;}})()")
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
UA = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36'
DOWN = ('fall', 'down', 'getup', 'dead', 'thrown')
BILL = {'nick': "Someone's gonna key my car, I know it.", 'kim': 'Let me help you to your car, sweetie!', 'will': 'I always get the closest spot.', 'jackie': 'Who needs a jump?'}
BRANDS = ['FORD', 'TOYOTA', 'HONDA', 'CHEVY', 'CHEVROLET', 'NISSAN', 'BMW', 'MERCEDES', 'TESLA', 'JEEP', 'DODGE', 'SUBARU', 'KIA', 'HYUNDAI', 'VOLVO', 'AUDI', 'MAZDA', 'LEXUS', 'CIVIC', 'CAMRY', 'PRIUS']
ONLY = sys.argv[1:] or list('ABCDEFGHIJKL')
GO4 = U + '?level=4&nocut=1&god=1&hero='
with sync_playwright() as p:
    b = p.chromium.launch()
    # ================================================================ A: art + data
    if 'A' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(GO4 + 'nick'); ready(pg)
        nick = pg.evaluate(f"({BOUNDS})('nick','idle')")[1]
        hs = {k: pg.evaluate(f"({BOUNDS})('{k}','idle')")[1] for k in ('ragevisitor', 'vanmom', 'coffeeguy', 'bigshot', 'valet')}
        check('garage visitors are staff-sized (0.9-1.1x Nick)', all(0.9 <= hs[k] / nick <= 1.1 for k in ('ragevisitor', 'vanmom', 'coffeeguy', 'bigshot')), [nick, hs])
        check('Vinnie the Valet is 1.2-1.5x a nurse', 1.2 <= hs['valet'] / nick <= 1.5, round(hs['valet'] / nick, 2))
        miss = pg.evaluate("""(()=>{const r=__nbd.G.atlas.sprites.rects, need=['gwall0','gceil','gfloor0','gopen1','gpillar','sodium','tube','neon_park','neon_stairs','neon_valet','booth','gatearm','ramp','valetstand','sign_vip','sign_lost',
          'cone0','cone1','shopcart0','paystation0','p_coffee','p_ticket','puddle_c','valetcart0','valetcartL0','valetcart2','valetroof0','w_weeoo','w_beepbeep','w_baited','w_screech','w_parked','w_valet','face_valet'];
          for (const m of ['hatch','sedan','van','wagon']) for (const c of [0,1]) for (const s of [0,1,2]) need.push(`car_${m}${c}_${s}`); return need.filter(n=>!r[n]);})()""")
        check('garage, car, prop, cart, word and portrait sprites are in the atlas', miss == [], miss)
        D = pg.evaluate("""(async()=>{const m=await import('./src/data.js'); return {ids:m.LEVELS.map(l=>l.id), lv4:{garage:m.LEVELS[3].garage, noAlarm:m.LEVELS[3].noAlarm, boss:m.LEVELS[3].zones.at(-1).boss, music:m.LEVELS[3].music, bossMusic:m.LEVELS[3].bossMusic, cut:m.LEVELS[3].cutBoss},
          cars:Object.values(m.CARS).map(c=>c.name), carProps:Object.keys(m.BREAKABLES).filter(k=>m.BREAKABLES[k].car&&m.BREAKABLES[k].alarm).length,
          lines:Object.fromEntries(['ragevisitor','vanmom','coffeeguy','bigshot'].map(k=>[k, m.ENEMIES[k].lines])), ko:['ragevisitor','vanmom','coffeeguy','bigshot'].every(k=>m.ENEMIES[k].ko.every(s=>s.includes('zzz'))),
          garage:Object.fromEntries(Object.entries(m.HEROES).map(([k,h])=>[k, h.garage])), loot:[m.LOOT.glovebox.map(x=>x[0]), m.LOOT.paystation.map(x=>x[0])]};})()""")
        check('Level P3 sits after the night shift (LEVELS = 1, 2, 3, 4)', D['ids'] == [1, 2, 3, 4] and D['lv4']['garage'] and D['lv4']['boss'] == 'valet' and D['lv4']['music'] == 'garage' and D['lv4']['bossMusic'] == 'valet', D['lv4'])
        check('parody cars only (no real brands), 8 parked-car props with alarms', not any(bw in n for n in D['cars'] for bw in BRANDS) and D['carProps'] == 8, D['cars'])
        check("visitors' lines: \"I've been circling for 40 minutes!\" + \"Do you know who I am?\"", "I've been circling for 40 minutes!" in D['lines']['ragevisitor'] and 'Do you know who I am?' in D['lines']['bigshot'], D['lines'])
        check('every visitor naps when beaten (zzz)', D['ko'])
        check('all six nurses have garage lines (spawn, idle, car, alarm, drop, clear)', all(D['garage'][k] and all(e in D['garage'][k] for e in ('spawn', 'idle', 'car', 'alarm', 'drop', 'clear')) for k in ('nick', 'kim', 'will', 'jackie', 'nate', 'heather')))
        check("Bill's four garage lines, verbatim", all(any(BILL[k] in v for v in D['garage'][k].values()) for k in BILL), BILL)
        check('busted cars + pay stations drop BEEF JERKY / snacks / energy / pizza / ZYNN', all(x in D['loot'][0] for x in ('jerky', 'snacks', 'energy', 'pizza', 'zynn')) and 'zynn' in D['loot'][1], D['loot'])
        pg.close()
    # ================================================================ B: the level: dark garage, neon, no fire alarm, Nick's spawn line
    if 'B' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(GO4 + 'nick'); ready(pg); time.sleep(0.4)
        L = pg.evaluate("""(()=>{const W=__nbd.W; const cols=W.lights.map(l=>l.col); return {id:W.lv.id, dark:W.dark, blue:cols.filter(c=>c==='#3aa8ff').length, violet:cols.filter(c=>c==='#a24dff').length, red:cols.filter(c=>c==='#ff3a4a').length, sodium:cols.filter(c=>c==='#ffa040').length,
          stations:W.alarms.length, allowed:__nbd.alarmAllowed(), noAlarm:W.noAlarm, said:W.said||[], cars:W.props.filter(p=>p.def.car).length, chair:W.props.some(p=>p.kind==='wheelchair'), carts:W.props.filter(p=>p.kind==='shopcart').length, cones:W.props.filter(p=>p.kind==='cone').length, pay:W.props.filter(p=>p.kind==='paystation').length, elev:Object.keys(W.elevs)};})()""")
        check('garage loads: gloomy, with neon blue + violet + red and sodium lamps', L['id'] == 4 and 0.2 < L['dark'] < 0.6 and L['blue'] >= 2 and L['violet'] >= 2 and L['red'] >= 2 and L['sodium'] >= 4, L)
        check('parked cars, a wheelchair left in a stall, carts, cones, pay stations, staff elevators', L['cars'] >= 12 and L['chair'] and L['carts'] >= 4 and L['cones'] >= 8 and L['pay'] == 2 and L['elev'] == ['A', 'B'], L)
        check('no fire alarm in the open-air garage (no pull stations, no yellers)', L['stations'] == 0 and L['noAlarm'] and not pg.evaluate("__nbd.maybeYeller(true)"), L['stations'])
        check("Nick's spawn line: \"Someone's gonna key my car, I know it.\"", BILL['nick'] in L['said'], L['said'])
        pg.screenshot(path='tests/out/v11_garage.png')
        pg.close()
    # ================================================================ C: lane cars hit nurses (jump to dodge) and visitors (BAITED!)
    if 'C' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=4&nocut=1&hero=will'); ready(pg); pg.evaluate(FREEZE); time.sleep(0.2)
        pg.evaluate("(()=>{window.C=__nbd.garage.sendCar({y:__nbd.W.heroes[0].y, dir:1});})()"); time.sleep(0.5)
        w = pg.evaluate("({st:C.st, horn:true, warn:__nbd.W.cars.length})")
        pg.screenshot(path='tests/out/v11_car_warn.png')
        check('a lane car warns first (lane flash + CAR! arrow + headlights)', w['st'] == 'warn' and w['warn'] == 1, w)
        hp0 = pg.evaluate("__nbd.W.heroes[0].hp"); time.sleep(2.2)
        h = pg.evaluate("({st:__nbd.W.heroes[0].st, hp:__nbd.W.heroes[0].hp, hits:__nbd.W.stats.carHits||0})")
        check('the car knocks a nurse standing in the lane down', h['hits'] == 1 and h['hp'] < hp0, h)
        pg.evaluate(FREEZE); time.sleep(1.2); pg.evaluate(FREEZE); time.sleep(0.2)
        pg.evaluate("(()=>{window.C=__nbd.garage.sendCar({y:__nbd.W.heroes[0].y, dir:-1, warn:0.2});})()")
        for k in range(40):
            if pg.evaluate("C.st==='go' && Math.abs(C.x-__nbd.W.heroes[0].x)<80"): break
            time.sleep(0.03)
        key(pg, 'KeyK', 0.25, 0.0); time.sleep(0.9)
        h = pg.evaluate("({hits:__nbd.W.stats.carHits||0, st:__nbd.W.heroes[0].st})")
        check('jumping over the car dodges it', h['hits'] == 1, h)
        # BAITED!: a visitor you were fighting gets hit by traffic
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2)
        foe(pg, 'ragevisitor', 30, dy=24, st='dizzy'); foe(pg, 'coffeeguy', 90, dy=24, st='dizzy'); pg.evaluate('F.forEach(e=>e.stun=20)')
        pg.evaluate("(()=>{F[0].lastHitBy=__nbd.W.heroes[0]; window.S0=__nbd.W.heroes[0].score; __nbd.garage.sendCar({y:F[0].y, dir:1, warn:0.3});})()"); time.sleep(2.4)
        r = pg.evaluate("({a:F[0].st, b:F[1].st, ahp:F[0].hp, baited:__nbd.W.stats.baited||0, foes:__nbd.W.stats.carFoes||0, ds:__nbd.W.heroes[0].score-S0, hit:__nbd.W.stats.carHits||0})")
        check('cars hit visitors too: both in the lane go down', r['a'] in DOWN and r['b'] in DOWN and r['foes'] == 2, r)
        check('BAITED!: only the one Will had been fighting scores it (+300 or more)', r['baited'] == 1 and r['ds'] >= 300, r)
        pg.screenshot(path='tests/out/v11_baited.png')
        # cones fly, carts roll
        pg.evaluate(FREEZE); time.sleep(0.2); prop(pg, 'cone', 60, dy=24); prop(pg, 'shopcart', 120, dy=24)
        pg.evaluate("__nbd.garage.sendCar({y:PP[0].y, dir:1, warn:0.2})"); time.sleep(1.6)
        pr = pg.evaluate("PP.map(p=>({k:p.kind, hp:p.hp, max:p.def.hp, vx:Math.round(p.vx), st:p.st, x:Math.round(p.x)}))")
        check('a car sends cones and shopping carts flying', all(q['hp'] < q['max'] or q['st'] >= 2 for q in pr), pr)
        pg.close()
    # ================================================================ D: back-outs + car alarms
    if 'D' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(GO4 + 'jackie'); ready(pg); pg.evaluate(FREEZE); time.sleep(0.2)
        i = prop(pg, 'car_sedan1', 40, dy=-36)
        pg.evaluate("(()=>{window.BC=__nbd.garage.backOut(PP[0]);})()"); time.sleep(0.4)
        r0 = pg.evaluate("({kind:BC.kind, st:BC.st, gone:!__nbd.W.props.includes(PP[0])})")
        pg.screenshot(path='tests/out/v11_backout.png')
        time.sleep(1.4); r1 = pg.evaluate("({st:BC.st, y:Math.round(BC.y), y0:Math.round(BC.y0)})")
        check('a parked car beeps, backs out of its stall into the lane, then drives off', r0['kind'] == 'back' and r0['st'] == 'warn' and r0['gone'] and r1['st'] in ('backing', 'stop', 'go') and r1['y'] > r1['y0'], [r0, r1])
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]; window.PP=[]"); time.sleep(0.2)
        pg.evaluate("__nbd.W.heroes[0].sayCd=0")
        prop(pg, 'car_van0', 40, dy=-30); foe(pg, 'vanmom', 90); foe(pg, 'bigshot', -60)
        pg.evaluate("(()=>{window.S0=__nbd.W.heroes[0].score; __nbd.hitProp(PP[0], 6, {dir:1, kb:60, from:__nbd.W.heroes[0]});})()"); time.sleep(0.3)
        a = pg.evaluate("({al:__nbd.W.carAlarms.length, n:__nbd.W.stats.carAlarms||0, dz:F.map(e=>e.st), ds:__nbd.W.heroes[0].score-S0, say:__nbd.W.heroes[0].sayS, lines:__nbd.W.heroes[0].d.garage.alarm})")
        check('hitting a parked car sets off its alarm (WEE-OO!) for points', a['al'] == 1 and a['n'] == 1 and a['ds'] >= 100, a)
        check('the alarm makes the visitors nearby dizzy', all(s == 'dizzy' for s in a['dz']), a['dz'])
        check("Jackie reacts to the alarm in her own words", a['say'] in a['lines'], a['say'])
        pg.screenshot(path='tests/out/v11_alarm.png')
        time.sleep(5.0); check('the alarm stops after a few seconds', pg.evaluate("__nbd.W.carAlarms.length") == 0)
        pg.close()
    # ================================================================ E: visitors' lines, Coffee Guy's latte, out of a parked car
    if 'E' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(GO4 + 'nate'); ready(pg); pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2)
        pg.evaluate("__nbd.W.rnd=()=>0.01")
        pg.evaluate("window.TX=[]; window.__tx=setInterval(()=>{for (const f of __nbd.W.fx) if (f.type==='txt' && !TX.includes(f.s)) TX.push(f.s);}, 50)")
        pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0]; const e=__nbd.spawn('ragevisitor','R'); e.x=h.x+100; e.y=h.y; e.tx=h.x+60; e.ty=h.y; F.push(e); W.shoutT=0; })()")
        time.sleep(1.4); pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0]; W.shoutT=0; const e=__nbd.spawn('bigshot','R'); e.x=h.x+110; e.y=h.y+20; e.tx=h.x+80; e.ty=h.y+20; F.push(e); })()"); time.sleep(1.4)
        txt = pg.evaluate("clearInterval(__tx), TX")
        pg.evaluate("__nbd.W.rnd=Math.random")
        check("visitors shout as they arrive: \"I've been circling...\" / \"Do you know who I am?\"", "I've been circling for 40 minutes!" in txt and 'Do you know who I am?' in txt, txt)
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2); foe(pg, 'coffeeguy', 110)
        pg.evaluate("(()=>{const e=F[0]; e.face=-1; e.throwKind='jello'; e.set('atk'); e.hitDone=false;})()"); time.sleep(0.15)
        sh = pg.evaluate("__nbd.W.shots.map(s=>s.spr)"); time.sleep(1.6)
        pud = pg.evaluate("__nbd.W.shots.filter(s=>s.kind==='puddle').map(s=>s.spr)")
        check("Coffee Guy lobs a latte that leaves a slippery coffee puddle", 'p_coffee' in sh and 'puddle_c' in pud, [sh, pud])
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2); prop(pg, 'car_hatch0', 60, dy=-30)
        e = pg.evaluate("(()=>{const e=__nbd.spawn('vanmom','C'); return {st:e.st, x:Math.round(e.x), cx:Math.round(PP.at(-1).x)};})()")
        check('a visitor can climb out of a parked car (spawn C)', e['st'] == 'enter_door' and abs(e['x'] - e['cx']) < 20, e)
        pg.close()
    # ================================================================ F: every nurse's garage lines (and the normal ones still work)
    if 'F' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        res = {}
        for hid in ('nick', 'kim', 'will', 'jackie', 'nate', 'heather'):
            pg.goto(GO4 + hid); ready(pg); pg.evaluate(FREEZE); time.sleep(0.1)
            res[hid] = pg.evaluate("""(()=>{const h=__nbd.W.heroes[0], W=__nbd.W, o={}; W.rnd=()=>0; for (const ev of ['spawn','idle','zone','car','alarm','drop','clear']) { h.sayCd=0; h.sayLast={}; o[ev]=h.say(ev,true); }
              h.sayCd=0; o.hurtNormal=h.d.lines.hurt ? h.d.lines.hurt.includes(h.say('hurt',true)) : true; W.rnd=Math.random; o.garage=h.d.garage; return o;})()""")
        check('each nurse speaks garage lines down here', all(all(res[k][ev] in res[k]['garage'][ev] for ev in ('spawn', 'car', 'alarm', 'clear')) for k in res), {k: res[k]['spawn'] for k in res})
        check("Kim after a knockdown: \"Let me help you to your car, sweetie!\"", res['kim']['drop'] == BILL['kim'], res['kim']['drop'])
        check("Will: \"I always get the closest spot.\" / Jackie: \"Who needs a jump?\"", res['will']['spawn'] == BILL['will'] and res['jackie']['spawn'] == BILL['jackie'], [res['will']['spawn'], res['jackie']['spawn']])
        check('Nate stays lazy and Heather snarky in the garage', 'Ugh' in res['nate']['spawn'] and res['heather']['spawn'].startswith('Twelve hours'), [res['nate']['spawn'], res['heather']['spawn']])
        check('their usual lines (hurt) still play', all(res[k]['hurtNormal'] for k in res))
        pg.close()
    # ================================================================ G: VINNIE THE VALET
    if 'G' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=4&zone=4&hero=kim&god=1&cuts=1'); pg.wait_for_function('window.__loaded === true', timeout=30000)
        pg.wait_for_function(f"{SC}==='cutscene' || (__nbd.W.boss && __nbd.W.boss.name)", timeout=30000)
        cut = pg.evaluate("__nbd.game.cut && __nbd.game.cut.id")
        check('a comic intro cutscene for the Valet', cut == 'valet', cut)
        time.sleep(3.2); pg.screenshot(path='tests/out/v11_cut_valet.png'); key(pg, 'KeyK', after=0.5)
        pg.wait_for_function("__nbd.W.boss && __nbd.W.boss.greeted", timeout=10000); time.sleep(0.3)
        B = pg.evaluate("(()=>{const B=__nbd.W.boss; return {name:B.name, hp:B.hp, max:B.maxHp, cart:B.inCart, said:__nbd.W.fx.filter(f=>f.type==='txt').map(f=>f.s), music:__nbd.W.lv.bossMusic};})()")
        check("VINNIE THE VALET drives in: \"Ticket's validated... NOT!\"", B['name'] == 'VINNIE THE VALET' and B['cart'] and "Ticket's validated... NOT!" in B['said'] and B['music'] == 'valet', B)
        pg.screenshot(path='tests/out/v11_valet_enter.png')
        pg.wait_for_function("__nbd.W.boss.st==='rev'", timeout=8000)
        check('he revs with a lane telegraph, then charges a pass', pg.evaluate("__nbd.W.boss.hint()") == 'GET OUT OF HIS LANE!')
        pg.wait_for_function("__nbd.W.boss.st==='pass'", timeout=4000)
        pg.evaluate("(()=>{window.B=__nbd.W.boss; B.st='cidle'; B.x=__nbd.W.camX+300; const hp=B.hp; B.takeHit({dmg:20, dir:1, from:__nbd.W.heroes[0]}); window.ARM=hp-B.hp;})()")
        check('the cart is armoured (30% damage)', abs(pg.evaluate("ARM") - 6) < 0.01, pg.evaluate("ARM"))
        # a pass also flattens visitors (BAITED! if a nurse had been on them)
        pg.evaluate("(()=>{const W=__nbd.W, e=__nbd.spawn('coffeeguy','R'); e.x=W.camX+180; e.y=B.y; e.set('idle'); e.cd=99; e.lastHitBy=W.heroes[0]; window.E=e; W.heroes[0].y=Math.min(212, B.y+40); B.x=W.camX+60; B.face=1; B.set('pass'); B.vx=250; B.passes=1; B.hitSet=new Set();})()")
        time.sleep(1.0)
        check("his passes flatten visitors too (BAITED!)", pg.evaluate("E.st") in DOWN and pg.evaluate("__nbd.W.stats.baited||0") >= 1, pg.evaluate("E.st"))
        pg.evaluate("(()=>{B.passes=0; B.set('park'); B.vx=0; B.x=__nbd.W.camX+260;})()")
        pg.wait_for_function("B.st==='foot'", timeout=5000)
        f = pg.evaluate("({cart:!!B.cart, decor:__nbd.W.decor.length, hint:B.hint()})")
        check('he screeches to a stop and hops out (cart parked, hint)', f['cart'] and f['decor'] == 1 and 'OUT OF THE CART' in f['hint'], f)
        pg.screenshot(path='tests/out/v11_valet_foot.png')
        r = pg.evaluate("(()=>{const hp=B.hp; B.takeHit({dmg:20, dir:1, from:__nbd.W.heroes[0], down:true}); return {d:hp-B.hp, st:B.st};})()")
        check('on foot he takes full damage and a hard hit knocks him down', abs(r['d'] - 20) < 0.01 and r['st'] == 'fall', r)
        pg.evaluate("(()=>{B.footLeft=0; B.knockCd=0;})()"); pg.wait_for_function("B.st==='return'||B.st==='climb'||B.inCart", timeout=8000)
        pg.wait_for_function("B.inCart", timeout=8000)
        check('then climbs back in his cart', pg.evaluate("B.inCart && !B.cart && __nbd.W.decor.length===0"))
        pg.evaluate("(()=>{B.hp=B.maxHp*0.45; B.takeHit({dmg:1, dir:1, from:__nbd.W.heroes[0], force:true}); B.set('cidle'); B.cd=0;})()")
        pg.wait_for_function("B.st==='rush'", timeout=4000); time.sleep(0.2)
        check("phase 2: RUSH HOUR! (and he calls the visitors)", pg.evaluate("B.phase===2 && B.p2label==='RUSH HOUR!'"))
        time.sleep(1.0); pg.screenshot(path='tests/out/v11_valet_rush.png')
        pg.evaluate("(()=>{B.set('cidle'); B.x=__nbd.W.camX+300; B.hp=1; B.takeHit({dmg:5, dir:1, from:__nbd.W.heroes[0], force:true});})()"); time.sleep(0.8)
        d = pg.evaluate("({st:B.st, wreck:__nbd.W.decor.some(o=>o.st===2), said:__nbd.W.fx.filter(f=>f.type==='txt').map(f=>f.s), foes:__nbd.W.enemies.filter(e=>e.alive&&e.st!=='dead').length})")
        check("defeat: the cart wrecks and he naps (\"Keep... the change... zzz\"), visitors too", d['st'] == 'defeat' and d['wreck'] and 'Keep... the change... zzz' in d['said'], d)
        time.sleep(1.2); pg.screenshot(path='tests/out/v11_valet_ko.png')
        pg.wait_for_function(f"{SC}==='tally'", timeout=12000); time.sleep(3.4); key(pg, 'KeyJ', after=0.5)
        check('garage tally -> the ending cutscene', pg.evaluate("__nbd.game.cut && __nbd.game.cut.id") == 'ending')
        T = pg.evaluate("(async()=>{const m=await import('./src/cutscene.js'); const o={}; for (const id of ['garage','valet','ending']) o[id]=m.makeCut(id).panels.map(f=>(f(398,160).bubbles||[]).map(b=>b.s)).flat(); return o;})()")
        check('the ending recap mentions the VALET', any('VALET' in s for s in T['ending']), T['ending'])
        time.sleep(1.5); key(pg, 'KeyK', after=0.6)
        check('-> THE END, 4 floors cleared', pg.evaluate(SC) == 'ending' and pg.evaluate("__nbd.save.best") == 4, pg.evaluate("__nbd.save.best"))
        pg.close()
    # ================================================================ H: flow: night shift tally -> garage cutscene -> garage
    if 'H' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=3&hero=heather&god=1&cuts=1'); pg.wait_for_function('window.__loaded === true', timeout=30000)
        pg.wait_for_function(f"{SC}==='play'", timeout=30000); pg.evaluate("__nbd.W.cleared = true")
        pg.wait_for_function(f"{SC}==='tally'", timeout=6000); time.sleep(3.3); s0 = pg.evaluate("__nbd.game.tally[0].total"); key(pg, 'KeyJ', after=0.5)
        check('night shift tally -> the garage cutscene', pg.evaluate("__nbd.game.cut && __nbd.game.cut.id") == 'garage')
        time.sleep(3.6); pg.screenshot(path='tests/out/v11_cut_garage.png')
        T = pg.evaluate("__nbd.game.cut.panels.map((f,i)=>{const P=__nbd.game.cut.cache && __nbd.game.cut.cache[i]; return P ? (P.bubbles||[]).map(b=>b.s) : [];}).flat()")
        check("Heather's snarky take + the road-rage visitor in the cutscene", any('fight for my car' in s for s in T) and "I've been circling for 40 minutes!" in T, T)
        key(pg, 'KeyK', after=0.6)
        pg.wait_for_function(f"__nbd.W.lv.id===4 && ({SC}==='intro'||{SC}==='play')", timeout=8000)
        check('-> Level P3 with the score carried over', pg.evaluate("__nbd.W.heroes[0].score") == s0, [s0, pg.evaluate("__nbd.W.heroes[0].score")])
        pg.close()
    # ================================================================ I: drops, Ativan, Code Blue, grabs + throws in the garage
    if 'I' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=4&nocut=1&hero=nick'); ready(pg); pg.evaluate(FREEZE); time.sleep(0.2)
        got = []
        for k in ('pizza', 'jerky', 'energy', 'snacks', 'zynn'):
            pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.hp=20; window.L0=h.lives;})()"); pg.evaluate(f"__nbd.drop('{k}')"); time.sleep(0.4)
            r = pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; return {hp:h.hp, lives:h.lives, left:__nbd.W.items.length};})()")
            got.append([k, r['hp'] > 20 or r['lives'] > pg.evaluate('L0'), r['left']]); pg.evaluate("__nbd.W.items.length=0")
        check('pizza, BEEF JERKY, energy drink, fruit snacks and ZYNN all work here', all(g[1] for g in got), got)
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2); foe(pg, 'ragevisitor', 26)
        pg.evaluate("__nbd.W.heroes[0].meter=40"); key(pg, 'KeyL', after=0.7)
        check('Ativan jab puts a road-rage visitor to sleep', pg.evaluate("F[0].sleepT > __nbd.W.t || F[0].st==='down'"), pg.evaluate("F[0].st"))
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2); foe(pg, 'bigshot', 60); foe(pg, 'vanmom', 120)
        pg.evaluate("__nbd.W.heroes[0].meter=100"); key(pg, 'KeyL', after=1.6)
        check('Code Blue zaps the Big Shot and the Minivan Mom', all(s in DOWN or s == 'zapped' for s in pg.evaluate("F.map(e=>e.st)")) and (pg.evaluate("__nbd.W.stats.supers") or 0) >= 1, pg.evaluate("F.map(e=>e.st)"))
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2); foe(pg, 'coffeeguy', 18, st='dizzy'); time.sleep(0.05)
        key(pg, 'KeyH', after=0.3); g = pg.evaluate("({st:__nbd.W.heroes[0].st, held:!!__nbd.W.heroes[0].held})")
        key(pg, 'KeyD', 0.05, 0.0); key(pg, 'KeyJ', after=0.8)
        check('grab + toss a Coffee Guy', g['held'] and pg.evaluate("F[0].st") in DOWN, [g, pg.evaluate("F[0].st")])
        pg.evaluate(FREEZE); time.sleep(0.2); prop(pg, 'cone', 16); time.sleep(0.05)
        key(pg, 'KeyH', after=0.4); c = pg.evaluate("__nbd.W.heroes[0].carry ? __nbd.W.heroes[0].carry.kind : null")
        check('pick up a traffic cone (to throw)', c == 'cone', c)
        pg.close()
    # ================================================================ J: keyboard 2P in the garage
    if 'J' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=4&nocut=1'); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.5)
        pg.evaluate("(()=>{__nbd.toSelect(2); const S=__nbd.game.sel; S.p[0].cur=1; S.p[0].locked=true; S.p.push({dev:'kb2', cur:3, locked:true}); __nbd.startGame();})()")
        pg.wait_for_function(f"{SC}==='play' && __nbd.W.heroes.length===2 && __nbd.W.heroes[1].st==='idle'", timeout=30000); time.sleep(0.3)
        ids = pg.evaluate("[__nbd.W.lv.id, ...__nbd.W.heroes.map(h=>h.id)]")
        check('2P in the garage', ids[0] == 4 and len(ids) == 3, ids)
        pg.evaluate(FREEZE); time.sleep(0.2)
        pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[1]; const e=__nbd.spawn('vanmom','R'); e.x=h.x+26; e.y=h.y; e.tx=e.x; e.ty=e.y; e.set('dizzy'); e.cd=99; window.F=[e];})()")
        key(pg, 'Comma', 0.06, 0.3)
        check('P2 (arrows / Comma) fights in the garage', pg.evaluate("F[0].hp < F[0].maxHp"))
        pg.evaluate("__nbd.garage.sendCar({y:__nbd.W.heroes[1].y, dir:1, warn:0.2})"); time.sleep(1.8)
        check('cars hit P2 as well', pg.evaluate("__nbd.W.stats.carHits||0") >= 1)
        pg.screenshot(path='tests/out/v11_2p.png')
        pg.close()
    # ================================================================ K: gamepad
    if 'K' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg); pg.add_init_script(MOCK)
        pg.goto(U + '?level=4&nocut=1&hero=heather'); ready(pg); pg.evaluate('__padConnect()'); time.sleep(0.3)
        def pb(i, hold=0.1, after=0.18): pg.evaluate(f'__padSet({i}, true)'); time.sleep(hold); pg.evaluate(f'__padSet({i}, false)'); time.sleep(after)
        pg.evaluate(FREEZE); pg.evaluate("window.F=[]"); time.sleep(0.2); foe(pg, 'bigshot', 26, st='dizzy')
        pb(2, after=0.2); check('pad: X attacks a Big Shot in the garage', pg.evaluate("F[0].hp < F[0].maxHp"))
        pg.evaluate(FREEZE); time.sleep(0.2); z0 = pg.evaluate("__nbd.W.heroes[0].z"); pb(0, hold=0.12, after=0.05)
        check('pad: A jumps (the car dodge)', pg.evaluate("__nbd.W.heroes[0].z") > z0)
        pg.close()
    # ================================================================ L: phone layout + touch in the garage
    if 'L' in ONLY:
        ctx = b.new_context(viewport={'width': 915, 'height': 412}, device_scale_factor=2.6, is_mobile=True, has_touch=True, user_agent=UA)
        pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg); watch(pg)
        def touch(kind, pts): cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [{'x': x, 'y': y, 'id': i} for i, x, y in pts]})
        pg.goto(U + '?level=4&nocut=1&hero=kim&god=1'); ready(pg); time.sleep(0.5)
        lay = pg.evaluate("(()=>{const r=__nbd.G.view.getBoundingClientRect(), pad=document.getElementById('pad'); return {VW:__nbd.G.VW, VH:__nbd.G.VH, w:r.width, h:r.height, pad:!!pad && getComputedStyle(pad).display!=='none', btns:[...document.querySelectorAll('#pad .ab')].map(b=>b.dataset.b)};})()")
        check('phone: wide view, touch pad with HIT / JUMP / SP / GRAB', lay['VW'] >= 400 and lay['pad'] and all(x in lay['btns'] for x in ('atk', 'jmp', 'sp', 'grab')), lay)
        jx, jy = 915 * 0.18, 412 * 0.7; x0 = pg.evaluate("__nbd.W.heroes[0].x")
        touch('touchStart', [(1, jx, jy)]); time.sleep(0.05)
        for k in range(10): touch('touchMove', [(1, jx + k * 5, jy)]); time.sleep(0.02)
        time.sleep(0.8); touch('touchEnd', []); time.sleep(0.2)
        bx = pg.locator('#pad .ab[data-b=jmp]').bounding_box(); touch('touchStart', [(2, bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2)]); time.sleep(0.08); touch('touchEnd', []); time.sleep(0.1)
        check('touch joystick + JUMP work in the garage', pg.evaluate("__nbd.W.heroes[0].x") > x0 + 20 and pg.evaluate("__nbd.W.heroes[0].z") > 0)
        time.sleep(0.8); pg.evaluate("__nbd.garage.sendCar({y:__nbd.W.heroes[0].y+28, dir:1, warn:3})"); time.sleep(0.9)
        pg.screenshot(path='tests/out/v11_phone.png')
        ctx.close()
    b.close()
print('ALL PASS' if ok else 'SOME FAILED')
print('\n'.join(errs[:30]) or 'no console errors')
