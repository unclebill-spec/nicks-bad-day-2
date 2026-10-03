// v0.5 Floor 4 bosses.
// MAGNA-SCAN 3000, the MRI magnet (boss, ~2.6x a nurse's height, ~6x her width). It never moves; it fights with its field:
//   MAGNET ON  -> pulls the nurses in (walk away to resist) and yanks every metal thing (IV poles, crutches, bedpans, carts,
//                 wheelchairs, IV stands, apron racks) across the floor into itself; whatever flies at it hits you on the way
//   QUENCH     -> after every pull it vents helium and its coil glows red: THE WEAK POINT (full damage, otherwise 20%)
//   KNOCK      -> its famous banging: sound waves roll along the floor lanes (jump them or change lanes)
//   TABLE      -> the patient table shoots out along your lane (the lane flashes red first; jump or step aside)
//   phase 2 (half health, SUPERCONDUCTING): stronger pull (run to resist) that ends in a REPEL blast, double tables,
//   more waves, and it pages patients in ("NEXT PATIENT, PLEASE!"). Defeated, it ramps down and says goodnight.
// LEAD-APRON LOU (mini-boss, ~2x a nurse's height): a gentle-giant ex-linebacker in three lead aprons. Linebacker charge
// (then he's winded = his weak moment), a ground-pound stomp ring, and X-ray film frisbees. Super armor unless winded.
import { G, text, rect, ellipse, frame, anim } from './gfx.js';
import { Y_MIN, Y_MAX } from './data.js';
import { W, offY, addShot, addFx, floatText, shake, spark, word, addScore, bumpProps, smashProp, dropItem, MRI_Y, mriX } from './world.js';
import { Actor, strike, clampY } from './actor.js';
import { sfx } from './sound.js';

const rr = (a, b) => a + W.rnd() * (b - a);
const liveHeroes = () => W.heroes.filter((h) => h.alive && !['dead', 'out', 'respawn'].includes(h.st));

export class MRI extends Actor {
  constructor(lock) {
    super('mri', mriX(lock), MRI_Y);
    this.isBoss = true; this.isMRI = true; this.name = 'MAGNA-SCAN 3000'; this.big = true; this.w = 150; this.h = 140; this.depthAny = true;
    this.maxHp = this.hp = Math.round(560 * W.diff.hp * (W.heroes.length > 1 ? 1.35 : 1));
    // face 1 = drawn unflipped (the machine faces the player by design)
    this.face = 1; this.phase = 1; this.set('enter'); this.cd = 1.4; this.shown = 0; this.step = 0; this.callCd = 9; this.p2label = 'SUPERCONDUCTING!';
  }
  get front() { return this.x - 74; }  // the face of the machine (heroes can't get past it)
  hittable() { return !['enter', 'defeat', 'super'].includes(this.st); }
  grabbable() { return false; }
  weak() { return this.st === 'vent'; }
  hint() { return this.st === 'vent' ? 'HIT THE HOT COIL!' : this.st === 'pull' ? 'WALK AWAY! DROP THE METAL!' : this.st === 'tableWarn' ? 'JUMP!' : null; }
  takeHit({ dmg, dir, from, force }) {
    if (!this.hittable() && !force) return;
    const weak = this.weak() || force, d = weak ? dmg : dmg * 0.2;
    this.hp -= d; this.flash = 0.1; if (from) addScore(from, d * 10);
    if (!weak && W.rnd() < 0.35) floatText('CLANK!', this.front + 6, this.y - 10, 60, '#c8ccd6');
    if (weak) { this.hurtT = 0.2; spark(this.front + 20, this.y - 10, 60, 'bigspark'); }
    if (this.hp <= 0) { this.hp = 0; this.die(from); return; }
    if (this.phase === 1 && this.hp < this.maxHp * 0.5) { this.phase = 2; this.set('super'); }
  }
  die(from) {
    this.set('defeat'); W.stop = 0.4; shake(8); sfx('powerdown'); sfx('explosion', { vol: 0.6 }); W.flash = 0.6; W.flashCol = '#bfeaff';
    if (from && from.isHero) addScore(from, 12000);
    floatText('SCAN COMPLETE. HAVE A NICE DAY.', this.front, this.y - 40, 64, '#bfeaff');
    for (const e of W.enemies) if (e.alive && e.st !== 'dead') e.takeHit({ dmg: 999, dir: -1, kb: 120, down: true, force: true });
  }
  target() { const hs = liveHeroes(); return hs.length ? hs[Math.floor(W.t * 0.5) % hs.length] : null; }
  update(dt) {
    this.t += dt; this.flash = Math.max(0, this.flash - dt); this.cd -= dt; this.callCd -= dt; this.hurtT = Math.max(0, (this.hurtT || 0) - dt);
    this.shown = Math.min(1, this.shown + dt * 0.7);
    const fn = this['s_' + this.st]; if (fn) fn.call(this, dt);
    for (const s of W.shots) if (s.kind === 'yank' && s.x >= this.front - 4) { s.life = 0; sfx('clunk', { vol: 0.7 }); word('w_clunk', this.front, s.y, 40); }
    // the machine is solid across the whole floor depth
    for (const h of W.heroes) if (h.alive && h.x > this.front - 10) h.x = this.front - 10;
    for (const e of W.enemies) if (e.alive && e.x > this.front - 10 && e.st !== 'dead') e.x = this.front - 10;
  }
  s_enter() {
    if (this.t < 0.05) { sfx('hum', { vol: 0.7 }); floatText('BOOTING UP...', this.front + 30, this.y - 40, 64, '#bfeaff'); }
    if (this.t > 0.9 && !this.greeted) { this.greeted = true; sfx('mri_voice', { vol: 0.8 }); floatText('PLEASE HOLD STILL. SCANNING... EVERYTHING!', this.front, this.y - 40, 70, '#ffffff'); }
    if (this.t > 2.4) { this.set('idle'); this.cd = 0.6; }
  }
  s_super() {
    if (this.t < 0.05) { word('w_superc', this.front + 20, this.y - 40, 90); W.flash = 0.6; W.flashCol = '#a24dff'; sfx('zap'); sfx('hum', { vol: 0.8, rate: 1.3 }); shake(5); }
    if (Math.floor(this.t * 20) % 2 === 0) addFx({ type: 'spark', kind: 'bluespark', x: this.x + rr(-60, 60), y: this.y - 2, z: rr(20, 130), dur: 0.15 });
    if (this.t > 1.4) { this.set('idle'); this.cd = 0.4; }
  }
  s_idle() {
    if (this.cd > 0) return;
    const minions = W.enemies.filter((e) => e.alive && e.st !== 'dead').length;
    if (this.phase === 2 && this.callCd <= 0 && minions < 2) { this.callCd = 15; floatText('NEXT PATIENT, PLEASE!', this.front, this.y - 40, 64, '#ffffff'); sfx('page', { vol: 0.6 }); W.director.backup(); this.cd = 0.8; return; }
    // readable rotation: PULL (then QUENCH: the weak point) -> KNOCK -> TABLE -> PULL ...; phase 2 doubles up
    const seq = this.phase === 1 ? ['pullWarn', 'bang', 'tableWarn'] : ['pullWarn', 'tableWarn', 'bang', 'tableWarn'];
    const next = seq[this.step++ % seq.length];
    this.set(next); this.lanes = 0; this.waves = 0;
    if (next === 'tableWarn') { const h = this.target(); this.lane = h ? clampY(h.y) : rr(Y_MIN + 10, Y_MAX - 10); sfx('beep', { vol: 0.6, rate: 0.7 }); }
  }
  // ---- MAGNET ON
  s_pullWarn() {
    if (this.t < 0.05) { word('w_magnet', this.front + 10, this.y - 30, 70); sfx('hum', { vol: 0.9 }); }
    if (this.t > (this.phase === 2 ? 0.6 : 0.85)) { this.set('pull'); this.yanked = new Set(); }
  }
  s_pull(dt) {
    const P2 = this.phase === 2, dur = P2 ? 3.0 : 2.5, pull = P2 ? 92 : 50;
    if (Math.floor(this.t * 10) % 3 === 0) sfx('hum', { vol: 0.35, gap: 0.9 });
    for (const h of liveHeroes()) {
      if (h.st === 'ride' || h.z > 40) continue;
      h.x += pull * dt;
      if (h.carry && h.carry.def.metal) {  // v0.6: a metal prop held overhead gets torn away too (and the magnet reels it in)
        floatText('HEY! THAT\'S MINE!', h.x, h.y, 70, '#bfeaff'); h.releaseProp(false, true); sfx('whoosh', { vol: 0.5 });
      }
      if (h.weapon && h.weapon.w.metal) {  // your IV pole / crutch / bedpan gets yanked right out of your hands
        const w = h.weapon; h.weapon = null;
        addShot({ kind: 'yank', spr: w.w.spr, x: h.x, y: h.y, z: 30, vx: 300, life: 2, owner: this });
        floatText(['MY ' + w.w.name + '!', 'HEY!', 'IT TOOK MY ' + w.w.name + '!'][Math.floor(W.rnd() * 3)], h.x, h.y, 64, '#bfeaff'); sfx('whoosh', { vol: 0.5 });
      }
      if (h.x >= this.front - 12 && (!h.zapT || W.t > h.zapT)) {  // stuck to the magnet: ZAP, and you're thrown clear
        h.zapT = W.t + 0.8; h.takeHit({ dmg: 6, dir: -1, kb: 190, down: true, from: this }); sfx('zap', { vol: 0.6 }); word('w_clunk', h.x, h.y, 30);
      }
    }
    for (const it of W.items) {  // metal weapons on the floor slide in and stick
      if (!it.weapon || !it.w.metal || it.gone) continue;
      it.x += (P2 ? 230 : 170) * dt; it.z = Math.max(it.z, 6);
      if (it.x >= this.front - 4) { it.gone = true; sfx('clunk', { vol: 0.7 }); word('w_clunk', this.front, it.y, 30); }
    }
    for (const p of W.props) {  // metal props roll in, plowing anyone in the way, and get crushed on the magnet
      if (p.st >= 2 || !p.def.metal || p.rider) continue;
      if (!p.magnet) { p.magnet = true; p.hitSet = new Set(); p.kicker = null; }
      p.vx = Math.min(P2 ? 360 : 300, Math.max(p.vx, 0) + 420 * dt); p.nudge = false;
      if (p.x + p.def.w / 2 >= this.front - 2) { p.magnet = false; smashProp(p); sfx('clunk', { vol: 0.8 }); word('w_clunk', this.front - 6, p.y, 26); continue; }
      if (p.vx > 110) for (const h of liveHeroes()) {
        if (p.hitSet.has(h) || h.z > 26 || Math.abs(h.y - p.y) > 12 || Math.abs(h.x - p.x) > p.def.w / 2 + 6) continue;
        p.hitSet.add(h); h.takeHit({ dmg: 8, dir: 1, kb: 120, down: true, from: this }); spark(h.x, h.y, 26, 'bigspark'); sfx('heavy', { vol: 0.7 });
      }
    }
    if (this.t > dur) {
      for (const p of W.props) if (p.magnet) { p.magnet = false; p.vx *= 0.3; }
      if (P2) { this.set('repel'); return; }
      this.toVent();
    }
  }
  s_repel() {  // phase 2: the field flips and blasts everyone back
    if (this.t < 0.05) { sfx('zap', { vol: 0.8 }); shake(5); W.flash = 0.3; W.flashCol = '#a24dff';
      addShot({ kind: 'shock', x: this.front, y: (Y_MIN + Y_MAX) / 2, z: 0, r: 10, grow: 420, rmax: 260, owner: this, dmg: 6, life: 0.7, col: '#d88aff', hostile: true }); }
    if (this.t > 0.5) this.toVent();
  }
  toVent() { this.set('vent'); sfx('quench', { vol: 0.9 }); word('w_quench', this.front + 40, this.y - 50, 40); if (!this.told) { this.told = true; floatText('Overheating! Do NOT hit the coil!', this.front, this.y - 40, 60, '#ffd8a0'); } }
  s_vent() {
    if (Math.floor(this.t * 12) % 3 === 0) addFx({ type: 'smoke', x: this.x + 36 + rr(-8, 8), y: this.y, z: 140 + rr(0, 10), dur: 0.7 });
    if (this.t > (this.phase === 2 ? 2.1 : 2.8)) { this.set('idle'); this.cd = this.phase === 2 ? 0.5 : 0.9; }
  }
  // ---- KNOCK: sound waves along the floor lanes
  s_bang(dt) {
    const n = this.phase === 2 ? 5 : 3, gap = this.phase === 2 ? 0.3 : 0.42;
    if (this.t <= 0.02) this.waves = 0;
    if (this.waves < n && this.t > 0.3 + this.waves * gap) {
      this.waves++; sfx('bang', { vol: 0.9 }); shake(3); word('w_knock', this.front + 8, this.y - 60 + (this.waves % 2) * 20, 40);
      const h = this.target(), y = this.waves === 1 && h ? clampY(h.y) : rr(Y_MIN + 6, Y_MAX - 6);
      addShot({ kind: 'enemy', spr: this.phase === 2 ? 'mri_wave1' : 'mri_wave0', x: this.front - 6, y, z: 2, vx: this.phase === 2 ? -210 : -170, vz: 0, grav: 0, owner: this, dmg: 7, life: 3.2, roll: true, glow: this.phase === 2 ? '#d88aff' : '#8ad8ff' });
    }
    if (this.t > 0.6 + n * gap) { this.set('idle'); this.cd = 0.7; }
  }
  // ---- TABLE: the lane flashes red, then the patient table shoots out along it
  s_tableWarn() { if (this.t > (this.phase === 2 ? 0.55 : 0.8)) { this.set('table'); } }
  s_table() {
    if (this.t < 0.02) {
      sfx('table', { vol: 0.9 }); shake(2);
      addShot({ kind: 'enemy', spr: 'mri_table', x: this.front - 20, y: this.lane, z: 6, vx: -340, vz: 0, grav: 0, owner: this, dmg: 12, life: 3, roll: true, glow: '#3aa8ff' });
    }
    if (this.t > 0.7) { this.lanes++; if (this.phase === 2 && this.lanes < 2) { const h = this.target(); this.lane = h ? clampY(h.y + (W.rnd() < 0.5 ? -20 : 20)) : this.lane; this.set('tableWarn'); this.t = 0.2; } else { this.set('idle'); this.cd = 0.6; } }
  }
  s_defeat() { if (Math.floor(this.t * 6) % 3 === 0) addFx({ type: 'smoke', x: this.x + rr(-50, 50), y: this.y, z: rr(60, 140), dur: 0.8 }); if (this.t > 0.8 && Math.floor(this.t * 2) !== Math.floor((this.t - 1 / 60) * 2)) addFx({ type: 'zzz', x: this.x, y: this.y, z: 150, dur: 1.4 }); }
  pose() {
    switch (this.st) {
      case 'pull': case 'pullWarn': return ['pull', Math.floor(W.t * (this.st === 'pull' ? 12 : 4))];
      case 'vent': return ['vent', Math.floor(W.t * 6)];
      case 'defeat': return ['dead', 0];
      case 'enter': return this.t < 0.9 ? ['dead', 0] : ['idle', Math.floor(W.t * 8)];
    }
    return ['idle', Math.floor(W.t * 3)];
  }
  // a light source for the dark floor (src/world.js drawLighting)
  light(L) {
    if (this.st === 'defeat') return;
    const col = this.st === 'vent' ? '#ff6a3a' : this.phase === 2 ? '#a24dff' : '#3aa8ff', on = this.st !== 'enter' || this.t > 0.9;
    if (on) { L.push({ x: this.x, y: this.y - 72, r: this.st === 'pull' ? 78 : 62, col, a: 1 }); L.push({ x: this.x - 40, y: this.y, r: 110, ry: 30, col, a: 0.7, floor: true }); }
  }
  drawShadow() {}
  draw() {
    const [n, i] = this.pose(), X = Math.round(this.x - W.camX + (this.st === 'bang' && Math.floor(W.t * 30) % 2 ? 1 : 0)), Y = Math.round(this.y + offY());
    // telegraph: the lane the table will come down flashes red
    if (this.st === 'tableWarn' && Math.floor(W.t * 10) % 2) { rect(W.camX - W.camX, this.lane + offY() - 5, this.front - W.camX, 10, '#ff3a4a', 0.35); rect(0, this.lane + offY() - 1, this.front - W.camX, 2, '#ffd0d0', 0.7); }
    if (this.st === 'pull') for (let k = 0; k < 4; k++) { const r = ((W.t * 90 + k * 30) % 120); const c = G.ctx; c.globalAlpha = 0.35 * (r / 120); c.strokeStyle = this.phase === 2 ? '#d88aff' : '#bfeaff'; c.beginPath(); c.ellipse(X, Y - 72, 160 - r, (160 - r) * 0.7, 0, 0, Math.PI * 2); c.stroke(); c.globalAlpha = 1; }
    this.drawSprite(n, i);
    // phase 2: violet glow around the bore
    if (this.phase === 2 && this.st !== 'defeat') ellipse(X, Y - 72, 40 + Math.sin(W.t * 18) * 2, 36, '#a24dff', 0.18);
    this.drawFace(X - 92 + 2, Y - 154);
  }
  // the LCD face above the bore: calm eyes that track you, angry when pulling, dizzy when venting, asleep when beaten
  drawFace(L, T) {
    const x0 = L + 53, y0 = T + 17, w = 74, h = 18, cx = x0 + w / 2, cy = y0 + h / 2;
    const col = this.st === 'defeat' ? '#2a3450' : this.phase === 2 ? '#d88aff' : this.st === 'vent' ? '#ffb03a' : '#7ad8ff';
    const hurt = this.hurtT > 0 || this.flash > 0.05;
    if (this.st === 'enter' && this.t < 0.9) { if (Math.floor(this.t * 6) % 2) text('...', cx, cy - 4, { col: '#3aa8ff', align: 'center', shadow: null }); return; }
    for (const s of [-1, 1]) {
      const ex = cx + s * 16;
      if (this.st === 'defeat') { rect(ex - 5, cy, 10, 2, col); continue; }
      if (hurt) { rect(ex - 4, cy - 4, 2, 2, col); rect(ex - 2, cy - 2, 2, 2, col); rect(ex, cy, 2, 2, col); rect(ex - 2, cy + 2, 2, 2, col); rect(ex - 4, cy + 4, 2, 2, col); continue; }
      if (this.st === 'vent') { for (let k = -3; k <= 3; k += 2) { rect(ex + k - 1, cy + k - 1, 2, 2, col); rect(ex - k - 1, cy + k - 1, 2, 2, col); } continue; }
      rect(ex - 5, cy - 5, 10, 10, col);
      const h0 = this.target(), look = h0 ? Math.max(-2, Math.min(2, Math.round((h0.x - this.x) / 80))) : 0;
      rect(ex - 2 + look, cy - 2, 4, 4, '#0c1430');
      if (this.st === 'pull' || this.st === 'pullWarn' || this.phase === 2) { rect(ex - 6, cy - 7 - (s < 0 ? 0 : 2), 12, 2, '#ff5a6a'); rect(ex + s * 3, cy - 9, 4, 2, '#ff5a6a'); }
    }
    if (this.st === 'vent') rect(cx + 26, y0 + 2, 3, 5, '#8ad8ff');  // sweat drop
  }
  drawIcon(x, y) { frame('mri', anim('mri', 'idle').s, x + 16, y + 26, { scale: 0.16 }); }
}

// ------------------------------------------------------------------ Lead-Apron Lou (mini-boss)
export class Lou extends Actor {
  constructor(x, y) {
    super('lou', x, y);
    this.isBoss = true; this.mini = true; this.name = 'LEAD-APRON LOU'; this.big = true; this.w = 46; this.h = 126; this.p2label = 'FOURTH QUARTER!';
    this.maxHp = this.hp = Math.round(260 * W.diff.hp * (W.heroes.length > 1 ? 1.35 : 1)); this.stompCd = 0;
    this.face = -1; this.phase = 1; this.set('enter'); this.cd = 1; this.shown = 0; this.called = false;
  }
  hittable() { return !['enter', 'defeat', 'down'].includes(this.st); }
  grabbable() { return false; }
  hint() { return this.st === 'tired' ? 'HE IS WINDED! HIT HIM!' : this.st === 'set' ? 'GET OUT OF HIS LANE!' : null; }
  takeHit({ dmg, dir, from, force, down }) {
    if (!this.hittable() && !force) return;
    const weak = this.st === 'tired' || force, d = weak ? dmg : dmg * 0.5;
    this.hp -= d; this.flash = 0.1; if (from) addScore(from, d * 10);
    if (!weak && W.rnd() < 0.3) floatText(['Is that it?', 'Ha! Tickles!', 'Lead apron, baby!'][Math.floor(W.rnd() * 3)], this.x, this.y, 116, '#ffffff');
    if (this.hp <= 0) { this.hp = 0; this.die(from, dir); return; }
    if (weak && down && this.st === 'tired') { this.set('hurt'); this.vx = (dir || 1) * 60; }
    if (this.phase === 1 && this.hp < this.maxHp * 0.5) { this.phase = 2; floatText('FOURTH QUARTER! HIKE!', this.x, this.y, 120, '#ffe84a'); word('w_hike', this.x, this.y, 90); sfx('lou', { vol: 0.8 }); if (!this.called) { this.called = true; W.director.backup(); } }
  }
  die(from, dir) {
    this.set('defeat'); this.vx = (dir || 1) * 80; W.stop = 0.3; shake(7); sfx('stomp'); W.flash = 0.4; W.flashCol = '#ffffff';
    if (from && from.isHero) addScore(from, 5000);
    floatText('Good game, nurses... nap time... zzz', this.x, this.y, 120, '#ffffff');
    dropItem('snacks', this.x - 10, this.y + 4); dropItem('star', this.x + 12, this.y + 6);
  }
  target() { const hs = liveHeroes(); return hs.length ? hs.reduce((a, b) => (Math.abs(a.x - this.x) < Math.abs(b.x - this.x) ? a : b)) : null; }
  update(dt) {
    this.t += dt; this.flash = Math.max(0, this.flash - dt); this.cd -= dt; this.stompCd -= dt; this.shown = Math.min(1, this.shown + dt * 0.8);
    const fn = this['s_' + this.st]; if (fn) fn.call(this, dt);
    this.y = clampY(this.y); this.x = Math.max(W.camX + 24, Math.min(W.camX + G.VW - 24, this.x));
    if (!['defeat', 'charge'].includes(this.st)) for (const h of W.heroes) {  // he's big and solid
      if (!h.alive || h.z > 30 || ['dead', 'out', 'fall', 'down'].includes(h.st)) continue;
      const dx = h.x - this.x; if (Math.abs(dx) < 24 && Math.abs(h.y - this.y) < 10) h.x = this.x + (Math.sign(dx) || 1) * 24;
    }
  }
  s_enter(dt) {
    const stopX = W.camX + G.VW * 0.74;
    if (this.t < 0.05) { floatText('LEAD-APRON LOU!', W.camX + G.VW / 2, 150, 80, '#ffe84a'); sfx('stomp', { vol: 0.6 }); }
    if (this.x > stopX) { this.x -= 70 * dt; this.walking = true; return; }
    this.walking = false;
    if (!this.greeted) { this.greeted = true; sfx('lou', { vol: 0.8 }); word('w_hike', this.x, this.y, 90); floatText('Hut, hut... HIKE! Nobody gets past ol\' Lou!', this.x, this.y, 120, '#ffffff'); }
    if (this.t > 2.4) this.set('idle');
  }
  s_idle(dt) {
    const h = this.target(); if (!h) return;
    this.face = Math.sign(h.x - this.x) || this.face;
    const dx = h.x - this.x, dy = h.y - this.y, adx = Math.abs(dx);
    const want = 70;
    if (adx > want + 10 || Math.abs(dy) > 4) { this.x += Math.sign(dx) * Math.min(adx - want, 46 * dt) * (adx > want ? 1 : 0); this.y += Math.sign(dy) * Math.min(Math.abs(dy), 36 * dt); this.walking = true; } else this.walking = false;
    if (this.cd > 0) return;
    if (adx < 60 && Math.abs(dy) < 18 && this.stompCd <= 0) { this.stompCd = this.phase === 2 ? 2.6 : 3.4; return this.set('stomp'); }
    const r = W.rnd();
    if (r < (this.phase === 2 ? 0.55 : 0.45)) { this.set('set'); this.face = Math.sign(dx) || this.face; this.lane = this.y; sfx('lou', { vol: 0.5, rate: 1.2 }); return; }
    this.set('throw'); this.thrown = 0;
  }
  s_set() {  // three-point stance: the telegraph for the charge
    if (Math.floor(this.t * 14) % 3 === 0) addFx({ type: 'dust', x: this.x - this.face * 14, y: this.y, dur: 0.3 });
    if (this.t > (this.phase === 2 ? 0.55 : 0.8)) { this.set('charge'); this.vx = this.face * (this.phase === 2 ? 300 : 250); this.hitSet = new Set(); word('w_hike', this.x, this.y, 80); }
  }
  s_charge(dt) {
    this.x += this.vx * dt;
    strike(this, { box: [-16, 34], z: [0, 90], depth: 14, dmg: 14, kb: 210, down: true, sfxName: 'heavy', once: this.hitSet, wordName: 'w_wham', props: false });
    bumpProps(this, 20, Math.sign(this.vx), null, this.hitSet, 22);
    if (Math.floor(this.t * 14) % 2 === 0) addFx({ type: 'dust', x: this.x - this.face * 20, y: this.y, dur: 0.3 });
    const L = W.camX + 30, R = W.camX + G.VW - 30;
    if ((this.vx < 0 && this.x < L) || (this.vx > 0 && this.x > R)) {
      this.x = Math.max(L, Math.min(R, this.x)); shake(5); sfx('heavy'); sfx('stomp', { vol: 0.5 });
      this.set('tired'); floatText(['*huff* *puff*', 'Need... a... water break...', 'Ow, my knees.'][Math.floor(W.rnd() * 3)], this.x, this.y, 116, '#ffffff');
    }
  }
  s_tired() { if (this.t > (this.phase === 2 ? 1.6 : 2.2)) { this.set('idle'); this.cd = 0.6; } }
  s_hurt(dt) { this.x += this.vx * dt; this.vx *= Math.exp(-dt * 6); if (this.t > 0.35) { this.set('tired'); this.t = 1.0; } }
  s_stomp() {
    if (!this.slam && this.t > 0.5) {
      this.slam = true; sfx('stomp'); shake(6); word('w_wham', this.x, this.y, 30);
      addShot({ kind: 'shock', x: this.x, y: this.y, z: 0, r: 8, grow: 260, rmax: this.phase === 2 ? 120 : 92, owner: this, dmg: 9, life: 0.5, col: '#ffe84a', hostile: true });
      for (let i = 0; i < 6; i++) addFx({ type: 'dust', x: this.x + rr(-40, 40), y: this.y + rr(-6, 6), dur: 0.4 });
    }
    if (this.t > 1.0) { this.slam = false; this.set('idle'); this.cd = this.phase === 2 ? 0.6 : 1.0; }
  }
  s_throw() {  // X-ray film frisbees (two in phase 2)
    const n = this.phase === 2 ? 2 : 1;
    if (this.thrown < n && this.t > 0.4 + this.thrown * 0.35) {
      this.thrown++; const h = this.target(); this.face = h ? Math.sign(h.x - this.x) || this.face : this.face; sfx('film', { vol: 0.8 });
      addShot({ kind: 'enemy', spr: 'p_film', x: this.x + this.face * 20, y: h ? clampY(h.y + (this.thrown - 1) * 14) : this.y, z: 40, vx: this.face * 210, vz: 0, grav: 0, owner: this, dmg: 8, spin: 14, life: 2.4, glow: '#3aa8ff' });
    }
    if (this.t > 0.7 + n * 0.35) { this.set('idle'); this.cd = 0.9; }
  }
  s_defeat(dt) { this.x += (this.vx || 0) * dt; this.vx = (this.vx || 0) * Math.exp(-dt * 4); if (this.t > 0.8 && Math.floor(this.t * 2) !== Math.floor((this.t - dt) * 2)) addFx({ type: 'zzz', x: this.x + 14, y: this.y, z: 40, dur: 1.4 }); }
  pose() {
    switch (this.st) {
      case 'enter': case 'idle': return this.walking ? ['walk', Math.floor(W.t * 6)] : ['idle', Math.floor(W.t * 2)];
      case 'set': return ['charge', 0];
      case 'charge': return ['charge', Math.floor(W.t * 12)];
      case 'tired': return ['tired', Math.floor(W.t * 3)];
      case 'hurt': return ['hurt', 0];
      case 'stomp': return ['stomp', this.t < 0.5 ? 0 : 1];
      case 'throw': return ['throw', this.t < 0.4 ? 0 : 1];
      case 'defeat': return this.t < 0.5 ? ['fall', 0] : ['sleep', 0];
    }
    return ['idle', 0];
  }
  drawShadow() { const X = this.x - W.camX, Y = this.y + offY(); ellipse(X, Y + 1, 26, 5, '#000', 0.32); }
  draw() {
    const [n, i] = this.pose();
    if (this.st === 'set' && Math.floor(W.t * 10) % 2) { const X = this.x - W.camX; rect(this.face > 0 ? X : 0, this.y + offY() - 5, this.face > 0 ? G.VW - X : X, 10, '#ffe84a', 0.22); }
    this.drawSprite(n, i);
    if (this.st === 'tired' && Math.floor(W.t * 8) % 2) text('!', this.x - W.camX, this.y + offY() - 142, { col: '#ffe84a', align: 'center' });
  }
}
