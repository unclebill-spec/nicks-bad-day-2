"""v0.8 sounds, without rebuilding older audio:

    python3 tools/v08_audio.py -> audio/sfx/{ativan_nate,yawn}.wav
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

SUITE = Path("/workspace/n64-suite")
sys.path.insert(0, str(SUITE))
from n64 import sfx as X  # noqa: E402
from n64.audio_util import write_wav  # noqa: E402

ROOT = Path(__file__).parent.parent
SFX = ROOT / "audio" / "sfx"
RATE = 22050


def save(name, x, g=0.85):
    x = x / (np.abs(x).max() or 1) * g
    write_wav(SFX / f"{name}.wav", x, RATE)


def build():
    # Nate's lazy Ativan line: lower, slower, trailing off
    save("ativan_nate", X.babble("Ugh... it's time for some Ativan.", random.Random(91), pitch=0.78, speed=0.72), 0.75)
    # a big lazy yawn: a falling, breathy vowel
    tt = np.arange(int(0.9 * RATE)) / RATE
    f = 260 - 130 * tt / 0.9
    v = np.sin(2 * np.pi * np.cumsum(f) / RATE) + 0.5 * np.sin(4 * np.pi * np.cumsum(f) / RATE)
    n = np.random.default_rng(92).uniform(-1, 1, len(tt)) * 0.35
    env = np.minimum(1, tt / 0.2) * np.minimum(1, (0.9 - tt) / 0.35)
    save("yawn", (v * 0.7 + n) * env, 0.5)


if __name__ == "__main__":
    build()
    print("ok")
