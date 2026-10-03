"""v0.4 sounds (numpy + suite babble, no music rebuild): beep (bed alarm), hiss (O2 tank valve), splat (jello),
fling (tray whoosh-clatter), charge (team-up shout "Charge nurse!" + brass hit), fanfare (bonus results), raid (snack rustle).

    python3 tools/v04_sfx.py   -> audio/sfx/{beep,hiss,splat,fling,charge,fanfare,raid}.wav
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "/workspace/n64-suite")
from n64.audio_util import write_wav  # noqa: E402
from n64 import sfx as X  # noqa: E402

RATE = 22050
OUT = Path(__file__).parent.parent / "audio" / "sfx"
NAMES = ("beep", "hiss", "splat", "fling", "charge", "fanfare", "raid")


def t(d):
    return np.arange(int(d * RATE)) / RATE


def save(name, x, g=0.85):
    x = x / (np.abs(x).max() or 1) * g
    write_wav(OUT / f"{name}.wav", x, RATE)


def sq(f, tt, duty=0.5):
    return np.where((tt * f) % 1 < duty, 1.0, -1.0)


def build():
    rng = np.random.default_rng(404)
    # beep: two-tone hospital bed alarm
    tt = t(0.32)
    b = np.where(tt < 0.14, sq(1760, tt, 0.5), 0) + np.where((tt > 0.17) & (tt < 0.31), sq(1320, tt, 0.5), 0)
    save("beep", b * 0.6, 0.45)
    # hiss: O2 valve venting, high-passed noise with a fade
    tt = t(0.9)
    n = rng.uniform(-1, 1, len(tt)); n = n - np.convolve(n, np.ones(6) / 6, "same")
    save("hiss", n * np.minimum(1, tt / 0.03) * np.exp(-tt * 2.6), 0.55)
    # splat: wet jello squelch, pitch-dropping blob + noise
    tt = t(0.3)
    sp = np.sin(2 * np.pi * np.cumsum(420 * np.exp(-tt * 18) + 70) / RATE) * np.exp(-tt * 14) + np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(12) / 12, "same") * np.exp(-tt * 16) * 2
    save("splat", sp, 0.75)
    # fling: whoosh + cutlery clatter
    tt = t(0.42)
    wh = np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(20) / 20, "same") * np.sin(np.pi * np.minimum(tt / 0.25, 1)) * 3
    cl = np.zeros_like(tt)
    for k in range(6):
        n0 = int(rng.uniform(0.02, 0.3) * RATE); ln = int(0.05 * RATE); f = rng.uniform(2500, 5200)
        seg = np.sin(2 * np.pi * f * np.arange(ln) / RATE) * np.exp(-np.arange(ln) / RATE * 80) * 0.4
        cl[n0:n0 + ln] += seg[: len(cl[n0:n0 + ln])]
    save("fling", wh + cl, 0.6)
    # charge: both nurses yell "Charge nurse!" (two pitches layered) over a brass stab + boom
    v1 = X.babble("Charge nurse!", random.Random(11), pitch=1.25, speed=1.15)
    v2 = X.babble("Charge nurse!", random.Random(12), pitch=0.9, speed=1.15)
    L = max(len(v1), len(v2)) + int(0.9 * RATE)
    out = np.zeros(L)
    out[: len(v1)] += v1 * 0.8; out[: len(v2)] += v2 * 0.7
    tt = t(L / RATE)
    stab = sum(np.sign(np.sin(2 * np.pi * f * tt)) * 0.18 for f in (262, 330, 392, 523)) * np.exp(-np.maximum(tt - 0.55, 0) * 3) * (tt > 0.55)
    boom = np.sin(2 * np.pi * np.cumsum(120 * np.exp(-np.maximum(tt - 0.55, 0) * 5) + 40) / RATE) * np.exp(-np.maximum(tt - 0.55, 0) * 4) * (tt > 0.55)
    save("charge", out + stab + boom * 0.8, 0.9)
    # fanfare: short chip "ta-da-daaa"
    notes = ((523, 0.12), (659, 0.12), (784, 0.12), (1047, 0.5))
    seq = np.concatenate([sq(f, t(d), 0.25) * np.exp(-t(d) * (2 if d > 0.3 else 6)) for f, d in notes])
    save("fanfare", seq, 0.5)
    # raid: crinkly snack-bag rustle
    tt = t(0.4)
    r = rng.uniform(-1, 1, len(tt)) * (rng.uniform(0, 1, len(tt)) > 0.82) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * tt) ** 2)
    save("raid", r, 0.4)


if __name__ == "__main__":
    build()
    print("v0.4 sfx:", sorted(p.name for p in OUT.glob("*.wav") if p.stem in NAMES))
