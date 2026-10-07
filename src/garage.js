// v0.11 THE PARKING GARAGE AT SHIFT CHANGE: the car traffic and the car alarms (TMNT-style street hazards).
// - Lane cars: a lane flashes, a "CAR!" arrow + headlights show at the screen edge with a horn, then a parody car tears
//   across the lane. It hits nurses (jump over it, or step out of the lane) AND visitors / patients, so you can bait
//   them into traffic: a car that flattens a patient you'd been fighting scores BAITED! for you.
// - Back-outs: a parked car's reverse lights blink and it beeps, then it backs out into the lane and drives off.
// - Car alarms: hit a parked car and its alarm goes off (WEE-OO!), hazards flashing: patients nearby get dizzy.
// Cars only run in the open fights, never during the Valet boss. GARAGE = the tuning.
import { G, spr, rect, text, ellipse, sprSize } from './gfx.js';
import { Y_MIN, Y_MAX, CARS } from './data.js';
import { W, offY, addFx, floatText, word, shake, spark, addScore, hitProp, propBox } from './world.js';
import { sfx } from './sound.js';

export const GARAGE = { first: 4, gap: [6.5, 10], warn: 1.25, speed: 270, backWarn: 1.0, backOut: 0.75, back: 0.3, alarm: 4.5, heroDmg: 16, foeDmg: 38, jump: 22, hop: 8, lane: 12, bait: 300 };
const MODELS = Object.keys(CARS);
const rr = (a, b) => a + W.rnd() * (b - a);
const VIEW = () => [W.camX, W.camX + G.VW];

export function resetGarage(lv) {
  W.cars = []; W.carAlarms = []; W.carNext = GARAGE.first; W.carN = 0;
  W.onCarHit = lv && lv.garage ? carAlarm : null;
}
const quiet = () => !W.lv || !W.lv.garage || W.bossOn || W.finalT || W.cleared || W.lv.zones[W.zone] && W.lv.zones[W.zone].boss;

// ---- spawning
function laneY() {  // somewhere a nurse is standing (it's a threat, not decoration), always in the driving lanes
  const hs = W.heroes.filter((h) => h.alive && h.st !== 'out');
  const base = hs.length && W.rnd() < 0.75 ? hs[Math.floor(W.rnd() * hs.length)].y + rr(-6, 6) : rr(160, 206);
  return Math.max(158, Math.min(Y_MAX - 4, base));
}
export function sendCar(opts = {}) {  // a car tears through a lane (tests: __nbd.garage.sendCar({ y, dir }))
  const dir = opts.dir || (W.rnd() < 0.7 ? 1 : -1), y = opts.y ?? laneY(), m = opts.model || MODELS[Math.floor(W.rnd() * MODELS.length)];
  const c = { kind: 'pass', st: 'warn', t: 0, dir, y, model: m, ci: W.rnd() < 0.5 ? 0 : 1, x: dir > 0 ? W.camX - 60 : W.camX + G.VW + 60, hitSet: new Set(), warn: opts.warn ?? GARAGE.warn };
  W.cars.push(c); W.carN++; sfx('carhorn', { vol: 0.7 }); sfx('rev', { vol: 0.4 });
  W.stats.carPasses = (W.stats.carPasses || 0) + 1;
  return c;
}
export function backOut(p) {  // a parked car backs out of its stall into the lane, then drives off
  const [L, R] = VIEW();
  p = p || W.props.filter((q) => q.def.car && q.st === 0 && !q.alarmT && q.x > L + 60 && q.x < R - 60)[0];
  if (!p) return null;
  W.props.splice(W.props.indexOf(p), 1);
  const toY = Math.max(158, Math.min(190, laneY()));
  const c = { kind: 'back', st: 'warn', t: 0, dir: W.rnd() < 0.6 ? 1 : -1, x: p.x, y: p.y, y0: p.y, toY, model: p.def.model, ci: p.def.ci, hitSet: new Set(), warn: GARAGE.backWarn, prop: p };
  W.cars.push(c); W.carN++; sfx('beepbeep', { vol: 0.6 }); word('w_beepbeep', p.x, p.y, 30);
  W.stats.backouts = (W.stats.backouts || 0) + 1;
  return c;
}

// ---- update
export function updateGarage(dt) {
  if (!W.lv || !W.lv.garage) return;
  if (!quiet() && W.heroes.some((h) => h.alive && h.st !== 'out') && W.cars.length === 0) {
    if ((W.carNext -= dt) <= 0) { W.carNext = rr(...GARAGE.gap); if (W.rnd() < 0.3 && backOut()) {} else sendCar(); }
  }
  for (const c of W.cars) moveCar(c, dt);
  W.cars = W.cars.filter((c) => !c.gone);
  updateAlarms(dt);
}
function moveCar(c, dt) {
  c.t += dt;
  if (c.st === 'warn') {
    if (c.kind === 'back' && Math.floor(c.t / 0.33) !== Math.floor((c.t - dt) / 0.33)) sfx('beep', { vol: 0.35 });
    if (c.t >= c.warn) { c.st = c.kind === 'back' ? 'backing' : 'go'; c.t = 0; if (c.kind === 'pass') sfx('rev', { vol: 0.6, rate: 1.2 }); }
    return;
  }
  if (c.st === 'backing') {  // slowly reverses out (it can still bump you)
    c.y += (c.toY - c.y0) / GARAGE.backOut * dt;
    if ((c.toY - c.y) * Math.sign(c.toY - c.y0 || 1) <= 0) { c.y = c.toY; c.st = 'stop'; c.t = 0; sfx('screech', { vol: 0.4 }); }
    hits(c, 0.45);
    return;
  }
  if (c.st === 'stop') { if (c.t > GARAGE.back) { c.st = 'go'; c.t = 0; sfx('rev', { vol: 0.6 }); } return; }
  // go: full speed down the lane
  const sp = GARAGE.speed * (c.kind === 'back' ? Math.min(1, 0.4 + c.t * 1.4) : 1);
  c.x += c.dir * sp * dt;
  if (Math.floor(c.t * 14) % 2 === 0) addFx({ type: 'dust', x: c.x - c.dir * 36, y: c.y, z: 0, dur: 0.25 });
  hits(c, 1);
  // a near miss: the nurse comments (no cooldown skip)
  for (const h of W.heroes) if (h.alive && !c.hitSet.has(h) && Math.abs(h.x - c.x) < 20 && Math.abs(h.y - c.y) < 26 && Math.abs(h.y - c.y) >= GARAGE.lane && h.say) { c.hitSet.add(h); h.say('car'); }
  const [L, R] = VIEW();
  if ((c.dir > 0 && c.x > R + 90) || (c.dir < 0 && c.x < L - 90)) c.gone = true;
}
function hits(c, k) {
  const hw = 34, front = c.x;
  for (const h of W.heroes) {
    if (c.hitSet.has(h) || !h.alive || !h.hittable() || Math.abs(h.y - c.y) > GARAGE.lane || Math.abs(h.x - front) > hw) continue;
    if (h.z > GARAGE.hop) continue;  // jumped it! (any real jump clears a car)
    c.hitSet.add(h);
    h.takeHit({ dmg: GARAGE.heroDmg * k, dir: c.dir || Math.sign(h.x - c.x) || 1, kb: 220 * k, down: true });
    word(k < 1 ? 'w_beepbeep' : 'w_wham', h.x, h.y, 20); shake(4); sfx('heavy', { vol: 0.8 }); sfx('carhorn', { vol: 0.6, rate: 1.1 });
    W.stats.carHits = (W.stats.carHits || 0) + 1; if (h.say) h.say('car', true);
  }
  for (const e of W.enemies) {
    if (c.hitSet.has(e) || !canRunOver(e) || Math.abs(e.y - c.y) > GARAGE.lane || Math.abs(e.x - front) > hw) continue;
    c.hitSet.add(e); runOver(e, c.dir || 1, k);
    if (W.rnd() < 0.5) floatText(['MY BUMPER!', 'I HAD THE RIGHT OF WAY!', 'WATCH IT, BUDDY!'][Math.floor(W.rnd() * 3)], c.x, c.y, 56, '#ffffff');
  }
  for (const p of W.props) {  // cones fly, carts roll, pay stations clang
    if (p.st >= 2 || c.hitSet.has(p) || p.def.car || p.rider || p.flying) continue;
    const b = propBox(p); if (Math.abs(p.y - c.y) > GARAGE.lane + 2 || front + hw < b.x0 || front - hw > b.x1) continue;
    c.hitSet.add(p); hitProp(p, 20 * k, { dir: c.dir || 1, kb: 220 * k });
  }
}

// a car (or the Valet's cart) bowls a visitor / patient over. If a nurse had been fighting them: BAITED!
export const canRunOver = (e) => e.alive && !['dead', 'thrown', 'enter_door', 'zapped', 'down', 'fall', 'getup'].includes(e.st) && e.z <= GARAGE.jump;
export function runOver(e, dir, k = 1) {
  const by = e.lastHitBy && e.lastHitBy.alive ? e.lastHitBy : null;
  e.takeHit({ dmg: GARAGE.foeDmg * k, dir, kb: 240 * k, down: true, force: true, from: by });
  spark(e.x, e.y, 24, 'bigspark'); shake(4); sfx('heavy', { vol: 0.9 }); W.stop = Math.max(W.stop, 0.06);
  W.stats.carFoes = (W.stats.carFoes || 0) + 1;
  if (by) { word('w_baited', e.x, e.y, 34); addScore(by, GARAGE.bait); floatText('BAITED! +' + GARAGE.bait, e.x, e.y, 70, '#ffe84a'); W.stats.baited = (W.stats.baited || 0) + 1; }
  else word('w_wham', e.x, e.y, 20);
}

// ---- car alarms
function carAlarm(p, from) {
  const A = W.carAlarms.find((a) => a.p === p);
  if (A) { A.t = Math.min(A.t, 1); return; }
  W.carAlarms.push({ p, t: 0 }); p.alarmT = 1;
  sfx('caralarm', { vol: 0.7 }); word('w_weeoo', p.x, p.y, 40); shake(2);
  W.stats.carAlarms = (W.stats.carAlarms || 0) + 1;
  if (from && from.isHero) { addScore(from, 100); floatText('+100', p.x, p.y, 60, '#ffe84a'); }
  let shouted = false;
  for (const e of W.enemies) {
    if (!e.alive || Math.abs(e.x - p.x) > 120 || !['idle', 'walk', 'windup'].includes(e.st)) continue;
    e.set('dizzy'); e.stun = 1.2; e.vx = 0;
    if (!shouted) { shouted = true; floatText(["WHOSE CAR IS THAT?!", 'IS THAT MY CAR?!', 'TURN IT OFF!'][Math.floor(W.rnd() * 3)], e.x, e.y, 64, '#ffb84a'); }
  }
  const hs = W.heroes.filter((h) => h.alive && h.say && h.st !== 'out').sort((a, b) => Math.abs(a.x - p.x) - Math.abs(b.x - p.x));
  if (hs[0]) hs[0].say('alarm', true);
}
function updateAlarms(dt) {
  for (const A of W.carAlarms) {
    A.t += dt;
    if (A.p.st >= 2) { A.done = true; floatText('...beep.', A.p.x, A.p.y, 46, '#c8ccd6'); continue; }
    if (A.t > GARAGE.alarm) { A.done = true; continue; }
    if (Math.floor(A.t / 1.65) !== Math.floor((A.t - dt) / 1.65)) sfx('caralarm', { vol: 0.5 });
  }
  for (const A of W.carAlarms) if (A.done) A.p.alarmT = 0;
  W.carAlarms = W.carAlarms.filter((A) => !A.done);
}

// ---- drawing
const carName = (c) => `car_${c.model}${c.ci}_0`;
function drawCar(c) {
  const X = Math.round(c.x - W.camX), Y = Math.round(c.y + offY()), name = carName(c), [w, h] = sprSize(name), f = c.dir < 0;
  ellipse(X, Y, 38, 4, '#000', 0.35);
  spr(name, X, Y + 2, { ax: 39, ay: h, flip: f });
  const fx = (dx) => X + (f ? -dx : dx);
  if (c.st === 'go' || c.kind === 'pass') { rect(fx(34) - 2, Y - 12, 4, 3, '#fff8c0'); }  // headlight
  if (c.kind === 'back' && c.st !== 'go' && Math.floor(W.t * 6) % 2) { rect(fx(-35) - 2, Y - 9, 4, 3, '#ffffff'); }  // reverse lights
  rect(fx(-36) - 1, Y - 12, 3, 2, '#ff3a4a');  // tail light
}
export function garageList(list) {
  if (!W.lv || !W.lv.garage) return;
  for (const c of W.cars || []) if (c.st !== 'warn' || c.kind === 'back') list.push({ y: c.y, d: () => drawCar(c) });
}
export function drawGarageFloor() {  // under the actors: the lane telegraph
  if (!W.lv || !W.lv.garage) return;
  for (const c of W.cars || []) {
    if (c.st === 'go' && c.kind === 'pass') continue;
    const on = Math.floor(W.t * 10) % 2, Y = c.y + offY();
    if (c.kind === 'pass') { const k = Math.min(1, c.t / c.warn); rect(0, Y - GARAGE.lane, G.VW, GARAGE.lane * 2, '#ffe84a', (on ? 0.22 : 0.12) * (0.6 + k * 0.6)); rect(0, Y - GARAGE.lane, G.VW, 1, '#ffe84a', 0.7); rect(0, Y + GARAGE.lane - 1, G.VW, 1, '#ffe84a', 0.7); }
    else { const X = c.x - W.camX; rect(X - 36, Math.min(c.y0, c.toY) + offY() - 4, 72, Math.abs(c.toY - c.y0) + 8, '#ffffff', on ? 0.16 : 0.08); }
  }
  for (const A of W.carAlarms || []) {  // hazards flashing orange around the car
    if (Math.floor(A.t * 4) % 2) continue;
    const X = A.p.x - W.camX, Y = A.p.y + offY();
    rect(X - 36, Y - 16, 4, 3, '#ffb020'); rect(X + 32, Y - 16, 4, 3, '#ffb020'); ellipse(X, Y - 12, 44, 12, '#ffb020', 0.12);
  }
}
export function drawGarageFront() {  // on top of everything: the CAR! arrow at the screen edge
  if (!W.lv || !W.lv.garage) return;
  for (const c of W.cars || []) {
    if (c.kind !== 'pass' || c.st !== 'warn' || Math.floor(W.t * 8) % 2) continue;
    const left = c.dir > 0, X = left ? 4 : G.VW - 44, Y = c.y + offY() - 30;
    rect(X, Y, 40, 13, '#c81a1a', 0.9); rect(X + 1, Y + 1, 38, 11, '#1a1020', 0.25);
    text(left ? '>CAR!' : 'CAR!<', X + 20, Y + 3, { col: '#ffffff', align: 'center' });
  }
}
export function garageLights(L) {
  if (!W.lv || !W.lv.garage) return;
  for (const c of W.cars || []) {
    if (c.kind === 'pass' && c.st === 'warn') {  // headlights sweep in from the edge
      const ex = c.dir > 0 ? W.camX - 4 : W.camX + G.VW + 4;
      L.push({ x: ex, y: c.y - 14, r: 30 + c.t * 30, col: '#fff2b0', a: 0.8 }); L.push({ x: ex + c.dir * 40, y: c.y, r: 60, ry: 12, col: '#fff2b0', a: 0.6, floor: true });
      continue;
    }
    if (c.st === 'go' || c.kind === 'pass') { L.push({ cone: true, x: c.x + c.dir * 36, y: c.y - 14, dir: c.dir, len: 120, half: 0.22 }); L.push({ x: c.x + c.dir * 80, y: c.y, r: 46, ry: 10, col: '#fff2b0', a: 0.55, floor: true }); }
    L.push({ x: c.x - c.dir * 36, y: c.y - 14, r: 16, col: '#ff3a4a', a: 0.8 });
    if (c.kind === 'back' && c.st !== 'go') L.push({ x: c.x - 36, y: c.y - 12, r: 22, col: '#ffffff', a: 0.7, blink: 3 });
  }
  for (const A of W.carAlarms || []) L.push({ x: A.p.x, y: A.p.y - 14, r: 46, ry: 20, col: '#ffb020', a: 0.85, blink: 2 });
}
// the test bot: step out of a car's lane
export function carDodge(h) {
  for (const c of W.cars || []) {
    if (c.st === 'stop' || Math.abs(h.y - c.y) > GARAGE.lane + 8) continue;
    if (c.st === 'go' && Math.sign(h.x - c.x) !== c.dir && Math.abs(h.x - c.x) > 40) continue;  // already past
    let d = h.y >= c.y ? 1 : -1;
    if (h.y + 22 > Y_MAX) d = -1; else if (h.y - 22 < Y_MIN) d = 1;
    return d;
  }
  return 0;
}
