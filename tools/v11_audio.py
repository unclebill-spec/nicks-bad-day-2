"""v0.11 audio for the PARKING GARAGE AT SHIFT CHANGE, without rebuilding older audio:

    python3 tools/v11_audio.py -> audio/music/{garage,valet}.mp3 (+ loop points in music.json)
                                  audio/sfx/{carhorn,caralarm,screech,rev,keys,meep,valet,valet_ko}.wav
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
    "garage": ("overworld", 23, "haunted", 1.12),   # a moody, driving street-level groove for the dawn garage
    "valet": ("boss", 13, "frost", 1.05),           # VINNIE THE VALET
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
    rng = np.random.default_rng(1111)
    # carhorn: a two-tone sedan horn (a minor third, slightly detuned square + saw), held ~0.5 s
    tt = t(0.5); env = np.minimum(1, tt / 0.01) * np.minimum(1, (0.5 - tt) / 0.04)
    h = sq(np.full(len(tt), 392.0)) * 0.5 + sq(np.full(len(tt), 466.0)) * 0.5 + np.sin(2 * np.pi * 784 * tt) * 0.2
    save("carhorn", np.convolve(h, np.ones(4) / 4, "same") * env, 0.55)
    # caralarm: the classic WEE-OO: a siren sweep up/down twice, then three chirps
    tt = t(1.2); f = 900 + 600 * np.abs(((tt * 2.5) % 2) - 1)
    a = sq(f) * 0.5 + np.sin(2 * np.pi * np.cumsum(f) / RATE) * 0.4
    t2 = t(0.45); ch = sq(np.full(len(t2), 1500.0)) * ((t2 % 0.15) < 0.08) * 0.6
    save("caralarm", np.concatenate([a, ch]) * 0.9, 0.42)
    # screech: tyres squealing on concrete (wobbling high squeal + hiss), longer than the scooter skid
    tt = t(0.8); f = 2100 + 220 * np.sin(2 * np.pi * 13 * tt) - 400 * tt
    s = sq(f) * 0.22 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / RATE) * 0.3
    save("screech", (s + rng.uniform(-1, 1, len(tt)) * 0.3) * np.minimum(1, tt / 0.03) * np.exp(-tt * 2.2), 0.45)
    # rev: an engine revving up (low saw rising, with a rumble)
    tt = t(0.9); f = 55 + 110 * (tt / 0.9) ** 1.5
    saw = 2 * ((np.cumsum(f) / RATE) % 1) - 1
    rum = np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(30) / 30, "same") * 2
    save("rev", (saw * 0.7 + rum * 0.5) * np.minimum(1, tt / 0.05) * np.minimum(1, (0.9 - tt) / 0.15), 0.6)
    # keys: a key ring jingling (short bright metallic pings)
    out = np.zeros(int(0.35 * RATE))
    for k in range(7):
        st = int(rng.uniform(0, 0.25) * RATE); n = int(0.08 * RATE); tt = np.arange(n) / RATE
        f = rng.uniform(3200, 5200)
        out[st:st + n] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 60) * 0.5
    save("keys", out, 0.5)
    # meep: the golf cart's little horn (two high toots)
    tt = t(0.32); on = ((tt % 0.16) < 0.11).astype(float)
    save("meep", (sq(np.full(len(tt), 880.0)) * 0.6 + np.sin(2 * np.pi * 1320 * tt) * 0.3) * on, 0.45)
    # VINNIE THE VALET's voice (suite babble): the taunt and the KO
    save("valet", X.babble("Ticket's validated... NOT!", random.Random(1112), pitch=0.9, speed=1.1), 0.7)
    save("valet_ko", X.babble("Keep... the change... zzz", random.Random(1113), pitch=0.8, speed=0.8), 0.7)


if __name__ == "__main__":
    build_music()
    build_sfx()
    print("ok")
