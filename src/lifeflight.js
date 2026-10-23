// v0.16 Boss: the rogue LIFE FLITE crew (parody air-ambulance branding) on the rooftop helipad, ~3 AM. ROXY the flight nurse
// (navy flight jacket + belted cargo pants, ponytail, defib paddles, ~1.35x a nurse) runs the show; DUKE the flight medic
// (~1.25x, jump bag) is her backup, and ACE the pilot buzzes the roof in the chopper. They have been on call for 30 hours.
// Moves: a paddle SWING, a defib "CLEAR!" ZAP (a blue spark that rolls down the lane and DIZZIES), a shoulder CHARGE, and an
// "AIR SUPPORT!" radio call: Ace's chopper sweeps across the roof and its ROTOR WASH (the glowing ring on the floor) shoves
// and dizzies anyone under it. Phase 2 (half health): "HOT LOAD!" -> the chopper hovers over the big pad (the wash pulses
// on / off), Duke jumps out, and Roxy speeds up. Defeated: the chopper lands, the rotor spins down, and Roxy + Duke "go off
// shift": out cold on a stretcher under a pile of zzz. Comedic, never mean.
import { G, text, spr, ellipse, ring } from './gfx.js';
import { Y_MIN, Y_MAX } from './data.js';
import { W, offY, addShot, addFx, floatText, shake, word, addScore } from './world.js';
import { Actor, strike, clampY } from './actor.js';
import { sfx } from './sound.js';
import { spawn } from './stage.js';

const TOP = 116;
export const LIFEFLIGHT = { hp: 480, speed: [66, 90], swing: 10, zap: 6, charge: 12, wash: 3, washR: 66, washPush: 120, knockCd: 2.4, pad: 2540 };
export const LIFEFLIGHT_LINES = {
  greet: ['LIFE FLITE! Nobody move, we are on a CALL!'],
  taunt: ['Thirty hours on call. THIRTY.', 'This is MY helipad.', 'You call that a transfer?', 'Ace! Keep it running!', 'Nobody lands here without my say-so!'],
  hurt: ['Watch the jacket!', 'I have PADDLES, hon.', 'Rude! I am a professional!', 'Ow! Okay! Okay!'],
  zap: ['CLEAR!', 'Everybody CLEAR!', 'Charging... CLEAR!'],
  radio: ['Ace! AIR SUPPORT!', 'Flite One, buzz the roof!', 'Ace, give them some wind!'],
  ace: ['Roger that, Roxy!', 'Coming in hot!', 'Yeehaw! Hold your hats!'],
  p2: ['HOT LOAD!', 'DUKE! HOT LOAD!'],
  ko: 'Going... off... shift... zzz',
};
const pick = (a) => a[Math.floor(W.rnd() * a.length)];

export class LifeFlight extends Actor {
  constructor(x, y) {
    super('roxy', x, y);
    this.isBoss = true; this.name = 'ROXY + THE LIFE FLITE CREW'; this.big = true; this.w = 26; this.h = 70; this.p2label = 'HOT LOAD!';
    this.maxHp = this.hp = Math.round(LIFEFLIGHT.hp * W.diff.hp * (W.heroes.length > 1 ? 1.35 : 1));
    this.face = -1; this.phase = 1; this.shown = 0; this.cd = 1.2; this.knockCd = 0; this.hits = 0; this.zapCd = 3; this.radioCd = 6; this.chargeCd = 4;
    this.heli = null; this.dukes = []; this.bolts = [];
    this.set('enter');
  }
  hint() {
    if (this.heli && this.heli.wash > 0) return 'ROTOR WASH! STAY OUT OF THE RING!';
    if (this.st === 'zap' && this.t < 0.5) return 'CLEAR! JUMP THE ZAP!';
    if (this.st === 'charge' && this.t < 0.45) return 'CHARGE! DODGE!';
    return null;
  }
  hittable() { return !['enter', 'defeat', 'fall', 'down', 'getup', 'p2'].includes(this.st); }
  grabbable() { return false; }
  takeHit({ dmg, from, dir, down, force }) {
    if (!this.hittable() && !force) return;
    this.hp -= dmg; this.flash = 0.1; if (from) addScore(from, dmg * 10);
    if (this.hp <= 0) { this.hp = 0; this.die(from); return; }
    if (this.phase === 1 && this.hp < this.maxHp * 0.5) { this.phase = 2; this.p2Next = true; }
    this.hits++; this.hurtT = 0.2;
    if ((down || this.hits >= 4) && this.knockCd <= 0) {
      this.hits = 0; this.knockCd = LIFEFLIGHT.knockCd; this.knock(dir || 1, 120, 160);
      if (W.rnd() < 0.6) floatText(pick(LIFEFLIGHT_LINES.hurt), this.x, this.y, TOP - 10, '#ffffff');
    }
  }
  die(from) {
    this.set('defeat'); this.vx = 0; this.bolts = []; W.stop = 0.4; shake(6); sfx('explosion', { vol: 0.6 }); W.flash = 0.5; W.flashCol = '#ffffff';
    if (from && from.isHero) addScore(from, 10000);
    floatText(LIFEFLIGHT_LINES.ko, this.x, this.y, TOP, '#ffffff'); sfx('roxy_ko', { vol: 0.8 });
    for (let i = 0; i < 6; i++) addFx({ type: 'chunk', spr: i % 2 ? 'deb_case' : 'deb_metal', x: this.x, y: this.y, z: 50, vx: (W.rnd() - 0.5) * 160, vy: 0, vz: 120 + W.rnd() * 120, spin: 8, dur: 1.2 });
    for (const e of W.enemies) if (e.alive && e.st !== 'dead') e.takeHit({ dmg: 999, dir: Math.sign(e.x - this.x) || 1, kb: 120, down: true, force: true });
    // the chopper comes in to land on the pad; Roxy + Duke go off shift on the stretcher next to it
    const padX = Math.max(W.camX + 90, Math.min(W.camX + G.VW - 90, LIFEFLIGHT.pad));
    this.heli = { x: this.heli ? this.heli.x : W.camX + G.VW + 90, y: 168, z: this.heli ? this.heli.z : 70, vx: 0, face: -1, mode: 'land', tx: padX, wash: 0, t: 0 };
    this.nap = { x: Math.max(W.camX + 40, Math.min(W.camX + G.VW - 60, this.x)), y: clampY(this.y), t: 0 };
    this.dukeNap = new Actor('duke', this.nap.x + 2, this.nap.y); this.dukeNap.face = 1;
    W.stats.offShift = 1;
  }
  target() {
    const hs = W.heroes.filter((h) => h.alive && !['dead', 'out'].includes(h.st));
    if (!hs.length) return null;
    return hs.reduce((a, b) => (Math.abs(a.x - this.x) + Math.abs(a.y - this.y) < Math.abs(b.x - this.x) + Math.abs(b.y - this.y) ? a : b));
  }
  update(dt) {
    this.t += dt; this.flash = Math.max(0, this.flash - dt); this.cd -= dt; this.knockCd -= dt; this.zapCd -= dt; this.radioCd -= dt; this.chargeCd -= dt;
    this.hurtT = Math.max(0, (this.hurtT || 0) - dt); this.shown = Math.min(1, this.shown + dt * 0.8);
    this.boltsTick(dt); this.heliTick(dt);
    if (this.stagT > 0 && this.st !== 'defeat') this.stagT -= dt;
    else if (['fall', 'down', 'getup'].includes(this.st)) { if (!this.fallStep(dt, 0.9) || this.st === 'idle') this.set('chase'); }
    else { const fn = this['s_' + this.st]; if (fn) fn.call(this, dt); }
    if (this.st !== 'defeat') this.y = clampY(this.y);
  }
  // ---- the defib zap: a blue spark that skims along the floor of her lane; a nurse standing in it gets zapped (dizzy)
  boltsTick(dt) {
    for (const s of this.bolts) {
      s.x += s.vx * dt; s.t += dt;
      if (W.rnd() < 0.5) addFx({ type: 'spark', kind: 'bluespark', x: s.x, y: s.y, z: 4 + W.rnd() * 8, dur: 0.18 });
      for (const h of W.heroes) {
        if (s.hit.has(h) || !h.hittable() || h.z > 10 || Math.abs(h.y - s.y) > 10 || Math.abs(h.x - s.x) > 12) continue;
        s.hit.add(h); h.takeHit({ dmg: LIFEFLIGHT.zap * W.diff.dmg, dir: Math.sign(s.vx), kb: 60, dizzy: 1.1, from: this }); word('w_clear', h.x, h.y, 30); sfx('defib', { vol: 0.6 });
        W.stats.zapped = (W.stats.zapped || 0) + 1;
      }
    }
    this.bolts = this.bolts.filter((s) => s.t < 2.4 && s.x > W.camX - 30 && s.x < W.camX + G.VW + 30);
  }
  // ---- Ace's chopper. mode 'pass' = a buzz across the roof (wash follows it), 'hover' = phase 2 over the big pad (wash
  // pulses: 2.2 s on, 2 s off, a thin ring telegraphs it), 'land' = after the KO (sets down, rotor spins down, no wash)
  heliTick(dt) {
    const H = this.heli; if (!H) return;
    H.t += dt;
    if (Math.floor(H.t * (H.mode === 'land' && H.z <= 0 ? 2 : 6)) !== Math.floor((H.t - dt) * (H.mode === 'land' && H.z <= 0 ? 2 : 6)) && !(H.mode === 'land' && H.t > 4)) sfx('rotor', { vol: 0.35 });
    if (H.mode === 'pass') {
      H.x += H.vx * dt; H.wash = H.t > 0.4 ? 1 : 0;
      if ((H.vx > 0 && H.x > W.camX + G.VW + 120) || (H.vx < 0 && H.x < W.camX - 120)) { this.heli = null; return; }
    } else if (H.mode === 'hover') {
      H.x += (H.tx - H.x) * Math.min(1, dt * 1.5); H.z += (46 - H.z) * Math.min(1, dt * 2);
      const cyc = (H.t % 4.2); H.warn = cyc < 0.9; H.wash = cyc >= 0.9 && cyc < 3.1 ? 1 : 0;
    } else if (H.mode === 'land') {
      H.x += (H.tx - H.x) * Math.min(1, dt * 1.2); H.z = Math.max(0, H.z - 30 * dt); H.wash = 0; H.warn = false;
      return;
    }
    if (!H.wash) return;
    const R = LIFEFLIGHT.washR;
    for (const h of W.heroes) {
      if (!h.alive || h.st === 'dead' || h.st === 'out') continue;
      const dx = h.x - H.x, dy = (h.y - H.y) * 2.6, d = Math.hypot(dx, dy);
      if (d > R) continue;
      const k = 1 - d / R, nx = d > 1 ? dx / d : (W.rnd() < 0.5 ? -1 : 1), ny = d > 1 ? dy / d : 0;
      h.x += nx * LIFEFLIGHT.washPush * k * dt; h.y = clampY(h.y + ny * LIFEFLIGHT.washPush * 0.45 * k * dt);
      W.stats.washed = (W.stats.washed || 0) + dt;
      if (!h.washT || W.t > h.washT) { h.washT = W.t + 1.6; if (h.hittable() && h.z < 8) { h.takeHit({ dmg: LIFEFLIGHT.wash * W.diff.dmg, dir: Math.sign(dx) || 1, kb: 40, dizzy: 0.8, from: this }); word('w_gust', h.x, h.y, 40); } }
    }
    if (W.rnd() < 0.8) { const a = W.rnd() * Math.PI * 2; addFx({ type: 'chunk', spr: null, col: '#d8e0ff', sz: 2, x: H.x + Math.cos(a) * R * 0.5, y: H.y + Math.sin(a) * R * 0.2, z: 4, vx: Math.cos(a) * 200, vy: Math.sin(a) * 50, vz: 30, spin: 0, dur: 0.4 }); }
  }
  callChopper() {  // phase 1: a buzz across the roof, through the nurses' lane
    const h = this.target(), from = W.rnd() < 0.5 ? -1 : 1;
    this.heli = { mode: 'pass', x: from < 0 ? W.camX - 110 : W.camX + G.VW + 110, y: h ? h.y : 176, z: 52, vx: -from * 200, face: -from, t: 0, wash: 0 };
    floatText(pick(LIFEFLIGHT_LINES.ace), this.heli.x - from * 140, this.heli.y, 100, '#bfe0ff'); sfx('ace', { vol: 0.7 });
    W.stats.flyovers = (W.stats.flyovers || 0) + 1;
  }
  hotLoad() {  // phase 2: hover over the big pad, Duke jumps out
    const padX = Math.max(W.camX + 70, Math.min(W.camX + G.VW - 70, LIFEFLIGHT.pad));
    this.heli = { mode: 'hover', x: this.heli ? this.heli.x : W.camX + G.VW + 110, y: 176, z: this.heli ? this.heli.z : 60, tx: padX, face: -1, t: 0, wash: 0 };
    sfx('ace', { vol: 0.7 }); floatText('Hot load! Duke, GO GO GO!', padX, 176, 110, '#bfe0ff');
    this.dukes.push(spawn('duke', 'R')); sfx('duke', { vol: 0.7 }); W.stats.dukes = (W.stats.dukes || 0) + 1;
    if (W.director && W.director.backup) W.director.backup();
  }
  s_enter(dt) {  // runs in from the right, in front of the chopper
    const stopX = W.camX + G.VW * 0.7; this.walking = true;
    if (this.x > stopX) { this.x -= 90 * dt; return; }
    this.walking = false;
    if (!this.greeted) { this.greeted = true; floatText(LIFEFLIGHT_LINES.greet[0], this.x, this.y, TOP, '#ffffff'); sfx('roxy', { vol: 0.85 }); word('w_hotload', this.x, this.y, 96); }
    if (this.t > 2.4) { this.set('chase'); this.cd = 0.6; }
  }
  s_chase(dt) {
    const h = this.target(); if (!h) return;
    if (this.p2Next) { this.p2Next = false; return this.set('p2'); }
    const dx = h.x - this.x, dy = h.y - this.y, adx = Math.abs(dx);
    this.face = Math.sign(dx) || this.face;
    const want = this.cd > 0.4 ? 78 : 36, gx = h.x - Math.sign(dx || 1) * want;
    const mx = gx - this.x, my = dy, ml = Math.hypot(mx, my), sp = LIFEFLIGHT.speed[this.phase - 1];
    if (ml > 4) { this.x += mx / ml * sp * dt; this.y += my / ml * sp * 0.72 * dt; this.walking = true; } else this.walking = false;
    if (this.cd > 0) return;
    if (adx < 50 && Math.abs(dy) < 10) { this.set('swing'); this.hitDone = false; return; }
    if (this.radioCd <= 0 && this.phase === 1 && !this.heli) { this.set('radio'); this.hitDone = false; floatText(pick(LIFEFLIGHT_LINES.radio), this.x, this.y, TOP - 10, '#ffffff'); return; }
    if (this.zapCd <= 0 && adx > 50) { this.set('zap'); this.hitDone = false; floatText(pick(LIFEFLIGHT_LINES.zap), this.x, this.y, TOP - 10, '#bfe0ff'); return; }
    if (this.chargeCd <= 0 && adx > 70 && Math.abs(dy) < 14) { this.set('charge'); this.hitSet = new Set(); sfx('roxy', { vol: 0.6, rate: 1.2 }); return; }
    if (W.rnd() < 0.08) { this.set('taunt'); floatText(pick(LIFEFLIGHT_LINES.taunt), this.x, this.y, TOP - 10, '#ffffff'); this.cd = 1; }
  }
  s_swing(dt) {  // a paddle bonk
    if (!this.hitDone && this.t > 0.34) { this.hitDone = true; sfx('whoosh', { vol: 0.5 }); strike(this, { box: [0, 52], z: [14, 72], depth: 12, dmg: LIFEFLIGHT.swing, kb: 150, down: W.rnd() < 0.3, sfxName: 'punch1', wordName: 'w_smack', props: false }); }
    if (this.t > 0.72) { this.set('chase'); this.cd = this.phase === 2 ? 0.5 : 0.85; }
  }
  s_zap(dt) {  // rubs the paddles, "CLEAR!", slams them on the floor: a blue spark skims down her lane (jump it)
    if (this.t < 0.05) sfx('defib', { vol: 0.4, rate: 0.7 });
    if (!this.hitDone && this.t > 0.55) {
      this.hitDone = true; this.zapCd = this.phase === 2 ? 3.5 : 5.5; sfx('clear', { vol: 0.7 }); word('w_clear', this.x, this.y, 80); shake(2);
      const v = this.face * (this.phase === 2 ? 170 : 140);
      this.bolts.push({ x: this.x + this.face * 20, y: this.y, vx: v, t: 0, hit: new Set() });
      if (this.phase === 2) addShot({ kind: 'enemy', spr: 'p_zap0', x: this.x + this.face * 14, y: this.y, z: 40, vx: this.face * 210, vz: 0, grav: 0, owner: this, dmg: 4 * W.diff.dmg, dizzy: 0.9, life: 1.4 });
      W.stats.zaps = (W.stats.zaps || 0) + 1;
    }
    if (this.t > 0.95) { this.set('chase'); this.cd = 0.6; }
  }
  s_charge(dt) {  // a shoulder charge down the lane (a stretcher-crew sprint)
    if (this.t < 0.45) return;
    this.x += this.face * (this.phase === 2 ? 280 : 240) * dt;
    for (const h of W.heroes) {
      if (this.hitSet.has(h) || !h.hittable() || h.z > 22 || Math.abs(h.y - this.y) > 14 || Math.abs(h.x - (this.x + this.face * 20)) > 18) continue;
      this.hitSet.add(h); h.takeHit({ dmg: LIFEFLIGHT.charge, dir: this.face, kb: 180, down: true, from: this }); word('w_smack', h.x, h.y, 30); sfx('punch1');
    }
    const edge = this.face > 0 ? this.x > W.camX + G.VW - 30 : this.x < W.camX + 30;
    if (edge || this.t > 1.6) { this.x = Math.max(W.camX + 30, Math.min(W.camX + G.VW - 30, this.x)); this.set('chase'); this.cd = 0.8; this.chargeCd = this.phase === 2 ? 3 : 4.5; shake(2); }
  }
  s_radio(dt) {  // "AIR SUPPORT!": Ace's chopper buzzes across
    if (this.t < 0.05) sfx('radio', { vol: 0.7 });
    if (!this.hitDone && this.t > 0.7) { this.hitDone = true; this.radioCd = 9; this.callChopper(); }
    if (this.t > 1.0) { this.set('chase'); this.cd = 0.5; }
  }
  s_taunt(dt) { if (this.t > 0.9) this.set('chase'); }
  s_p2(dt) {
    if (this.t < 0.05) { floatText(pick(LIFEFLIGHT_LINES.p2), this.x, this.y, TOP, '#ff8a9a'); W.flash = 0.5; W.flashCol = '#a24dff'; sfx('roxy'); word('w_hotload', this.x, this.y, 96); this.hotLoad(); }
    if (this.t > 1.2) { this.set('chase'); this.cd = 0.3; this.zapCd = 1; }
  }
  s_defeat(dt) {  // off shift: out cold on the stretcher
    if (this.nap) this.nap.t += dt;
    if (this.t > 0.6 && Math.floor(this.t * 2) !== Math.floor((this.t - dt) * 2)) {
      addFx({ type: 'zzz', x: (this.nap ? this.nap.x : this.x) + 6, y: this.y, z: 30, dur: 1.4 });
      addFx({ type: 'zzz', x: (this.nap ? this.nap.x : this.x) + 26, y: this.y, z: 26, dur: 1.4 });
    }
  }
  pose() {
    switch (this.st) {
      case 'enter': return this.walking ? ['run', Math.floor(W.t * 9)] : ['radio', Math.floor(this.t * 4)];
      case 'chase': return this.hurtT > 0 ? ['hurt', 0] : this.walking ? ['walk', Math.floor(W.t * 8)] : ['idle', Math.floor(W.t * 3)];
      case 'swing': return ['atk', this.t > 0.32 ? 1 : 0];
      case 'zap': return ['zap', this.t > 0.5 ? 1 : 0];
      case 'charge': return this.t < 0.45 ? ['charge', 0] : ['run', Math.floor(this.t * 10)];
      case 'radio': case 'taunt': case 'p2': return ['radio', Math.floor(this.t * 5)];
      case 'fall': return ['fall', 0];
      case 'down': return ['down', 0];
      case 'getup': return ['getup', 0];
      case 'defeat': return this.t > 0.5 ? ['sleep', 0] : ['dizzy', Math.floor(this.t * 4)];
    }
    return ['idle', 0];
  }
  drawShadow() {  // floor layer: her shadow, the zap bolts, the rotor-wash ring (+ its warning ring)
    const X = this.x - W.camX, oy = offY();
    if (!(this.st === 'defeat' && this.t > 0.5)) ellipse(X, this.y + oy, 18, 3.5, '#000', 0.32);
    for (const s of this.bolts) { ellipse(s.x - W.camX, s.y + oy, 12, 3, '#3aa8ff', 0.7); spr('p_zap' + (Math.floor(s.t * 10) % 2), s.x - W.camX - 11, s.y + oy - 10); }
    const H = this.heli;
    if (H) {
      const hx = H.x - W.camX, hy = H.y + oy, R = LIFEFLIGHT.washR;
      ellipse(hx, hy, 60 * Math.max(0.4, 1 - H.z / 160), 9, '#000', 0.3);
      if (H.wash) { ellipse(hx, hy, R, R / 2.6, '#bfe0ff', 0.12 + Math.sin(W.t * 30) * 0.04); ring(hx, hy, R, R / 2.6, '#3aa8ff', 2, 0.7); ring(hx, hy, R * 0.6, R / 4.3, '#a24dff', 1, 0.5); }
      else if (H.warn && Math.floor(W.t * 8) % 2) ring(hx, hy, R, R / 2.6, '#ff3a4a', 1, 0.8);
    }
  }
  draw() {
    const X = this.x - W.camX, oy = offY();
    if (this.st === 'defeat' && this.t > 0.5 && this.nap) {  // the stretcher: Duke at the foot, Roxy on top, both out cold
      const nx = this.nap.x - W.camX, ny = this.nap.y + oy;
      spr('stretcher', nx - 28, ny - 22);
      this.dukeNap.x = this.nap.x + 10; this.dukeNap.y = this.nap.y; this.dukeNap.drawSprite('sleep', 0, { dy: -14 });
      this.x = this.nap.x - 8; this.y = this.nap.y; this.face = -1; this.drawSprite('sleep', 0, { dy: -18 });
      this.drawHeli(); return;
    }
    if (this.phase === 2 && this.st !== 'defeat') ellipse(X, this.y + oy, 20, 4, '#a24dff', 0.4 + Math.sin(W.t * 20) * 0.08);
    const [n, i] = this.pose(); this.drawSprite(n, i);
    if (((this.st === 'swing' && this.t < 0.32) || (this.st === 'zap' && this.t < 0.55) || (this.st === 'charge' && this.t < 0.45)) && Math.floor(this.t * 12) % 2) text('!', X + this.face * 6, this.y + oy - this.z - 100, { col: '#ff5a3a', align: 'center' });
    this.drawHeli();
  }
  drawHeli() {
    const H = this.heli; if (!H) return;
    const landed = H.mode === 'land' && H.z <= 0 && H.t > 2.5;
    const name = landed ? 'chopper_nap' : 'chopper' + (Math.floor(W.t * 16) % 2);
    spr(name, H.x - W.camX - 75, H.y + offY() - H.z - 62, { flip: H.face < 0 });
  }
  drawIcon(x, y) { spr('face_roxy', x, y, { scale: 0.75 }); }
  light(L) {
    if (this.st !== 'defeat') L.push({ x: this.x, y: this.y - 40, r: 30, col: '#bfe0ff', a: 0.35 });
    for (const s of this.bolts) L.push({ x: s.x, y: s.y - 4, r: 26, col: '#3aa8ff', a: 0.9 });
    const H = this.heli;
    if (H) {  // the chopper's searchlight pool on the floor + its red / blue strobes
      L.push({ x: H.x, y: H.y, r: 56, ry: 18, col: '#e8f0ff', a: H.mode === 'land' && H.z <= 0 ? 0.35 : 0.7, floor: true });
      L.push({ x: H.x - 60 * (H.face || 1), y: H.y - H.z - 40, r: 18, col: '#ff3a4a', a: 0.9, blink: 0.9, ph: 0 });
      L.push({ x: H.x + 50 * (H.face || 1), y: H.y - H.z - 40, r: 18, col: '#3aa8ff', a: 0.9, blink: 0.9, ph: 0.5 });
    }
  }
}
