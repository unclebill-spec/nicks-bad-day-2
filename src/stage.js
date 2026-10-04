// Stage flow for a floor: zone triggers + camera locks, wave spawns from both screen edges, patient-room doors and the
// elevators, projectiles, the boss, and the end-of-floor sequence.
import { G } from './gfx.js';
import { Y_MIN, Y_MAX, VARIANTS } from './data.js';
import { W, openDoor, openElev, addFx, addShot, floatText, word, shake, spark, dropItem, breakProp, hitProp, propBox, addScore, makeProp } from './world.js';
import { Enemy } from './enemy.js';
import { Tilly } from './boss.js';
import { MRI, Lou } from './mri.js';
import { sfx, playMusic } from './sound.js';
import { resetAlarm, maybeYeller, updateAlarm, alarmPending } from './alarm.js';

const rr = (a, b) => a + W.rnd() * (b - a);

export function spawn(kind, where) {
  const vcount = (W.vc = (W.vc || 0) + 1);
  let x, y, tx, ty, st = 'enter';
  if (where === 'L' || where === 'R') {
    const side = where === 'L' ? -1 : 1;
    x = side < 0 ? W.camX - 26 : W.camX + G.VW + 26; y = rr(Y_MIN + 6, Y_MAX - 6);
    tx = side < 0 ? W.camX + rr(26, 70) : W.camX + G.VW - rr(26, 70); ty = y;
  } else if (where[0] === 'D') {  // patient-room door, e.g. D301
    const d = W.doors[+where.slice(1)];
    const dx = d ? d.x + 18 : W.camX + G.VW / 2;
    if (d) openDoor(d.num);
    x = dx; y = 121; tx = dx + rr(-10, 10); ty = rr(Y_MIN + 8, Y_MIN + 40); st = 'enter_door';
  } else if (where[0] === 'E') {  // elevator car, e.g. EB
    const e = W.elevs[where.slice(1)];
    const ex = e ? e.x + 40 : W.camX + G.VW / 2;
    if (e) openElev(where.slice(1));
    x = ex + rr(-14, 14); y = 122; tx = ex + rr(-50, 50); ty = rr(Y_MIN + 10, Y_MAX - 10); st = 'enter_door';
  }
  const e = new Enemy(kind, x, y, vcount);
  e.tx = Math.max(W.camX + 14, Math.min(W.camX + G.VW - 14, tx)); e.ty = ty; e.set(st); e.face = Math.sign(e.tx - x) || 1;
  if (st === 'enter_door') e.t = -rr(0, 0.25);
  W.enemies.push(e);
  return e;
}

// a lobbed urinal lands (or hits a nurse): splash FX, a SPLOOSH! word and a slippery yellow puddle
function splashAt(s, h) {
  if (s.splash === 'barium') {  // v0.5: Contrast Chugger's barium cup, a chalky white puddle
    for (const vx of [-50, 40, 10]) addFx({ type: 'chunk', spr: null, col: vx > 20 ? '#ffffff' : '#e8e4d8', sz: 3, x: s.x, y: s.y, z: 6, vx, vy: 0, vz: 120, spin: 0, dur: 0.8 });
    word('w_splat', s.x, s.y, h ? 20 : 4); sfx('splat', { vol: 0.7 });
    if (h) floatText(['CHALKY!', 'BANANA FLAVOR?!', 'MY CLEAN SCRUBS!'][Math.floor(W.rnd() * 3)], h.x, h.y, 66, '#ffffff');
    addShot({ kind: 'puddle', spr: 'puddle_w', x: s.x, y: s.y, z: 0, life: 5, owner: s.owner, hostile: true });
    return;
  }
  if (s.splash === 'jello') {  // v0.4: lobbed jello cup, wobbly green splat that's just as slippery
    addFx({ type: 'chunk', spr: null, col: '#5ad85a', sz: 3, x: s.x, y: s.y, z: 6, vx: -40, vy: 0, vz: 110, spin: 0, dur: 0.8 }); addFx({ type: 'chunk', spr: null, col: '#bfffbf', sz: 2, x: s.x, y: s.y, z: 6, vx: 50, vy: 0, vz: 130, spin: 0, dur: 0.8 });
    word('w_splat', s.x, s.y, h ? 20 : 4); sfx('splat', { vol: 0.7 });
    if (h) floatText(['JIGGLY!', 'NOT THE JELLO!', 'LIME? REALLY?'][Math.floor(W.rnd() * 3)], h.x, h.y, 66, '#8ae87a');
    addShot({ kind: 'puddle', spr: 'puddle_g', x: s.x, y: s.y, z: 0, life: 5, owner: s.owner, hostile: true });
    return;
  }
  addFx({ type: 'splash', x: s.x, y: s.y, z: h ? Math.max(10, s.z) : 0, dur: 0.45 });
  word('w_sploosh', s.x, s.y, h ? 20 : 4); sfx('splash', { vol: 0.6 });
  if (h) floatText(['EWWW!', 'GROSS!', 'NOT MY SCRUBS!'][Math.floor(W.rnd() * 3)], h.x, h.y, 66, '#fff27a');
  addShot({ kind: 'puddle', spr: 'puddle_y', x: s.x + (h ? -Math.sign(s.vx) * 6 : 0), y: s.y, z: 0, life: 5, owner: s.owner, hostile: true });
}
export const Director = {
  reset() { resetAlarm(W.lv); W.zone = -1; W.zoneOn = false; W.wave = 0; W.queue = []; W.go = 0; W.lockX = null; W.camMin = 0; W.camMax = W.lv.zones[0].lock; W.bossOn = false; W.cleared = false; W.endT = 0; },
  alive() { return W.enemies.filter((e) => e.alive && e.st !== 'dead').length; },
  update(dt) {
    const L = W.lv, zs = L.zones;
    const lead = Math.max(...W.heroes.filter((h) => h.alive).map((h) => h.x), -1e9);
    // trigger the next zone
    if (!W.zoneOn && W.zone + 1 < zs.length && lead >= zs[W.zone + 1].at) {
      W.zone++; W.zoneOn = true; W.wave = 0; const z = zs[W.zone];
      W.lockX = Math.min(z.lock, L.width - G.VW); W.go = 0;
      if (z.boss) { if (W.onBossCut && !z.mini) W.onBossCut(() => this.startBoss(z)); else this.startBoss(z); } else this.startWave();
    }
    // spawn queue (capped on-screen count)
    const cap = W.diff.cap + (W.heroes.length > 1 ? 1 : 0);
    for (const q of W.queue) { q.t -= dt; if (q.t <= 0 && !q.done && this.alive() < cap && Math.abs(W.camX - W.lockX) < 4) { q.done = true; spawn(q.kind, q.where); } }
    W.queue = W.queue.filter((q) => !q.done);
    // v0.5 mini-boss down: he naps where he fell (as scenery) and the zone opens up
    if (W.bossOn && W.boss && W.boss.mini && W.boss.st === 'defeat' && W.boss.t > 2.2) { W.decor.push(W.boss); W.boss = null; W.bossOn = false; playMusic(L.music || 'stage'); }
    updateAlarm(dt, spawn);
    if (W.zoneOn && !W.bossOn && !W.queue.length && !alarmPending() && this.alive() === 0 && Math.abs(W.camX - W.lockX) < 4) {
      const z = zs[W.zone];
      if (W.wave + 1 < z.waves.length) { W.wave++; this.startWave(); }
      else if (z.final && !W.finalT) { W.finalT = 0.001; }  // night shift's last wave: the lights come back on (main.js), then the tally
      else { W.zoneOn = false; W.lockX = null; W.camMin = W.camX; W.camMax = W.zone + 1 < zs.length ? zs[W.zone + 1].lock : L.width - G.VW; W.go = 3.2; sfx('select'); }
    }
    W.go = Math.max(0, W.go - dt);
    W.enemies = W.enemies.filter((e) => e.alive);
    this.shots(dt);
    if (W.finalT) { W.finalT += dt; if (W.finalT > 2.8 && !W.cleared) W.cleared = true; }
    if (W.bossOn && W.boss && W.boss.st === 'defeat' && !W.cleared) { W.endT += dt; if (W.endT > 2.6) { W.cleared = true; } }
  },
  startWave() {
    const z = W.lv.zones[W.zone], wave = z.waves[W.wave]; if (!wave) return;
    for (const [kind, where, delay] of wave) W.queue.push({ kind, where, t: delay });
    maybeYeller(!!W.forceYeller);  // v0.6: now and then a Fire Alarm Yeller joins the wave
    if (W.wave === 0 && z.title) floatText(z.title, W.lockX + G.VW / 2, 150, 60, '#8ad8ff');
  },
  startBoss(z = W.lv.zones[W.zone]) {
    W.bossOn = true; const kind = z.boss || 'tilly';
    if (kind === 'lou') { W.boss = new Lou(W.lockX + G.VW + 50, 170); playMusic('boss'); }
    else if (kind === 'mri') { W.boss = new MRI(z.lock); playMusic(W.lv.bossMusic || 'boss'); }
    else { W.boss = new Tilly(W.lockX + G.VW + 60, 176); playMusic(W.lv.bossMusic || 'boss'); }
    floatText(z.title || 'DAYROOM', W.lockX + G.VW / 2, 150, 70, '#d8b4f4');
  },
  backup() {  // a boss's call for help: two patients answer
    const kinds = W.lv.backup || ['wanderer', 'escape', 'crutch', 'bell', 'tray', 'o2'];
    spawn(kinds[Math.floor(W.rnd() * kinds.length)], W.doors[314] ? 'D314' : 'L'); spawn(kinds[Math.floor(W.rnd() * kinds.length)], W.rnd() < 0.5 ? 'L' : 'R');
  },
  // ------------------------------------------------------------ projectiles
  shots(dt) {
    for (const s of W.shots) {
      s.t += dt; s.life -= dt;
      if (s.kind === 'shock') {
        s.r = Math.min(s.rmax || 200, s.r + s.grow * dt);
        const list = s.hostile ? W.heroes : [...W.enemies, ...(W.boss ? [W.boss] : [])];
        for (const t of list) {
          if (s.hit.has(t) || !t.alive || !t.hittable || !t.hittable()) continue;
          const dx = (t.depthAny ? Math.max(0, t.front - s.x) : t.x - s.x) / s.r, dy = t.depthAny ? 0 : (t.y - s.y) / (s.r * 0.36);
          if (dx * dx + dy * dy <= 1 && t.z < 40) {
            s.hit.add(t);
            t.takeHit({ dmg: s.dmg, dir: Math.sign(t.x - s.x) || 1, kb: 150, down: !s.dizzy, dizzy: s.dizzy || 0, from: s.owner });
            if (!s.hostile) { spark(t.x, t.y, 30, s.col === '#ffe84a' ? 'bigspark' : 'bluespark'); addScore(s.owner, 100); }
          }
        }
        if (!s.hostile) for (const p of W.props) { if (s.hit.has(p) || p.st >= 2) continue; const dx = (p.x - s.x) / s.r, dy = (p.y - s.y) / (s.r * 0.36); if (dx * dx + dy * dy <= 1) { s.hit.add(p); hitProp(p, 20, { dir: Math.sign(p.x - s.x) || 1, kb: 220, from: s.owner }); } }
        if (s.r >= (s.rmax || 200)) s.life = Math.min(s.life, 0.08);
        continue;
      }
      if (s.kind === 'defib') {  // v0.6 Code Blue: two crackling bolts racing forward (facing direction only)
        s.reach = Math.min(G.VW + 40, s.reach + 1100 * dt);
        for (const t of [...W.enemies, ...(W.boss ? [W.boss] : [])]) {
          if (s.hit.has(t) || !t.alive || t.st === 'dead') continue;
          const tx = t.depthAny ? (t.front ?? t.x) : t.x, dx = (tx - s.x) * s.dir;
          if (dx < -10 || dx > s.reach || (!t.depthAny && Math.abs(t.y - s.y) > 28 + (t.big ? 6 : 0))) continue;
          s.hit.add(t);
          if (t.isBoss) { if (t.hittable && !t.hittable()) continue; t.takeHit({ dmg: t.maxHp * 0.12, dir: s.dir, from: s.owner, force: true }); t.flash = 0.6; t.stagT = Math.max(t.stagT || 0, 0.5); }
          else if (t.zap) t.zap(60 * ((s.owner && s.owner.d && s.owner.d.power) || 1), s.dir, s.owner);
          addFx({ type: 'spark', kind: 'bluespark', x: t.x, y: t.y, z: 30, dur: 0.35 }); addScore(s.owner, 200);
        }
        for (const p of W.props) { if (s.hit.has(p) || p.st >= 2 || p.rider) continue; const dx = (p.x - s.x) * s.dir; if (dx > -6 && dx < s.reach && Math.abs(p.y - s.y) < 28) { s.hit.add(p); hitProp(p, 30, { dir: s.dir, kb: 240, from: s.owner }); } }
        continue;
      }
      if (s.kind === 'puddle') {
        for (const h of W.heroes) {
          if (!h.hittable() || h.z > 2 || Math.abs(h.y - s.y) > 5 || Math.abs(h.x - s.x) > 14) continue;
          if ((h.slipT || 0) > W.t) continue; h.slipT = W.t + 1.6;
          floatText('WHOOPS!', h.x, h.y, 60, '#9ad8ff'); h.takeHit({ dmg: 3, dir: h.face, kb: 60, down: true }); sfx('splash', { vol: 0.5 });
        }
        continue;
      }
      // moving projectiles
      if (s.kind === 'boomerang') {
        const out = s.t < 0.62;
        if (out) s.x += s.vx * dt;
        else { const o = s.owner; const dx = o.x - s.x, dy = o.y - s.y, l = Math.hypot(dx, dy) || 1; s.x += dx / l * 320 * dt; s.y += dy / l * 160 * dt; if (l < 14) s.life = 0; if (!s.back) { s.back = true; s.hit = new Set(); } }
      } else {
        s.x += s.vx * dt;
        if (s.grav) { s.vz -= s.grav * dt; s.z += s.vz * dt; }
        if (s.z <= 0) {
          s.z = 0;
          if (s.roll) { s.vx *= Math.exp(-dt * 0.5); s.vz = 0; if (Math.abs(s.vx) < 6) s.vx = 0; }
          else if (s.kind === 'enemy') {
            s.life = 0; if (s.splash) splashAt(s); else addFx({ type: 'dust', x: s.x, y: s.y, dur: 0.3 });
            // v0.6: a missed meal tray stays on the floor as a loose, throwable prop (a few at most)
            if (s.spr === 'p_tray' && W.props.filter((p) => p.kind === 'mealtray' && p.st < 2).length < 4 && s.x > W.camX + 10 && s.x < W.camX + G.VW - 10) W.props.push(makeProp('mealtray', s.x, Math.max(Y_MIN, Math.min(Y_MAX, s.y))));
          }
        }
      }
      if (s.kind === 'enemy') {
        for (const h of W.heroes) {
          if (!h.hittable() || Math.abs(h.y - s.y) > 8 || Math.abs(h.x - s.x) > 11 || s.z > h.z + h.h || s.z + 6 < h.z) continue;
          h.takeHit({ dmg: s.dmg, dir: Math.sign(s.vx) || 1, kb: s.roll ? 80 : 40, stun: 0.35, down: !!s.roll, from: s.owner });
          s.life = 0; if (s.splash) splashAt(s, h); else { spark(s.x, s.y, s.z, 'spark'); sfx(s.roll ? 'bounce' : 'punch0', { vol: 0.5 }); } break;
        }
      } else if (s.kind === 'weapon' || s.kind === 'boomerang') {
        for (const t of [...W.enemies, ...(W.boss ? [W.boss] : [])]) {
          if (s.hit.has(t) || !t.alive || !t.hittable() || (!t.depthAny && Math.abs(t.y - s.y) > 10 + (t.big ? 6 : 0)) || Math.abs(t.x - s.x) > t.w / 2 + 8 || s.z > t.z + t.h) continue;
          s.hit.add(t); t.takeHit({ dmg: s.dmg, dir: Math.sign(s.vx) || (t.x > s.x ? 1 : -1), kb: 150, down: true, from: s.owner });
          spark(t.x, t.y, s.z, 'bigspark'); sfx('clang', { vol: 0.6 }); addScore(s.owner, 150);
          if (s.kind === 'weapon') { s.life = 0; s.dropAt = true; }
        }
        for (const p of W.props) { if (s.hit.has(p) || p.st >= 2) continue; const b = propBox(p); if (Math.abs(p.y - s.y) < 12 && s.x > b.x0 && s.x < b.x1 && s.z < b.z1 + 10) { s.hit.add(p); hitProp(p, 12, { dir: Math.sign(s.vx) || 1, kb: 160, from: s.owner }); } }
        if (s.kind === 'weapon' && (s.life <= 0 || s.x < W.camX - 20 || s.x > W.camX + G.VW + 20)) s.life = 0;
      }
      if (s.x < W.camX - 60 || s.x > W.camX + G.VW + 60) s.life = 0;
    }
    W.shots = W.shots.filter((s) => s.life > 0);
  },
};
W.director = Director;
