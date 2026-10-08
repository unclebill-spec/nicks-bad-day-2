// v0.13 Boss: "DR." PHIL-IN, in the psych ward's group room. A patient in a stolen white lab coat with a crayon MD badge
// and a stethoscope, who is SURE he's the attending. ~1.3x a nurse's height. He swings his clipboard, "writes orders"
// (paper orders flutter out and patients come running: W.director.backup()), and twirls his stethoscope like a lasso that
// yanks a nurse in. Hard hits (or 4 in a row) knock him down. Phase 2 (half health): "STAT!" -> faster, more orders.
// Defeated: he lies down on the group-room floor for a nap: "Discharge... me... zzz". Comedic, never mean.
import { G, text, spr, ellipse } from './gfx.js';
import { W, offY, addShot, addFx, floatText, shake, word, addScore } from './world.js';
import { Actor, strike, clampY } from './actor.js';
import { sfx } from './sound.js';

const TOP = 96;
export const PHIL = { hp: 420, speed: [64, 84], swing: 10, lasso: 8, order: 5, knockCd: 2.4, orderCd: [9, 6.5] };
export const PHIL_LINES = {
  greet: ["I'm the doctor here!"],
  taunt: ["I'm the doctor here!", "Nurse, I'm ordering 10 of Dilaudid!", 'Take two of these and call me never.', 'I went to medical school! On TV!', 'Who paged me? Was it me?'],
  write: ['ORDERS: MORE PATIENTS, STAT!', 'Consult! CONSULT!', 'Admit EVERYBODY!', 'Per my orders!'],
  hurt: ['Malpractice!', "I'm calling the ethics board!", 'Not the coat! It is on loan!', 'Ow! I need a doctor! ...Oh wait.'],
  lasso: ['Come here, I need a vital sign!', 'Deep breath in!', 'Say AHH!'],
  stat: ['STAT! STAT! STAT!', 'CODE BROWN! I mean... CODE ME!'],
  ko: 'Discharge... me... zzz',
};
const pick = (a) => a[Math.floor(W.rnd() * a.length)];

export class PhilIn extends Actor {
  constructor(x, y) {
    super('philin', x, y);
    this.isBoss = true; this.name = '"DR." PHIL-IN'; this.big = true; this.w = 22; this.h = 62; this.p2label = 'STAT!';
    this.maxHp = this.hp = Math.round(PHIL.hp * W.diff.hp * (W.heroes.length > 1 ? 1.35 : 1));
    this.face = -1; this.phase = 1; this.shown = 0; this.cd = 1.2; this.knockCd = 0; this.orderCd = 4; this.hits = 0;
    this.set('enter');
  }
  hint() { return this.st === 'lasso' && this.t < 0.6 ? 'DODGE THE STETHOSCOPE!' : this.st === 'write' ? 'HE IS WRITING ORDERS! HIT HIM!' : null; }
  hittable() { return !['enter', 'defeat', 'fall', 'down', 'getup', 'stat'].includes(this.st); }
  grabbable() { return false; }
  takeHit({ dmg, dir, kb, down, from, force }) {
    if (!this.hittable() && !force) return;
    const d = this.st === 'write' ? dmg * 1.25 : dmg;  // writing orders = distracted: a bit more damage
    this.hp -= d; this.flash = 0.1; if (from) addScore(from, d * 10);
    if (this.hp <= 0) { this.hp = 0; this.die(from); return; }
    if (this.phase === 1 && this.hp < this.maxHp * 0.5) { this.phase = 2; this.statNext = true; }
    this.hits++; this.hurtT = 0.2;
    if ((down || this.hits >= 4) && this.knockCd <= 0) { this.hits = 0; this.knockCd = PHIL.knockCd; this.knock(dir || 1, 130, 170); if (W.rnd() < 0.6) floatText(pick(PHIL_LINES.hurt), this.x, this.y, TOP - 10, '#ffffff'); }
  }
  die(from) {
    this.set('defeat'); this.vx = 0; W.stop = 0.4; shake(6); sfx('explosion', { vol: 0.6 }); W.flash = 0.5; W.flashCol = '#ffffff';
    if (from && from.isHero) addScore(from, 10000);
    floatText(PHIL_LINES.ko, this.x, this.y, TOP, '#ffffff'); sfx('philin_ko', { vol: 0.8 });
    for (let i = 0; i < 8; i++) addFx({ type: 'chunk', spr: 'p_order', x: this.x, y: this.y, z: 50, vx: (W.rnd() - 0.5) * 160, vy: 0, vz: 120 + W.rnd() * 120, spin: 8, dur: 1.2 });
    for (const e of W.enemies) if (e.alive && e.st !== 'dead') e.takeHit({ dmg: 999, dir: Math.sign(e.x - this.x) || 1, kb: 120, down: true, force: true });
  }
  target() {
    const hs = W.heroes.filter((h) => h.alive && !['dead', 'out'].includes(h.st));
    if (!hs.length) return null;
    return hs.reduce((a, b) => (Math.abs(a.x - this.x) + Math.abs(a.y - this.y) < Math.abs(b.x - this.x) + Math.abs(b.y - this.y) ? a : b));
  }
  update(dt) {
    this.t += dt; this.flash = Math.max(0, this.flash - dt); this.cd -= dt; this.knockCd -= dt; this.orderCd -= dt; this.hurtT = Math.max(0, (this.hurtT || 0) - dt);
    this.shown = Math.min(1, this.shown + dt * 0.8);
    if (this.stagT > 0 && this.st !== 'defeat') {
      this.stagT -= dt; if (Math.floor(this.stagT * 20) % 3 === 0) addFx({ type: 'spark', kind: 'bluespark', x: this.x + (W.rnd() - 0.5) * this.w, y: this.y, z: 20 + W.rnd() * 50, dur: 0.12 });
    } else if (['fall', 'down', 'getup'].includes(this.st)) { if (!this.fallStep(dt, 0.9) || this.st === 'idle') this.set('chase'); }
    else { const fn = this['s_' + this.st]; if (fn) fn.call(this, dt); }
    this.y = clampY(this.y);
  }
  s_enter(dt) {
    const stopX = W.camX + G.VW * 0.7; this.walking = true;
    if (this.x > stopX) { this.x -= 70 * dt; return; }
    this.walking = false;
    if (!this.greeted) { this.greeted = true; floatText(PHIL_LINES.greet[0], this.x, this.y, TOP, '#ffffff'); sfx('philin', { vol: 0.85 }); }
    if (this.t > 2.6) { this.set('chase'); this.cd = 0.6; }
  }
  s_chase(dt) {
    const h = this.target(); if (!h) return;
    if (this.statNext) { this.statNext = false; return this.set('stat'); }
    const dx = h.x - this.x, dy = h.y - this.y, adx = Math.abs(dx);
    this.face = Math.sign(dx) || this.face;
    const want = this.cd > 0.4 ? 70 : 30, gx = h.x - Math.sign(dx || 1) * want;
    const mx = gx - this.x, my = dy, ml = Math.hypot(mx, my), sp = PHIL.speed[this.phase - 1];
    if (ml > 4) { this.x += mx / ml * sp * dt; this.y += my / ml * sp * 0.72 * dt; this.walking = true; } else this.walking = false;
    if (this.cd > 0) return;
    const minions = W.enemies.filter((e) => e.alive && e.st !== 'dead').length;
    if (this.orderCd <= 0 && minions < 3) { this.set('write'); this.hitDone = false; return; }
    if (adx < 46 && Math.abs(dy) < 10) { this.set('swing'); this.hitDone = false; return; }
    if (adx > 50 && adx < 100 && Math.abs(dy) < 12) { this.set('lasso'); this.hitDone = false; floatText(pick(PHIL_LINES.lasso), this.x, this.y, TOP - 10, '#ffffff'); return; }
    if (W.rnd() < 0.12) { this.set('taunt'); floatText(pick(PHIL_LINES.taunt), this.x, this.y, TOP - 10, '#ffffff'); sfx('philin', { vol: 0.5 }); this.cd = 1; }
  }
  s_swing(dt) {  // clipboard bonk
    if (!this.hitDone && this.t > 0.32) { this.hitDone = true; sfx('whoosh', { vol: 0.6 }); strike(this, { box: [0, 46], z: [14, 66], depth: 12, dmg: PHIL.swing, kb: 150, down: W.rnd() < 0.35, sfxName: 'punch1', wordName: 'w_smack', props: false }); }
    if (this.t > 0.7) { this.set('chase'); this.cd = this.phase === 2 ? 0.6 : 0.95; }
  }
  s_lasso(dt) {  // twirl the stethoscope (dodge window), then fling it: a nurse in the lane gets yanked in
    if (this.t < 0.05) sfx('lasso', { vol: 0.7 });
    if (!this.hitDone && this.t > 0.62) {
      this.hitDone = true;
      for (const h of W.heroes) {
        if (!h.hittable() || h.z > 12 || Math.abs(h.y - this.y) > 11) continue;
        const dx = (h.x - this.x) * this.face; if (dx < 10 || dx > 104) continue;
        h.takeHit({ dmg: PHIL.lasso, dir: -this.face, kb: 210, stun: 0.5, from: this }); word('w_smack', h.x, h.y, 40);
        floatText('YANK!', h.x, h.y, 60, '#ffe84a'); W.stats.lassoed = (W.stats.lassoed || 0) + 1;
      }
    }
    if (this.t > 1.0) { this.set('chase'); this.cd = 0.8; }
  }
  s_write(dt) {  // writes orders on the clipboard; papers flutter out and patients come running
    if (this.t < 0.05) { floatText(pick(PHIL_LINES.write), this.x, this.y, TOP, '#ffe84a'); sfx('philin', { vol: 0.6 }); }
    if (!this.hitDone && this.t > 0.9) {
      this.hitDone = true; this.orderCd = PHIL.orderCd[this.phase - 1]; W.stats.orders = (W.stats.orders || 0) + 1;
      for (let i = 0; i < 3; i++) addShot({ kind: 'enemy', spr: 'p_order', x: this.x + this.face * 10, y: clampY(this.y + (i - 1) * 14), z: 60, vx: this.face * (90 + i * 30), vz: 80, grav: 160, owner: this, dmg: PHIL.order, spin: 6, life: 2 });
      if (W.director && W.director.backup) W.director.backup();
    }
    if (this.t > 1.3) { this.set('chase'); this.cd = 0.5; }
  }
  s_taunt(dt) { if (this.t > 0.9) this.set('chase'); }
  s_stat(dt) {
    if (this.t < 0.05) { floatText(pick(PHIL_LINES.stat), this.x, this.y, TOP, '#ff8a9a'); W.flash = 0.5; W.flashCol = '#a24dff'; sfx('alarm', { vol: 0.5 }); sfx('philin'); word('w_weeoo', this.x, this.y, 74); }
    if (this.t > 1.2) { this.set('chase'); this.cd = 0.3; this.orderCd = 0.5; }
  }
  s_defeat(dt) {
    if (this.t > 0.6 && Math.floor(this.t * 2) !== Math.floor((this.t - dt) * 2)) addFx({ type: 'zzz', x: this.x + 10 * this.face, y: this.y, z: 24, dur: 1.4 });
  }
  pose() {
    switch (this.st) {
      case 'enter': return this.walking ? ['walk', Math.floor(W.t * 7)] : ['taunt', Math.floor(this.t * 4)];
      case 'chase': return this.hurtT > 0 ? ['hurt', 0] : this.walking ? ['walk', Math.floor(W.t * 8)] : ['idle', Math.floor(W.t * 3)];
      case 'swing': return ['swing', this.t > 0.3 ? 1 : 0];
      case 'lasso': return ['lasso', this.t > 0.6 ? 2 : Math.floor(this.t * 10) % 2];
      case 'write': return ['write', this.t > 0.85 ? 2 : Math.floor(this.t * 6) % 2];
      case 'taunt': case 'stat': return ['taunt', Math.floor(this.t * 5)];
      case 'fall': return ['fall', 0];
      case 'down': return ['down', 0];
      case 'getup': return ['getup', 0];
      case 'defeat': return ['sleep', 0];
    }
    return ['idle', 0];
  }
  drawShadow() { const X = this.x - W.camX, Y = this.y + offY(); ellipse(X, Y, 15, 3, '#000', 0.32); }
  draw() {
    const X = this.x - W.camX;
    if (this.phase === 2 && this.st !== 'defeat') ellipse(X, this.y + offY(), 18, 4, '#a24dff', 0.4 + Math.sin(W.t * 20) * 0.08);
    const [n, i] = this.pose(); this.drawSprite(n, i);
    if ((this.st === 'swing' && this.t < 0.3) || (this.st === 'lasso' && this.t < 0.6)) if (Math.floor(this.t * 12) % 2) text('!', X + this.face * 6, this.y + offY() - this.z - 92, { col: '#ff5a3a', align: 'center' });
  }
  drawIcon(x, y) { spr('face_philin', x, y, { scale: 0.75 }); }
  light(L) { if (this.st !== 'defeat') L.push({ x: this.x, y: this.y - 40, r: 30, col: '#bfe0ff', a: 0.35 }); }
}
