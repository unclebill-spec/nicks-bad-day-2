// The four nurses: movement, combos, jump kick, dash attack, grab / knee / throw, back attack, weapons, the
// per-hero desperation special (costs a little health) and the Code Blue super (meter).
import { G, frame, spr, sprSize, ellipse, text } from './gfx.js';
import { HEROES, ATTACKS, WEAPONS, Y_MIN, Y_MAX } from './data.js';
import { W, offY, dropItem, addShot, addFx, word, floatText, shake, spark, addScore } from './world.js';
import { Actor, strike, clampY } from './actor.js';
import { sfx } from './sound.js';

export class Hero extends Actor {
  constructor(id, slot, x, y) {
    super(id, x, y);
    this.isHero = true; this.id = id; this.slot = slot; this.d = HEROES[id];
    this.maxHp = this.hp = this.d.hp; this.lives = 3; this.score = 0; this.meter = 0; this.combo = 0; this.comboT = 0; this.maxCombo = 0; this.kos = 0;
    this.weapon = null; this.held = null; this.step = 0; this.gap = 9; this.buf = null; this.bufT = 0; this.speedT = 0; this.mash = 0; this.respawnT = 0; this.ctl = null;
    this.h = id === 'kim' || id === 'will' ? 48 : 54; this.w = id === 'will' ? 18 : 14;
  }
  hittable() { return this.inv <= 0 && !['fall', 'down', 'getup', 'dead', 'super', 'respawn', 'enter', 'win', 'out'].includes(this.st); }
  canAct() { return ['idle', 'walk', 'run'].includes(this.st); }
  get spd() { return this.speedT > 0 ? 1.4 : 1; }

  takeHit({ dmg, dir, kb, stun, down, dizzy, from }) {
    if (!this.hittable()) return;
    if (this.held) this.release();
    if (this.grabber) this.grabber = null;
    const d = dmg * W.diff.dmg;
    this.hp -= d; this.flash = 0.12; this.meter = Math.min(100, this.meter + d * 0.35); this.combo = 0;
    sfx('hurt', { vol: 0.55 });
    if (this.hp <= 0) { this.hp = 0; this.knock(dir, 150, 220); floatText(['OUCH!', 'MY BACK!', 'NOT TODAY!'][Math.floor(W.rnd() * 3)], this.x, this.y, 64, '#ff8ac0'); return; }
    if (dizzy) { this.set('dizzy'); this.stun = dizzy; return; }
    if (down) this.knock(dir, kb || 140, 180);
    else { this.set('hurt'); this.stun = stun || 0.3; this.vx = dir * (kb || 30); }
  }
  release() { if (this.held) { const e = this.held; this.held = null; if (e.st === 'held') { e.set('hurt'); e.stun = 0.2; e.vx = this.face * 40; } } }

  update(dt, inp) {
    this.t += dt; this.inv = Math.max(0, this.inv - dt); this.flash = Math.max(0, this.flash - dt); this.speedT = Math.max(0, this.speedT - dt);
    this.comboT -= dt; if (this.comboT <= 0) this.combo = 0;
    this.gap += dt;
    if (this.st === 'out') return;
    // back-attack buffer: attack + jump within 3 frames
    let atk = inp.prs.atk, jmp = inp.prs.jmp;
    if (this.buf) { this.bufT += dt; if ((this.buf === 'atk' && jmp) || (this.buf === 'jmp' && atk)) { this.buf = null; atk = jmp = false; this.wantBack = true; } else if (this.bufT > 0.05) { if (this.buf === 'atk') atk = true; else jmp = true; this.buf = null; } else { atk = jmp = false; } }
    else if (atk && jmp) { atk = jmp = false; this.wantBack = true; }
    else if ((atk || jmp) && this.canAct() && !this.weapon) { this.buf = atk ? 'atk' : 'jmp'; this.bufT = 0; atk = jmp = false; }
    const I = { ...inp, atk, jmp };
    const falling = this.fallStep(dt, 0.8);
    if (!falling) { const fn = this['s_' + this.st]; if (fn) fn.call(this, dt, I); }
    this.y = clampY(this.y);
    const L = W.camX + 10, R = W.camX + G.VW - 10;
    if (this.st !== 'enter' && this.st !== 'out') this.x = Math.max(L, Math.min(R, this.x));
    if (!falling) this.pickups();
  }
  s_dead() { this.onDead(); }
  onDead() {
    if (this.t < 0.05) { this.lives -= 1; this.respawnT = 0; sfx('explosion', { vol: 0.4 }); }
    this.respawnT += 1 / 60;
    if (this.respawnT > 1.6) {
      if (this.lives > 0) this.respawn();
      else if (this.st !== 'out') { this.set('out'); this.alive = false; this.continueT = 9.99; }
    }
  }
  respawn() {
    this.hp = this.maxHp; this.set('respawn'); this.z = 140; this.vz = 0; this.inv = 2.4; this.weapon = null; this.x = Math.max(W.camX + 40, Math.min(W.camX + G.VW - 40, this.x)); this.alive = true;
  }
  move(dt, I, k = 1) {
    const sp = (I.run ? this.d.run : this.d.walk) * this.spd * k;
    this.x += I.mx * sp * dt; this.y += I.my * this.d.depth * this.spd * k * dt;
    if (Math.abs(I.mx) > 0.2) this.face = Math.sign(I.mx);
  }
  // ------------------------------------------------------------ states
  s_enter(dt) { this.x += this.d.walk * dt; this.y += (170 - this.y) * Math.min(1, dt * 3); if (this.t > 1.0) this.set('idle'); }
  s_respawn(dt) { this.vz -= 600 * dt; this.z += this.vz * dt; if (this.z <= 0) { this.z = 0; this.set('idle'); shake(3); addFx({ type: 'dust', x: this.x, y: this.y, dur: 0.4 }); } }
  s_win() {}
  s_idle(dt, I) {
    const moving = Math.hypot(I.mx, I.my) > 0.15;
    if (moving) { this.move(dt, I); this.st = I.run && Math.abs(I.mx) > 0.5 ? 'run' : 'walk'; }
    this.common(dt, I);
  }
  s_walk(dt, I) { this.s_idle(dt, I); if (Math.hypot(I.mx, I.my) <= 0.15) this.st = 'idle'; this.autoGrab(dt, I); }
  s_run(dt, I) {
    if (!(I.run && Math.abs(I.mx) > 0.5)) { this.st = Math.hypot(I.mx, I.my) > 0.15 ? 'walk' : 'idle'; return; }
    this.move(dt, I); this.trail = (this.trail || 0) + dt; if (this.trail > 0.12) { this.trail = 0; addFx({ type: 'dust', x: this.x - this.face * 8, y: this.y, dur: 0.3 }); }
    if (I.atk || this.buf === 'atk') { this.buf = null; return this.startDash(); }
    this.common(dt, I);
  }
  common(dt, I) {
    if (this.wantBack) { this.wantBack = false; this.set('back'); this.hitDone = false; sfx('whoosh', { vol: 0.5 }); return; }
    if (I.prs.sp) return this.special();
    if (I.jmp) { this.set('jump'); this.vz = this.d.jump; this.vx = I.mx * (I.run ? this.d.run : this.d.walk) * this.spd; this.vy = I.my * this.d.depth * 0.8; this.kicked = false; sfx('jump', { vol: 0.4 }); return; }
    if (I.atk) {
      if (this.weapon) return this.useWeapon(I);
      return this.attack();
    }
    if (I.prs.grab) return this.grabOrPick();
    if (this.weapon && this.weapon.w.spray && I.held.atk) return this.useWeapon(I);
  }
  attack() {
    if (this.gap > (this.d.comboGap || 0.6)) this.step = 0;
    const name = this.d.combo[Math.min(this.step, this.d.combo.length - 1)];
    this.atkName = name; this.atk = ATTACKS[name]; this.set('atk'); this.hitDone = false; this.queued = false;
    this.last = this.step === this.d.combo.length - 1;
    this.step = this.last ? 0 : this.step + 1;
    this.vx = this.face * 20;
    sfx('whoosh', { vol: 0.25, rate: 1.3 });
  }
  s_atk(dt, I) {
    const A = this.atk, dur = A.dur * (this.id === 'kim' ? 0.85 : this.id === 'will' ? 1.12 : 1);
    this.slide(dt, 10);
    const hitAt = dur * 0.45;
    if (!this.hitDone && this.t >= hitAt) {
      this.hitDone = true;
      const r = this.d.reach, fin = this.last;
      const hits = strike(this, { box: [A.box[0], A.box[1] * r], z: A.z, dmg: A.dmg * this.d.power * (fin ? 1.2 : 1), kb: fin ? A.kb : A.kb, stun: A.stun,
        down: fin || A.down && fin, sfxName: A.sfx, wordName: fin ? ['w_pow', 'w_wham', 'w_smack'][Math.floor(W.rnd() * 3)] : null });
      this.connected = hits.length > 0;
      if (hits.length) addScore(this, A.dmg * 10);
    }
    if (I.atk && this.t > dur * 0.35) this.queued = true;
    if (this.t >= dur) { this.gap = 0; if (this.queued && !this.last) this.attack(); else this.set('idle'); }
  }
  startDash() {
    this.set('dash'); this.hitSet = new Set(); this.vx = this.face * this.d.run * 1.25 * (this.d.dashK || 1); sfx('whoosh', { vol: 0.6 });
  }
  s_dash(dt) {
    this.x += this.vx * dt; this.vx *= Math.exp(-dt * 3.2);
    if (this.t > 0.04 && this.t < 0.34) {
      const A = ATTACKS.dash;
      const hits = strike(this, { box: A.box, z: A.z, dmg: A.dmg * this.d.power * (this.d.dashK ? 1.25 : 1), kb: A.kb, down: true, sfxName: A.sfx, once: this.hitSet, wordName: 'w_wham' });
      if (hits.length) addScore(this, 150);
    }
    if (this.t > A_DASH) this.set('idle');
  }
  s_back(dt) {
    const A = ATTACKS.back;
    if (!this.hitDone && this.t > 0.12) { this.hitDone = true; strike(this, { box: A.box, z: A.z, dmg: A.dmg * this.d.power, kb: A.kb, down: true, sfxName: A.sfx, back: true }); }
    if (this.t > A.dur) this.set('idle');
  }
  s_jump(dt, I) {
    this.vx += I.mx * 60 * dt;
    if ((I.atk || this.buf === 'atk') && !this.kicked) { this.buf = null; this.kicked = true; this.kickSet = new Set(); sfx('whoosh', { vol: 0.4 }); }
    if (this.kicked) {
      const A = ATTACKS.jkick;
      strike(this, { box: [A.box[0], A.box[1] * this.d.reach], z: A.z, dmg: A.dmg * this.d.power, kb: A.kb, down: true, sfxName: A.sfx, once: this.kickSet, wordName: 'w_pow' });
    }
    if (this.airborne(1 / 60 * (dt * 60))) { this.vx = 0; this.vy = 0; this.set('land'); }
  }
  s_land(dt) { if (this.t > 0.07) this.set('idle'); }
  s_hurt(dt) { this.slide(dt); if (this.t > this.stun) this.set('idle'); }
  s_dizzy(dt, I) { if (this.t > this.stun) this.set('idle'); }
  // ---- grabs
  autoGrab(dt, I) {
    if (this.weapon || !Math.abs(I.mx)) { this.pushT = 0; return; }
    const e = this.grabTarget(16);
    if (e && Math.sign(e.x - this.x) === Math.sign(I.mx)) { this.pushT = (this.pushT || 0) + dt; if (this.pushT > 0.22) this.grab(e); } else this.pushT = 0;
  }
  grabTarget(r) {
    let best = null, bd = 1e9;
    for (const e of W.enemies) {
      if (!e.alive || !e.grabbable()) continue;
      const dx = (e.x - this.x) * this.face;
      if (dx < -4 || dx > r * (this.d.grabR || 1) + 6 || Math.abs(e.y - this.y) > 8) continue;
      if (dx < bd) { bd = dx; best = e; }
    }
    return best;
  }
  grabOrPick() {
    const e = this.grabTarget(24);
    if (e && !this.weapon) return this.grab(e);
    const it = this.itemHere(true);
    if (it) { this.set('pickup'); this.pick = it; return; }
    if (this.weapon) return this.throwWeapon();
  }
  grab(e) {
    this.held = e; e.set('held'); e.holder = this; this.set('grab'); this.knees = 0; this.pushT = 0;
    e.face = -this.face; sfx('punch0', { vol: 0.3 });
  }
  s_grab(dt, I) {
    const e = this.held; if (!e || e.st !== 'held') { this.held = null; return this.set('idle'); }
    e.x = this.x + this.face * 15; e.y = this.y + 0.5; e.z = 0;
    if (I.atk) {
      const away = I.mx && Math.sign(I.mx) !== this.face;
      if (away || this.knees >= 2) return this.throwHeld(away ? -this.face : this.face);
      this.knees++; this.set('knee'); e.takeHit({ dmg: ATTACKS.knee.dmg * this.d.power, dir: this.face, kb: 0, stun: 0.2, held: true, from: this }); sfx('punch0'); spark(e.x, e.y, 26);
      addScore(this, 60);
    } else if (I.jmp || I.prs.grab) return this.throwHeld(I.mx ? Math.sign(I.mx) : this.face);
    if (this.t > 1.7) { this.release(); this.set('idle'); }
  }
  s_knee(dt) { const e = this.held; if (e) { e.x = this.x + this.face * 15; e.y = this.y + 0.5; } if (this.t > ATTACKS.knee.dur) { if (e && e.st === 'held' && e.hp > 0) { this.st = 'grab'; this.t = 0.2; } else { this.held = null; this.set('idle'); } } }
  throwHeld(dir) {
    const e = this.held; if (!e) return;
    this.face = dir; this.set('throw'); this.throwDir = dir; this.thrown = false;
  }
  s_throw(dt) {
    const e = this.held;
    if (e && !this.thrown && this.t > 0.14) {
      this.thrown = true; this.held = null;
      e.thrownBy(this, this.throwDir, this.d.throwK || 1);
      sfx('whoosh', { vol: 0.7 }); addScore(this, 120);
    }
    if (this.t > 0.36) this.set('idle');
  }
  // ---- pickups and weapons
  itemHere(weaponsOnly = false) {
    for (const it of W.items) { if (it.gone || it.z > 4 || (weaponsOnly && !it.weapon)) continue; if (Math.abs(it.x - this.x) < 14 && Math.abs(it.y - this.y) < 9) return it; }
    return null;
  }
  s_pickup(dt) {
    if (this.t > 0.18) {
      const it = this.pick; this.pick = null;
      if (it && !it.gone) { it.gone = true; if (this.weapon) this.dropWeapon(); this.weapon = { k: it.k.slice(2), w: it.w, uses: it.uses, ammo: it.ammo }; floatText(it.w.name, this.x, this.y, 60, '#8ad8ff'); sfx('select'); }
      this.set('idle');
    }
  }
  pickups() {
    if (!this.alive || this.st === 'dead') return;
    for (const it of W.items) {
      if (it.gone || it.weapon || it.z > 6) continue;
      if (Math.abs(it.x - this.x) < 13 && Math.abs(it.y - this.y) < 10) {
        it.gone = true; const d = it.def;
        if (d.heal) this.hp = Math.min(this.maxHp, this.hp + d.heal);
        if (d.speed) this.speedT = d.speed;
        if (d.life) this.lives += d.life;
        this.score += d.score; floatText(d.msg, this.x, this.y, 60, d.heal ? '#8ae87a' : '#ffe84a'); sfx(d.life ? 'powerup' : 'coin');
      }
    }
  }
  dropWeapon() { if (!this.weapon) return; const w = this.weapon; this.weapon = null; const it = dropItem('w:' + w.k, this.x + this.face * 10, this.y + 2); it.uses = w.uses; it.ammo = w.ammo; }
  throwWeapon() {
    const w = this.weapon; this.weapon = null; this.set('throw'); this.thrown = true;
    addShot({ kind: 'weapon', spr: w.w.spr, x: this.x + this.face * 12, y: this.y, z: 32, vx: this.face * 260, owner: this, dmg: 15 * this.d.power, spin: 14, life: 1.4, wk: w.k });
    sfx('whoosh');
  }
  useWeapon(I) {
    const w = this.weapon.w;
    if (w.spray) { this.set('spray'); this.sprayT = 0; return; }
    this.set('swing'); this.hitDone = false;
  }
  s_swing(dt) {
    const w = this.weapon && this.weapon.w; if (!w) return this.set('idle');
    if (!this.hitDone && this.t > w.rate * 0.5) {
      this.hitDone = true;
      const hits = strike(this, { box: [4, w.reach * (this.d.reach > 1 ? 1.1 : 1)], z: [8, 54], dmg: w.dmg * this.d.power, kb: w.down ? 150 : 50, stun: 0.4, down: !!w.down, dizzy: w.dizzy ? 1.0 : 0, sfxName: w.sfx, wordName: w.word });
      if (hits.length) { this.weapon.uses -= 1; addScore(this, w.dmg * 10); if (this.weapon.uses <= 0) { floatText('BROKE!', this.x, this.y, 60, '#ff8ac0'); addFx({ type: 'dust', x: this.x + this.face * 20, y: this.y, z: 20, dur: 0.4 }); this.weapon = null; } }
    }
    if (this.t > w.rate) this.set('idle');
  }
  s_spray(dt, I) {
    const W2 = this.weapon; if (!W2) return this.set('idle');
    this.sprayT += dt; W2.ammo -= dt;
    if (Math.floor(this.t * 30) % 2 === 0) for (let i = 0; i < 2; i++) addFx({ type: 'smoke', x: this.x + this.face * (20 + W.rnd() * 50), y: this.y + (W.rnd() - 0.5) * 10, z: 26 + W.rnd() * 10, dur: 0.35 });
    if (this.sprayT > 0.16) { this.sprayT = 0; sfx('spray', { vol: 0.5, gap: 0.12 }); strike(this, { box: [8, W2.w.reach], z: [0, 60], depth: 16, dmg: 1.5, kb: 10, stun: 0.3, dizzy: 1.3, sfxName: 'spray' }); }
    if (W2.ammo <= 0) { floatText('EMPTY!', this.x, this.y, 60, '#8ad8ff'); this.weapon = null; return this.set('idle'); }
    if (!I.held.atk && this.t > 0.25) this.set('idle');
  }
  // ---- specials
  special() {
    if (this.meter >= 100) return this.codeBlue();
    if (this.hp <= 1) { floatText('TOO TIRED!', this.x, this.y, 60, '#ff8ac0'); return; }
    this.hp = Math.max(1, this.hp - 8); this.set('special'); this.spDone = false; this.hitSet = new Set(); this.inv = Math.max(this.inv, 0.4);
    floatText(this.d.special + '!', this.x, this.y, 70, '#8ad8ff');
    if (this.id === 'kim') sfx('whoosh');
  }
  s_special(dt) {
    const id = this.id;
    if (id === 'nick') {  // rub paddles .. CLEAR! .. shockwave ring
      if (this.t > 0.15 && this.t < 0.2) sfx('zap', { gap: 1 });
      if (!this.spDone && this.t > 0.62) { this.spDone = true; addShot({ kind: 'shock', x: this.x + this.face * 14, y: this.y, z: 0, r: 6, grow: 260, rmax: 120, owner: this, dmg: 22 * this.d.power, life: 0.5, col: '#8ad8ff' }); word('w_clear', this.x, this.y, 30); shake(5); W.flash = 0.25; W.flashCol = '#c8f0ff'; }
      if (this.t > 0.9) this.set('idle');
    } else if (id === 'kim') {  // whirlwind: travel forward, multi-hit
      this.x += this.face * 120 * dt; this.inv = 0.2;
      const tick = Math.floor(this.t / 0.15); if (tick !== this.lastTick) { this.lastTick = tick; this.hitSet = new Set(); sfx('whoosh', { vol: 0.4, gap: 0.1 }); }
      const last = this.t > 0.82;
      strike(this, { box: [-30, 32], z: [6, 50], depth: 12, dmg: (last ? 10 : 5) * this.d.power, kb: last ? 160 : 20, stun: 0.25, down: last, once: this.hitSet, sfxName: 'punch1' });
      if (this.t > 0.95) this.set('idle');
    } else if (id === 'will') {  // body slam
      if (this.t < 0.18) {} else if (!this.spDone) { this.z = Math.sin(Math.min(1, (this.t - 0.18) / 0.4) * Math.PI) * 44; this.x += this.face * 40 * dt; if (this.t > 0.58) { this.spDone = true; this.z = 0; addShot({ kind: 'shock', x: this.x, y: this.y, z: 0, r: 8, grow: 280, rmax: 100, owner: this, dmg: 24 * this.d.power, life: 0.4, col: '#ffe84a' }); word('w_slam', this.x, this.y, 10); shake(7); sfx('explosion'); } }
      if (this.t > 0.85) this.set('idle');
    } else {  // jackie: spinning clipboard boomerang
      if (!this.spDone && this.t > 0.22) { this.spDone = true; addShot({ kind: 'boomerang', spr: 'w_clipboard', x: this.x + this.face * 14, y: this.y, z: 34, vx: this.face * 300, owner: this, dmg: 16 * this.d.power, spin: 18, life: 2.2, x0: this.x, dir: this.face }); sfx('whoosh'); }
      if (this.t > 0.5) this.set('idle');
    }
  }
  codeBlue() {
    this.meter = 0; this.set('super'); this.inv = 1.4; W.stop = 0.25; W.flash = 1; W.flashCol = '#3a7aff';
    sfx('page'); word('w_codeblue', W.camX + G.VW / 2, 110, 40); floatText('CODE BLUE, FLOOR 3!', W.camX + G.VW / 2, 120, 30, '#c8f0ff');
    W.codeBlue = { t: 0, by: this };
  }
  s_super(dt) {
    if (this.t > 0.55 && !this.spDone) {
      this.spDone = true; shake(8); sfx('zap'); sfx('explosion');
      for (const e of W.enemies) if (e.alive && e.x > W.camX - 10 && e.x < W.camX + G.VW + 10 && e.st !== 'dead') { e.takeHit({ dmg: 60, dir: Math.sign(e.x - this.x) || 1, kb: 160, down: true, from: this, force: true }); addFx({ type: 'spark', kind: 'bluespark', x: e.x, y: e.y, z: 30, dur: 0.3 }); }
      if (W.boss && W.boss.alive) W.boss.takeHit({ dmg: W.boss.maxHp * 0.12, dir: 1, from: this, force: true });
      addScore(this, 1000);
    }
    if (this.t > 1.0) { this.set('idle'); this.spDone = false; W.codeBlue = null; }
  }
  s_grabbed(dt, I) {
    const g = this.grabber; if (!g || g.st !== 'hug') { this.grabber = null; return this.set('idle'); }
    this.x = g.x + g.face * 14; this.y = g.y - 0.5; this.face = -g.face;
    const mashed = (I.prs.atk || I.prs.jmp || I.prs.grab || I.prs.sp ? 1 : 0) + (Math.abs(I.mx) > 0.6 && Math.sign(I.mx) !== this.lastMash ? 1 : 0);
    if (Math.abs(I.mx) > 0.6) this.lastMash = Math.sign(I.mx);
    this.mash += mashed;
    if (this.mash >= 6 || this.t > 3.2) { this.mash = 0; g.breakHug(); this.set('idle'); this.inv = 0.6; floatText('FREE!', this.x, this.y, 60, '#8ae87a'); }
  }
  // ------------------------------------------------------------ drawing
  pose() {
    const t = this.t, st = this.st;
    switch (st) {
      case 'idle': case 'land': return ['idle', Math.floor(W.t * 2.2)];
      case 'walk': case 'enter': return ['walk', Math.floor(W.t * 8)];
      case 'run': return ['run', Math.floor(W.t * 12)];
      case 'atk': { const A = this.atk; const n = this.atkName; const k = t / (A.dur * (this.id === 'kim' ? 0.85 : this.id === 'will' ? 1.12 : 1)); return [n, n === 'atk3' ? (k < 0.3 ? 0 : k < 0.75 ? 1 : 2) : (k < 0.4 ? 0 : 1)]; }
      case 'dash': return ['dash', 0];
      case 'back': return ['back', 0];
      case 'jump': case 'respawn': return this.kicked ? ['jkick', 0] : ['jump', this.vz > 0 ? 0 : 1];
      case 'grab': return ['grab', 0];
      case 'knee': return ['knee', 0];
      case 'throw': return ['throw', t < 0.14 ? 0 : 1];
      case 'hurt': return ['hurt', 0];
      case 'grabbed': return ['hurt', Math.floor(W.t * 6)];
      case 'dizzy': return ['dizzy', Math.floor(W.t * 4)];
      case 'fall': return ['fall', 0];
      case 'down': case 'dead': case 'out': return ['down', 0];
      case 'getup': return ['getup', 0];
      case 'pickup': return ['pickup', 0];
      case 'swing': return ['swing', t < (this.weapon ? this.weapon.w.rate * 0.45 : 0.1) ? 0 : 1];
      case 'spray': return ['spray', 0];
      case 'win': return ['win', Math.floor(W.t * 3)];
      case 'super': return ['win', 0];
      case 'special': {
        if (this.id === 'nick') return ['special', t < 0.3 ? 0 : t < 0.6 ? 1 : 2];
        if (this.id === 'kim') return ['special', Math.floor(t * 18)];
        if (this.id === 'will') return ['special', t < 0.18 ? 0 : !this.spDone ? 1 : 2];
        return ['special', t < 0.22 ? 0 : t < 0.36 ? 1 : 2];
      }
    }
    return ['idle', 0];
  }
  draw() {
    if (this.st === 'out') return;
    const [name, i] = this.pose();
    if (this.st === 'super') { const X = this.x - W.camX, Y = this.y + offY() - 30; ellipse(X, Y, 26 + Math.sin(W.t * 30) * 3, 30, '#8ad8ff', 0.35); }
    if (this.speedT > 0 && Math.floor(W.t * 10) % 2) ellipse(this.x - W.camX, this.y + offY() - 26, 14, 28, '#ffe84a', 0.18);
    this.drawSprite(name, i);
    // weapon in hand
    if (this.weapon && !['down', 'fall', 'dead', 'getup'].includes(this.st)) {
      const h = this.handOf(name, i), w = this.weapon.w;
      const a = (h[2] ?? 90) * Math.PI / 180;
      let rot = Math.atan2(Math.cos(a), Math.sin(a));  // forearm direction as a canvas angle (facing right)
      if (w.spray) rot = 0;
      const X = this.x - W.camX + this.face * h[0], Y = this.y + offY() - this.z + h[1];
      const f = this.face < 0;
      spr(w.spr, X, Y, { ax: w.grip[0], ay: w.grip[1], rot: f ? -rot : rot, flip: f });
    }
    if (this.st === 'dizzy') spr('dizzy' + (Math.floor(W.t * 8) % 3), this.x - W.camX, this.y + offY() - this.z - this.h - 4, { ax: 11 });
    if (this.slot !== undefined && W.heroes.length > 1 && this.st !== 'dead') text(`${this.slot + 1}P`, this.x - W.camX, this.y + offY() - this.z - this.h - 14, { col: this.slot ? '#8ad8ff' : '#ffe84a', align: 'center' });
  }
}
const A_DASH = ATTACKS.dash.dur;
