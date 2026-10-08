"""v0.13 audio for the PSYCH WARD, without rebuilding older audio:

    python3 tools/v13_audio.py -> audio/music/{psych,philin}.mp3 (+ loop points in music.json)
                                  audio/sfx/{buzzer,flicker,strap,lasso,croon,greg,philin,philin_ko}.wav
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
    "psych": ("overworld", 41, "haunted", 0.96),    # the ward: a woozy, slightly-off waltzy groove under flickering lights
    "philin": ("boss", 29, "haunted", 1.08),        # "DR." PHIL-IN
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
    rng = np.random.default_rng(1313)
    # buzzer: the locked ward door's harsh entry buzz (120 Hz square + odd harmonics), 0.6 s
    tt = t(0.6)
    save("buzzer", (sq(np.full(len(tt), 120.0)) * 0.6 + sq(np.full(len(tt), 360.0)) * 0.25) * np.minimum(1, (0.6 - tt) / 0.03), 0.4)
    # flicker: a fluorescent tube stuttering: hum bursts with clicks
    tt = t(0.7); on = (rng.uniform(0, 1, len(tt) // 400 + 1).repeat(400)[:len(tt)] > 0.45).astype(float)
    hum = np.sin(2 * np.pi * 120 * tt) * 0.5 + np.sin(2 * np.pi * 240 * tt) * 0.25 + rng.uniform(-1, 1, len(tt)) * 0.08
    clicks = np.zeros(len(tt)); clicks[np.abs(np.diff(on, prepend=0)) > 0] = 1.0
    save("flicker", hum * on + np.convolve(clicks, np.ones(40) / 6, "same"), 0.4)
    # strap: a soft restraint strap cracked like a whip (a fast noise snap)
    tt = t(0.25)
    save("strap", rng.uniform(-1, 1, len(tt)) * np.exp(-tt * 30) * (1 + np.sin(2 * np.pi * 900 * tt)), 0.55)
    # lasso: the stethoscope twirling (whoosh up-down) then a thwip
    tt = t(0.5); f = 300 + 500 * np.sin(np.pi * tt / 0.5)
    w = np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(12) / 12, "same") * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(f) / RATE))
    save("lasso", w * np.sin(np.pi * tt / 0.5), 0.5)
    # croon: GREG's synth crooner hum, "doo-be-doo-be-doo" (no real recording, no real melody): soft vibrato sine notes + a little brush
    notes = [(392, 0.22), (440, 0.18), (392, 0.18), (330, 0.18), (392, 0.5)]
    out = []
    for f0, d in notes:
        tt = t(d); f = f0 * (1 + 0.012 * np.sin(2 * np.pi * 5.5 * tt))
        ph = 2 * np.pi * np.cumsum(f) / RATE
        v = (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)) * np.minimum(1, tt / 0.03) * np.minimum(1, (d - tt) / 0.05)
        out.append(v)
    c = np.concatenate(out); c = c + np.convolve(rng.uniform(-1, 1, len(c)), np.ones(60) / 60, "same") * 0.3
    save("croon", c, 0.5)
    # voices (suite babble)
    save("greg", X.babble("Wanna get outta here?", random.Random(1314), pitch=0.75, speed=0.85), 0.7)
    save("philin", X.babble("I'm the doctor here!", random.Random(1315), pitch=0.95, speed=1.15), 0.7)
    save("philin_ko", X.babble("Discharge... me... zzz", random.Random(1316), pitch=0.8, speed=0.8), 0.7)


if __name__ == "__main__":
    build_music()
    build_sfx()
    print("ok")
