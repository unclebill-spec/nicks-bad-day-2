# v0.3 breakables: crash carts roll + plow patients + bounce off the screen edges + break apart; every prop kind breaks
# after a few hits (debris, drops); props slide; patients knocked / thrown into props; loot rates; props never block;
# keyboard, gamepad (as P2 in 2-player) and touch all smash props. Screenshots -> tests/out/props_*.png
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
CLEAR = "(()=>{const W=__nbd.W; W.enemies.forEach(e=>{e.alive=false}); W.enemies.length=0; W.director.queue && (W.director.queue.length=0); W.queue && (W.queue.length=0); W.items.length=0;})()"
HOLD = "(()=>{const W=__nbd.W; W.lockX = W.camX; })()"
def place(pg, kind, dx=24, dy=0, hx=110, drops='[]'):
    return pg.evaluate(f"(()=>{{const W=__nbd.W,h=W.heroes[0]; h.x=W.camX+{hx}; h.y=172; h.face=1; h.set('idle'); return __nbd.prop('{kind}',{dx},{dy},{drops});}})()")
P = lambda i: f"(()=>{{const p=__nbd.W.props[{i}]; return {{x:Math.round(p.x), y:Math.round(p.y), vx:Math.round(p.vx), hp:p.hp, st:p.st}}}})()"
ok = True
def check(name, cond, info=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name, info); ok = ok and bool(cond)

with sync_playwright() as p:
    b = p.chromium.launch()
    # ---------------------------------------------------------------- A: keyboard, Nick
    pg = b.new_page(viewport={'width': 1280, 'height': 720}); watch(pg)
    pg.goto(U + '?autostart=1&hero=nick&god=1'); ready(pg)
    # level layout sanity: every placed prop is on the floor band
    lay = pg.evaluate("__nbd.W.props.slice(0,36).map(p=>[p.kind,p.y])")
    check('level props placed on the floor', len(lay) >= 30 and all(136 <= y <= 212 for k, y in lay), len(lay))
    pg.evaluate(CLEAR); pg.evaluate(HOLD); pg.evaluate("__nbd.W.props.length = 0")  # a clean stretch of floor for the physics checks
    # 1) crash cart: punch -> rolls right, plows a patient, bounces off the right screen edge
    ci = place(pg, 'crashcart', 22)
    pg.evaluate("(()=>{const W=__nbd.W; __nbd.spawn('wanderer','R'); const e=W.enemies[W.enemies.length-1]; e.x=W.camX+250; e.y=172; e.st='idle'; e.cd=99; e.tx=e.x; e.ty=e.y; window.E=e;})()")
    time.sleep(0.1); key(pg, 'KeyK', 0.06, 0.12); key(pg, 'KeyJ', 0.05, 0.0)
    v0 = {'vx': 0}
    for i in range(12):
        s = pg.evaluate(P(ci))
        if abs(s['vx']) > abs(v0['vx']): v0 = s
        time.sleep(0.03)
    seen_down, max_x, flipped = False, 0, False
    for i in range(30):
        s = pg.evaluate(P(ci)); est = pg.evaluate("E.st"); max_x = max(max_x, s['x'])
        seen_down = seen_down or est in ('fall', 'down', 'getup'); flipped = flipped or s['vx'] < 0
        time.sleep(0.06)
    pg.screenshot(path='tests/out/props_cart_roll.png')
    check('jump kick sends the crash cart rolling', v0['vx'] > 150, v0)
    check('rolling cart knocks the patient down', seen_down, pg.evaluate("[E.st, E.hp, E.maxHp]"))
    vw = pg.evaluate("__nbd.G.VW"); cam = pg.evaluate("__nbd.W.camX")
    pg.evaluate(f"(()=>{{const W=__nbd.W,p=W.props[{ci}],h=W.heroes[0]; W.props.forEach(q=>{{if(q!==p&&q.x>W.camX+{vw}-160&&q.x<W.camX+{vw}+60) q.x+=600;}}); p.vx=0; p.x=W.camX+{vw}-90; p.y=172; h.x=p.x-26; h.y=172; h.face=1; h.set('idle');}})()")
    key(pg, 'KeyK', 0.06, 0.12); key(pg, 'KeyJ', 0.05, 0.0); max_x, flipped = 0, False
    for i in range(25):
        s = pg.evaluate(P(ci)); max_x = max(max_x, s['x']); flipped = flipped or s['vx'] < 0; time.sleep(0.04)
    check('cart bounces off the screen edge', flipped and max_x <= cam + vw, f'max_x={max_x} edge={cam + vw}')
    # 2) keep hitting a fresh one until it breaks apart: drawers/supplies debris + score
    pg.evaluate(CLEAR); pg.evaluate("__nbd.W.props.length=0"); ci = place(pg, "crashcart", 24)
    s0 = pg.evaluate("__nbd.W.heroes[0].score"); n = 0
    for i in range(12):
        if pg.evaluate(P(ci))['st'] >= 2: break
        pg.evaluate(f"(()=>{{const W=__nbd.W,p=W.props[{ci}],h=W.heroes[0]; p.vx=0; h.x=p.x-22; h.y=p.y; h.face=1; h.set('idle'); h.step=0; h.gap=9;}})()")
        key(pg, 'KeyJ', after=0.3); n += 1
    chunks = pg.evaluate("__nbd.W.fx.filter(f=>f.type==='chunk').length")
    pg.screenshot(path='tests/out/props_cart_smash.png')
    check('crash cart breaks after several hits', pg.evaluate(P(ci))['st'] == 2 and 2 <= n <= 6, f'hits={n}')
    check('debris flies', chunks >= 6, f'chunks={chunks}')
    check('smash scores points', pg.evaluate("__nbd.W.heroes[0].score") > s0)
    # 2b) a full ground combo (jab, jab, jab, finisher) smashes a fresh crash cart without it escaping
    pg.evaluate(CLEAR); pg.evaluate("__nbd.W.props.length=0"); ci2 = place(pg, "crashcart", 24)
    pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.step=0; h.gap=9;})()")
    for k in range(4):
        key(pg, 'KeyJ', 0.05, 0.22)
    time.sleep(0.4); s = pg.evaluate(P(ci2))
    check('one full combo smashes a crash cart', s['st'] == 2, s)
    # 3) every kind breaks after a few hits; movers move, the vending machine does not
    res = {}
    for kind in ['crashcart', 'supplycart', 'medcart', 'wheelchair', 'linen', 'ivstand', 'chair', 'trash', 'plant', 'wetfloor', 'vending']:
        pg.evaluate(CLEAR); pg.evaluate("__nbd.W.props.forEach(p=>{if(p.st<2){p.vx=0}})")
        i = place(pg, kind, 26 if kind != 'vending' else 30, 0, 90); x0 = pg.evaluate(P(i))['x']; moved = 0; hits = 0
        for k in range(12):
            s = pg.evaluate(P(i))
            if s['st'] >= 2: break
            pg.evaluate(f"(()=>{{const W=__nbd.W,p=W.props[{i}],h=W.heroes[0]; h.x=p.x-{30 if kind=='vending' else 24}; h.y=p.y; h.face=1; h.set('idle'); h.step=0; h.gap=9;}})()")
            key(pg, 'KeyJ', after=0.04); time.sleep(0.25); hits += 1
            moved = max(moved, abs(pg.evaluate(P(i))['x'] - x0))
            pg.evaluate(f"__nbd.W.props[{i}].vx=0")
        res[kind] = (pg.evaluate(P(i))['st'], hits, moved)
    print(json.dumps(res))
    check('all prop kinds break in 1-6 hits', all(v[0] == 2 and 1 <= v[1] <= 6 for v in res.values()))
    check('kickable props move, vending machine stays put', all(v[2] >= 2 for k, v in res.items() if k != 'vending') and res['vending'][2] == 0)
    # 4) patient knocked into a cart sends it rolling; thrown patient smashes a chair
    pg.evaluate(CLEAR); i = place(pg, 'supplycart', 120, 0, 60)
    pg.evaluate(f"(()=>{{const W=__nbd.W; __nbd.spawn('escape','R'); const e=W.enemies[W.enemies.length-1]; const p=W.props[{i}]; e.x=p.x-40; e.y=p.y; e.st='idle'; e.cd=99; e.knock(1, 220, 160); window.E=e;}})()")
    time.sleep(0.8); s = pg.evaluate(P(i))
    check('patient knocked into a cart shoves + damages it', s['hp'] < 4 and s['x'] > pg.evaluate(f"__nbd.W.heroes[0].x") + 130, s)
    pg.evaluate(CLEAR); i = place(pg, 'chair', 110, 0, 60)
    pg.evaluate(f"(()=>{{const W=__nbd.W,h=W.heroes[0]; __nbd.spawn('wanderer','R'); const e=W.enemies[W.enemies.length-1]; e.x=h.x+14; e.y=h.y; e.st='idle'; e.cd=99; e.thrownBy(h, 1, 1);}})()")
    time.sleep(0.9); s = pg.evaluate(P(i))
    check('thrown patient smashes into a chair', s['hp'] < 2, s)
    # 5) props never block: walk straight through an intact plant
    pg.evaluate(CLEAR); i = place(pg, 'plant', 40, 0, 60); hx0 = pg.evaluate("__nbd.W.heroes[0].x")
    pg.keyboard.down('KeyD'); time.sleep(1.2); pg.keyboard.up('KeyD')
    check('hero walks through props (no blocking)', pg.evaluate("__nbd.W.heroes[0].x") > pg.evaluate(P(i))['x'] + 10 or pg.evaluate(P(i))['st'] >= 0 and pg.evaluate("__nbd.W.heroes[0].x") - hx0 > 60)
    # 6) loot odds (20k rolls per table, ZYNN capped at one per level from props)
    rates = pg.evaluate("""(()=>{const W=__nbd.W, out={}; for (const t of ['cart','linen','trash','small','vending']) { W.zynnProps=-1e9; const c={}; let any=0;
      for (let i=0;i<20000;i++){ const k=__nbd.rollLoot(t); if(k){any++; c[k]=(c[k]||0)+1;} } out[t]={drop:+(any/200).toFixed(1), zynn:+((c.zynn||0)/200).toFixed(2), weapon:+(Object.keys(c).filter(k=>k.startsWith('w:')).reduce((s,k)=>s+c[k],0)/200).toFixed(1)}; }
      W.zynnProps=0; let z=0; for (let i=0;i<5000;i++) if(__nbd.rollLoot('cart')==='zynn') z++; out.zynnCap=z; W.zynnProps=0; return out;})()""")
    print(json.dumps(rates))
    check('drop rates sensible', 70 <= rates['cart']['drop'] <= 90 and 30 <= rates['small']['drop'] <= 55 and rates['small']['zynn'] <= 1.5 and rates['zynnCap'] == 1)
    pg.close()
    # ---------------------------------------------------------------- B: 2 players, keyboard P1 + gamepad P2
    MOCK = """(() => { const pad = { id: 'Xbox Wireless Controller (STANDARD GAMEPAD)', index: 0, connected: true, mapping: 'standard', timestamp: 0,
      axes: [0, 0, 0, 0], buttons: Array.from({ length: 17 }, () => ({ pressed: false, value: 0, touched: false })) };
      window.__pad = pad; navigator.getGamepads = () => [window.__padOn ? pad : null, null, null, null];
      window.__padSet = (i, on) => { pad.buttons[i].pressed = on; pad.buttons[i].value = on ? 1 : 0; pad.timestamp++; };
      window.__padConnect = () => { window.__padOn = true; const e = new Event('gamepadconnected'); e.gamepad = pad; dispatchEvent(e); }; })();"""
    pg = b.new_page(viewport={'width': 1280, 'height': 720}); pg.add_init_script(MOCK); watch(pg)
    def tap(i, hold=0.1): pg.evaluate(f'__padSet({i}, true)'); time.sleep(hold); pg.evaluate(f'__padSet({i}, false)'); time.sleep(0.12)
    pg.goto(U + '?god=1'); pg.wait_for_function('window.__loaded === true'); time.sleep(0.5)
    key(pg, 'KeyS', after=0.2); key(pg, 'Enter', after=0.5)
    pg.evaluate('__padConnect()'); time.sleep(0.3); tap(2); time.sleep(0.3); tap(15); tap(2)
    key(pg, 'KeyJ', after=1.0)
    pg.wait_for_function("__nbd.game.scene==='play' && __nbd.W.heroes.length===2 && __nbd.W.heroes.every(h=>h.st==='idle')", timeout=30000); time.sleep(0.3)
    pg.evaluate(CLEAR); pg.evaluate(HOLD)
    a = pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0]; h.x=W.camX+90; h.y=150; h.face=1; return __nbd.prop('trash',24,0);})()")
    bb = pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[1]; h.x=W.camX+90; h.y=200; h.face=1; h.set('idle'); const p=__nbd.prop('crashcart',0,0); W.props[p].x=h.x+24; W.props[p].y=200; return p;})()")
    key(pg, 'KeyJ', after=0.2); tap(2); time.sleep(0.3)
    sa, sb = pg.evaluate(P(a)), pg.evaluate(P(bb))
    pg.screenshot(path='tests/out/props_2p.png')
    check('2P: keyboard P1 hits a trash can', sa['hp'] < 2 or sa['st'] == 2, sa)
    check('2P: gamepad P2 hits a crash cart', sb['hp'] < 5, sb)
    pg.close()
    # ---------------------------------------------------------------- C: touch (emulated phone landscape)
    UA = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36'
    ctx = b.new_context(viewport={'width': 915, 'height': 412}, device_scale_factor=2.6, is_mobile=True, has_touch=True, user_agent=UA)
    pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg); watch(pg)
    def touch(kind, pts): cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [{'x': x, 'y': y, 'id': i} for i, x, y in pts]})
    pg.goto(U + '?autostart=1&hero=jackie&god=1'); ready(pg)
    pg.evaluate(CLEAR); pg.evaluate(HOLD); i = place(pg, 'wheelchair', 26)
    r = pg.locator('#pad .ab[data-b=atk]').bounding_box(); ax, ay = r['x'] + r['width'] / 2, r['y'] + r['height'] / 2
    touch('touchStart', [(2, ax, ay)]); time.sleep(0.06); touch('touchEnd', []); time.sleep(0.25)
    s = pg.evaluate(P(i)); pg.screenshot(path='tests/out/props_touch.png')
    check('touch: HIT button kicks a wheelchair', s['hp'] < 3, s)
    ctx.close()
    # ---------------------------------------------------------------- D: the bot plays zones 4-5 with all the props (no softlock)
    pg = b.new_page(viewport={'width': 1280, 'height': 720}); watch(pg)
    pg.goto(U + '?autostart=1&hero=will&god=1&bot=1&zone=3'); pg.wait_for_function('window.__loaded === true', timeout=30000)
    t0 = time.time(); last = None
    while time.time() - t0 < 230:
        z = pg.evaluate("[__nbd.W.zone, !!__nbd.W.boss, Math.round(__nbd.W.camX), __nbd.W.props.filter(p=>p.st>=2).length]")
        if z != last: last = z
        if z[1]: break
        time.sleep(2)
    pg.screenshot(path='tests/out/props_bot_boss.png')
    check('bot reaches the boss with props in play (no softlock)', last and last[1], last)
    b.close()
print('ALL PASS' if ok else 'SOME FAILED')
print('\n'.join(errs[:30]) or 'no console errors')
