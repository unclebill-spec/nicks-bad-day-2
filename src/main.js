// Nick's Very Bad, Terrible Bad Day Part II: boot, the fixed-step loop, scenes (title, hero select, stage, tally,
// teaser, game over, high scores), pause / settings / how-to menus, saves, display presets and fullscreen / install.
// v0.4 flow: select -> [cutscene start] -> intro -> play -> [cutscene boss] -> Tilly -> tally -> [cutscene lunch] ->
// Breakroom Bonus -> bonus tally -> [cutscene next] -> Floor 4 Radiology (Lou mini-boss, [cutscene mri] -> MRI boss) ->
// tally -> [cutscene scoot] -> v0.9 SCOOTER RUN (Motorcart Marv) -> scooter tally -> [cutscene night] -> Night Shift -> tally -> [cutscene ending] -> THE END (v0.5). Scores, lives, continues and
// 2P carry from floor to floor. Cutscenes skip with any button / tap (auto-skipped with ?bot / ?nocut).
import { G, initGfx, resize, present, text, spr, rect, panel, frame, anim, textW, sprSize, frameRect, ellipse } from './gfx.js';
import { loaded, Q, audio } from '../kit/common.js';
import { createDisplay } from '../kit/display.js';
import { C, initControls, pollControls, readPlayer, menuIntents } from './controls.js';
import { initSound, sfx, playMusic, stopMusic, setVolumes, preloadMusic, S as SND } from './sound.js';
import { HEROES, HERO_ORDER, LEVEL1, LEVELS, DIFF } from './data.js';
import { dropItem } from './world.js';
import { W, buildLevel, drawBackground, updateWorld, updateCamera, drawProp, drawItem, drawShot, drawFx, offY, floatText, makeProp, hitProp, rollLoot, drawLighting, word } from './world.js';
import { Director, spawn } from './stage.js';
import { Hero, drawTeamBack, drawTeamFront, TIER } from './hero.js';
import { ALARM, drawStations, drawWetFloor, drawAlarmFront, maybeYeller, pullAlarm, stationFor, alarmAllowed } from './alarm.js';
import { drawHUD } from './hud.js';
import { makeCut, updateCut, drawCut } from './cutscene.js';
import { B as BONUS_STATE, buildBreakroom, startBonus, updateBonus, drawBonusHUD, bonusRows } from './bonus.js';
import { SC, SCOOT, startScooter, updateScooter, drawScooter, drawScooterHUD, scootRows, drawScootTally, scootBot, continueRider, scootSpawn } from './scooter.js';

// ------------------------------------------------------------------ save
const SAVE_KEY = 'nbd2.save';
const DEF = { hi: [], best: 0, plays: 0, settings: { music: 0.6, sfx: 0.8, diff: 'normal', cont: 3, shake: true, touch: 'auto', flash: 'full' } };
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
    { label: 'FLASHING', ...cyc('flash', ['full', 'reduced'], ['FULL', 'REDUCED']) },  // v0.6: photosensitivity (fire-alarm strobe + screen flashes)
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
  const st = save.settings; W.shakeOn = st.shake; W.diff = DIFF[st.diff] || DIFF.normal; W.reducedFlash = st.flash === 'reduced';
  document.documentElement.dataset.touchui = st.touch;
}
function helpMenu(back) {
  const m = Menu('HOW TO PLAY', [], { back, help: true, w: Math.min(G.VW - 16, 400), page: 0 });
  const flip = () => { m.page = (m.page + 1) % 2; sfx('blip', { vol: 0.5 }); };
  m.items = [{ label: 'PAGE', act: flip, left: flip, right: flip }, { label: 'BACK', act: back, left: flip, right: flip }];
  return m;
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
function drawHelp(m) {  // v0.7: two pages (controls, moves) sized to fit a sideways phone above the pause/clock row
  const VW = G.VW, VH = G.VH, w = m.w, h = Math.min(VH - 34, 190), x = Math.round((VW - w) / 2), y = 4, pg = m.page || 0;
  rect(0, 0, VW, VH, '#05060c', 0.6); panel(x, y, w, h);
  text(pg ? 'HOW TO PLAY: MOVES' : 'HOW TO PLAY: CONTROLS', VW / 2, y + 6, { col: '#ffe84a', align: 'center' });
  if (!pg) {
    const L = [
      ['', 'KEYS', 'PAD', 'TOUCH'],
      ['MOVE', 'WASD/ARROWS', 'STICK/DPAD', 'L-THUMB'],
      ['ATTACK', 'J (Z)', 'X / []', 'HIT'],
      ['JUMP', 'K/SPACE(X)', 'A / X', 'JUMP'],
      ['SPECIAL', 'L (C)', 'Y / /\\', 'SP'],
      ['GRAB', 'H (V)', 'B / O', 'GRAB'],
      ['RUN', '2TAP/SHIFT', 'RB/2TAP', '2-FLICK'],
      ['BACK ATK', 'ATK+JUMP', 'ATK+JUMP', 'HIT+JUMP'],
      ['PAUSE', 'ENTER/ESC', 'START', 'II'],
    ];
    const cw = (w - 16) / 4;
    L.forEach((r, i) => r.forEach((c, j) => text(c, x + 8 + j * cw, y + 20 + i * 11, { col: i === 0 ? '#8ad8ff' : j === 0 ? '#ffe84a' : '#ffffff' })));
    ['GRAB A PATIENT: FORWARD = TOSS, AWAY = SLAM.', 'P2 KEYS: ARROWS + , (ATK) . (JUMP) / (SP) M', '(GRAB). GAMEPADS: P1 + P2. TOUCH: P1.']
      .forEach((t, i) => text(t, x + 8, y + 124 + i * 10, { col: '#c8d4f0' }));
  } else {
    const T = [['RUN + ATK = DASH ATTACK. JUMP+ATK = KICK.', '#c8d4f0'], ['GRAB BUTTON NEXT TO A PATIENT, THEN:', '#ffe84a'],
      [' ATK = KNEE THEM (THE 3RD ONE TOSSES)', '#c8d4f0'], [' FORWARD (OR FWD+ATK) = TOSS FORWARD', '#8ae87a'], [' AWAY (OR AWAY+ATK) = BODY SLAM BEHIND', '#ff8a6a'],
      [' TOSSED / SLAMMED PATIENTS BOWL OTHERS!', '#c8d4f0'], ['GRAB AT A PROP = PICK UP, ATK = THROW IT.', '#c8d4f0'], ['GRAB AT A GURNEY = RIDE. AT A WEAPON = TAKE.', '#c8d4f0'],
      ['SP: 1/3 METER = ATIVAN JAB, FULL = DEFIB!', '#8ad8ff'], ['EMPTY METER: SP = SPECIAL (COSTS SOME HP).', '#c8d4f0'], ['2P: BOTH HOLD SP CLOSE = CHARGE NURSE!', '#c8d4f0'],
      ['KO THE FIRE ALARM YELLER BEFORE HE PULLS!', '#ff8a6a']];
    T.forEach(([t, col], i) => text(t, x + 8, y + 20 + i * 11, { col }));
  }
  const by = y + h - 15, half = Math.round(w / 2);
  m.rects = [[x, by - 2, half, 14], [x + half, by - 2, w - half, 14]];
  text(`${m.sel === 0 ? '>' : ' '} PAGE ${pg + 1}/2`, x + half / 2, by, { col: m.sel === 0 ? '#ffe84a' : '#c8d4f0', align: 'center' });
  text(`${m.sel === 1 ? '>' : ' '} BACK`, x + half + (w - half) / 2, by, { col: m.sel === 1 ? '#ffe84a' : '#c8d4f0', align: 'center' });
}
function hitMenu(m, lx, ly) {
  for (let i = 0; i < m.rects.length; i++) { const r = m.rects[i]; if (lx >= r[0] && lx <= r[0] + r[2] && ly >= r[1] && ly <= r[1] + r[3]) return i; }
  return -1;
}

// ------------------------------------------------------------------ scenes
// ---- v0.4 cutscenes
const noCuts = () => !!(Q.get('bot') || Q.get('nocut') || ((Q.get('autostart') || Q.get('zone') || Q.get('level')) && !Q.get('cuts')));  // test URLs skip them unless &cuts=1
function startCut(id, done) {
  game.cut = makeCut(id); game.cutDone = done; game.cutSkip = false; game.scene = 'cutscene'; game.t = 0; setScene('menu');
}
function anyButton() { return (C.lastCodes || []).length > 0 || Object.values(C.devs).some((d) => Object.values(d.prs).some(Boolean)); }
// ---- v0.4 breakroom bonus between Floor 3 and Floor 4
function goLunch() {
  buildBreakroom();
  const go = () => { startBonus(); game.scene = 'bonus'; game.t = 0; setScene('game'); playMusic('stage'); };
  if (noCuts()) go(); else startCut('lunch', go);
}
function toBonusTally() {
  game.scene = 'btally'; game.t = 0; setScene('menu'); playMusic('clear'); sfx('fanfare', { vol: 0.7 });
  for (const h of W.heroes) if (h.alive && h.st !== 'out') { h.set('win'); h.inv = 0; }
  game.btally = W.heroes.map((h) => {
    const r = bonusRows(h); h.score += r.total;
    return { h, ...r };
  });
}
function goNext() {  // after the breakroom: up to Floor 4
  const go = () => loadLevel(1);
  if (noCuts()) go(); else startCut('next', go);
}
// ---- v0.9 SCOOTER RUN between Radiology and the night shift (src/scooter.js)
function scootUI(on) {  // touch: the stick steers, HIT becomes SHOOT, GRAB / SP hide
  document.documentElement.dataset.mode = on ? 'scoot' : '';
  const b = document.getElementById('b_atk'); if (b) b.textContent = on ? 'SHOOT' : 'HIT';
  if (!on) W.scoot = false;
}
function enterScooter() { startScooter(game); game.scene = 'scoot'; game.t = 0; game.tally = null; setScene('game'); scootUI(true); playMusic('scooter'); preloadMusic(['clear', 'night']); }
function goScooter() { if (noCuts()) enterScooter(); else startCut('scoot', enterScooter); }
function scootPlay(dt) {
  let pause = (C.lastCodes || []).some((c) => c === 'Escape' || c === 'Pause');
  const inputs = new Map();
  for (const h of W.heroes) { const I = Q.get('bot') && h.slot === 0 ? scootBot(h) : readPlayer(h); inputs.set(h, I); if (I.prs.start && h.st !== 'out' && !Q.get('bot')) pause = true; }
  if (pause && !game.overlay) { game.overlay = pauseMenu(); sfx('select'); return; }
  SC.god = !!Q.get('god');
  for (const h of W.heroes) {
    if (h.st !== 'out') continue;
    const I = inputs.get(h);
    if (h.continueT > 0 && game.continuesLeft() > 0) {
      h.continueT -= dt;
      if (I.prs.start || I.prs.atk || I.prs.jmp) { game.creditsUsed++; continueRider(h); sfx('powerup'); game.toast(`${h.d.name}: back on the scooter!`); }
    } else h.continueT = 0;
  }
  if (updateScooter(dt, inputs)) { toScootTally(); return; }
  if (W.heroes.every((h) => h.st === 'out' && !(h.continueT > 0 && game.continuesLeft() > 0))) { scootUI(false); W.scootOver = true; toGameOver(); }
}
function toScootTally() {
  game.scene = 'stally'; game.t = 0; setScene('menu'); scootUI(false); W.scootOver = true; playMusic('clear'); sfx('fanfare', { vol: 0.7 });
  game.stally = W.heroes.map((h) => { const r = scootRows(h); h.score += r.total; return { h, ...r }; });
}
function goNight() { W.scootOver = false; const go = () => loadLevel(2); if (noCuts()) go(); else startCut('night', go); }
// v0.5: after a floor's tally. Floor 4 -> night shift -> the ending.
function afterTally() {
  const i = W.lv.id;
  if (i === 1) return goLunch();
  if (i === 2) return goScooter();  // v0.9: Radiology -> the Scooter Run -> the night shift
  finishRun(true); save.best = Math.max(save.best, 3); writeSave();
  const go = () => { game.scene = 'ending'; game.t = 0; setScene('menu'); playMusic('clear'); };
  if (noCuts()) go(); else startCut('ending', go);
}
// v0.5: put the team on floor idx (0-based) with everything they've earned: score, lives, meter, continues used, 2P
function loadLevel(idx, zone = 0) {
  const lv = LEVELS[idx];
  W.enemies = []; W.boss = null; W.shots = []; W.fx = []; W.items = []; W.decor = []; W.t = 0; W.finalT = 0; W.vc = 0; W.bgHook = null; W.team = null;
  W.forceYeller = !!Q.get('yeller'); W.noAlarm = !!Q.get('noalarm'); W.scoot = false; W.scootOver = false; scootUI(false);
  buildLevel(lv); Director.reset(); W.camX = 0; W.camMin = 0; W.clock = lv.clock || 7 * 60; W.stats.time = 0;
  if (idx === 0) W.hallBg = W.bg; else if (idx === 1) W.radBg = W.bg; else W.nightBg = W.bg;
  W.heroes.forEach((h, i) => {
    h.kos = 0; h.maxCombo = 0; h.combo = 0; h.weapon = null; h.carry = null; h.held = null; h.grabber = null; h.ride = null; h.z = 0; h.vx = h.vy = h.vz = 0; h.inv = 0;
    if (h.st === 'out') { if (game.continuesLeft() > 0) h.continueT = 10; h.x = 56 + i * 22; return; }  // a KO'd partner can still continue here
    h.hp = h.maxHp; h.x = 56 + i * 22; h.y = 126 + i * 2; h.set('enter'); h.face = 1;
  });
  W.elevs.A.target = 1; W.elevs.A.t = 0; W.elevs.A.light = 1.2; sfx('ding');
  game.scene = 'intro'; game.t = 0; game.tally = null; setScene('game');
  if (zone > 0 && zone < lv.zones.length) {
    const z = lv.zones[zone]; W.zone = zone - 1; W.camX = W.camMin = Math.max(0, z.lock - 60); W.camMax = z.lock;
    W.heroes.forEach((h, i) => { if (h.st === 'out') return; h.carry = null; h.x = z.at + 4 + i * 20; h.y = 172; h.set('idle'); }); game.t = 2.4;
  }
  if (lv.lightsOut) { W.dark = 0; W.lightsOutT = zone > 0 ? 9 : 0; if (zone > 0) W.dark = lv.dark; }
  playMusic(lv.music || 'stage'); preloadMusic([lv.bossMusic || 'boss', 'clear']);
}
// night shift: the lights flicker and die in the intro, and come back on when the last patient is tucked in
function nightLights(dt) {
  const lv = W.lv; if (!lv.lightsOut) return;
  if (W.finalT) { if (W.finalT < 0.05) { word('w_power', W.camX + G.VW / 2, 180, 60); sfx('powerup'); sfx('click'); } W.dark = Math.max(0.12, lv.dark * (1 - W.finalT / 1.2)); return; }
  if (W.lightsOutT === undefined || W.lightsOutT > 5) return;
  const t0 = W.lightsOutT; W.lightsOutT += dt; const t = W.lightsOutT;
  if (t < 0.9) W.dark = 0;
  else if (t < 1.6) W.dark = Math.floor(t * 14) % 3 === 0 ? 0 : lv.dark * 0.6;  // flicker...
  else { if (t0 < 1.6) { sfx('lightsout'); word('w_lightsout', W.camX + G.VW / 2, 176, 70); floatText('Uh oh.', W.heroes[0] ? W.heroes[0].x : W.camX + 100, 172, 70, '#ffffff'); } W.dark = lv.dark; }
  if (t > 0.9 && t0 <= 0.9) sfx('powerdown', { vol: 0.6 });
}
function toTitle() {
  W.bgHook = null; W.team = null; W.scootOver = false; scootUI(false);
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
      S.p.push({ dev: d.id, cur: (S.p[0].cur + 1) % HERO_ORDER.length, locked: false }); sfx('powerup'); continue;
    }
    if (pi < 0) continue;
    const P = S.p[pi];
    if (!P.locked) {
      if (d.menuEdge === 'left' || d.menuEdge === 'up') { P.cur = (P.cur + HERO_ORDER.length - 1) % HERO_ORDER.length; sfx('blip', { vol: 0.5 }); }
      if (d.menuEdge === 'right' || d.menuEdge === 'down') { P.cur = (P.cur + 1) % HERO_ORDER.length; sfx('blip', { vol: 0.5 }); }
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
  W.heroes = []; W.stats = { kos: 0, time: 0 }; W.t = 0;
  applySettings();
  W.onBossCut = (go) => { if (noCuts()) return go(); startCut(W.lv.cutBoss || 'boss', () => { game.scene = 'play'; game.t = 0; setScene('game'); go(); }); };
  S.p.forEach((p, i) => {
    const h = new Hero(HERO_ORDER[p.cur], i, 56 + i * 22, 126 + i * 2);
    h.devs = game.mode === 2 ? [p.dev] : null;
    W.heroes.push(h);
  });
  game.creditsUsed = 0; save.plays++; writeSave();
  const li = Math.max(0, Math.min(LEVELS.length - 1, (+Q.get('level') || 1) - 1)), zj = +Q.get('zone') || 0;
  loadLevel(li, zj);
  if (!zj && !li && !noCuts()) startCut('start', () => { game.scene = 'intro'; game.t = 0; setScene('game'); });
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
  if (W.stop > 0) {  // hit-stop: freeze the action, but buffer button presses so none are lost
    W.stop -= dt; for (const f of W.fx) f.t += dt * 0.25;
    for (const h of W.heroes) { const I = readPlayer(h); for (const k in I.prs) if (I.prs[k]) (h.pend || (h.pend = {}))[k] = true; }
    return;
  }
  W.t += dt; W.stats.time += dt; W.clock += dt / 1.5; nightLights(dt);
  for (const h of W.heroes) {
    const I = Q.get('bot') && h.slot === 0 ? botInput(h) : readPlayer(h);
    if (h.pend) { for (const k in h.pend) I.prs[k] = true; h.pend = null; }
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
  const f = foes[0], off = f.isMRI ? f.w / 2 + 6 : f.isBoss ? f.w / 2 + 18 : 24;
  let side = f.isMRI ? -1 : h.x < f.x ? -1 : 1;
  if (!f.isMRI && (f.x + side * off < W.camX + 14 || f.x + side * off > W.camX + G.VW - 14)) side = -side;  // pinned at the screen edge: go round
  const crossing = !f.isMRI && Math.sign(h.x - f.x) !== side && Math.abs(h.x - f.x) < off;  // step out of his lane to get past
  const gx = f.x + side * off, dx = gx - h.x, dy = f.isMRI ? 0 : (crossing ? f.y + (f.y > 176 ? -24 : 24) : f.y) - h.y;
  o.mx = Math.abs(dx) > 5 ? Math.sign(dx) : 0; o.my = Math.abs(dy) > 3 ? Math.sign(dy) : 0;
  if (Math.abs(dx) < 14 && Math.abs(dy) < 8) { o.mx = 0; if (h.face !== -side) o.mx = -side * 0.3; o.prs.atk = (W.t * 60 | 0) % 7 === 0; if ((W.t * 60 | 0) % 400 === 0) o.prs.sp = true; }
  if (h.meter >= 100) o.prs.sp = o.held.jmp = true;
  return o;
}
function toTally() {
  game.scene = 'tally'; game.t = 0; playMusic('clear'); setScene('menu');
  for (const h of W.heroes) if (h.alive && h.st !== 'out') { h.set('win'); h.inv = 0; }
  const timeBonus = Math.max(0, Math.round(((W.lv.clock || 7 * 60) + 120 - W.clock) * 40));
  game.tally = W.heroes.map((h) => ({ h, score0: h.score, rows: [['SCORE', h.score], [`TUCKED IN x${h.kos}`, h.kos * 100], [`COMBO x${h.maxCombo || 0}`, (h.maxCombo || 0) * 50], ['ON TIME', h.st === 'out' ? 0 : timeBonus]], shown: 0 }));
  for (const t of game.tally) { t.quote = t.h.say ? t.h.say('clear', true) : null; t.h.sayS = null; }  // v0.8: heroes with lines (Nate) sign off on the card
  for (const t of game.tally) { t.total = t.rows.reduce((s, r, i) => s + (i ? r[1] : 0), t.rows[0][1]); t.h.score = t.total; }  // the bonus carries to the next floor
  save.best = Math.max(save.best, W.lv.id || 1); writeSave();
}
function finishRun(cleared) {
  const entries = W.heroes.map((h) => ({ s: h.score, h: h.id }));
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
  drawStations(G.VH - 224); drawWetFloor(G.VH - 224);  // v0.6 fire-alarm pull stations + wet-floor sheen
  drawTeamBack();
  const list = [];
  for (const p of W.props) list.push({ y: p.y - 2, d: () => drawProp(p) });
  for (const it of W.items) list.push({ y: it.y - 1, d: () => drawItem(it) });
  for (const s of W.shots) list.push({ y: s.kind === 'puddle' ? 0 : s.y, d: () => drawShot(s) });
  const actors = [...W.heroes, ...W.enemies, ...(W.boss ? [W.boss] : [])];
  for (const a of actors) if (a.st !== 'out') a.drawShadow();
  for (const a of actors) list.push({ y: a.y + (a.st === 'held' ? 0.6 : 0), d: () => a.draw() });
  for (const a of W.decor || []) list.push({ y: a.y, d: () => a.draw() });  // a beaten mini-boss napping on the floor
  list.sort((a, b) => a.y - b.y);
  for (const o of list) o.d();
  if (W.dark > 0.01) { drawLighting(); drawEyes(); }
  for (const f of W.fx) drawFx(f);
  // gurney hint: RIDE! over a gurney a nurse is standing next to
  for (const h of W.heroes) { if (!h.canAct()) continue; const g = h.nearGurney(); if (g && Math.floor(W.t * 3) % 2) text('RIDE!', g.x - W.camX, g.y + offY() - 44, { col: '#8ad8ff', align: 'center' }); }
  // v0.6 lift hint: PICK UP over the prop a nurse would lift with GRAB
  for (const h of W.heroes) {  // v0.7: while holding a patient, show which way tosses and which way slams (first few grabs each floor)
    if (!h.held || (h.st !== 'grab' && h.st !== 'knee') || (W.stats.grabs || 0) > 4) continue;
    const X = h.x - W.camX, Y = h.y + offY() - 74, L = h.face > 0 ? '<SLAM' : '<TOSS', R = h.face > 0 ? 'TOSS>' : 'SLAM>';
    rect(X - 46, Y - 2, 92, 11, '#1a1020', 0.75); text(L, X - 3, Y, { col: L.includes('TOSS') ? '#8ae87a' : '#ff8a6a', align: 'right' }); text(R, X + 3, Y, { col: R.includes('TOSS') ? '#8ae87a' : '#ff8a6a' });
  }
  for (const h of W.heroes) { if (h.carry || grabContext(h) !== 'PICK UP') continue; const p = h.liftTarget(); if (p && Math.floor(W.t * 3) % 2) text('PICK UP', p.x - W.camX, p.y + offY() - (p.def.h || 24) - 12, { col: '#8ae87a', align: 'center' }); }
  for (const h of W.heroes) h.drawSay();  // v0.8 speech bubbles on top of everything (and of the dark)
  c.restore();
  drawAlarmFront(W.reducedFlash);
  if (W.flash > 0) rect(0, 0, G.VW, G.VH, W.flashCol, Math.min(W.reducedFlash ? 0.22 : 0.75, W.flash * (W.reducedFlash ? 0.3 : 0.8)));
  drawTeamFront();
}
// v0.5 light sources that move: nurses' flashlights on the night shift (a little glow around them on Radiology), the MRI
W.lightHook = (L) => {
  if (W.boss && W.boss.light) W.boss.light(L);
  for (const h of W.heroes) {
    if (!h.alive || h.st === 'out') continue;
    const Y = h.y - h.z - 30;
    if (W.lv.flashlight) {
      L.push({ cone: true, x: h.x + h.face * 6, y: Y, dir: h.face, len: 124, half: 0.34 });
      L.push({ x: h.x + h.face * 74, y: h.y, r: 40, ry: 11, col: '#fff2b0', a: 0.55, floor: true });
      L.push({ x: h.x, y: Y + 4, r: 24, col: '#fff2b0', a: 0.55 });
    } else L.push({ x: h.x, y: Y + 6, r: 30, a: 0.45 });
  }
};
// in the dark, patients' eyes glow (night shift): two little dots that blink now and then
function drawEyes() {
  if (W.lv.flashlight) for (const h of W.heroes) { if (!h.alive || h.st === 'out') continue; const X = Math.round(h.x - W.camX + h.face * 7), Y = Math.round(h.y + offY() - h.z - 30); rect(X - (h.face < 0 ? 5 : 0), Y, 5, 3, '#2a2e3a'); rect(h.face > 0 ? X + 5 : X - 6, Y, 1, 3, '#fff6c8'); }
  if (W.dark < 0.5) return;
  for (const e of W.enemies) {
    if (!e.alive || ['dead', 'down', 'fall', 'sleep'].includes(e.st) || e.isThief) continue;
    const [n, i] = e.pose ? e.pose() : ['idle', 0], hd = e.handOf(n, i);
    if (!hd || hd.length < 6 || ((W.t + e.x * 0.01) % 3.2) < 0.12) continue;
    const X = Math.round(e.x - W.camX + hd[4] * (e.face < 0 ? -1 : 1)), Y = Math.round(e.y + offY() - e.z + hd[5]);
    rect(X - 1 + (e.face < 0 ? -2 : 1), Y, 2, 1, '#fff6a0'); rect(X + 3 * (e.face < 0 ? -1 : 1) + (e.face < 0 ? -2 : 1), Y, 2, 1, '#fff6a0');
  }
}
// touch: the GRAB button turns into RIDE next to a gurney
let rideLabel = 'GRAB';
// the touch GRAB button is context-sensitive: RIDE next to a gurney, PICK UP at a liftable prop, THROW while carrying one
function grabContext(h) {
  if (!h || !(game.scene === 'play' || game.scene === 'bonus')) return 'GRAB';
  if (h.carry) return 'THROW';
  if (h.held && (h.st === 'grab' || h.st === 'knee')) return 'TOSS';  // v0.7: GRAB again tosses (AWAY + GRAB slams)
  if (!h.canAct()) return 'GRAB';
  if (h.grabTarget(24) && !h.weapon) return 'GRAB';
  if (h.nearGurney()) return 'RIDE';
  return h.canLift() ? 'PICK UP' : 'GRAB';
}
let spLabel = 'SP';
function updateSpLabel() {  // v0.6: the touch SP button shows what SP will do right now
  const h = W.heroes[0], play = game.scene === 'play' || game.scene === 'bonus';
  const want = !play || !h ? 'SP' : h.meter >= 100 ? 'CODE BLUE' : h.meter >= TIER - 0.01 ? 'ATIVAN' : 'SP';
  if (want === spLabel) return; spLabel = want;
  const b = document.getElementById('b_sp'); if (b) { b.textContent = want === 'CODE BLUE' ? 'CODE\nBLUE' : want; b.dataset.ctx = want; b.classList.toggle('ctx', want !== 'SP'); b.classList.toggle('full', want === 'CODE BLUE'); }
}
function updateRideLabel() {
  updateSpLabel();
  const want = grabContext(W.heroes[0]);
  if (want === rideLabel) return; rideLabel = want;
  const b = document.getElementById('b_grab'); if (b) { b.textContent = want === 'PICK UP' ? 'PICK\nUP' : want; b.classList.toggle('ctx', want !== 'GRAB'); b.classList.toggle('thr', want === 'THROW' || want === 'TOSS'); b.dataset.ctx = want; }
}
function drawBonusTally() {
  const VW = G.VW, VH = G.VH;
  rect(0, 0, VW, VH, '#05060c', Math.min(0.6, game.t));
  const [w] = sprSize('w_bonus'); spr('w_bonus', VW / 2, 16, { ax: w / 2, scale: Math.min(1, (VW - 20) / w) });
  text(`THIEVES STOPPED ${BONUS_STATE.stopped}   SNACKS LOST ${BONUS_STATE.escaped}`, VW / 2, 44, { col: '#c8d4f0', align: 'center' });
  const n = game.btally.length, pw = Math.min(210, (VW - 20) / n - 6);
  game.btally.forEach((T, i) => {
    const x = Math.round(VW / 2 - (n * (pw + 6)) / 2 + i * (pw + 6)), y = 58;
    panel(x, y, pw, 112);
    spr(`face_${T.h.id}`, x + 4, y + 4); text(T.h.d.name, x + 44, y + 10, { col: T.h.slot ? '#8ad8ff' : '#ffe84a' });
    const reveal = Math.min(T.rows.length, Math.floor(game.t * 2));
    T.rows.forEach((r, j) => { if (j >= reveal) return; text(r[0], x + 6, y + 44 + j * 14, { col: j === 2 && r[1] ? '#8ae87a' : '#c8d4f0' }); text(String(r[1]), x + pw - 6, y + 44 + j * 14, { col: '#ffffff', align: 'right' }); });
    if (reveal >= T.rows.length) text(`BONUS ${T.total}`, x + pw / 2, y + 96, { col: '#ffe84a', align: 'center' });
  });
  if (game.t > 3) text(Math.floor(game.t * 2) % 2 ? 'PRESS ATTACK' : '', VW / 2, VH - 30, { col: '#ffffff', align: 'center' });
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
  const xs = [24, 56, VW - 88, VW - 56, VW - 24];  // v0.8: five nurses, two left of the menu, three right (Nate on the end)
  HERO_ORDER.forEach((id, i) => { const A = anim(id, 'idle'); frame(id, A.s + (Math.floor(game.t * 2 + i) % A.n), xs[i], 212, { flip: i > 1 }); });
  // Tilly cruises back and forth along the bottom, behind the menu
  const per = 14, ph = (game.t % per) / per, dir = ph < 0.5 ? 1 : -1, u = ph < 0.5 ? ph * 2 : (1 - ph) * 2;
  const T = anim('tilly', 'drive'); frame('tilly', T.s + (Math.floor(game.t * 8) % T.n), -90 + u * (VW + 180), 226, { flip: dir < 0, scale: 1.2 });
  if (!game.overlay) panel(VW / 2 - 76, 124, 152, 74, '#0a1030', '#3a4c92', 0.82);
  text(`HI ${String(save.hi[0] ? save.hi[0].s : 0).padStart(7, '0')}`, VW - 6, 4, { col: '#ffe84a', align: 'right' });
  if (!game.overlay) drawMenu(game.menu);
  text('ORIGINAL GAME FOR BILL W. 2026', VW / 2, VH - 9, { col: '#c8d4f0', align: 'center' });
}
function drawSelect() {
  const VW = G.VW, VH = G.VH, S = game.sel;
  W.camX = 600; drawBackground(); rect(0, 0, VW, VH, '#0a1030', 0.72);
  text('CHOOSE YOUR NURSE', VW / 2, 8, { col: '#ffe84a', align: 'center', scale: 1 });
  // v0.8: five cards. Fits 398 px (16:9 phones/desktop) up to wide phones; long names (NASTY NATE) wrap onto two lines
  const n = HERO_ORDER.length, cw = Math.min(84, Math.floor((VW - 12) / n) - 4), ch = 176, x0 = Math.round((VW - (cw + 4) * n + 4) / 2), y0 = 20;
  game.cardRects = [];
  HERO_ORDER.forEach((id, i) => {
    const H = HEROES[id], x = x0 + i * (cw + 4), y = y0;
    const p1 = S.p[0] && S.p[0].cur === i, p2 = S.p[1] && S.p[1].cur === i;
    game.cardRects.push([x, y, cw, ch]);
    panel(x, y, cw, ch, p1 || p2 ? '#2a3a7a' : '#141c40', p1 && p2 ? '#ffffff' : p1 ? '#ffe84a' : p2 ? '#8ad8ff' : '#3a4c92');
    spr(`face_${id}`, x + cw / 2 - 18, y + 3);
    const nm = H.name.length * 8 > cw - 8 ? H.name.split(' ') : [H.name];
    nm.forEach((q, k) => text(q, x + cw / 2, y + 41 + k * 9, { col: '#ffffff', align: 'center' }));
    text(H.role.toUpperCase(), x + cw / 2, y + 41 + nm.length * 9, { col: H.color, align: 'center' });
    const A = anim(id, (p1 && S.p[0].locked) || (p2 && S.p[1].locked) ? 'win' : 'idle');
    frame(id, A.s + (Math.floor(game.t * 3) % A.n), x + cw / 2, y + 131, {});
    const bw = Math.floor((cw - 34) / 5);
    ['POW', 'SPD', 'RCH', 'TUF'].forEach((lab, j) => {
      const yy = y + 134 + j * 8; text(lab, x + 3, yy, { col: '#c8d4f0', shadow: null });
      for (let k = 0; k < 5; k++) rect(x + 30 + k * bw, yy + 1, bw - 1, 5, k < H.stats[j] ? H.color : '#2a2e4a');
    });
    if (p1) text('1P', x + 2, y + 4, { col: '#ffe84a' });
    if (p2) text('2P', x + cw - 2, y + 4, { col: '#8ad8ff', align: 'right' });
    const ok = (p1 && S.p[0].locked) || (p2 && S.p[1].locked);
    if (ok) text('OK!', x + cw / 2, y + ch - 9, { col: p1 && S.p[0].locked ? '#ffe84a' : '#8ad8ff', align: 'center' });
  });
  const P = S.p[0]; const H = HEROES[HERO_ORDER[P.cur]];
  text(`SPECIAL: ${H.special}`, VW / 2, y0 + ch + 4, { col: '#8ad8ff', align: 'center' });
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
function wrapText(s, max) {  // v0.8: greedy word wrap for 8 px text
  const out = []; let cur = '';
  for (const w of s.split(' ')) { if (cur && (cur + ' ' + w).length > max) { out.push(cur); cur = w; } else cur = cur ? cur + ' ' + w : w; }
  if (cur) out.push(cur);
  return out;
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
    if (T.quote && game.t > 0.6) wrapText(`"${T.quote}"`, Math.floor((pw - 50) / 8)).slice(0, 2).forEach((q, k) => text(q, x + 44, y + 21 + k * 9, { col: '#c8f0e8', shadow: null }));  // v0.8 Nate's floor-clear line
    const reveal = Math.min(T.rows.length, Math.floor(game.t * 2));
    T.rows.forEach((r, j) => { if (j >= reveal) return; text(r[0], x + 6, y + 44 + j * 14, { col: '#c8d4f0' }); text(String(r[1]), x + pw - 6, y + 44 + j * 14, { col: '#ffffff', align: 'right' }); });
    if (reveal >= T.rows.length) text(`TOTAL ${T.total}`, x + pw / 2, y + 104, { col: '#ffe84a', align: 'center' });
  });
  if (game.t > 3) text(Math.floor(game.t * 2) % 2 ? 'PRESS ATTACK' : '', VW / 2, VH - 30, { col: '#ffffff', align: 'center' });
}
function drawEnding() {  // v0.5: the end of the shift
  const VW = G.VW, VH = G.VH;
  rect(0, 0, VW, VH, '#05060c', 0.9);
  const sc = Math.min(1, (VW - 20) / sprSize('w_theend')[0]), [w] = sprSize('w_theend');
  spr('w_theend', VW / 2, 26, { ax: w / 2, scale: sc * Math.min(1, game.t * 2) });
  text('NICK AND THE CREW SURVIVED THE SHIFT.', VW / 2, 82, { col: '#ffffff', align: 'center' });
  text('EVERY PATIENT TUCKED IN. MOSTLY.', VW / 2, 96, { col: '#c8d4f0', align: 'center' });
  W.heroes.forEach((h, i) => { const n = W.heroes.length, x = VW / 2 + (i - (n - 1) / 2) * 120; spr(`face_${h.id}`, x - 52, 112); text(h.d.short || h.d.name, x - 10, 118, { col: h.slot ? '#8ad8ff' : '#ffe84a' }); text(String(h.score).padStart(7, '0'), x - 10, 132, { col: '#ffffff' }); });
  text('SEE YOU NEXT SHIFT...', VW / 2, 164, { col: '#3aa8ff', align: 'center' });
  if (game.newHi) text('NEW HIGH SCORE!', VW / 2, 178, { col: Math.floor(game.t * 6) % 2 ? '#ffe84a' : '#ff8a1e', align: 'center' });
  if (game.t > 1.5) text('PRESS ATTACK', VW / 2, VH - 20, { col: '#c8d4f0', align: 'center' });
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
      W.t += dt; for (const h of W.heroes) if (h.st !== 'out') h.update(dt, { mx: 0, my: 0, held: {}, prs: {} }); updateWorld(dt); nightLights(dt);
      if (game.t > 2.4) { game.scene = 'play'; for (const h of W.heroes) if (h.st === 'enter') h.set('idle'); }
      break;
    }
    case 'play': playUpdate(dt); break;
    case 'cutscene': { const skip = game.t > 0.6 && (anyButton() || game.cutSkip); game.cutSkip = false; if (updateCut(game.cut, dt, skip)) { const d = game.cutDone; game.cut = null; game.cutDone = null; if (d) d(); } break; }
    case 'bonus': {
      if (BONUS_STATE.phase === 'intro') { W.t += dt; for (const h of W.heroes) h.update(dt, { mx: 0, my: 0, held: {}, prs: {} }); updateWorld(dt); updateBonus(dt); }
      else { playUpdate(dt); if (game.scene === 'bonus' && !game.overlay && updateBonus(dt)) toBonusTally(); }
      break;
    }
    case 'btally': W.t += dt; for (const h of W.heroes) h.t += dt; updateWorld(dt); if (game.t > 3 && any) goNext(); break;
    case 'scoot': scootPlay(dt); break;
    case 'stally': W.t += dt; updateWorld(dt); if (game.t > 3 && any) goNight(); break;
    case 'tally': W.t += dt; for (const h of W.heroes) h.t += dt; updateWorld(dt); if (game.t > 3 && any) afterTally(); break;
    case 'teaser': if (game.t > 1.5 && any) toTitle(); break;
    case 'ending': if (game.t > 1.5 && any) { game.scene = 'scores'; game.t = 0; } break;
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
    case 'cutscene': drawCut(game.cut); break;
    case 'bonus': drawWorld(); drawHUD(game); drawBonusHUD(); break;
    case 'btally': drawWorld(); drawBonusTally(); break;
    case 'scoot': drawScooter(); drawHUD(game); drawScooterHUD(); break;
    case 'stally': drawScooter(); drawScootTally(game); break;
    case 'teaser': drawTeaser(); break;
    case 'ending': drawEnding(); break;
    case 'gameover': if (W.scootOver) drawScooter(); else drawWorld(); drawGameOver(); break;
    case 'scores': drawScores(); break;
  }
  if (game.overlay) drawMenu(game.overlay);
  if (game.scene !== 'play' && game.scene !== 'intro' && game.toasts.length) { const t = game.toasts[0]; const w = textW(t.s) + 16; panel((G.VW - w) / 2, G.VH - 40, w, 16, '#1a2450', '#8ad8ff'); text(t.s, G.VW / 2, G.VH - 36, { col: '#fff', align: 'center' }); }
  updateRideLabel();
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
  document.getElementById('pausebtn').addEventListener('pointerdown', (e) => { e.preventDefault(); e.stopPropagation(); if (game.scene === 'play' || game.scene === 'bonus' || game.scene === 'scoot') { if (game.overlay) resume(); else { game.overlay = pauseMenu(); sfx('select'); } } });
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
    if (game.scene === 'cutscene') { game.cutSkip = true; return; }
    if (game.scene === 'select') selectTap(lx, ly);
    else if (['teaser', 'gameover', 'scores', 'ending'].includes(game.scene) && game.t > 1.2) { if (game.scene === 'teaser') toTitle(); else if (game.scene === 'gameover' || game.scene === 'ending') { game.scene = 'scores'; game.t = 0; } else toTitle(); }
    else if (game.scene === 'tally' && game.t > 3) afterTally();
    else if (game.scene === 'btally' && game.t > 3) goNext();
    else if (game.scene === 'stally' && game.t > 3) goNight();
  });
  view.addEventListener('pointermove', (e) => { const m = activeMenu(); if (!m || e.pointerType !== 'mouse') return; const [lx, ly] = toLogical(e); const i = hitMenu(m, lx, ly); if (i >= 0 && i !== m.sel) m.sel = i; });
  toTitle();
  loaded();
  requestAnimationFrame(frameLoop);
  // test hooks
  window.__nbd = { spawn, prop: (kind, dx = 40, dy = 0, drops = []) => { const h = W.heroes[0]; const p = makeProp(kind, (h ? h.x : W.camX + 200) + dx, Math.max(136, Math.min(212, (h ? h.y : 170) + dy)), drops); W.props.push(p); return W.props.length - 1; }, hitProp, rollLoot, drop: (k) => { const h = W.heroes[0]; return h && dropItem(k, h.x, h.y, false); }, game, W, G, C, save, startGame, toSelect, toTitle, Director, display,
    cut: (id, after) => startCut(id, () => (after === 'play' ? (game.scene = 'play', setScene('game')) : toTitle())), bonus: () => { buildBreakroom(); startBonus(); game.scene = 'bonus'; game.t = 0; setScene('game'); }, B: BONUS_STATE, goLunch, loadLevel, afterTally, goNext, scooter: enterScooter, goScooter, goNight, SC, SCOOT, scootSpawn, ALARM, maybeYeller, pullAlarm, stationFor, alarmAllowed, settingsMenu, applySettings };
  if (Q.get('autostart') || Q.get('zone') || Q.get('level')) { toSelect(1); game.sel.p[0].cur = Math.max(0, HERO_ORDER.indexOf(Q.get('hero') || 'nick')); startGame(); if (Q.get('scene') === 'bonus') { game.cut = null; game.cutDone = null; window.__nbd.bonus(); } if (Q.get('scene') === 'scooter') { game.cut = null; game.cutDone = null; enterScooter(); } }
}
boot().catch((e) => { const t = document.getElementById('loadtxt'); if (t) t.textContent = 'Could not load: ' + e.message; console.error(e); });
