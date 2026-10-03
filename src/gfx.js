// Low-res pixel renderer: everything draws into a VW x VH buffer (224 or 240 lines tall), which is blitted with nearest
// scaling to the visible canvas. Sprite sheets come from art/atlas.json (built by tools/make_art.py).
export const G = { VW: 398, VH: 224, k: 1, buf: null, ctx: null, view: null, vctx: null, atlas: null, img: {}, white: {}, font: null, fontCache: {}, shake: 0, shakeX: 0, shakeY: 0, flash: 0, flashCol: '#fff' };

export function loadImage(src) {
  return new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = () => rej(new Error('image ' + src)); i.src = src; });
}

function silhouette(img, col = '#fff') {
  const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
  const x = c.getContext('2d'); x.drawImage(img, 0, 0); x.globalCompositeOperation = 'source-in'; x.fillStyle = col; x.fillRect(0, 0, c.width, c.height);
  return c;
}

export async function initGfx(onProgress) {
  G.view = document.getElementById('view');
  G.vctx = G.view.getContext('2d');
  G.buf = document.createElement('canvas');
  G.ctx = G.buf.getContext('2d');
  G.atlas = await (await fetch('art/atlas.json')).json();
  const list = [['sprites', G.atlas.sprites.img], ['font', 'art/font8.png']];
  for (const [k, v] of Object.entries(G.atlas.chars)) list.push([k, v.img]);
  let n = 0;
  await Promise.all(list.map(async ([k, src]) => { G.img[k] = await loadImage(src); onProgress && onProgress(++n / list.length); }));
  for (const k of Object.keys(G.atlas.chars)) G.white[k] = silhouette(G.img[k]);
  G.font = G.img.font;
  resize(398, 224, 1);
}

export function resize(vw, vh, k) {
  G.VW = vw; G.VH = vh; G.k = k;
  G.buf.width = vw; G.buf.height = vh;
  G.view.width = vw * k; G.view.height = vh * k;
  G.ctx.imageSmoothingEnabled = false; G.vctx.imageSmoothingEnabled = false;
}

export function present() {
  const v = G.vctx; v.imageSmoothingEnabled = false;
  v.drawImage(G.buf, 0, 0, G.VW * G.k, G.VH * G.k);
}

// ---- atlas sprites
export function spr(name, x, y, { flip = false, alpha = 1, ax = 0, ay = 0, rot = 0, scale = 1, light = false } = {}) {
  const r = G.atlas.sprites.rects[name]; if (!r) return;
  const c = G.ctx;
  if (!flip && !rot && alpha === 1 && scale === 1 && !light) { c.drawImage(G.img.sprites, r[0], r[1], r[2], r[3], Math.round(x - ax), Math.round(y - ay), r[2], r[3]); return; }
  c.save(); c.globalAlpha = alpha; if (light) c.globalCompositeOperation = 'lighter'; c.translate(Math.round(x), Math.round(y)); if (rot) c.rotate(rot); if (flip) c.scale(-1, 1); if (scale !== 1) c.scale(scale, scale);
  c.drawImage(G.img.sprites, r[0], r[1], r[2], r[3], -ax, -ay, r[2], r[3]); c.restore();
}
export const sprSize = (name) => { const r = G.atlas.sprites.rects[name]; return r ? [r[2], r[3]] : [0, 0]; };

// ---- character frames: sheet + global frame index
export function frame(sheet, idx, x, y, { flip = false, white = false, alpha = 1, scale = 1 } = {}) {
  const A = G.atlas.chars[sheet]; if (!A) return;
  const [cw, ch] = A.cell, [ax, ay] = A.anchor, cols = A.cols;
  const sx = (idx % cols) * cw, sy = Math.floor(idx / cols) * ch;
  const im = white ? G.white[sheet] : G.img[sheet];
  const c = G.ctx;
  c.save(); c.globalAlpha = alpha; c.translate(Math.round(x), Math.round(y)); if (flip) c.scale(-1, 1); if (scale !== 1) c.scale(scale, scale);
  c.drawImage(im, sx, sy, cw, ch, -ax, -ay, cw, ch); c.restore();
}
// Runtime recolour: a copy of a character sheet with exact colours swapped (hair, skin, gown, socks). Cached by name.
const hex = (c) => [parseInt(c.slice(1, 3), 16), parseInt(c.slice(3, 5), 16), parseInt(c.slice(5, 7), 16)];
export function tintSheet(base, key, pairs) {
  const name = `${base}~${key}`;
  if (G.img[name]) return name;
  const src = G.img[base]; if (!src) return base;
  const c = document.createElement('canvas'); c.width = src.width; c.height = src.height;
  const x = c.getContext('2d'); x.drawImage(src, 0, 0);
  const id = x.getImageData(0, 0, c.width, c.height), d = id.data;
  const map = new Map();
  for (const [a, b] of pairs) { if (a && b && a !== b) { const A = hex(a); map.set((A[0] << 16) | (A[1] << 8) | A[2], hex(b)); } }
  for (let i = 0; i < d.length; i += 4) {
    if (!d[i + 3]) continue;
    const t = map.get((d[i] << 16) | (d[i + 1] << 8) | d[i + 2]);
    if (t) { d[i] = t[0]; d[i + 1] = t[1]; d[i + 2] = t[2]; }
  }
  x.putImageData(id, 0, 0);
  G.img[name] = c; G.white[name] = G.white[base]; G.atlas.chars[name] = G.atlas.chars[base];
  return name;
}
export function anim(sheet, name) { const A = G.atlas.chars[sheet]; return A && A.anims[name]; }

// ---- bitmap text (Press Start 2P 8x8)
function tinted(col) {
  if (G.fontCache[col]) return G.fontCache[col];
  return (G.fontCache[col] = silhouette(G.font, col));
}
export function text(s, x, y, { col = '#fff', shadow = '#1a1020', align = 'left', scale = 1, alpha = 1 } = {}) {
  s = String(s); const w = s.length * 8 * scale;
  let x0 = align === 'center' ? x - w / 2 : align === 'right' ? x - w : x;
  x0 = Math.round(x0); y = Math.round(y);
  const c = G.ctx; c.save(); c.globalAlpha = alpha;
  const draw = (img, dx, dy) => {
    for (let i = 0; i < s.length; i++) {
      const code = s.charCodeAt(i) - 32; if (code <= 0 || code > 94) continue;
      c.drawImage(img, (code % 16) * 8, Math.floor(code / 16) * 8, 8, 8, x0 + i * 8 * scale + dx, y + dy, 8 * scale, 8 * scale);
    }
  };
  if (shadow) draw(tinted(shadow), scale, scale);
  draw(tinted(col), 0, 0);
  c.restore();
  return w;
}
export const textW = (s, scale = 1) => String(s).length * 8 * scale;

// ---- primitives
export function rect(x, y, w, h, col, alpha = 1) { const c = G.ctx; c.globalAlpha = alpha; c.fillStyle = col; c.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h)); c.globalAlpha = 1; }
export function frameRect(x, y, w, h, col) { rect(x, y, w, 1, col); rect(x, y + h - 1, w, 1, col); rect(x, y, 1, h, col); rect(x + w - 1, y, 1, h, col); }
export function panel(x, y, w, h, fill = '#1a2450', edge = '#ffe84a', alpha = 0.92) {
  rect(x + 2, y + 2, w, h, '#000', 0.4); rect(x, y, w, h, fill, alpha); frameRect(x, y, w, h, '#1a1020'); frameRect(x + 1, y + 1, w - 2, h - 2, edge);
}
export function ellipse(x, y, rx, ry, col, alpha = 1) {
  const c = G.ctx; c.globalAlpha = alpha; c.fillStyle = col; c.beginPath(); c.ellipse(Math.round(x), Math.round(y), rx, ry, 0, 0, Math.PI * 2); c.fill(); c.globalAlpha = 1;
}
export function ring(x, y, rx, ry, col, w = 2, alpha = 1) {
  const c = G.ctx; c.globalAlpha = alpha; c.strokeStyle = col; c.lineWidth = w; c.beginPath(); c.ellipse(Math.round(x), Math.round(y), Math.max(1, rx), Math.max(1, ry), 0, 0, Math.PI * 2); c.stroke(); c.globalAlpha = 1;
}
export function bolt(x0, y0, x1, y1, col, seed, w = 1) {
  const c = G.ctx; c.strokeStyle = col; c.lineWidth = w; c.beginPath(); c.moveTo(x0, y0);
  let s = seed; const rnd = () => { s = (s * 16807) % 2147483647; return s / 2147483647 - 0.5; };
  for (let i = 1; i < 6; i++) { const t = i / 6; c.lineTo(x0 + (x1 - x0) * t + rnd() * 8, y0 + (y1 - y0) * t + rnd() * 8); }
  c.lineTo(x1, y1); c.stroke();
}
