// Shared actor physics + drawing, and the combat helpers every fighter uses.
import { G, frame, anim, ellipse, spr, sprSize } from './gfx.js';
import { Y_MIN, Y_MAX, GRAV } from './data.js';
import { W, offY, spark, word, shake, floatText, addFx, breakProp, propBox, addScore } from './world.js';
import { sfx } from './sound.js';

export class Actor {
  constructor(sheet, x, y) {
    Object.assign(this, { sheet, x, y, z: 0, vx: 0, vy: 0, vz: 0, face: 1, st: 'idle', t: 0, hp: 1, maxHp: 1, inv: 0, flash: 0, alive: true, stun: 0, w: 14, h: 52, big: false });
  }
  set(st) { this.st = st; this.t = 0; }
  frameOf(name, i) { const A = anim(this.sheet, name); if (!A) return 0; return A.s + (((i % A.n) + A.n) % A.n); }
  handOf(name, i) { const A = anim(this.sheet, name); if (!A || !A.h.length) return [10, -30, 90]; return A.h[((i % A.n) + A.n) % A.n]; }
  airborne(dt) {  // generic ballistic step; returns true on landing this frame
    this.vz -= GRAV * dt; this.z += this.vz * dt; this.x += this.vx * dt; this.y += this.vy * dt;
    this.y = Math.max(Y_MIN, Math.min(Y_MAX, this.y));
    if (this.z <= 0) { this.z = 0; return true; }
    return false;
  }
  slide(dt, f = 6) { this.x += this.vx * dt; this.vx *= Math.exp(-dt * f); if (Math.abs(this.vx) < 2) this.vx = 0; }
  // knockdown arc / bounce / lie / get up (shared by heroes and patients)
  fallStep(dt, downDur = 0.75) {
    if (this.st === 'fall') {
      if (this.airborne(dt)) {
        if (this.vz < -110 && !this.bounced) { this.bounced = true; this.vz = 120; this.z = 0.1; this.vx *= 0.5; sfx('bounce', { vol: 0.35 }); addFx({ type: 'dust', x: this.x, y: this.y, z: 0, dur: 0.35 }); shake(2); }
        else { this.vz = 0; this.vx = 0; this.bounced = false; this.set(this.hp <= 0 ? 'dead' : 'down'); addFx({ type: 'dust', x: this.x, y: this.y, z: 0, dur: 0.35 }); }
      }
      return true;
    }
    if (this.st === 'down') { if (this.t > downDur) this.set('getup'); return true; }
    if (this.st === 'getup') { if (this.t > 0.32) { this.set('idle'); this.inv = Math.max(this.inv, this.isHero ? 0.9 : 0.25); } return true; }
    return false;
  }
  knock(dir, kb = 150, vz = 190) { this.set('fall'); this.vx = dir * kb; this.vz = vz; this.z = Math.max(this.z, 1); this.bounced = false; }
  drawShadow() {
    const X = this.x - W.camX, Y = this.y + offY(), s = Math.max(0.45, 1 - this.z / 140);
    ellipse(X, Y, (this.big ? 15 : 11) * s, 3 * s, '#000', 0.32);
  }
  drawSprite(name, i, opts = {}) {
    if (this.inv > 0 && this.isHero && Math.floor(W.t * 20) % 2 && this.st !== 'dead') return;
    const X = this.x - W.camX, Y = this.y + offY() - this.z + (opts.dy || 0);
    const idx = this.frameOf(name, i);
    const flip = (opts.face ?? this.face) < 0;
    frame(this.sheet, idx, X + (opts.dx || 0), Y, { flip, alpha: opts.alpha ?? 1 });
    if (this.flash > 0) frame(this.sheet, idx, X + (opts.dx || 0), Y, { flip, white: true, alpha: Math.min(1, this.flash * 9) });
  }
}

// ---- hit testing: a forward box from the attacker, against every patient / the boss / breakables
// box: [x0, x1] forward reach, z: [z0, z1] height band. Returns the list of things hit.
export function strike(a, { box, z = [10, 50], depth = 10, dmg, kb = 40, stun = 0.3, down = false, dizzy = false, sfxName = 'punch0', wordName = null, once = null, targets = null, props = true, back = false }) {
  const f = a.face, hits = [];
  const x0 = a.x + f * box[0], x1 = a.x + f * box[1], lo = Math.min(x0, x1), hi = Math.max(x0, x1);
  const za = a.z + z[0], zb = a.z + z[1];
  const list = targets || (a.isHero ? [...W.enemies, ...(W.boss ? [W.boss] : [])] : W.heroes);
  for (const t of list) {
    if (!t.alive || t === a || !t.hittable || !t.hittable()) continue;
    if (once && once.has(t)) continue;
    const dep = depth + (t.big ? 5 : 0);
    if (Math.abs(t.y - a.y) > dep) continue;
    const tw = t.w / 2 + (t.big ? 6 : 0);
    if (t.x + tw < lo || t.x - tw > hi) continue;
    if (t.z + t.h < za || t.z > zb) continue;
    const dir = back ? -f : (Math.sign(t.x - a.x) || f);
    t.takeHit({ dmg, dir, kb, stun, down, dizzy, from: a });
    if (once) once.add(t);
    hits.push(t);
    spark((t.x + a.x + f * (box[1] - 8)) / 2 + (t.x - a.x) * 0.3, t.y + 1, a.z + (z[0] + z[1]) / 2, dmg >= 12 ? 'bigspark' : 'spark');
  }
  if (props && a.isHero) for (const p of W.props) {
    if (p.st >= 2 || (once && once.has(p))) continue;
    const b = propBox(p);
    if (Math.abs(p.y - a.y) > depth + 6 || b.x1 < lo || b.x0 > hi) continue;
    if (breakProp(p, dmg, a)) { if (once) once.add(p); hits.push(p); }
  }
  if (hits.length) {
    sfx(sfxName, { vol: 0.8 });
    const real = hits.filter((h) => h.takeHit);
    if (real.length) {
      W.stop = Math.max(W.stop, down ? 0.075 : 0.045);
      if (down) shake(3);
      if (wordName) word(wordName, real[0].x, real[0].y, a.z + 16);
      if (a.isHero) { const foe = real.find((r) => !r.isBoss); if (foe) { a.lastFoe = foe; a.lastFoeT = W.t + 2.2; } a.combo = (a.combo || 0) + real.length; a.comboT = 1.6; a.maxCombo = Math.max(a.maxCombo || 0, a.combo); a.meter = Math.min(100, (a.meter || 0) + dmg * 0.55 * real.length); }
    }
  }
  return hits;
}

export const clampY = (v) => Math.max(Y_MIN, Math.min(Y_MAX, v));
export { addScore, floatText, word, shake, spark, addFx };
