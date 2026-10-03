// 2D stand-in for the n64-suite runtime's common.js: just the parts input.js / display.js need (key state, virtual presses,
// the loading gate and the audio unlock flags), with the same semantics, minus three.js.
export const Q = new URLSearchParams(location.search);
export const keys = {};
export const pressed = [];
export const audio = { ready: false, unlocked: false, onUnlock: null };
addEventListener('keydown', (e) => {
  if (!audio.ready) { e.preventDefault(); return; }                     // loading gate: input is swallowed until loaded()
  if (!keys[e.code]) pressed.push(e.code);
  keys[e.code] = true;
  if (['Tab', 'Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Slash', 'Quote'].includes(e.code)) e.preventDefault();
});
addEventListener('keyup', (e) => { keys[e.code] = false; });
addEventListener('blur', () => { for (const k in keys) keys[k] = false; });
export function takePressed() { return pressed.splice(0, pressed.length); }
export function pressKey(code) { pressed.push(code); }
let armed = false;
for (const ev of ['pointerdown', 'touchstart']) addEventListener(ev, () => { if (audio.ready) armed = true; }, { capture: true, passive: true });
function unlockAudio(e) {
  if (!audio.ready || audio.unlocked || (e.type !== 'keydown' && e.type !== 'gamepad' && !armed)) return;
  audio.unlocked = true; if (audio.onUnlock) audio.onUnlock(e);
}
export function audioKick() { if (audio.ready && !audio.unlocked) unlockAudio({ type: 'gamepad' }); }
for (const ev of ['pointerup', 'touchend', 'click', 'keydown']) addEventListener(ev, unlockAudio, true);
export function loaded() {
  if (audio.ready) return; audio.ready = true; window.__loaded = true;
  const el = document.getElementById('loading'); if (el) { el.classList.add('done'); setTimeout(() => el.remove(), 400); }
}
