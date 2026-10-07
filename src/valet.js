// v0.11 Boss: VINNIE THE VALET, in his golf cart, at the valet stand on Level P3. ~1.25x a nurse's height.
// In the cart he revs (his lane flashes), then charges across the garage and off the screen, honking, and comes back
// for another pass (2 passes, 3 when he's mad). Then he screeches to a stop, hops out and fights on foot with his key
// ring and flicks parking tickets, and after a while climbs back in. The cart is armoured (30% damage, CLANK!): beat
// on him while he's on foot (full damage, a hard hit knocks him down). His passes flatten visitors too (BAITED!).
// Phase 2 (half health): RUSH HOUR! Faster passes, tickets scattered behind the cart and he calls the angry visitors.
// Defeated: the cart wrecks, he's thrown clear and naps on the hood line: "Keep... the change... zzz".
import { G, text, spr, ellipse, rect } from './gfx.js';
import { Y_MIN, Y_MAX } from './data.js';
import { W, offY, addShot, addFx, floatText, shake, spark, word, addScore, bumpProps } from './world.js';
import { Actor, strike, clampY } from './actor.js';
import { sfx } from './sound.js';
import { runOver, canRunOver } from './garage.js';

const SOLID = 30, LANE = 18, TOP = 104, SEAT = [-11, -15];  // cart half-width, charge lane half-depth, text height, rider offset
export const VALET = { hp: 440, passes: [2, 3], speed: [250, 320], rev: [0.95, 0.7], foot: [6.5, 5.5], knockCd: 2.5, swing: 10, pass: 14, ticket: 6 };
const LINES = { taunt: ["Ticket's validated... NOT!", 'Keys, please!', 'No tip? No car!', 'Nice scrubs. Self-park.'],
  park: ['Hold my keys!', 'Valet parking, baby!', 'Let me get the door!'], hurt: ['Hey! Watch the vest!', 'Not the bow tie!', 'I just got this cap!'],
  climb: ['Back to the cart!', "Beep beep, I'm out!"], rush: ['RUSH HOUR, BABY!', 'EVERYBODY NEEDS A SPOT!'] };
const pick = (a) => a[Math.floor(W.rnd() * a.length)];

class CartProp {  // the parked (or wrecked) golf cart, drawn in the depth-sorted list while Vinnie is out of it
  constructor(x, y, face, st = 0) { Object.assign(this, { x, y, face, st, t: 0 }); }
  draw() { drawCart(this.x, this.y, this.face, this.st, null); }
}
function drawCart(x, y, face, st, rider) {
  const X = x - W.camX, Y = y + offY() + 1, flip = face < 0;
  spr((flip ? 'valetcartL' : 'valetcart') + st, X, Y, { ax: 44, ay: 93 });  // (a mirrored body keeps VALET readable)
  if (rider) rider();
  spr('valetroof' + st, X, Y, { ax: 44, ay: 93, flip });
  if (st < 2 && Math.floor(W.t * 4) % 2) ellipse(X + (flip ? 2 : -2), Y - 86, 4, 3, '#ffb020', 0.8);  // the beacon
}

export class Valet extends Actor {
  constructor(x, y) {
    super('valet', x, y);
    this.isBoss = true; this.name = 'VINNIE THE VALET'; this.big = true; this.w = 52; this.h = 74; this.p2label = 'RUSH HOUR!';
    this.maxHp = this.hp = Math.round(VALET.hp * W.diff.hp * (W.heroes.length > 1 ? 1.35 : 1));
    this.face = -1; this.phase = 1; this.shown = 0; this.inCart = true; this.cart = null; this.cd = 1; this.passes = 0; this.knockCd = 0; this.callCd = 4; this.hits = 0;
    this.set('enter');
  }
  hint() {
    if (this.st === 'rev') return 'GET OUT OF HIS LANE!';
    if (!this.inCart && ['foot', 'swing', 'throw', 'taunt'].includes(this.st) && (this.foots || 0) <= 2) return "HE'S OUT OF THE CART! GET HIM!";
    return null;
  }
  hittable() { return !['enter', 'rush', 'hop', 'climb', 'defeat', 'off', 'fall', 'down', 'getup', 'pass'].includes(this.st) || (this.st === 'pass' && this.onScreen()); }
  grabbable() { return false; }
  onScreen() { return this.x > W.camX - 10 && this.x < W.camX + G.VW + 10; }
  setCart(on) {
    this.inCart = on; this.w = on ? 52 : 18; this.big = true;
  }
  takeHit({ dmg, dir, kb, down, from, force }) {
    if (!this.hittable() && !force) return;
    const weak = !this.inCart || force, d = weak ? dmg : dmg * 0.3;
    this.hp -= d; this.flash = 0.1; if (from) addScore(from, d * 10);
    if (!weak && W.rnd() < 0.35) floatText('CLANK!', this.x, this.y, 60, '#c8ccd6');
    if (this.hp <= 0) { this.hp = 0; this.die(from); return; }
    if (this.phase === 1 && this.hp < this.maxHp * 0.5) { this.phase = 2; this.rushNext = true; }
    if (!this.inCart && !['fall', 'down', 'getup', 'hop', 'climb'].includes(this.st)) {
      this.hits++; this.hurtT = 0.2;
      if ((down || this.hits >= 4) && this.knockCd <= 0) { this.hits = 0; this.knockCd = VALET.knockCd; this.knock(dir || 1, 130, 170); if (W.rnd() < 0.6) floatText(pick(LINES.hurt), this.x, this.y, TOP - 10, '#ffffff'); }
    }
  }
  die(from) {
    this.set('defeat'); this.vx = 0; W.stop = 0.4; shake(8); sfx('explosion'); sfx('screech', { vol: 0.8 }); W.flash = 0.6; W.flashCol = '#ffffff';
    if (from && from.isHero) addScore(from, 10000);
    if (this.inCart) {  // the cart wrecks and he's thrown clear
      W.decor.push(new CartProp(this.x, this.y, this.face, 2)); this.setCart(false); this.z = 1; this.vz = 220; this.vx = -this.face * 90;
      for (let i = 0; i < 6; i++) addFx({ type: 'smoke', x: this.x + (W.rnd() - 0.5) * 40, y: this.y, z: 20 + W.rnd() * 30, dur: 0.8 });
    } else if (this.cart) this.cart.st = 2;
    this.cart = null;
    floatText('Keep... the change... zzz', this.x, this.y, TOP, '#ffffff'); sfx('valet_ko', { vol: 0.8 });
    for (const e of W.enemies) if (e.alive && e.st !== 'dead') e.takeHit({ dmg: 999, dir: Math.sign(e.x - this.x) || 1, kb: 120, down: true, force: true });
  }
  target() {
    const hs = W.heroes.filter((h) => h.alive && !['dead', 'out'].includes(h.st));
    if (!hs.length) return null;
    return hs.reduce((a, b) => (Math.abs(a.x - this.x) + Math.abs(a.y - this.y) < Math.abs(b.x - this.x) + Math.abs(b.y - this.y) ? a : b));
  }
  update(dt) {
    this.t += dt; this.flash = Math.max(0, this.flash - dt); this.cd -= dt; this.knockCd -= dt; this.callCd -= dt; this.hurtT = Math.max(0, (this.hurtT || 0) - dt);
    this.shown = Math.min(1, this.shown + dt * 0.8);
    if (this.stagT > 0 && this.st !== 'defeat') {  // Ativan / Code Blue stagger
      this.stagT -= dt; if (Math.floor(this.stagT * 20) % 3 === 0) addFx({ type: 'spark', kind: 'bluespark', x: this.x + (W.rnd() - 0.5) * this.w, y: this.y, z: 20 + W.rnd() * 50, dur: 0.12 });
    } else if (!this.inCart && ['fall', 'down', 'getup'].includes(this.st)) { if (!this.fallStep(dt, 0.9) || this.st === 'idle') this.set('foot'); }
    else { const fn = this['s_' + this.st]; if (fn) fn.call(this, dt); }
    if (this.st !== 'pass' && this.st !== 'off') this.y = clampY(this.y);
    // the cart is solid (his own, or the parked one)
    const solids = [];
    if (this.inCart && !['pass', 'off', 'defeat'].includes(this.st)) solids.push(this);
    if (this.cart) solids.push(this.cart);
    for (const s of solids) for (const h of W.heroes) {
      if (!h.alive || h.z > 20 || ['dead', 'out', 'fall', 'down'].includes(h.st)) continue;
      const dx = h.x - s.x, dy = h.y - s.y;
      if (Math.abs(dx) < SOLID && Math.abs(dy) < 12) h.x = s.x + (Math.sign(dx) || 1) * SOLID;
    }
  }
  // ---- in the cart
  s_enter(dt) {
    const stopX = W.camX + G.VW * 0.72;
    if (this.t < 0.05) { sfx('rev', { vol: 0.6 }); sfx('meep', { vol: 0.6 }); }
    if (this.x > stopX) { this.x -= 170 * dt; return; }
    if (!this.greeted) { this.greeted = true; sfx('screech', { vol: 0.6 }); floatText("Ticket's validated... NOT!", this.x, this.y, TOP, '#ffffff'); sfx('valet', { vol: 0.85 }); word('w_parked', this.x, this.y, 70); }
    if (this.t > 2.8) { this.set('cidle'); this.passes = VALET.passes[0]; this.cd = 0.4; }
  }
  s_cidle(dt) {
    const h = this.target(); if (!h) return;
    this.face = Math.sign(h.x - this.x) || this.face;
    this.y += Math.sign(h.y - this.y) * Math.min(Math.abs(h.y - this.y), 34 * dt);
    if (this.rushNext) { this.rushNext = false; return this.set('rush'); }
    if (this.cd > 0) return;
    const minions = W.enemies.filter((e) => e.alive && e.st !== 'dead').length;
    if (this.phase === 2 && this.callCd <= 0 && minions < 2) { this.callCd = 14; W.director.backup(); floatText('VISITORS, ATTACK!', this.x, this.y, TOP, '#ffffff'); sfx('carhorn', { vol: 0.6 }); }
    if (this.passes > 0) return this.set('rev');
    this.set('park');
  }
  s_rev(dt) {
    const dur = VALET.rev[this.phase - 1], lock = dur - 0.4;
    const h = this.target(); if (h && this.t < lock) { this.y += Math.sign(h.y - this.y) * Math.min(Math.abs(h.y - this.y), 60 * dt); if (this.onScreen()) this.face = Math.sign(h.x - this.x) || this.face; }
    if (this.t < 0.05) { sfx('rev', { vol: 0.7 }); if (W.rnd() < 0.5) sfx('meep', { vol: 0.5 }); }
    if (Math.floor(this.t * 20) % 3 === 0) addFx({ type: 'dust', x: this.x - this.face * 30, y: this.y, dur: 0.25 });
    if (this.t > dur) { this.set('pass'); this.vx = this.face * VALET.speed[this.phase - 1]; this.hitSet = new Set(); this.dropT = 0; this.passes--; sfx('carhorn', { vol: 0.8 }); word('w_beepbeep', this.x, this.y, 60); }
  }
  s_pass(dt) {
    this.x += this.vx * dt;
    if (this.onScreen()) {
      strike(this, { box: [-30, 38], z: [0, 64], depth: LANE - 5, dmg: VALET.pass, kb: 200, down: true, sfxName: 'heavy', once: this.hitSet, wordName: 'w_wham', props: false, targets: W.heroes });
      for (const e of W.enemies) if (!this.hitSet.has(e) && canRunOver(e) && Math.abs(e.y - this.y) < LANE - 4 && Math.abs(e.x - this.x) < 34) { this.hitSet.add(e); runOver(e, Math.sign(this.vx) || 1, 1); }
      bumpProps(this, 20, Math.sign(this.vx) || this.face, null, this.hitSet, 30);
      if (Math.floor(this.t * 14) % 2 === 0) addFx({ type: 'dust', x: this.x - this.face * 30, y: this.y, dur: 0.3 });
      if (this.phase === 2 && (this.dropT += dt) > 0.3) {  // parking tickets flutter out behind the cart
        this.dropT = 0;
        addShot({ kind: 'enemy', spr: 'p_ticket', x: this.x - this.face * 30, y: clampY(this.y + (W.rnd() - 0.5) * 36), z: 40, vx: -this.face * 30, vz: 60, grav: 140, owner: this, dmg: VALET.ticket, spin: 9, life: 2.2 });
      }
    }
    // the last pass: he brakes hard on screen, then hops out
    const L = W.camX + 70, R = W.camX + G.VW - 70;
    if (this.passes <= 0 && this.t > 0.35 && ((this.vx < 0 && this.x < L + 30) || (this.vx > 0 && this.x > R - 30))) { this.set('park'); return; }
    if ((this.vx < 0 && this.x < W.camX - 70) || (this.vx > 0 && this.x > W.camX + G.VW + 70)) this.set('off');
  }
  s_off(dt) {  // round the block: back in from the side he left, on a nurse's lane
    if (this.t > (this.phase === 2 ? 0.5 : 0.8)) {
      const h = this.target(); if (h) this.y = h.y;
      this.face = -Math.sign(this.vx) || -this.face; this.x = this.face > 0 ? W.camX - 34 : W.camX + G.VW + 34; this.vx = 0;
      sfx('meep', { vol: 0.6 }); this.set('rev');
    }
  }
  s_park(dt) {  // screech! then hop out
    if (this.t < 0.05) { sfx('screech', { vol: 0.8 }); word('w_screech', this.x, this.y, 50); }
    this.x += this.vx * dt; this.vx *= Math.exp(-dt * 7);
    if (Math.floor(this.t * 20) % 2 === 0) addFx({ type: 'smoke', x: this.x - this.face * 26, y: this.y, z: 4, dur: 0.4 });
    this.x = Math.max(W.camX + 40, Math.min(W.camX + G.VW - 40, this.x));
    if (this.t > 0.55) {
      this.vx = 0; this.cart = new CartProp(this.x, this.y, this.face, this.phase === 2 ? 1 : 0); W.decor.push(this.cart);
      this.setCart(false); this.x += SEAT[0] * this.face; this.z = 18; this.vz = 160; this.set('hop'); sfx('keys', { vol: 0.7 });
      floatText(pick(LINES.park), this.x, this.y, TOP, '#ffffff'); this.foots = (this.foots || 0) + 1;
    }
  }
  s_hop(dt) {
    const h = this.target(); this.x += (h ? Math.sign(h.x - this.x) : -this.face) * 40 * dt;
    if (this.airborne(dt)) { this.vz = 0; this.vx = 0; this.footLeft = VALET.foot[this.phase - 1]; this.set('foot'); this.cd = 0.5; addFx({ type: 'dust', x: this.x, y: this.y, dur: 0.3 }); }
  }
  // ---- on foot
  s_foot(dt) {
    this.footLeft -= dt;
    const h = this.target(); if (!h) return;
    if (this.rushNext && this.footLeft > 1) this.footLeft = 1;
    if (this.footLeft <= 0) return this.set('return');
    const dx = h.x - this.x, dy = h.y - this.y, adx = Math.abs(dx);
    this.face = Math.sign(dx) || this.face;
    const want = this.cd > 0.4 ? 60 : 28, gx = h.x - Math.sign(dx || 1) * want;
    const mx = gx - this.x, my = dy, ml = Math.hypot(mx, my);
    if (ml > 4) { this.x += mx / ml * 74 * dt; this.y += my / ml * 54 * dt; this.walking = true; } else this.walking = false;
    if (this.cd > 0) return;
    if (adx < 44 && Math.abs(dy) < 10) { this.set('swing'); this.hitDone = false; return; }
    if (adx > 90 && Math.abs(dy) < 14 && W.rnd() < 0.5) { this.set('throw'); this.hitDone = false; return; }
    if (W.rnd() < 0.15) { this.set('taunt'); floatText(pick(LINES.taunt), this.x, this.y, TOP - 10, '#ffffff'); this.cd = 1; }
  }
  s_swing(dt) {  // the key ring
    this.footLeft -= dt;
    if (!this.hitDone && this.t > 0.32) { this.hitDone = true; sfx('keys', { vol: 0.8 }); strike(this, { box: [0, 46], z: [14, 60], depth: 12, dmg: VALET.swing, kb: 150, down: W.rnd() < 0.4, sfxName: 'punch1', wordName: 'w_smack', props: false }); }
    if (this.t > 0.7) { this.set('foot'); this.cd = this.phase === 2 ? 0.7 : 1.0; }
  }
  s_throw(dt) {  // flicks a parking ticket
    this.footLeft -= dt;
    if (!this.hitDone && this.t > 0.3) {
      this.hitDone = true; sfx('whoosh', { vol: 0.5, rate: 1.3 });
      addShot({ kind: 'enemy', spr: 'p_ticket', x: this.x + this.face * 14, y: this.y, z: 42, vx: this.face * 210, vz: 0, grav: 0, owner: this, dmg: VALET.ticket, spin: 14, life: 1.8 });
      if (W.rnd() < 0.5) floatText(pick(['TICKET!', "You're TOWED!", 'Expired meter!']), this.x, this.y, TOP - 10, '#ffffff');
    }
    if (this.t > 0.65) { this.set('foot'); this.cd = 0.9; }
  }
  s_taunt(dt) { this.footLeft -= dt; if (this.t > 0.9) this.set('foot'); }
  s_return(dt) {  // back to the cart
    const c = this.cart; if (!c) { this.setCart(true); return this.set('cidle'); }
    const gx = c.x + SEAT[0] * c.face, mx = gx - this.x, my = c.y - this.y, ml = Math.hypot(mx, my);
    this.face = Math.sign(mx) || this.face;
    if (ml > 6) { this.x += mx / ml * 110 * dt; this.y += my / ml * 70 * dt; return; }
    this.set('climb'); this.z = 0; this.vz = 150; floatText(pick(LINES.climb), this.x, this.y, TOP, '#ffffff');
  }
  s_climb(dt) {
    const c = this.cart;
    this.vz -= 600 * dt; this.z += this.vz * dt;
    if (this.t > 0.42 || this.z < 0) {
      this.z = 0; this.x = c.x; this.y = c.y; this.face = c.face; W.decor.splice(W.decor.indexOf(c), 1); this.cart = null;
      this.setCart(true); this.set('cidle'); this.cd = 0.6; this.passes = VALET.passes[this.phase - 1]; sfx('meep', { vol: 0.6 }); sfx('rev', { vol: 0.5 });
    }
  }
  s_rush(dt) {
    if (this.t < 0.05) { word('w_valet', this.x, this.y, 74); floatText(pick(LINES.rush), this.x, this.y, TOP, '#ff8a9a'); W.flash = 0.6; W.flashCol = '#a24dff'; sfx('carhorn'); sfx('rev', { vol: 0.8, rate: 1.2 }); }
    if (Math.floor(this.t * 16) % 2 === 0) addFx({ type: 'smoke', x: this.x - this.face * 28, y: this.y, z: 6, dur: 0.4 });
    if (this.t > 0.7 && !this.called) { this.called = true; W.director.backup(); this.callCd = 14; }
    if (this.t > 1.4) { this.set('cidle'); this.cd = 0.3; this.passes = VALET.passes[1]; }
  }
  s_defeat(dt) {
    if (this.z > 0 || this.vz > 0) { this.vz -= 700 * dt; this.z += this.vz * dt; this.x += this.vx * dt; if (this.z <= 0) { this.z = 0; this.vz = 0; this.vx = 0; shake(3); sfx('bounce'); addFx({ type: 'dust', x: this.x, y: this.y, dur: 0.4 }); } return; }
    if (this.t > 0.6 && Math.floor(this.t * 2) !== Math.floor((this.t - dt) * 2)) addFx({ type: 'zzz', x: this.x + 10 * this.face, y: this.y, z: 30, dur: 1.4 });
  }
  pose() {
    if (this.inCart) {
      if (this.st === 'rev' || this.st === 'rush') return ['honk', Math.floor(W.t * 8)];
      if (this.hurtT > 0 || this.flash > 0) return ['churt', 0];
      if (this.st === 'enter' && this.greeted) return ['honk', Math.floor(this.t * 4)];
      return ['drive', Math.floor(W.t * (this.st === 'pass' ? 10 : 3))];
    }
    switch (this.st) {
      case 'hop': case 'climb': return ['hop', 0];
      case 'foot': case 'return': return this.hurtT > 0 ? ['hurt', 0] : (this.walking || this.st === 'return') ? ['walk', Math.floor(W.t * 8)] : ['idle', Math.floor(W.t * 3)];
      case 'swing': return ['swing', this.t > 0.3 ? 1 : 0];
      case 'throw': return ['throw', this.t > 0.28 ? 1 : 0];
      case 'taunt': return ['taunt', Math.floor(this.t * 5)];
      case 'fall': return ['fall', 0];
      case 'down': return ['down', 0];
      case 'getup': return ['getup', 0];
      case 'defeat': return this.z > 0 ? ['fall', 0] : ['sleep', 0];
    }
    return ['idle', 0];
  }
  drawShadow() { const X = this.x - W.camX, Y = this.y + offY(); if (this.st === 'off') return; if (this.inCart) ellipse(X, Y + 1, 40, 5, '#000', 0.34); else ellipse(X, Y, 14 * Math.max(0.5, 1 - this.z / 140), 3, '#000', 0.32); }
  draw() {
    if (this.st === 'off') return;
    const X = this.x - W.camX;
    if (this.phase === 2 && this.st !== 'defeat') ellipse(X, this.y + offY(), this.inCart ? 44 : 16, this.inCart ? 6 : 4, '#ff3a4a', 0.4 + Math.sin(W.t * 20) * 0.08);
    if (this.st === 'rev') {  // lane telegraph (like Tilly's): flashes while he revs, solid once it's locked in
      const lockd = this.t > VALET.rev[this.phase - 1] - 0.4;
      if (lockd || Math.floor(W.t * 10) % 2) { const lx = this.face > 0 ? Math.max(0, X) : 0, lw = this.face > 0 ? G.VW - lx : Math.min(G.VW, X), ly = this.y + offY() - LANE, col = this.phase === 2 ? '#ff4a6a' : '#ffe84a'; rect(lx, ly, lw, LANE * 2, col, lockd ? 0.28 : 0.16); rect(lx, ly, lw, 1, col, 0.7); rect(lx, ly + LANE * 2 - 1, lw, 1, col, 0.7); }
    }
    const [n, i] = this.pose();
    if (this.inCart) drawCart(this.x, this.y, this.face, this.phase === 2 ? 1 : 0, () => this.drawSprite(n, i, { dx: SEAT[0] * this.face, dy: SEAT[1] }));
    else this.drawSprite(n, i);
    if (!this.inCart && this.st === 'swing' && this.t < 0.3 && Math.floor(this.t * 12) % 2) text('!', X + this.face * 6, this.y + offY() - this.z - 84, { col: '#ff5a3a', align: 'center' });
  }
  drawIcon(x, y) { spr('face_valet', x, y, { scale: 0.75 }); }
  light(L) {
    const at = this.inCart && this.st !== 'off' ? this : this.cart;
    if (!at || this.st === 'defeat' && !this.cart) return;
    L.push({ cone: true, x: at.x + at.face * 40, y: at.y - 16, dir: at.face, len: 120, half: 0.26 });
    L.push({ x: at.x + at.face * 84, y: at.y, r: 44, ry: 10, col: '#fff2b0', a: 0.5, floor: true });
    L.push({ x: at.x, y: at.y - 86, r: 22, col: '#ffb020', a: 0.8, blink: 2 });
  }
}
