// In-game HUD, drawn in the pixel buffer: portraits, health, lives, score, Code Blue meter, weapon, combo counter,
// the last enemy you hit, GO arrow, boss bar, continue countdowns and toasts.
import { G, spr, text, rect, frameRect, panel, sprSize, textW, heroName } from './gfx.js';
import { HEROES, WEAPONS } from './data.js';
import { W } from './world.js';

const pad = (n, l = 7) => String(Math.floor(n)).padStart(l, '0');

function portrait(id, x, y, hurt) {
  const c = G.ctx; c.save(); c.beginPath(); c.rect(x, y, 24, 24); c.clip();
  spr(`face_${id}${hurt ? '_hurt' : ''}`, x - 6, y - 3);
  c.restore(); frameRect(x - 1, y - 1, 26, 26, '#1a1020'); frameRect(x - 2, y - 2, 28, 28, '#ffe84a');
}
function bar(x, y, w, h, v, col, back = '#3a0a14') {
  rect(x - 1, y - 1, w + 2, h + 2, '#1a1020'); rect(x, y, w, h, back);
  rect(x, y, Math.max(0, Math.round(w * v)), h, col); rect(x, y, Math.max(0, Math.round(w * v)), 1, '#ffffff', 0.35);
  for (let i = 1; i < 10; i++) rect(x + Math.round(w * i / 10), y, 1, h, '#1a1020', 0.35);
}

export function drawHUD(game) {
  const VW = G.VW, left = 30, slotW = Math.min(180, (VW - left - 8) / 2);  // v0.10.1: 180 fits NERVOUS NICK / KILLER KIM beside the score
  for (let s = 0; s < 2; s++) {
    const h = W.heroes.find((q) => q.slot === s);
    const x = s === 0 ? left : VW - slotW - 4, y = 4;
    if (!h) {
      if (s === 1 && game.mode !== 'attract' && !W.scoot && Math.floor(W.t * 2) % 2) text('2P PRESS START', x + slotW / 2, y + 10, { col: '#8ad8ff', align: 'center' });
      continue;
    }
    if (h.st === 'out') {
      if (game.continuesLeft() > 0 && h.continueT > 0) { const [hn, ha] = heroName(h.d, slotW - 34); text(hn, x + 30, y + 2, { col: '#ffffff', adv: ha }); text(`CONTINUE? ${Math.ceil(h.continueT - 1)}`, x + 30, y + 13, { col: Math.floor(W.t * 4) % 2 ? '#ffe84a' : '#ff8a1e' }); portrait(h.id, x, y + 1, true); }
      else text('SHIFT OVER', x + slotW / 2, y + 10, { col: '#ff8ac0', align: 'center' });
      continue;
    }
    portrait(h.id, x, y + 1, h.st === 'hurt' || h.st === 'fall' || h.hp < h.maxHp * 0.25);
    let [hn, ha] = heroName(h.d, slotW - 34 - 60), sa = 8;  // full name when it fits next to the score, else the short one
    if (hn !== h.d.name) { const [n2, a2] = heroName(h.d, slotW - 34 - 53, 6); if (n2 === h.d.name) { hn = n2; ha = a2; sa = 7; } }  // CHARGE JACKIE / WONDERFUL WILL: squeeze the score too
    text(hn, x + 30, y, { col: s ? '#8ad8ff' : '#ffe84a', adv: ha });
    text(pad(h.score), x + slotW - 4, y, { col: '#ffffff', align: 'right', adv: sa });
    const bw = slotW - 34;
    bar(x + 30, y + 10, bw, 5, h.hp / h.maxHp, h.hp < h.maxHp * 0.3 ? (Math.floor(W.t * 6) % 2 ? '#ff3a3a' : '#ffe84a') : '#3ae86a');
    // Code Blue meter
    const full = h.meter >= 100;
    bar(x + 30, y + 18, bw - 30, 3, h.meter / 100, full && Math.floor(W.t * 8) % 2 ? '#ffffff' : '#3a7aff', '#0a1430');
    text(`x${h.lives}`, x + slotW - 4, y + 15, { col: '#ffffff', align: 'right' });
    rect(x + 30 + Math.round((bw - 30) / 2), y + 17, 1, 5, '#ffe84a', 0.8);  // half-meter tick: Charge Nurse team-up (2P)
    for (const f of [1 / 3, 2 / 3]) rect(x + 30 + Math.round((bw - 30) * f), y + 17, 1, 5, h.meter >= f * 100 - 0.01 ? '#c8f0ff' : '#5a6a9a', 0.9);  // v0.6 tiers: each 1/3 = one Ativan jab
    const mate = W.heroes.length > 1 && W.heroes.find((q) => q !== h && q.alive && q.st !== 'out');
    if (W.scoot) { /* v0.9 Scooter Run: no SP moves on a scooter */ }
    else if (full) text('CODE BLUE: SP!', x + 30, y + 24, { col: Math.floor(W.t * 6) % 2 ? '#8ad8ff' : '#ffffff' });
    else if (h.meter >= 100 / 3 - 0.01 && !h.weapon && !(mate && h.meter >= 50 && mate.meter >= 50)) text('ATIVAN: SP!', x + 30, y + 24, { col: Math.floor(W.t * 4) % 2 ? '#c8a0ff' : '#ffffff' });
    else if (mate && h.meter >= 50 && mate.meter >= 50 && !h.weapon) text('TEAM UP: SP+SP!', x + 30, y + 24, { col: Math.floor(W.t * 6) % 2 ? '#ffe84a' : '#ffffff' });
    else if (h.weapon) {
      spr(h.weapon.w.spr, x + 30, y + 23, { scale: 0.5 });
      const u = h.weapon.w.spray ? `${Math.max(0, Math.ceil(h.weapon.ammo * 10))}` : `${h.weapon.uses}`;
      text(`${h.weapon.w.name} ${u}`, x + 52, y + 24, { col: '#c8e4ff' });
    }
    if (h.combo >= 3) text(`${h.combo} HITS!`, x + 30, y + 34 + (h.weapon || full ? 0 : -8), { col: Math.floor(W.t * 10) % 2 ? '#ffe84a' : '#ff8a1e' });
    // last enemy hit
    if (h.lastFoe && h.lastFoeT > W.t) {
      const e = h.lastFoe; const ny = y + 44;
      text(e.d ? e.d.name : '', x + 30, ny, { col: '#ffffff' });
      bar(x + 30, ny + 9, Math.min(bw, 90), 3, e.hp / e.maxHp, '#ff8a1e');
    }
  }
  // GO arrow
  if (W.go > 0 && Math.floor(W.go * 3) % 2) { spr('w_go', VW - 44, 104, { ax: 0 }); text('>', VW - 14, 110, { col: '#ffe84a', scale: 2 }); }
  // boss bar
  const b = W.boss;
  if (b && b.st !== 'enter' || (b && b.t > 0.4)) {
    if (b) {
      const bw = Math.min(200, VW - 120), bx = (VW - bw) / 2, by = 46;
      if (b.drawIcon) b.drawIcon(bx - 30, by - 8); else spr(b.mini ? 'face_lou' : 'face_tilly', bx - 30, by - 8, { scale: 0.75 });
      text(b.name + (b.phase === 2 ? '  ' + (b.p2label || 'TURBO!') : ''), bx, by - 10, { col: b.phase === 2 ? '#8ad8ff' : '#d8b4f4' });
      bar(bx, by, bw, 6, (b.hp / b.maxHp) * b.shown, b.phase === 2 ? '#a24dff' : b.isMRI ? '#3aa8ff' : '#ff4a9a');
      const hint = b.hint ? b.hint() : b.st === 'open' ? 'HIT THE BATTERY!' : null;
      if (hint && Math.floor(W.t * 6) % 2) text(hint, VW / 2, by + 12, { col: '#ffe84a', align: 'center' });
    }
  }
  // floor progress strip (where you are on the floor), small, under the P HUD
  // toasts
  if (game.toasts.length) {
    const t = game.toasts[0]; const w = textW(t.s) + 16;
    panel((VW - w) / 2, G.VH - 64, w, 16, '#1a2450', '#8ad8ff', 0.9); text(t.s, VW / 2, G.VH - 60, { col: '#ffffff', align: 'center' });
  }
}
