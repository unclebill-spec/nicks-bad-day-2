# v0.2 patients: spawn every type (random looks), watch the elite throw syringes + urinals (splash + puddle),
# check KO drops, and the new pickups (energy drink, fruit snacks, ZYNN tin).
import time, json
from playwright.sync_api import sync_playwright
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: errs.append(f'PAGEERROR: {e}'))
    pg.goto('http://localhost:8731/?autostart=1&god=1&hero=nick'); pg.wait_for_function('window.__loaded === true'); time.sleep(3)
    pg.evaluate("(() => { const D = __nbd.Director, W = __nbd.W; D.update = function (dt) { this.shots(dt); W.enemies = W.enemies.filter((e) => e.alive); }; })()")  # freeze the wave director so only our test patients exist
    pg.evaluate("""(() => { const N = __nbd; N.W.enemies.length = 0; const h = N.W.heroes[0]; h.x = 100; h.y = 170;
      ['wanderer','spammer','escape','ivswing','sundowner','crutch','bell','elite','elite','visitor'].forEach((k, i) => { const e = N.spawn(k, 'R'); e.x = 150 + i * 24; e.tx = e.x; e.y = e.ty = 140 + (i % 4) * 16; e.set('idle'); e.cd = 99; }); })()""")
    time.sleep(0.4); pg.screenshot(path='tests/out/p_lineup.png')
    print('sheets', pg.evaluate("JSON.stringify(__nbd.W.enemies.map(e => e.sheet))"))
    # elite throws: put one elite far from the hero and let it act
    pg.evaluate("""(() => { const N = __nbd; N.W.enemies.length = 0; const h = N.W.heroes[0]; h.x = 80; h.y = 170;
      for (const i of [0, 1]) { const e = N.spawn('elite', 'R'); e.x = 300 + i * 40; e.y = e.ty = 170; e.tx = e.x; e.set('idle'); e.cd = 0; } })()""")
    seen = set(); splash = 0; puddles = 0
    for i in range(70):
        time.sleep(0.1)
        r = pg.evaluate("JSON.stringify({s: __nbd.W.shots.map(s => s.spr || s.kind), fx: __nbd.W.fx.filter(f => f.type === 'splash').length})")
        r = json.loads(r); seen.update(r['s']); splash = max(splash, r['fx']); puddles = max(puddles, r['s'].count('puddle_y'))
        if i == 18: pg.screenshot(path='tests/out/p_throw.png')
        if r['fx'] and splash == r['fx'] and i > 5 and not (seen and 'shot' in seen): pg.screenshot(path='tests/out/p_splash.png')
    print('projectiles seen', sorted(seen), 'max splash fx', splash, 'max puddles', puddles)
    # KO drops: knock out crutch / bell patients a few times, count weapon items
    drops = pg.evaluate("""(() => { const N = __nbd; N.W.enemies.length = 0; N.W.items.length = 0; let made = 0;
      for (let i = 0; i < 12; i++) { const e = N.spawn(i % 2 ? 'crutch' : 'bell', 'R'); e.x = 200; e.koBy = N.W.heroes[0]; e.onKO(); made++; }
      return N.W.items.map(it => it.k); })()""")
    print('ko drops', drops)
    # pickups (fresh page without god mode so heals show)
    pg.goto('http://localhost:8731/?autostart=1&hero=kim'); pg.wait_for_function('window.__loaded === true'); time.sleep(3)
    pg.evaluate("(() => { const D = __nbd.Director, W = __nbd.W; D.update = function (dt) { this.shots(dt); }; W.enemies.length = 0; })()")
    for k in ['energy', 'snacks', 'zynn']:
        pg.evaluate(f"(() => {{ const h = __nbd.W.heroes[0]; h.hp = 20; __nbd.drop('{k}'); }})()"); time.sleep(0.3)
        print(k, pg.evaluate("JSON.stringify([__nbd.W.heroes[0].hp, __nbd.W.heroes[0].lives])"))
    b.close()
print('\n'.join(errs[:30]) or 'no console errors')
