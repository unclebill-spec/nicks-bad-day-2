// WebAudio sound: all SFX decoded up front (small 22 kHz WAVs), music streamed into buffers with loop points from
// audio/music/music.json. Nothing plays until the first deliberate tap / key / pad press after loading (kit/common.js).
import { audio } from '../kit/common.js';

const SFX = ['jump', 'select', 'blip', 'coin', 'powerup', 'explosion', 'bounce', 'door', 'splash', 'laser', 'hurt', 'hit2', 'punch0', 'punch1', 'punch2',
  'heavy', 'whoosh', 'ding', 'honk', 'zap', 'motor', 'clang', 'smash', 'spray', 'page', 'voice0', 'voice1', 'voice2', 'voice3', 'voice4', 'voice5', 'tilly'];
export const S = { ctx: null, buf: {}, music: {}, loops: {}, cur: null, curName: null, master: null, mus: null, fx: null, vol: { music: 0.6, sfx: 0.8 }, want: null };

export async function initSound(vol) {
  Object.assign(S.vol, vol || {});
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return;
  S.ctx = new AC();
  S.master = S.ctx.createGain(); S.master.connect(S.ctx.destination);
  S.mus = S.ctx.createGain(); S.mus.connect(S.master); S.fx = S.ctx.createGain(); S.fx.connect(S.master);
  setVolumes();
  try { S.loops = await (await fetch('audio/music/music.json')).json(); } catch (e) { S.loops = {}; }
  await Promise.all(SFX.map(async (n) => { try { S.buf[n] = await decode(`audio/sfx/${n}.wav`); } catch (e) { /* missing sound is not fatal */ } }));
  audio.onUnlock = () => { if (S.ctx.state !== 'running') S.ctx.resume().catch(() => {}); if (S.want) { const w = S.want; S.want = null; playMusic(w, true); } };
}
async function decode(url) { const r = await fetch(url); const a = await r.arrayBuffer(); return await new Promise((res, rej) => S.ctx.decodeAudioData(a, res, rej)); }
export function setVolumes() { if (!S.ctx) return; S.mus.gain.value = S.vol.music * 0.55; S.fx.gain.value = S.vol.sfx; }

const last = {};
export function sfx(name, { vol = 1, rate = 1, gap = 0.03 } = {}) {
  if (!S.ctx || !audio.unlocked || !S.buf[name]) return;
  const now = S.ctx.currentTime; if (last[name] && now - last[name] < gap) return; last[name] = now;
  const src = S.ctx.createBufferSource(); src.buffer = S.buf[name]; src.playbackRate.value = rate * (0.97 + Math.random() * 0.06);
  const g = S.ctx.createGain(); g.gain.value = vol; src.connect(g); g.connect(S.fx); src.start();
}

export async function playMusic(name, force = false) {
  if (!S.ctx) return;
  if (S.curName === name && !force) return;
  stopMusic(); S.curName = name;
  if (!audio.unlocked) { S.want = name; return; }
  if (!S.music[name]) { try { S.music[name] = await decode(`audio/music/${name}.mp3`); } catch (e) { return; } }
  if (S.curName !== name) return;
  const src = S.ctx.createBufferSource(); src.buffer = S.music[name];
  const L = S.loops[name];
  if (!L || L.loop !== false) { src.loop = true; if (L && L.end > L.start + 2) { src.loopStart = L.start; src.loopEnd = Math.min(L.end, src.buffer.duration); } }
  src.connect(S.mus); src.start(); S.cur = src;
}
export function stopMusic() { if (S.cur) { try { S.cur.stop(); } catch (e) { /* already stopped */ } S.cur = null; } S.curName = null; S.want = null; }
export function preloadMusic(names) { if (!S.ctx) return; for (const n of names) if (!S.music[n]) decode(`audio/music/${n}.mp3`).then((b) => { S.music[n] = b; }).catch(() => {}); }
