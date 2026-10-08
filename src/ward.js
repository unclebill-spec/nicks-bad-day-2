// v0.13 PSYCH WARD: the flickering fluorescent lights. Every so often the tubes stutter and the ward goes briefly dark
// (only the glow accents stay lit: exit signs, the caged TVs, the call-light strips, neon), so patients are hard to see for a
// moment, then the lights stutter back. Tuning in WARD. Only on levels with lv.ward; quiet during the boss intro / tally.
import { W } from './world.js';
import { sfx } from './sound.js';

export const WARD = { first: 7, gap: [10, 15], dur: [1.0, 1.7], dark: 0.86, flick: 0.45 };
const rr = (a) => a[0] + Math.random() * (a[1] - a[0]);

export function resetWard(lv) { W.ward = lv && lv.ward ? { next: WARD.first, t: -1, dur: 0, n: 0 } : null; }
export function blackout() {  // start a flicker-out now (tests / debug)
  const F = W.ward; if (!F) return false;
  F.t = 0; F.dur = rr(WARD.dur); F.n++; W.stats.blackouts = (W.stats.blackouts || 0) + 1; sfx('flicker', { vol: 0.6 });
  const h = W.heroes.find((q) => q.alive && q.st !== 'out'); if (h && Math.random() < 0.7) h.say('dark', true);
  return true;
}
export function updateWard(dt) {
  const F = W.ward; if (!F) return;
  const base = W.lv.dark || 0;
  if (F.t >= 0) {
    F.t += dt; const t = F.t, fl = (k) => (Math.floor(t * 22) % 2 ? WARD.dark : base * k);
    if (t < WARD.flick) W.dark = fl(1);
    else if (t < WARD.flick + F.dur) W.dark = WARD.dark;
    else if (t < WARD.flick * 2 + F.dur) W.dark = fl(1);
    else { F.t = -1; W.dark = base; F.next = rr(WARD.gap); }
    return;
  }
  if (W.cleared || W.endT || (W.boss && W.boss.st === 'enter')) return;
  F.next -= dt;
  if (F.next <= 0) blackout();
}
