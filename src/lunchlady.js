// v0.14 Boss: LUNCH LADY LORETTA, behind the cafeteria serving line. Pink top, bib apron, hairnet, ~1.3x a nurse's height.
// She swings her ladle, sends a soup splash rolling down the lane (jump it!), shouts "NEXT!" (nurses on the floor nearby
// get dizzy) and flings mystery meat. Phase 2 (half health): "WE'RE OUT OF PUDDING!" -> faster, and pudding cups that leave
// slippery jello puddles. Defeated: she sits down for her own lunch break: "Kitchen's... closed... zzz". Comedic, never mean.
import { G, text, spr, ellipse } from './gfx.js';
import { W, offY, addShot, addFx, floatText, shake, word, addScore } from './world.js';
import { Actor, strike, clampY } from './actor.js';
import { sfx } from './sound.js';

const TOP = 100;
export const LORETTA = { hp: 440, speed: [60, 82], swing: 11, soup: 9, meat: 7, next: 1.1, knockCd: 2.4 };
export const LORETTA_LINES = {
  greet: ['NO CUTTING. NO SUBSTITUTIONS.'],
  taunt: ['One scoop. ONE.', 'You want fries with that? We have NO fries.', 'Hairnets save lives, hon.', "It's mystery meat. The mystery is part of it.", 'Trays go BACK on the belt!'],
  hurt: ['Watch the apron!', "That's a health code violation!", 'Hon, I have a LADLE.', 'Ow! My bunions!'],
  soup: ['SOUP OF THE DAY!', "Careful, it's hot!", 'Split pea, coming through!'],
  meat: ['Mystery meat! Catch!', 'Nobody knows what it is!', "Chef's surprise!"],
  p2: ["WE'RE OUT OF PUDDING!", 'WHO TOOK THE LAST PUDDING?!'],
  ko: "Kitchen's... closed... zzz",
};
const pick = (a) => a[Math.floor(W.rnd() * a.length)];

export class LunchLady extends Actor {
  constructor(x, y) {
    super('lunchlady', x, y);
    this.isBoss = true; this.name = 'LUNCH LADY LORETTA'; this.big = true; this.w = 24; this.h = 64; this.p2label = "WE'RE OUT OF PUDDING!";
    this.maxHp = this.hp = Math.round(LORETTA.hp * W.diff.hp * (W.heroes.length > 1 ? 1.35 : 1));
    this.face = -1; this.phase = 1; this.shown = 0; this.cd = 1.2; this.knockCd = 0; this.hits = 0; this.soupCd = 3; this.nextCd = 5; this.waves = [];
    this.set('enter');
  }
  hint() { return this.waves.length ? 'JUMP THE SOUP!' : this.st === 'shout' && this.t < 0.5 ? 'JUMP! SHE IS YELLING NEXT!' : null; }
  hittable() { return !['enter', 'defeat', 'fall', 'down', 'getup', 'p2'].includes(this.st); }
  grabbable() { return false; }
  takeHit({ dmg, from, dir, down, force }) {
    if (!this.hittable() && !force) return;
    this.hp -= dmg; this.flash = 0.1; if (from) addScore(from, dmg * 10);
    if (this.hp <= 0) { this.hp = 0; this.die(from); return; }
    if (this.phase === 1 && this.hp < this.maxHp * 0.5) { this.phase = 2; this.p2Next = true; }
    this.hits++; this.hurtT = 0.2;
    if ((down || this.hits >= 4) && this.knockCd <= 0) { this.hits = 0; this.knockCd = LORETTA.knockCd; this.knock(dir || 1, 120, 160); if (W.rnd() < 0.6) floatText(pick(LORETTA_LINES.hurt), this.x, this.y, TOP - 10, '#ffffff'); }
  }
  die(from) {
    this.set('defeat'); this.vx = 0; this.waves = []; W.stop = 0.4; shake(6); sfx('explosion', { vol: 0.6 }); W.flash = 0.5; W.flashCol = '#ffffff';
    if (from && from.isHero) addScore(from, 10000);
    floatText(LORETTA_LINES.ko, this.x, this.y, TOP, '#ffffff'); sfx('lunchlady_ko', { vol: 0.8 });
    for (let i = 0; i < 6; i++) addFx({ type: 'chunk', spr: 'deb_tray', x: this.x, y: this.y, z: 50, vx: (W.rnd() - 0.5) * 160, vy: 0, vz: 120 + W.rnd() * 120, spin: 8, dur: 1.2 });
    for (const e of W.enemies) if (e.alive && e.st !== 'dead') e.takeHit({ dmg: 999, dir: Math.sign(e.x - this.x) || 1, kb: 120, down: true, force: true });
  }
  target() {
    const hs = W.heroes.filter((h) => h.alive && !['dead', 'out'].includes(h.st));
    if (!hs.length) return null;
    return hs.reduce((a, b) => (Math.abs(a.x - this.x) + Math.abs(a.y - this.y) < Math.abs(b.x - this.x) + Math.abs(b.y - this.y) ? a : b));
  }
  update(dt) {
    this.t += dt; this.flash = Math.max(0, this.flash - dt); this.cd -= dt; this.knockCd -= dt; this.soupCd -= dt; this.nextCd -= dt; this.hurtT = Math.max(0, (this.hurtT || 0) - dt);
    this.shown = Math.min(1, this.shown + dt * 0.8);
    this.wavesTick(dt);
    if (this.stagT > 0 && this.st !== 'defeat') this.stagT -= dt;
    else if (['fall', 'down', 'getup'].includes(this.st)) { if (!this.fallStep(dt, 0.9) || this.st === 'idle') this.set('chase'); }
    else { const fn = this['s_' + this.st]; if (fn) fn.call(this, dt); }
    this.y = clampY(this.y);
  }
  wavesTick(dt) {  // soup splash waves roll along a lane; a nurse on the ground in that lane gets splashed
    for (const s of this.waves) {
      s.x += s.vx * dt; s.t += dt;
      if (W.rnd() < 0.4) addFx({ type: 'chunk', spr: null, col: '#9ac83a', sz: 2, x: s.x, y: s.y, z: 4, vx: -s.vx * 0.2, vy: 0, vz: 60, spin: 0, dur: 0.4 });
      for (const h of W.heroes) {
        if (s.hit.has(h) || !h.hittable() || h.z > 8 || Math.abs(h.y - s.y) > 10 || Math.abs(h.x - s.x) > 12) continue;
        s.hit.add(h); h.takeHit({ dmg: LORETTA.soup, dir: Math.sign(s.vx), kb: 120, down: true, from: this }); word('w_splat', h.x, h.y, 20);
        floatText('SOUP!', h.x, h.y, 60, '#9ac83a'); W.stats.souped = (W.stats.souped || 0) + 1;
      }
    }
    this.waves = this.waves.filter((s) => s.t < 2.4 && s.x > W.camX - 30 && s.x < W.camX + G.VW + 30);
  }
  s_enter(dt) {
    const stopX = W.camX + G.VW * 0.7; this.walking = true;
    if (this.x > stopX) { this.x -= 70 * dt; return; }
    this.walking = false;
    if (!this.greeted) { this.greeted = true; floatText(LORETTA_LINES.greet[0], this.x, this.y, TOP, '#ffffff'); sfx('lunchlady', { vol: 0.85 }); }
    if (this.t > 2.4) { this.set('chase'); this.cd = 0.6; }
  }
  s_chase(dt) {
    const h = this.target(); if (!h) return;
    if (this.p2Next) { this.p2Next = false; return this.set('p2'); }
    const dx = h.x - this.x, dy = h.y - this.y, adx = Math.abs(dx);
    this.face = Math.sign(dx) || this.face;
    const want = this.cd > 0.4 ? 74 : 32, gx = h.x - Math.sign(dx || 1) * want;
    const mx = gx - this.x, my = dy, ml = Math.hypot(mx, my), sp = LORETTA.speed[this.phase - 1];
    if (ml > 4) { this.x += mx / ml * sp * dt; this.y += my / ml * sp * 0.72 * dt; this.walking = true; } else this.walking = false;
    if (this.cd > 0) return;
    if (adx < 48 && Math.abs(dy) < 10) { if (this.nextCd <= 0 && W.rnd() < 0.4) { this.set('shout'); this.hitDone = false; return; } this.set('swing'); this.hitDone = false; return; }
    if (this.soupCd <= 0 && adx > 50) { this.set('scoop'); this.hitDone = false; floatText(pick(LORETTA_LINES.soup), this.x, this.y, TOP - 10, '#ffffff'); return; }
    if (adx > 60 && W.rnd() < 0.5) { this.set('fling'); this.hitDone = false; return; }
    if (W.rnd() < 0.1) { this.set('taunt'); floatText(pick(LORETTA_LINES.taunt), this.x, this.y, TOP - 10, '#ffffff'); this.cd = 1; }
  }
  s_swing(dt) {  // ladle bonk
    if (this.t < 0.05) sfx('ladle', { vol: 0.6 });
    if (!this.hitDone && this.t > 0.34) { this.hitDone = true; strike(this, { box: [0, 50], z: [14, 70], depth: 12, dmg: LORETTA.swing, kb: 160, down: W.rnd() < 0.35, sfxName: 'punch1', wordName: 'w_smack', props: false }); }
    if (this.t > 0.72) { this.set('chase'); this.cd = this.phase === 2 ? 0.55 : 0.9; }
  }
  s_scoop(dt) {  // slops a ladle of soup on the floor: a splash wave rolls down her lane
    if (!this.hitDone && this.t > 0.5) {
      this.hitDone = true; this.soupCd = this.phase === 2 ? 4 : 6; sfx('soup', { vol: 0.7 });
      this.waves.push({ x: this.x + this.face * 20, y: this.y, vx: this.face * (this.phase === 2 ? 150 : 120), t: 0, hit: new Set() });
      W.stats.soups = (W.stats.soups || 0) + 1;
    }
    if (this.t > 0.9) { this.set('chase'); this.cd = 0.6; }
  }
  s_shout(dt) {  // "NEXT!" - nurses close by and on the ground get dizzy
    if (!this.hitDone && this.t > 0.5) {
      this.hitDone = true; this.nextCd = 7; sfx('next', { vol: 0.8 }); word('w_next', this.x, this.y, 80); shake(3);
      for (const h of W.heroes) { if (!h.hittable() || h.z > 6 || Math.abs(h.x - this.x) > 70 || Math.abs(h.y - this.y) > 22) continue; h.takeHit({ dmg: 2, dir: this.face, kb: 60, dizzy: LORETTA.next, from: this }); }
    }
    if (this.t > 1.0) { this.set('chase'); this.cd = 0.5; }
  }
  s_fling(dt) {  // mystery meat lob (phase 2: a pudding cup that leaves jello)
    if (!this.hitDone && this.t > 0.4) {
      this.hitDone = true; const h = this.target(); const p2 = this.phase === 2;
      if (!p2) floatText(pick(LORETTA_LINES.meat), this.x, this.y, TOP - 10, '#ffffff');
      const tx = h ? h.x : this.x + this.face * 80, ty = h ? h.y : this.y, fl = 0.8;
      this.y += Math.max(-8, Math.min(8, ty - this.y));
      addShot({ kind: 'enemy', spr: p2 ? 'p_cup' : 'p_meat', x: this.x + this.face * 12, y: this.y, z: 64, vx: Math.max(-200, Math.min(200, (tx - this.x) / fl)), vz: 110, grav: 300, owner: this, dmg: LORETTA.meat, spin: 8, life: 3, splash: p2 ? 'jello' : undefined });
      sfx('whoosh', { vol: 0.5 });
    }
    if (this.t > 0.8) { this.set('chase'); this.cd = 0.7; }
  }
  s_taunt(dt) { if (this.t > 0.9) this.set('chase'); }
  s_p2(dt) {
    if (this.t < 0.05) { floatText(pick(LORETTA_LINES.p2), this.x, this.y, TOP, '#ff8a9a'); W.flash = 0.5; W.flashCol = '#ff3a4a'; sfx('lunchlady'); word('w_lunchrush', this.x, this.y, 80); if (W.director && W.director.backup) W.director.backup(); }
    if (this.t > 1.2) { this.set('chase'); this.cd = 0.3; this.soupCd = 0.5; }
  }
  s_defeat(dt) {
    if (this.t > 0.6 && Math.floor(this.t * 2) !== Math.floor((this.t - dt) * 2)) addFx({ type: 'zzz', x: this.x + 10 * this.face, y: this.y, z: 24, dur: 1.4 });
  }
  pose() {
    switch (this.st) {
      case 'enter': return this.walking ? ['walk', Math.floor(W.t * 7)] : ['shout', Math.floor(this.t * 4)];
      case 'chase': return this.hurtT > 0 ? ['hurt', 0] : this.walking ? ['walk', Math.floor(W.t * 8)] : ['idle', Math.floor(W.t * 3)];
      case 'swing': return ['swing', this.t > 0.32 ? 1 : 0];
      case 'scoop': return ['scoop', this.t > 0.45 ? 1 : 0];
      case 'shout': case 'taunt': case 'p2': return ['shout', Math.floor(this.t * 5)];
      case 'fling': return ['fling', this.t > 0.38 ? 1 : 0];
      case 'fall': return ['fall', 0];
      case 'down': return ['down', 0];
      case 'getup': return ['getup', 0];
      case 'defeat': return ['sleep', 0];
    }
    return ['idle', 0];
  }
  drawShadow() { const X = this.x - W.camX, Y = this.y + offY(); ellipse(X, Y, 16, 3, '#000', 0.32); }
  draw() {
    const X = this.x - W.camX, oy = offY();
    for (const s of this.waves) { ellipse(s.x - W.camX, s.y + oy, 12, 3, '#9ac83a', 0.8); spr('p_soup' + (Math.floor(s.t * 8) % 2), s.x - W.camX - 14, s.y + oy - 14); }
    if (this.phase === 2 && this.st !== 'defeat') ellipse(X, this.y + oy, 19, 4, '#ff3a4a', 0.4 + Math.sin(W.t * 20) * 0.08);
    const [n, i] = this.pose(); this.drawSprite(n, i);
    if ((this.st === 'swing' && this.t < 0.32) || ((this.st === 'scoop' || this.st === 'shout') && this.t < 0.5)) if (Math.floor(this.t * 12) % 2) text('!', X + this.face * 6, this.y + oy - this.z - 96, { col: '#ff5a3a', align: 'center' });
  }
  drawIcon(x, y) { spr('face_lunchlady', x, y, { scale: 0.75 }); }
  light(L) { if (this.st !== 'defeat') L.push({ x: this.x, y: this.y - 40, r: 30, col: '#ffd8b0', a: 0.35 }); }
}
