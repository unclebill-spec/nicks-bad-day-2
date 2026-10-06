// The four nurses: movement, combos, jump kick, dash attack, grab / knee / throw, back attack, weapons, the
// per-hero desperation special (costs a little health) and the Code Blue super (meter).
// v0.4: gurney rides (GRAB or ATK+JUMP next to a gurney; touch shows a RIDE button) and the 2-player Charge Nurse team-up
// (both hold SP near each other with half a meter each: a screen-clearing combined move).
// v0.6: lift small / medium props overhead (GRAB, or ATK when no patient is in reach) and throw them (ATK or GRAB; hold
// up / down to throw along the floor's depth, ATK+JUMP throws backward, jump + ATK is a jump-throw). Getting hit drops it.
// v0.6 meter tiers: SP with 1/3 meter = "It's time for some Ativan!" (syringe jab: sleepy knockdown, heavy damage), SP with a
// full meter = Code Blue defib paddles (CLEAR!, then lightning bolts forward in the facing direction only).
import { G, frame, spr, sprSize, ellipse, text, rect, ring } from './gfx.js';
import { HEROES, ATTACKS, WEAPONS, Y_MIN, Y_MAX } from './data.js';
import { W, offY, dropItem, addShot, addFx, word, floatText, shake, spark, addScore, smashProp, hitProp, bumpProps, THROW, propSprite } from './world.js';
import { Actor, strike, clampY } from './actor.js';
import { sfx } from './sound.js';

export const TIER = 100 / 3;  // v0.6 Code Blue meter tiers: 1/3 = Ativan jab, full = defib super
const CARRY_OK = new Set(['idle', 'walk', 'jump', 'land', 'lift', 'toss']);  // states a nurse can hold a prop overhead in

export class Hero extends Actor {
  constructor(id, slot, x, y) {
    super(id, x, y);
    this.isHero = true; this.id = id; this.slot = slot; this.d = HEROES[id];
    this.maxHp = this.hp = this.d.hp; this.lives = 3; this.score = 0; this.meter = 0; this.combo = 0; this.comboT = 0; this.maxCombo = 0; this.kos = 0;
    this.weapon = null; this.held = null; this.step = 0; this.gap = 9; this.buf = null; this.bufT = 0; this.speedT = 0; this.mash = 0; this.respawnT = 0; this.ctl = null;
    this.h = id === 'kim' || id === 'will' ? 48 : id === 'nate' ? 57 : 54; this.w = id === 'will' ? 18 : 14;
    this.sayS = null; this.sayUntil = 0; this.sayCd = 0; this.sayLast = {}; this.idleT = 0; this.hiLv = null;  // v0.8 speech bubbles (heroes with d.lines)
  }
  hittable() { return this.inv <= 0 && !(this.st === 'special' && (this.id === 'nate' || (this.id === 'heather' && this.t > 0.1 && this.t < 0.82))) && !['fall', 'down', 'getup', 'dead', 'super', 'ativan', 'respawn', 'enter', 'win', 'out', 'ride', 'teamup', 'slam'].includes(this.st); }
  canAct() { return ['idle', 'walk', 'run'].includes(this.st); }
  set(st) { super.set(st); if (this.carry && !CARRY_OK.has(st)) this.releaseProp(false, st === 'win' || st === 'enter' || st === 'teamup'); }  // any hit / grab / KO drops the prop
  get spd() { return this.speedT > 0 ? 1.4 : 1; }

  takeHit({ dmg, dir, kb, stun, down, dizzy, from }) {
    if (!this.hittable()) return;
    if (this.held) this.release();
    if (this.carry) this.releaseProp(false);
    if (this.grabber) this.grabber = null;
    const d = dmg * W.diff.dmg * (from && from.rageT > W.t ? 1.35 : 1);  // enraged patients (fire alarm) hit harder
    this.hp -= d; this.flash = 0.12; this.meter = Math.min(100, this.meter + d * 0.35); this.combo = 0;
    sfx('hurt', { vol: 0.55 });
    if (this.hp <= 0) { this.hp = 0; this.knock(dir, 150, 220); if (!this.say('ko', true)) floatText(['OUCH!', 'MY BACK!', 'NOT TODAY!'][Math.floor(W.rnd() * 3)], this.x, this.y, 64, '#ff8ac0'); return; }
    this.say('hurt');
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
    this.sayTick(dt, I);
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
    this.hiLv = W.lv; this.idleT = 0; this.say('revive', true);
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
    if (moving) { if (this.carry) { this.move(dt, { ...I, run: false }, 0.74); this.st = 'walk'; } else { this.move(dt, I); this.st = I.run && Math.abs(I.mx) > 0.5 ? 'run' : 'walk'; } }
    this.common(dt, I);
  }
  s_walk(dt, I) { this.s_idle(dt, I); if (Math.hypot(I.mx, I.my) <= 0.15) this.st = 'idle'; }  // v0.7: no walk-in grabs; GRAB is a dedicated button
  s_run(dt, I) {
    if (!(I.run && Math.abs(I.mx) > 0.5)) { this.st = Math.hypot(I.mx, I.my) > 0.15 ? 'walk' : 'idle'; return; }
    this.move(dt, I); this.trail = (this.trail || 0) + dt; if (this.trail > 0.12) { this.trail = 0; addFx({ type: 'dust', x: this.x - this.face * 8, y: this.y, dur: 0.3 }); }
    if (I.atk || this.buf === 'atk') { this.buf = null; return this.startDash(); }
    this.common(dt, I);
  }
  common(dt, I) {
    if (this.carry) return this.carryInput(I);
    if (I.prs.grab && !this.weapon) { const e = this.grabTarget(24); if (e) return this.grab(e); }  // a patient in reach beats everything
    if ((this.wantBack || I.prs.grab) && !(this.held && this.held.st === 'held')) { const g = this.nearGurney(); if (g) { this.wantBack = false; return this.mount(g); } }
    if (this.wantBack) { this.wantBack = false; this.set('back'); this.hitDone = false; sfx('whoosh', { vol: 0.5 }); return; }
    if (I.prs.sp) return this.special();
    if (I.jmp) { this.set('jump'); this.vz = this.d.jump; this.vx = I.mx * (I.run ? this.d.run : this.d.walk) * this.spd; this.vy = I.my * this.d.depth * 0.8; this.kicked = false; sfx('jump', { vol: 0.4 }); return; }
    if (I.atk) {
      if (this.weapon) return this.useWeapon(I);
      if (this.gap > (this.d.comboGap || 0.6) && !this.foeNear()) { const p = this.liftTarget(true); if (p) return this.lift(p); }  // ATK at a prop with nobody to hit: pick it up
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
    const A = this.atk, dur = A.dur * (this.d.atkK || 1);
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
    if (this.carry) {  // jump-throw: ATK (or GRAB) in the air hurls it down at an angle
      if (I.atk || I.prs.grab || this.buf === 'atk') { this.buf = null; this.tossDir = I.mx ? Math.sign(I.mx) : this.face; this.face = this.tossDir; this.tossVy = I.my || 0; this.releaseProp(true); this.airTossT = W.t + 0.25; }
      if (this.airborne(1 / 60 * (dt * 60))) { this.vx = 0; this.vy = 0; this.set('land'); }
      return;
    }
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
    if (this.weapon || this.carry || !Math.abs(I.mx)) { this.pushT = 0; return; }
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
  grabOrPick() {  // GRAB priority: patient > gurney (in common) > weapon on the floor > liftable prop > throw your weapon
    const e = this.grabTarget(24);
    if (e && !this.weapon) return this.grab(e);
    const it = this.itemHere(true);
    if (it) { this.set('pickup'); this.pick = it; return; }
    const p = this.liftTarget();
    if (p) { if (this.weapon) this.dropWeapon(); return this.lift(p); }
    if (this.weapon) return this.throwWeapon();
  }
  // ---- v0.6 carrying props overhead
  foeNear() {  // is a patient (or the boss) close enough in front to punch? then ATK punches instead of lifting
    for (const e of [...W.enemies, ...(W.boss ? [W.boss] : [])]) {
      if (!e.alive || !e.hittable || !e.hittable() || e.st === 'dead') continue;
      if (!e.depthAny && Math.abs(e.y - this.y) > 14 + (e.big ? 6 : 0)) continue;
      const dx = (e.x - this.x) * this.face, ew = e.w / 2;
      if (dx > -ew - 4 && dx < 46 + ew) return true;
    }
    return false;
  }
  liftTarget(strict = false) {  // the closest carryable prop at the nurse's feet / just in front (ATK uses a tighter reach)
    let best = null, bd = 1e9;
    for (const p of W.props) {
      const d = p.def;
      if (!d.carry || p.st >= 2 || p.rider || p.flying || p.magnet || p.z > 6 || Math.abs(p.vx) > 40) continue;
      const dy = Math.abs(p.y - this.y); if (dy > (strict ? 10 : 13)) continue;
      const dx = (p.x - this.x) * this.face;
      if (dx < -(d.w / 2 + 4) || dx > d.w / 2 + (strict ? 8 : 14)) continue;
      const sc = Math.abs(dx) + dy * 1.5; if (sc < bd) { bd = sc; best = p; }
    }
    return best;
  }
  canLift() { return !this.carry && this.canAct() && !this.nearGurney() && !(this.grabTarget(24) && !this.weapon) && !this.itemHere(true) && !!this.liftTarget(); }
  lift(p) {
    const i = W.props.indexOf(p); if (i >= 0) W.props.splice(i, 1);  // out of the world while it's overhead
    p.vx = p.vy = p.vz = 0; p.z = 0; p.shake = 0; p.nudge = false; p.magnet = false; p.carrier = this;
    this.say('lift');
    this.carry = p; this.liftDX = (p.x - this.x) * this.face; this.liftDY = p.y - this.y; this.vx = 0; this.pushT = 0;
    if (Math.abs(p.x - this.x) > 3) this.face = Math.sign(p.x - this.x) || this.face;
    this.set('lift'); sfx('whoosh', { vol: 0.35, rate: 0.7 }); W.stats.lifts = (W.stats.lifts || 0) + 1;
  }
  s_lift(dt) { if (this.t > 0.24) this.set('idle'); }
  carryInput(I) {
    if (I.prs.sp) { this.releaseProp(false, true); return this.special(); }
    if (this.wantBack) { this.wantBack = false; return this.toss(-this.face, I); }  // ATK+JUMP: throw it behind you
    if (I.jmp) { this.set('jump'); this.vz = this.d.jump * 0.88; this.vx = I.mx * this.d.walk * 0.8; this.vy = I.my * this.d.depth * 0.7; this.kicked = false; sfx('jump', { vol: 0.4 }); return; }
    if (I.atk || I.prs.grab) return this.toss(Math.abs(I.mx) > 0.3 ? Math.sign(I.mx) : this.face, I);
  }
  toss(dir, I) { this.face = dir; this.tossDir = dir; this.tossVy = Math.abs(I.my || 0) > 0.3 ? Math.sign(I.my) : 0; this.set('toss'); this.tossed = false; }
  s_toss(dt) {
    if (!this.tossed && this.t > 0.1) this.releaseProp(true);
    if (this.t > 0.3) this.set('idle');
  }
  releaseProp(thrown, gentle = false) {
    const p = this.carry; if (!p) return;
    this.carry = null; p.carrier = null; this.tossed = true;
    p.hitSet = new Set([this]); p.kicker = this; p.spin = 0;
    if (thrown) {
      const air = this.z > 8, dir = this.tossDir || this.face;
      p.x = this.x + dir * 10; p.y = this.y; p.z = this.z + THROW.z;
      p.vx = dir * THROW.vx; p.vy = (this.tossVy || 0) * THROW.vy; p.vz = air ? THROW.airVz : THROW.vz;
      p.flying = { owner: this, hit: new Set(), dir, air };
      sfx('whoosh', { vol: 0.85, rate: 0.75 }); addScore(this, 50); W.stats.throws = (W.stats.throws || 0) + 1;
      if (air) floatText('JUMP THROW!', this.x, this.y, this.z + 70, '#8ad8ff');
    } else if (gentle) {  // set it down in front (SP while carrying)
      p.x = this.x + this.face * (p.def.w / 2 + 6); p.y = this.y; p.z = 0; p.vx = p.vy = p.vz = 0;
    } else {  // knocked out of your hands: it tumbles off behind you and takes a knock
      p.x = this.x; p.y = this.y; p.z = this.z + 34; p.vz = 60; p.vx = -this.face * 50; p.vy = 0;
    }
    W.props.push(p);
    if (!thrown && !gentle) { p.hp -= 1; if (p.hp <= 0) { p.z = 0; p.vz = 0; smashProp(p); } else p.st = Math.max(p.st, p.hp <= Math.ceil(p.def.hp / 2) ? Math.min(1, (p.def.states || 3) - 2) : 0); }
  }

  grab(e) {
    this.held = e; e.set('held'); e.holder = this; this.set('grab'); this.knees = 0; this.pushT = 0;
    this.dirArmed = false; this.dirHeld = 0;  // a direction only counts once the stick has been neutral (or is held on purpose)
    e.face = -this.face; e.rot = 0; sfx('punch0', { vol: 0.3 }); W.stats.grabs = (W.stats.grabs || 0) + 1; this.say('grab');
  }
  // v0.7 holding a patient: FORWARD (tap, hold, or with ATK) = toss them forward; AWAY = over-the-shoulder body slam
  // behind you; ATK alone = knees (the third one tosses); JUMP or GRAB again = toss forward (GRAB + AWAY = slam).
  s_grab(dt, I) {
    const e = this.held; if (!e || e.st !== 'held') { this.held = null; return this.set('idle'); }
    e.x = this.x + this.face * 15; e.y = this.y + 0.5; e.z = 0;
    const sx = Math.abs(I.mx) > 0.55 ? Math.sign(I.mx) : 0;
    if (!sx) { this.dirArmed = true; this.dirHeld = 0; } else this.dirHeld += dt;
    if (I.atk && sx) return sx === this.face ? this.throwHeld(this.face) : this.slam();
    if (sx && this.t > 0.06 && (this.dirArmed || this.dirHeld > 0.4)) return sx === this.face ? this.throwHeld(this.face) : this.slam();
    if (I.jmp || I.prs.grab) return sx === -this.face ? this.slam() : this.throwHeld(this.face);
    if (I.atk) {
      if (this.knees >= 2) return this.throwHeld(this.face);
      this.knees++; this.set('knee'); e.takeHit({ dmg: ATTACKS.knee.dmg * this.d.power, dir: this.face, kb: 0, stun: 0.2, held: true, from: this }); sfx('punch0'); spark(e.x, e.y, 26);
      addScore(this, 60);
    }
    if (this.t > 2.0) { this.release(); this.set('idle'); }
  }
  slam() {  // over-the-shoulder body slam: the patient arcs over your head and lands BEHIND you
    const e = this.held; if (!e) return;
    this.set('slam'); this.slamF = this.face; this.slamDone = false; e.rot = 0; sfx('toss', { vol: 0.6 }); this.inv = Math.max(this.inv, 0.1);
  }
  s_slam(dt) {
    const e = this.held, f = this.slamF, T = 0.4;
    if (e && !this.slamDone) {
      if (e.st !== 'held' || !e.alive) { this.held = null; this.slamDone = true; }
      else {
        const p = Math.min(1, this.t / T), a = p * Math.PI;
        e.x = this.x + f * 16 * Math.cos(a); e.y = this.y + 0.5; e.z = Math.sin(a) * 40 + (1 - p) * 2;
        e.face = -f; e.rot = -f * a * 0.95;  // spin over the shoulder (head first)
        if (p >= 1) this.slamLand(e, f);
      }
    }
    if (this.t > 0.66) this.set('idle');
  }
  slamLand(e, f) {
    this.slamDone = true; this.held = null; e.holder = null; e.rot = 0; e.z = 0; e.x = this.x - f * 20;
    const pw = this.d.power;
    e.takeHit({ dmg: 26 * pw, dir: -f, kb: 50, down: true, from: this, force: true });
    shake(7); W.stop = Math.max(W.stop, 0.1); sfx('slam', { vol: 0.95 }); sfx('heavy', { vol: 0.6 }); word('w_slam', e.x, e.y, 10);
    for (let i = 0; i < 4; i++) addFx({ type: 'dust', x: e.x + (i - 1.5) * 9, y: e.y + (i % 2) * 3, dur: 0.45 });
    // the landing knocks over anyone close by (and smashes props), patients only take a knock, bosses a little damage
    for (const o of W.enemies) {
      if (o === e || !o.alive || !o.hittable() || Math.abs(o.y - e.y) > 14 || Math.abs(o.x - e.x) > 34) continue;
      o.takeHit({ dmg: 14 * pw, dir: Math.sign(o.x - e.x) || -f, kb: 130, down: true, from: this }); spark(o.x, o.y, 24, 'bigspark'); addScore(this, 150);
    }
    const B = W.boss;
    if (B && B.alive && B.hittable && B.hittable() && (B.depthAny || Math.abs(B.y - e.y) < 18) && Math.abs(B.x - e.x) < (B.w || 40) / 2 + 24) B.takeHit({ dmg: 12 * pw, dir: -f, from: this });
    bumpProps({ x: e.x, y: e.y, z: 0, w: 20 }, 12, -f, this, new Set([e]), 16);
    addScore(this, 250); W.stats.slams = (W.stats.slams || 0) + 1; this.say('throw', true);
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
      e.thrownBy(this, this.throwDir, this.d.throwK || 1); e.rot = 0;
      sfx('whoosh', { vol: 0.7 }); sfx('toss', { vol: 0.5 }); addScore(this, 120); W.stats.tosses = (W.stats.tosses || 0) + 1; this.say('throw');
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
      if (it && !it.gone) { it.gone = true; if (this.weapon) this.dropWeapon(); this.weapon = { k: it.k.slice(2), w: it.w, uses: it.uses, ammo: it.ammo }; floatText(it.w.name, this.x, this.y, 60, '#8ad8ff'); sfx('select'); this.say('weapon'); }
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
        this.score += d.score; floatText(d.msg, this.x, this.y, 60, d.heal ? '#8ae87a' : '#ffe84a'); sfx(d.sfx || (d.life ? 'powerup' : 'coin'), { vol: d.sfx ? 0.9 : 1 }); if (d.sfx) sfx('coin', { vol: 0.4 });
        if (d.heal) this.say('food', true); else if (d.speed) this.say('coffee');
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
  // ---- v0.4 gurney ride: hop on, it rolls forward ~2.6 s plowing patients and props, then crashes (JUMP bails early and
  // sends the empty gurney rolling on). Up / down steers.
  nearGurney() {
    for (const p of W.props) {
      if (!p.def.ride || p.st >= 2 || p.rider || Math.abs(p.vx) > 40) continue;
      if (Math.abs(p.y - this.y) < 14 && Math.abs(p.x - this.x) < p.def.w / 2 + 12) return p;
    }
    return null;
  }
  mount(g) {
    this.ride = g; g.rider = this; g.kicker = this; g.vx = g.vy = 0; g.hitSet = new Set([this]);
    this.rideDir = this.face; this.set('ride'); this.rideSet = new Set([g]); this.hopX = this.x; this.rolling = false;
    sfx('jump', { vol: 0.5 }); floatText('GURNEY RIDE!', this.x, this.y, 70, '#8ad8ff'); W.stats.rides = (W.stats.rides || 0) + 1;
  }
  s_ride(dt, I) {
    const g = this.ride;
    if (!g || g.st >= 2) return this.dismount(false);
    const hop = 0.22;
    if (this.t < hop) { const k = this.t / hop; this.x = this.hopX + (g.x - this.hopX) * k; this.y += (g.y + 0.5 - this.y) * Math.min(1, dt * 12); this.z = Math.sin(k * Math.PI) * 18 + k * 12; return; }
    const d = this.rideDir, sp = Math.min(290, 200 + (this.t - hop) * 120);
    if (!this.rolling) { this.rolling = true; sfx('rattle', { vol: 0.7 }); shake(2); }
    g.x += d * sp * dt; g.y = clampY(g.y + I.my * 70 * dt); g.vx = d * sp;
    this.x = g.x; this.y = g.y + 0.5; this.z = 12 + (Math.floor(W.t * 30) % 2); this.face = d;
    if ((this.rattleT = (this.rattleT || 0) + dt) > 0.3) { this.rattleT = 0; sfx('rattle', { vol: 0.45 }); addFx({ type: 'dust', x: g.x - d * g.def.w / 2, y: g.y, z: 0, dur: 0.3 }); }
    if (Math.floor(this.t * 30) % 2 === 0) addFx({ type: 'speed', x: g.x - d * (g.def.w / 2 + 14) - 5, y: g.y, z: 6 + W.rnd() * 34, dur: 0.18 });
    for (const e of [...W.enemies, ...(W.boss ? [W.boss] : [])]) {  // plow through the crowd
      if (!e.alive || this.rideSet.has(e) || !e.hittable() || e.z > 30) continue;
      if (Math.abs(e.y - g.y) > 13 + (e.big ? 6 : 0) || Math.abs(e.x - (g.x + d * 6)) > g.def.w / 2 + e.w / 2) continue;
      this.rideSet.add(e);
      if (e.isBoss) { e.takeHit({ dmg: 14, dir: d, from: this }); spark(e.x, e.y, 26, 'bigspark'); return this.dismount(true); }
      e.takeHit({ dmg: 16 * this.d.power, dir: d, kb: 200, stun: 0.5, down: true, from: this });
      spark(e.x, e.y, 26, 'bigspark'); sfx('heavy', { vol: 0.8 }); shake(3); W.stop = Math.max(W.stop, 0.04);
      word(['w_wham', 'w_pow', 'w_smack'][Math.floor(W.rnd() * 3)], e.x, e.y, 14); addScore(this, 200);
      this.combo = (this.combo || 0) + 1; this.comboT = 1.6; this.maxCombo = Math.max(this.maxCombo || 0, this.combo); this.meter = Math.min(100, this.meter + 6); this.lastFoe = e; this.lastFoeT = W.t + 2.2;
    }
    bumpProps({ x: g.x + d * (g.def.w / 2), y: g.y, z: 0 }, 14, d, this, this.rideSet, 4);  // carts and chairs in the way go flying
    const edge = (d > 0 && g.x > W.camX + G.VW - g.def.w / 2 - 2) || (d < 0 && g.x < W.camX + g.def.w / 2 + 2);
    if (I.jmp) return this.dismount(false);
    if (edge || this.t > hop + 2.6) return this.dismount(true);
  }
  dismount(crash) {
    const g = this.ride, d = this.rideDir || this.face; this.ride = null; this.rolling = false;
    if (g) {
      g.rider = null;
      if (crash && g.st < 2) { g.vx = d * 40; smashProp(g); shake(6); floatText('WHOA!', this.x, this.y, 70, '#ffffff'); W.stats.crashes = (W.stats.crashes || 0) + 1; }
      else if (g.st < 2) { g.vx = d * 240; g.hitSet = new Set([this]); g.nudge = false; g.kicker = this; }
    }
    this.set('jump'); this.vz = 210; this.vx = d * (crash ? 50 : -40); this.vy = 0; this.z = Math.max(this.z, 8);
    this.kicked = true; this.kickSet = new Set(g ? [g] : []); this.inv = Math.max(this.inv, 0.5);
  }
  // ---- v0.4 Charge Nurse team-up (2P): both hold SP within reach of each other with >= half a meter each
  partner() {
    if (W.heroes.length < 2) return null;
    const o = W.heroes.find((q) => q !== this && q.alive && !['out', 'dead'].includes(q.st));
    return o && Math.abs(o.x - this.x) < 110 && Math.abs(o.y - this.y) < 40 ? o : null;
  }
  s_teamwait(dt, I) {
    const p = this.partner();
    if (p && p.st === 'teamwait') return startTeam(p, this);
    if (!p || !(I.held && I.held.sp) || this.t > 1.2) { this.set('idle'); this.soloSpecial(); }
  }
  s_teamup(dt) {
    const T = W.team; this.z = Math.sin(Math.min(1, this.t / 1.5) * Math.PI) * 16;
    if (T && T.a === this) { T.t = this.t; if (!T.hit && this.t > 0.75) { T.hit = true; teamBlast(T); } }
    if (this.t > 1.6) { this.z = 0; this.set('idle'); if (T && T.a === this) W.team = null; }
  }
  // ---- specials
  special() {
    const p = this.partner();
    if (p && this.meter >= 50 && p.meter >= 50) {
      if (p.st === 'teamwait') return startTeam(p, this);
      this.set('teamwait'); sfx('blip', { vol: 0.6 }); return;
    }
    return this.soloSpecial();
  }
  soloSpecial() {
    if (this.meter >= 100) return this.codeBlue();
    if (this.meter >= TIER - 0.01) return this.ativan();
    if (this.hp <= 1) { floatText('TOO TIRED!', this.x, this.y, 60, '#ff8ac0'); return; }
    this.hp = Math.max(1, this.hp - 8); this.set('special'); this.spDone = false; this.hitSet = new Set(); this.inv = Math.max(this.inv, this.id === 'nate' || this.id === 'heather' ? 0 : 0.4); this.lastTick = -1;
    floatText(this.d.special + '!', this.x, this.y, 70, '#8ad8ff');
    if (this.id === 'kim') sfx('whoosh');
    if (this.id === 'nate') sfx('clunk', { vol: 0.6 });
    if (this.id === 'heather') sfx('charge', { vol: 0.5 });
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
    } else if (id === 'nate') {  // v0.8 ROLLING CHAIR: plops into an office chair and coasts forward, plowing patients over
      if (this.t > 0.16 && this.t < 0.98) {
        const v = 190 * Math.min(1, (this.t - 0.16) / 0.12) * (this.t > 0.8 ? (0.98 - this.t) / 0.18 : 1);
        this.x += this.face * v * dt;  // (not hittable while rolling: see hittable(); no inv so he doesn't blink)
        if (Math.floor(this.t * 12) !== this.lastTick) { this.lastTick = Math.floor(this.t * 12); addFx({ type: 'dust', x: this.x - this.face * 12, y: this.y, dur: 0.3 }); sfx('rattle', { vol: 0.3, gap: 0.25 }); }
        const hits = strike(this, { box: [-6, 30], z: [0, 40], depth: 14, dmg: 15 * this.d.power, kb: 170, stun: 0.5, down: true, once: this.hitSet, sfxName: 'heavy', wordName: 'w_wham' });
        if (hits.length) addScore(this, 150 * hits.length);
      }
      if (this.t > 1.12) { this.set('idle'); addFx({ type: 'dust', x: this.x, y: this.y, dur: 0.35 }); this.say('special'); }
    } else if (id === 'heather') {  // v0.10 RUNNING CLOTHESLINE: cock the arm, sprint forward with it out at neck height, flatten everyone in the way
      if (this.t > 0.12 && this.t < 0.8) {
        if (!this.spDone) { this.spDone = true; sfx('clothesline', { vol: 0.8 }); }
        const v = 255 * Math.min(1, (this.t - 0.12) / 0.08) * (this.t > 0.66 ? (0.8 - this.t) / 0.14 : 1);
        this.x += this.face * v * dt;  // (not hittable mid-dash: see hittable(); no inv blink)
        const tick = Math.floor(this.t * 14);
        if (tick !== this.lastTick) { this.lastTick = tick; addFx({ type: 'dust', x: this.x - this.face * 10, y: this.y, dur: 0.28 }); }
        const hits = strike(this, { box: [-4, 28], z: [8, 52], depth: 15, dmg: 16 * this.d.power, kb: 200, stun: 0.55, down: true, once: this.hitSet, sfxName: 'heavy', wordName: 'w_wham' });
        if (hits.length) { addScore(this, 150 * hits.length); shake(3); W.stats.clotheslined = (W.stats.clotheslined || 0) + hits.length; }
      }
      if (this.t > 0.8 && this.t < 0.84 && this.lastTick !== 99) { this.lastTick = 99; sfx('skid', { vol: 0.4 }); addFx({ type: 'dust', x: this.x + this.face * 6, y: this.y, dur: 0.35 }); }
      if (this.t > 1.0) { this.set('idle'); this.say('special', true); }
    } else {  // jackie: spinning clipboard boomerang
      if (!this.spDone && this.t > 0.22) { this.spDone = true; addShot({ kind: 'boomerang', spr: 'w_clipboard', x: this.x + this.face * 14, y: this.y, z: 34, vx: this.face * 300, owner: this, dmg: 16 * this.d.power, spin: 18, life: 2.2, x0: this.x, dir: this.face }); sfx('whoosh'); }
      if (this.t > 0.5) this.set('idle');
    }
  }
  // ---- v0.6 tier 1: the Ativan jab
  jabTarget(range) {  // nearest patient (or boss) in front, within range
    let best = null, bd = 1e9;
    for (const e of [...W.enemies, ...(W.boss ? [W.boss] : [])]) {
      if (!e.alive || e.st === 'dead' || !e.hittable || !e.hittable()) continue;
      if (!e.depthAny && Math.abs(e.y - this.y) > 16 + (e.big ? 6 : 0)) continue;
      const dx = (e.depthAny ? (e.front ?? e.x) - this.x : e.x - this.x) * this.face - (e.isBoss && !e.depthAny ? e.w / 2 : 0);
      if (dx < -8 || dx > range) continue;
      if (dx < bd) { bd = dx; best = e; }
    }
    return best;
  }
  ativan() {
    this.meter = Math.max(0, this.meter - TIER); this.set('ativan'); this.spDone = false; this.inv = Math.max(this.inv, 0.5);
    this.shoutT = W.t + 1.7; this.jabT = this.jabTarget(80);
    sfx(this.d.ativanSfx || 'ativan', { vol: 0.85 }); this.sayS = null; W.stats.ativan = (W.stats.ativan || 0) + 1;
  }
  s_ativan(dt) {
    const e = this.jabT;
    if (this.t > 0.16 && this.t < 0.42 && e && e.alive) {  // lunge in to reach the target
      const gap = (e.depthAny ? (e.front ?? e.x) : e.x - this.face * (e.isBoss ? e.w / 2 : 0)) - this.x;
      if (Math.abs(gap) > 22) this.x += Math.sign(gap) * Math.min(Math.abs(gap) - 22, 230 * dt);
      if (!e.depthAny) this.y += Math.sign(e.y - this.y) * Math.min(Math.abs(e.y - this.y), 60 * dt);
    }
    if (!this.spDone && this.t > 0.42) {
      this.spDone = true;
      const t = this.jabTarget(40);
      if (!t) { floatText('MISSED!', this.x, this.y, 60, '#8ad8ff'); sfx('whoosh', { vol: 0.4 }); }
      else if (t.isBoss) {  // bosses / mini-bosses: damage + a short stagger
        t.takeHit({ dmg: 34 * this.d.power, dir: this.face, kb: 0, from: this, force: true }); t.stagT = 0.8; t.flash = 0.3;
        floatText('WOOZY...', t.x, t.y, 90, '#c8a0ff'); sfx('punch1'); spark(this.x + this.face * 22, this.y, 34, 'bigspark'); shake(4); W.stop = 0.08;
      } else {
        const big = 36 * this.d.power, dmg = t.hp > 16 ? Math.min(big, t.hp - 4) : big;  // heavy, but leaves most of them snoozing for free hits
        t.takeHit({ dmg, dir: this.face, kb: 90, down: true, from: this, force: true });
        if (t.alive && t.hp > 0) { t.sleepT = W.t + 2.6; t.zzzT = 0; }
        floatText('NIGHTY NIGHT!', t.x, t.y, 70, '#c8a0ff'); sfx('punch1'); spark(t.x, t.y, 30, 'bigspark'); addFx({ type: 'zzz', x: t.x, y: t.y, z: 40, dur: 1.4 }); shake(3); W.stop = 0.07;
        addScore(this, 400); this.say('ativan', true); this.combo = (this.combo || 0) + 1; this.comboT = 1.6; this.maxCombo = Math.max(this.maxCombo, this.combo);
      }
    }
    if (this.t > 0.7) this.set('idle');
  }
  // ---- v0.6 full meter: Code Blue defib paddles. Charge .. CLEAR! .. lightning forward (facing direction only)
  codeBlue() {
    this.meter = 0; this.set('super'); this.inv = 1.6; W.stop = 0.2; W.flash = 0.8; W.flashCol = '#3a7aff'; this.spDone = false; this.cleared = false;
    sfx('page'); sfx('defib', { vol: 0.9 }); word('w_codeblue', W.camX + G.VW / 2, 110, 40); floatText('CODE BLUE! PADDLES!', this.x, this.y, 132, '#c8f0ff');
    W.codeBlue = { t: 0, by: this }; W.stats.supers = (W.stats.supers || 0) + 1; this.say('codeblue', true);
  }
  s_super(dt) {
    if (!this.cleared && this.t > 0.34) { this.cleared = true; word('w_clear', this.x + this.face * 10, this.y, 62); sfx('clear', { vol: 0.9 }); W.flash = Math.max(W.flash, 0.3); W.flashCol = '#c8f0ff'; }
    if (Math.floor(this.t * 20) % 3 === 0 && this.t < 0.62) addFx({ type: 'spark', kind: 'bluespark', x: this.x + this.face * 12, y: this.y, z: 30 + W.rnd() * 14, dur: 0.12 });
    if (this.t > 0.62 && !this.spDone) {
      this.spDone = true; shake(8); sfx('crackle', { vol: 0.9 }); sfx('zap');
      addShot({ kind: 'defib', x: this.x + this.face * 18, y: this.y, z: 30, dir: this.face, reach: 0, owner: this, life: 0.8, seed: Math.floor(W.rnd() * 999) });
      addScore(this, 500);
    }
    if (this.t > 1.25) { this.set('idle'); this.spDone = false; W.codeBlue = null; }
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
      case 'idle': case 'land': return this.carry ? ['lift', Math.floor(W.t * 2.2)] : ['idle', Math.floor(W.t * 2.2)];
      case 'walk': case 'enter': return this.carry ? ['carry', Math.floor(W.t * 6)] : ['walk', Math.floor(W.t * 8)];
      case 'lift': return t < 0.1 ? ['pickup', 0] : ['lift', 0];
      case 'toss': return ['throw', t < 0.1 ? 0 : 1];
      case 'run': return ['run', Math.floor(W.t * 12)];
      case 'atk': { const A = this.atk; const n = this.atkName; const k = t / (A.dur * (this.d.atkK || 1)); return [n, A.t.length === 3 ? (k < 0.3 ? 0 : k < 0.75 ? 1 : 2) : (k < 0.4 ? 0 : 1)]; }
      case 'dash': return ['dash', 0];
      case 'back': return ['back', 0];
      case 'jump': case 'respawn': return this.carry ? ['lift', 0] : (this.airTossT || 0) > W.t ? ['throw', 1] : this.kicked ? ['jkick', 0] : ['jump', this.vz > 0 ? 0 : 1];
      case 'grab': return ['grab', 0];
      case 'knee': return ['knee', 0];
      case 'throw': return ['throw', t < 0.14 ? 0 : 1];
      case 'slam': return this.t < 0.22 ? ['lift', 0] : ['throw', 1];
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
      case 'super': return ['defib', this.t < 0.34 ? 0 : this.t < 0.62 ? 1 : 2];
      case 'ativan': return ['jab', this.t < 0.38 ? 0 : 1];
      case 'ride': return this.t < 0.22 ? ['jump', 0] : ['ride', Math.floor(W.t * 8)];
      case 'teamwait': return ['team', 0];
      case 'teamup': return ['team', 0];
      case 'special': {
        if (this.id === 'nick') return ['special', t < 0.3 ? 0 : t < 0.6 ? 1 : 2];
        if (this.id === 'kim') return ['special', Math.floor(t * 18)];
        if (this.id === 'will') return ['special', t < 0.18 ? 0 : !this.spDone ? 1 : 2];
        if (this.id === 'nate') return t < 0.16 || t > 1.0 ? ['special', 0] : ['special', 1 + (Math.floor(t * 8) % 2)];
        if (this.id === 'heather') return t < 0.12 ? ['special', 0] : t < 0.8 ? ['special', 1 + (Math.floor(t * 14) % 2)] : ['special', 3];
        return ['special', t < 0.22 ? 0 : t < 0.36 ? 1 : 2];
      }
    }
    return ['idle', 0];
  }
  drawShout() {  // speech bubble: "It's time for some Ativan!" (v0.8: each hero can have their own wording, d.shout)
    const L = this.d.shout || ["IT'S TIME FOR", 'SOME ATIVAN!'];
    const w = Math.max(112, Math.max(...L.map((q) => q.length)) * 8 + 8), h = 22;
    const X = Math.round(this.x - W.camX), Y = Math.round(this.y + offY() - this.z - this.h - 40);
    const bx = Math.max(2, Math.min(G.VW - w - 2, X - w / 2));
    rect(bx - 1, Y - 1, w + 2, h + 2, '#1a1020'); rect(bx, Y, w, h, '#ffffff');
    rect(X - 3, Y + h, 6, 3, '#ffffff'); rect(X - 1, Y + h + 3, 3, 3, '#ffffff');
    text(L[0], bx + w / 2, Y + 2, { col: '#1a1020', align: 'center', shadow: null });
    text(L[1], bx + w / 2, Y + 12, { col: '#7a3ab8', align: 'center', shadow: null });
  }
  // ---- v0.8 speech bubbles: heroes with d.lines say something in character (Nasty Nate: lazy). ev = spawn, idle, grab, food,
  // weapon, hurt, ko, revive, codeblue, special, zone, clear (v0.10.1: + throw, drop = a patient you knocked down). A line shows ~2.6 s; `force` skips the cooldown (big moments).
  say(ev, force = false) {
    const L = this.d.lines && this.d.lines[ev];
    if (!L || !L.length || (!force && W.t < this.sayCd)) return null;
    let i = Math.floor(W.rnd() * L.length);
    if (L.length > 1 && i === this.sayLast[ev]) i = (i + 1) % L.length;
    const read = 2.6 + Math.max(0, L[i].length - 34) * 0.045;  // v0.10: long lines (Heather's) stay up long enough to read
    this.sayLast[ev] = i; this.sayS = L[i]; this.sayUntil = Math.max(W.t, this.shoutT || 0) + read; this.sayCd = this.sayUntil + 1.9;
    W.stats.says = (W.stats.says || 0) + 1; (W.said || (W.said = [])).push(L[i]);
    return L[i];
  }
  sayTick(dt, I) {  // spawn line (once per floor, when he can first act) + the idle line after ~6 s doing nothing
    if (!this.d.lines) return;
    if (this.hiLv !== W.lv && this.canAct()) { this.hiLv = W.lv; this.say('spawn', true); }
    const busy = Math.hypot(I.mx, I.my) > 0.15 || I.atk || I.jmp || I.prs.sp || I.prs.grab || this.st !== 'idle';
    this.idleT = busy ? 0 : this.idleT + dt;
    if (this.idleT > 6) { this.idleT = -6; if (this.say('idle', true)) sfx(this.d.idleSfx || 'yawn', { vol: 0.5 }); }
    if (this.sayS && W.t > this.sayUntil) this.sayS = null;
  }
  drawSay() {
    if (!this.sayS || this.shoutT > W.t || this.st === 'out') return;
    const words = this.sayS.split(' '), lines = [];
    let cur = '';
    const wrapN = this.sayS.length > 60 ? 27 : this.sayS.length > 36 ? 22 : 18;  // v0.10: wider bubbles for long lines so they stay 3-4 rows
    for (const wd of words) { if (cur && (cur + ' ' + wd).length > wrapN) { lines.push(cur); cur = wd; } else cur = cur ? cur + ' ' + wd : wd; }
    if (cur) lines.push(cur);
    const w = Math.max(...lines.map((q) => q.length)) * 8 + 8, h = lines.length * 10 + 4;
    const X = Math.round(this.x - W.camX), head = Math.round(this.y + offY() - this.z - this.h - 6 - (this.held ? 14 : 0));  // clear the <SLAM TOSS> hint
    const Y = Math.max(32, head - h - 6), bx = Math.max(2, Math.min(G.VW - w - 2, X - w / 2));
    const a = Math.min(1, (this.sayUntil - W.t) / 0.25);
    rect(bx - 1, Y - 1, w + 2, h + 2, '#1a1020', a); rect(bx, Y, w, h, '#ffffff', a);
    const tx = Math.max(bx + 3, Math.min(bx + w - 6, X));
    if (head - (Y + h) > 1) { rect(tx - 2, Y + h, 5, 2, '#ffffff', a); rect(tx - 1, Y + h + 2, 3, 2, '#ffffff', a); }
    lines.forEach((q, k) => text(q, bx + w / 2, Y + 3 + k * 10, { col: '#1a1020', align: 'center', shadow: null, alpha: a }));
  }
  drawCarry(name, i) {  // the prop rides on her hands, overhead (it swings up from the floor during the lift)
    const p = this.carry, h = this.handOf(name, i), sn = propSprite(p), [w, ph] = sprSize(sn);
    const top = Math.min(h[1], h[4] ?? h[1]);
    let X = this.x - W.camX + this.face * ((h[0] + (h[3] ?? h[0])) / 2), Y = this.y + offY() - this.z + top + 3;
    if (this.st === 'lift' && this.t < 0.18) {  // lerp from where it stood
      const k = Math.min(1, this.t / 0.18), fx = this.x - W.camX + this.face * this.liftDX, fy = this.y + offY() + this.liftDY;
      X = fx + (X - fx) * k; Y = fy + (Y - fy) * k;
    }
    if (this.inv > 0 && Math.floor(W.t * 20) % 2) return;
    spr(sn, Math.round(X - w / 2), Math.round(Y - ph));
  }
  draw() {
    if (this.st === 'out') return;
    const [name, i] = this.pose();
    if (this.st === 'super') { const X = this.x - W.camX, Y = this.y + offY() - 30; ellipse(X, Y, 26 + Math.sin(W.t * 30) * 3, 30, '#8ad8ff', 0.35); }
    if (this.st === 'teamwait' || this.st === 'teamup') { const X = this.x - W.camX, Y = this.y + offY() - this.z - 28; ellipse(X, Y, 22 + Math.sin(W.t * 24) * 3, 30, this.st === 'teamup' ? '#ffffff' : '#ffe84a', 0.35); }
    if (this.speedT > 0 && Math.floor(W.t * 10) % 2) ellipse(this.x - W.camX, this.y + offY() - 26, 14, 28, '#ffe84a', 0.18);
    if (this.st === 'special' && this.id === 'heather' && this.t > 0.12 && this.t < 0.8) {  // v0.10 clothesline speed streaks behind her (arm height + legs)
      const X = this.x - W.camX, Y = this.y + offY() - this.z;
      for (const [dy, len, al] of [[-40, 30, 0.75], [-33, 20, 0.5], [-24, 26, 0.4], [-12, 16, 0.35]]) rect(this.face > 0 ? X - 10 - len : X + 10, Y + dy + (Math.floor(W.t * 30) % 2), len, 1, '#ffffff', al);
    }
    if (this.st === 'special' && this.id === 'nate') {  // v0.8 the rolling office chair under Nate (backrest behind him)
      spr('chair' + (Math.floor(W.t * 14) % 2), this.x - W.camX - this.face * 3, this.y + offY() - this.z + 1, { ax: 13, ay: 34, flip: this.face < 0 });
    }
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
    if (this.carry && CARRY_OK.has(this.st)) this.drawCarry(name, i);
    if (this.st === 'ativan') {  // the syringe in her jabbing hand
      const h = this.handOf(name, i), a = (h[2] ?? 90) * Math.PI / 180, rot = Math.atan2(Math.cos(a), Math.sin(a)), f = this.face < 0;
      spr('ativan', this.x - W.camX + this.face * h[0], this.y + offY() - this.z + h[1], { ax: 4, ay: 4, rot: f ? -rot : rot, flip: f });
    }
    if (this.shoutT > W.t) this.drawShout();
    if (this.st === 'dizzy') spr('dizzy' + (Math.floor(W.t * 8) % 3), this.x - W.camX, this.y + offY() - this.z - this.h - 4, { ax: 11 });
    if (this.st === 'teamwait' && Math.floor(W.t * 6) % 2) text('TEAM UP? HOLD SP!', this.x - W.camX, this.y + offY() - this.h - 26, { col: '#ffe84a', align: 'center' });
    if (this.slot !== undefined && W.heroes.length > 1 && this.st !== 'dead') text(`${this.slot + 1}P`, this.x - W.camX, this.y + offY() - this.z - this.h - 14, { col: this.slot ? '#8ad8ff' : '#ffe84a', align: 'center' });
  }
}
const A_DASH = ATTACKS.dash.dur;

// ---- Charge Nurse team-up
function startTeam(a, b) {
  for (const h of [a, b]) { h.meter = Math.max(0, h.meter - 50); if (h.held) h.release(); h.set('teamup'); h.inv = 2; h.vx = 0; }
  const cx = (a.x + b.x) / 2, cy = (a.y + b.y) / 2;
  W.team = { t: 0, x: cx, y: cy, a, b, hit: false };
  W.stop = 0.12; W.flash = 1; W.flashCol = '#ffffff'; sfx('charge'); shake(4);
  word('w_charge', cx, cy, 64); floatText('CHARGE NURSE, COMING THROUGH!', cx, cy, 96, '#ffe84a');
  for (const h of [a, b]) if (h.say('teamup', true)) break;  // v0.10.1 Charge Jackie has a line for it
  W.stats.teamups = (W.stats.teamups || 0) + 1;
}
function teamBlast(T) {
  shake(10); sfx('explosion'); sfx('zap'); W.flash = 0.9; W.flashCol = '#ffe84a';
  let n = 0;
  for (const e of W.enemies) {
    if (!e.alive || e.st === 'dead' || e.x < W.camX - 10 || e.x > W.camX + G.VW + 10) continue;
    const by = n++ % 2 ? T.b : T.a;
    e.takeHit({ dmg: 70, dir: Math.sign(e.x - T.x) || 1, kb: 200, down: true, from: by, force: true });
    addFx({ type: 'spark', kind: 'bigspark', x: e.x, y: e.y, z: 30, dur: 0.3 }); addFx({ type: 'spark', kind: 'bluespark', x: e.x, y: e.y, z: 16, dur: 0.3 });
  }
  if (W.boss && W.boss.alive) W.boss.takeHit({ dmg: W.boss.maxHp * 0.15, dir: 1, from: T.a, force: true });
  for (const p of W.props) if (p.st < 2 && p.x > W.camX - 10 && p.x < W.camX + G.VW + 10) hitProp(p, 30, { dir: Math.sign(p.x - T.x) || 1, kb: 240, from: T.a });
  addScore(T.a, 1500); addScore(T.b, 1500);
}
const RAYC = ['#ffe84a', '#ffffff', '#ff8ac0', '#ffffff'];
export function drawTeamBack() {  // rotating starburst behind everyone
  const T = W.team; if (!T) return;
  const c = G.ctx, X = T.x - W.camX, Y = T.y + offY() - 34, t = T.t;
  c.save(); c.globalAlpha = Math.min(0.6, 0.25 + t * 2) * (t > 1.3 ? Math.max(0, (1.6 - t) / 0.3) : 1);
  const n = 18, R = 520;
  for (let i = 0; i < n; i++) {
    const a0 = i / n * Math.PI * 2 + t * 1.6, a1 = a0 + Math.PI / n * 0.7;
    c.fillStyle = RAYC[i % 4]; c.beginPath(); c.moveTo(X, Y); c.lineTo(X + Math.cos(a0) * R, Y + Math.sin(a0) * R); c.lineTo(X + Math.cos(a1) * R, Y + Math.sin(a1) * R); c.closePath(); c.fill();
  }
  c.restore();
}
export function drawTeamFront() {  // shock rings, pixel confetti and the arcade cut-in band with both nurses
  const T = W.team; if (!T) return;
  const VW = G.VW, X = T.x - W.camX, Y = T.y + offY(), t = T.t;
  if (t > 0.75) { const k = t - 0.75; ['#ffe84a', '#ff8ac0', '#8ad8ff'].forEach((col, j) => { const r = k * 460 - j * 34; if (r > 4) ring(X, Y, r, r * 0.34, col, 3, Math.max(0, 1 - k * 1.1)); }); }
  for (let i = 0; i < 28; i++) {
    const a = i * 2.4 + t * 4, r = 14 + ((t * 140 + i * 19) % 170), s = (i % 3) + 2;
    rect(Math.round(X + Math.cos(a) * r), Math.round(Y - 34 + Math.sin(a) * r * 0.6), s, s, ['#ffffff', '#ffe84a', '#ff8ac0', '#8ad8ff'][i % 4]);
  }
  if (t < 1.0) {
    const k = Math.min(1, t / 0.18), out = t > 0.8 ? (t - 0.8) / 0.2 : 0, by = 72, bh = 54;
    const off = Math.round((1 - k) * -VW + out * VW);
    rect(off, by - 3, VW, bh + 6, '#ffe84a', 0.95); rect(off, by, VW, bh, '#1a1020', 0.92);
    for (let i = 0; i < 12; i++) rect(off + ((i * 53 + Math.floor(t * 600)) % (VW + 40)) - 20, by + 6 + (i * 13) % (bh - 10), 18, 1, '#ffffff', 0.5);
    const fa = `face_${T.a.id}`, fb = `face_${T.b.id}`;
    spr(fa, off + 10, by + 3, { scale: 1.35 }); spr(fb, off + VW - 10, by + 3, { scale: 1.35, flip: true });
    const [w, h] = sprSize('w_charge'); spr('w_charge', off + VW / 2, by + bh / 2, { ax: w / 2, ay: h / 2, scale: Math.min(1, (VW - 130) / w) * (0.9 + Math.sin(t * 30) * 0.05) });
  }
}
