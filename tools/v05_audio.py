"""v0.5 audio: three new chiptune tracks (Radiology stage, MRI boss, Night Shift) and the new sounds, without
rebuilding the v0.1-v0.4 audio. Merges loop points into audio/music/music.json.

    python3 tools/v05_audio.py   -> audio/music/{radiology,mri,night}.mp3 + audio/sfx/{hum,bang,quench,table,powerdown,click,lightsout,film,stomp,clunk}.wav
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
    "radiology": ("overworld", 9, "frost", 0.92),   # cold dorian, a notch slower than Floor 3
    "mri": ("boss", 8, "frost", 1.0),
    "night": ("dungeon", 6, "haunted", 1.3),        # sparse and spooky, but brisk enough to fight to
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


def build_sfx():
    rng = np.random.default_rng(55)
    # hum: the magnet spinning up (rising buzzy drone with a 2nd harmonic wobble)
    tt = t(1.2); f = 60 + 50 * np.minimum(1, tt / 0.8)
    hum = np.sign(np.sin(2 * np.pi * np.cumsum(f) / RATE)) * 0.35 + np.sin(2 * np.pi * np.cumsum(f * 2.01) / RATE) * 0.5 * (1 + 0.3 * np.sin(2 * np.pi * 9 * tt))
    save("hum", hum * np.minimum(1, tt / 0.1) * np.minimum(1, (1.2 - tt) / 0.15), 0.6)
    # bang: the MRI's famous knock (square thud + metallic ring)
    tt = t(0.28)
    body = np.sign(np.sin(2 * np.pi * np.cumsum(90 * np.exp(-tt * 10) + 50) / RATE)) * np.exp(-tt * 16)
    ringm = sum(np.sin(2 * np.pi * fq * tt) * np.exp(-tt * d) for fq, d in ((410, 14), (987, 20)))
    save("bang", body + ringm * 0.4 + rng.uniform(-1, 1, len(tt)) * np.exp(-tt * 70) * 0.6, 0.85)
    # quench: a huge cold helium whoosh
    tt = t(1.3); n = rng.uniform(-1, 1, len(tt))
    sw = np.convolve(n, np.ones(4) / 4, "same") * np.minimum(1, tt / 0.05) * np.exp(-tt * 1.6)
    save("quench", sw + np.sin(2 * np.pi * np.cumsum(900 - 500 * tt) / RATE) * 0.15 * np.exp(-tt * 3), 0.7)
    # table: patient table sliding out on rails (rattly motor)
    tt = t(0.7); f = 140 + 120 * tt
    save("table", (np.sign(np.sin(2 * np.pi * np.cumsum(f) / RATE)) * 0.3 + rng.uniform(-1, 1, len(tt)) * 0.25 * (np.sin(2 * np.pi * 30 * tt) > 0)) * np.minimum(1, (0.7 - tt) / 0.1), 0.55)
    # powerdown: falling sine sweep (machine winding down)
    tt = t(1.6)
    save("powerdown", np.sin(2 * np.pi * np.cumsum(520 * np.exp(-tt * 1.8) + 30) / RATE) * np.minimum(1, (1.6 - tt) / 0.3), 0.6)
    # click: flashlight switch
    tt = t(0.05)
    save("click", rng.uniform(-1, 1, len(tt)) * np.exp(-tt * 300) + np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt * 200), 0.6)
    # lightsout: a big breaker clunk + the hum dying
    tt = t(1.0)
    clunk = np.sin(2 * np.pi * np.cumsum(70 * np.exp(-tt * 6) + 30) / RATE) * np.exp(-tt * 9)
    dying = np.sign(np.sin(2 * np.pi * np.cumsum(120 * np.exp(-tt * 2.5)) / RATE)) * 0.25 * np.exp(-tt * 2.2)
    save("lightsout", clunk + dying + rng.uniform(-1, 1, len(tt)) * np.exp(-tt * 40) * 0.5, 0.85)
    # film: an X-ray film sheet wobbling through the air (warbly whoosh)
    tt = t(0.4); n = np.convolve(rng.uniform(-1, 1, len(tt)), np.ones(5) / 5, "same")
    save("film", n * (0.6 + 0.4 * np.sin(2 * np.pi * 22 * tt)) * np.exp(-((tt - 0.15) / 0.12) ** 2), 0.5)
    # stomp: mini-boss ground pound
    tt = t(0.5)
    save("stomp", np.sin(2 * np.pi * np.cumsum(60 * np.exp(-tt * 5) + 25) / RATE) * np.exp(-tt * 6) + rng.uniform(-1, 1, len(tt)) * np.exp(-tt * 18) * 0.7, 0.9)
    # clunk: metal stuck to the magnet
    tt = t(0.35)
    save("clunk", sum(np.sin(2 * np.pi * fq * tt) * np.exp(-tt * d) for fq, d in ((240, 12), (530, 16), (1210, 24))) + rng.uniform(-1, 1, len(tt)) * np.exp(-tt * 90) * 0.8, 0.8)
    # voices (suite babble)
    for name, (txt, p, sp, seed) in {"mri_voice": ("Please hold still. Scanning!", 0.7, 1.0, 71), "lou": ("Hut hut HIKE!", 0.6, 1.0, 72),
                                     "scared": ("Who turned off the lights?", 1.4, 1.2, 73)}.items():
        save(name, X.babble(txt, random.Random(seed), pitch=p, speed=sp), 0.7)


if __name__ == "__main__":
    build_music()
    build_sfx()
    print("ok")
