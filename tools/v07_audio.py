"""v0.7 sounds, without rebuilding older audio:

    python3 tools/v07_audio.py -> audio/sfx/{jerky,slam,toss}.wav
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

SUITE = Path("/workspace/n64-suite")
sys.path.insert(0, str(SUITE))
from n64.audio_util import write_wav  # noqa: E402

ROOT = Path(__file__).parent.parent
SFX = ROOT / "audio" / "sfx"
RATE = 22050


def t(d):
    return np.arange(int(d * RATE)) / RATE


def save(name, x, g=0.85):
    x = x / (np.abs(x).max() or 1) * g
    write_wav(SFX / f"{name}.wav", x, RATE)


def build():
    rng = np.random.default_rng(77)
    # jerky: a crinkly bag rip (bursts of filtered noise) and a chewy little "nom"
    tt = t(0.34)
    env = np.zeros_like(tt)
    for c in (0.0, 0.05, 0.09, 0.14):
        env += np.exp(-np.maximum(0, tt - c) * 60) * (tt >= c)
    crinkle = np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(3) / 3, "same") * env
    nt = tt - 0.2
    nom = np.sin(2 * np.pi * (180 + 60 * np.sin(2 * np.pi * 9 * nt)) * nt) * np.exp(-np.abs(nt - 0.05) * 30) * (nt > 0) * 0.7
    save("jerky", crinkle + nom, 0.8)
    # slam: an over-the-shoulder body slam (whoosh into a deep floor thud + rattle)
    tt = t(0.5)
    whoosh = np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(9) / 9, "same") * np.exp(-((tt - 0.12) / 0.07) ** 2) * 0.6
    st = tt - 0.2
    thud = (np.sin(2 * np.pi * (70 - 30 * np.minimum(1, st / 0.2)) * st) * np.exp(-st * 14) + rng.uniform(-1, 1, len(tt)) * np.exp(-st * 40) * 0.5) * (st > 0)
    save("slam", whoosh + thud, 0.9)
    # toss: a quick heave grunt-whoosh
    tt = t(0.25)
    toss = np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(5) / 5, "same") * np.sin(np.pi * np.minimum(1, tt / 0.25)) ** 2
    save("toss", toss + np.sin(2 * np.pi * 140 * tt) * np.exp(-tt * 18) * 0.3, 0.7)


if __name__ == "__main__":
    build(); print("wrote jerky, slam, toss")
