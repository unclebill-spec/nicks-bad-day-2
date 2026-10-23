// v0.15 Boss: THE STORK, on a "special delivery" to Labor & Delivery. A giant (parody) stork in a mail-carrier cap, ~1.5x a
// nurse standing. Moves: a beak-PECK, a beak-first CHARGE down the hall, a WING GUST that shoves nurses across the lanes, and
// a fly-over BUNDLE DROP (watch the shadows!). Phase 2 (half health): "SPECIAL DELIVERY!" -> faster, more bundles, backup.
// Defeated: it grabs its "baby" (a sack of hospital laundry) and flaps away: "Wrong... address... honk". Comedic, never scary.
import { G, text, spr, ellipse } from './gfx.js';
import { W, offY, addShot, addFx, floatText, shake, word, addScore } from './world.js';
import { Actor, strike, clampY } from './actor.js';
import { sfx } from './sound.js';

const TOP = 112;
export const STORK = { hp: 460, speed: [64, 88], peck: 10, charge: 12, bundle: 8, gust: 120, knockCd: 2.4 };
export const STORK_LINES = {
  greet: ['SPECIAL DELIVERY! Sign here, please!'],
  taunt: ['Honk! Who ordered a baby?', 'No returns. No exchanges.', 'I have forty more stops tonight!', 'Is this Room 204? It says Room 204.', 'Signature required!'],
  hurt: ['Mind the feathers!', 'HONK! Rude!', 'I am a licensed carrier!', 'My cap! Watch the cap!'],
  drop: ['Incoming bundle!', 'Air mail!', 'Fragile! Probably!'],
  gust: ['Stand back! Wingspan!', 'WHOOSH!', 'Gusty out tonight!'],
  p2: ['SPECIAL DELIVERY!', 'EXPRESS SHIPPING!'],
  ko: 'Wrong... address... honk',
};
const pick = (a) => a[Math.floor(W.rnd() * a.length)];

export class Stork extends Actor {
  constructor(x, y) {
    super('stork', x, y);
    this.isBoss = true; this.name = 'THE STORK'; this.big = true; this.w = 30; this.h = 76; this.p2label = 'SPECIAL DELIVERY!';
    this.maxHp = this.hp = Math.round(STORK.hp * W.diff.hp * (W.heroes.length > 1 ? 1.35 : 1));
    this.face = -1; this.phase = 1; this.shown = 0; this.cd = 1.2; this.knockCd = 0; this.hits = 0; this.dropCd = 4; this.gustCd = 6; this.chargeCd = 3;
    this.set('enter');
  }
  hint() {
    if (this.st === 'drop') return 'WATCH THE SHADOWS!';
    if (this.st === 'gust') return 'WING GUST! HOLD ON!';
    if (this.st === 'charge' && this.t < 0.45) return 'BEAK CHARGE! JUMP OR DODGE!';
    return null;
  }
  hittable() { return !['enter', 'defeat', 'fall', 'down', 'getup', 'p2'].includes(this.st) && this.z < 30; }
  grabbable() { return false; }
  takeHit({ dmg, from, dir, down, force }) {
    if (!this.hittable() && !force) return;
    this.hp -= dmg; this.flash = 0.1; if (from) addScore(from, dmg * 10);
    if (this.hp <= 0) { this.hp = 0; this.die(from); return; }
    if (this.phase === 1 && this.hp < this.maxHp * 0.5) { this.phase = 2; this.p2Next = true; }
    this.hits++; this.hurtT = 0.2;
    if ((down || this.hits >= 4) && this.knockCd <= 0 && this.z < 4) {
      this.hits = 0; this.knockCd = STORK.knockCd; this.knock(dir || 1, 120, 160); sfx('storkhonk', { vol: 0.6, rate: 1.2 });
      if (W.rnd() < 0.6) floatText(pick(STORK_LINES.hurt), this.x, this.y, TOP - 10, '#ffffff');
      for (let i = 0; i < 3; i++) addFx({ type: 'chunk', spr: null, col: '#f8f8fc', sz: 3, x: this.x, y: this.y, z: 50, vx: (W.rnd() - 0.5) * 120, vy: 0, vz: 80 + W.rnd() * 80, spin: 0, dur: 1.0 });
    }
  }
  die(from) {
    this.set('defeat'); this.vx = 0; W.stop = 0.4; shake(6); sfx('explosion', { vol: 0.6 }); W.flash = 0.5; W.flashCol = '#ffffff';
    if (from && from.isHero) addScore(from, 10000);
    floatText(STORK_LINES.ko, this.x, this.y, TOP, '#ffffff'); sfx('stork_ko', { vol: 0.8 });
    for (let i = 0; i < 8; i++) addFx({ type: 'chunk', spr: null, col: i % 2 ? '#f8f8fc' : '#2a2a3a', sz: 3, x: this.x, y: this.y, z: 50, vx: (W.rnd() - 0.5) * 160, vy: 0, vz: 120 + W.rnd() * 120, spin: 0, dur: 1.4 });
    for (const e of W.enemies) if (e.alive && e.st !== 'dead') e.takeHit({ dmg: 999, dir: Math.sign(e.x - this.x) || 1, kb: 120, down: true, force: true });
  }
  target() {
    const hs = W.heroes.filter((h) => h.alive && !['dead', 'out'].includes(h.st));
    if (!hs.length) return null;
    return hs.reduce((a, b) => (Math.abs(a.x - this.x) + Math.abs(a.y - this.y) < Math.abs(b.x - this.x) + Math.abs(b.y - this.y) ? a : b));
  }
  update(dt) {
    this.t += dt; this.flash = Math.max(0, this.flash - dt); this.cd -= dt; this.knockCd -= dt; this.dropCd -= dt; this.gustCd -= dt; this.chargeCd -= dt;
    this.hurtT = Math.max(0, (this.hurtT || 0) - dt); this.shown = Math.min(1, this.shown + dt * 0.8);
    if (this.stagT > 0 && this.st !== 'defeat') this.stagT -= dt;
    else if (['fall', 'down', 'getup'].includes(this.st)) { if (!this.fallStep(dt, 0.9) || this.st === 'idle') this.set('chase'); }
    else { const fn = this['s_' + this.st]; if (fn) fn.call(this, dt); }
    if (this.st !== 'defeat') this.y = clampY(this.y);
  }
  s_enter(dt) {  // swoops in from the right and lands
    const stopX = W.camX + G.VW * 0.7;
    if (this.x > stopX) { this.x -= 110 * dt; this.z = Math.max(0, (this.x - stopX) * 0.35); this.flying = true; if (Math.floor(this.t * 3) !== Math.floor((this.t - dt) * 3)) sfx('flap', { vol: 0.4 }); return; }
    this.z = 0; this.flying = false;
    if (!this.greeted) { this.greeted = true; floatText(STORK_LINES.greet[0], this.x, this.y, TOP, '#ffffff'); sfx('stork', { vol: 0.85 }); word('w_honk', this.x, this.y, 96); }
    if (this.t > 2.6) { this.set('chase'); this.cd = 0.6; }
  }
  s_chase(dt) {
    const h = this.target(); if (!h) return;
    if (this.p2Next) { this.p2Next = false; return this.set('p2'); }
    const dx = h.x - this.x, dy = h.y - this.y, adx = Math.abs(dx);
    this.face = Math.sign(dx) || this.face;
    const want = this.cd > 0.4 ? 80 : 40, gx = h.x - Math.sign(dx || 1) * want;
    const mx = gx - this.x, my = dy, ml = Math.hypot(mx, my), sp = STORK.speed[this.phase - 1];
    if (ml > 4) { this.x += mx / ml * sp * dt; this.y += my / ml * sp * 0.72 * dt; this.walking = true; } else this.walking = false;
    if (this.cd > 0) return;
    if (adx < 56 && Math.abs(dy) < 12) { this.set('peck'); this.hitDone = false; return; }
    if (this.dropCd <= 0) { this.set('drop'); this.drops = 0; this.dropT = 0.5; floatText(pick(STORK_LINES.drop), this.x, this.y, TOP - 10, '#ffffff'); return; }
    if (this.gustCd <= 0 && adx < 200) { this.set('gust'); this.gustDir = h.y > 176 ? -1 : 1; floatText(pick(STORK_LINES.gust), this.x, this.y, TOP - 10, '#ffffff'); return; }
    if (this.chargeCd <= 0 && adx > 70 && Math.abs(dy) < 14) { this.set('charge'); this.hitSet = new Set(); sfx('storkhonk', { vol: 0.7 }); return; }
    if (W.rnd() < 0.08) { this.set('taunt'); floatText(pick(STORK_LINES.taunt), this.x, this.y, TOP - 10, '#ffffff'); this.cd = 1; }
  }
  s_peck(dt) {  // a quick beak jab
    if (!this.hitDone && this.t > 0.38) { this.hitDone = true; sfx('whoosh', { vol: 0.5 }); strike(this, { box: [10, 60], z: [20, 80], depth: 12, dmg: STORK.peck, kb: 150, down: W.rnd() < 0.3, sfxName: 'punch1', wordName: 'w_smack', props: false }); }
    if (this.t > 0.7) { this.set('chase'); this.cd = this.phase === 2 ? 0.5 : 0.85; }
  }
  s_charge(dt) {  // windup (0.45s), then a beak-first sprint down the lane; it skids to a stop at the screen edge
    if (this.t < 0.45) return;
    const sp = this.phase === 2 ? 290 : 250;
    this.x += this.face * sp * dt;
    if (Math.floor(this.t * 10) % 2) addFx({ type: 'chunk', spr: null, col: '#f8f8fc', sz: 2, x: this.x - this.face * 20, y: this.y, z: 30, vx: -this.face * 60, vy: 0, vz: 20, spin: 0, dur: 0.4 });
    for (const h of W.heroes) {
      if (this.hitSet.has(h) || !h.hittable() || h.z > 22 || Math.abs(h.y - this.y) > 14 || Math.abs(h.x - (this.x + this.face * 24)) > 18) continue;
      this.hitSet.add(h); h.takeHit({ dmg: STORK.charge, dir: this.face, kb: 180, down: true, from: this }); word('w_smack', h.x, h.y, 30); sfx('punch1');
    }
    const edge = this.face > 0 ? this.x > W.camX + G.VW - 30 : this.x < W.camX + 30;
    if (edge || this.t > 1.6) { this.x = Math.max(W.camX + 30, Math.min(W.camX + G.VW - 30, this.x)); this.set('chase'); this.cd = 0.8; this.chargeCd = this.phase === 2 ? 3 : 4.5; shake(2); }
  }
  s_gust(dt) {  // big wing beats: shove every nurse in front of it back AND across the lanes (into the props / puddles / the crowd)
    if (Math.floor(this.t * 4) !== Math.floor((this.t - dt) * 4)) sfx('flap', { vol: 0.55 });
    if (this.t > 0.35 && this.t < 1.5) {
      for (const h of W.heroes) {
        if (!h.alive || h.st === 'dead' || Math.sign(h.x - this.x) !== this.face || Math.abs(h.x - this.x) > 230) continue;
        h.x += this.face * STORK.gust * dt; h.y = clampY(h.y + this.gustDir * 55 * dt); W.stats.gusted = (W.stats.gusted || 0) + dt;
      }
      for (const p of W.props) { if (Math.sign(p.x - this.x) === this.face && Math.abs(p.x - this.x) < 200 && p.st < 2 && !p.carried) p.x += this.face * 60 * dt; }
      if (W.rnd() < 0.6) addFx({ type: 'chunk', spr: null, col: '#e8f4ff', sz: 2, x: this.x + this.face * (30 + W.rnd() * 150), y: this.y + (W.rnd() - 0.5) * 50, z: 10 + W.rnd() * 50, vx: this.face * 220, vy: this.gustDir * 40, vz: 0, spin: 0, dur: 0.5 });
    }
    if (this.t > 1.7) { this.set('chase'); this.cd = 0.5; this.gustCd = this.phase === 2 ? 5 : 7; }
  }
  s_drop(dt) {  // takes off, flies over the nurses and drops laundry "bundles" on them (shadows show where)
    const up = Math.min(1, this.t / 0.5), n = this.phase === 2 ? 3 : 2;
    this.z = 70 * up * (this.drops >= n && this.t > this.landT ? Math.max(0, 1 - (this.t - this.landT) / 0.5) : 1);
    if (Math.floor(this.t * 3) !== Math.floor((this.t - dt) * 3)) sfx('flap', { vol: 0.45 });
    const h = this.target();
    if (h && this.drops < n) { const dx = h.x - this.x; this.face = Math.sign(dx) || this.face; this.x += Math.max(-150, Math.min(150, dx * 2.4)) * dt; this.y += (h.y - this.y) * 2 * dt; }
    this.dropT -= dt;
    if (this.t > 0.5 && this.drops < n && this.dropT <= 0) {
      this.drops++; this.dropT = 0.55;
      const tx = h ? h.x + (W.rnd() - 0.5) * 20 : this.x, ty = h ? h.y : this.y;
      addShot({ kind: 'enemy', spr: 'p_bundle', x: tx, y: ty, z: this.z + 30, vx: 0, vz: 0, grav: 260, owner: this, dmg: STORK.bundle, spin: 3, life: 3 });
      sfx('whoosh', { vol: 0.5 }); W.stats.bundles = (W.stats.bundles || 0) + 1;
      if (this.drops >= n) this.landT = this.t + 0.4;
    }
    if (this.drops >= n && this.t > this.landT + 0.5) { this.z = 0; this.set('chase'); this.cd = 0.6; this.dropCd = this.phase === 2 ? 5 : 7.5; }
  }
  s_taunt(dt) { if (this.t > 0.9) this.set('chase'); }
  s_p2(dt) {
    if (this.t < 0.05) { floatText(pick(STORK_LINES.p2), this.x, this.y, TOP, '#ff8a9a'); W.flash = 0.5; W.flashCol = '#a24dff'; sfx('stork'); word('w_delivery', this.x, this.y, 96); if (W.director && W.director.backup) W.director.backup(); }
    if (this.t > 1.2) { this.set('chase'); this.cd = 0.3; this.dropCd = 1; }
  }
  s_defeat(dt) {  // dazed for a beat, then it grabs the "baby" (the laundry sack) and flaps off up and away
    if (this.t > 0.9) {
      if (!this.gone) { this.gone = true; sfx('flap', { vol: 0.6 }); sfx('storkhonk', { vol: 0.6, rate: 0.9 }); floatText('...it was just laundry anyway.', this.x, this.y, TOP + 6, '#c8d4f0'); }
      this.face = 1; this.x += 120 * dt; this.z += 70 * dt;
      if (Math.floor(this.t * 3) !== Math.floor((this.t - dt) * 3)) sfx('flap', { vol: 0.35 });
    }
  }
  pose() {
    switch (this.st) {
      case 'enter': return this.flying ? ['fly', Math.floor(W.t * 6)] : ['shout', Math.floor(this.t * 4)];
      case 'chase': return this.hurtT > 0 ? ['hurt', 0] : this.walking ? ['walk', Math.floor(W.t * 8)] : ['idle', Math.floor(W.t * 3)];
      case 'peck': return ['peck', this.t > 0.36 ? 1 : 0];
      case 'charge': return this.t < 0.45 ? ['peck', 0] : ['charge', Math.floor(this.t * 10)];
      case 'gust': return ['flap', Math.floor(this.t * 8)];
      case 'drop': return this.z > 8 ? ['drop', Math.floor(this.t * 6)] : ['flap', Math.floor(this.t * 8)];
      case 'taunt': case 'p2': return ['shout', Math.floor(this.t * 5)];
      case 'fall': return ['fall', 0];
      case 'down': return ['down', 0];
      case 'getup': return ['getup', 0];
      case 'defeat': return this.t > 0.9 ? ['fly', Math.floor(this.t * 6)] : ['dizzy', Math.floor(this.t * 4)];
    }
    return ['idle', 0];
  }
  drawShadow() { const X = this.x - W.camX, Y = this.y + offY(), k = Math.max(0.3, 1 - this.z / 140); ellipse(X, Y, 20 * k, 3.5 * k, '#000', 0.32 * k); }
  draw() {
    const X = this.x - W.camX, oy = offY();
    if (this.phase === 2 && this.st !== 'defeat') ellipse(X, this.y + oy, 22, 4, '#a24dff', 0.4 + Math.sin(W.t * 20) * 0.08);
    const [n, i] = this.pose(); this.drawSprite(n, i);
    if (((this.st === 'peck' && this.t < 0.36) || (this.st === 'charge' && this.t < 0.45) || (this.st === 'gust' && this.t < 0.35)) && Math.floor(this.t * 12) % 2) text('!', X + this.face * 6, this.y + oy - this.z - 104, { col: '#ff5a3a', align: 'center' });
  }
  drawIcon(x, y) { spr('face_stork', x, y, { scale: 0.75 }); }
  light(L) { if (this.st !== 'defeat') L.push({ x: this.x, y: this.y - 44, r: 34, col: '#e8f0ff', a: 0.35 }); }
}
