# v0.10.1: GINGER NERVOUS NICK, KILLER KIM, CHARGE JACKIE, WONDERFUL WILL. Names + personality roles, Bill's lines verbatim, ~30+ bubbles each
# on the Nate / Heather triggers (+ drop / throw, Jackie's team-up line), lines fit a phone bubble, Nick's copper hair is not
# Kim's red, Kim talks to the patient she just dropped, and the select / HUD / cutscene show the new names.
# Screenshots -> tests/out/v101_*.png
import time, sys, json
from playwright.sync_api import sync_playwright
U = 'http://localhost:8731/'
errs = []; ok = True
def watch(pg):
    pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: errs.append(f'PAGEERROR: {e}'))
def check(name, cond, info=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name, info if not cond else ''); sys.stdout.flush(); ok = ok and bool(cond)
def key(pg, k, hold=0.08, after=0.1): pg.keyboard.down(k); time.sleep(hold); pg.keyboard.up(k); time.sleep(after)
def ready(pg):
    pg.wait_for_function('window.__loaded === true', timeout=30000)
    pg.wait_for_function("__nbd.game.scene==='play' && __nbd.W.heroes.length>0 && __nbd.W.heroes[0].st==='idle'", timeout=30000); time.sleep(0.4)
FREEZE = "(()=>{const W=__nbd.W; W.enemies.forEach(e=>{e.alive=false}); W.enemies.length=0; W.queue && (W.queue.length=0); W.items.length=0; W.shots.length=0; W.zone=99; W.zoneOn=false; W.lockX=W.camX; W.heroes.forEach((h,i)=>{h.x=W.camX+150; h.y=176+i*20; h.face=1; h.carry=null; h.weapon=null; h.held=null; h.ride=null; h.set('idle');}); W.props=W.props.filter(p=>p.x<W.camX-60||p.x>W.camX+__nbd.G.VW+60);})()"
COUNT = """((sheet, an, hexes) => { const G = __nbd.G, A = G.atlas.chars[sheet], [cw, ch] = A.cell, i = A.anims[an].s, sx = (i % A.cols) * cw, sy = Math.floor(i / A.cols) * ch;
  const c = document.createElement('canvas'); c.width = cw; c.height = ch; const x = c.getContext('2d', { willReadFrequently: true }); x.drawImage(G.img[sheet], sx, sy, cw, ch, 0, 0, cw, ch);
  const d = x.getImageData(0, 0, cw, ch).data, out = {}; for (const h of hexes) out[h] = 0;
  for (let j = 0; j < d.length; j += 4) { if (d[j + 3] < 200) continue; const h = '#' + [d[j], d[j + 1], d[j + 2]].map(v => v.toString(16).padStart(2, '0')).join(''); if (h in out) out[h]++; } return out; })"""
TRIG = ['spawn', 'idle', 'grab', 'hurt', 'ativan', 'codeblue', 'special', 'zone', 'clear', 'throw', 'drop', 'ko', 'revive']
BAD = ['fuck', 'shit', 'bitch', 'retard', 'damn']
WANT = {'nick': ('NERVOUS NICK', 'NICK', 'Pessimist'), 'kim': ('KILLER KIM', 'KIM', 'Cheerful'), 'jackie': ('CHARGE JACKIE', 'JACKIE', 'Helpful'), 'will': ('WONDERFUL WILL', 'WILL', 'Top Dog')}
with sync_playwright() as p:
    b = p.chromium.launch()
    # ---------------------------------------------------------------- A: data + art
    pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
    pg.goto(U + '?noalarm=1'); pg.wait_for_function('window.__loaded === true', timeout=30000); time.sleep(0.5)
    D = pg.evaluate("import('./src/data.js').then(m => ({H: Object.fromEntries(['nick','kim','jackie','will'].map(k => [k, {name: m.HEROES[k].name, short: m.HEROES[k].short, role: m.HEROES[k].role, lines: m.HEROES[k].lines, scoot: m.HEROES[k].scoot, shout: m.HEROES[k].shout}])), N: m.NICK_LINES, K: m.KIM_LINES, J: m.JACKIE_LINES, Wl: m.WILL_LINES}))")
    for k, (nm, sh, role) in WANT.items():
        H = D['H'][k]; allL = [s for v in H['lines'].values() for s in v]; uniq = set(allL + [s for v in H['scoot'].values() for s in v])
        check(f'{k}: name {nm} / short {sh} / role {role}', (H['name'], H['short'], H['role']) == (nm, sh, role), (H['name'], H['short'], H['role']))
        check(f'{k}: ~30+ distinct lines ({len(uniq)})', len(uniq) >= 28, len(uniq))
        check(f'{k}: every trigger has lines', all(H['lines'].get(t) for t in TRIG) and all(H['scoot'].get(t) for t in ('start', 'crash', 'snack', 'hit')), [t for t in TRIG if not H['lines'].get(t)])
        check(f'{k}: lines short enough for a phone bubble (<= 60 chars)', max(map(len, uniq)) <= 60, max(uniq, key=len))
        check(f'{k}: PG-13 (no slurs / strong swears)', not any(w in s.lower() for s in uniq for w in BAD))
        check(f'{k}: own Ativan shout fits', H['shout'] and max(map(len, H["shout"])) <= 24, H['shout'])
    gl = lambda k: [s for v in D['H'][k]['lines'].values() for s in v]
    check("Bill's Nick lines verbatim", all(s in gl('nick') for s in D['N']) and len(D['N']) == 3, D['N'])
    check("Bill's Kim line verbatim", all(s in gl('kim') for s in D['K']))
    check("Bill's Jackie lines verbatim", all(s in gl('jackie') for s in D['J']) and len(D['J']) == 5, D['J'])
    for s in ["It's a full moon, isn't it? I knew it.", "Don't say the Q word.", "We're short two nurses again.", "I haven't peed in nine hours.", 'Of course the Pyxis is down.',
              "Watch, they'll float me to the ICU.", "Something's gonna code before shift change.", "I'm never getting a lunch break.", "Charge nurse is looking at me. That's bad.", 'This is fine. Nothing is fine.']:
        check(f'nick says: {s}', s in gl('nick'))
    for s in ["Oopsie! Let's get you tucked in!", "Fall risk! Good thing I'm here!", 'Nap time, sweetie!', 'Great job resting! Stay down!', "I'll chart that as a mechanical fall!",
              "Let's work on those deep breaths, okay?", "You're doing amazing! Stay on the floor!", "Bed alarm's on, hon!", "Smile! It's a beautiful day on the unit!", 'Ambulation goal met!', "I'll get you a warm blanket after this!"]:
        check(f'kim says: {s}', s in gl('kim'))
    check('kim: extra lines for knockdowns / grabs / throws / special', len(D['H']['kim']['lines']['drop']) >= 6 and len(D['H']['kim']['lines']['grab']) >= 3 and len(D['H']['kim']['lines']['throw']) >= 3 and len(D['H']['kim']['lines']['special']) >= 3)
    for s in ["I'll grab the next admit, you take a breather.", "Go eat lunch, I've got your patients.", "I'll call pharmacy for you.", 'Need another set of hands in 12?', "I'll start that IV.",
              "Don't worry, I'll talk to the family.", "I've got the call light!", "Who's drowning? Point me at it.", "I'll take the rapid response.", 'Teamwork makes the dream work!']:
        check(f'jackie says: {s}', s in gl('jackie'))
    check("Bill's Will lines verbatim", all(s in gl('will') for s in D['Wl']) and len(D['Wl']) == 6, D['Wl'])
    for s in ['Patient satisfaction scores just went up.', 'They should name the unit after me.', 'One stick. Every time.', 'Hold your applause.', 'Nurse of the Year, three years running. In my heart.',
              "You're welcome, everybody.", 'Doctors ask ME for advice.', 'Did someone say rock star?', "I don't break a sweat, I break records.", 'Watch and learn, rookies.']:
        check(f'will says: {s}', s in gl('will'))
    check('jackie: Charge Nurse team-up line', bool(D['H']['jackie']['lines'].get('teamup')))
    C = pg.evaluate(f"({COUNT})('nick', 'idle', ['#e8842e', '#b0581c', '#f6dc72', '#c9a640', '#e2aa88'])")
    K = pg.evaluate(f"({COUNT})('kim', 'idle', ['#d8462a', '#e8842e'])")
    check('nick: copper-orange ginger hair, no old blond', C['#e8842e'] + C['#b0581c'] > 20 and C['#f6dc72'] + C['#c9a640'] == 0, C)
    check("kim: still her own red (not Nick's copper)", K['#d8462a'] > 10 and K['#e8842e'] == 0, K)
    dist = sum((int('e8842e'[i:i + 2], 16) - int('d8462a'[i:i + 2], 16)) ** 2 for i in (0, 2, 4)) ** 0.5
    check(f'nick vs kim hair colour distance {dist:.0f} (> 50)', dist > 50)
    Wc = pg.evaluate(f"({COUNT})('will', 'idle', ['#2f86f6', '#1c5ec4', '#e0303a', '#a81e28', '#2fae4a', '#1e7e34', '#f4f6fa', '#c8d0dc', '#ffe84a', '#2a3658', '#1c2440', '#ff8a1e', '#e87a1a'])")
    check('will: Christmas sweater (blue knit + red band/hem/cuffs + green tree + white snowflakes)', Wc['#2f86f6'] + Wc['#1c5ec4'] > 40 and Wc['#e0303a'] + Wc['#a81e28'] > 8 and Wc['#2fae4a'] + Wc['#1e7e34'] >= 3 and Wc['#f4f6fa'] + Wc['#c8d0dc'] >= 4, Wc)
    check('will: navy pants kept, no pumpkin orange', Wc['#2a3658'] + Wc['#1c2440'] > 40 and Wc['#ff8a1e'] + Wc['#e87a1a'] == 0, Wc)
    Wf = pg.evaluate("""(() => { const G = __nbd.G, r = G.atlas.sprites.rects.face_will, c = document.createElement('canvas'); c.width = r[2]; c.height = r[3]; const x = c.getContext('2d'); x.drawImage(G.img.sprites, r[0], r[1], r[2], r[3], 0, 0, r[2], r[3]);
      const d = x.getImageData(0, 0, r[2], r[3]).data; let n = 0; for (let j = 0; j < d.length; j += 4) if (d[j] === 0xe0 && d[j + 1] === 0x30 && d[j + 2] === 0x3a) n++; return n; })()""")
    check('will: HUD face shows the sweater collar', Wf > 4, Wf)
    key(pg, 'Enter', after=0.8); pg.screenshot(path='tests/out/v101_select.png'); pg.close()
    # ---------------------------------------------------------------- B: bubbles in play (desktop + phone width)
    for vw, tag in ((960, 'desk'), (740, 'phone')):
        for hero in ('nick', 'kim', 'jackie', 'will'):
            pg = b.new_page(viewport={'width': vw, 'height': 360 if tag == 'phone' else 540}); watch(pg)
            pg.goto(U + f'?level=1&hero={hero}&god=1&nocut=1&noalarm=1'); ready(pg); pg.evaluate(FREEZE); time.sleep(0.3)
            if hero == 'kim':
                pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0]; const e=__nbd.spawn('wanderer','R'); e.x=h.x+24; e.y=h.y; e.tx=e.x; e.ty=e.y; e.set('idle'); e.cd=99; e.atkCd=99; h.sayCd=0; h.sayS=null; W.said=[]; window.E=e;})()")
                got = None
                for k in range(50):
                    key(pg, 'KeyJ', hold=0.05, after=0.09)
                    st = pg.evaluate("[__nbd.W.heroes[0].sayS, E.st]")
                    if st[0] and st[1] in ('fall', 'down', 'dead'): got = st; break
                check(f'{tag}: Killer Kim talks to the patient she just knocked down', got and got[0] in D['H']['kim']['lines']['drop'], got)
            else:
                ln = max(gl(hero), key=len)
                pg.evaluate("(()=>{const h=__nbd.W.heroes[0]; h.sayCd=0; h.d.lines.__t=[%s]; h.say('__t', true);})()" % json.dumps(ln)); time.sleep(0.4)
            r = pg.evaluate("(()=>{const h=__nbd.W.heroes[0], G=__nbd.G; const s=h.sayS||''; const n=s.length>60?27:s.length>36?22:18; let L=[],c=''; for (const w of s.split(' ')) { if (c && (c+' '+w).length>n) { L.push(c); c=w; } else c=c?c+' '+w:w; } if (c) L.push(c); return {s, w: Math.max(...L.map(q=>q.length))*8+8, rows: L.length, VW: G.VW}; })()")
            check(f'{tag}: {hero} bubble fits the screen ({r["w"]}px of {r["VW"]}, {r["rows"]} rows)', r['s'] and r['w'] <= r['VW'] - 4 and r['rows'] <= 4, r)
            time.sleep(0.2); pg.screenshot(path=f'tests/out/v101_{tag}_{hero}.png'); pg.close()
    # ---------------------------------------------------------------- C: their takes in the cutscenes (opening scene on screen)
    pg = b.new_page(viewport={'width': 960, 'height': 540}); watch(pg)
    pg.goto(U + '?level=1&hero=nick&god=1&noalarm=1&cuts=1'); pg.wait_for_function("window.__loaded===true", timeout=30000)
    pg.wait_for_function("__nbd.game.scene==='cutscene'", timeout=30000)
    txt = pg.evaluate("__nbd.game.cut.panels.map(f => (f(398, 160).bubbles || []).map(b => b.s)).flat()")
    check("opening cutscene: Nervous Nick's own line", "A RUNNER? Of course there's a runner." in txt, txt[:3])
    pg.wait_for_function("__nbd.game.scene==='cutscene' && __nbd.game.cut.lastPanel===1", timeout=30000); time.sleep(1.6)
    pg.screenshot(path='tests/out/v101_cut_nick.png')
    TAKE = {'nick': "Something's gonna code. Watch.", 'kim': 'Best. Shift. EVER!', 'jackie': "I've got your patients!", 'will': "I've earned it. Every day."}
    for hero, want in TAKE.items():
        T = pg.evaluate("""(async (id) => { const m = await import('./src/cutscene.js'); const W = __nbd.W, keep = W.heroes.slice(); W.heroes.length = 0; W.heroes.push({ id });
          const o = []; for (const c of ['lunch', 'ending', 'scoot', 'night']) o.push(...m.makeCut(c).panels.map(f => (f(398, 160).bubbles || []).map(b => b.s)).flat());
          W.heroes.length = 0; W.heroes.push(...keep); return o; })""", hero)
        check(f'cutscenes: {hero} has their own take', any(want in t for t in T), T[:4])
        check(f'cutscenes: {hero} lines stay short (<= 72 chars, wrapped by the panel)', max(map(len, T)) <= 72, max(T, key=len))
    pg.close()
    b.close()
print('no console errors' if not errs else 'CONSOLE ERRORS: ' + '; '.join(errs[:6]))
print('ALL PASS' if ok and not errs else 'SOME FAIL')
