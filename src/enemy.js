// Patients. Each type has one signature move: the Wanderer hugs, the Call-light Spammer throws remotes and pudding cups,
// the Escape Artist slaps and runs, the IV-pole Swinger sweeps, the Sundowner charges, the Visitor is a tough brute.
// v0.2: every patient wears the checked gown + yellow grip socks with randomized hair / skin; the Crutch Crusader pokes,
// the Bell Ringer whips a call bell on its cord (dizzies), and the elite Frequent Flyer canes you up close and throws
// syringe darts and (comedic) full urinals that splash and leave a slippery puddle.
import { G, text, spr, tintSheet } from './gfx.js';
import { ENEMIES, VARIANTS, Y_MIN, Y_MAX } from './data.js';
import { W, offY, addShot, addFx, floatText, shake, spark, addScore, word, breakProp, propBox, dropItem } from './world.js';
import { Actor, strike, clampY } from './actor.js';
import { sfx } from './sound.js';

// A small pool of random looks per patient type (hair colour, skin tone, green or olive gown; elites: red or blue socks).
const POOL = {}, POOL_N = 6;
const pick = (a) => a[Math.floor(Math.random() * a.length)];
export function lookFor(kind, n) {
  const d = ENEMIES[kind], A = G.atlas.chars[d.sheet], P = G.atlas.palettes;
  if (!A || !A.pal || !P) return d.sheet;
  const pool = POOL[kind] || (POOL[kind] = []);
  const i = n % POOL_N;
  if (!pool[i]) {
    const hair = pick(P.hair), skin = pick(P.skin), gown = pick(P.gown), sock = d.elite ? P.sock_elite[i % P.sock_elite.length] : P.sock[0];
    const pal = A.pal, pairs = [];
    pal.hair.forEach((c, j) => pairs.push([c, hair[j]])); pal.skin.forEach((c, j) => pairs.push([c, skin[j]]));
    pal.gown.forEach((c, j) => pairs.push([c, gown[j]])); pal.sock.forEach((c, j) => pairs.push([c, sock[j]]));
    pool[i] = tintSheet(d.sheet, `${i}`, pairs);
  }
  return pool[i];
}

export class Enemy extends Actor {
  constructor(kind, x, y, variant = 0) {
    const d = ENEMIES[kind];
    super(VARIANTS[kind] ? VARIANTS[kind][variant % VARIANTS[kind].length] : lookFor(kind, variant), x, y);
    this.kind = kind; this.d = d; this.maxHp = this.hp = Math.round(d.hp * W.diff.hp * (W.heroes.length > 1 ? 1.25 : 1));
    this.cd = 0.8 + W.rnd() * 1.2; this.armor = d.armor || 0; this.armorT = 0; this.big = !!d.big; this.h = d.big ? 62 : 50; this.w = d.big ? 20 : 14;
    this.side = W.rnd() < 0.5 ? -1 : 1; this.wob = W.rnd() * 6; this.target = null; this.tx = x; this.ty = y; this.speechT = 2 + W.rnd() * 6;
  }
  hittable() { return !['dead', 'thrown', 'enter_door'].includes(this.st) && !(this.st === 'down' || this.st === 'getup'); }
  grabbable() { return ['idle', 'walk', 'hurt', 'dizzy', 'flee'].includes(this.st) && this.z === 0; }
  attacking() { return ['windup', 'atk', 'hug', 'charge', 'recover'].includes(this.st); }

  takeHit({ dmg, dir, kb, stun, down, dizzy, from, held, force }) {
    if (!force && !this.hittable()) return;
    if (this.st === 'hug' && from && from.isHero) this.breakHug();
    this.hp -= dmg; this.flash = 0.12;
    if (from) addScore(from, dmg * 8);
    if (this.hp <= 0) {
      this.hp = 0; if (this.holder) { this.holder.held = null; this.holder = null; }
      this.knock(dir, Math.max(kb || 0, 130), 200); this.koBy = from; return;
    }
    if (held) { this.flash = 0.12; return; }
    if (this.armor > 0 && !down && !force) { this.armor--; this.armorT = 1.6; return; }  // brute shrugs off jabs
    if (down || force) { if (this.holder) { this.holder.held = null; this.holder = null; } this.knock(dir, kb || 140, 190); return; }
    if (dizzy) { this.set('dizzy'); this.stun = dizzy; this.vx = 0; return; }
    this.set('hurt'); this.stun = stun || 0.3; this.vx = dir * (kb || 30);
  }
  thrownBy(h, dir, k) {
    this.holder = null; this.set('thrown'); this.face = -dir; this.vx = dir * 210 * k; this.vz = 170; this.z = 8; this.thrower = h; this.k = k; this.hitSet = new Set([this]);
  }
  breakHug() {
    if (this.victim) { const v = this.victim; this.victim = null; if (v.st === 'grabbed') v.set('idle'); v.grabber = null; }
    this.set('hurt'); this.stun = 0.5; this.vx = -this.face * 60;
  }
  pickTarget() {
    const hs = W.heroes.filter((h) => h.alive && !['dead', 'out'].includes(h.st));
    if (!hs.length) return null;
    if (this.target && hs.includes(this.target) && W.rnd() > 0.01) return this.target;
    hs.sort((a, b) => Math.abs(a.x - this.x) + Math.abs(a.y - this.y) * 2 - (Math.abs(b.x - this.x) + Math.abs(b.y - this.y) * 2));
    return hs[0];
  }
  tokens(h) { return W.enemies.filter((e) => e !== this && e.target === h && e.attacking()).length; }

  update(dt) {
    this.t += dt; this.flash = Math.max(0, this.flash - dt); this.inv = Math.max(0, this.inv - dt); this.cd -= dt;
    if (this.armorT > 0 && (this.armorT -= dt) <= 0) this.armor = this.d.armor || 0;
    if (this.st === 'dead') { if (this.t > 1.6) this.alive = false; if (this.t < dt * 1.5) this.onKO(); return; }
    if (this.fallStep(dt, 0.7)) return;
    const fn = this['s_' + this.st]; if (fn) fn.call(this, dt);
    if (!['enter', 'enter_door', 'thrown', 'charge', 'flee'].includes(this.st)) this.y = clampY(this.y);
    if (--this.speechT < 0) this.speechT = 0;
  }
  onKO() {
    const k = this.koBy;
    if (k && k.isHero) { k.kos++; addScore(k, this.d.score); }
    W.stats.kos++;
    floatText(this.d.ko[Math.floor(W.rnd() * this.d.ko.length)], this.x, this.y, 50, '#ffffff');
    addFx({ type: 'zzz', x: this.x + 4, y: this.y, z: 20, dur: 1.5 });
    sfx(this.d.voice, { vol: 0.35, rate: 0.8 });
    if (this.d.drop && W.rnd() < this.d.drop[1]) dropItem(this.d.drop[0], this.x, this.y);
  }
  // ------------------------------------------------------------------ states
  s_enter(dt) {  // walk in from a screen edge, a door or an elevator to (tx, ty)
    const dx = this.tx - this.x, dy = this.ty - this.y, l = Math.hypot(dx, dy);
    const sp = Math.max(40, this.d.speed) * (this.kind === 'escape' ? 1 : 1.2);
    if (l < 3) { this.set('idle'); return; }
    this.x += dx / l * sp * dt; this.y += dy / l * sp * dt; if (Math.abs(dx) > 1) this.face = Math.sign(dx);
  }
  s_enter_door(dt) { if (this.t > 0.35) { this.st = 'enter'; } }
  s_idle(dt) { this.think(dt); }
  s_walk(dt) { this.think(dt); }
  think(dt) {
    const h = this.target = this.pickTarget();
    if (!h) { this.st = 'idle'; return; }
    const dx = h.x - this.x, dy = h.y - this.y, adx = Math.abs(dx);
    if (Math.abs(dx) > 4) this.face = Math.sign(dx);
    const K = this.kind, d = this.d;
    // speech bubbles now and then
    if (this.speechT <= 0 && W.rnd() < 0.003) { this.speechT = 6; const L = { wanderer: ['Are you my nurse?', 'Where am I?'], spammer: ['NURSE! NURSE!', 'My TV is broken!'], escape: ['Catch me!', "I'm going home!"],
      ivswing: ['I need ice chips!', 'Fore!'], sundowner: ['Who are you?!', 'Get off my lawn!'], visitor: ['Who is in charge?!', 'I know my rights!'],
      crutch: ['Outta my way!', 'I can walk fine!'], bell: ['*DING DING DING*', 'Room service!'], elite: ["I've been here 40 times!", 'I want my usual room!'] }[K]; floatText(L[Math.floor(W.rnd() * L.length)], this.x, this.y, 64, '#ffffff'); sfx(d.voice, { vol: 0.3 }); }
    let gx, gy = h.y, want = d.reach * 0.85;
    const busy = this.tokens(h) >= (W.diff.cap >= 5 ? 3 : 2) && !this.attacking();
    if (K === 'spammer' || (K === 'elite' && this.cd > 0.3)) { want = d.keep; this.side = Math.sign(this.x - h.x) || this.side; }
    else if (busy || this.cd > 0.6) { want = 62 + (this.wob % 3) * 14; gy = h.y + Math.sin(W.t * 0.8 + this.wob) * 22; }
    else this.side = Math.sign(this.x - h.x) || this.side;
    gx = h.x + this.side * want;
    // keep on screen
    gx = Math.max(W.camX + 12, Math.min(W.camX + G.VW - 12, gx));
    const mx = gx - this.x, my = gy - this.y, ml = Math.hypot(mx, my);
    const sp = d.speed * (K === 'escape' ? 0.9 : 1);
    if (ml > 4) { this.x += mx / ml * sp * dt; this.y += my / ml * sp * 0.8 * dt; this.st = 'walk'; } else this.st = 'idle';
    if (K === 'sundowner' && this.cd <= 0 && Math.abs(dy) < 6 && adx > 40 && adx < 220) return this.begin('windup');
    if (K === 'elite' && this.cd <= 0 && !busy && Math.abs(dy) < 10) {  // cane up close, otherwise throw something
      if (adx < d.reach + 6) { this.throwKind = null; return this.begin('windup'); }
      if (adx > 60 && adx < 260) { this.throwKind = W.rnd() < 0.55 ? 'toss' : 'lob'; return this.begin('windup'); }
    }
    if (K === 'elite') return;
    if (this.cd <= 0 && !busy && Math.abs(dy) < (K === 'spammer' ? 10 : 6)) {
      if (K === 'spammer' && adx > 50) return this.begin('windup');
      if (K !== 'spammer' && K !== 'sundowner' && adx < d.reach + 6 && adx > 6) return this.begin('windup');
      if (K === 'sundowner' && adx < 30) return this.begin('windup');
    }
  }
  begin(st) { this.set(st); this.face = this.target ? Math.sign(this.target.x - this.x) || this.face : this.face; this.hitDone = false; }
  s_windup(dt) {
    const K = this.kind;
    const wt = { wanderer: 0.42, spammer: 0.4, escape: 0.22, ivswing: 0.5, sundowner: 0.55, visitor: 0.48, crutch: 0.42, bell: 0.4, elite: this.throwKind ? 0.42 : 0.36 }[K];
    if (K === 'sundowner' && Math.floor(this.t * 20) % 2) this.x += (W.rnd() - 0.5) * 2;
    if (this.t >= wt) {
      if (K === 'wanderer') { this.set('hug'); this.vx = this.face * 90; this.hugT = 0; this.victim = null; }
      else if (K === 'sundowner') { this.set('charge'); this.vx = this.face * 175; sfx(this.d.voice, { vol: 0.4, rate: 1.4 }); this.hitSet = new Set(); }
      else { this.set('atk'); this.hitDone = false; }
    }
  }
  s_atk(dt) {
    const K = this.kind, d = this.d, dm = W.diff.dmg;
    if (!this.hitDone && this.t > 0.04) {
      this.hitDone = true;
      if (K === 'spammer') {
        const pud = W.rnd() < 0.35;
        addShot({ kind: 'enemy', spr: pud ? 'pudding' : 'remote', x: this.x + this.face * 10, y: this.y, z: 36, vx: this.face * 165, vz: 40, grav: 120, owner: this, dmg: 6, spin: pud ? 0 : 12, life: 2.2 });
        sfx('whoosh', { vol: 0.4 }); if (W.rnd() < 0.4) floatText(pud ? 'PUDDING!' : 'NURSE!', this.x, this.y, 60, '#ffffff');
      } else if (K === 'elite' && this.throwKind) {
        if (this.throwKind === 'toss') {
          addShot({ kind: 'enemy', spr: 'syringe', x: this.x + this.face * 12, y: this.y, z: 36, vx: this.face * 235, vz: 0, grav: 0, owner: this, dmg: 6, life: 1.6 });
          sfx('whoosh', { vol: 0.45, rate: 1.4 }); if (W.rnd() < 0.4) floatText('FLU SHOT!', this.x, this.y, 62, '#ffffff');
        } else {
          addShot({ kind: 'enemy', spr: 'urinal', x: this.x + this.face * 10, y: this.y, z: 42, vx: this.face * 120, vz: 150, grav: 330, owner: this, dmg: 8, spin: 7, splash: true, life: 2.4 });
          sfx('whoosh', { vol: 0.45, rate: 0.8 }); if (W.rnd() < 0.5) floatText('INCOMING!', this.x, this.y, 62, '#ffffff');
        }
      } else if (K === 'elite') strike(this, { box: [2, 38], z: [16, 50], dmg: 9, kb: 120, stun: 0.45, sfxName: 'punch1', wordName: 'w_smack', props: false });
      else if (K === 'crutch') strike(this, { box: [0, 46], z: [16, 46], depth: 10, dmg: 9, kb: 140, down: true, sfxName: 'clang', wordName: 'w_poke', props: false });
      else if (K === 'bell') { strike(this, { box: [4, 64], z: [20, 50], depth: 12, dmg: 6, kb: 30, dizzy: 0.9, sfxName: 'ding', wordName: 'w_ding', props: false }); sfx('ding', { vol: 0.5, rate: 1.3 }); }
      else if (K === 'escape') strike(this, { box: [4, 24], z: [20, 48], dmg: 5, kb: 40, stun: 0.3, sfxName: 'punch1', props: false });
      else if (K === 'ivswing') strike(this, { box: [0, 56], z: [10, 50], depth: 12, dmg: 10, kb: 140, down: true, sfxName: 'clang', props: false });
      else if (K === 'visitor') strike(this, { box: [4, 36], z: [18, 56], dmg: 14, kb: 160, down: true, sfxName: 'heavy', wordName: 'w_wham', props: false });
    }
    const rec = { spammer: 0.45, escape: 0.3, ivswing: 0.55, visitor: 0.6, crutch: 0.5, bell: 0.5, elite: 0.45 }[K] || 0.4;
    if (this.t > rec) {
      this.cd = d.cd[0] + W.rnd() * (d.cd[1] - d.cd[0]);
      if (K === 'escape') { this.set('flee'); this.fleeDir = -this.face; } else this.set('idle');
    }
  }
  s_flee(dt) {  // escape artist runs off after a slap, then circles back
    this.x += this.fleeDir * this.d.speed * 1.2 * dt; this.face = this.fleeDir;
    const edgeL = W.camX + 14, edgeR = W.camX + G.VW - 14;
    if (this.x < edgeL || this.x > edgeR || this.t > 1.1) { this.x = Math.max(edgeL, Math.min(edgeR, this.x)); this.set('idle'); if (W.rnd() < 0.4) floatText('Nyah nyah!', this.x, this.y, 60, '#ffffff'); }
  }
  s_hug(dt) {
    if (!this.victim) {
      this.slide(dt, 5);
      for (const h of W.heroes) {
        if (!h.hittable() || h.st === 'grabbed' || Math.abs(h.y - this.y) > 7 || Math.abs(h.x - (this.x + this.face * 14)) > 12) continue;
        this.victim = h; h.grabber = this; if (h.held) h.release(); h.set('grabbed'); h.mash = 0; floatText('Are you my nurse?', this.x, this.y, 64, '#ffffff'); sfx('voice0', { vol: 0.4 }); break;
      }
      if (!this.victim && this.t > 0.45) { this.cd = 1.4; this.set('idle'); }
      return;
    }
    const v = this.victim;
    if (v.st !== 'grabbed') { this.victim = null; this.set('idle'); this.cd = 1.6; return; }
    this.hugT += dt;
    if (this.hugT > 0.55) { this.hugT = 0; v.hp = Math.max(1, v.hp - 3 * W.diff.dmg); v.flash = 0.1; sfx('hurt', { vol: 0.3 }); addFx({ type: 'heart', x: (v.x + this.x) / 2, y: this.y, z: 46, dur: 0.8 }); }
  }
  s_charge(dt) {
    this.x += this.vx * dt;
    strike(this, { box: [-4, 18], z: [6, 46], dmg: 10, kb: 150, down: true, sfxName: 'heavy', once: this.hitSet, props: false });
    if (Math.floor(this.t * 12) % 2 === 0) addFx({ type: 'dust', x: this.x - this.face * 8, y: this.y, dur: 0.3 });
    if (this.t > 1.5 || this.x < W.camX + 6 || this.x > W.camX + G.VW - 6) { this.x = Math.max(W.camX + 8, Math.min(W.camX + G.VW - 8, this.x)); this.set('dizzy'); this.stun = 1.1; this.cd = 2.4; floatText('Where am I?', this.x, this.y, 60, '#ffffff'); }
  }
  s_hurt(dt) { this.slide(dt); if (this.t > this.stun) { this.set('idle'); this.cd = Math.max(this.cd, 0.35); } }
  s_dizzy(dt) { if (this.t > this.stun) { this.set('idle'); this.cd = Math.max(this.cd, 0.4); } }
  s_held(dt) { if (!this.holder || this.holder.held !== this) { this.holder = null; this.set('hurt'); this.stun = 0.2; } }
  s_thrown(dt) {
    const k = this.k || 1;
    // knock over anyone in the way, smash props
    for (const e of W.enemies) {
      if (this.hitSet.has(e) || !e.alive || !e.hittable() || Math.abs(e.y - this.y) > 10 || Math.abs(e.x - this.x) > 16 || this.z > 40) continue;
      this.hitSet.add(e); e.takeHit({ dmg: 12 * k, dir: Math.sign(this.vx), kb: 150, down: true, from: this.thrower }); spark(e.x, e.y, 24, 'bigspark'); sfx('heavy'); shake(3); addScore(this.thrower, 200);
    }
    if (W.boss && W.boss.alive && !this.hitSet.has(W.boss) && Math.abs(W.boss.y - this.y) < 14 && Math.abs(W.boss.x - this.x) < 26) { this.hitSet.add(W.boss); W.boss.takeHit({ dmg: 10 * k, dir: Math.sign(this.vx), from: this.thrower }); }
    for (const p of W.props) { if (p.st >= 2 || this.hitSet.has(p)) continue; const b = propBox(p); if (Math.abs(p.y - this.y) < 12 && this.x > b.x0 - 6 && this.x < b.x1 + 6) { this.hitSet.add(p); breakProp(p, 12, this.thrower); } }
    if (this.airborne(dt)) {
      this.hp -= 18 * k; this.flash = 0.12; shake(4); sfx('heavy'); word('w_slam', this.x, this.y, 0); addFx({ type: 'dust', x: this.x, y: this.y, dur: 0.4 });
      if (this.hp <= 0) { this.hp = 0; this.koBy = this.thrower; }
      this.vx *= 0.4; this.vz = 90; this.z = 0.1; this.set('fall'); this.bounced = true;
    }
    this.x = Math.max(W.camX - 30, Math.min(W.camX + G.VW + 30, this.x));
  }
  // ------------------------------------------------------------------ drawing
  pose() {
    const st = this.st, t = this.t, K = this.kind;
    switch (st) {
      case 'idle': return ['idle', Math.floor(W.t * 2 + this.wob)];
      case 'walk': case 'enter': case 'flee': return ['walk', Math.floor(W.t * (K === 'escape' || st === 'flee' ? 12 : 7) + this.wob)];
      case 'enter_door': return ['idle', 0];
      case 'windup': return K === 'sundowner' ? ['idle', 0] : [K === 'elite' && this.throwKind ? this.throwKind : 'atk', 0];
      case 'atk': return K === 'elite' && this.throwKind ? [this.throwKind, 1] : ['atk', K === 'ivswing' ? (t < 0.2 ? 1 : 2) : 1];
      case 'hug': return this.victim ? ['hug', Math.floor(W.t * 4)] : ['atk', t < 0.12 ? 0 : 1];
      case 'charge': return ['atk', Math.floor(W.t * 14)];
      case 'hurt': return ['hurt', this.flash > 0 ? 0 : 1];
      case 'dizzy': return ['dizzy', Math.floor(W.t * 4)];
      case 'held': return ['held', 0];
      case 'thrown': case 'fall': return ['fall', 0];
      case 'down': return ['down', 0];
      case 'dead': return ['sleep', 0];
      case 'getup': return ['getup', 0];
    }
    return ['idle', 0];
  }
  draw() {
    if (this.st === 'dead' && this.t > 1.0 && Math.floor(this.t * 16) % 2) return;
    const [n, i] = this.pose();
    const dx = this.st === 'windup' && this.kind !== 'sundowner' ? 0 : 0;
    this.drawSprite(n, i, { dx });
    const X = this.x - W.camX, Y = this.y + offY() - this.z;
    if (this.st === 'dizzy') spr('dizzy' + (Math.floor(W.t * 8) % 3), X, Y - this.h - 2, { ax: 11 });
    if (this.st === 'windup' && Math.floor(this.t * 12) % 2) text('!', X + this.face * 6, Y - this.h - 12, { col: '#ff5a3a', align: 'center' });
  }
}
