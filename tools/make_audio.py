"""Chiptune music + SFX for the game, using the n64-suite generators (music.compose + its built-in pulse/saw/triangle
synth, and the sfxr-style sfx.make), plus a few custom numpy sounds (elevator ding, horn honk, defib zap, punches).

    python3 tools/make_audio.py   -> audio/music/*.mp3 (+ loop json), audio/sfx/*.wav
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

SUITE = Path("/workspace/n64-suite")
sys.path.insert(0, str(SUITE))
from n64 import music as M  # noqa: E402
from n64 import sfx as X  # noqa: E402
from n64.audio_util import write_wav  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).parent.parent
MUS, SFX = ROOT / "audio" / "music", ROOT / "audio" / "sfx"
MUS.mkdir(parents=True, exist_ok=True)
SFX.mkdir(parents=True, exist_ok=True)
TMP = ROOT / "tests" / "out" / "audio"
TMP.mkdir(parents=True, exist_ok=True)
RATE = 22050

TRACKS = {  # game track: (suite mood, seed, theme)
    "title": ("title", 11, "ember"),
    "select": ("town", 4, "verdant"),
    "stage": ("overworld", 7, "ember"),
    "boss": ("boss", 5, "ember"),
    "clear": ("victory", 2, "verdant"),
}
loops = {}
for name, (mood, seed, theme) in TRACKS.items():
    song, info = M.compose(mood, seed, theme)
    if name == "stage":
        song.tempo = int(song.tempo * 1.08)
    wav = TMP / f"{name}.wav"
    M.render_fallback(song, wav, RATE)  # pulse / saw / triangle + noise drums = chiptune
    M._normalize(wav, -1.0)
    mp3 = MUS / f"{name}.mp3"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-ac", "1", "-b:a", "64k", str(mp3)], check=True)
    loops[name] = {"loop": info["loop"], "start": round(info["loop_start_s"] * 120 / song.tempo * song.tempo / 120, 3),
                   "end": round(info["loop_end_s"], 3), "tempo": song.tempo}
    if name == "stage":
        k = 1 / 1.08
        loops[name]["start"] = round(info["loop_start_s"] * k, 3)
        loops[name]["end"] = round(info["loop_end_s"] * k, 3)
(MUS / "music.json").write_text(json.dumps(loops, indent=1))

# ---- sfxr-style picks (seed chosen by ear for each)
PICK = {"jump": ("jump", 3), "select": ("select", 2), "blip": ("blip", 5), "coin": ("coin", 4), "powerup": ("powerup", 6),
        "explosion": ("explosion", 3), "bounce": ("bounce", 2), "door": ("door", 1), "splash": ("splash", 2), "laser": ("laser", 7),
        "hurt": ("hurt", 9), "hit2": ("hit", 4)}
for out, (kind, seed) in PICK.items():
    s, _ = X.make(kind, seed)
    write_wav(SFX / f"{out}.wav", s * 0.9, RATE)

t = lambda d: np.arange(int(d * RATE)) / RATE
rng = np.random.default_rng(7)


def env(x, a=0.004, d=0.2):
    n = len(x); tt = np.arange(n) / RATE
    return x * np.minimum(1, tt / a) * np.exp(-tt / d)


def save(name, x, g=0.85):
    x = x / (np.abs(x).max() or 1) * g
    write_wav(SFX / f"{name}.wav", x, RATE)


# punches: a low thump + noise crack (3 variants), heavy hit, whoosh
for i, (f0, crack) in enumerate(((150, 0.5), (120, 0.6), (95, 0.8))):
    tt = t(0.16)
    body = np.sin(2 * np.pi * np.cumsum(f0 * np.exp(-tt * 18) + 40) / RATE)
    noise = rng.uniform(-1, 1, len(tt)) * np.exp(-tt * 60) * crack
    save(f"punch{i}", env(body, 0.002, 0.07) + noise)
tt = t(0.32)
save("heavy", env(np.sin(2 * np.pi * np.cumsum(110 * np.exp(-tt * 9) + 30) / RATE), 0.002, 0.14) + rng.uniform(-1, 1, len(tt)) * np.exp(-tt * 25) * 0.9)
tt = t(0.18)
wn = rng.uniform(-1, 1, len(tt))
k = np.exp(-((tt - 0.07) / 0.05) ** 2)
save("whoosh", np.convolve(wn, np.ones(6) / 6, "same") * k, 0.5)
# elevator ding: two soft bell partials
tt = t(1.4)
ding = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt * dcy) for f, a, dcy in ((1318.5, 1, 2.2), (2637, 0.35, 4), (3950, 0.12, 6)))
save("ding", ding, 0.7)
# horn honk: buzzy square with a pitch wobble (bulb horn)
tt = t(0.5)
f = 330 + 18 * np.sin(2 * np.pi * 7 * tt)
sq = np.sign(np.sin(2 * np.pi * np.cumsum(f) / RATE)) * 0.6 + np.sign(np.sin(2 * np.pi * np.cumsum(f * 1.5) / RATE)) * 0.3
save("honk", sq * np.minimum(1, tt / 0.01) * np.minimum(1, (0.5 - tt) / 0.08), 0.6)
# defib zap: rising buzz + crack
tt = t(0.7)
f = 80 + 900 * tt
zz = np.sign(np.sin(2 * np.pi * np.cumsum(f) / RATE)) * (tt / 0.7) * 0.5
cr = np.zeros_like(tt); n0 = int(0.55 * RATE); cr[n0:] = rng.uniform(-1, 1, len(tt) - n0) * np.exp(-(tt[n0:] - 0.55) * 30)
save("zap", zz + cr * 1.2, 0.8)
# motor whine (boss charge)
tt = t(1.0)
f = 120 + 260 * np.minimum(1, tt / 0.6)
save("motor", (np.sign(np.sin(2 * np.pi * np.cumsum(f) / RATE)) * 0.4 + np.sin(2 * np.pi * np.cumsum(f * 2) / RATE) * 0.3) * np.minimum(1, (1.0 - tt) / 0.1), 0.5)
# clang (metal weapon)
tt = t(0.5)
save("clang", sum(np.sin(2 * np.pi * fq * tt) * np.exp(-tt * d) for fq, d in ((620, 7), (1490, 9), (2310, 12), (3170, 16))) + rng.uniform(-1, 1, len(tt)) * np.exp(-tt * 80), 0.7)
# glass / vending smash
tt = t(0.6)
save("smash", rng.uniform(-1, 1, len(tt)) * np.exp(-tt * 8) * (1 + 0.5 * np.sin(2 * np.pi * 3000 * tt)), 0.7)
# extinguisher spray (filtered noise loop)
tt = t(0.4)
save("spray", np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(3) / 3, "same") * np.minimum(1, tt / 0.03) * np.minimum(1, (0.4 - tt) / 0.05), 0.45)
# page tones ("Code Blue" overhead page): three rising tones
seq = np.concatenate([np.sin(2 * np.pi * fq * t(0.16)) * np.exp(-t(0.16) * 4) for fq in (523.25, 659.25, 783.99)])
save("page", seq, 0.7)
# patient voices: gibberish babble (suite)
for i, (txt, p) in enumerate((("Hey! Is it morning?", 0.8), ("Nurse! Nurse!", 1.3), ("Where are my teeth?", 1.0), ("I want pudding!", 1.6),
                              ("Zzz... five more minutes", 0.7), ("Hah!", 1.9))):
    s = X.babble(txt, np.random.default_rng(i) if False else __import__("random").Random(i), pitch=p, speed=1.1)
    save(f"voice{i}", s, 0.6)
s = X.babble("Out of my way, sweetie!", __import__("random").Random(42), pitch=1.5, speed=1.2)
save("tilly", s, 0.7)
import prop_sfx  # noqa: E402  (v0.3 crash / rattle / thunk / shatter)
prop_sfx.build()
print("music:", sorted(p.name for p in MUS.iterdir()))
print("sfx:", sorted(p.name for p in SFX.iterdir()))
