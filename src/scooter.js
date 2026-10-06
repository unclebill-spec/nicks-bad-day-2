// v0.9 SCOOTER RUN: a TMNT sewer-surf style driving level between Radiology and the Night Shift. The nurses chase
// Motorcart Marv down the long Floor 4 hallway on hospital mobility scooters. The screen auto-scrolls; UP / DOWN steers
// across the lanes, RIGHT / LEFT speeds up or eases off a little, JUMP hops floor junk (tipped trash cans, mop buckets,
// spills), ATTACK flicks Ativan syringes forward to put patients to sleep. Crashing into a wet-floor sign, a gurney, a
// cart or a patient costs health (then a short blink of invincibility). Snacks heal; a rare ZYNN tin is a 1-up.
// ~60 s of hallway, then the Marv chase (~20 s). Score, lives and continues are the Hero objects' own, so they carry.
//
// Coordinates: hallway things have a world x (distance down the hall, S.d = how far the camera has scrolled); riders
// and Marv live in screen x. y is the usual floor depth (Y_MIN..Y_MAX), z the height off the floor. W.camX stays 0 so
// the shared effects (floatText, word, dust, sparks) can be placed in screen x.
import { G, spr, text, rect, panel, frame, anim, sprSize, ellipse } from './gfx.js';
import { ITEMS, Y_MIN, Y_MAX } from './data.js';
import { W, buildLevel, floatText, word, addFx, shake, offY, FLOOR_Y, updateWorld, drawFx } from './world.js';
import { lookFor } from './enemy.js';
import { sfx } from './sound.js';

export const SC = { phase: 'off', t: 0, d: 0, speed: 0, ob: [], shots: [], pr: [], boss: null, tip: null, n: 0, crashes: 0, sedated: 0, bossBeat: false, done: false, over: false, endT: 0 };
export const SCOOT = { len: 10600, base: 172, jumpV: 236, grav: 760, steer: 96, dmg: 14, inv: 1.6, cd: 0.22, hold: 0.3, shotV: 330, bossHp: 30, bossHp2: 42, bossMax: 24 };
const YT = Y_MIN + 6, YB = Y_MAX - 2, MID = (YT + YB) / 2;
const rr = (a, b) => a + W.rnd() * (b - a);
const pick = (a) => a[Math.floor(W.rnd() * a.length)];
const lane = () => rr(YT + 4, YB - 4);
// hallway hazards: w / dep = half length / half depth of the footprint, h = height, jump = a scooter can hop it, tall = never
const KIND = {
  sign: { spr: 'wetfloor0', ax: 10, ay: 27, w: 7, dep: 6, h: 28, tall: true, stop: true },
  gurney: { spr: 'gurney', ax: 26, ay: 25, w: 24, dep: 7, h: 26, tall: true, stop: true },
  cart: { spr: 'supplycart0', ax: 17, ay: 39, w: 14, dep: 7, h: 40, tall: true, stop: true },
  med: { spr: 'medcart0', ax: 15, ay: 31, w: 13, dep: 7, h: 32, tall: true, stop: true },
  iv: { spr: 'ivstand0', ax: 10, ay: 55, w: 4, dep: 4, h: 56, tall: true },
  can: { spr: 'tipcan', ax: 17, ay: 15, w: 13, dep: 5, h: 12, jump: true },
  bucket: { spr: 'mopbucket', ax: 16, ay: 19, w: 13, dep: 5, h: 16, jump: true },
  spill: { spr: 'puddle_g', ax: 14, ay: 4, w: 12, dep: 5, h: 2, jump: true, skid: true },
  item: { w: 9, dep: 9, h: 20, pickup: true },
};
const FOE = {  // patients: look = whose sheet (randomly recoloured), hp = syringes to sleep, vx = world speed (negative = at you)
  wander: { look: 'wanderer', an: 'walk', hp: 1, score: 200, lines: ['Is this the cafeteria?', 'Where am I?', 'Nurse? NURSE?'] },
  charge: { look: 'escape', an: 'walk', hp: 1, score: 250, vx: -78, rate: 14, lines: ['RACE YA!', 'MY TURN TO DRIVE!', 'WHEEEE!'] },
  thrower: { look: 'tray', an: 'idle', hp: 2, score: 300, lines: ['CATCH!', 'JELLO TIME!', 'FOOD FIGHT!'] },
  wheel: { look: 'sundowner', an: 'wheel', hp: 2, score: 300, vx: -112, lines: ['WHEELCHAIR DERBY!', 'OUTTA MY WAY!', 'BEEP BEEP!'] },
};
const SLEEP = ['Nice scooter... zzz', 'Five more minutes... zzz', 'Wheee... zzz', 'Is it lunch? ...zzz', 'zzz...'];
// rider lines live in HEROES[id].scoot (v0.8 Nate, v0.10 Heather): start, crash, snack, hit

// ---------------------------------------------------------------- the hallway (a 1536 px loop) and the course
function buildHall() {
  const wall = [[16, 'door0'], [100, 'window0'], [196, 'poster_hands'], [236, 'sign_rooms1'], [300, 'door0'], [380, 'chairs'], [470, 'window1'], [560, 'poster_quiet'],
    [610, 'fountain'], [680, 'door0'], [770, 'plant1'], [840, 'window2'], [930, 'sign_exit'], [960, 'door0'], [1050, 'poster_duck'], [1100, 'station'],
    [1260, 'window0'], [1350, 'door0'], [1440, 'poster_bingo']];
  buildLevel({ id: 'S', name: 'SCOOTER RUN', width: 1536, music: 'scooter', tint: 'rgba(255,140,80,0.10)', wall, zones: [], props: [] });
  W.scootBg = W.bg;
}
function addOb(k, x, y, extra = {}) { const o = { k, x, y, z: 0, t: 0, ...KIND[k], ...extra }; SC.ob.push(o); return o; }
function addFoe(f, x, y, extra = {}) {
  const d = FOE[f], n = ++SC.n;
  return addOb('foe', x, y, { foe: f, d, hp: d.hp, sheet: lookFor(f === 'wheel' ? pick(['sundowner', 'o2', 'wanderer']) : d.look, n), vx: d.vx || 0, w: f === 'wheel' ? 12 : 8, dep: 7, h: 50, st: 'go', cd: rr(0.3, 0.9), ph: W.rnd() * 6, said: false, ...extra });
}
function addItem(k, x, y) { return addOb('item', x, y, { item: k }); }
function buildCourse() {
  const L = SCOOT.len;
  SC.ob = []; SC.tips = [[260, 'STEER UP / DOWN.  RIGHT = FASTER'], [480, 'JUMP OVER JUNK ON THE FLOOR!'], [1020, 'ATTACK = ATIVAN SYRINGE!'], [1700, 'DODGE SIGNS, GURNEYS + CARTS!']];
  addOb('can', 640, MID); addOb('bucket', 860, YT + 12); addOb('can', 900, YB - 10);
  addItem('snacks', 960, MID);
  addFoe('wander', 1180, MID - 10); addFoe('wander', 1330, YB - 14);
  addOb('sign', 1760, YT + 8); addOb('sign', 1760, YB - 8); addOb('gurney', 1980, MID);
  let x = 2200, zynn = 0;
  while (x < L - 260) {
    const p = x / L, r = W.rnd();
    if (p > 0.44 && !SC.derby) {  // set piece: the wheelchair derby
      SC.derby = true; SC.tips.push([x - 260, 'WHEELCHAIR DERBY!']);
      [YT + 10, MID, YB - 10, MID - 18].forEach((y, i) => addFoe('wheel', x + 120 + i * 150, y));
      x += 720; continue;
    }
    if (p > 0.68 && !SC.slalom) {  // set piece: gurney slalom
      SC.slalom = true; SC.tips.push([x - 260, 'GURNEY SLALOM!']);
      for (let i = 0; i < 5; i++) addOb('gurney', x + i * 130, i % 2 ? YB - 12 : YT + 12);
      addItem('donut', x + 330, MID);
      x += 760; continue;
    }
    if (r < 0.15) addOb(pick(['can', 'bucket']), x, lane());
    else if (r < 0.25 && p > 0.15) { const y0 = rr(-4, 4); [YT + 8, MID, YB - 8].forEach((y) => addOb(pick(['can', 'bucket', 'spill']), x + rr(-5, 5), y + y0)); addItem('energy', x + 70, lane()); }
    else if (r < 0.36) addOb(pick(['sign', 'sign', 'cart', 'med', 'iv']), x, lane());
    else if (r < 0.44) { const y1 = rr(YT + 2, MID - 14); addOb(pick(['sign', 'cart', 'med']), x, y1); addOb(pick(['sign', 'cart', 'med']), x + rr(-10, 10), y1 + rr(44, 54)); }
    else if (r < 0.52) addOb('gurney', x, lane());
    else if (r < 0.64) addFoe('wander', x, lane());
    else if (r < 0.74 && p > 0.12) addFoe('charge', x + 160, lane());
    else if (r < 0.84 && p > 0.22) addFoe('thrower', x, W.rnd() < 0.5 ? YT - 2 : YB + 2);
    else if (r < 0.92 && p > 0.3) addFoe('wheel', x + 200, lane());
    else addItem(pick(['snacks', 'jerky', 'donut', 'energy']), x, lane());
    if (p > 0.6 && !zynn) { zynn++; addItem('zynn', x + 60, lane()); }  // one occasional ZYNN tin (+1 life) per run
    x += rr(170, 270) * (1 - 0.28 * p);
  }
  SC.tips.sort((a, b) => a[0] - b[0]);
}

// ---------------------------------------------------------------- start / riders
const riders = () => W.heroes.filter((h) => h.sc && h.st !== 'out');
export function startScooter(game) {
  SC.game = game;
  buildHall();
  W.enemies = []; W.boss = null; W.shots = []; W.fx = []; W.items = []; W.props = []; W.decor = []; W.bgHook = null; W.team = null; W.t = 0; W.camX = 0; W.camMin = 0; W.dark = 0;
  W.zone = -1; W.go = 0; W.cleared = false; W.scoot = true; W.clock = 18 * 60 + 30; W.stats.time = 0;
  Object.assign(SC, { phase: 'intro', t: 0, d: 0, speed: SCOOT.base, shots: [], pr: [], boss: null, tip: null, n: 0, crashes: 0, sedated: 0, bossBeat: false, done: false, over: false, endT: 0, derby: false, slalom: false, fg: 0 });
  buildCourse();
  W.heroes.forEach((h, i) => {
    h.sc = { x: -40 - i * 30, y: MID - 16 + i * 32, z: 0, vz: 0, inv: 0, crash: 0, cd: 0, fire: 0, spin: 0, col: h.slot ? 'blue' : 'red', bx: 84 - i * 14 };
    h.scKO = 0; h.scSnack = 0; h.scCrash = 0; h.weapon = null; h.carry = null; h.held = null; h.grabber = null; h.ride = null; h.combo = 0; h.inv = 0; h.vx = h.vy = h.vz = 0;
    if (h.st === 'out') { if (game.continuesLeft() > 0) h.continueT = 10; return; }
    h.hp = h.maxHp; h.set('idle'); h.face = 1;
  });
  sfx('scoot', { vol: 0.6 });
}
function syncHero(h) {  // keep the Hero's own x / y / z on its rider so speech bubbles and the HUD follow it
  const r = h.sc; h.x = r.x; h.y = r.y; h.z = r.z + 4; h.face = 1;
  if (h.sayS && W.t > h.sayUntil) h.sayS = null;
}
function line(h, ev) {
  const L = h.d.scoot && h.d.scoot[ev];
  if (!L || !L.length) return;
  if (ev !== 'start' && W.t < h.sayCd) return;
  h.sayS = pick(L); h.sayUntil = W.t + 2.6 + Math.max(0, h.sayS.length - 34) * 0.045; h.sayCd = h.sayUntil + 1.9 + (ev === 'hit' ? 4 : 0);
  (W.said || (W.said = [])).push(h.sayS);
}
function crash(h, dmg, what, push = 14) {
  const r = h.sc;
  if (r.inv > 0 || h.st === 'out' || SC.phase === 'finish') return false;
  r.inv = SCOOT.inv; r.crash = 0.55; r.x = Math.max(16, r.x - push); r.vz = Math.max(r.vz, 60);
  SC.crashes++; h.scCrash++;
  if (!SC.god) h.hp -= Math.round(dmg * ((W.diff && W.diff.dmg) || 1));
  sfx('crash', { vol: 0.8 }); sfx('skid', { vol: 0.6 }); shake(5);
  word(what === 'skid' ? 'w_sploosh' : what === 'junk' ? 'w_clang' : 'w_crash', r.x + 6, r.y, r.z + 14);
  addFx({ type: 'dust', x: r.x - 10, y: r.y, z: 0, dur: 0.35 });
  if (h.hp <= 0) {
    h.lives--;
    if (h.lives > 0) { h.hp = h.maxHp; r.inv = 2.6; floatText('BACK IN THE SEAT!', r.x, r.y, 70, '#8ae87a'); sfx('powerup', { vol: 0.5 }); }
    else { h.hp = 0; h.set('out'); h.alive = false; h.continueT = SC.game && SC.game.continuesLeft() > 0 ? 10 : 0; floatText(['OUCH!', 'MY BACK!', 'NOT TODAY!'][Math.floor(W.rnd() * 3)], r.x, r.y, 64, '#ff8ac0'); }
  } else line(h, 'crash');
  return true;
}
export function continueRider(h) {  // a KO'd nurse spends a continue: back on a scooter, blinking
  const r = h.sc || (h.sc = { x: 0, y: MID, z: 0, vz: 0, inv: 0, crash: 0, cd: 0, fire: 0, spin: 0, col: h.slot ? 'blue' : 'red', bx: 84 - h.slot * 14 });
  h.lives = 3; h.alive = true; h.hp = h.maxHp; h.set('idle'); h.meter = 50; r.x = -30; r.z = 0; r.vz = 0; r.inv = 2.6; r.crash = 0;
}

// ---------------------------------------------------------------- update
export function updateScooter(dt, inputs) {
  SC.t += dt; W.t += dt; W.stats.time += dt; W.clock += dt / 1.5;
  const VW = G.VW, act = riders();
  // scroll speed: everyone's RIGHT / LEFT nudges it (+-25%)
  let mx = 0; for (const h of act) mx += (inputs.get(h) || {}).mx || 0;
  mx = act.length ? mx / act.length : 0;
  const want = SC.phase === 'intro' ? SCOOT.base * 0.6 : SC.phase === 'finish' ? SCOOT.base * 1.4 : SCOOT.base * (1 + 0.25 * mx);
  SC.speed += (want - SC.speed) * Math.min(1, dt * 3);
  SC.d += SC.speed * dt;
  // riders
  for (const h of W.heroes) {
    const r = h.sc; if (!r || h.st === 'out') continue;
    const I = inputs.get(h) || { mx: 0, my: 0, held: {}, prs: {} };
    r.inv = Math.max(0, r.inv - dt); r.crash = Math.max(0, r.crash - dt); r.cd -= dt; r.fire = Math.max(0, r.fire - dt);
    if (SC.phase === 'intro') { r.x += (r.bx - r.x) * Math.min(1, dt * 1.6); syncHero(h); continue; }
    const tx = SC.phase === 'finish' ? VW + 80 : r.bx + (I.mx || 0) * 46;
    r.x += Math.max(-90 * dt, Math.min(90 * dt, (tx - r.x) * dt * 3));
    if (SC.phase !== 'finish') r.x = Math.max(18, Math.min(VW * 0.56, r.x));
    if (r.crash <= 0) r.y = Math.max(YT, Math.min(YB, r.y + (I.my || 0) * SCOOT.steer * dt));
    if (I.prs.jmp && r.z <= 0 && r.crash <= 0) { r.vz = SCOOT.jumpV; sfx('jump', { vol: 0.6 }); addFx({ type: 'dust', x: r.x - 12, y: r.y, z: 0, dur: 0.3 }); }
    if (r.z > 0 || r.vz > 0) { r.vz -= SCOOT.grav * dt; r.z += r.vz * dt; if (r.z <= 0) { r.z = 0; r.vz = 0; sfx('thunk', { vol: 0.5 }); addFx({ type: 'dust', x: r.x - 8, y: r.y, z: 0, dur: 0.3 }); } }
    const fire = I.prs.atk || (I.held.atk && r.cd < SCOOT.cd - SCOOT.hold);
    if (fire && r.cd <= 0 && r.crash <= 0 && SC.phase !== 'finish' && SC.shots.filter((s) => s.h === h).length < 4) {
      r.cd = SCOOT.cd; r.fire = 0.16; SC.shots.push({ h, x: r.x + 20, y: r.y, z: r.z + 24, t: 0 }); sfx('pew', { vol: 0.55 });
    }
    if (W.t % 0.25 < dt && r.z === 0) addFx({ type: 'speed', x: r.x - 30 - W.rnd() * 10, y: r.y - 2 - W.rnd() * 4, z: 4 + W.rnd() * 10, dur: 0.25 });
    syncHero(h);
  }
  // tips
  // v0.10: a rider's speech bubble (Nate / Heather) sits where the tip banner goes, so tips wait (and pause) while someone is talking
  SC.talk = W.heroes.some((h) => h.sc && h.st !== 'out' && h.sayS && W.t < h.sayUntil);
  if (!SC.talk) while (SC.tips.length && SC.d + VW * 0.5 > SC.tips[0][0]) { SC.tip = { s: SC.tips.shift()[1], t: 0 }; }
  if (SC.tip && !SC.talk && (SC.tip.t += dt) > 2.8) SC.tip = null;
  // hallway things
  for (const o of SC.ob) {
    const sx = o.x - SC.d; if (sx > VW + 140) continue;
    o.t += dt;
    if (o.k === 'foe') updateFoe(o, sx, dt, act);
    else if (o.k === 'chair') { o.x += o.vx * dt; o.y += o.vy * dt; }
    if (o.gone || o.st === 'fly' || o.st === 'sleep' || o.k === 'chair') continue;
    for (const h of act) {
      const r = h.sc; if (!r || r.crash > 0.3) continue;
      if (Math.abs(sx - r.x) > o.w + 12 || Math.abs(o.y - r.y) > o.dep + 5) continue;
      if (o.pickup) { if (r.z < 30) collect(h, o); continue; }
      if (o.jump && r.z > o.h * 0.7) continue;
      if (o.k === 'foe' && r.z > 34) continue;
      if (r.inv > 0) continue;
      if (crash(h, o.skid ? SCOOT.dmg * 0.6 : o.k === 'foe' ? SCOOT.dmg : SCOOT.dmg * (o.jump ? 0.8 : 1), o.skid ? 'skid' : o.jump ? 'junk' : 'hit')) {
        if (o.k === 'foe') knock(o, null);
        else if (o.jump && !o.skid) { o.gone = true; for (let i = 0; i < 3; i++) addFx({ type: 'chunk', x: sx, y: o.y, z: 6, vx: 60 + W.rnd() * 80, vy: (W.rnd() - 0.5) * 60, vz: 140 + W.rnd() * 80, spin: 8, col: '#8a94a4', sz: 3, dur: 1.0 }); }
      }
    }
  }
  SC.ob = SC.ob.filter((o) => !o.gone && o.x - SC.d > -120);
  // syringes
  for (const s of SC.shots) {
    s.t += dt; s.x += SCOOT.shotV * dt;
    for (const o of SC.ob) {
      const sx = o.x - SC.d;
      if (o.gone || Math.abs(sx - s.x) > o.w + 6 || Math.abs(o.y - s.y) > (o.k === 'foe' ? 10 : o.dep + 2)) continue;
      if (o.k === 'foe' && o.st === 'go') { s.gone = true; o.hp--; o.flash = 0.1; sfx('hit2', { vol: 0.6 }); addFx({ type: 'spark', x: s.x, y: s.y, z: s.z, dur: 0.18 }); if (o.hp <= 0) knock(o, s.h); break; }
      if (o.stop && s.z < o.h) { s.gone = true; sfx('clang', { vol: 0.35 }); addFx({ type: 'spark', x: s.x, y: s.y, z: s.z, dur: 0.18 }); break; }
    }
    const b = SC.boss;
    if (!s.gone && b && b.st === 'fight' && Math.abs(s.y - b.y) < 13 && s.x > b.x - 30 && s.x < b.x + 46) { s.gone = true; hitBoss(s); }
  }
  SC.shots = SC.shots.filter((s) => !s.gone && s.x < VW + 20);
  // thrown things (lobs from patients and Marv)
  for (const p of SC.pr) {
    p.t += dt; p.x += p.vx * dt; p.y += p.vy * dt; p.vz -= 420 * dt; p.z += p.vz * dt;
    const sx = p.x - SC.d;
    for (const h of act) { const r = h.sc; if (p.z < 30 && Math.abs(sx - r.x) < 12 && Math.abs(p.y - r.y) < 9 && Math.abs(p.z - (r.z + 14)) < 20 && crash(h, SCOOT.dmg * 0.8, 'hit', 6)) { p.gone = true; } }
    if (p.z <= 0 && !p.gone) { p.gone = true; addFx({ type: 'splash', x: sx, y: p.y, z: 0, dur: 0.3 }); sfx('splat', { vol: 0.4 }); }
  }
  SC.pr = SC.pr.filter((p) => !p.gone);
  // phases
  if (SC.phase === 'intro' && SC.t > 2.4) { SC.phase = 'ride'; SC.t = 0; sfx('scoot'); word('w_go', VW / 2, 150, 40); for (const h of act) { line(h, 'start'); if (!h.d.scoot) floatText(pick(["LET'S ROLL!", 'BEEP BEEP!', 'WHEEE!', 'AFTER HIM!']), h.sc.x, h.sc.y, 64, '#ffffff'); } }
  if (SC.phase === 'ride' && SC.d > SCOOT.len && !SC.ob.some((o) => o.k === 'foe' && o.st === 'go' && o.x - SC.d < VW)) startBoss();
  if (SC.boss) updateBoss(dt, act);
  if (SC.phase === 'finish') { SC.endT += dt; if (SC.endT > 3.2) { SC.phase = 'off'; SC.done = true; } }
  updateWorld(dt);
  return SC.done;
}
function collect(h, o) {
  const it = ITEMS[o.item]; o.gone = true; h.scSnack++;
  if (it.heal) h.hp = Math.min(h.maxHp, h.hp + it.heal);
  if (it.life) h.lives++;
  h.score += it.score || 100;
  floatText(it.msg || 'SNACK!', h.sc.x, h.sc.y, 56, it.life ? '#8ad8ff' : '#8ae87a'); sfx(it.sfx || (it.life ? 'powerup' : 'coin'), { vol: 0.6 });
  if (it.heal) line(h, 'snack');
}
function knock(o, by) {  // a sedated (or bowled-over) patient tumbles to the side of the hall and naps there
  if (o.st !== 'go') return;
  o.st = 'fly'; o.t = 0; o.vz = 150; o.ty = o.y < MID ? YT - 10 : YB + 6; o.vy0 = o.y;
  if (by) { line(by, 'hit'); by.score += o.d.score; by.scKO++; SC.sedated++; floatText(pick(SLEEP), o.x - SC.d, o.y, 60, '#c8a0ff'); sfx('coin', { vol: 0.45 }); }
  else sfx('punch1', { vol: 0.6 });
  if (o.foe === 'wheel') { SC.ob.push({ k: 'chair', x: o.x, y: o.y, vx: -40, vy: o.y < MID ? -30 : 30, t: 0, w: 0, dep: 0 }); }
}
function updateFoe(o, sx, dt, act) {
  if (o.flash) o.flash = Math.max(0, o.flash - dt);
  if (o.st === 'fly') {
    o.vz -= 520 * dt; o.z = Math.max(0, o.z + o.vz * dt); o.x += 70 * dt; o.y += (o.ty - o.y) * Math.min(1, dt * 4);
    if (o.z <= 0 && o.t > 0.2) { o.st = 'sleep'; o.t = 0; addFx({ type: 'dust', x: sx, y: o.y, z: 0, dur: 0.3 }); }
    return;
  }
  if (o.st === 'sleep') { if (Math.floor(o.t * 1.2) !== Math.floor((o.t - dt) * 1.2)) addFx({ type: 'zzz', x: sx + 4, y: o.y, z: 18, dur: 1.0 }); return; }
  if (!o.said && sx < G.VW - 20) { o.said = true; if (W.rnd() < 0.6) floatText(pick(o.d.lines), sx, o.y, 62, '#ffffff'); if (o.foe === 'wheel') sfx('honk', { vol: 0.4, rate: 1.3 }); }
  o.x += o.vx * dt;
  if (o.foe === 'wander') o.y = Math.max(YT, Math.min(YB, o.y + Math.sin(o.t * 1.4 + o.ph) * 26 * dt));
  if (o.foe === 'charge' && act.length && sx < G.VW) { const r = act[0].sc; o.y += Math.sign(r.y - o.y) * Math.min(Math.abs(r.y - o.y), 18 * dt); }
  if (o.foe === 'thrower' && sx < G.VW - 10 && sx > G.VW * 0.35 && act.length) {
    o.cd -= dt;
    if (o.cd <= 0) { o.cd = rr(1.3, 2.0); o.lobT = 0.35; lob(o.x - 8, o.y, 40, pick(act).sc, pick(['p_jello', 'p_cup', 'p_tray'])); }
  }
  if (o.lobT) o.lobT = Math.max(0, o.lobT - dt);
}
function lob(wx, y, z, r, s, T = 0.9) {  // arc a thrown thing to land where rider r will be in T seconds
  const tx = SC.d + SC.speed * T + r.x, ty = r.y;
  SC.pr.push({ x: wx, y, z, vx: (tx - wx) / T, vy: (ty - y) / T, vz: (0.5 * 420 * T * T - z) / T, spr: s, t: 0 });
  sfx('fling', { vol: 0.4 });
}

// ---------------------------------------------------------------- Motorcart Marv
function startBoss() {
  SC.phase = 'boss'; SC.tip = { s: 'HONK HONK! MARV IS BEHIND YOU!', t: 0 };
  const hp = W.heroes.length > 1 ? SCOOT.bossHp2 : SCOOT.bossHp;
  SC.boss = { x: -110, y: MID, ty: MID, z: 0, st: 'enter', t: 0, hp, maxHp: hp, act: 'weave', actT: 0, n: 0, hurt: 0, phase: 1, k: 0, fightT: 0 };
  W.boss = { name: 'MOTORCART MARV', hp, maxHp: hp, shown: 1, phase: 1, st: 'enter', t: 0, p2label: 'NITRO!', drawIcon: (x, y) => { const c = G.ctx; c.save(); c.beginPath(); c.rect(x, y, 24, 22); c.clip(); frame('marv', anim('marv', 'drive').s, x + 12, y + 74); c.restore(); },
    hint: () => (SC.boss && SC.boss.act === 'ram' && SC.boss.actT < 0.8 ? 'HE\'S BACKING UP! DODGE!' : null) };
  sfx('honk'); sfx('marv', { vol: 0.8 });
}
const ACTS = ['weave', 'throw', 'weave', 'drop', 'ram'];
function updateBoss(dt, act) {
  const b = SC.boss, VW = G.VW, home = VW - 98, sp = b.phase === 2 ? 1.3 : 1;
  b.t += dt; b.hurt = Math.max(0, b.hurt - dt); W.boss.t = b.t; W.boss.st = b.st; W.boss.hp = b.hp; W.boss.phase = b.phase;
  if (b.st === 'enter') {
    b.x += (b.t < 1.2 ? 330 : 120) * dt; b.y += (MID - b.y) * dt * 2;
    if (b.t > 0.3 && b.t < 0.32) floatText('EAT MY EXHAUST, NURSES!', Math.max(80, b.x), b.y, 84, '#ffe84a');
    if (b.x >= home) { b.x = home; b.st = 'fight'; b.t = 0; b.act = 'weave'; b.actT = 0; W.boss.shown = 1; }
    return;
  }
  if (b.st === 'dead') {
    b.x -= 70 * dt; b.y += (MID - b.y) * dt;
    if (W.t % 0.2 < dt) addFx({ type: 'smoke', x: b.x - 30, y: b.y, z: 22, dur: 0.6 });
    return;
  }
  b.fightT += dt; b.actT += dt;
  if (b.fightT > SCOOT.bossMax) return defeatBoss(true);
  const tgt = act.length ? act[Math.floor(b.fightT / 4) % act.length].sc : null;
  if (b.act === 'weave') {
    if (b.actT % 0.9 < dt) b.ty = tgt && W.rnd() < 0.5 ? tgt.y : lane();
    b.y += Math.sign(b.ty - b.y) * Math.min(Math.abs(b.ty - b.y), 70 * sp * dt); b.x += (home - b.x) * dt * 2;
    if (b.actT > 2.2 / sp) nextAct(b);
  } else if (b.act === 'throw') {
    if (tgt && b.actT > 0.3 && Math.floor(b.actT / (0.62 / sp)) > b.k) { b.k++; b.throwT = 0.3; lob(SC.d + b.x - 4, b.y, 56, tgt, pick(['w_bedpan', 'urinal']), 0.8); }
    if (b.actT > 2.1) nextAct(b);
  } else if (b.act === 'drop') {
    b.y += Math.sin(b.actT * 3) * 50 * dt;
    b.y = Math.max(YT, Math.min(YB, b.y));
    if (b.actT > 0.2 && Math.floor(b.actT / (0.48 / sp)) > b.k) { b.k++; addOb(b.k % 2 ? 'spill' : 'can', SC.d + b.x - 44, b.y); sfx('clunk', { vol: 0.4 }); }
    if (b.actT > 2.0) nextAct(b);
  } else if (b.act === 'ram') {  // the comedy move: BEEP BEEP BEEP, he reverses straight back at you
    if (b.actT < 0.05 && tgt) { b.ty = tgt.y; sfx('beepbeep', { vol: 0.7 }); }
    if (b.actT < 0.8) { b.y += Math.sign(b.ty - b.y) * Math.min(Math.abs(b.ty - b.y), 90 * dt); if (b.actT % 0.42 < dt) sfx('beepbeep', { vol: 0.6 }); }
    else if (b.actT < 0.8 + 1.1 / sp) { b.x = Math.max(36, b.x - 300 * sp * dt); }
    else { b.x += (home - b.x) * dt * 2.2; if (b.x > home - 6) nextAct(b); }
  }
  // contact with riders
  for (const h of act) {
    const r = h.sc;
    if (Math.abs(r.y - b.y) < 12 && r.x > b.x - 40 && r.x < b.x + 50 && r.z < 40) crash(h, SCOOT.dmg, 'hit', 26);
  }
  if (b.phase === 2 && W.t % 0.12 < dt) addFx({ type: 'spark', kind: 'bigspark', x: b.x - 36, y: b.y, z: 8, dur: 0.18 });
}
function nextAct(b) { b.n++; b.act = ACTS[b.n % ACTS.length]; b.actT = 0; b.k = 0; if (b.act === 'weave' && W.rnd() < 0.4) floatText(pick(['VROOOM!', 'TOO SLOW!', 'CATCH ME IF YOU CAN!', 'BEEP BEEP, NURSES!']), b.x, b.y, 84, '#ffe84a'); }
function hitBoss(s) {
  const b = SC.boss; b.hp--; b.hurt = 0.12; s.h.score += 50;
  sfx('hit2', { vol: 0.7 }); addFx({ type: 'spark', x: s.x, y: s.y, z: s.z, dur: 0.18 });
  if (b.phase === 1 && b.hp <= b.maxHp / 2) { b.phase = 2; floatText('NITRO BOOST!', b.x, b.y, 90, '#8ad8ff'); sfx('charge'); }
  if (b.hp <= 0) defeatBoss(false);
}
function defeatBoss(timeout) {
  const b = SC.boss; b.st = 'dead'; b.t = 0; b.hp = 0; W.boss.hp = 0; W.boss.st = 'defeat';
  SC.bossBeat = !timeout; SC.phase = 'finish'; SC.endT = 0; SC.tip = null;
  word('w_ko', b.x, b.y, 50); sfx('explosion', { vol: 0.6 }); sfx('marv_ko', { vol: 0.8 }); shake(8);
  floatText(timeout ? 'OUT OF BATTERY! ...zzz' : 'TUCKED IN! ...zzz', b.x, b.y, 96, '#c8a0ff');
  if (!timeout) for (const h of riders()) { h.score += 5000; floatText('+5000', h.sc.x, h.sc.y, 70, '#ffe84a'); }
  SC.pr = [];
}

// test hook: drop a hazard / patient / pickup dx px ahead of rider `who` (k = a KIND, a FOE, or an ITEMS key)
export function scootSpawn(k, dx = 80, dy = 0, who = 0) {
  const h = W.heroes[who], r = h && h.sc; if (!r) return false;
  const x = SC.d + r.x + dx, y = Math.max(YT - 2, Math.min(YB + 2, r.y + dy));
  SC.last = FOE[k] ? addFoe(k, x, y) : KIND[k] ? addOb(k, x, y) : ITEMS[k] ? addItem(k, x, y) : null;
  return !!SC.last;
}

// ---------------------------------------------------------------- bot (tests): dodge, hop, shoot
export function scootBot(h) {
  const o = { mx: 0, my: 0, held: {}, prs: {}, run: false }, r = h.sc; if (!r) return o;
  let threat = null, best = 1e9;
  for (const q of SC.ob) {
    if (q.gone || q.pickup || q.k === 'chair' || (q.k === 'foe' && q.st !== 'go')) continue;
    const dx = q.x - SC.d - r.x; if (dx < -10 || dx > 150) continue;
    if (Math.abs(q.y - r.y) < q.dep + 14 && dx < best) { best = dx; threat = q; }
  }
  const b = SC.boss;
  if (threat) {
    if (threat.jump) { if (best < 44) o.prs.jmp = true; }
    else { const up = threat.y - (threat.dep + 18), dn = threat.y + threat.dep + 18; o.my = (up < YT ? 1 : dn > YB ? -1 : r.y < threat.y ? -1 : 1); }
    if (threat.k === 'foe') o.prs.atk = (W.t * 60 | 0) % 8 === 0;
  } else if (b && b.st === 'fight') {
    const ram = b.act === 'ram' && Math.abs(b.y - r.y) < 26;
    const ty = ram ? (b.y > MID ? YT + 4 : YB - 4) : b.y;
    o.my = Math.abs(ty - r.y) > 3 ? Math.sign(ty - r.y) : 0; o.prs.atk = (W.t * 60 | 0) % 8 === 0;
  } else {
    const f = SC.ob.find((q) => q.k === 'foe' && q.st === 'go' && q.x - SC.d > r.x + 40 && q.x - SC.d < G.VW);
    if (f) { o.my = Math.abs(f.y - r.y) > 4 ? Math.sign(f.y - r.y) * 0.7 : 0; o.prs.atk = (W.t * 60 | 0) % 8 === 0; }
    else o.my = Math.abs(MID - r.y) > 6 ? Math.sign(MID - r.y) * 0.5 : 0;
  }
  return o;
}

// ---------------------------------------------------------------- drawing
function strip(img, off, sy, h, dy) {  // blit a horizontal band of the looping hallway, wrapped
  const w = img.width; let x = ((Math.round(off) % w) + w) % w, dx = 0;
  while (dx < G.VW) { const n = Math.min(w - x, G.VW - dx); G.ctx.drawImage(img, x, sy, n, h, dx, dy + sy, n, h); dx += n; x = 0; }
}
function drawHall() {
  const img = W.scootBg, oy = offY();
  if (oy) rect(0, 0, G.VW, oy, '#d8d8cc');
  strip(img, SC.d * 0.72, 0, FLOOR_Y, oy);              // far: ceiling + wall + doors + windows (slower = parallax)
  strip(img, SC.d, FLOOR_Y, 224 - FLOOR_Y, oy);          // the floor, at full speed
  rect(0, FLOOR_Y + oy, G.VW, 4, '#1e283c', 0.25);
  // floor seams whipping past for speed
  for (let i = 0; i < 6; i++) { const x = ((i * 97 - SC.d * 1.0) % (G.VW + 60) + G.VW + 60) % (G.VW + 60) - 30; rect(x, FLOOR_Y + oy + 14 + i * 15, 18 + i * 3, 1, '#ffffff', 0.18); }
  // dusk glow pools under the ceiling lights (they ride with the wall)
  for (let i = 0; i < 6; i++) { const x = ((i * 96 + 48 - SC.d * 0.72) % 576 + 576) % 576 - 40; ellipse(x, FLOOR_Y + oy + 10, 34, 6, '#ffd8a0', 0.12); }
}
function drawFront() {  // near: support posts in front of the action, sweeping past faster than everything else
  const oy = offY(), P = 300, VH = G.VH;
  for (let i = 0; i < 3; i++) {
    const x = Math.round(((i * P - SC.d * 1.45) % (P * 3) + P * 3) % (P * 3) - 20); if (x > G.VW + 10) continue;
    rect(x, oy + 132, 9, VH - oy - 132, '#0e1220', 0.62); rect(x + 1, oy + 132, 1, VH - oy - 132, '#8a94b4', 0.35);
    rect(x - 2, oy + 128, 13, 5, '#0e1220', 0.7);
  }
}
function drawRider(h) {
  const r = h.sc, X = Math.round(r.x), G0 = Math.round(r.y + offY());
  ellipse(X, G0, Math.max(10, 20 - r.z * 0.2), 4, '#000', 0.3);
  if (r.inv > 0 && r.crash <= 0 && Math.floor(W.t * 16) % 2) return;
  const flip = r.crash > 0 && Math.floor(r.crash * 18) % 2 === 1, Y = G0 - Math.round(r.z) + (r.z === 0 && Math.floor(W.t * 10) % 2 ? 1 : 0);
  const wheel = Math.floor(W.t * 14) % 2;
  spr(`scoot_${r.col}${wheel}`, X, Y, { ax: 22, ay: 43, flip });
  const a = r.crash > 0 ? 'scooth' : r.fire > 0 ? 'scootf' : 'scoot', A = anim(h.id, a);
  if (A) frame(h.id, A.s + (Math.floor(W.t * 4) % A.n), X + (flip ? 4 : -4), Y - 4, { flip });
}
function drawFoe(o, sx) {
  const G0 = Math.round(o.y + offY()), X = Math.round(sx);
  if (o.st === 'go') ellipse(X, G0, 12, 3, '#000', 0.3);
  const Y = G0 - Math.round(o.z || 0);
  if (o.st === 'sleep' || o.st === 'fly') { const A = anim(o.sheet, o.st === 'fly' ? 'fall' : 'sleep'); if (A) frame(o.sheet, A.s, X, Y, { flip: true }); return; }
  if (o.foe === 'wheel') { spr('wheelchair', X, G0, { ax: 15, ay: 29, flip: true }); const A = anim(o.sheet, 'wheel'); frame(o.sheet, A.s + (Math.floor(W.t * 6) % A.n), X + 2, G0 - 3, { flip: true, white: o.flash > 0 }); return; }
  let an = o.d.an; if (o.foe === 'thrower' && o.lobT > 0) an = 'lob';
  const A = anim(o.sheet, an) || anim(o.sheet, 'idle');
  frame(o.sheet, A.s + (Math.floor(W.t * (o.d.rate || 7)) % A.n), X, Y, { flip: true, white: o.flash > 0 });
}
function drawBoss(b) {
  const X = Math.round(b.x), G0 = Math.round(b.y + offY());
  ellipse(X + 6, G0, 40, 6, '#000', 0.3);
  const dead = b.st === 'dead', i = dead ? 2 : Math.floor(W.t * 14) % 2;
  if (b.act === 'ram' && b.actT < 0.8 && b.st === 'fight' && Math.floor(W.t * 8) % 2) text('BEEP BEEP!', X, G0 - 92, { col: '#ff5a3a', align: 'center' });
  spr(`marvcart${i}`, X, G0, { ax: 34, ay: 49 });
  const an = dead ? 'sleep' : b.hurt > 0 ? 'hurt' : b.throwT > 0 ? 'throw' : b.act === 'weave' && b.actT > 1.4 ? 'taunt' : 'drive', A = anim('marv', an);
  frame('marv', A.s + (Math.floor(W.t * 5) % A.n), X - 1, G0 - 8, { white: b.hurt > 0.06 });
  if (b.throwT) b.throwT = Math.max(0, b.throwT - 1 / 60);
  if (dead && Math.floor(b.t * 1.5) !== Math.floor((b.t - 1 / 60) * 1.5)) addFx({ type: 'zzz', x: X, y: b.y, z: 70, dur: 1.0 });
}
export function drawScooter() {
  const c = G.ctx, sx0 = W.shakeAmt > 0 ? Math.round((Math.random() - 0.5) * W.shakeAmt) : 0, sy0 = W.shakeAmt > 0 ? Math.round((Math.random() - 0.5) * W.shakeAmt) : 0;
  c.save(); c.translate(sx0, sy0);
  drawHall();
  const list = [], oy = offY();
  for (const o of SC.ob) {
    const sx = o.x - SC.d; if (sx < -80 || sx > G.VW + 80) continue;
    if (o.k === 'foe') list.push({ y: o.y, d: () => drawFoe(o, sx) });
    else if (o.k === 'chair') list.push({ y: o.y, d: () => spr('wheelchair', sx, o.y + oy, { ax: 15, ay: 29, flip: Math.floor(o.t * 8) % 2 === 0 }) });
    else if (o.k === 'item') list.push({ y: o.y, d: () => { const it = ITEMS[o.item], [w, h] = sprSize(it.spr); ellipse(sx, o.y + oy, 7, 2, '#000', 0.3); spr(it.spr, sx, o.y + oy - 8 - Math.round(Math.sin(W.t * 5 + o.x) * 2), { ax: w / 2, ay: h }); } });
    else list.push({ y: o.skid ? o.y - 20 : o.y, d: () => { if (!o.skid) ellipse(sx, o.y + oy, o.w + 2, 3, '#000', 0.25); spr(o.spr, sx, o.y + oy, { ax: o.ax, ay: o.ay }); } });
  }
  for (const h of W.heroes) if (h.sc && h.st !== 'out') list.push({ y: h.sc.y + 0.5, d: () => drawRider(h) });
  if (SC.boss) list.push({ y: SC.boss.y, d: () => drawBoss(SC.boss) });
  for (const p of SC.pr) list.push({ y: p.y, d: () => { const sx = p.x - SC.d; ellipse(sx, p.y + oy, 4, 1.5, '#000', 0.3); const [w, h] = sprSize(p.spr); spr(p.spr, sx, p.y + oy - p.z, { ax: w / 2, ay: h / 2, rot: Math.round(p.t * 10) * (Math.PI / 2) }); } });
  for (const s of SC.shots) list.push({ y: s.y, d: () => { ellipse(s.x, s.y + oy, 5, 1.5, '#000', 0.2); spr('ativan', s.x, s.y + oy - s.z, { ax: 11, ay: 4 }); rect(s.x - 18, s.y + oy - s.z, 8, 1, '#c8a0ff', 0.6); } });
  list.sort((a, b) => a.y - b.y);
  for (const o of list) o.d();
  for (const f of W.fx) drawFx(f);
  drawFront();
  for (const h of W.heroes) if (h.sc && h.st !== 'out') h.drawSay();
  c.restore();
  rect(0, 0, G.VW, G.VH, '#ff7a3a', 0.05);  // dusk
}
export function drawScooterHUD() {
  const VW = G.VW;
  if (SC.phase === 'intro') {
    const y = 84; rect(0, y - 8, VW, 52, '#0a1030', 0.78); rect(0, y - 8, VW, 1, '#ffe84a'); rect(0, y + 43, VW, 1, '#ffe84a');
    text('SCOOTER RUN!', VW / 2, y, { col: '#ffe84a', align: 'center', scale: 2 });
    text('CATCH MOTORCART MARV!', VW / 2, y + 20, { col: '#ffffff', align: 'center' });
    text('JUMP = HOP JUNK   ATTACK = ATIVAN', VW / 2, y + 31, { col: '#8ad8ff', align: 'center' });
    return;
  }
  if (SC.phase === 'ride') {  // progress strip: you -> Marv's checkered flag
    const w = 150, x = Math.round((VW - w) / 2), y = 40, k = Math.min(1, SC.d / SCOOT.len);
    rect(x - 1, y - 1, w + 2, 5, '#1a1020'); rect(x, y, w, 3, '#3a4c92'); rect(x, y, Math.round(w * k), 3, '#ffe84a');
    rect(x + Math.round(w * k) - 1, y - 3, 3, 9, '#ff5a3a');
    for (let i = 0; i < 3; i++) rect(x + w + 2 + i * 2, y - 3 + (i % 2) * 2, 2, 2, '#ffffff');
  }
  if (SC.tip && !SC.talk) { const s = SC.tip.s, a = SC.tip.t < 2.2 || Math.floor(SC.tip.t * 8) % 2; if (a) { const w = s.length * 8 + 12; panel((VW - w) / 2, 52, w, 15, '#1a2450', '#8ad8ff', 0.88); text(s, VW / 2, 56, { col: '#ffffff', align: 'center' }); } }
  if (SC.phase === 'finish' && SC.endT > 0.8) { const [w] = sprSize('w_clear'); spr('w_clear', VW / 2, 96, { ax: w / 2, scale: Math.min(1, (VW - 20) / w) }); }
}
export function scootRows(h) {
  const n = h.scKO || 0, s = h.scSnack || 0, c = h.scCrash || 0;
  const rows = [[`SEDATED x${n}`, n * 150], [`SNACKS x${s}`, s * 100], [c ? `CRASHES x${c}` : 'NO CRASHES!', c ? 0 : 3000], [SC.bossBeat ? 'MARV PARKED!' : 'MARV GOT AWAY', SC.bossBeat ? 2000 : 0]];
  return { rows, total: rows.reduce((a, r) => a + r[1], 0) };
}
export function drawScootTally(game) {
  const VW = G.VW, VH = G.VH;
  rect(0, 0, VW, VH, '#05060c', Math.min(0.6, game.t));
  text('SCOOTER RUN', VW / 2, 14, { col: '#ffe84a', align: 'center', scale: 2 });
  text(`PATIENTS SEDATED ${SC.sedated}   CRASHES ${SC.crashes}`, VW / 2, 38, { col: '#c8d4f0', align: 'center' });
  const T = game.stally || [], n = T.length || 1, pw = Math.min(210, (VW - 20) / n - 6);
  T.forEach((R, i) => {
    const x = Math.round(VW / 2 - (n * (pw + 6)) / 2 + i * (pw + 6)), y = 52;
    panel(x, y, pw, 128);
    spr(`face_${R.h.id}`, x + 4, y + 4); text(R.h.d.name, x + 44, y + 10, { col: R.h.slot ? '#8ad8ff' : '#ffe84a' });
    const reveal = Math.min(R.rows.length, Math.floor(game.t * 2));
    R.rows.forEach((r, j) => { if (j >= reveal) return; text(r[0], x + 6, y + 44 + j * 14, { col: r[1] && j >= 2 ? '#8ae87a' : '#c8d4f0' }); text(String(r[1]), x + pw - 6, y + 44 + j * 14, { col: '#ffffff', align: 'right' }); });
    if (reveal >= R.rows.length) text(`BONUS ${R.total}`, x + pw / 2, y + 108, { col: '#ffe84a', align: 'center' });
  });
  if (game.t > 3) text(Math.floor(game.t * 2) % 2 ? 'PRESS ATTACK' : '', VW / 2, VH - 30, { col: '#ffffff', align: 'center' });
}
