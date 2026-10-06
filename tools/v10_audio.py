"""v0.10 sounds for Heather, without rebuilding older audio:

    python3 tools/v10_audio.py -> audio/sfx/{ativan_heather,huff,clothesline}.wav
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
    # Heather's Ativan call: brisk, a little higher, clipped ("No more Dilaudid. Here's your Ativan.")
    save("ativan_heather", X.babble("No more Dilaudid. Here's your Ativan.", random.Random(1010), pitch=1.12, speed=1.18), 0.75)
    # an annoyed huff: a short breathy burst that falls in pitch, then a tongue click ("tsk")
    tt = np.arange(int(0.55 * RATE)) / RATE
    f = 300 - 160 * tt / 0.55
    v = np.sin(2 * np.pi * np.cumsum(f) / RATE) * 0.35
    n = np.random.default_rng(1011).uniform(-1, 1, len(tt))
    env = np.minimum(1, tt / 0.04) * np.exp(-tt * 5.5)
    huff = (v + n * 0.9) * env
    k = np.zeros(int(0.12 * RATE)); k[int(0.06 * RATE):int(0.06 * RATE) + 60] = np.random.default_rng(1012).uniform(-1, 1, 60) * np.linspace(1, 0, 60)
    save("huff", np.concatenate([huff, k]), 0.5)
    # the clothesline: a fast rising whoosh of air
    tt = np.arange(int(0.45 * RATE)) / RATE
    n = np.random.default_rng(1013).uniform(-1, 1, len(tt))
    sm = np.convolve(n, np.ones(6) / 6, mode="same")
    swirl = np.sin(2 * np.pi * np.cumsum(180 + 900 * tt / 0.45) / RATE) * 0.25
    env = np.minimum(1, tt / 0.18) * np.minimum(1, (0.45 - tt) / 0.12)
    save("clothesline", (sm * 1.4 + swirl) * env, 0.7)


if __name__ == "__main__":
    build()
    print("ok")
