// v0.16 ROOFTOP HELIPAD AT NIGHT: the wind. Every so often the windsock snaps straight, a "GUST!" warning shows with an arrow
// (which way it will blow), then a gust shoves EVERYONE (nurses, patients, props) across the lanes for a moment. Use it:
// a gust can carry a patient into your combo or out of your reach. Jumping (in the air) rides it out. Only on lv.roof
// levels, quiet during the boss intro / tally. The landing lights round the H pad pulse in a blue / violet / red chase and
// cast light on everyone standing near them (roofLights). ROOF = the tuning.
import { G, rect, text, spr } from './gfx.js';
import { Y_MIN, Y_MAX } from './data.js';
import { W, offY, addFx, word } from './world.js';
import { sfx } from './sound.js';

export const ROOF = { first: 6, gap: [8, 12], warn: 1.2, dur: 1.8, push: 62, drift: 26 };
const rr = (a) => a[0] + Math.random() * (a[1] - a[0]);
const PADCOL = ['#3aa8ff', '#a24dff', '#ff3a4a'];

export function resetRoof(lv) { W.roof = lv && lv.roof ? { next: ROOF.first, t: -1, dir: 1, dx: 1, n: 0 } : null; W.wind = 0; }
export function gust(dir) {  // start a gust now (tests / debug / the chopper): dir +1 = blows toward the front lane, -1 = the back
  const R = W.roof; if (!R) return false;
  const h0 = W.heroes.find((q) => q.alive && q.st !== 'out');
  R.t = 0; R.n++; R.dir = dir || (h0 && h0.y > (Y_MIN + Y_MAX) / 2 ? -1 : 1); R.dx = Math.random() < 0.5 ? -1 : 1;
  W.stats.gusts = (W.stats.gusts || 0) + 1; sfx('gust', { vol: 0.65 });
  if (h0) { word('w_gust', h0.x, h0.y, 70); if (Math.random() < 0.7) h0.say('gust', true); }
  return true;
}
function pushable(a) { return a && a.alive !== false && a.st !== 'dead' && a.st !== 'out' && !a.held && !a.grabbedBy && (a.z || 0) < 6; }
export function updateRoof(dt) {
  const R = W.roof; if (!R) { W.wind = 0; return; }
  if (R.t >= 0) {
    R.t += dt;
    const k = R.t < ROOF.warn ? 0 : Math.sin(Math.PI * Math.min(1, (R.t - ROOF.warn) / ROOF.dur));
    W.wind = k * R.dir;
    if (k > 0) {
      const vy = R.dir * ROOF.push * k * dt, vx = R.dx * ROOF.drift * k * dt;
      for (const a of [...W.heroes, ...W.enemies]) {
        if (!pushable(a) || a.isBoss) continue;
        a.y = Math.max(Y_MIN, Math.min(Y_MAX, a.y + vy)); a.x += vx;
        if (a.isHero) W.stats.gusted = (W.stats.gusted || 0) + dt;
      }
      for (const p of W.props) if (p.st < 2 && !p.carried) p.y = Math.max(Y_MIN, Math.min(Y_MAX, p.y + vy * 0.6));
      if (Math.random() < 0.7) addFx({ type: 'chunk', spr: null, col: '#d8e0ff', sz: 2, x: W.camX + Math.random() * G.VW, y: Y_MIN + Math.random() * (Y_MAX - Y_MIN), z: 6 + Math.random() * 60, vx: R.dx * 260, vy: R.dir * 90, vz: 0, spin: 0, dur: 0.5 });
    }
    if (R.t > ROOF.warn + ROOF.dur) { R.t = -1; W.wind = 0; R.next = rr(ROOF.gap); }
    return;
  }
  W.wind = 0;
  if (W.cleared || W.endT || (W.boss && ['enter', 'defeat'].includes(W.boss.st))) return;
  R.next -= dt;
  if (R.next <= 0) gust();
}
export function drawRoofFloor() {  // under the actors: the live pad lights (a chase round the H), the gust telegraph
  if (!W.lv || !W.lv.roof) return;
  const oy = offY();
  for (const p of W.roofPads || []) {
    const X = p.x - W.camX; if (X < -10 || X > G.VW + 10) continue;
    const on = (Math.floor(W.t * 6) + p.i) % 3 === 0;
    spr('padlight' + p.c, X - 3, p.y + oy - 2, { alpha: on ? 1 : 0.55 });
  }
  const R = W.roof;
  if (R && R.t >= 0 && R.t < ROOF.warn && Math.floor(R.t * 8) % 2) {  // which way: arrows down the edges
    const ch = R.dir > 0 ? 'v' : '^';
    for (const x of [14, G.VW - 22]) for (let k = 0; k < 3; k++) text(ch, x, Y_MIN + oy + 10 + k * 22, { col: '#bfe0ff' });
    rect(0, (R.dir > 0 ? Y_MAX : Y_MIN) + oy - 1, G.VW, 2, '#bfe0ff', 0.5);
  }
}
export function roofLights(L) {
  if (!W.lv || !W.lv.roof) return;
  for (const p of W.roofPads || []) {
    if (p.x - W.camX < -60 || p.x - W.camX > G.VW + 60) continue;
    const on = (Math.floor(W.t * 6) + p.i) % 3 === 0;
    L.push({ x: p.x, y: p.y, r: on ? 30 : 18, ry: on ? 10 : 6, col: PADCOL[p.c], a: on ? 0.95 : 0.6, floor: true });
  }
}
