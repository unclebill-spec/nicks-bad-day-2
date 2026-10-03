// Per-player controls for 1-2 players: keyboard (one shared set in solo, split sets in 2P), any number of gamepads
// (standard mapping; Xbox / PlayStation / Switch Pro), and touch (floating joystick + 4 buttons). The shared
// kit/input.js still runs for device detection (<html data-input>), controller glyphs and connect toasts.
import { keys, takePressed } from '../kit/common.js';
import { createInput } from '../kit/input.js';

export const KB1 = { up: ['KeyW'], down: ['KeyS'], left: ['KeyA'], right: ['KeyD'], atk: ['KeyJ'], jmp: ['KeyK', 'Space'], sp: ['KeyL'], grab: ['KeyH', 'KeyU'], run: ['ShiftLeft'], start: ['Enter', 'KeyP'] };
export const KB2 = { up: ['ArrowUp'], down: ['ArrowDown'], left: ['ArrowLeft'], right: ['ArrowRight'], atk: ['Numpad1', 'Comma'], jmp: ['Numpad2', 'Period'], sp: ['Numpad3', 'Slash'], grab: ['Numpad0', 'KeyM'], run: ['ShiftRight'], start: ['NumpadEnter', 'Backslash'] };
const merge = (...ms) => { const o = {}; for (const m of ms) for (const k in m) o[k] = [...(o[k] || []), ...m[k]]; return o; };
export const KBALL = merge(KB1, KB2, { atk: ['KeyZ'], jmp: ['KeyX'], sp: ['KeyC'], grab: ['KeyV'] });
const BTN = ['atk', 'jmp', 'sp', 'grab', 'run', 'start', 'select'];
const PADMAP = { 0: 'jmp', 1: 'grab', 2: 'atk', 3: 'sp', 4: 'sp', 5: 'run', 6: 'grab', 7: 'run', 8: 'select', 9: 'start' };

export const C = { devs: {}, input: null, touch: { x: 0, y: 0, on: false, btn: {} }, split: false, menuQ: [], pads: [] };

function newDev(id) { return { id, mx: 0, my: 0, held: {}, prev: {}, prs: {}, tapT: 0, tapDir: 0, runLatch: false, lastMx: 0, idle: 0, any: false }; }
function dev(id) { return C.devs[id] || (C.devs[id] = newDev(id)); }

export function initControls(toast) {
  const nb = {}; for (const k of ['A', 'B', 'X', 'Y', 'LB', 'RB', 'LT', 'RT', 'SELECT', 'START', 'L3', 'R3', 'UP', 'DOWN', 'LEFT', 'RIGHT']) nb[k] = 'Pad' + k;
  C.input = createInput({ storageKey: 'nbd2.input', stickKeys: false, binds: nb, onToast: toast });
  // ---- touch: floating joystick in the left zone, 4 action buttons
  const zone = document.getElementById('joyzone'), joy = document.getElementById('joy'), knob = document.getElementById('knob');
  let jid = null, jc = null;
  const stage = document.getElementById('stage');
  zone.addEventListener('pointerdown', (e) => {
    if (jid !== null) return; e.preventDefault(); jid = e.pointerId; const r = stage.getBoundingClientRect();
    jc = { x: e.clientX, y: e.clientY }; joy.style.left = `${e.clientX - r.left}px`; joy.style.top = `${e.clientY - r.top}px`; joy.classList.add('on');
    knob.style.transform = ''; C.touch.on = true; C.touch.x = C.touch.y = 0;
  });
  zone.style.pointerEvents = 'auto';
  addEventListener('pointermove', (e) => {
    if (e.pointerId !== jid) return; const R = joy.clientWidth * 0.42 || 50;
    let x = (e.clientX - jc.x) / R, y = (e.clientY - jc.y) / R; const l = Math.hypot(x, y); if (l > 1) { x /= l; y /= l; }
    C.touch.x = l < 0.12 ? 0 : x; C.touch.y = l < 0.12 ? 0 : y; knob.style.transform = `translate(${x * R}px, ${y * R}px)`;
  });
  for (const ev of ['pointerup', 'pointercancel']) addEventListener(ev, (e) => { if (e.pointerId === jid) { jid = null; C.touch.on = false; C.touch.x = C.touch.y = 0; joy.classList.remove('on'); } });
  for (const b of document.querySelectorAll('#pad .ab')) {
    const k = b.dataset.b;
    b.addEventListener('pointerdown', (e) => { e.preventDefault(); e.stopPropagation(); C.touch.btn[k] = true; C.touch.tap = C.touch.tap || {}; C.touch.tap[k] = true; b.classList.add('down'); try { b.setPointerCapture(e.pointerId); } catch (err) { /* old browsers */ } });
    const up = (e) => { C.touch.btn[k] = false; b.classList.remove('down'); };
    b.addEventListener('pointerup', up); b.addEventListener('pointercancel', up); b.addEventListener('lostpointercapture', up);
  }
}

function kbHeld(map, a) { const l = map[a]; if (!l) return false; for (const c of l) if (keys[c]) return true; return false; }
function inMap(map, code) { for (const a in map) if (map[a].includes(code)) return a; return null; }

// called once per fixed step, before game logic
export function pollControls(dt) {
  const codes = takePressed();
  C.lastCodes = codes;
  const kbSets = C.split ? [['kb1', KB1], ['kb2', KB2]] : [['kb', KBALL]];
  for (const id of C.split ? ['kb'] : ['kb1', 'kb2']) delete C.devs[id];  // drop the stale keyboard device when switching modes
  for (const [id, map] of kbSets) {
    const d = dev(id);
    d.mx = (kbHeld(map, 'right') ? 1 : 0) - (kbHeld(map, 'left') ? 1 : 0);
    d.my = (kbHeld(map, 'down') ? 1 : 0) - (kbHeld(map, 'up') ? 1 : 0);
    for (const b of BTN) d.held[b] = kbHeld(map, b);
    const tapped = {}; for (const c of codes) { const a = inMap(map, c); if (a) tapped[a] = true; }
    finish(d, tapped, dt, codes.some((c) => inMap(map, c)));
  }
  // gamepads
  const list = navigator.getGamepads ? [...navigator.getGamepads()] : [];
  C.pads = [];
  for (const g of list) {
    if (!g || !g.connected) continue;
    const d = dev('pad' + g.index); C.pads.push(d.id);
    let x = g.axes[0] || 0, y = g.axes[1] || 0; const m = Math.hypot(x, y); if (m < 0.22) { x = 0; y = 0; }
    const b = (i) => { const q = g.buttons[i]; return !!q && (q.pressed || q.value > 0.55); };
    if (b(14)) x = -1; if (b(15)) x = 1; if (b(12)) y = -1; if (b(13)) y = 1;
    d.mx = x; d.my = y;
    for (const k of BTN) d.held[k] = false;
    for (const i in PADMAP) if (b(+i)) d.held[PADMAP[i]] = true;
    finish(d, {}, dt, Object.values(d.held).some(Boolean) || m > 0.5);
  }
  for (const id of Object.keys(C.devs)) if (id.startsWith('pad') && !C.pads.includes(id)) delete C.devs[id];
  // touch
  const t = dev('touch');
  t.mx = C.touch.x; t.my = C.touch.y;
  for (const k of BTN) t.held[k] = !!C.touch.btn[k];
  finish(t, C.touch.tap || {}, dt, !!C.touch.on || Object.values(C.touch.btn).some(Boolean));
  C.touch.tap = {};
}

function finish(d, tapped, dt, active) {
  if (!d.init) { d.init = true; for (const b of BTN) d.prev[b] = d.held[b]; tapped = {}; }  // a new device (mode switch / hot-plug) never fires on its first frame
  for (const b of BTN) { d.prs[b] = (d.held[b] && !d.prev[b]) || !!tapped[b]; d.prev[b] = d.held[b]; }
  // double-tap left/right -> run (keyboard, d-pad, stick and touch joystick)
  const dir = d.mx > 0.6 ? 1 : d.mx < -0.6 ? -1 : 0;
  const was = d.lastMx > 0.6 ? 1 : d.lastMx < -0.6 ? -1 : 0;
  d.tapT += dt;
  if (dir && !was) { if (dir === d.tapDir && d.tapT < 0.28) d.runLatch = true; d.tapDir = dir; d.tapT = 0; }
  if (!dir) d.runLatch = false;
  d.lastMx = d.mx;
  d.run = d.held.run || d.runLatch;
  // menu edges (with auto-repeat while held)
  const md = d.my < -0.6 ? 'up' : d.my > 0.6 ? 'down' : d.mx < -0.6 ? 'left' : d.mx > 0.6 ? 'right' : null;
  if (md !== d.menuDir) { d.menuDir = md; d.menuT = 0; d.menuEdge = md; } else if (md) { d.menuT += dt; d.menuEdge = null; if (d.menuT > 0.42) { d.menuT -= 0.12; d.menuEdge = md; } } else d.menuEdge = null;
  d.any = active || Object.values(d.prs).some(Boolean);
  if (d.any) d.idle = 0; else d.idle += dt;
}

// which device ids feed a player: in solo every device drives P1; in 2P each player has one device
export function devicesFor(p) { return p.devs || Object.keys(C.devs); }
export function readPlayer(p) {
  const o = { mx: 0, my: 0, held: {}, prs: {}, run: false };
  for (const id of devicesFor(p)) {
    const d = C.devs[id]; if (!d) continue;
    o.mx += d.mx; o.my += d.my; o.run = o.run || d.run;
    for (const b of BTN) { o.held[b] = o.held[b] || d.held[b]; o.prs[b] = o.prs[b] || d.prs[b]; }
  }
  const l = Math.hypot(o.mx, o.my); if (l > 1) { o.mx /= l; o.my /= l; }
  return o;
}
// menu intents from every device (anyone can drive menus)
export function menuIntents() {
  const out = [];
  for (const d of Object.values(C.devs)) {
    if (d.menuEdge) out.push({ a: d.menuEdge, dev: d.id });
    if (d.prs.atk || d.prs.jmp || d.prs.start) out.push({ a: 'ok', dev: d.id, start: d.prs.start });
    if (d.prs.grab) out.push({ a: 'back', dev: d.id });
  }
  for (const c of C.lastCodes || []) if (c === 'Escape' || c === 'Backspace') out.push({ a: 'back', dev: 'kb' });
  return out;
}
export function anyDevicePressed(ids) { return Object.values(C.devs).filter((d) => (!ids || ids.includes(d.id)) && (d.prs.atk || d.prs.jmp || d.prs.start)); }
