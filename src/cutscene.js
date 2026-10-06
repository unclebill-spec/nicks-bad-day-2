// v0.4 shift-change cutscenes, Simpsons-arcade style: a comic page of three panels that pop in one after another,
// with caption boxes and speech bubbles (typewriter text). Any button or tap skips the whole scene.
//   start: before Floor 3 (night-shift handoff, Tilly zooms past)   boss: before Turbo Tilly
//   lunch: after the floor tally, into the Breakroom Bonus          next: after the bonus, up to Floor 4
// v0.5: mri: before the MRI boss   night: after Radiology, into the night shift   ending: after the night shift
// v0.9: scoot: after Radiology, Motorcart Marv busts out and the nurses grab the mobility scooters (then the Scooter Run)
import { G, text, rect, spr, frame, anim, sprSize, tintSheet, textW } from './gfx.js';
import { LEVEL1, HEROES } from './data.js';
import { W } from './world.js';
import { lookFor } from './enemy.js';
import { sfx } from './sound.js';

const INK = '#1a1020', PANEL_T = [0, 2.7, 5.4], END = 8.6;
const FLOOR_Y = 118;

function nightNurse() {  // the night-shift nurse: Jackie's build in maroon scrubs, grey hair, white clogs
  return tintSheet('jackie', 'night', [['#283a7a', '#7a2a5a'], ['#1b2756', '#561a40'], ['#1d2a5e', '#66204c'], ['#121a40', '#4a1434'], ['#10183a', '#38102a'], ['#4a2a18', '#b8bcc8'], ['#2e180c', '#868a98'], ['#9a5ae0', '#f4f4f8'], ['#6a34a8', '#b8c2d0']]);
}
const lz = (id, s, lazy, snark) => (id === 'nate' ? lazy : id === 'heather' && snark ? snark : s);  // v0.8 Nasty Nate's lazy take / v0.10 Heather's snarky take on a hero line
const heroIds = () => { const h = W.heroes.map((q) => q.id); return h.length ? h : ['nick']; };
const nm = (id) => (HEROES[id] ? HEROES[id].name : 'NURSE');

// ---- scripts: each panel is (w, h) => { bg, cap, acts, faces, bubbles, fx }
const SCRIPTS = {
  start() {
    const [a, b] = heroIds(), night = nightNurse();
    return [
      (w, h) => ({ bg: ['hall', 0, 58], cap: '6:58 AM. FLOOR 3 WEST.', acts: [{ s: a, a: 'walk', x: w * 0.2, y: h - 3, mv: 14 }, ...(b ? [{ s: b, a: 'walk', x: w * 0.2 - 26, y: h - 1, mv: 14 }] : []), { s: night, a: 'idle', x: w * 0.72, y: h - 3, flip: true }],
        bubbles: [{ x: w * 0.3, y: 4, s: 'Morning! 30 patients, 12 call lights, and one RUNNER.', tail: [w * 0.7, h - 52], at: 0.35, mw: Math.min(220, w * 0.62) }] }),
      (w, h) => ({ bg: ['hall', 620, 58], dark: true, faces: [{ id: a, x: w / 2 - 36, y: h - 72, scale: 2 }],
        bubbles: [{ x: 6, y: 6, s: lz(a, `Did you say... RUNNER?`, 'RUNNER? Ugh. I was playing a game on my phone.', "A RUNNER? I'm your nurse, not your track coach."), tail: [w / 2 - 6, h - 70], at: 0.3, mw: w - 20 }] }),
      (w, h) => ({ bg: ['hall', 1340, 58], speed: true, acts: [{ s: 'tilly', a: 'drive', x: w * 0.85, y: h - 4, flip: true, mv: -70, rate: 10 }],
        bubbles: [{ x: 4, y: 4, s: 'OUT OF MY WAY, SWEETIE! HONK HONK!', tail: [w * 0.7, h - 70], at: 0.2, mw: w - 16, shout: true },
          { x: 4, y: h - 26, s: "One of THOSE days.", tail: [8, h - 2], at: 1.4, mw: w - 16 }] }),
    ];
  },
  boss() {
    const [a, b] = heroIds();
    return [
      (w, h) => ({ bg: ['hall', 3080, 58], cap: 'THE DAYROOM. 11:00 AM.', acts: [{ s: a, a: 'idle', x: w * 0.16, y: h - 3 }, ...(b ? [{ s: b, a: 'idle', x: w * 0.16 + 26, y: h - 1 }] : []), { s: 'tilly', a: 'drive', x: w * 0.74, y: h - 2, flip: true, rate: 6 }],
        bubbles: [{ x: w * 0.3, y: 6, s: 'This is MY dayroom, sweeties! My STORIES are on!', tail: [w * 0.7, h - 62], at: 0.35, mw: Math.min(220, w * 0.6), shout: true }] }),
      (w, h) => ({ bg: null, burst: '#e83a6a', faces: [{ id: 'tilly', x: w / 2 - 36, y: h - 72, scale: 2 }],
        bubbles: [{ x: 6, y: 6, s: 'NOBODY touches the remote!', tail: [w / 2, h - 72], at: 0.25, mw: w - 20, shout: true }] }),
      (w, h) => ({ bg: ['hall', 2860, 58], faces: [{ id: a, x: b ? 6 : w / 2 - 36, y: h - 72, scale: 2 }, ...(b ? [{ id: b, x: w - 78, y: h - 72, scale: 2, flip: true }] : [])],
        bubbles: [{ x: 4, y: 4, s: lz(a, 'Time for your meds, Tilly.', 'Time for your meds, Tilly.', "Hospital food isn't room service, Tilly. Meds."), tail: [b ? 40 : w / 2, h - 70], at: 0.25, mw: w - 16 }, { x: 4, y: 30, s: b ? `...and a NAP.` : '...and a NAP. For me.', tail: [b ? w - 40 : w / 2, h - 70], at: 1.3, mw: w - 16 }] }),
    ];
  },
  lunch() {
    const [a, b] = heroIds(), thief = lookFor('wanderer', 3);
    return [
      (w, h) => ({ bg: ['hall', 600, 58], cap: '12:30 PM. FLOOR 3: QUIET. FOR NOW.', acts: [{ s: a, a: 'win', x: w * 0.3, y: h - 3, rate: 3 }, ...(b ? [{ s: b, a: 'win', x: w * 0.3 + 34, y: h - 1, rate: 3 }] : [])],
        bubbles: [{ x: w * 0.5, y: 20, s: lz(a, 'Finally... LUNCH BREAK!', 'Is it time for my break yet? ...It IS?!', "Lunch. Nobody ring for ice chips."), tail: [w * 0.36, h - 50], at: 0.35, mw: Math.min(200, w * 0.45) }] }),
      (w, h) => ({ bg: ['break', 'fridge', 58], cap: 'MEANWHILE, IN THE BREAKROOM...', fridge: true, acts: [{ s: thief, a: 'atk', x: w * 0.42, y: h - 3, rate: 6 }],
        bubbles: [{ x: 4, y: h - 30, s: 'Nom nom nom!', tail: [w * 0.42, h - 52], at: 0.4, mw: w - 16 }] }),
      (w, h) => ({ bg: null, burst: '#ff8a1e', faces: [{ id: a, x: w / 2 - 36, y: h - 72, scale: 2 }],
        bubbles: [{ x: 4, y: 4, s: lz(a, "HEY! That's MY yogurt! It was LABELED!", "HEY! That's MY yogurt! It was LABELED!", "HEY! This isn't a restaurant! That's MY yogurt!"), tail: [w / 2, h - 70], at: 0.25, mw: w - 16, shout: true }] }),
    ];
  },
  next() {
    const [a, b] = heroIds();
    return [
      (w, h) => ({ bg: ['hall', 1130, 58], cap: '3:00 PM. FLOOR 3: DONE.', acts: [{ s: a, a: 'idle', x: w * 0.36, y: h - 3, flip: true }, ...(b ? [{ s: b, a: 'idle', x: w * 0.36 + 28, y: h - 1, flip: true }] : [])],
        bubbles: [{ x: w * 0.5, y: 20, s: 'Snacks: saved. Shift: NOT done.', tail: [w * 0.4, h - 52], at: 0.35, mw: Math.min(180, w * 0.45) }] }),
      (w, h) => ({ bg: null, elevator: true, cap: 'THE PAGER GOES OFF...',
        bubbles: [{ x: 4, y: h - 30, s: '*BZZT* Floor 4, Radiology. STAT!', tail: [w - 10, h - 40], at: 0.3, mw: w - 16, shout: true }] }),
      (w, h) => ({ bg: null, glow: true, cap: 'FLOOR 4: RADIOLOGY', faces: [{ id: a, x: w / 2 - 36, y: h - 72, scale: 2 }],
        bubbles: [{ x: 4, y: 20, s: lz(a, 'Why is everything up there... GLOWING?', "Glowing? Ugh. I'm not charting that.", "Glowing? Great. Nobody's charting that either."), tail: [w / 2, h - 70], at: 0.4, mw: w - 16 }] }),
    ];
  },
  mri() {
    const [a, b] = heroIds();
    return [
      (w, h) => ({ bg: ['rad', 2900, 58], dark: true, cap: 'THE MRI SUITE. 5:00 PM.', acts: [{ s: a, a: 'idle', x: w * 0.14, y: h - 3 }, ...(b ? [{ s: b, a: 'idle', x: w * 0.14 + 26, y: h - 1 }] : []), { s: 'mri', a: 'idle', x: w * 0.7, y: h + 2, rate: 4 }],
        bubbles: [{ x: w * 0.36, y: 18, s: 'PLEASE HOLD STILL. SCANNING... EVERYTHING!', tail: [w * 0.7, h - 70], at: 0.35, mw: Math.min(230, w * 0.6), shout: true }] }),
      (w, h) => ({ bg: null, burst: '#3aa8ff', acts: [{ s: 'mri', a: 'pull', x: w / 2, y: h + 24, scale: 1.6, rate: 10 }],
        bubbles: [{ x: 6, y: 4, s: 'MAGNET... ON!', tail: [w / 2, h - 60], at: 0.25, mw: w - 20, shout: true }] }),
      (w, h) => ({ bg: ['rad', 2700, 58], dark: true, floaty: true, faces: [{ id: a, x: w / 2 - 36, y: h - 72, scale: 2 }],
        bubbles: [{ x: 4, y: 4, s: 'Why is my badge clip FLOATING?', tail: [w / 2, h - 70], at: 0.25, mw: w - 16 }, { x: 4, y: 36, s: 'Drop the IV pole! DROP IT!', tail: [w / 2, h - 70], at: 1.4, mw: w - 16 }] }),
    ];
  },
  scoot() {
    const [a, b] = heroIds();
    return [
      (w, h) => ({ bg: ['rad', 300, 58], speed: true, cap: '6:30 PM. RADIOLOGY: DONE. GOING HOME.', acts: [{ s: a, a: 'idle', x: w * 0.14, y: h - 3 }, ...(b ? [{ s: b, a: 'idle', x: w * 0.14 + 26, y: h - 1 }] : []),
        { s: 'marv', a: 'taunt', ride: 'marvcart', x: w * 1.04, y: h - 2, mv: -48, rate: 6 }],
        bubbles: [{ x: w * 0.4, y: 18, s: 'OUTTA MY WAY, NURSES! MOTORCART MARV IS BUSTING OUT!', tail: [w * 0.75, h - 66], at: 0.3, mw: Math.min(230, w * 0.6), shout: true }] }),
      (w, h) => ({ bg: null, burst: '#ff8a1e', faces: [{ id: a, x: w / 2 - 36, y: h - 72, scale: 2 }],
        bubbles: [{ x: 4, y: 4, s: lz(a, 'Was that a mobility scooter... with FLAMES?', 'Flames? Ugh. Can someone else chase him?', "Flames? On a mobility scooter? I'm charting that."), tail: [w / 2, h - 70], at: 0.25, mw: w - 16 }] }),
      (w, h) => ({ bg: ['rad', 900, 58], cap: 'THE SCOOTER CHARGING STATION', acts: [{ s: a, a: 'scoot', ride: 'scoot_red', x: w * 0.3, y: h - 4, mv: 22, rate: 4 }, ...(b ? [{ s: b, a: 'scoot', ride: 'scoot_blue', x: w * 0.3 - 40, y: h - 2, mv: 22, rate: 4 }] : [])],
        bubbles: [{ x: 4, y: 4, s: lz(a, 'Grab a scooter! He went down the long hall!', "Wait. I get to SIT? ...I'm in.", "Grab a scooter! I'm your nurse, not your chauffeur, Marv!"), tail: [w * 0.3, h - 50], at: 0.25, mw: w - 16, shout: a !== 'nate' }] }),
    ];
  },
  night() {
    const [a, b] = heroIds();
    return [
      (w, h) => ({ bg: ['hall', 600, 58], dark: true, moon: true, cap: '11:00 PM. BACK ON FLOOR 3.', acts: [{ s: a, a: 'idle', x: w * 0.3, y: h - 3 }, ...(b ? [{ s: b, a: 'idle', x: w * 0.3 + 28, y: h - 1 }] : [])],
        bubbles: [{ x: w * 0.46, y: 12, s: lz(a, 'Double shift. Quiet night, right?', 'Double shift? You made me get up from my chair.', 'Double shift. One more ice chip call and I walk.'), tail: [w * 0.33, h - 52], at: 0.35, mw: Math.min(200, w * 0.48) }] }),
      (w, h) => ({ bg: null, blackout: true, cap: 'KA-CHUNK!',
        bubbles: [{ x: 4, y: h - 26, s: '...nurse?  ...nurse?  ...NURSE?', tail: [w * 0.5, h - 50], at: 0.6, mw: w - 16 }] }),
      (w, h) => ({ bg: null, flashlight: true, faces: [{ id: a, x: w / 2 - 36, y: h - 72, scale: 2 }],
        bubbles: [{ x: 4, y: 4, s: 'WHO SAID THE Q-WORD?!', tail: [w / 2, h - 70], at: 0.25, mw: w - 16, shout: true }] }),
    ];
  },
  ending() {
    const [a, b] = heroIds(), night = nightNurse();
    return [
      (w, h) => ({ bg: ['hall', 0, 58], sunrise: true, cap: '7:00 AM. SHIFT CHANGE. AGAIN.', acts: [{ s: a, a: 'win', x: w * 0.24, y: h - 3, rate: 3 }, ...(b ? [{ s: b, a: 'win', x: w * 0.24 + 28, y: h - 1, rate: 3 }] : []), { s: night, a: 'idle', x: w * 0.74, y: h - 3, flip: true }],
        bubbles: [{ x: w * 0.36, y: 4, s: 'Morning! How was the night shift?', tail: [w * 0.72, h - 52], at: 0.35, mw: Math.min(200, w * 0.55) }] }),
      (w, h) => ({ bg: null, burst: '#ff8a1e', faces: [{ id: a, x: w / 2 - 36, y: h - 72, scale: 2 }],
        bubbles: [{ x: 4, y: 4, s: 'A wheelchair drag race, a magnet that ate my IV pole, and a blackout.', tail: [w / 2, h - 70], at: 0.25, mw: w - 16 }] }),
      (w, h) => ({ bg: ['hall', 40, 58], sunrise: true, acts: [{ s: a, a: 'walk', x: w * 0.3, y: h - 3, mv: -30, flip: true }, ...(b ? [{ s: b, a: 'walk', x: w * 0.3 + 26, y: h - 1, mv: -30, flip: true }] : [])],
        bubbles: [{ x: 4, y: 4, s: lz(a, 'NOPE! See you tomorrow!', 'NOPE! See you tomorrow!', "NOPE! Here's a rag. See you tomorrow!"), tail: [w * 0.3, h - 52], at: 0.25, mw: w - 16, shout: true }] }),
    ];
  },
};

export function makeCut(id) { return { id, t: 0, lastPanel: -1, panels: (SCRIPTS[id] || SCRIPTS.start)() }; }
// returns true when the scene is over (timed out or skipped)
export function updateCut(cs, dt, skip) {
  cs.t += dt;
  const p = PANEL_T.filter((t) => cs.t >= t).length - 1;
  if (p !== cs.lastPanel) { cs.lastPanel = p; sfx(p === 0 ? 'page' : 'whoosh', { vol: 0.45 }); }
  return skip || cs.t > END;
}

// ---------------------------------------------------------------- drawing
function wrap(s, maxW) {
  const words = s.split(' '), lines = []; let cur = '';
  for (const w of words) { const t = cur ? cur + ' ' + w : w; if (textW(t) > maxW && cur) { lines.push(cur); cur = w; } else cur = t; }
  if (cur) lines.push(cur);
  return lines;
}
function poly(pts, fill, stroke) {
  const c = G.ctx; c.beginPath(); pts.forEach(([x, y], i) => (i ? c.lineTo(x, y) : c.moveTo(x, y))); c.closePath();
  c.fillStyle = fill; c.fill(); if (stroke) { c.strokeStyle = stroke; c.lineWidth = 1; c.stroke(); }
}
function bubble(px, py, pw, ph, B, local) {
  if (local < B.at) return;
  const lines = wrap(B.s, B.mw), n = Math.floor((local - B.at) * 38);
  const bw = Math.max(...lines.map((l) => textW(l))) + 10, bh = lines.length * 10 + 6;
  const x = Math.round(px + Math.max(2, Math.min(pw - bw - 2, B.x))), y = Math.round(py + Math.max(2, Math.min(ph - bh - 2, B.y)));
  const fill = B.shout ? '#fff27a' : '#ffffff';
  // tail toward the speaker
  const tx = px + B.tail[0], ty = py + B.tail[1], cx = Math.max(x + 8, Math.min(x + bw - 8, tx)), below = ty > y + bh;
  const by = below ? y + bh - 1 : y + 1;
  poly([[cx - 5, by], [cx + 5, by], [tx, ty]], fill, INK);
  if (B.shout) for (let i = 0; i < 10; i++) { const a = i / 10 * Math.PI * 2; const sx = x + bw / 2 + Math.cos(a) * (bw / 2 + 4), sy = y + bh / 2 + Math.sin(a) * (bh / 2 + 4); poly([[sx, sy], [x + bw / 2 + Math.cos(a + 0.2) * bw / 2, y + bh / 2 + Math.sin(a + 0.2) * bh / 2], [x + bw / 2 + Math.cos(a - 0.2) * bw / 2, y + bh / 2 + Math.sin(a - 0.2) * bh / 2]], fill, INK); }
  rect(x - 1, y, bw + 2, bh, INK); rect(x, y - 1, bw, bh + 2, INK); rect(x, y, bw, bh, fill);
  if (!below) { /* tail drawn above */ } else rect(cx - 4, y + bh - 1, 8, 1, fill);
  let left = n;
  lines.forEach((l, i) => { if (left <= 0) return; const part = l.slice(0, left); left -= l.length + 1; text(part, x + 5, y + 4 + i * 10, { col: INK, shadow: null }); });
}
function hallBits(sx, sy, px, py, pw) {  // live parts of the hallway the pre-rendered bg lacks: room doors + elevator doors
  for (const [wx, kind, extra] of LEVEL1.wall) {
    if (wx < sx - 90 || wx > sx + pw + 10) continue;
    if (kind === 'door') { spr('door0', px + wx - sx, py + FLOOR_Y - 68 - sy); text(String(extra), px + wx + 39 - sx, py + 65 - sy, { col: '#ffffff', shadow: null }); }
    if (kind === 'elev') { const X = px + wx - sx, Y = py + FLOOR_Y - 82 - sy; spr('elev_door', X + 8, Y + 14); spr('elev_door', X + 40, Y + 14); }
  }
}
function drawPanel(P, px, py, pw, ph, local, idx) {
  const c = G.ctx;
  const k = Math.min(1, local / 0.16), slide = Math.round((1 - k) * (idx === 1 ? -24 : 24));
  px += slide;
  // ink frame
  rect(px - 3, py - 3, pw + 6, ph + 6, INK); rect(px - 1, py - 1, pw + 2, ph + 2, '#ffffff');
  c.save(); c.beginPath(); c.rect(px, py, pw, ph); c.clip();
  rect(px, py, pw, ph, '#2a3060');
  if (P.bg) {
    const [src, x0, y0] = P.bg;
    const img = src === 'break' ? W.breakBg : src === 'rad' ? (W.radBg || W.hallBg) : W.hallBg;
    let sx = x0 === 'fridge' ? Math.max(0, (W.breakFridgeX || 300) - pw * 0.55) : x0;
    if (img) { sx = Math.max(0, Math.min(img.width - pw, sx)); c.drawImage(img, sx, y0, pw, ph, px, py, pw, ph); }
    if (src === 'hall') hallBits(sx, y0, px, py, pw);
    if (P.fridge && W.breakFridgeX) spr('fridge_open', px + W.breakFridgeX - sx, py + FLOOR_Y + 3 - 72 - y0);
    if (P.dark) rect(px, py, pw, ph, '#0a1030', 0.45);
    if (P.moon) { rect(px, py, pw, ph, '#04061a', 0.35); for (let i = 0; i < 3; i++) { c.globalAlpha = 0.18; c.fillStyle = '#3aa8ff'; c.beginPath(); c.ellipse(px + pw * (0.2 + i * 0.3), py + ph - 8, 30, 6, 0, 0, Math.PI * 2); c.fill(); } c.globalAlpha = 1; }
    if (P.sunrise) { c.globalAlpha = 0.28; c.fillStyle = '#ff9a4a'; c.fillRect(px, py, pw, ph); c.globalAlpha = 0.25; c.fillStyle = '#ffe8a0'; c.beginPath(); c.ellipse(px + pw * 0.85, py + 10, 60, 40, 0, 0, Math.PI * 2); c.fill(); c.globalAlpha = 1; }
  }
  if (P.burst) {  // dramatic close-up: radial burst
    rect(px, py, pw, ph, P.burst);
    const cx = px + pw / 2, cy = py + ph / 2;
    for (let i = 0; i < 14; i++) { const a0 = i / 14 * Math.PI * 2 + local * 0.6, a1 = a0 + 0.18; poly([[cx, cy], [cx + Math.cos(a0) * 300, cy + Math.sin(a0) * 300], [cx + Math.cos(a1) * 300, cy + Math.sin(a1) * 300]], '#fff27a'); }
  }
  if (P.elevator) {  // elevator call panel close-up: the floor indicator ticking 3 -> 4
    rect(px, py, pw, ph, '#b8c0cc'); rect(px + pw / 2 - 40, py + 20, 80, 30, '#20222c'); rect(px + pw / 2 - 38, py + 22, 76, 26, '#101218');
    const n = local > 1.0 ? '4' : '3'; text(n, px + pw / 2 - 6, py + 28, { col: '#ff5a3a', scale: 2, shadow: null }); text('^', px + pw / 2 + 16, py + 30, { col: Math.floor(local * 4) % 2 ? '#ffe84a' : '#5a3a20', shadow: null });
    rect(px + pw / 2 - 8, py + 58, 16, 16, '#e4e8f0'); rect(px + pw / 2 - 6, py + 60, 12, 12, local > 0.5 ? '#ffe84a' : '#8a94a4');
  }
  if (P.glow) {  // Floor 4 teaser: dark room, pulsing neon-blue glow (Bill's cold fire), x-ray lightboxes
    rect(px, py, pw, ph, '#040a1a'); const g = 0.35 + Math.sin(local * 5) * 0.15;
    for (let r = 5; r > 0; r--) { c.globalAlpha = g / r; c.fillStyle = '#3aa8ff'; c.beginPath(); c.ellipse(px + pw / 2, py + ph / 2, r * 26, r * 16, 0, 0, Math.PI * 2); c.fill(); }
    c.globalAlpha = 1; rect(px + 8, py + 26, 34, 44, '#cfe8ff', 0.5); rect(px + pw - 42, py + 26, 34, 44, '#cfe8ff', 0.5);
  }
  if (P.blackout) {  // night: lights out, only eyes, a red exit sign and blinking call lights
    rect(px, py, pw, ph, '#03040c');
    rect(px + pw - 40, py + 8, 30, 10, '#ff3a4a', 0.9); text('EXIT', px + pw - 37, py + 10, { col: '#ffffff', shadow: null });
    for (let i = 0; i < 3; i++) if (Math.floor(local * 3 + i) % 2) rect(px + 20 + i * 50, py + 26, 6, 4, '#ff4a3a');
    for (let i = 0; i < 6; i++) { const ex = px + 16 + ((i * 53) % (pw - 30)), ey = py + 40 + ((i * 29) % (ph - 60)); if (local > 0.3 + i * 0.15 && Math.floor(local * 1.3 + i) % 4) { rect(ex, ey, 3, 2, '#fff6a0'); rect(ex + 7, ey, 3, 2, '#fff6a0'); } }
  }
  if (P.flashlight) { rect(px, py, pw, ph, '#03040c'); c.globalAlpha = 0.85; c.fillStyle = '#fff2b0'; c.beginPath(); c.moveTo(px + pw / 2, py + ph + 10); c.lineTo(px + pw / 2 - 70, py - 10); c.lineTo(px + pw / 2 + 70, py - 10); c.closePath(); c.fill(); c.globalAlpha = 1; }
  if (P.speed) for (let i = 0; i < 10; i++) rect(px + ((i * 47 - local * 400) % pw + pw) % pw, py + 30 + (i * 17) % (ph - 34), 22, 1, '#ffffff', 0.7);
  for (const A of P.acts || []) {
    const an = anim(A.s, A.a); if (!an) continue;
    const i = an.s + (Math.floor(local * (A.rate || 8)) % an.n), X = px + A.x + (A.mv || 0) * local, Y = py + A.y;
    if (A.ride) {  // v0.9: on a vehicle (a nurse's mobility scooter or Motorcart Marv's hot rod), drawn under the rider
      const marv = A.ride === 'marvcart', wh = Math.floor(local * 12) % 2;
      spr(A.ride + wh, X, Y, { ax: marv ? 34 : 22, ay: marv ? 49 : 43, flip: !!A.flip });
      frame(A.s, i, X + (marv ? -1 : -4) * (A.flip ? -1 : 1), Y - (marv ? 8 : 4), { flip: !!A.flip });
      continue;
    }
    frame(A.s, i, X, Y, { flip: !!A.flip, scale: A.scale || 1 });
  }
  if (P.floaty) for (let i = 0; i < 6; i++) { const k = (local * 0.6 + i * 0.17) % 1; rect(px + 10 + i * (pw / 6), py + ph - 10 - k * (ph - 20), 4, 3, ['#c8ccd6', '#ffe84a', '#8ad8ff'][i % 3]); }
  for (const F of P.faces || []) spr(`face_${F.id}`, px + F.x + (F.flip ? 36 * F.scale : 0), py + F.y, { scale: F.scale, flip: !!F.flip });
  if (P.cap) { const w = Math.min(pw - 8, textW(P.cap) + 8); rect(px + 2, py + 2, w + 2, 13, INK); rect(px + 3, py + 3, w, 11, '#ffe84a'); text(P.cap, px + 7, py + 5, { col: INK, shadow: null }); }
  for (const B of P.bubbles || []) bubble(px, py, pw, ph, B, local);
  if (local < 0.12) rect(px, py, pw, ph, '#ffffff', (0.12 - local) * 6);
  c.restore();
}
export function drawCut(cs) {
  const VW = G.VW, VH = G.VH;
  rect(0, 0, VW, VH, '#141c40');
  for (let y = 0; y < VH; y += 4) for (let x = (y / 4) % 2 ? 2 : 0; x < VW; x += 4) rect(x, y, 1, 1, '#22305e');  // halftone page
  const m = 7, aw = VW - m * 2, ah = Math.round((VH - m * 3) * 0.5), bw = Math.floor((VW - m * 3) / 2), bh = VH - m * 3 - ah;
  const rects = [[m, m, aw, ah], [m, m * 2 + ah, bw, bh], [m * 2 + bw, m * 2 + ah, VW - m * 3 - bw, bh]];
  cs.panels.forEach((fn, i) => {
    const local = cs.t - PANEL_T[i]; if (local < 0) return;
    const [x, y, w, h] = rects[i];
    if (!cs.cache) cs.cache = [];
    const P = cs.cache[i] || (cs.cache[i] = fn(w, h));
    drawPanel(P, x, y, w, h, local, i);
  });
  if (Math.floor(cs.t * 2) % 2) text('ANY BUTTON: SKIP', VW - 4, VH - 9, { col: '#ffffff', align: 'right' });
}
