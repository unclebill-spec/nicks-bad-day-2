"""v0.3 prop sounds (numpy, no music rebuild needed): crash (cart/chair breaks apart), rattle (casters rolling),
thunk (plastic / light hit), shatter (ceramic pot). Run standalone or from make_audio.py.

    python3 tools/prop_sfx.py   -> audio/sfx/{crash,rattle,thunk,shatter}.wav
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "/workspace/n64-suite")
from n64.audio_util import write_wav  # noqa: E402

RATE = 22050
OUT = Path(__file__).parent.parent / "audio" / "sfx"


def t(d):
    return np.arange(int(d * RATE)) / RATE


def save(name, x, g=0.85):
    x = x / (np.abs(x).max() or 1) * g
    write_wav(OUT / f"{name}.wav", x, RATE)


def build():
    rng = np.random.default_rng(31)
    # crash: low body thump + metallic partials + a scatter of little clinks (drawers, supplies)
    tt = t(0.75)
    thump = np.sin(2 * np.pi * np.cumsum(90 * np.exp(-tt * 10) + 35) / RATE) * np.exp(-tt * 9)
    metal = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) for f, d in ((410, 9), (980, 11), (1730, 14), (2610, 18))) * 0.35
    noise = rng.uniform(-1, 1, len(tt)) * np.exp(-tt * 12) * 0.8
    clinks = np.zeros_like(tt)
    for k in range(9):
        n0 = int((0.08 + rng.uniform(0, 0.55)) * RATE); f = rng.uniform(1800, 4200); ln = int(0.06 * RATE)
        seg = np.sin(2 * np.pi * f * np.arange(ln) / RATE) * np.exp(-np.arange(ln) / RATE * 70) * rng.uniform(0.2, 0.5)
        clinks[n0:n0 + ln] += seg[: len(clinks[n0:n0 + ln])]
    save("crash", thump + metal + noise + clinks, 0.9)
    # rattle: casters on linoleum, bumpy filtered noise with a 22 Hz wobble
    tt = t(0.5)
    r = np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(9) / 9, "same") * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 22 * tt)))
    save("rattle", r * np.minimum(1, tt / 0.02) * np.exp(-tt * 3), 0.45)
    # thunk: hollow plastic knock
    tt = t(0.18)
    th = np.sin(2 * np.pi * np.cumsum(260 * np.exp(-tt * 14) + 90) / RATE) * np.exp(-tt * 28) + rng.uniform(-1, 1, len(tt)) * np.exp(-tt * 90) * 0.4
    save("thunk", th, 0.75)
    # shatter: ceramic pot, bright noise burst + falling shards
    tt = t(0.55)
    sh = rng.uniform(-1, 1, len(tt)) * np.exp(-tt * 10)
    sh = sh - np.convolve(sh, np.ones(4) / 4, "same")  # high-pass-ish
    for k in range(7):
        n0 = int(rng.uniform(0.05, 0.45) * RATE); ln = int(0.04 * RATE)
        seg = rng.uniform(-1, 1, ln) * np.exp(-np.arange(ln) / RATE * 90) * 0.6
        sh[n0:n0 + ln] += seg[: len(sh[n0:n0 + ln])]
    save("shatter", sh + np.sin(2 * np.pi * 140 * tt) * np.exp(-tt * 20) * 0.6, 0.8)


if __name__ == "__main__":
    build()
    print("prop sfx:", sorted(p.name for p in OUT.glob("*.wav") if p.stem in ("crash", "rattle", "thunk", "shatter")))
