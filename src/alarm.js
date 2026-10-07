// v0.6 Fire Alarm Yeller event (works on any floor). Now and then, during a locked (non-boss) fight, a yelling patient
// sprints for a red wall-mounted pull station. He reaches up for ~1.6 s with a big flashing "!" (knock him down to stop
// it). If he pulls it: the alarm blares, a red/white strobe (or a soft red pulse with REDUCED FLASHING), the sprinklers
// rain on everything (wet floor sheen + slippery puddles), every patient on screen gets ENRAGED (faster, harder hits,
// steaming) for a while and an extra wave pours out of the doors / elevators. Capped: 2 per floor, 60 s apart, never
// during boss or mini-boss fights, and the zone can't clear until the extra wave is in (so it can't break a zone lock).
import { G, spr, rect, text, ellipse, textW } from './gfx.js';
import { Y_MIN, Y_MAX } from './data.js';
import { W, addShot, floatText, shake, word, addFx } from './world.js';
import { sfx } from './sound.js';

export const ALARM = { perLevel: 2, gap: 60, first: 20, chance: 0.5, windup: 1.6, rain: 8, enrage: 14, wetFor: 12, extra: 4 };
const FLOOR_Y = 118;

// pull stations along the wall, every ~320 px, nudged off doors, elevators and wall features
export function placeStations(lv) {
  const busy = [];
  for (const d of Object.values(W.doors)) busy.push([d.x - 6, d.x + 84]);
  for (const e of Object.values(W.elevs)) busy.push([e.x - 6, e.x + 88]);
  for (const [wx, kind] of lv.wall || []) if (!/^(door|elev)/.test(kind)) busy.push([wx - 4, wx + (/window/.test(kind) ? 70 : 34)]);
  const free = (x) => busy.every(([a, b]) => x + 20 < a || x > b);
  const out = []; let last = -1e9;
  for (let x = 200; x < lv.width - 120; x += 8) if (x - last >= 320 && free(x)) { out.push({ x, pulled: false, shake: 0 }); last = x; }
  return out;
}
export function resetAlarm(lv) { W.alarm = null; W.alarmUses = 0; W.alarmNext = ALARM.first; W.wet = 0; W.alarms = lv.noAlarm ? [] : placeStations(lv); W.yellers = 0; }  // v0.11: the open-air garage has none (lv.noAlarm)
function inView(x, m = 24) { return x > W.camX + m && x < W.camX + G.VW - m; }
export function stationFor(e) {  // the nearest station on screen (one is put up if none is in view)
  let best = null, bd = 1e9;
  for (const s of W.alarms || []) if (inView(s.x + 10)) { const d = Math.abs(s.x + 10 - e.x); if (d < bd) { bd = d; best = s; } }
  if (!best) { best = { x: Math.round(W.camX + G.VW * (e.x < W.camX + G.VW / 2 ? 0.3 : 0.62)), pulled: false, shake: 0 }; (W.alarms || (W.alarms = [])).push(best); }
  return best;
}
export function alarmAllowed() {
  const z = W.lv && W.lv.zones && W.lv.zones[W.zone];
  return !!(W.zoneOn && !W.bossOn && z && !z.boss && !W.lv.bonus && !W.lv.noAlarm && !W.alarm && (W.alarmUses || 0) < ALARM.perLevel);
}
// called when a wave starts: maybe add a yeller to it
export function maybeYeller(force = false) {
  if (!alarmAllowed() || W.noAlarm || (W.yellers || 0) >= ALARM.perLevel) return false;
  if (!force && (W.stats.time < (W.alarmNext || 0) || (W.yellers || 0) >= ALARM.perLevel || W.rnd() > ALARM.chance)) return false;
  W.alarmNext = W.stats.time + ALARM.gap; W.yellers = (W.yellers || 0) + 1;
  W.queue.push({ kind: 'yeller', where: W.rnd() < 0.5 ? 'L' : 'R', t: force ? 0.2 : 1.5 + W.rnd() * 2 });
  return true;
}
export function pullAlarm(st, by) {
  if (W.alarm || W.bossOn) return false;
  st.pulled = true; st.shake = 0.4; W.alarmUses = (W.alarmUses || 0) + 1; W.stats.alarms = (W.stats.alarms || 0) + 1;
  const pend = [], kinds = W.lv.backup || ['wanderer', 'escape', 'crutch', 'bell', 'tray', 'o2'];
  const exits = [...Object.values(W.doors).filter((d) => inView(d.x + 39, 10)).map((d) => 'D' + d.num), ...Object.entries(W.elevs).filter(([, e]) => inView(e.x + 40, 10)).map(([k]) => 'E' + k)];
  for (let i = 0; i < ALARM.extra; i++) pend.push({ kind: kinds[Math.floor(W.rnd() * kinds.length)], where: exits.length ? exits[i % exits.length] : (i % 2 ? 'L' : 'R'), t: 1.2 + i * 0.9 });
  W.alarm = { t: 0, st, pend, by };
  let n = 0; for (const e of W.enemies) if (e.alive && e.st !== 'dead' && inView(e.x, -10)) enrage(e, e !== by && n++ < 2);  // only a couple shout (keeps it readable)
  sfx('alarm', { vol: 0.8 }); shake(5); W.stop = Math.max(W.stop, 0.12);
  return true;
}
export function enrage(e, shout = false) { if (!e || e.isBoss) return; e.rageT = W.t + ALARM.enrage; if (!shout) return; e.speechT = 0; floatText(['GRRR!', 'NOW I\'M MAD!', 'WHO PULLED THAT?!'][Math.floor(W.rnd() * 3)], e.x, e.y, 64, '#ff8a6a'); }
export function updateAlarm(dt, spawn) {
  for (const s of W.alarms || []) s.shake = Math.max(0, s.shake - dt);
  const A = W.alarm;
  if (!A) { W.wet = Math.max(0, (W.wet || 0) - dt / ALARM.wetFor); return; }
  A.t += dt;
  if (W.bossOn) { A.pend = []; A.t = Math.max(A.t, ALARM.rain); }  // never let it run into a boss fight
  const raining = A.t < ALARM.rain;
  if (raining) {
    W.wet = Math.min(1, (W.wet || 0) + dt * 0.8);
    if (Math.floor(A.t / 1.5) !== Math.floor((A.t - dt) / 1.5)) sfx('alarm', { vol: 0.65 });
    if (Math.floor(A.t / 1.2) !== Math.floor((A.t - dt) / 1.2)) sfx('sprinkler', { vol: 0.5 });
    if ((A.pud = (A.pud || 0) + dt) > 0.7 && W.shots.filter((s) => s.kind === 'puddle' && s.wet).length < 6) {
      A.pud = 0; addShot({ kind: 'puddle', spr: 'puddle', wet: true, x: W.camX + 30 + W.rnd() * (G.VW - 60), y: Y_MIN + 6 + W.rnd() * (Y_MAX - Y_MIN - 12), z: 0, life: ALARM.wetFor, owner: null, hostile: true });
    }
  }
  for (const q of A.pend) { if (!q.done && A.t >= q.t) { q.done = true; const e = spawn(q.kind, q.where); enrage(e); } }
  A.pend = A.pend.filter((q) => !q.done);
  if (!raining && !A.pend.length) { if (A.st) A.st.pulled = false; W.alarm = null; floatText('...SPRINKLERS OFF.', W.camX + G.VW / 2, Y_MIN + 10, 90, '#8ad8ff'); }
}
export const alarmPending = () => !!(W.alarm && W.alarm.pend.length);
// ---- drawing
export function drawStations(OFF) {
  for (const s of W.alarms || []) {
    const X = s.x - W.camX; if (X < -24 || X > G.VW + 4) continue;
    const lit = s.pulled && Math.floor(W.t * 6) % 2;
    spr(s.pulled ? 'firealarm1' : 'firealarm0', Math.round(X + (s.shake > 0 ? Math.sin(s.shake * 80) * 1.5 : 0)), FLOOR_Y - 58 + OFF);
    if (lit) ellipse(X + 10, FLOOR_Y - 55 + OFF, 14, 9, '#ffffff', 0.35);
  }
}
export function drawWetFloor(OFF) {  // a glossy sheen + reflections while the floor is wet
  const w = W.wet || 0; if (w <= 0.01) return;
  rect(0, FLOOR_Y + OFF, G.VW, 224 - FLOOR_Y, '#7ac8ff', 0.13 * w);
  for (let i = 0; i < 9; i++) { const x = ((i * 97 - W.camX * 1.0) % (G.VW + 80) + G.VW + 80) % (G.VW + 80) - 40; rect(Math.round(x), FLOOR_Y + OFF + 14 + (i * 23) % 88, 26 + (i * 13) % 30, 1, '#e8f6ff', 0.35 * w); }
}
export function drawAlarmFront(reduced) {  // sprinkler rain + the strobe (or the reduced-flash pulse)
  const A = W.alarm; if (!A) return;
  const VW = G.VW, VH = G.VH;
  if (A.t < ALARM.rain) {
    const k = Math.min(1, A.t * 2) * Math.min(1, (ALARM.rain - A.t) * 2);
    for (let i = 0; i < 70; i++) { const x = (i * 53.7 + Math.sin(i) * 20) % VW, y = ((i * 37 + A.t * 380) % (VH + 20)) - 10; rect(Math.round(x), Math.round(y), 1, 6, '#bfe6ff', 0.55 * k); }
    if (reduced) { const p = 0.5 + 0.5 * Math.sin(A.t * Math.PI * 1.2); rect(0, 0, VW, 6, '#ff3a3a', 0.35 * p); rect(0, VH - 6, VW, 6, '#ff3a3a', 0.35 * p); rect(0, 0, VW, VH, '#ff3a3a', 0.06 * p); }
    else { const ph = Math.floor(A.t * 5) % 4;  // 2.5 flashes/s (under the 3/s photosensitivity guideline)
      if (ph === 0) rect(0, 0, VW, VH, '#ff2a2a', 0.22); else if (ph === 2) rect(0, 0, VW, VH, '#ffffff', 0.16); }
    { const on = Math.floor(A.t * 3) % 2, tw = textW('FIRE ALARM!') * 2 + 10; rect(VW / 2 - tw / 2, 58, tw, 20, on ? '#c81a1a' : '#1a1020', 0.85); text('FIRE ALARM!', VW / 2, 60, { col: on ? '#ffffff' : '#ff5a3a', align: 'center', scale: 2 }); }
  }
}
