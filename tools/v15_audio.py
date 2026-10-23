"""v0.15 audio for LABOR & DELIVERY, without rebuilding older audio:

    python3 tools/v15_audio.py -> audio/music/{ld,stork}.mp3 (+ loop points in music.json)
                                  audio/sfx/{camflash,purse,juice,flap,storkhonk,stork,stork_ko,grandma}.wav
"""
from __future__ import annotations

import json
import random
import subprocess
import sys
from pathlib import Path

import numpy as np

SUITE = Path("/workspace/n64-suite")
sys.path.insert(0, str(SUITE))
from n64 import music as M  # noqa: E402
from n64 import sfx as X  # noqa: E402
from n64.audio_util import write_wav  # noqa: E402

ROOT = Path(__file__).parent.parent
MUS, SFX = ROOT / "audio" / "music", ROOT / "audio" / "sfx"
TMP = ROOT / "tests" / "out" / "audio"
TMP.mkdir(parents=True, exist_ok=True)
RATE = 22050
TRACKS = {  # name: (suite mood, seed, theme, tempo factor)
    "ld": ("overworld", 71, "reef", 1.0),         # labor & delivery: a sweet lullaby-pop groove
    "stork": ("boss", 73, "ember", 1.12),         # THE STORK
}


def build_music():
    loops = json.loads((MUS / "music.json").read_text())
    for name, (mood, seed, theme, k) in TRACKS.items():
        song, info = M.compose(mood, seed, theme)
        song.tempo = int(song.tempo * k)
        wav = TMP / f"{name}.wav"
        M.render_fallback(song, wav, RATE)
        M._normalize(wav, -1.0)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-ac", "1", "-b:a", "64k", str(MUS / f"{name}.mp3")], check=True)
        loops[name] = {"loop": info["loop"], "start": round(info["loop_start_s"] / k, 3), "end": round(info["loop_end_s"] / k, 3), "tempo": song.tempo}
    (MUS / "music.json").write_text(json.dumps(loops, indent=1))


def t(d):
    return np.arange(int(d * RATE)) / RATE


def save(name, x, g=0.85):
    x = x / (np.abs(x).max() or 1) * g
    write_wav(SFX / f"{name}.wav", x, RATE)


def sq(f):
    return np.sign(np.sin(2 * np.pi * np.cumsum(f) / RATE))


def build_sfx():
    rng = np.random.default_rng(1515)
    # camflash: a camcorder flash, a capacitor whine up then a POP
    tt = t(0.35); f = 1800 + 5000 * tt / 0.35
    save("camflash", np.concatenate([np.sin(2 * np.pi * np.cumsum(f[:5000]) / RATE) * 0.3, rng.uniform(-1, 1, len(tt) - 5000) * np.exp(-np.arange(len(tt) - 5000) / 500)]), 0.6)
    # purse: a heavy leathery WHUMP
    tt = t(0.3); n = np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(40) / 40, "same")
    save("purse", (n + np.sin(2 * np.pi * 90 * tt) * 0.6) * np.exp(-tt * 14), 0.7)
    # juice: a squishy juice-box squirt
    tt = t(0.3); save("juice", sq(700 - 1400 * tt) * 0.3 * np.exp(-tt * 10) + np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(8) / 8, "same") * np.exp(-tt * 12), 0.5)
    # flap: big wing beats (three low noise whooshes)
    tt = t(0.8); x = np.zeros(len(tt)); base = np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(60) / 60, "same")
    for k in range(3):
        c = 0.12 + k * 0.25
        x += base * np.exp(-((tt - c) / 0.05) ** 2)
    save("flap", x, 0.7)
    # honk: a goofy bird honk (a nasal square wave with a bend)
    tt = t(0.4); save("storkhonk", sq(330 + 60 * np.sin(2 * np.pi * 5 * tt)) * np.minimum(1, tt * 40) * np.exp(-tt * 3), 0.55)
    save("stork", X.babble("Special delivery!", random.Random(1517), pitch=1.15, speed=1.2), 0.7)
    save("stork_ko", X.babble("Wrong... address... honk", random.Random(1518), pitch=1.0, speed=0.8), 0.7)
    save("grandma", X.babble("I'm not going anywhere!", random.Random(1519), pitch=1.2, speed=0.9), 0.7)


if __name__ == "__main__":
    build_music()
    build_sfx()
    print("ok")
