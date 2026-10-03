// Nick's Very Bad, Terrible Bad Day Part II: boot, the fixed-step loop, scenes (title, hero select, stage, tally,
// teaser, game over, high scores), pause / settings / how-to menus, saves, display presets and fullscreen / install.
import { G, initGfx, resize, present, text, spr, rect, panel, frame, anim, textW, sprSize, frameRect, ellipse } from './gfx.js';
import { loaded, Q, audio } from '../kit/common.js';
import { createDisplay } from '../kit/display.js';
import { C, initControls, pollControls, readPlayer, menuIntents } from './controls.js';
import { initSound, sfx, playMusic, stopMusic, setVolumes, preloadMusic, S as SND } from './sound.js';
import { HEROES, HERO_ORDER, LEVEL1, DIFF } from './data.js';
import { dropItem } from './world.js';
import { W, buildLevel, drawBackground, updateWorld, updateCamera, drawProp, drawItem, drawShot, drawFx, offY, floatText, makeProp, hitProp, rollLoot } from './world.js';
import { Director, spawn } from './stage.js';
import { Hero } from './hero.js';
import { drawHUD } from './hud.js';

// ------------------------------------------------------------------ save
const SAVE_KEY = 'nbd2.save';
const DEF = { hi: [], best: 0, plays: 0, settings: { music: 0.6, sfx: 0.8, diff: 'normal', cont: 3, shake: true, touch: 'auto' } };
function loadSave() { try { const s = JSON.parse(localStorage.getItem(SAVE_KEY) || 'null'); if (s) return { ...DEF, ...s, settings: { ...DEF.settings, ...(s.settings || {}) } }; } catch (e) { /* private mode */ } return JSON.parse(JSON.stringify(DEF)); }
export const save = loadSave();
function writeSave() { try { localStorage.setItem(SAVE_KEY, JSON.stringify(save)); } catch (e) { /* private mode */ } }

// ------------------------------------------------------------------ game state
const game = window.__game = {
  scene: 'boot', overlay: null, mode: 1, t: 0, toasts: [], players: [], creditsUsed: 0, menu: null, skipOk: false, sel: null, tally: null,
  continuesLeft() { const c = save.settings.cont; return c >= 99 ? 99 : Math.max(0, c - this.creditsUsed); },
  toast(html) { const s = String(html).replace(/<br\s*\/?>/gi, ' - ').replace(/<[^>]+>/g, '').replace(/&#\d+;/g, '').replace(/&[a-z]+;/g, '').replace(/[^\x20-\x7e]/g, '').trim(); if (s) this.toasts.push({ s: s.slice(0, 46), t: 2.6 }); },
};
let display = null;

// ------------------------------------------------------------------ resolution
function applyRes(D) {
  if (!G.buf) return;
  const VH = D.res === 'retro' ? 240 : 224;
  const VW = Math.max(300, Math.min(480, Math.round(VH * D.aspect)));
  const dpr = Math.min(devicePixelRatio || 1, 3);
  let k = Math.max(1, Math.round(D.h * dpr / VH));
  if (D.res === 'retro') k = 1; else if (D.res === 'p720') k = 3; else if (D.res === 'p1080') k = 5; else k = Math.min(k, D.res === 'phone' ? 4 : 6);
  resize(VW, VH, k);
}

// ------------------------------------------------------------------ menus (canvas lists, keyboard / pad / touch / mouse)
function Menu(title, items, opts = {}) { return { title, items, sel: 0, rects: [], ...opts }; }
const onoff = (v) => (v ? 'ON' : 'OFF');
function settingsMenu(back) {
  const st = save.settings;
  const vol = (k) => ({ label: k === 'music' ? 'MUSIC' : 'SFX', value: () => '#'.repeat(Math.round(st[k] * 10)).padEnd(10, '-'), left: () => { st[k] = Math.max(0, +(st[k] - 0.1).toFixed(1)); SND.vol[k] = st[k]; setVolumes(); writeSave(); sfx('blip'); }, right: () => { st[k] = Math.min(1, +(st[k] + 0.1).toFixed(1)); SND.vol[k] = st[k]; setVolumes(); writeSave(); sfx('blip'); } });
  const cyc = (k, list, labels) => ({ left: () => { st[k] = list[(list.indexOf(st[k]) - 1 + list.length) % list.length]; writeSave(); applySettings(); }, right: () => { st[k] = list[(list.indexOf(st[k]) + 1) % list.length]; writeSave(); applySettings(); }, value: () => labels[list.indexOf(st[k])] });
  return Menu('SETTINGS', [
    vol('music'), vol('sfx'),
    { label: 'DISPLAY', value: () => display.label('res').toUpperCase().replace('(LANDSCAPE)', '').slice(0, 18), left: () => setRes(-1), right: () => setRes(1), act: () => setRes(1) },
    { label: 'ASPECT', value: () => display.label('aspect').toUpperCase(), left: () => display.cycle('aspect', -1), right: () => display.cycle('aspect', 1), act: () => display.cycle('aspect', 1) },
    { label: 'FULLSCREEN', value: () => onoff(display.isFS()), act: () => display.toggleFS(), gesture: true },
    { label: 'INSTALL APP', value: () => display.installLabel().toUpperCase(), act: () => display.install(), gesture: true },
    { label: 'DIFFICULTY', ...cyc('diff', ['easy', 'normal', 'hard'], ['EASY', 'NORMAL', 'HARD']) },
    { label: 'CONTINUES', ...cyc('cont', [3, 5, 99], ['3', '5', 'FREE PLAY']) },
    { label: 'SCREEN SHAKE', value: () => onoff(st.shake), act: () => { st.shake = !st.shake; writeSave(); applySettings(); }, left: () => { st.shake = !st.shake; writeSave(); applySettings(); }, right: () => { st.shake = !st.shake; writeSave(); applySettings(); } },
    { label: 'TOUCH BUTTONS', ...cyc('touch', ['auto', 'on', 'off'], ['AUTO', 'ON', 'OFF']) },
    { label: 'RESET SAVE', value: () => (game.confirmReset ? 'SURE? OK AGAIN' : ''), act: () => { if (game.confirmReset) { save.hi = []; save.best = 0; writeSave(); game.confirmReset = false; game.toast('Save data cleared'); } else game.confirmReset = true; } },
    { label: 'BACK', act: back },
  ], { back, w: 260 });
}
let prevAspect = null;
function setRes(d) {
  const before = display.settings.res; display.cycle('res', d); const now = display.settings.res;
  if (now === 'retro' && before !== 'retro') { prevAspect = display.settings.aspect; display.set('aspect', '4:3'); }
  else if (before === 'retro' && now !== 'retro' && prevAspect) { display.set('aspect', prevAspect); prevAspect = null; }
}
function applySettings() {
  const st = save.settings; W.shakeOn = st.shake; W.diff = DIFF[st.diff] || DIFF.normal;
  document.documentElement.dataset.touchui = st.touch;
}
function helpMenu(back) {
  return Menu('HOW TO PLAY', [{ label: 'BACK', act: back }], { back, help: true, w: Math.min(G.VW - 16, 400) });
}
function titleMenu() {
  return Menu(null, [
    { label: '1 PLAYER', act: () => toSelect(1) },
    { label: '2 PLAYERS', act: () => toSelect(2) },
    { label: 'HOW TO PLAY', act: () => { game.overlay = helpMenu(() => { game.overlay = null; }); } },
    { label: 'HIGH SCORES', act: () => { game.scene = 'scores'; game.t = 0; } },
    { label: 'SETTINGS', act: () => { game.overlay = settingsMenu(() => { game.overlay = null; }); } },
  ], { w: 140, y0: 126, plain: true });
}
function pauseMenu() {
  return Menu('PAUSED', [
    { label: 'RESUME', act: () => resume() },
    { label: 'SETTINGS', act: () => { game.overlay = settingsMenu(() => { game.overlay = pauseMenu(); }); } },
    { label: 'HOW TO PLAY', act: () => { game.overlay = helpMenu(() => { game.overlay = pauseMenu(); }); } },
    { label: 'QUIT TO TITLE', act: () => { game.overlay = null; toTitle(); } },
  ], { back: () => resume(), w: 170 });
}
function resume() { game.overlay = null; sfx('select'); }
function activeMenu() { return game.overlay || (game.scene === 'title' ? game.menu : null); }

function menuInput(m, intents) {
  for (const it of intents) {
    const item = m.items[m.sel];
    if (it.a === 'up') { m.sel = (m.sel - 1 + m.items.length) % m.items.length; sfx('blip', { vol: 0.5 }); game.confirmReset = false; }
    else if (it.a === 'down') { m.sel = (m.sel + 1) % m.items.length; sfx('blip', { vol: 0.5 }); game.confirmReset = false; }
    else if (it.a === 'left' && item.left) item.left();
    else if (it.a === 'right' && item.right) item.right();
    else if (it.a === 'ok') { if (game.skipOk) { game.skipOk = false; continue; } if (item.act) { sfx('select'); item.act(false); } else if (item.right) item.right(); return; }
    else if (it.a === 'back' && m.back) { sfx('blip'); m.back(); return; }
  }
}
function drawMenu(m) {
  const VW = G.VW, VH = G.VH;
  if (m.help) return drawHelp(m);
  const lh = 13, w = m.w || 200, h = (m.title ? 22 : 8) + m.items.length * lh + 6;
  const x = Math.round((VW - w) / 2), y = m.y0 ?? Math.round((VH - h) / 2);
  if (!m.plain) { rect(0, 0, VW, VH, '#05060c', 0.55); panel(x, y, w, h); }
  if (m.title) text(m.title, VW / 2, y + 7, { col: '#ffe84a', align: 'center' });
  m.rects = [];
  m.items.forEach((it, i) => {
    const iy = y + (m.title ? 22 : 8) + i * lh, on = i === m.sel;
    m.rects.push([x, iy - 3, w, lh]);
    if (on) { rect(x + 4, iy - 3, w - 8, lh - 1, m.plain ? '#1a2450' : '#3a4c92', m.plain ? 0.8 : 1); text('>', x + 8, iy, { col: '#ffe84a' }); }
    const v = it.value ? it.value() : null;
    if (v !== null && v !== undefined) { text(it.label, x + 20, iy, { col: on ? '#ffffff' : '#c8d4f0' }); text(v, x + w - 10, iy, { col: on ? '#ffe84a' : '#8ad8ff', align: 'right' }); }
    else text(it.label, m.plain ? VW / 2 : x + 20, iy, { col: on ? '#ffffff' : '#c8d4f0', align: m.plain ? 'center' : 'left' });
  });
}
function drawHelp(m) {
  const VW = G.VW, VH = G.VH, w = m.w, h = Math.min(VH - 12, 210), x = Math.round((VW - w) / 2), y = Math.round((VH - h) / 2);
  rect(0, 0, VW, VH, '#05060c', 0.6); panel(x, y, w, h);
  text('HOW TO PLAY', VW / 2, y + 6, { col: '#ffe84a', align: 'center' });
  const L = [
    ['', 'KEYS', 'PAD', 'TOUCH'],
    ['MOVE', 'WASD/ARROWS', 'STICK/DPAD', 'L-THUMB'],
    ['ATTACK', 'J (Z)', 'X / []', 'HIT'],
    ['JUMP', 'K/SPACE (X)', 'A / X', 'JUMP'],
    ['SPECIAL', 'L (C)', 'Y / /\\', 'SP'],
    ['GRAB/PICK', 'H (V)', 'B / O', 'GRAB'],
    ['RUN', '2-TAP / SHIFT', 'RB / 2-TAP', '2-FLICK'],
    ['BACK ATK', 'ATK+JUMP', 'ATK+JUMP', 'HIT+JUMP'],
    ['PAUSE', 'ENTER/ESC', 'START', 'II'],
  ];
  const cw = (w - 16) / 4;
  L.forEach((r, i) => r.forEach((c, j) => text(c, x + 8 + j * cw, y + 20 + i * 11, { col: i === 0 ? '#8ad8ff' : j === 0 ? '#ffe84a' : '#ffffff', scale: 1 })));
  const tips = ['RUN + ATTACK = DASH ATTACK.  JUMP + ATTACK = KICK.', 'WALK INTO A PATIENT TO GRAB. ATTACK = KNEE,', 'JUMP/GRAB = THROW. GRAB ON A WEAPON PICKS IT UP.', 'SP COSTS A LITTLE HEALTH. FULL METER = CODE BLUE!', '2P ON ONE KEYBOARD: P1 WASD+HJKL, P2 ARROWS+,./M'];
  tips.forEach((s, i) => text(s, x + 8, y + 124 + i * 11, { col: '#c8d4f0', scale: 1 }));
  m.rects = [[x, y + h - 18, w, 16]];
  text('> BACK', VW / 2, y + h - 14, { col: '#ffe84a', align: 'center' });
}
function hitMenu(m, lx, ly) {
  for (let i = 0; i < m.rects.length; i++) { const r = m.rects[i]; if (lx >= r[0] && lx <= r[0] + r[2] && ly >= r[1] && ly <= r[1] + r[3]) return i; }
  return -1;
}

// ------------------------------------------------------------------ scenes
function toTitle() {
  game.scene = 'title'; game.t = 0; game.menu = titleMenu(); W.heroes = []; W.enemies = []; W.boss = null; W.shots = []; W.fx = []; game.overlay = null;
  C.split = false; buildLevel(LEVEL1); W.camX = 0; playMusic('title'); setScene('menu');
}
function setScene(kind) { document.documentElement.dataset.scene = kind; }
function toSelect(mode) {
  game.scene = 'select'; game.mode = mode; game.t = 0; setScene('menu');
  const d = game.lastDev || 'kb';
  C.split = mode === 2;
  const dev1 = mode === 2 ? (d === 'kb' || d === 'kb2' ? 'kb1' : d) : null;
  game.sel = { p: [{ dev: dev1, cur: 0, locked: false }], wait: mode === 2 };
  playMusic('select');
}
function selectUpdate(dt) {
  const S = game.sel;
  for (const d of Object.values(C.devs)) {
    // which player does this device drive?
    let pi = S.p.findIndex((p) => p.dev === d.id || (!p.dev && game.mode === 1));
    if (pi < 0 && game.mode === 2 && S.p.length < 2 && (d.prs.atk || d.prs.start || d.prs.jmp) && d.id !== S.p[0].dev) {
      if (d.id === 'kb') continue;
      S.p.push({ dev: d.id, cur: (S.p[0].cur + 1) % 4, locked: false }); sfx('powerup'); continue;
    }
    if (pi < 0) continue;
    const P = S.p[pi];
    if (!P.locked) {
      if (d.menuEdge === 'left' || d.menuEdge === 'up') { P.cur = (P.cur + 3) % 4; sfx('blip', { vol: 0.5 }); }
      if (d.menuEdge === 'right' || d.menuEdge === 'down') { P.cur = (P.cur + 1) % 4; sfx('blip', { vol: 0.5 }); }
      if (d.prs.atk || d.prs.jmp || d.prs.start) { const other = S.p.find((q) => q !== P && q.locked && q.cur === P.cur); if (other) { sfx('hurt'); game.toast('Already picked: choose another nurse'); } else { P.locked = true; sfx('powerup'); } }
      if (d.prs.grab && pi === 0) { toTitle(); return; }
    } else if (d.prs.grab) { P.locked = false; sfx('blip'); }
    else if (d.prs.start && game.mode === 2 && S.p.length === 1 && pi === 0) { startGame(); return; }  // P1 can go solo
  }
  for (const c of C.lastCodes || []) if (c === 'Escape') { toTitle(); return; }
  if (S.p.every((p) => p.locked) && (game.mode === 1 || S.p.length === 2)) { S.go = (S.go || 0) + dt; if (S.go > 0.6) startGame(); }
}
function selectTap(lx, ly) {
  const S = game.sel, P = S.p[0], cards = game.cardRects || [];
  for (let i = 0; i < cards.length; i++) {
    const r = cards[i]; if (lx < r[0] || lx > r[0] + r[2] || ly < r[1] || ly > r[1] + r[3]) continue;
    if (P.cur === i && !P.locked) { P.locked = true; sfx('powerup'); } else if (!P.locked) { P.cur = i; sfx('blip'); }
    return;
  }
  if (game.backRect && lx < game.backRect[0] + game.backRect[2] && ly > game.backRect[1] && ly < game.backRect[1] + game.backRect[3] && lx > game.backRect[0]) { if (P.locked) P.locked = false; else toTitle(); }
}
function startGame() {
  const S = game.sel;
  W.heroes = []; W.enemies = []; W.boss = null; W.shots = []; W.fx = []; W.stats = { kos: 0, time: 0 }; W.clock = 7 * 60; W.t = 0; W.vc = 0;
  applySettings(); buildLevel(LEVEL1); Director.reset(); W.camX = 0; W.camMin = 0;
  S.p.forEach((p, i) => {
    const h = new Hero(HERO_ORDER[p.cur], i, 56 + i * 22, 126 + i * 2);
    h.devs = game.mode === 2 ? [p.dev] : null; h.set('enter'); h.face = 1;
    W.heroes.push(h);
  });
  W.elevs.A.target = 1; W.elevs.A.t = 0; W.elevs.A.light = 1.2; sfx('ding');
  game.scene = 'intro'; game.t = 0; game.creditsUsed = 0; save.plays++; writeSave(); setScene('game');
  const zj = +Q.get('zone');
  if (zj > 0 && zj < W.lv.zones.length) {
    const z = W.lv.zones[zj]; W.zone = zj - 1; W.camX = W.camMin = Math.max(0, z.lock - 60); W.camMax = z.lock;
    W.heroes.forEach((h, i) => { h.x = z.at + 4 + i * 20; h.y = 172; h.set('idle'); }); game.t = 2.4;
  }
  playMusic('stage'); preloadMusic(['boss', 'clear']);
}
function dropIn(d) {  // a second player presses Start mid-game
  if (W.heroes.length >= 2 || game.scene !== 'play') return false;
  const p1 = W.heroes[0]; const used = p1.id;
  const id = HERO_ORDER.find((h) => h !== used);
  const lastP1 = game.lastP1 || 'kb';
  if (d.id === lastP1 || (d.id === 'kb' && lastP1 === 'kb')) return false;
  if (d.id === 'touch') return false;
  const h = new Hero(id, 1, W.camX + 60, 170); h.respawn(); h.devs = [d.id === 'kb' ? 'kb' : d.id];
  p1.devs = Object.keys(C.devs).filter((k) => k !== d.id && !(d.id === 'kb' && k.startsWith('kb')));
  W.heroes.push(h); game.mode = 2; sfx('powerup'); game.toast(`${h.d.name} clocks in! (2P)`);
  return true;
}
function playUpdate(dt) {
  // drop-in for a second player (Start on a device P1 isn't using), then pause
  if (W.heroes.length < 2) for (const d of Object.values(C.devs)) if (d.prs.start && d.id !== (game.lastP1 || 'kb') && dropIn(d)) { d.prs.start = false; break; }
  let pause = (C.lastCodes || []).some((c) => c === 'Escape' || c === 'Pause');
  for (const h of W.heroes) { const I = readPlayer(h); if (I.prs.start && h.st !== 'out') pause = true; }
  if (pause && !game.overlay) { game.overlay = pauseMenu(); sfx('select'); return; }
  if (W.stop > 0) { W.stop -= dt; for (const f of W.fx) f.t += dt * 0.25; return; }
  W.t += dt; W.stats.time += dt; W.clock += dt / 1.5;
  for (const h of W.heroes) {
    const I = Q.get('bot') && h.slot === 0 ? botInput(h) : readPlayer(h);
    if (Q.get('god')) { h.hp = h.maxHp; }
    h.update(dt, I);
    if (h.st === 'out') {
      if (h.continueT > 0 && game.continuesLeft() > 0) {
        h.continueT -= dt;
        if (I.prs.start || I.prs.atk || I.prs.jmp) { game.creditsUsed++; h.lives = 3; h.alive = true; h.score = h.score; h.respawn(); h.meter = 50; sfx('powerup'); game.toast(`${h.d.name}: back on shift!`); }
      } else h.continueT = 0;
    }
  }
  for (const e of W.enemies) e.update(dt);
  if (W.boss) W.boss.update(dt);
  Director.update(dt);
  updateWorld(dt);
  updateCamera(dt);
  if (W.cleared) { toTally(); return; }
  if (W.heroes.every((h) => h.st === 'out' && !(h.continueT > 0 && game.continuesLeft() > 0))) { toGameOver(); }
}
// test-only bot: walk to the nearest patient (or the boss / the GO arrow) and mash attack, sometimes grab or special
function botInput(h) {
  const o = { mx: 0, my: 0, held: {}, prs: {}, run: false };
  const foes = [...W.enemies.filter((e) => e.alive && e.st !== 'down' && e.x > W.camX - 10 && e.x < W.camX + G.VW + 10), ...(W.boss && W.boss.st !== 'defeat' ? [W.boss] : [])];
  if (!foes.length) { o.mx = 1; o.run = W.go > 0; return o; }
  foes.sort((a, b) => Math.abs(a.x - h.x) + Math.abs(a.y - h.y) - Math.abs(b.x - h.x) - Math.abs(b.y - h.y));
  const f = foes[0], side = h.x < f.x ? -1 : 1, gx = f.x + side * (f.isBoss ? 44 : 24), dx = gx - h.x, dy = f.y - h.y;
  o.mx = Math.abs(dx) > 5 ? Math.sign(dx) : 0; o.my = Math.abs(dy) > 3 ? Math.sign(dy) : 0;
  if (Math.abs(dx) < 14 && Math.abs(dy) < 8) { o.mx = 0; if (h.face !== -side) o.mx = -side * 0.3; o.prs.atk = (W.t * 60 | 0) % 7 === 0; if ((W.t * 60 | 0) % 400 === 0) o.prs.sp = true; }
  if (h.meter >= 100) o.prs.sp = o.held.jmp = true;
  return o;
}
function toTally() {
  game.scene = 'tally'; game.t = 0; playMusic('clear'); setScene('menu');
  for (const h of W.heroes) if (h.alive && h.st !== 'out') { h.set('win'); h.inv = 0; }
  const timeBonus = Math.max(0, Math.round((9 * 60 - W.clock) * 40));
  game.tally = W.heroes.map((h) => ({ h, rows: [['SCORE', h.score], [`TUCKED IN x${h.kos}`, h.kos * 100], [`COMBO x${h.maxCombo || 0}`, (h.maxCombo || 0) * 50], ['ON TIME', h.st === 'out' ? 0 : timeBonus]], shown: 0 }));
  for (const t of game.tally) t.total = t.rows.reduce((s, r, i) => s + (i ? r[1] : 0), t.rows[0][1]);
  save.best = Math.max(save.best, 1); writeSave();
}
function finishRun(cleared) {
  const entries = (game.tally ? game.tally.map((t) => ({ s: t.total, h: t.h.id })) : W.heroes.map((h) => ({ s: h.score, h: h.id })));
  game.newHi = false;
  for (const e of entries) {
    if (e.s <= 0) continue;
    const d = new Date(); const rec = { s: e.s, h: e.h, f: cleared ? 1 : 0, d: `${d.getMonth() + 1}/${d.getDate()}` };
    save.hi.push(rec); save.hi.sort((a, b) => b.s - a.s); save.hi = save.hi.slice(0, 5);
    if (save.hi.includes(rec)) game.newHi = true;
  }
  writeSave();
}
function toGameOver() { setScene('menu'); game.scene = 'gameover'; game.t = 0; stopMusic(); sfx('explosion'); finishRun(false); }

// ------------------------------------------------------------------ drawing
function drawWorld() {
  const c = G.ctx;
  const sx = W.shakeAmt > 0 ? Math.round((Math.random() - 0.5) * W.shakeAmt) : 0, sy = W.shakeAmt > 0 ? Math.round((Math.random() - 0.5) * W.shakeAmt) : 0;
  c.save(); c.translate(sx, sy);
  drawBackground();
  const list = [];
  for (const p of W.props) list.push({ y: p.y - 2, d: () => drawProp(p) });
  for (const it of W.items) list.push({ y: it.y - 1, d: () => drawItem(it) });
  for (const s of W.shots) list.push({ y: s.kind === 'puddle' ? 0 : s.y, d: () => drawShot(s) });
  const actors = [...W.heroes, ...W.enemies, ...(W.boss ? [W.boss] : [])];
  for (const a of actors) if (a.st !== 'out') a.drawShadow();
  for (const a of actors) list.push({ y: a.y + (a.st === 'held' ? 0.6 : 0), d: () => a.draw() });
  list.sort((a, b) => a.y - b.y);
  for (const o of list) o.d();
  for (const f of W.fx) drawFx(f);
  c.restore();
  if (W.flash > 0) rect(0, 0, G.VW, G.VH, W.flashCol, Math.min(0.75, W.flash * 0.8));
}
function drawTitle() {
  const VW = G.VW, VH = G.VH;
  W.camX = (game.t * 14) % (W.lv.width - VW - 10);
  drawBackground();
  rect(0, 0, VW, VH, '#0a1030', 0.55);
  const lw = (n) => sprSize(n)[0];
  const sc = Math.min(1, (VW - 12) / lw('logo2'));
  const bob = Math.round(Math.sin(game.t * 2) * 2);
  spr('logo1', VW / 2, 12 + bob, { ax: lw('logo1') / 2, scale: sc });
  spr('logo2', VW / 2, 42 + bob, { ax: lw('logo2') / 2, scale: sc });
  spr('logo3', VW / 2, 80 + bob, { ax: lw('logo3') / 2, scale: sc });
  // the four nurses and Tilly
  const xs = [26, 60, VW - 60, VW - 26];
  HERO_ORDER.forEach((id, i) => { const A = anim(id, 'idle'); frame(id, A.s + (Math.floor(game.t * 2 + i) % A.n), xs[i], 212, { flip: i > 1 }); });
  // Tilly cruises back and forth along the bottom, behind the menu
  const per = 14, ph = (game.t % per) / per, dir = ph < 0.5 ? 1 : -1, u = ph < 0.5 ? ph * 2 : (1 - ph) * 2;
  const T = anim('tilly', 'drive'); frame('tilly', T.s + (Math.floor(game.t * 8) % T.n), -70 + u * (VW + 140), 226, { flip: dir < 0 });
  if (!game.overlay) panel(VW / 2 - 76, 124, 152, 74, '#0a1030', '#3a4c92', 0.82);
  text(`HI ${String(save.hi[0] ? save.hi[0].s : 0).padStart(7, '0')}`, VW - 6, 4, { col: '#ffe84a', align: 'right' });
  if (!game.overlay) drawMenu(game.menu);
  text('ORIGINAL GAME FOR BILL W. 2026', VW / 2, VH - 9, { col: '#c8d4f0', align: 'center' });
}
function drawSelect() {
  const VW = G.VW, VH = G.VH, S = game.sel;
  W.camX = 600; drawBackground(); rect(0, 0, VW, VH, '#0a1030', 0.72);
  text('CHOOSE YOUR NURSE', VW / 2, 8, { col: '#ffe84a', align: 'center', scale: 1 });
  const cw = Math.min(92, Math.floor((VW - 16) / 4) - 4), ch = 172, x0 = Math.round((VW - (cw + 4) * 4 + 4) / 2), y0 = 22;
  game.cardRects = [];
  HERO_ORDER.forEach((id, i) => {
    const H = HEROES[id], x = x0 + i * (cw + 4), y = y0;
    const p1 = S.p[0] && S.p[0].cur === i, p2 = S.p[1] && S.p[1].cur === i;
    game.cardRects.push([x, y, cw, ch]);
    panel(x, y, cw, ch, p1 || p2 ? '#2a3a7a' : '#141c40', p1 && p2 ? '#ffffff' : p1 ? '#ffe84a' : p2 ? '#8ad8ff' : '#3a4c92');
    spr(`face_${id}`, x + cw / 2 - 18, y + 4);
    text(H.name, x + cw / 2, y + 42, { col: '#ffffff', align: 'center' });
    text(H.role.toUpperCase(), x + cw / 2, y + 52, { col: H.color, align: 'center' });
    const A = anim(id, (p1 && S.p[0].locked) || (p2 && S.p[1].locked) ? 'win' : 'idle');
    frame(id, A.s + (Math.floor(game.t * 3) % A.n), x + cw / 2, y + 122, {});
    ['POW', 'SPD', 'RCH', 'TUF'].forEach((lab, j) => {
      const yy = y + 128 + j * 9; text(lab, x + 4, yy, { col: '#c8d4f0', shadow: null });
      for (let k = 0; k < 5; k++) rect(x + 30 + k * Math.floor((cw - 34) / 5), yy + 1, Math.floor((cw - 34) / 5) - 1, 5, k < H.stats[j] ? H.color : '#2a2e4a');
    });
    if (p1) text(S.p[0].locked ? '1P OK!' : '1P', x + 4, y + ch - 10, { col: '#ffe84a' });
    if (p2) text(S.p[1].locked ? '2P OK!' : '2P', x + cw - 4, y + ch - 10, { col: '#8ad8ff', align: 'right' });
  });
  const P = S.p[0]; const H = HEROES[HERO_ORDER[P.cur]];
  text(`SPECIAL: ${H.special}`, VW / 2, y0 + ch + 6, { col: '#8ad8ff', align: 'center' });
  if (game.mode === 2 && S.p.length < 2 && Math.floor(game.t * 2) % 2) text('2P: PRESS ATTACK ON ANOTHER PAD OR ARROWS + , KEY', VW / 2, VH - 10, { col: '#ffffff', align: 'center', scale: 1 });
  else text(P.locked ? (game.mode === 2 && S.p.length < 2 ? 'START = PLAY SOLO' : 'GET READY!') : 'LEFT/RIGHT, ATTACK TO PICK. TAP A CARD TWICE.', VW / 2, VH - 10, { col: '#c8d4f0', align: 'center' });
  game.backRect = [2, 2, 40, 14]; text('< BACK', 4, 6, { col: '#8a94b4' });
}
function drawIntro() {
  const k = game.t;
  if (k < 2.6) {
    const VW = G.VW; const y = 84;
    rect(0, y - 6, VW, 44, '#0a1030', 0.75); rect(0, y - 6, VW, 1, '#ffe84a'); rect(0, y + 37, VW, 1, '#ffe84a');
    text(W.lv.name, VW / 2, y, { col: '#ffe84a', align: 'center', scale: 1 });
    text(W.lv.sub, VW / 2, y + 12, { col: '#ffffff', align: 'center' });
    if (k > 0.8) { const [w] = sprSize('w_ready'); spr('w_ready', VW / 2, y + 26, { ax: w / 2, ay: 0, scale: Math.min(0.62, (k - 0.8) * 3) }); }
  }
}
function drawTally() {
  const VW = G.VW, VH = G.VH;
  rect(0, 0, VW, VH, '#05060c', Math.min(0.6, game.t));
  const [w] = sprSize('w_clear_stage'); spr('w_clear_stage', VW / 2, 18, { ax: w / 2, scale: Math.min(1, (VW - 20) / w) });
  const n = game.tally.length, pw = Math.min(200, (VW - 20) / n - 6);
  game.tally.forEach((T, i) => {
    const x = Math.round(VW / 2 - (n * (pw + 6)) / 2 + i * (pw + 6)), y = 56;
    panel(x, y, pw, 118);
    spr(`face_${T.h.id}`, x + 4, y + 4); text(T.h.d.name, x + 44, y + 10, { col: T.h.slot ? '#8ad8ff' : '#ffe84a' });
    const reveal = Math.min(T.rows.length, Math.floor(game.t * 2));
    T.rows.forEach((r, j) => { if (j >= reveal) return; text(r[0], x + 6, y + 44 + j * 14, { col: '#c8d4f0' }); text(String(r[1]), x + pw - 6, y + 44 + j * 14, { col: '#ffffff', align: 'right' }); });
    if (reveal >= T.rows.length) text(`TOTAL ${T.total}`, x + pw / 2, y + 104, { col: '#ffe84a', align: 'center' });
  });
  if (game.t > 3) text(Math.floor(game.t * 2) % 2 ? 'PRESS ATTACK' : '', VW / 2, VH - 30, { col: '#ffffff', align: 'center' });
}
function drawTeaser() {
  const VW = G.VW, VH = G.VH;
  rect(0, 0, VW, VH, '#05060c', 0.85);
  text('NEXT SHIFT...', VW / 2, 50, { col: '#8ad8ff', align: 'center' });
  text('FLOOR 4: RADIOLOGY', VW / 2, 74, { col: '#ffe84a', align: 'center', scale: 1 });
  text('THINGS ARE ABOUT TO GET', VW / 2, 98, { col: '#ffffff', align: 'center' });
  text('X-TRA WEIRD.', VW / 2, 110, { col: '#ffffff', align: 'center' });
  text('COMING SOON!', VW / 2, 140, { col: '#ff8ac0', align: 'center' });
  if (game.newHi) text('NEW HIGH SCORE!', VW / 2, 166, { col: Math.floor(game.t * 6) % 2 ? '#ffe84a' : '#ff8a1e', align: 'center' });
  if (game.t > 1.5) text('PRESS ATTACK', VW / 2, VH - 24, { col: '#c8d4f0', align: 'center' });
}
function drawGameOver() {
  const VW = G.VW, VH = G.VH;
  rect(0, 0, VW, VH, '#05060c', Math.min(0.8, game.t));
  const [w] = sprSize('w_gameover'); spr('w_gameover', VW / 2, 70, { ax: w / 2, scale: Math.min(1, (VW - 20) / w) });
  text('EVEN HEROES NEED A BREAK.', VW / 2, 120, { col: '#ffffff', align: 'center' });
  if (game.newHi) text('NEW HIGH SCORE!', VW / 2, 140, { col: '#ffe84a', align: 'center' });
  if (game.t > 1.5) text('PRESS ATTACK', VW / 2, VH - 30, { col: '#c8d4f0', align: 'center' });
}
function drawScores() {
  const VW = G.VW, VH = G.VH;
  W.camX = 1200; drawBackground(); rect(0, 0, VW, VH, '#0a1030', 0.78);
  text('EMPLOYEES OF THE MONTH', VW / 2, 24, { col: '#ffe84a', align: 'center' });
  const L = save.hi.length ? save.hi : [];
  for (let i = 0; i < 5; i++) {
    const r = L[i], y = 50 + i * 24;
    text(`${i + 1}.`, VW / 2 - 120, y, { col: '#8ad8ff' });
    if (r) { spr(`face_${r.h}`, VW / 2 - 100, y - 10, { scale: 0.5 }); text(HEROES[r.h] ? HEROES[r.h].name : '?', VW / 2 - 76, y, { col: '#ffffff' }); text(String(r.s).padStart(7, '0'), VW / 2 + 70, y, { col: '#ffe84a', align: 'right' }); text(r.d || '', VW / 2 + 120, y, { col: '#8a94b4', align: 'right' }); }
    else text('-------', VW / 2 + 70, y, { col: '#3a4c92', align: 'right' });
  }
  text(`FLOORS CLEARED: ${save.best}   SHIFTS WORKED: ${save.plays}`, VW / 2, 178, { col: '#c8d4f0', align: 'center' });
  text('PRESS ATTACK', VW / 2, VH - 20, { col: '#ffffff', align: 'center' });
}

// ------------------------------------------------------------------ loop
let acc = 0, lastT = performance.now();
const DT = 1 / 60;
function step(dt) {
  pollControls(dt);
  for (const d of Object.values(C.devs)) if (d.any) { game.lastDev = d.id; if (game.scene === 'play' && W.heroes[0] && (!W.heroes[0].devs || W.heroes[0].devs.includes(d.id))) game.lastP1 = d.id; }
  if ((C.lastCodes || []).includes('Fullscreen')) display.toggleFS();
  game.t += dt;
  for (const t of game.toasts) t.t -= dt; game.toasts = game.toasts.filter((t) => t.t > 0);
  if (game.overlay) { menuInput(game.overlay, menuIntents()); if (game.scene !== 'play') return; else return; }
  const any = menuIntents().some((i) => i.a === 'ok');
  switch (game.scene) {
    case 'title': menuInput(game.menu, menuIntents()); break;
    case 'select': selectUpdate(dt); break;
    case 'intro': {
      W.t += dt; for (const h of W.heroes) h.update(dt, { mx: 0, my: 0, held: {}, prs: {} }); updateWorld(dt);
      if (game.t > 2.4) { game.scene = 'play'; for (const h of W.heroes) if (h.st === 'enter') h.set('idle'); }
      break;
    }
    case 'play': playUpdate(dt); break;
    case 'tally': W.t += dt; for (const h of W.heroes) h.t += dt; updateWorld(dt); if (game.t > 3 && any) { game.scene = 'teaser'; game.t = 0; finishRun(true); } break;
    case 'teaser': if (game.t > 1.5 && any) toTitle(); break;
    case 'gameover': if (game.t > 1.5 && any) { game.scene = 'scores'; game.t = 0; } break;
    case 'scores': if (game.t > 0.4 && (any || menuIntents().some((i) => i.a === 'back'))) toTitle(); break;
  }
}
function render() {
  const c = G.ctx; c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1;
  rect(0, 0, G.VW, G.VH, '#000');
  switch (game.scene) {
    case 'title': drawTitle(); break;
    case 'select': drawSelect(); break;
    case 'intro': case 'play': drawWorld(); drawHUD(game); if (game.scene === 'intro') drawIntro(); break;
    case 'tally': drawWorld(); drawTally(); break;
    case 'teaser': drawTeaser(); break;
    case 'gameover': drawWorld(); drawGameOver(); break;
    case 'scores': drawScores(); break;
  }
  if (game.overlay) drawMenu(game.overlay);
  if (game.scene !== 'play' && game.scene !== 'intro' && game.toasts.length) { const t = game.toasts[0]; const w = textW(t.s) + 16; panel((G.VW - w) / 2, G.VH - 40, w, 16, '#1a2450', '#8ad8ff'); text(t.s, G.VW / 2, G.VH - 36, { col: '#fff', align: 'center' }); }
  present();
  const clk = document.getElementById('clock');
  if (clk) { const m = Math.floor(W.clock), hh = Math.floor(m / 60) % 12 || 12; clk.textContent = `${hh}:${String(m % 60).padStart(2, '0')} ${Math.floor(m / 60) % 24 < 12 ? 'AM' : 'PM'}`; }
}
function frameLoop(now) {
  requestAnimationFrame(frameLoop);
  let el = Math.min(0.1, (now - lastT) / 1000); lastT = now;
  acc += el; let n = 0;
  while (acc >= DT && n < 6) { step(DT); acc -= DT; n++; }
  render();
}

// ------------------------------------------------------------------ boot
async function boot() {
  const bar = document.getElementById('loadbar');
  await initGfx((p) => { if (bar) bar.style.width = `${Math.round(p * 80)}%`; });
  display = createDisplay({ renderer: { setPixelRatio() {}, setSize() {} }, storageKey: 'nbd2.display', title: "Nick's Bad Day II", onChange: applyRes, onToast: (m) => game.toast(m) });
  window.__display = display;
  applyRes(display);
  initControls((m) => game.toast(m));
  applySettings();
  await initSound({ music: save.settings.music, sfx: save.settings.sfx });
  if (bar) bar.style.width = '100%';
  // HUD buttons
  document.getElementById('fsbtn').addEventListener('click', (e) => { e.stopPropagation(); display.toggleFS(); });
  document.getElementById('pausebtn').addEventListener('pointerdown', (e) => { e.preventDefault(); e.stopPropagation(); if (game.scene === 'play') { if (game.overlay) resume(); else { game.overlay = pauseMenu(); sfx('select'); } } });
  addEventListener('keydown', (e) => {
    if (e.code === 'Backquote') { display.toggleFS(); return; }
    const m = activeMenu();
    if (m && ['Enter', 'Space', 'KeyJ', 'KeyK', 'NumpadEnter'].includes(e.code)) { const it = m.items[m.sel]; if (it && it.gesture) { sfx('select'); it.act(true); game.skipOk = true; } }
  });
  // taps / clicks on canvas menus (run inside the gesture so fullscreen + install work)
  const view = G.view;
  const toLogical = (e) => { const r = view.getBoundingClientRect(); return [(e.clientX - r.left) / r.width * G.VW, (e.clientY - r.top) / r.height * G.VH]; };
  view.addEventListener('pointerup', (e) => {
    if (!audio.ready) return;
    const [lx, ly] = toLogical(e);
    const m = activeMenu();
    if (m) {
      const i = hitMenu(m, lx, ly);
      if (i >= 0) {
        const it = m.items[i];
        if (m.sel !== i && !('ontouchstart' in window) && e.pointerType === 'mouse') { m.sel = i; }
        m.sel = i;
        if (it.right && !it.act && lx > G.VW / 2) it.right(); else if (it.left && !it.act && lx <= G.VW / 2) it.left(); else if (it.act) { sfx('select'); it.act(true); }
      } else if (m.help && m.back) m.back();
      return;
    }
    if (game.scene === 'select') selectTap(lx, ly);
    else if (['teaser', 'gameover', 'scores'].includes(game.scene) && game.t > 1.2) { if (game.scene === 'teaser') toTitle(); else if (game.scene === 'gameover') { game.scene = 'scores'; game.t = 0; } else toTitle(); }
    else if (game.scene === 'tally' && game.t > 3) { game.scene = 'teaser'; game.t = 0; finishRun(true); }
  });
  view.addEventListener('pointermove', (e) => { const m = activeMenu(); if (!m || e.pointerType !== 'mouse') return; const [lx, ly] = toLogical(e); const i = hitMenu(m, lx, ly); if (i >= 0 && i !== m.sel) m.sel = i; });
  toTitle();
  loaded();
  requestAnimationFrame(frameLoop);
  // test hooks
  window.__nbd = { spawn, prop: (kind, dx = 40, dy = 0, drops = []) => { const h = W.heroes[0]; const p = makeProp(kind, (h ? h.x : W.camX + 200) + dx, Math.max(136, Math.min(212, (h ? h.y : 170) + dy)), drops); W.props.push(p); return W.props.length - 1; }, hitProp, rollLoot, drop: (k) => { const h = W.heroes[0]; return h && dropItem(k, h.x, h.y, false); }, game, W, G, C, save, startGame, toSelect, toTitle, Director, display };
  if (Q.get('autostart') || Q.get('zone')) { toSelect(1); game.sel.p[0].cur = Math.max(0, HERO_ORDER.indexOf(Q.get('hero') || 'nick')); startGame(); }
}
boot().catch((e) => { const t = document.getElementById('loadtxt'); if (t) t.textContent = 'Could not load: ' + e.message; console.error(e); });
