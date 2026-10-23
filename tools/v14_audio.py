"""v0.14 audio for the CAFETERIA LUNCH RUSH, without rebuilding older audio:

    python3 tools/v13_audio.py -> audio/music/{cafe,lunchlady}.mp3 (+ loop points in music.json)
                                  audio/sfx/{ladle,soup,traycrash,next,lunchlady,lunchlady_ko}.wav
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
    "cafe": ("overworld", 61, "reef", 1.06),      # the lunch rush: a bouncy, clattery groove
    "lunchlady": ("boss", 63, "ember", 1.1),       # LUNCH LADY LORETTA
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
    rng = np.random.default_rng(1414)
    # ladle: a big metal BONG (inharmonic partials, fast decay)
    tt = t(0.5)
    save("ladle", sum(np.sin(2 * np.pi * f * tt) * a for f, a in ((420, 1), (1130, 0.6), (2210, 0.3))) * np.exp(-tt * 9), 0.6)
    # soup: a sloshy splash (low-passed noise with a wobble)
    tt = t(0.6); n = np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(30) / 30, "same")
    save("soup", n * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * tt)) * np.exp(-tt * 4), 0.6)
    # traycrash: a stack of plastic trays clattering down (a run of short clacks)
    tt = t(0.9); x = np.zeros(len(tt))
    for k in range(11):
        i = int((0.05 + k * 0.07 + rng.uniform(0, 0.03)) * RATE); L = 700
        x[i:i + L] += rng.uniform(-1, 1, L) * np.exp(-np.arange(L) / 120) * (1 - k / 14)
    save("traycrash", x, 0.6)
    save("next", X.babble("NEXT!", random.Random(1417), pitch=0.85, speed=1.3), 0.8)
    save("lunchlady", X.babble("No substitutions!", random.Random(1415), pitch=0.85, speed=1.1), 0.7)
    save("lunchlady_ko", X.babble("Kitchen's... closed... zzz", random.Random(1416), pitch=0.75, speed=0.8), 0.7)


if __name__ == "__main__":
    build_music()
    build_sfx()
    print("ok")
