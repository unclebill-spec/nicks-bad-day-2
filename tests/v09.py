# v0.9: the SCOOTER RUN driving level (TMNT sewer-surf style) between Radiology and the Night Shift: nurses on mobility
# scooters (seated, normal scrubs), auto-scroll, steer / speed, jump floor junk, Ativan syringes, crashes + invincibility,
# snacks + ZYNN, patients that charge / throw / ride wheelchairs, Motorcart Marv (modestly bigger than a nurse), the
# cutscene lead-in, flow + carry-over, 2P, gamepad, touch (stick + SHOOT + JUMP), pause, continues, and a timed bot ride.
# Screenshots -> tests/out/v09_*.png (+ docs/v09_boss.png, docs/v09_cutscene.png, docs/v09_2p.png)
import time, sys
from playwright.sync_api import sync_playwright
U = 'http://localhost:8731/'
errs = []
def watch(pg):
    pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: errs.append(f'PAGEERROR: {e}'))
def key(pg, k, hold=0.08, after=0.1): pg.keyboard.down(k); time.sleep(hold); pg.keyboard.up(k); time.sleep(after)
def hold(pg, k, t): pg.keyboard.down(k); time.sleep(t); pg.keyboard.up(k); time.sleep(0.05)
SC = "__nbd.game.scene"
ok = True
def check(name, cond, info=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name, info); sys.stdout.flush(); ok = ok and bool(cond)
MOCK = """(() => { const pad = { id: 'Xbox Wireless Controller (STANDARD GAMEPAD)', index: 0, connected: true, mapping: 'standard', timestamp: 0,
  axes: [0, 0, 0, 0], buttons: Array.from({ length: 17 }, () => ({ pressed: false, value: 0, touched: false })) };
  window.__pad = pad; navigator.getGamepads = () => [window.__padOn ? pad : null, null, null, null];
  window.__padSet = (i, on) => { pad.buttons[i].pressed = on; pad.buttons[i].value = on ? 1 : 0; pad.timestamp++; };
  window.__padConnect = () => { window.__padOn = true; const e = new Event('gamepadconnected'); e.gamepad = pad; dispatchEvent(e); }; })();"""
BOUNDS = """(([sheet, an, k]) => { const G = __nbd.G, A = G.atlas.chars[sheet], [cw, ch] = A.cell, i = A.anims[an].s + (k || 0), sx = (i % A.cols) * cw, sy = Math.floor(i / A.cols) * ch;
  const c = document.createElement('canvas'); c.width = cw; c.height = ch; const x = c.getContext('2d'); x.drawImage(G.img[sheet], sx, sy, cw, ch, 0, 0, cw, ch);
  const d = x.getImageData(0, 0, cw, ch).data; let x0 = cw, x1 = 0, y0 = ch, y1 = 0, n = 0; const cols = {};
  for (let y = 0; y < ch; y++) for (let q = 0; q < cw; q++) { const o = (y * cw + q) * 4; if (d[o + 3] > 20) { n++; x0 = Math.min(x0, q); x1 = Math.max(x1, q); y0 = Math.min(y0, y); y1 = Math.max(y1, y);
    const hx = '#' + [d[o], d[o + 1], d[o + 2]].map((v) => v.toString(16).padStart(2, '0')).join(''); cols[hx] = (cols[hx] || 0) + 1; } }
  return { w: x1 - x0 + 1, h: y1 - y0 + 1, top: A.anchor[1] - y0, n, cols }; })"""
R0 = "(()=>{const h=__nbd.W.heroes[%d], r=h.sc; return {x:r.x, y:r.y, z:r.z, inv:r.inv, crash:r.crash, fire:r.fire, hp:h.hp, max:h.maxHp, lives:h.lives, st:h.st, score:h.score, ko:h.scKO, snack:h.scSnack, col:r.col, cont:h.continueT};})()"
def rider(pg, i=0): return pg.evaluate(R0 % i)
CLEAR = "(()=>{const S=__nbd.SC; S.ob.length=0; S.tips.length=0; S.pr.length=0; S.shots.length=0; S.tip=null; __nbd.W.heroes.forEach(h=>{if(h.sc){h.sc.inv=0; h.sc.crash=0;}});})()"
HOLD = "(()=>{const S=__nbd.SC; if (S.d > S.len0) S.d = 2000;})()"
def ride(pg):  # wait for the Scooter Run to be rolling, then clear the course and keep it short of Marv
    pg.wait_for_function('window.__loaded === true', timeout=30000)
    pg.wait_for_function(f"{SC}==='scoot' && __nbd.SC.phase==='ride'", timeout=30000); time.sleep(0.2)
    pg.evaluate("(()=>{__nbd.SCOOT.len = 1e9;})()"); pg.evaluate(CLEAR)
def spawn(pg, k, dx, dy=0, who=0): return pg.evaluate(f"__nbd.scootSpawn('{k}', {dx}, {dy}, {who})")
SKIP = "(()=>{const S=__nbd.SC; S.phase='finish'; S.endT=0; S.bossBeat=true;})()"
UA = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36'
ONLY = sys.argv[1:] or list('ABCDEFGHIJKLMN')
SCOOT = U + '?autostart=1&scene=scooter&hero=%s'
with sync_playwright() as p:
    b = p.chromium.launch()
    # ================================================================ A: art: seated nurses in normal scrubs, scooters, junk, Marv's size
    if 'A' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.5)
        heroes = ['nick', 'kim', 'will', 'jackie', 'nate']
        has = pg.evaluate("(hs)=>hs.every(h=>['scoot','scootf','scooth'].every(a=>__nbd.G.atlas.chars[h].anims[a]))", heroes)
        check('all five nurses have seated scooter poses (ride / shoot / crash)', has)
        sp = pg.evaluate("['scoot_red0','scoot_red1','scoot_blue0','scoot_blue1','tipcan','mopbucket','marvcart0','marvcart1','marvcart2'].every(n=>__nbd.G.atlas.sprites.rects[n])")
        check('sprites: red + blue scooters, tipped trash can, mop bucket, Marv\'s hot-rod cart (3 states)', sp)
        mv = pg.evaluate("['drive','taunt','throw','hurt','sleep'].every(a=>__nbd.G.atlas.chars.marv && __nbd.G.atlas.chars.marv.anims[a])")
        check('Motorcart Marv sheet (drive, taunt, throw, hurt, sleep)', mv)
        stand = [pg.evaluate(BOUNDS, [h, 'idle', 0])['h'] for h in heroes]
        seat = [pg.evaluate(BOUNDS, [h, 'scoot', 0]) for h in heroes]
        avg = sum(stand) / len(stand)
        check('nurses visibly sit on the scooter (seated frame well under standing height)', all(s['h'] < st * 0.92 for s, st in zip(seat, stand)), [(s['h'], st) for s, st in zip(seat, stand)])
        nick = seat[0]['cols']
        top, pants = nick.get('#283a7a', 0) + nick.get('#1b2756', 0), nick.get('#1d2a5e', 0) + nick.get('#121a40', 0)
        check('normal clothes on the scooter: separate scrub top + pants (no onesie)', top > 20 and pants > 20, [top, pants])
        m = pg.evaluate(BOUNDS, ['marv', 'drive', 0]); marv_top = m['top'] + 8  # seated on the raised cart seat (drawn 8 px up)
        cart = pg.evaluate("__nbd.G.atlas.sprites.rects.marvcart0")
        nurse_ride = seat[0]['top'] + 4
        ratio = marv_top / avg
        check('Marv on his cart is only modestly bigger than a nurse (1.15-1.5x a standing nurse)', 1.15 <= ratio <= 1.5, [marv_top, round(avg, 1), round(ratio, 2)])
        check('...and taller than a nurse on a scooter, but not a giant (<1.6x)', marv_top > nurse_ride and marv_top < nurse_ride * 1.6, [marv_top, nurse_ride])
        pg.close()
    # ================================================================ B: flow: Radiology tally -> Scooter Run -> scooter tally -> Night Shift, all carried
    if 'B' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=2&hero=jackie&god=1&noalarm=1'); pg.wait_for_function('window.__loaded === true', timeout=30000)
        pg.wait_for_function(f"{SC}==='play'", timeout=20000); time.sleep(0.4)
        pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.score=12345; h.lives=2; __nbd.game.creditsUsed=1; __nbd.W.cleared=true;})()")
        pg.wait_for_function(f"{SC}==='tally'", timeout=6000); time.sleep(3.3); s0 = pg.evaluate("__nbd.W.heroes[0].score"); key(pg, 'KeyJ', after=0.6)
        check('Radiology tally -> the Scooter Run', pg.evaluate(SC) == 'scoot' and pg.evaluate("__nbd.W.scoot") is True, pg.evaluate(SC))
        r = rider(pg)
        check('score, lives and continues carry onto the scooter', r['score'] == s0 and r['lives'] == 2 and pg.evaluate("__nbd.game.creditsUsed") == 1, [r['score'], s0, r['lives']])
        check('touch layout switches: HIT reads SHOOT, GRAB / SP hidden', pg.evaluate("document.getElementById('b_atk').textContent") == 'SHOOT' and pg.evaluate("document.documentElement.dataset.mode") == 'scoot')
        pg.wait_for_function("__nbd.SC.phase==='ride'", timeout=6000); time.sleep(1.5); pg.screenshot(path='tests/out/v09_flow_ride.png')
        pg.evaluate(SKIP); pg.wait_for_function(f"{SC}==='stally'", timeout=8000); time.sleep(3.3)
        tot = pg.evaluate("__nbd.game.stally[0].total"); s1 = pg.evaluate("__nbd.W.heroes[0].score")
        rows = pg.evaluate("__nbd.game.stally[0].rows.map(r=>r[0])")
        check('scooter tally adds its bonus (sedated, snacks, crashes, Marv)', s1 == s0 + tot and tot > 0 and any('MARV' in x for x in rows), [s0, tot, s1, rows])
        pg.screenshot(path='tests/out/v09_tally.png'); key(pg, 'KeyJ', after=0.6)
        check('scooter tally -> Night Shift (score + lives still there)', pg.evaluate("__nbd.W.lv.id") == 3 and pg.evaluate("__nbd.W.heroes[0].score") == s1 and pg.evaluate("__nbd.W.heroes[0].lives") == 2)
        check('touch layout back to normal on foot', pg.evaluate("document.getElementById('b_atk').textContent") == 'HIT' and pg.evaluate("document.documentElement.dataset.mode") == '' and pg.evaluate("__nbd.W.scoot") is False)
        pg.close()
    # ================================================================ C: keyboard: steer, speed, jump, shoot
    if 'C' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(SCOOT % 'kim' + '&god=1'); ride(pg)
        y0 = rider(pg)['y']; hold(pg, 'KeyS', 0.4); y1 = rider(pg)['y']; hold(pg, 'KeyW', 0.6); y2 = rider(pg)['y']
        check('UP / DOWN steer across the lanes', y1 > y0 + 15 and y2 < y1 - 25, [y0, y1, y2])
        base = pg.evaluate("__nbd.SCOOT.base"); pg.keyboard.down('KeyD'); time.sleep(1.2); fast = pg.evaluate("__nbd.SC.speed"); x_f = rider(pg)['x']; pg.keyboard.up('KeyD')
        pg.keyboard.down('KeyA'); time.sleep(1.2); slow = pg.evaluate("__nbd.SC.speed"); pg.keyboard.up('KeyA'); time.sleep(1.0)
        check('RIGHT speeds up a little, LEFT eases off (+-25%)', base * 1.12 < fast <= base * 1.26 and base * 0.74 <= slow < base * 0.88, [base, round(fast), round(slow)])
        d0 = pg.evaluate("__nbd.SC.d"); time.sleep(0.5); d1 = pg.evaluate("__nbd.SC.d")
        check('the hallway auto-scrolls quickly on its own', d1 - d0 > base * 0.35, round(d1 - d0))
        key(pg, 'KeyK', after=0.12); z = rider(pg)['z']
        check('JUMP pops the scooter into the air', z > 10, z)
        time.sleep(0.8); key(pg, 'KeyJ', after=0.02); n = pg.evaluate("__nbd.SC.shots.length"); f = rider(pg)['fire']
        check('ATTACK fires an Ativan syringe forward (and the shoot pose)', n >= 1 and f > 0, [n, f])
        pg.screenshot(path='tests/out/v09_shoot.png')
        pg.close()
    # ================================================================ D: crashes, invincibility, jumpable junk vs tall obstacles
    if 'D' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(SCOOT % 'nick'); ride(pg)
        spawn(pg, 'sign', 50); time.sleep(0.6); r = rider(pg)
        check('hitting a wet-floor sign costs health + starts the invincible blink', r['hp'] < r['max'] and r['inv'] > 0, r)
        hp1 = r['hp']; spawn(pg, 'gurney', 50); time.sleep(0.5)
        check('...no second hit while blinking', rider(pg)['hp'] == hp1)
        pg.screenshot(path='tests/out/v09_crash.png')
        time.sleep(1.4); pg.evaluate(CLEAR); hp1 = rider(pg)['hp']
        spawn(pg, 'can', 60); key(pg, 'KeyK', hold=0.04, after=0.7)
        check('JUMP clears a knocked-over trash can', rider(pg)['hp'] == hp1 and pg.evaluate("__nbd.SC.crashes") == 1, [rider(pg)['hp'], hp1])
        time.sleep(0.4); spawn(pg, 'bucket', 60); key(pg, 'KeyK', hold=0.04, after=0.7)
        check('JUMP clears a mop bucket', rider(pg)['hp'] == hp1)
        time.sleep(0.4); spawn(pg, 'can', 50); time.sleep(0.6)
        check('...but riding into the junk is a crash', rider(pg)['hp'] < hp1 and pg.evaluate("__nbd.SC.crashes") == 2)
        time.sleep(1.8); pg.evaluate(CLEAR); hp1 = rider(pg)['hp']
        spawn(pg, 'sign', 60); key(pg, 'KeyK', hold=0.04, after=0.7)
        check('tall things (wet-floor sign) can\'t be jumped: dodge them', rider(pg)['hp'] < hp1)
        time.sleep(1.8); pg.evaluate(CLEAR); y = rider(pg)['y']; hp1 = rider(pg)['hp']
        spawn(pg, 'gurney', 120); hold(pg, 'KeyW' if y > 176 else 'KeyS', 0.45); time.sleep(0.6)
        check('steering round a gurney avoids it', rider(pg)['hp'] == hp1)
        pg.close()
    # ================================================================ E: Ativan vs patients: wanderer, charger, wheelchair, thrower
    if 'E' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(SCOOT % 'will' + '&god=1'); ride(pg)
        s0 = rider(pg)['score']; spawn(pg, 'wander', 150); key(pg, 'KeyJ', after=0.25)
        st = pg.evaluate("__nbd.SC.last.st"); time.sleep(0.8); st2 = pg.evaluate("__nbd.SC.last.st")
        check('a syringe knocks a wandering patient down -> asleep at the side', st == 'fly' and st2 == 'sleep' and rider(pg)['ko'] == 1 and rider(pg)['score'] > s0, [st, st2])
        y = pg.evaluate("__nbd.SC.last.y")
        check('...out of the lane so the nurse can ride past', y < 140 or y > 210, y)
        pg.evaluate(CLEAR); spawn(pg, 'wheel', 380); x0 = pg.evaluate("__nbd.SC.last.x"); time.sleep(0.3); x1 = pg.evaluate("__nbd.SC.last.x")
        check('wheelchair patients roll AT you', x1 < x0 - 20, [x0, x1])
        key(pg, 'KeyJ', after=0.02); pg.wait_for_function("__nbd.SC.last.hp < 2 || __nbd.SC.last.st !== 'go'", timeout=3000); one = pg.evaluate("[__nbd.SC.last.st, __nbd.SC.last.hp]")
        time.sleep(0.25); key(pg, 'KeyJ', after=0.02); pg.wait_for_function("__nbd.SC.last.st !== 'go'", timeout=3000); two = pg.evaluate("__nbd.SC.last.st")
        chair = pg.evaluate("__nbd.SC.ob.some(o=>o.k==='chair')")
        check('...take two syringes, then tumble out (the empty chair rolls off)', one == ['go', 1] and two in ('fly', 'sleep') and chair, [one, two, chair])
        pg.screenshot(path='tests/out/v09_wheelchair.png')
        pg.evaluate(CLEAR); spawn(pg, 'charge', 260); x0 = pg.evaluate("__nbd.SC.last.x"); time.sleep(0.4); x1 = pg.evaluate("__nbd.SC.last.x")
        check('chargers run at the scooters', x1 < x0 - 20)
        pg.evaluate(CLEAR); spawn(pg, 'thrower', 260, -60); thrown = False
        for _ in range(30):
            time.sleep(0.1)
            if pg.evaluate("__nbd.SC.pr.length") > 0: thrown = True; break
        check('throwers lob things at the riders', thrown)
        pg.screenshot(path='tests/out/v09_thrower.png')
        pg.close()
    # ================================================================ F: pickups: health snacks + the occasional ZYNN tin
    if 'F' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(SCOOT % 'jackie'); ride(pg)
        pg.evaluate("__nbd.W.heroes[0].hp = 30"); l0 = rider(pg)['lives']
        spawn(pg, 'snacks', 50); time.sleep(0.6); hp = rider(pg)['hp']
        check('health snacks heal', hp > 30, hp)
        spawn(pg, 'zynn', 50); time.sleep(0.6)
        check('a ZYNN tin is a 1-up', rider(pg)['lives'] == l0 + 1 and rider(pg)['snack'] == 2)
        pg.close()
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(SCOOT % 'jackie'); pg.wait_for_function('window.__loaded === true', timeout=30000); pg.wait_for_function(f"{SC}==='scoot'", timeout=30000)
        c = pg.evaluate("(()=>{const o=__nbd.SC.ob, k=(f)=>o.filter(f).length; return {zynn:k(q=>q.item==='zynn'), food:k(q=>q.k==='item'&&q.item!=='zynn'), jump:k(q=>q.jump), tall:k(q=>q.tall), wander:k(q=>q.foe==='wander'), charge:k(q=>q.foe==='charge'), thrower:k(q=>q.foe==='thrower'), wheel:k(q=>q.foe==='wheel'), gurney:k(q=>q.k==='gurney'), sign:k(q=>q.k==='sign')};})()")
        check('the course mixes junk to jump, things to dodge, every patient type, snacks, and just one ZYNN', c['zynn'] == 1 and c['food'] >= 4 and c['jump'] >= 6 and c['tall'] >= 8 and min(c['wander'], c['charge'], c['thrower'], c['wheel']) >= 1 and c['gurney'] >= 3 and c['sign'] >= 2, c)
        pg.close()
    # ================================================================ G: KO -> continue; out of continues -> game over
    if 'G' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(SCOOT % 'nick'); ride(pg)
        pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.hp=1; h.lives=1;})()"); spawn(pg, 'sign', 50); time.sleep(0.6); r = rider(pg)
        check('crashing on the last life: out, with a CONTINUE countdown', r['st'] == 'out' and r['cont'] > 0, r)
        pg.screenshot(path='tests/out/v09_continue.png')
        key(pg, 'KeyJ', after=0.4); r = rider(pg)
        check('ATTACK continues: back on the scooter (3 lives, blinking)', r['st'] != 'out' and r['lives'] == 3 and r['inv'] > 0 and pg.evaluate("__nbd.game.creditsUsed") == 1, r)
        time.sleep(2.8); pg.evaluate(CLEAR)
        pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.hp=1; h.lives=1; __nbd.game.creditsUsed=99; h.sc.inv=0;})()"); spawn(pg, 'sign', 50)
        pg.wait_for_function(f"{SC}==='gameover'", timeout=5000)
        check('no continues left -> GAME OVER (drawn over the hallway)', pg.evaluate(SC) == 'gameover')
        time.sleep(1.0); pg.screenshot(path='tests/out/v09_gameover.png')
        pg.close()
    # ================================================================ H: Motorcart Marv: enter, attacks, nitro, defeat -> tally
    if 'H' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(SCOOT % 'nate' + '&god=1'); ride(pg)
        pg.evaluate("(()=>{__nbd.SCOOT.len = 100; __nbd.SC.d = 200;})()")
        pg.wait_for_function("__nbd.SC.phase==='boss'", timeout=4000)
        check('end of the hall: Motorcart Marv roars up from behind', pg.evaluate("__nbd.W.boss.name") == 'MOTORCART MARV')
        pg.wait_for_function("__nbd.SC.boss.st==='fight'", timeout=6000)
        hp0 = pg.evaluate("__nbd.SC.boss.hp")
        for _ in range(8):
            pg.evaluate("(()=>{const r=__nbd.W.heroes[0].sc; r.y=__nbd.SC.boss.y; r.inv=5;})()"); key(pg, 'KeyJ', after=0.25)
        hp1 = pg.evaluate("__nbd.SC.boss.hp")
        check('syringes wear Marv down (boss bar)', hp1 < hp0, [hp0, hp1])
        time.sleep(0.3); pg.screenshot(path='docs/v09_boss.png')
        pg.evaluate("(()=>{const b=__nbd.SC.boss; b.act='ram'; b.actT=0; b.k=0;})()"); x0 = pg.evaluate("__nbd.SC.boss.x"); time.sleep(1.4); x1 = pg.evaluate("__nbd.SC.boss.x")
        check('BEEP BEEP: he reverses back at the nurses', x1 < x0 - 60, [x0, x1])
        pg.screenshot(path='tests/out/v09_ram.png')
        pg.evaluate("(()=>{const b=__nbd.SC.boss; b.act='drop'; b.actT=0; b.k=0;})()"); time.sleep(1.2)
        check('...and drops junk + spills behind his cart', pg.evaluate("__nbd.SC.ob.filter(o=>o.k==='can'||o.k==='spill').length") >= 1)
        pg.evaluate("(()=>{const b=__nbd.SC.boss; b.act='throw'; b.actT=0; b.k=0;})()"); time.sleep(1.0)
        check('...and throws bedpans', pg.evaluate("__nbd.SC.pr.length") >= 1 or pg.evaluate("__nbd.SC.boss.k") >= 1)
        pg.evaluate("(()=>{const b=__nbd.SC.boss; b.hp=Math.floor(b.maxHp/2)+1; b.act='weave'; b.actT=0;})()")
        for _ in range(4):
            pg.evaluate("(()=>{const r=__nbd.W.heroes[0].sc; r.y=__nbd.SC.boss.y; r.inv=5;})()"); key(pg, 'KeyJ', after=0.25)
        check('half health: NITRO phase', pg.evaluate("__nbd.SC.boss.phase") == 2)
        pg.evaluate("(()=>{const b=__nbd.SC.boss; b.hp=1;})()")
        for _ in range(8):
            if pg.evaluate("__nbd.SC.boss.st") == 'dead': break
            pg.evaluate("(()=>{const r=__nbd.W.heroes[0].sc; r.y=__nbd.SC.boss.y; r.inv=5;})()"); key(pg, 'KeyJ', after=0.25)
        check('Marv tucked in: the cart sputters, finish line', pg.evaluate("__nbd.SC.boss.st") == 'dead' and pg.evaluate("__nbd.SC.bossBeat") and pg.evaluate("__nbd.SC.phase") == 'finish')
        time.sleep(1.2); pg.screenshot(path='tests/out/v09_marv_ko.png')
        pg.wait_for_function(f"{SC}==='stally'", timeout=6000)
        check('-> scooter tally', 'MARV PARKED!' in pg.evaluate("__nbd.game.stally[0].rows.map(r=>r[0])"))
        pg.close()
    # ================================================================ I: 2P: two scooters, P2 on the arrows / , . keys
    if 'I' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?god=1&noalarm=1'); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.6)
        key(pg, 'KeyS'); key(pg, 'Enter', after=0.4); key(pg, 'Comma', after=0.3); key(pg, 'KeyJ', after=0.3); key(pg, 'ArrowRight'); key(pg, 'Comma', after=1.2)
        pg.wait_for_function(f"{SC}==='cutscene'", timeout=8000); key(pg, 'KeyK', after=0.4)
        pg.wait_for_function(f"{SC}==='play'", timeout=8000)
        pg.evaluate("(()=>{const W=__nbd.W; W.heroes[0].score=1111; W.heroes[1].score=2222;})()")
        pg.evaluate("__nbd.scooter()"); ride(pg)
        a, c = rider(pg, 0), rider(pg, 1)
        check('2P: two scooters (red + blue), both scores carried', a['col'] == 'red' and c['col'] == 'blue' and a['score'] == 1111 and c['score'] == 2222, [a['col'], c['col']])
        hold(pg, 'ArrowDown', 0.4); a2, c2 = rider(pg, 0), rider(pg, 1)
        check('P2 steers with the arrows (P1 stays put)', c2['y'] > c['y'] + 15 and abs(a2['y'] - a['y']) < 2, [c['y'], c2['y'], a['y'], a2['y']])
        key(pg, 'Comma', after=0.03); sh = pg.evaluate("__nbd.SC.shots.map(s=>s.h.slot)")
        check('P2 fires with , (comma)', 1 in sh and 0 not in sh, sh)
        key(pg, 'Period', after=0.1)
        check('P2 jumps with . (period)', rider(pg, 1)['z'] > 5 and rider(pg, 0)['z'] == 0)
        hold(pg, 'KeyW', 0.3); time.sleep(0.6)
        for k, dx, dy in (('wander', 200, 0), ('can', 140, 30), ('snacks', 120, -20)): spawn(pg, k, dx, dy, 1)
        time.sleep(0.3); key(pg, 'KeyJ', after=0.2); pg.screenshot(path='docs/v09_2p.png')
        pg.close()
    # ================================================================ J: gamepad
    if 'J' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); pg.add_init_script(MOCK); watch(pg)
        pg.goto(SCOOT % 'will' + '&god=1'); ride(pg); pg.evaluate('__padConnect()'); time.sleep(0.3)
        y0 = rider(pg)['y']; pg.evaluate('__padSet(13, true)'); time.sleep(0.4); pg.evaluate('__padSet(13, false)'); time.sleep(0.05); y1 = rider(pg)['y']
        pg.evaluate("__pad.axes[1]=-1; __pad.timestamp++"); time.sleep(0.6); pg.evaluate("__pad.axes[1]=0; __pad.timestamp++"); time.sleep(0.05); y2 = rider(pg)['y']
        check('gamepad d-pad / stick steer', y1 > y0 + 15 and y2 < y1 - 20, [y0, y1, y2])
        pg.evaluate('__padSet(2, true)'); time.sleep(0.06); pg.evaluate('__padSet(2, false)'); time.sleep(0.03); n = pg.evaluate("__nbd.SC.shots.length")
        pg.evaluate('__padSet(0, true)'); time.sleep(0.08); pg.evaluate('__padSet(0, false)'); time.sleep(0.05); z = rider(pg)['z']
        check('gamepad X shoots, A jumps', n >= 1 and z > 5, [n, z])
        pg.close()
    # ================================================================ K: touch: joystick steers, SHOOT + JUMP buttons
    if 'K' in ONLY:
        ctx = b.new_context(viewport={'width': 915, 'height': 412}, device_scale_factor=2.6, is_mobile=True, has_touch=True, user_agent=UA)
        pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg); watch(pg)
        def touch(kind, pts): cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [{'x': x, 'y': y, 'id': i} for i, x, y in pts]})
        pg.goto(SCOOT % 'kim' + '&god=1'); ride(pg); time.sleep(0.3)
        lab = pg.evaluate("[document.getElementById('b_atk').textContent, getComputedStyle(document.getElementById('b_grab')).visibility, getComputedStyle(document.getElementById('b_sp')).visibility, getComputedStyle(document.getElementById('b_jmp')).visibility]")
        check('touch pad on the scooter: SHOOT + JUMP (GRAB / SP hidden)', lab == ['SHOOT', 'hidden', 'hidden', 'visible'], lab)
        jx, jy = 915 * 0.18, 412 * 0.62; y0 = rider(pg)['y']
        touch('touchStart', [(1, jx, jy)]); time.sleep(0.05)
        for k in range(10): touch('touchMove', [(1, jx, jy + k * 5)]); time.sleep(0.02)
        time.sleep(0.5); touch('touchEnd', []); time.sleep(0.1); y1 = rider(pg)['y']
        check('the joystick steers the scooter', y1 > y0 + 15, [y0, y1])
        bx = pg.locator('#b_atk').bounding_box(); touch('touchStart', [(2, bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2)]); time.sleep(0.06); touch('touchEnd', []); time.sleep(0.03)
        n = pg.evaluate("__nbd.SC.shots.length")
        bx = pg.locator('#b_jmp').bounding_box(); touch('touchStart', [(3, bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2)]); time.sleep(0.08); touch('touchEnd', []); time.sleep(0.05)
        z = rider(pg)['z']
        check('SHOOT fires, JUMP hops', n >= 1 and z > 5, [n, z])
        spawn(pg, 'wander', 220); spawn(pg, 'bucket', 150, 20); time.sleep(0.3); pg.screenshot(path='tests/out/v09_touch.png')
        ctx.close()
    # ================================================================ L: comic cutscene lead-in (Nate's lazy take) + his seated line
    if 'L' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(U + '?level=2&hero=nate&god=1&cuts=1&noalarm=1'); pg.wait_for_function('window.__loaded === true', timeout=30000)
        pg.wait_for_function(f"{SC}==='play'", timeout=20000); pg.evaluate("__nbd.goScooter()")
        check('cutscene "scoot" before the Scooter Run', pg.evaluate(SC) == 'cutscene' and pg.evaluate("__nbd.game.cut.id") == 'scoot')
        time.sleep(7.6); pg.screenshot(path='docs/v09_cutscene.png')
        pg.wait_for_function(f"{SC}==='scoot'", timeout=5000)
        pg.wait_for_function("__nbd.SC.phase==='ride'", timeout=6000); time.sleep(0.3)
        check('Nate, finally sitting: "Finally. A job I can do sitting down."', pg.evaluate("__nbd.W.heroes[0].sayS") == 'Finally. A job I can do sitting down.')
        pg.close()
    # ================================================================ M: pause on the scooter
    if 'M' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(SCOOT % 'jackie' + '&god=1'); ride(pg)
        key(pg, 'Escape', after=0.3); d0 = pg.evaluate("__nbd.SC.d"); time.sleep(0.5); d1 = pg.evaluate("__nbd.SC.d")
        check('Esc pauses the ride', pg.evaluate("!!__nbd.game.overlay") and d1 == d0)
        key(pg, 'Escape', after=0.3); time.sleep(0.3)
        check('...and resumes', not pg.evaluate("!!__nbd.game.overlay") and pg.evaluate("__nbd.SC.d") > d1)
        key(pg, 'Enter', after=0.3)
        check('Start (Enter) pauses too', pg.evaluate("!!__nbd.game.overlay")); key(pg, 'Escape', after=0.2)
        pg.close()
    # ================================================================ N: the real thing, timed: the bot rides the whole level, Marv and all
    if 'N' in ONLY:
        pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
        pg.goto(SCOOT % 'jackie' + '&bot=1&god=1'); pg.wait_for_function('window.__loaded === true', timeout=30000)
        pg.wait_for_function(f"{SC}==='scoot'", timeout=30000); t0 = time.time()
        pg.wait_for_function("__nbd.SC.d > 3600", timeout=60000); pg.screenshot(path='tests/out/v09_ride.png')
        pg.wait_for_function("__nbd.SC.phase==='boss'", timeout=120000); tb = time.time() - t0
        pg.wait_for_function(f"{SC}==='stally'", timeout=120000); te = time.time() - t0
        check('one run is 60-90 s of scooter (hallway ~60 s, then the Marv chase)', 55 <= tb <= 75 and 60 <= te <= 95, [round(tb), round(te)])
        check('...and the bot parks Marv', pg.evaluate("__nbd.SC.bossBeat"))
        pg.close()
    b.close()
print('ALL PASS' if ok else 'SOME FAILED')
print('\n'.join(errs[:30]) or 'no console errors')
