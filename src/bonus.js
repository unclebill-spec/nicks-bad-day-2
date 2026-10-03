// v0.4 Breakroom Bonus round (between Floor 3 and Floor 4): one screen, 45 seconds. Snack thieves (patients in gowns)
// come out of the staff door and both screen edges, raid the fridge / vending machine / counter, then make a run for it.
// Tuck them back in before they get away: points per thief stopped, per snack saved, and a bonus if nothing is stolen.
import { G, spr, text, rect, panel, sprSize } from './gfx.js';
import { BONUS, ITEMS, Y_MIN, Y_MAX } from './data.js';
import { W, buildLevel, openDoor, floatText, word, addFx, dropItem, offY, FLOOR_Y } from './world.js';
import { Enemy, lookFor } from './enemy.js';
import { sfx } from './sound.js';

export const B = { phase: 'off', t: 0, left: 0, spawnT: 0, stopped: 0, escaped: 0, saved: 0, fridgeOpen: 0, spots: [], n: 0, done: false };
const rr = (a, b) => a + W.rnd() * (b - a);
const pick = (a) => a[Math.floor(W.rnd() * a.length)];

export function buildBreakroom() {
  const w = G.VW, vx = Math.round(w * 0.26), cx = vx + 46, fx = w - 46;
  const wall = [[10, 'door', 1], [6, 'sign_breakroom'], [vx, 'vend_wall'], [cx, 'cabinets'], [cx, 'counter'], [fx, 'fridge']];
  if (fx - (cx + 124) > 26) wall.push([cx + 128, 'poster_clock']);
  if (fx - (cx + 156) > 36) wall.push([cx + 156, 'note_food']);
  const lv = { id: 'B', name: 'BREAKROOM BONUS', sub: '12:30 PM. LUNCH BREAK.', width: w, music: 'stage', tint: 'rgba(255,180,110,0.08)', wall, zones: [],
    props: [[Math.round(w * 0.47), 200, 'chair', []], [Math.round(w * 0.6), 194, 'chair', []], [Math.round(w * 0.16), 206, 'trash', []], [Math.round(w * 0.78), 186, 'wetfloor', []]] };
  buildLevel(lv);
  W.breakBg = W.bg; W.breakFridgeX = fx;
  B.spots = [{ kind: 'fridge', x: fx + 18, y: Y_MIN + 3 }, { kind: 'vending', x: vx + 18, y: Y_MIN + 3 }, { kind: 'counter', x: cx + 60, y: Y_MIN + 3 }];
  W.bgHook = () => { if (B.fridgeOpen > 0) spr('fridge_open', W.breakFridgeX - W.camX, FLOOR_Y + 3 - 72 + offY()); };
}

export function startBonus() {
  W.enemies = []; W.boss = null; W.shots = []; W.fx = []; W.items = []; W.t = 0;
  W.zone = -1; W.zoneOn = false; W.wave = 0; W.queue = []; W.go = 0; W.lockX = 0; W.camMin = 0; W.camMax = 0; W.camX = 0; W.bossOn = false; W.cleared = false;
  W.heroes.forEach((h, i) => {
    if (h.st === 'out') return;
    h.x = 70 + i * 34; h.y = 178 + i * 6; h.z = 0; h.vx = h.vy = h.vz = 0; h.set('idle'); h.face = 1; h.hp = h.maxHp; h.inv = 0; h.held = null; h.grabber = null; h.ride = null;
    h.bStops = 0; h.bSaved = 0;
  });
  Object.assign(B, { phase: 'intro', t: 0, left: BONUS.time, spawnT: 0.6, stopped: 0, escaped: 0, saved: 0, fridgeOpen: 0, n: 0, done: false, endT: 0 });
}

class Thief extends Enemy {
  constructor(x, y, n) {
    super('thief', x, y, n);
    this.sheet = lookFor(BONUS.looks[n % BONUS.looks.length], n); this.isThief = true; this.loot = null; this.spot = null; this.raidT = 0; this.nomT = 0;
    this.offX = rr(-8, 8);
  }
  grabbable() { return ['idle', 'walk', 'hurt', 'dizzy', 'raid', 'getaway'].includes(this.st) && this.z === 0; }
  think(dt) {
    if (B.phase !== 'play' || this.loot) return this.runOff();
    if (!this.spot) this.spot = pick(B.spots);
    const gx = this.spot.x + this.offX, gy = this.spot.y + 2, mx = gx - this.x, my = gy - this.y, ml = Math.hypot(mx, my);
    if (ml < 3) { this.set('raid'); this.raidT = 0; this.face = W.rnd() < 0.5 ? -1 : 1; return; }
    this.x += mx / ml * this.d.speed * dt; this.y += my / ml * this.d.speed * 0.8 * dt; this.face = Math.abs(mx) > 2 ? Math.sign(mx) : this.face; this.st = 'walk';
  }
  runOff() { this.set('getaway'); this.dir = this.x < W.camX + G.VW / 2 ? -1 : 1; }
  s_raid(dt) {
    if (B.phase !== 'play') return this.runOff();
    this.raidT += dt; if (this.spot.kind === 'fridge') B.fridgeOpen = 0.25;
    if ((this.nomT -= dt) <= 0) { this.nomT = 0.7; floatText(pick(['NOM NOM', 'OOH, PUDDING!', 'MUNCH', '*rustle*', 'SNACKS!']), this.x, this.y, 60, '#ffffff'); sfx('raid', { vol: 0.45 }); }
    if (this.raidT > BONUS.raid) { this.loot = pick(BONUS.loot[this.spot.kind]); floatText('GOT ONE!', this.x, this.y, 68, '#ff8ac0'); this.runOff(); }
  }
  s_getaway(dt) {
    this.x += this.dir * this.d.speed * 1.15 * dt; this.face = this.dir;
    if (this.x < W.camX - 30 || this.x > W.camX + G.VW + 30) {
      this.alive = false;
      if (this.loot) { B.escaped++; floatText('SNACK STOLEN!', Math.max(40, Math.min(G.VW - 40, this.x)), this.y, 60, '#ff8ac0'); sfx('hurt', { vol: 0.3 }); }
    }
  }
  pose0() {
    if (this.st === 'raid') return ['atk', Math.floor(W.t * 6) % 2];
    return super.pose0();
  }
  onKO() {
    super.onKO();
    B.stopped++; word('w_stopped', this.x, this.y, 22); sfx('coin', { vol: 0.5 });
    const k = this.koBy && this.koBy.isHero ? this.koBy : this.lastHitBy;
    if (k) k.bStops = (k.bStops || 0) + 1;
    if (this.loot) { B.saved++; if (k) k.bSaved = (k.bSaved || 0) + 1; dropItem(this.loot, this.x, this.y); floatText('SNACK SAVED!', this.x, this.y, 74, '#8ae87a'); this.loot = null; }
  }
  draw() {
    super.draw();
    if (this.loot && this.st !== 'dead' && ITEMS[this.loot]) { const X = this.x - W.camX, Y = this.y + offY() - this.z - this.h - 4 + Math.round(Math.sin(W.t * 10)); const s = ITEMS[this.loot].spr; const [w, h] = sprSize(s); spr(s, X - w / 2, Y - h); }
  }
}

function spawnThief() {
  const n = ++B.n, r = W.rnd();
  let x, y, tx, ty, st = 'enter';
  if (r < 0.4 && W.doors[1]) { const d = W.doors[1]; openDoor(1); x = d.x + 18; y = 121; tx = x + rr(-6, 14); ty = rr(Y_MIN + 10, Y_MIN + 36); st = 'enter_door'; }
  else { const side = r < 0.7 ? -1 : 1; x = side < 0 ? W.camX - 24 : W.camX + G.VW + 24; y = rr(Y_MIN + 8, Y_MAX - 6); tx = side < 0 ? W.camX + rr(24, 60) : W.camX + G.VW - rr(24, 60); ty = y; }
  const e = new Thief(x, y, n); e.tx = tx; e.ty = ty; e.set(st); e.face = Math.sign(tx - x) || 1;
  W.enemies.push(e);
}

// runs after playUpdate each frame while the bonus is on; returns true when the round is over
export function updateBonus(dt) {
  B.t += dt; B.fridgeOpen = Math.max(0, B.fridgeOpen - dt);
  if (B.phase === 'intro') { if (B.t > 2.2) { B.phase = 'play'; B.t = 0; sfx('select'); } return false; }
  if (B.phase === 'play') {
    B.left -= dt;
    const alive = W.enemies.filter((e) => e.alive && e.st !== 'dead').length, cap = BONUS.cap + (W.heroes.length > 1 ? 1 : 0);
    if ((B.spawnT -= dt) <= 0 && alive < cap && B.left > 3) { spawnThief(); B.spawnT = rr(...BONUS.every); }
    if (B.left <= 0) { B.left = 0; B.phase = 'end'; B.endT = 0; word('w_timeup', W.camX + G.VW / 2, 150, 40); sfx('page'); }
    return false;
  }
  if (B.phase === 'end') {
    B.endT += dt;
    const left = W.enemies.filter((e) => e.alive && e.st !== 'dead').length;
    if ((B.endT > 2.2 && !left) || B.endT > 5) { B.phase = 'off'; B.done = true; return true; }
  }
  return false;
}

export function drawBonusHUD() {
  const VW = G.VW, VH = G.VH;
  if (B.phase === 'intro') {
    const y = 84; rect(0, y - 8, VW, 50, '#0a1030', 0.78); rect(0, y - 8, VW, 1, '#ffe84a'); rect(0, y + 41, VW, 1, '#ffe84a');
    const [w] = sprSize('w_bonus'); spr('w_bonus', VW / 2, y - 4, { ax: w / 2, scale: Math.min(1, (VW - 16) / w) * Math.min(1, 0.4 + B.t * 2) });
    text('STOP THE SNACK THIEVES!', VW / 2, y + 26, { col: '#ffffff', align: 'center' });
    return;
  }
  const s = Math.ceil(B.left), w = 196, x = Math.round((VW - w) / 2), y = 62;  // up on the wall, clear of the floor and the touch clock
  panel(x, y, w, 16, '#1a2450', '#ffe84a', 0.9);
  text(`TIME ${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`, x + 6, y + 4, { col: s <= 10 && Math.floor(W.t * 4) % 2 ? '#ff5a3a' : '#ffe84a' });
  text(`STOPPED ${B.stopped}`, x + 86, y + 4, { col: '#8ae87a' });
  text(`LOST ${B.escaped}`, x + w - 6, y + 4, { col: '#ff8ac0', align: 'right' });
}

export function bonusRows(h) {
  const perfect = B.escaped === 0 && B.stopped > 0, n = h.bStops || 0, s = h.bSaved || 0;
  const rows = [[`THIEVES STOPPED x${n}`, n * BONUS.stop], [`SNACKS SAVED x${s}`, s * BONUS.saved], [perfect ? 'NOTHING STOLEN!' : `SNACKS LOST x${B.escaped}`, perfect ? BONUS.perfect : 0]];
  return { rows, total: rows.reduce((a, r) => a + r[1], 0) };
}
