# AGENTS.md: Nick's Very Bad, Terrible Bad Day Part II

Handoff notes for any builder (Cursor reads this file automatically, and so do Bill's bots). Keep this file and
`CHANGELOG.md` current before every commit and push. **Pull first** when you resume work.

## What it is
A 1990s arcade beat 'em up in the spirit of Golden Axe and the TMNT and Simpsons arcade games. Four nurses fight
their way through hospital floors full of comedic patients. Plain HTML5 Canvas 2D plus ES modules. No build step
and no dependencies at runtime. Live on GitHub Pages: https://unclebill-spec.github.io/nicks-bad-day-2/

## Current state (2026-10-03, v0.2.1)
- **Level 1 "Floor 3: Med-Surg" is fully playable** from the title screen through to the tally and the "Floor 4: Radiology" teaser.
  The level is 3560 px wide with 6 camera-lock zones: 5 wave zones, then the boss dayroom.
- **4 heroes:**
  - Nick: balanced, Crash Cart special.
  - Kim: fast, Whirlwind Kick.
  - Will: power, Body Slam, big throws. He is bald (skin-tone head with a shine) in a plain bright blue shirt, and his stat color is blue; there's no orange or Halloween look anywhere.
  - Jackie: reach, Clipboard Spin, strong jump and dash.
- **Moves:** combos with a finisher, jump and jump kick, run (double-tap or Shift/RB) and dash attack, back attack (Attack+Jump),
  auto-grab, then knee or throw (throws hit other patients), a special that costs 8 HP, and the Code Blue super when the meter is full.
- **Patients:** all wear checked hospital gowns (pale green or faded olive) with yellow grip socks, and get random hair and skin at runtime.
  - Types: Wanderer (hugs), Call-light Spammer (throws remotes and pudding), Escape Artist (slaps and runs), IV-pole Swinger (sweeps),
    Sundowner (charges), Crutch Crusader (crutch poke), and Bell Ringer (call bell on a cord, whip that dizzies).
  - **Elite "Frequent Flyer":** beehive with curlers, red or blue socks, a cane up close, and from range syringe darts or lobbed urinals that splash and leave a slippery puddle.
  - The Belligerent Visitor is an armored brute in a tracksuit; he's a visitor, so no gown.
  - Each has its own KO line and falls asleep or gets tucked in. Crutch, bell and elite patients may drop their weapon.
- **Spawns** come in waves with an on-screen cap, from hallway room doors (301–314), from the elevators (B, C), and from both screen edges.
- **Pickups:** energy drink (small heal), fruit snacks (big heal), candy (speed), the ZYNN tin (+1 life; parody label, never the real logo), and score items (donut, gold star).
- **Weapons:** clipboard, bedpan, mop, IV pole, crutch, call bell (dizzies), cane, and an extinguisher that sprays and stuns.
- **Breakables:** med cart, linen bin, vending machine and IV stand.
- **Boss: Turbo Tilly** in an electric wheelchair.
  - Phase 1: horn honk shock ring (dizzies), rev and charge. After a charge her battery panel opens as the weak point; she takes only 30% damage otherwise.
  - Phase 2 (turbo): faster charges, drops puddles and yarn, and calls patients for backup.
- **Flow:** title, 1P/2P select, stage intro, waves, boss, tally, teaser. Continues (3 / 5 / free play), lives,
  top-5 high scores, and settings saved in localStorage (`nbd2.save`, `nbd2.display`, `nbd2.input`).
- **Local 2-player co-op:**
  - Split keyboard: P1 uses WASD + H/J/K/L, P2 uses arrows + M , . /
  - Or keyboard + pad, or two pads.
  - P2 can drop in mid-game by pressing Start on another device.
- **Bill's required features:**
  - Fullscreen button at the far left (also the ` key, or Start+Select on a pad).
  - Sideways-phone layout with a rotate prompt.
  - Display presets: Auto, Phone, 720p, 1080p, Retro 320x240 (forces 4:3), plus Fit / 16:9 / 4:3.
  - Install app button in Settings (iPhone shows the Add to Home Screen steps).
  - PWA manifest and service worker.
  - Chiptune music and SFX, with music and SFX volume.

## Run it
```bash
cd /workspace/games/nicks-bad-day-2
python3 -m http.server 8731          # then open http://localhost:8731/
```
Debug query params:
- `?autostart=1&hero=kim` skips the menus.
- `?zone=5` jumps to the boss (zones 0–5; 2 is the elevator bank).
- `?god=1` keeps P1 at full HP.
- `?bot=1` lets a simple bot drive P1 (used for tests and GIFs).

Tests (Playwright + Chromium; the server must be running):
```bash
python3 tests/smoke.py      # desktop keyboard: title, select, first fight
python3 tests/moves.py      # every hero: jump, kick, special cost, super, run/dash, weapon pickup + swing
python3 tests/pad.py        # mocked gamepad: menus, select, move, attack, pause; 2P keyboard + pad
python3 tests/touch.py      # emulated Pixel phone landscape: taps, floating joystick, buttons, pause, rotate prompt
python3 tests/flow.py       # boss defeat -> tally -> teaser -> title; continue; game over -> high scores
python3 tests/will.py       # Will's look on title, select, in-game HUD, tally
python3 tests/patients.py   # all patient types + random looks, elite syringe/urinal throws, splash + puddle, KO drops, new pickups
python3 tests/before_after.py <old art dir> docs/art_before_after.png   # art comparison sheet
python3 tests/shots.py "autostart=1&bot=1&god=1" 240 full 1280 720 6   # whole level with the bot
python3 tests/video.py      # webm clips for the GIF (ffmpeg converts)
```
Screenshots go to `tests/out/`, which is git-ignored. `docs/screenshots.png` and `docs/gameplay.gif` are committed copies.

## Rebuilding art and audio
- Patient looks: `tools/chars.py` has `GOWN`, `GOWN_OLIVE`, `SOCK`, `SOCK_ELITE` and `HAIRS`. `make_art.py` writes them to `atlas.json`
  (`chars.<patient>.pal` and `palettes`), and the game swaps those exact colors per spawn (a pool of 6 looks per type).
  If you add a patient, give it `**gown` and `**socks`, and add it to `PATIENTS` in `make_art.py`.
- `python3 tools/make_art.py` rewrites `art/*.png`, `art/atlas.json`, the font and the icons.
  - `tools/rig.py` is the side-view pixel puppet rig. `tools/chars.py` holds the heroes and patients, `tools/boss.py` Tilly, and `tools/props.py` the hospital art.
  - It uses vendored copies of Master Builder's Gravewake `sprite_writer`/`pixel_writer` and brileta-sprites (plants, via node).
  - Never edit `/workspace/gravewake` itself. It belongs to another bot.
- `python3 tools/make_audio.py` rewrites `audio/music/*.mp3` (with loop points in `music.json`) and `audio/sfx/*.wav`, using the N64 suite in `/workspace/n64-suite` (music.compose with the chiptune fallback, sfx.make, babble).
- All art is original. There are no copyrighted characters or sprites.

## Code layout
| File | What it does |
|---|---|
| `index.html`, `src/style.css` | DOM HUD (fullscreen button, touch joystick zone, buttons, pause + clock row), loading gate |
| `src/main.js` | boot, fixed 60 Hz loop + hit-stop, scenes, canvas menus (pause/settings/how-to), saves, display presets, test hooks (`window.__nbd`) |
| `src/gfx.js` | low-res buffer canvas scaled up crisply; sprites, sheets, bitmap text, panels |
| `src/sound.js` | WebAudio music with loop points and SFX; unlocks on first gesture |
| `src/controls.js` | devices `kb`/`kb1`/`kb2`/`padN`/`touch` → per-player input, double-tap run, menu intents |
| `kit/input.js`, `kit/display.js` | copied unchanged from the N64 suite's Mossgnome runtime (pad detection, display presets, fullscreen, install, rotate prompt); `kit/common.js` is a 2D shim |
| `src/data.js` | heroes, attacks, weapons, items, enemies, difficulty, `LEVEL1` layout + zones/waves |
| `src/world.js` | world state `W`, background pre-render, doors/elevators, props/items/shots/fx, camera (no scrolling back) |
| `src/actor.js`, `src/hero.js`, `src/enemy.js`, `src/boss.js` | actor base + `strike()` hit logic, hero state machine, patient AI, Turbo Tilly |
| `src/stage.js` | Director: zone triggers, camera locks, wave queue with cap, GO arrow, boss start/backup, projectiles |
| `src/hud.js` | portraits, HP/meter, lives, score, combo, last-hit foe bar, boss bar, toasts, continue prompts |
| `sw.js`, `app.webmanifest`, `icons/` | PWA (cache name `nbd2-app-vN`: **bump N on every release**) |

## Bill's standing preferences
- Brief, plain replies, with times in ET. He often uses voice-to-text, so read his messages generously.
- Every web game needs: a fullscreen button at the far left, a sideways-phone layout, display presets,
  an in-game Install app button (Add to Home Screen steps on iPhone), touch + gamepad + keyboard, and saves.
- He likes "gloom and glow" neon (blue cold fire, violet, red) for night or mystic scenes. Portal references are in `/workspace/gravewake/style/rift_refs`.
- The tone of this game is comedic and never mean toward patients: they get tucked in, fall asleep, and so on.
- Every repo needs a CHANGELOG.md (dated), descriptive commits, and this AGENTS.md. Run the secret scan before every push:
  `python3 /workspace/scratch/sec/scan.py history` and `... tree` from the repo root. Abort on any finding.
- Don't modify other bots' projects; copy what you need.

## Known issues / caveats
- Tested on emulated phones (Chromium, Pixel-size landscape) and desktop Chromium with a mocked gamepad. It has not been tested on real iPhone or Android hardware yet.
- The heroes' skin tones and hair styles were guessed from Bill's short descriptions (they may be real coworkers). They are easy to change in `tools/chars.py` `bodies()`, followed by `python3 tools/make_art.py`.
- Only Level 1 exists. The teaser points to Floor 4: Radiology.
- Balance is first-pass: Tilly has 420 HP and patient damage scales by difficulty in `DIFF`. The elite waves make zones 2–4 noticeably harder.
- The gown check pattern is drawn on a fixed pixel grid, so it doesn't move with the body. It shimmers very slightly during animation.
- Online co-op is not implemented. That was optional in the spec.

## Next steps
1. Bill plays on his phone and gives feedback on feel, difficulty and hero looks.
2. Level 2 (Radiology), with new patient types, a new boss, and an X-ray hallway gimmick.
3. Character voice barks, plus an attract-mode demo on the title screen using the bot.
4. More stages per the spec: lobby/ER, ICU, cafeteria, roof helipad.
