// The level: pre-rendered hospital hallway, wall features (doors and elevators that open), breakables, floor items,
// projectiles, effects, the camera and the zone / wave spawner.
import { G, spr, sprSize, rect, text, ellipse, ring, bolt, frame, textW } from './gfx.js';
import { Y_MIN, Y_MAX, LEVEL1, BREAKABLES, LOOT, ITEMS, WEAPONS, DIFF, GRAV } from './data.js';
import { sfx } from './sound.js';

export const W = {
  lv: null, bg: null, camX: 0, camMin: 0, camMax: 0, lockX: null, t: 0, stop: 0,
  heroes: [], enemies: [], boss: null, props: [], items: [], shots: [], fx: [], doors: {}, elevs: {},
  zone: -1, zoneOn: false, wave: 0, queue: [], go: 0, clock: 7 * 60, diff: DIFF.normal, cleared: false, stats: { kos: 0, time: 0 },
  shakeAmt: 0, shakeOn: true, flash: 0, flashCol: '#fff', rnd: Math.random,
};
const FLOOR_Y = 118, OFF = () => G.VH - 224;  // retro (240 lines) adds a strip of ceiling on top

// ---------------------------------------------------------------- background
const LAYER = {  // wall features: vertical placement by kind
  door: (w, h) => FLOOR_Y - h, elev: (w, h) => FLOOR_Y - 82, callpanel: () => 74, floornum3: () => 40, station: (w, h) => FLOOR_Y + 2 - h,
  chairs: (w, h) => FLOOR_Y + 4 - h, plant0: (w, h) => FLOOR_Y + 3 - h, plant1: (w, h) => FLOOR_Y + 3 - h, plant2: (w, h) => FLOOR_Y + 3 - h,
  gurney: (w, h) => FLOOR_Y + 3 - h, fountain: (w, h) => FLOOR_Y - 4 - h + 4, wheelchair: (w, h) => FLOOR_Y + 3 - h,
};
function wallY(kind, w, h) {
  if (LAYER[kind]) return LAYER[kind](w, h);
  if (kind.startsWith('window')) return 30;
  if (kind.startsWith('sign')) return 22;
  if (kind === 'poster_clock') return 26;
  if (kind === 'poster_tv') return 32;
  if (kind === 'poster_sanitizer' || kind === 'poster_alarm') return 52;
  return 38;  // posters
}

export function buildLevel(lv) {
  W.lv = lv; W.doors = {}; W.elevs = {};
  const c = document.createElement('canvas'); c.width = lv.width; c.height = 224;
  const x = c.getContext('2d'); x.imageSmoothingEnabled = false;
  const at = G.atlas.sprites.rects;
  const blit = (name, dx, dy) => { const r = at[name]; if (r) x.drawImage(G.img.sprites, r[0], r[1], r[2], r[3], Math.round(dx), Math.round(dy), r[2], r[3]); };
  // ceiling + wall
  for (let i = 0; i * 32 < lv.width; i++) {
    blit(i % 3 === 1 ? 'ceil_lit' : 'ceil', i * 32, 0);
    blit('wall' + ((i * 7) % 4), i * 32, 14);
  }
  // floor: two-tone linoleum rows, each row nudged sideways for a gentle perspective
  for (let r = 0; r < 9; r++) {
    const y = FLOOR_Y + r * 12, off = (r * 5) % 24;
    for (let i = -1; i * 24 < lv.width + 24; i++) blit('floor' + ((i + r) & 1), i * 24 - off, y);
  }
  // soft shadow along the baseboard + a polish shine stripe
  x.fillStyle = 'rgba(30,40,60,0.22)'; x.fillRect(0, FLOOR_Y, lv.width, 4);
  x.fillStyle = 'rgba(255,255,255,0.10)'; x.fillRect(0, FLOOR_Y + 40, lv.width, 2); x.fillRect(0, FLOOR_Y + 70, lv.width, 1);
  // dayroom: a different floor tint past the boss line
  x.fillStyle = 'rgba(160,120,220,0.12)'; x.fillRect(lv.bossArena - 40, FLOOR_Y, lv.width, 106);
  for (const [wx, kind, extra] of lv.wall) {
    if (kind === 'door') {  // door frame drawn live (it opens); room number plate drawn into the wall
      W.doors[extra] = { x: wx, open: 0, target: 0, t: 0, num: extra };
      x.fillStyle = '#2a5aa8'; x.fillRect(wx + 38, 64, 15, 9); x.fillStyle = '#1a1020'; x.strokeStyle = '#1a1020';
      continue;
    }
    if (kind === 'elev') { W.elevs[extra] = { x: wx, open: 0, target: 0, t: 0, light: 0 }; blit('elevator', wx, FLOOR_Y - 82); continue; }
    const [w, h] = sprSize(kind);
    blit(kind, wx, wallY(kind, w, h));
  }
  W.bg = c;
  // breakables + floor items
  W.props = lv.props.map(([px, py, kind, drops]) => makeProp(kind, px, py, drops)); W.zynnProps = 0;
  W.items = []; for (const [ix, iy, k] of lv.floorItems || []) dropItem(k, ix, iy, false);
}

function drawDoor(d) {
  const idx = d.open < 0.15 ? 0 : d.open < 0.45 ? 1 : d.open < 0.75 ? 2 : 3;
  spr('door' + idx, d.x - W.camX, FLOOR_Y - 68 + OFF());
  text(String(d.num), d.x + 39 - W.camX, 65 + OFF(), { col: '#ffffff', shadow: null, scale: 1 }) ;
}
function drawElev(e) {
  const c = G.ctx, X = Math.round(e.x - W.camX), Y = FLOOR_Y - 82 + OFF();
  const o = Math.round(e.open * 30);
  c.save(); c.beginPath(); c.rect(X + 8, Y + 14, 64, 68); c.clip();
  spr('elev_door', X + 8 - o, Y + 14); spr('elev_door', X + 40 + o, Y + 14);
  c.restore();
  // floor indicator light: "3" with a down/up arrow; flashes when the car arrives
  rect(X + 23, Y + 1, 34, 6, '#20222c');
  text('3', X + 36, Y, { col: e.light > 0 && Math.floor(W.t * 6) % 2 ? '#ffe84a' : '#ff5a3a', shadow: null });
}

export function drawBackground() {
  const c = G.ctx, cx = Math.round(W.camX);
  if (OFF()) { rect(0, 0, G.VW, OFF(), '#d8d8cc'); }
  c.drawImage(W.bg, cx, 0, G.VW, 224, 0, OFF(), G.VW, 224);
  for (const d of Object.values(W.doors)) if (d.x - cx > -40 && d.x - cx < G.VW + 4) drawDoor(d);
  for (const e of Object.values(W.elevs)) if (e.x - cx > -84 && e.x - cx < G.VW + 4) drawElev(e);
}

// ---------------------------------------------------------------- items, props, projectiles
export function dropItem(k, x, y, pop = true) {
  const weapon = k.startsWith('w:');
  const it = { k, weapon, w: weapon ? WEAPONS[k.slice(2)] : null, def: weapon ? null : ITEMS[k], x, y: Math.max(Y_MIN, Math.min(Y_MAX, y)), z: pop ? 18 : 0, vz: pop ? 120 : 0, vx: pop ? (W.rnd() - 0.5) * 60 : 0, t: 0, uses: null };
  if (weapon) it.uses = it.w.uses ?? null, it.ammo = it.w.ammo ?? null;
  W.items.push(it); return it;
}
// ---- v0.3 kickable / breakable props. Hits knock carts rolling (they plow patients over and bounce off the screen
// edges), light things scoot, everything breaks after a few hits into chunky debris and maybe a drop.
export function makeProp(kind, x, y, drops = []) {
  const def = BREAKABLES[kind];
  return { x, y, z: 0, vx: 0, vy: 0, vz: 0, kind, def, hp: def.hp, st: 0, drops: [...drops], shake: 0, flash: 0, hitSet: new Set(), kicker: null, rattle: 0 };
}
const SPEED = { roll: [180, 340], slide: [120, 240] };
const moving = (p) => Math.abs(p.vx) > 4 || Math.abs(p.vy) > 4;
// hit a prop: dmg decides how many "hp pips" it loses, dir/kb decide the shove. Returns true if something happened.
export function hitProp(p, dmg, { dir = 1, kb = 60, from = null, quiet = false } = {}) {
  if (p.st >= 2) return false;
  const d = p.def;
  p.hp -= dmg >= 18 ? 3 : dmg >= 10 ? 2 : 1; p.shake = 0.22; p.flash = 0.1;
  if (from && from.isHero) p.kicker = from; else if (from && from.kicker) p.kicker = from.kicker;
  burst(p, 2 + Math.floor(W.rnd() * 3), 0.5);
  if (p.hp <= 0) { smashProp(p); return true; }
  if (p.hp <= Math.ceil(d.hp / 2)) p.st = Math.min(1, (d.states || 3) - 2);
  if (!quiet) { sfx(d.hit || 'clang', { vol: 0.65 }); spark(p.x, p.y, 22, 'spark'); W.stop = Math.max(W.stop, 0.035); shake(2); }
  if (d.zap && W.rnd() < 0.5) addFx({ type: 'spark', kind: 'bluespark', x: p.x - 4, y: p.y, z: 34, dur: 0.2 });
  if (d.move && !quiet) {  // launch it
    // jabs just nudge it (so a combo can finish it off); kicks, finishers, dashes and throws send it flying
    const [lo, hi] = SPEED[d.move], hard = (kb || 0) >= 110;
    p.nudge = !hard;
    if (!hard) { p.vx = dir * 38 * (d.push || 1); p.vy = 0; }
    else {
      p.vx = dir * Math.max(lo, Math.min(hi, 90 + kb * 1.25)) * (d.push || 1); p.vy = (W.rnd() - 0.5) * 30; p.hitSet = new Set(); p.rattle = 0;
      if (d.move === 'slide') { p.vz = 50; p.z = Math.max(p.z, 0.5); }
      if (d.move === 'roll') sfx('rattle', { vol: 0.5, gap: 0.2 });
    }
  }
  return true;
}
export function smashProp(p) {
  const d = p.def;
  p.st = 2; p.hp = 0; p.vx *= 0.35; p.vy = 0; p.flash = 0.15;
  sfx(d.brk || 'smash', { vol: 0.9 }); if (d.zap) sfx('zap', { vol: 0.45, rate: 1.6 });
  W.stop = Math.max(W.stop, 0.07); shake(d.big ? 6 : 4);
  addFx({ type: 'dust', x: p.x, y: p.y + 1, z: 0, dur: 0.45 }); addFx({ type: 'spark', kind: 'bigspark', x: p.x, y: p.y, z: 20, dur: 0.22 });
  if (d.zap) for (let i = 0; i < 3; i++) addFx({ type: 'spark', kind: 'bluespark', x: p.x + (W.rnd() - 0.5) * 20, y: p.y, z: 16 + W.rnd() * 20, dur: 0.25 });
  burst(p, d.big ? 18 : 12, 1);
  word(d.big ? 'w_wham' : 'w_pow', p.x, p.y, 10);
  for (const k of p.drops) dropItem(k, p.x + (W.rnd() - 0.5) * 20, p.y + 6);
  const loot = rollLoot(d.loot);
  if (loot) dropItem(loot, p.x + (W.rnd() - 0.5) * 16, p.y + 4);
  const pts = d.big ? 500 : d.move === 'roll' ? 300 : 150;
  addScore(p.kicker, pts); floatText(String(pts), p.x, p.y, 40, '#ffe84a');
  W.stats.props = (W.stats.props || 0) + 1;
}
export function rollLoot(table) {
  const T = LOOT[table]; if (!T) return null;
  let r = W.rnd();
  for (const [k, pr] of T) {
    if (r < pr) { if (k === 'zynn' && (W.zynnProps || 0) >= 1) return 'energy'; if (k === 'zynn') W.zynnProps = (W.zynnProps || 0) + 1; return k; }
    r -= pr;
  }
  return null;
}
function burst(p, n, power) {  // chunky debris: a mix of the prop's own bits (drawers, gauze, shards) and colour chunks
  const d = p.def, bits = d.bits || [], cols = d.deb || ['#b8c0cc'];
  for (let i = 0; i < n; i++) {
    const useBit = bits.length && (i % 2 === 0);
    const dir = p.vx ? -Math.sign(p.vx) * (W.rnd() < 0.3 ? -1 : 1) : (W.rnd() < 0.5 ? -1 : 1);
    addFx({ type: 'chunk', spr: useBit ? bits[Math.floor(W.rnd() * bits.length)] : null, col: cols[Math.floor(W.rnd() * cols.length)],
      sz: 2 + Math.floor(W.rnd() * 3), x: p.x + (W.rnd() - 0.5) * d.w, y: p.y + (W.rnd() - 0.5) * 6, z: 8 + W.rnd() * (d.big ? 40 : 22),
      vx: dir * (30 + W.rnd() * 110) * power, vy: (W.rnd() - 0.5) * 50 * power, vz: (90 + W.rnd() * 150) * (0.5 + power * 0.5),
      spin: (W.rnd() - 0.5) * 18, dur: 1.4 + W.rnd() * 0.8 });
  }
}
export const breakProp = (p, dmg, from) => hitProp(p, dmg, { dir: from ? (Math.sign(p.x - from.x) || from.face || 1) : 1, kb: dmg * 8, from });
export function propBox(p) { return { x0: p.x - p.def.w / 2, x1: p.x + p.def.w / 2, y: p.y, z1: (p.def.h || (p.def.big ? 60 : 30)) + 10 }; }  // +10: jump kicks still connect
function updateProp(p, dt) {
  p.shake = Math.max(0, p.shake - dt); p.flash = Math.max(0, p.flash - dt);
  if (p.z > 0 || p.vz > 0) { p.vz -= GRAV * dt; p.z += p.vz * dt; if (p.z <= 0) { p.z = 0; p.vz = 0; } }
  if (!moving(p)) { p.vx = p.vy = 0; return; }
  const d = p.def, fr = p.st >= 2 ? 5 : (d.fr || 2) + (p.nudge ? 6 : 0);
  p.x += p.vx * dt; p.y += p.vy * dt;
  p.vx *= Math.exp(-fr * dt); p.vy *= Math.exp(-(fr + 3) * dt);
  if (Math.abs(p.vx) < 6) p.vx = 0; if (Math.abs(p.vy) < 4) p.vy = 0;
  // the floor's edges + the screen edges are walls: bounce back into play
  if (p.y < Y_MIN) { p.y = Y_MIN; p.vy = Math.abs(p.vy) * 0.5; } else if (p.y > Y_MAX) { p.y = Y_MAX; p.vy = -Math.abs(p.vy) * 0.5; }
  const L = W.camX + d.w / 2 + 2, R = W.camX + G.VW - d.w / 2 - 2;
  if (p.x > W.camX - 40 && p.x < W.camX + G.VW + 40) {
    if ((p.x < L && p.vx < 0) || (p.x > R && p.vx > 0)) {
      p.x = p.x < L ? L : R; p.vx = -p.vx * 0.55; p.hitSet = new Set(); shake(2);
      sfx(d.hit || 'clang', { vol: 0.5 }); addFx({ type: 'dust', x: p.x, y: p.y, z: 0, dur: 0.3 });
      if (Math.abs(p.vx) > 80) burst(p, 2, 0.4);
    }
  }
  if (p.st >= 2) return;
  const sp = Math.abs(p.vx);
  if (d.move === 'roll' && (p.rattle += dt) > 0.12 && sp > 60) { p.rattle = 0; addFx({ type: 'dust', x: p.x - Math.sign(p.vx) * d.w / 2, y: p.y, z: 0, dur: 0.25 }); }
  if (sp < 70) return;
  const dir = Math.sign(p.vx), k = Math.max(0.6, Math.min(1.3, 0.55 + sp / 400));
  // plow into patients (and Tilly): knock them down
  for (const e of [...W.enemies, ...(W.boss ? [W.boss] : [])]) {
    if (!e.alive || p.hitSet.has(e) || !e.hittable || !e.hittable() || e.z > 30) continue;
    if (Math.abs(e.y - p.y) > 12 + (e.big ? 6 : 0) || Math.abs(e.x - p.x) > d.w / 2 + e.w / 2) continue;
    p.hitSet.add(e);
    e.takeHit({ dmg: Math.round(d.dmg * k * (e.isBoss ? 0.6 : 1)), dir, kb: 170, stun: 0.5, down: true, from: p.kicker });
    e.propSet = new Set([p]);  // the patient it just bowled over can't bump it straight back
    spark(e.x, e.y, 26, 'bigspark'); sfx('heavy', { vol: 0.8 }); shake(3); W.stop = Math.max(W.stop, 0.05);
    if (!p.wordT || W.t > p.wordT) { word('w_wham', e.x, e.y, 14); p.wordT = W.t + 0.5; }
    addScore(p.kicker, 150);
    const h = p.kicker; if (h && h.isHero) { h.combo = (h.combo || 0) + 1; h.comboT = 1.6; h.maxCombo = Math.max(h.maxCombo || 0, h.combo); h.meter = Math.min(100, (h.meter || 0) + 5); h.lastFoe = e; h.lastFoeT = W.t + 2.2; }
    p.vx *= d.mass >= 2 ? 0.82 : 0.55;
    if (d.mass < 1 && hitProp(p, 4, { dir, kb: 0, quiet: true }) && p.st >= 2) return;
  }
  // and into other props: shove (or bounce off the heavy ones) and damage both a little
  for (const q of W.props) {
    if (q === p || q.st >= 2 || p.hitSet.has(q)) continue;
    if (Math.abs(q.y - p.y) > 12 || Math.abs(q.x - p.x) > (d.w + q.def.w) / 2) continue;
    p.hitSet.add(q); q.hitSet.add(p);
    const v = p.vx, ratio = Math.min(1.2, (d.mass || 1) / (q.def.mass || 1));
    q.kicker = p.kicker;
    hitProp(q, 6, { dir, kb: 0, from: p.kicker });
    if (q.def.move && q.st < 2) { q.vx = v * 0.85 * ratio; q.vy = p.vy * 0.5; q.hitSet = new Set([p]); q.nudge = false; }
    const qm = q.def.mass || 1, pm = d.mass || 1;
    p.vx = q.def.move && qm < pm * 4 ? v * Math.max(0.3, 1 - 0.6 * qm / pm) : -v * 0.45;  // heavy carts plow through light stuff
    if (qm >= pm * 0.5) { const keep = p.vx; hitProp(p, 4, { dir: Math.sign(keep) || dir, kb: 0, quiet: true }); p.vx = keep; p.vz = 0; p.z = 0; }
    if (p.st >= 2) return;
  }
}
// something heavy (a falling / thrown patient, Tilly) slams into props in its path
export function bumpProps(a, dmg, dir, from, set, reach = 6) {
  for (const p of W.props) {
    if (p.st >= 2 || (set && set.has(p))) continue;
    const b = propBox(p);
    if (Math.abs(p.y - a.y) > 12 || a.x < b.x0 - reach || a.x > b.x1 + reach || (a.z || 0) > b.z1) continue;
    if (set) set.add(p);
    hitProp(p, dmg, { dir, kb: 160, from }); p.hitSet.add(a);
  }
}

export function addShot(s) { W.shots.push(Object.assign({ t: 0, z: 30, vz: 0, hit: new Set(), life: 3 }, s)); }
export function addFx(f) { W.fx.push(Object.assign({ t: 0, z: 0 }, f)); return f; }
export function spark(x, y, z, kind = 'spark') { addFx({ type: 'spark', kind, x: x + (W.rnd() - 0.5) * 6, y, z, dur: 0.18 }); }
export function word(name, x, y, z) { addFx({ type: 'word', name, x, y, z: z + 30, dur: 0.6 }); }
export function floatText(s, x, y, z, col = '#ffe84a') { addFx({ type: 'txt', s, x, y, z, dur: 1.2, col }); }
export function shake(a) { if (W.shakeOn) W.shakeAmt = Math.max(W.shakeAmt, a); }
export function addScore(h, n) { if (h && h.isHero) h.score += Math.round(n); }

export function updateWorld(dt) {
  for (const d of Object.values(W.doors)) { d.open += Math.sign(d.target - d.open) * Math.min(Math.abs(d.target - d.open), dt * 3.2); if (d.target > 0 && (d.t += dt) > 2.4) d.target = 0; }
  for (const e of Object.values(W.elevs)) { e.open += Math.sign(e.target - e.open) * Math.min(Math.abs(e.target - e.open), dt * 1.8); e.light = Math.max(0, e.light - dt); if (e.target > 0 && (e.t += dt) > 3.4) e.target = 0; }
  for (const p of W.props) updateProp(p, dt);
  for (const it of W.items) {
    it.t += dt;
    if (it.z > 0 || it.vz > 0) { it.vz -= GRAV * dt; it.z += it.vz * dt; it.x += it.vx * dt; if (it.z <= 0) { it.z = 0; if (it.vz < -60) { it.vz = -it.vz * 0.35; } else { it.vz = 0; it.vx = 0; } } }
  }
  W.items = W.items.filter((it) => !it.gone && it.t < 40);
  for (const f of W.fx) {
    f.t += dt;
    if (f.type === 'chunk') {  // debris: ballistic, bounces twice, skids, then blinks out
      f.vz -= GRAV * dt; f.x += f.vx * dt; f.y += f.vy * dt; f.z += f.vz * dt; f.rot = (f.rot || 0) + f.spin * dt;
      if (f.y < Y_MIN - 6) { f.y = Y_MIN - 6; f.vy = Math.abs(f.vy) * 0.4; } else if (f.y > Y_MAX + 6) { f.y = Y_MAX + 6; f.vy = -Math.abs(f.vy) * 0.4; }
      if (f.z <= 0) { f.z = 0; if (f.vz < -40) { f.vz = -f.vz * 0.38; f.vx *= 0.6; f.vy *= 0.6; f.spin *= 0.5; } else { f.vz = 0; f.vx *= Math.exp(-dt * 8); f.vy *= Math.exp(-dt * 8); f.spin = 0; } }
    }
  }
  W.fx = W.fx.filter((f) => f.t < f.dur);
  W.shakeAmt = Math.max(0, W.shakeAmt - dt * 18);
  W.flash = Math.max(0, W.flash - dt * 3);
}

// door / elevator spawn helpers
export function openDoor(num) { const d = W.doors[num]; if (d) { d.target = 1; d.t = 0; sfx('door', { vol: 0.5 }); } return d; }
export function openElev(id) { const e = W.elevs[id]; if (e) { if (e.target < 1) { e.light = 1.2; sfx('ding'); } e.target = 1; e.t = 0; } return e; }

// ---------------------------------------------------------------- drawing helpers for world-space things
export function drawProp(p) {
  const fast = moving(p) && p.st < 2 && p.def.move === 'roll';
  const X = Math.round(p.x - W.camX + (p.shake > 0 ? Math.sin(p.shake * 90) * 2 : 0)), Y = Math.round(p.y + OFF() - p.z - (fast && Math.floor(W.t * 30) % 2 ? 1 : 0));
  const name = p.def.spr + Math.min(p.st, (p.def.states || 3) - 1);
  const [w, h] = sprSize(name);
  ellipse(p.x - W.camX, p.y + OFF(), p.def.w / 2 + 3, 3, '#000', 0.25);
  spr(name, X - w / 2, Y - h + 2);
  if (p.flash > 0) spr(name, X - w / 2, Y - h + 2, { light: true, alpha: Math.min(0.8, p.flash * 8) });
}
export function drawItem(it) {
  const X = it.x - W.camX, Y = it.y + OFF();
  ellipse(X, Y, 6, 2, '#000', 0.3);
  const name = it.weapon ? it.w.spr : it.def.spr;
  const [w, h] = sprSize(name);
  const blink = it.t > 32 && Math.floor(it.t * 8) % 2;
  if (blink) return;
  const bob = !it.weapon && it.z === 0 ? Math.round(Math.sin(it.t * 4) * 1) : 0;
  spr(name, X - w / 2, Y - h - it.z + bob - (it.weapon ? 0 : 1), { rot: it.weapon && it.z === 0 && it.w.spr === 'w_extinguisher' ? Math.PI / 2 : 0, ax: 0, ay: 0 });
  if (!it.weapon && Math.floor(it.t * 3) % 4 === 0) rect(X + w / 2 - 2, Y - h - it.z + bob - 2, 1, 1, '#fff');
}
export function drawShot(s) {
  const X = s.x - W.camX, Y = s.y + OFF();
  if (s.kind !== 'puddle') ellipse(X, Y, 5, 2, '#000', 0.3);
  if (s.kind === 'puddle') { spr(s.spr || 'puddle', X - 14, Y - 4, { alpha: Math.min(1, s.life) }); return; }
  if (s.kind === 'shock') {  // Nick's crash-cart ring / Will's slam ring
    const r = s.r;
    ring(X, Y, r, r * 0.32, s.col || '#8ad8ff', 3, 0.85); ring(X, Y, r * 0.8, r * 0.26, '#ffffff', 1, 0.7);
    if (s.col !== '#ffe84a') for (let i = 0; i < 6; i++) { const a = i / 6 * Math.PI * 2 + W.t * 3; bolt(X, Y - 20, X + Math.cos(a) * r, Y + Math.sin(a) * r * 0.32, '#c8f0ff', (i + 1) * 977 + Math.floor(W.t * 20)); }
    return;
  }
  if (s.kind === 'spray') return;
  const name = s.spr; const [w, h] = sprSize(name);
  spr(name, X, Y - s.z, { ax: w / 2, ay: h / 2, rot: s.spin ? s.t * s.spin : 0, flip: s.vx < 0 });
}
export function drawFx(f) {
  const X = f.x - W.camX, Y = f.y + OFF() - f.z;
  const k = f.t / f.dur;
  if (f.type === 'chunk') {
    const left = f.dur - f.t; if (left < 0.35 && Math.floor(f.t * 20) % 2) return;
    const Yg = f.y + OFF();
    if (f.z > 1) ellipse(X, Yg, 2, 1, '#000', 0.25);
    if (f.spr) { const [w, h] = sprSize(f.spr); spr(f.spr, Math.round(X), Math.round(Y), { ax: w / 2, ay: h / 2, rot: Math.round((f.rot || 0) / (Math.PI / 2)) * (Math.PI / 2) }); }
    else { const s = f.sz, x0 = Math.round(X - s / 2), y0 = Math.round(Y - s / 2); rect(x0 - 1, y0 - 1, s + 2, s + 2, '#1a1020'); rect(x0, y0, s, s, f.col); }
    return;
  }
  if (f.type === 'spark') { const i = Math.min(2, Math.floor(k * 3)); spr((f.kind || 'spark') + i, X, Y, { ax: f.kind === 'bigspark' ? 14 : f.kind === 'bluespark' ? 10 : 8, ay: f.kind === 'bigspark' ? 14 : f.kind === 'bluespark' ? 10 : 8 }); }
  else if (f.type === 'dust') { const i = Math.min(3, Math.floor(k * 4)); spr('dust' + i, X, Y, { ax: 10, ay: 10 }); }
  else if (f.type === 'smoke') { const i = Math.min(2, Math.floor(k * 3)); spr('smoke' + i, X, Y - k * 10, { ax: 8, ay: 8 }); }
  else if (f.type === 'word') { const [w, h] = sprSize(f.name); const s = k < 0.15 ? 0.6 + k / 0.15 * 0.6 : k < 0.25 ? 1.2 - (k - 0.15) * 2 : 1; spr(f.name, X, Y - k * 6, { ax: w / 2, ay: h / 2, scale: s, alpha: k > 0.8 ? (1 - k) * 5 : 1 }); }
  else if (f.type === 'txt') text(f.s, Math.max(textW(f.s) / 2 + 2, Math.min(G.VW - textW(f.s) / 2 - 2, X)), Y - k * 16, { col: f.col, align: 'center', alpha: k > 0.75 ? (1 - k) * 4 : 1 });
  else if (f.type === 'zzz') spr('zzz', X, Y - k * 8, { alpha: 1 - k * 0.5 });
  else if (f.type === 'heart') spr('heart', X, Y - k * 14, { alpha: 1 - k });
  else if (f.type === 'splash') spr('splash' + Math.min(2, Math.floor(k * 3)), X, Y, { ax: 13, ay: 18 });
  else if (f.type === 'speed') rect(X, Y, 10, 1, '#fff', 1 - k);
}

// ---------------------------------------------------------------- camera
export function updateCamera(dt) {
  const hs = W.heroes.filter((h) => h.alive);
  if (!hs.length) return;
  const ax = hs.reduce((s, h) => s + h.x, 0) / hs.length;
  let target = ax - G.VW * 0.42;
  const maxX = W.lv.width - G.VW;
  let hi = W.camMax;
  if (W.lockX !== null) { target = W.lockX; hi = W.lockX; }
  target = Math.max(W.camMin, Math.min(hi, Math.min(maxX, target)));
  const sp = W.lockX !== null ? 220 : 400;
  W.camX += Math.sign(target - W.camX) * Math.min(Math.abs(target - W.camX), sp * dt);
  if (W.lockX === null) W.camMin = Math.max(W.camMin, W.camX);  // arcade rule: no scrolling back
}
export const offY = OFF;
export { FLOOR_Y };
