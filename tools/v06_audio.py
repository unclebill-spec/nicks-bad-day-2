"""v0.6 sounds, without rebuilding older audio:

    python3 tools/v06_audio.py -> audio/sfx/{ativan,defib,crackle,alarm,yell,sprinkler,stink}.wav
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


def t(d):
    return np.arange(int(d * RATE)) / RATE


def save(name, x, g=0.85):
    x = x / (np.abs(x).max() or 1) * g
    write_wav(SFX / f"{name}.wav", x, RATE)


def build():
    rng = np.random.default_rng(66)
    # (v0.7: the meat-stick "snap" became the BEEF JERKY bag rip in tools/v07_audio.py)
    # defib: the capacitor charging whine (rising) then a fat discharge thump
    tt = t(0.9); f = 600 + 2600 * np.minimum(1, tt / 0.6)
    whine = np.sin(2 * np.pi * np.cumsum(f) / RATE) * 0.35 * (tt < 0.62)
    th = np.maximum(0, tt - 0.62)
    thump = (np.sin(2 * np.pi * np.cumsum(90 * np.exp(-th * 6) + 30) / RATE) + rng.uniform(-1, 1, len(tt)) * np.exp(-th * 14) * 0.9) * (tt >= 0.62) * np.exp(-th * 5)
    save("defib", whine + thump, 0.9)
    # crackle: electric arcs (gated noise bursts + buzzy square)
    tt = t(0.7)
    gate = (rng.uniform(0, 1, len(tt) // 220 + 1) > 0.45).repeat(220)[:len(tt)]
    buzz = np.sign(np.sin(2 * np.pi * 120 * tt)) * 0.3
    save("crackle", (rng.uniform(-1, 1, len(tt)) * gate + buzz) * np.exp(-tt * 2.5), 0.75)
    # alarm: fire-alarm blare (two-tone square horn, 3 whoops) -- not too harsh
    tt = t(1.5); seg = (tt * 4).astype(int) % 2
    f = np.where(seg == 0, 880, 660)
    horn = np.sign(np.sin(2 * np.pi * np.cumsum(f) / RATE)) * 0.5 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / RATE) * 0.3
    save("alarm", horn * np.minimum(1, tt / 0.02) * np.minimum(1, (1.5 - tt) / 0.05), 0.6)
    # sprinkler: a soft hiss of water
    tt = t(1.2); n = np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(3) / 3, "same")
    save("sprinkler", n * np.minimum(1, tt / 0.15) * np.minimum(1, (1.2 - tt) / 0.3) * (0.8 + 0.2 * np.sin(2 * np.pi * 7 * tt)), 0.45)
    # stink: a wobbly "ew" for the old pizza
    tt = t(0.35); f = 300 - 120 * tt / 0.35
    save("stink", np.sin(2 * np.pi * np.cumsum(f + 25 * np.sin(2 * np.pi * 18 * tt)) / RATE) * np.exp(-tt * 4), 0.6)
    # voices (suite babble)
    for name, (txt, p, sp, seed) in {"ativan": ("It's time for some Ativan!", 1.15, 1.15, 81),
                                     "yell": ("FIRE! FIRE! FIRE!", 0.85, 1.25, 82),
                                     "clear": ("CLEAR!", 1.0, 1.0, 83)}.items():
        save(name, X.babble(txt, random.Random(seed), pitch=p, speed=sp), 0.75)


if __name__ == "__main__":
    build()
    print("ok")
