"""v0.16 audio for the ROOFTOP HELIPAD, without rebuilding older audio:

    python3 tools/v16_audio.py -> audio/music/{roof,lifeflight}.mp3 (+ loop points in music.json)
                                  audio/sfx/{rotor,gust,vape,drone,radio,roxy,roxy_ko,duke,ace}.wav
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
    "roof": ("overworld", 81, "frost", 0.96),     # the rooftop at night: a windy synth groove
    "lifeflight": ("boss", 83, "haunted", 1.16),    # the rogue LIFE FLITE crew
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
    rng = np.random.default_rng(1616)
    # rotor: chopper blades, a low noise thump chopped at ~11 Hz (loopable-ish, 1.2s)
    tt = t(1.2); n = np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(30) / 30, "same")
    chop = 0.25 + 0.75 * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * tt)) ** 3
    save("rotor", (n + np.sin(2 * np.pi * 70 * tt) * 0.4) * chop, 0.7)
    # gust: a big rising + falling wind whoosh
    tt = t(1.4); n = np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(14) / 14, "same")
    save("gust", n * np.sin(np.pi * tt / 1.4) ** 2, 0.6)
    # vape: a long soft exhale hiss
    tt = t(0.6); save("vape", np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(4) / 4, "same") * np.sin(np.pi * tt / 0.6) * 0.8, 0.45)
    # drone: a whiny little quad-copter buzz
    tt = t(0.5); save("drone", sq(420 + 30 * np.sin(2 * np.pi * 9 * tt)) * 0.3 * np.minimum(1, tt * 30) * np.exp(-tt * 2), 0.45)
    # radio: a squelch blip + static ("over!")
    tt = t(0.35); save("radio", np.concatenate([np.sin(2 * np.pi * 1200 * t(0.06)) * 0.5, rng.uniform(-1, 1, len(tt)) * 0.4 * np.exp(-tt * 6)]), 0.5)
    save("roxy", X.babble("Clear the pad!", random.Random(1617), pitch=1.15, speed=1.1), 0.7)
    save("roxy_ko", X.babble("Off shift... wake me at seven", random.Random(1618), pitch=1.0, speed=0.8), 0.7)
    save("duke", X.babble("Bag's heavy!", random.Random(1619), pitch=0.85, speed=1.0), 0.7)
    save("ace", X.babble("Ace here, buzzing the tower!", random.Random(1620), pitch=0.9, speed=1.2), 0.7)


if __name__ == "__main__":
    build_music()
    build_sfx()
    print("ok")
