"""v0.9 audio for the SCOOTER RUN, without rebuilding older audio:

    python3 tools/v09_audio.py -> audio/music/scooter.mp3 (+ loop points in music.json)
                                  audio/sfx/{pew,skid,scoot,beepbeep,marv,marv_ko}.wav
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


def build_music():
    """A bright, fast 'overworld' chiptune for the scooter chase (ember theme, pushed to ~165 bpm)."""
    loops = json.loads((MUS / "music.json").read_text())
    name, k = "scooter", 1.25
    song, info = M.compose("overworld", 11, "ember")
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


def build_sfx():
    rng = np.random.default_rng(909)
    # pew: an Ativan syringe flicked off the scooter (short pneumatic "thwip" + a rising glint)
    tt = t(0.16)
    air = np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(3) / 3, "same") * np.exp(-tt * 40)
    save("pew", air * 0.8 + np.sin(2 * np.pi * np.cumsum(900 + 2600 * tt / 0.16) / RATE) * 0.5 * np.exp(-tt * 22), 0.6)
    # skid: tyres squealing on hospital linoleum (a wobbling high squeal over hiss)
    tt = t(0.55); f = 1900 + 160 * np.sin(2 * np.pi * 17 * tt)
    sq = np.sign(np.sin(2 * np.pi * np.cumsum(f) / RATE)) * 0.25 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / RATE) * 0.3
    save("skid", (sq + rng.uniform(-1, 1, len(tt)) * 0.35) * np.minimum(1, tt / 0.03) * np.exp(-tt * 3.2), 0.5)
    # scoot: the little electric motor revving up (rising whine)
    tt = t(0.6); f = 180 + 520 * (tt / 0.6) ** 0.7
    wh = np.sin(2 * np.pi * np.cumsum(f) / RATE) + 0.4 * np.sign(np.sin(2 * np.pi * np.cumsum(f * 0.5) / RATE))
    save("scoot", wh * np.minimum(1, tt / 0.05) * np.minimum(1, (0.6 - tt) / 0.12), 0.45)
    # beepbeep: the mobility-scooter reversing beeper (two square beeps)
    tt = t(0.42); on = ((tt % 0.21) < 0.13).astype(float)
    save("beepbeep", np.sign(np.sin(2 * np.pi * 1320 * tt)) * on * 0.5, 0.45)
    # Marv's voice lines (suite babble): the taunt and the KO
    save("marv", X.babble("Eat my exhaust, nurses!", random.Random(93), pitch=0.85, speed=1.15), 0.7)
    save("marv_ko", X.babble("Out of... battery... zzz", random.Random(94), pitch=0.8, speed=0.8), 0.7)


if __name__ == "__main__":
    build_music()
    build_sfx()
    print("ok")
