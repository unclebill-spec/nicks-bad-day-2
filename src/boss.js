// Turbo Tilly, the Electric Wheelchair Lady. Phase 1: charges across the hall, honks a stunning horn, and her battery
// panel pops open after every charge (the weak point). Phase 2 (half health): TURBO MODE, double charges, yarn and spilled
// water dropped behind her, and she rings her call button for backup. Defeated, she simply nods off.
import { G, text, spr, ellipse, rect } from './gfx.js';
import { Y_MIN, Y_MAX } from './data.js';
import { W, offY, addShot, addFx, floatText, shake, spark, word, addScore, bumpProps } from './world.js';
import { Actor, strike, clampY } from './actor.js';
import { sfx } from './sound.js';

const SOLID = 28, LANE = 18, TOP = 100;  // chair half-width (heroes can't stand in it), charge lane half-depth, text height

export class Tilly extends Actor {
  constructor(x, y) {
    super('tilly', x, y);
    this.isBoss = true; this.name = 'TURBO TILLY'; this.big = true; this.w = 48; this.h = 70;  // v0.7: Bill's override, ~1.45x a nurse's height (flag included)
    this.maxHp = this.hp = Math.round(420 * W.diff.hp * (W.heroes.length > 1 ? 1.35 : 1));
    this.face = -1; this.phase = 1; this.set('enter'); this.cd = 1.2; this.honkCd = 3; this.callCd = 6; this.charges = 0; this.shown = 0;
  }
  hittable() { return !['enter', 'turbo', 'defeat'].includes(this.st); }
  grabbable() { return false; }
  takeHit({ dmg, dir, from, force }) {
    if (!this.hittable() && !force) return;
    const weak = this.st === 'open' || force;
    const d = weak ? dmg : dmg * 0.3;
    this.hp -= d; this.flash = 0.1; if (from) addScore(from, d * 10);
    if (!weak && W.rnd() < 0.3) floatText('CLANK!', this.x, this.y, 66, '#c8ccd6');
    if (weak && this.st === 'open') { this.hurtT = 0.18; }
    if (this.hp <= 0) { this.hp = 0; this.die(from); return; }
    if (this.phase === 1 && this.hp < this.maxHp * 0.5) { this.phase = 2; this.set('turbo'); this.vx = 0; }
  }
  die(from) {
    this.set('defeat'); this.vx = 0; W.stop = 0.4; shake(8); sfx('explosion'); W.flash = 0.6; W.flashCol = '#ffffff';
    if (from && from.isHero) addScore(from, 10000);
    floatText('Zzz... wake me for bingo.', this.x, this.y, TOP, '#ffffff');
    for (const e of W.enemies) if (e.alive && e.st !== 'dead') e.takeHit({ dmg: 999, dir: Math.sign(e.x - this.x) || 1, kb: 120, down: true, force: true });
  }
  target() {
    const hs = W.heroes.filter((h) => h.alive && !['dead', 'out'].includes(h.st));
    if (!hs.length) return null;
    return hs.reduce((a, b) => (Math.abs(a.x - this.x) < Math.abs(b.x - this.x) ? a : b));
  }
  update(dt) {
    this.t += dt; this.flash = Math.max(0, this.flash - dt); this.cd -= dt; this.honkCd -= dt; this.callCd -= dt; this.hurtT = Math.max(0, (this.hurtT || 0) - dt);
    this.shown = Math.min(1, this.shown + dt * 0.8);
    const fn = this['s_' + this.st]; if (this.stagT > 0 && this.st !== 'defeat') { this.stagT -= dt; if (Math.floor(this.stagT * 20) % 3 === 0) addFx({ type: 'spark', kind: 'bluespark', x: this.x + (W.rnd() - 0.5) * (this.w || 40), y: this.y, z: 20 + W.rnd() * 60, dur: 0.12 }); } else if (fn) fn.call(this, dt);  // v0.6: Ativan / defib stagger
    this.y = clampY(this.y);
    // the chair is solid: nudge heroes out of it
    if (!['defeat'].includes(this.st)) for (const h of W.heroes) {
      if (!h.alive || h.z > 20 || ['dead', 'out', 'fall', 'down'].includes(h.st)) continue;
      const dx = h.x - this.x, dy = h.y - this.y;
      if (Math.abs(dx) < SOLID && Math.abs(dy) < 12) h.x = this.x + (Math.sign(dx) || 1) * SOLID;
    }
  }
  s_enter(dt) {
    const stopX = W.camX + G.VW * 0.72;
    if (this.t < 0.05) { sfx('motor', { vol: 0.6 }); }
    if (this.x > stopX) { this.x -= 150 * dt; return; }
    if (!this.greeted) { this.greeted = true; this.honk(true); floatText('Out of my way, sweetie!', this.x, this.y, TOP, '#ffffff'); sfx('tilly', { vol: 0.7 }); }
    if (this.t > 2.6) this.set('idle');
  }
  honk(free = false) {
    this.set('honk'); this.honked = false; this.honkCd = this.phase === 2 ? 4 : 6; this.free = free;
  }
  s_honk(dt) {
    if (!this.honked && this.t > 0.25) {
      this.honked = true; sfx('honk', { vol: 0.9 }); word('w_honk', this.x + this.face * 28, this.y, 44); shake(3);
      addShot({ kind: 'shock', x: this.x + this.face * 26, y: this.y, z: 0, r: 10, grow: 210, rmax: this.free ? 0 : 80, owner: this, dmg: 4, dizzy: 1.0, life: 0.45, col: '#ffe84a', hostile: true });
    }
    if (this.t > 0.8) { this.set(this.free ? 'enter' : 'idle'); if (this.free) this.t = 1.0; this.cd = 0.7; }
  }
  s_idle(dt) {
    const h = this.target(); if (!h) return;
    this.face = Math.sign(h.x - this.x) || this.face;
    this.y += Math.sign(h.y - this.y) * Math.min(Math.abs(h.y - this.y), 30 * dt);
    if (this.cd > 0) return;
    const near = Math.abs(h.x - this.x) < 62 && Math.abs(h.y - this.y) < 16;
    const minions = W.enemies.filter((e) => e.alive && e.st !== 'dead').length;
    if (this.phase === 2 && this.callCd <= 0 && minions < 2) return this.set('call');
    if (near && this.honkCd <= 0) return this.honk();
    this.set('rev'); this.charges = this.phase === 2 ? 2 : 1; sfx('motor', { vol: 0.6 });
  }
  s_rev(dt) {
    const dur = this.phase === 2 ? 0.7 : 0.95, lock = dur - 0.4;  // lane locks 0.4s before she goes: the flash is the real lane
    const h = this.target(); if (h && this.t < lock) { this.y += Math.sign(h.y - this.y) * Math.min(Math.abs(h.y - this.y), 60 * dt); this.face = Math.sign(h.x - this.x) || this.face; }
    if (Math.floor(this.t * 20) % 3 === 0) addFx({ type: 'spark', kind: 'bluespark', x: this.x - this.face * 22 + (W.rnd() - 0.5) * 20, y: this.y, z: 6 + W.rnd() * 10, dur: 0.15 });
    if (this.t > dur) { this.set('charge'); this.vx = this.face * (this.phase === 2 ? 300 : 230); this.hitSet = new Set(); this.dropT = 0; if (this.phase === 2) word('w_turbo', this.x, this.y, 64); }
  }
  s_charge(dt) {
    this.x += this.vx * dt;
    strike(this, { box: [-28, 34], z: [0, 62], depth: LANE - 5, dmg: 14, kb: 190, down: true, sfxName: 'heavy', once: this.hitSet, wordName: 'w_wham', props: false });
    bumpProps(this, 20, Math.sign(this.vx) || this.face, null, this.hitSet, 28);  // she plows through chairs and carts
    if (Math.floor(this.t * 14) % 2 === 0) { addFx({ type: 'dust', x: this.x - this.face * 22, y: this.y - 3, dur: 0.3 }); addFx({ type: 'dust', x: this.x + this.face * 16, y: this.y + 3, dur: 0.3 }); }
    if (this.phase === 2 && (this.dropT += dt) > 0.32) {
      this.dropT = 0;
      if (W.rnd() < 0.5) addShot({ kind: 'puddle', x: this.x - this.face * 32, y: this.y + (W.rnd() - 0.5) * 30, z: 0, life: 6, owner: this, hostile: true });
      else addShot({ kind: 'enemy', spr: W.rnd() < 0.5 ? 'yarn0' : 'yarn1', x: this.x - this.face * 12, y: clampY(this.y + (W.rnd() - 0.5) * 40), z: 46, vx: -this.face * 40, vz: 120, grav: 500, owner: this, dmg: 6, life: 2.5, roll: true });
    }
    const L = W.camX + 36, R = W.camX + G.VW - 36;
    if ((this.vx < 0 && this.x < L) || (this.vx > 0 && this.x > R)) {
      this.x = Math.max(L, Math.min(R, this.x)); shake(4); sfx('clang'); this.charges--;
      this.face = -this.face;
      if (this.charges > 0) { this.set('rev'); this.t = 0.2; }
      else { this.set('open'); this.opens = (this.opens || 0) + 1; floatText(['Oh, my battery!', 'Low battery!', 'Fiddlesticks!'][Math.floor(W.rnd() * 3)], this.x, this.y, TOP, '#ffffff'); }
    }
  }
  s_open(dt) {  // weak point: the battery panel is open and sparking
    if (Math.floor(this.t * 10) % 3 === 0) addFx({ type: 'smoke', x: this.x - this.face * 12, y: this.y, z: 30, dur: 0.6 });
    if (this.t > (this.phase === 2 ? 1.5 : 2.0)) { this.set('idle'); this.cd = this.phase === 2 ? 0.5 : 0.9; }
  }
  s_turbo(dt) {
    if (this.t < 0.05) { word('w_turbo', this.x, this.y, 64); floatText('TURBO MODE, SWEETIE!', this.x, this.y, TOP, '#8ad8ff'); W.flash = 0.6; W.flashCol = '#a24dff'; sfx('zap'); }
    if (Math.floor(this.t * 20) % 2 === 0) addFx({ type: 'spark', kind: 'bluespark', x: this.x + (W.rnd() - 0.5) * 54, y: this.y, z: W.rnd() * 66, dur: 0.15 });
    if (this.t > 1.3) { this.set('idle'); this.cd = 0.3; }
  }
  s_call(dt) {
    if (this.t < 0.05) { floatText('NURSE! NURSE! NURSE!', this.x, this.y, TOP, '#ffffff'); sfx('voice1', { vol: 0.6 }); }
    if (this.t > 0.6 && !this.called) { this.called = true; W.director.backup(); }
    if (this.t > 1.1) { this.called = false; this.callCd = 13; this.set('idle'); this.cd = 0.4; }
  }
  s_defeat(dt) { if (Math.floor(this.t * 6) % 3 === 0) addFx({ type: 'smoke', x: this.x - 10, y: this.y, z: 40, dur: 0.8 }); if (this.t > 0.6 && Math.floor(this.t * 2) !== Math.floor((this.t - dt) * 2)) addFx({ type: 'zzz', x: this.x + 10 * this.face, y: this.y, z: 74, dur: 1.4 }); }
  pose() {
    switch (this.st) {
      case 'enter': return ['drive', Math.floor(W.t * 12)];
      case 'idle': return this.hurtT > 0 ? ['hurt', 0] : ['idle', Math.floor(W.t * 3)];
      case 'rev': return ['rev', Math.floor(W.t * 16)];
      case 'charge': return ['drive', Math.floor(W.t * 16)];
      case 'honk': return ['honk', this.t > 0.25 ? 1 : 0];
      case 'open': return this.hurtT > 0 ? ['hurt', 0] : ['open', Math.floor(W.t * 6)];
      case 'turbo': return ['laugh', Math.floor(W.t * 6)];
      case 'call': return ['call', 0];
      case 'defeat': return ['defeat', Math.floor(W.t * 2)];
    }
    return ['idle', 0];
  }
  drawShadow() { const X = this.x - W.camX, Y = this.y + offY(); ellipse(X, Y + 1, 36, 5, '#000', 0.34); }
  draw() {
    const [n, i] = this.pose();
    if (this.phase === 2 && this.st !== 'defeat') { const X = this.x - W.camX, Y = this.y + offY(); ellipse(X, Y, 40 + Math.sin(W.t * 20) * 2, 6, '#3d9bff', 0.45); }
    // charge-lane telegraph (like Lou's): her lane flashes while she revs, solid once it's locked in
    if (this.st === 'rev') { const X = this.x - W.camX, lockd = this.t > (this.phase === 2 ? 0.3 : 0.55); if (lockd || Math.floor(W.t * 10) % 2) { const lx = this.face > 0 ? X : 0, lw = this.face > 0 ? G.VW - X : X, ly = this.y + offY() - LANE, col = this.phase === 2 ? '#ff4a6a' : '#ffe84a'; rect(lx, ly, lw, LANE * 2, col, lockd ? 0.28 : 0.16); rect(lx, ly, lw, 1, col, 0.7); rect(lx, ly + LANE * 2 - 1, lw, 1, col, 0.7); } }
    this.drawSprite(n, i);
    if (this.st === 'open') { const X = this.x - W.camX - this.face * 12, Y = this.y + offY() - 34; if (Math.floor(W.t * 8) % 2) { text('!', X, Y - 40, { col: '#ffe84a', align: 'center' }); if ((this.opens || 0) <= 2) text('HIT THE BATTERY!', X, Y - 52, { col: '#ffffff', align: 'center' }); } }
  }
}
