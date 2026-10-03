# AGENTS.md: Nick's Very Bad, Terrible Bad Day Part II

Handoff notes for any builder (Cursor reads this file automatically, and so do Bill's bots). Keep this file and
`CHANGELOG.md` current before every commit and push. **Pull first** when you resume work.

## What it is
A 1990s arcade beat 'em up in the spirit of Golden Axe and the TMNT and Simpsons arcade games. Four nurses fight
their way through hospital floors full of comedic patients. Plain HTML5 Canvas 2D plus ES modules. No build step
and no dependencies at runtime. Live on GitHub Pages: https://unclebill-spec.github.io/nicks-bad-day-2/

## Current state (2026-10-03, v0.5)
- **A full shift is playable, start to finish:** Level 1 "Floor 3: Med-Surg" (Turbo Tilly) → Breakroom Bonus → comic cutscene →
  Level 2 "Floor 4: Radiology" (Lead-Apron Lou mini-boss, MAGNA-SCAN 3000 MRI boss) → cutscene → Level 3 "Night Shift" → ending
  cutscene → THE END screen → high scores. Score, lives, meter, continues used and 2P carry from floor to floor (`loadLevel(idx)` in main.js).
  Level 1 is 3560 px wide with 6 camera-lock zones: 5 wave zones, then the boss dayroom.
- **Level 2 "Floor 4: Radiology" (v0.5, `LEVEL2` in data.js):** 3500 px, 6 zones (waves, X-RAY, IMAGING WAITING = Lou, waves, waves, MRI SUITE).
  - **Look:** dark slate tiles (`rwall`/`rceil`/`rfloor`), `W.dark = 0.5`, lit by neon-blue X-ray lightboxes (chest, hand, skull, rubber duck),
    blinking red "IN USE" warning lamps, violet MRI sign. The lights come from wall pieces (`GLOW` table in world.js) plus glowing props and the MRI bore.
  - **Props:** lead-apron racks (`apronrack`), contrast carts (`contrastcart`, glow amber, zap), film viewers (`viewer`, glow blue), wheelchairs, gurneys,
    IV stands, crash carts. All use the v0.3 kick/break system. `metal: true` marks what the MRI magnet pulls (props and weapons).
  - **Patients:** Contrast Chugger (`barium`, `ai:'tray'`, lobs barium cups `p_cup` → white chalky puddle `puddle_w`), Lead-Apron Hugger
    (`apron`, `ai:'wanderer'`, armor 2: shrugs off two jabs). `d.ai` lets a new patient reuse an AI; `e.kind` is the AI, `e.type` the patient id.
  - **Mini-boss: LEAD-APRON LOU** (`Lou` in `src/mri.js`), ~133 px tall = **2.2x a nurse**. Telegraphed three-point stance → linebacker charge →
    winded (`tired`, the weak point: full damage; 40% otherwise, no flinch). Stomp shock ring, X-ray film frisbees (`p_film`). Phase 2 at half HP
    ("FOURTH QUARTER! HIKE!") calls 2 helpers. Zone has `mini:true` (no cutscene); when beaten he is moved to `W.decor` (naps as scenery) and the zone opens.
  - **Boss: MAGNA-SCAN 3000** (`MRI` in `src/mri.js`), a front-view MRI machine with a live LCD face. **Size: 2.5x a nurse's height, 6.6x her width,
    23x her area.** Bill's rule is 5x; a 5x-tall boss (~280 px) can't fit the 224 px screen, so it is ≥5x by area/width and as tall as fits.
    It is solid across the whole floor depth (`depthAny`, `front`). Rotation: MAGNET ON (pulls nurses 50 px/s, yanks metal weapons out of
    hands, drags floor weapons and metal props in; props hurt nurses on the way and smash on the magnet; touching the face zaps) → QUENCH vent
    (**weak point**: full damage, otherwise 20%) → KNOCK sound waves along lanes (jump/dodge) → TABLE shot down your lane after a red flash (jump).
    Phase 2 (half HP, SUPERCONDUCTING, violet): 92 px/s pull ending in a REPEL ring, double tables, 5 waves, pages backup.
    Before the fight it sits powered down in the suite (drawn in `drawBackground`).
- **Level 3 "Night Shift" (v0.5, `LEVEL3`):** 2100 px, 4 zones; the Med-Surg hall at 11 PM. `lightsOut`: the lights flicker and die in the intro
  (`nightLights()` in main.js), `W.dark = 0.9`, and only red exit signs, blinking call lights over the doors, station monitors, moonlit windows and
  little night-lights glow. Each nurse carries a flashlight (a stepped cone + floor pool from `W.lightHook`). Patients' eyes glow in the dark
  (`drawEyes`). The last zone has `final:true`: when it's cleared the power comes back (`W.finalT`, "POWER'S BACK!") and then the tally.
- **Lighting (v0.5, `drawLighting()` in world.js):** an offscreen darkness layer at `W.dark` with banded (retro-stepped) holes cut for every
  light, then an additive colour glow. `W.lights` is built from the wall pieces in `buildLevel`; moving lights come from `W.lightHook`.
- **4 heroes:**
  - Nick: balanced, Crash Cart special.
  - Kim: fast, Whirlwind Kick.
  - Will: power, Body Slam, big throws. He is bald (skin-tone head with a shine) in a normal fitted short-sleeve bright blue top, with skin forearms, a belt, dark pants and shoes. His stat color is blue. There's no orange/Halloween look and no padded suit/armor look.
  - Jackie: reach, Clipboard Spin, strong jump and dash.
- **Moves:** combos with a finisher, jump and jump kick, run (double-tap or Shift/RB) and dash attack, back attack (Attack+Jump),
  auto-grab, then knee or throw (throws hit other patients), a special that costs 8 HP, and the Code Blue super when the meter is full.
- **Patients:** all wear checked hospital gowns (pale green or faded olive) with yellow grip socks, and get random hair and skin at runtime.
  - Types: Wanderer (hugs), Call-light Spammer (throws remotes and pudding), Escape Artist (slaps and runs), IV-pole Swinger (sweeps),
    Sundowner (charges), Crutch Crusader (crutch poke), and Bell Ringer (call bell on a cord, whip that dizzies).
  - **v0.4 patients:**
    - Bed-Alarm Runner (`runner`): flees and beeps. Caught, he drops snacks and +1000. He escapes after `escape` seconds, so he never softlocks a zone.
    - Food-Tray Thrower (`tray`): flat trays (`p_tray`) and lobbed jello (`p_jello`, which leaves a green slippery puddle).
    - O2 Wanderer (`o2`): tank swing. `loseTank()` turns the tank into a kickable `o2tank` prop, and then he uses the `idle2`/`walk2`/`atk2` poses.
  - **Elite "Frequent Flyer":** beehive with curlers, red or blue socks, a cane up close, and from range syringe darts or lobbed urinals that splash and leave a slippery puddle.
  - The Belligerent Visitor is a tough guy in normal street clothes: plaid flannel (`plaid` body option), jeans, belt and white sneakers, with short brown hair, a beard and a yellow visitor badge. He's a visitor, so no gown, and he must not look like a tracksuit, cap, armor or red suit.
  - Each has its own KO line and falls asleep or gets tucked in. Crutch, bell and elite patients may drop their weapon.
- **Spawns** come in waves with an on-screen cap, from hallway room doors (301–314), from the elevators (B, C), and from both screen edges.
- **Pickups:** energy drink (small heal), fruit snacks (big heal), candy (speed), the ZYNN tin (+1 life; parody label, never the real logo), and score items (donut, gold star).
- **Weapons:** clipboard, bedpan, mop, IV pole, crutch, call bell (dizzies), cane, and an extinguisher that sprays and stuns.
- **Breakables (v0.3, kickable):** there are 36 floor props in Level 1, defined by `BREAKABLES` + `LOOT` in `src/data.js`, with physics in `src/world.js` (`makeProp`, `hitProp`, `smashProp`, `updateProp`, `bumpProps`).
  - **Kinds:** crash cart, supply cart, med cart, wheelchair, linen hamper, IV stand (all `roll`); chair, trash can, plant, wet-floor sign (all `slide`); vending machine (doesn't move).
  - **Hits:** jabs nudge a prop. Hard hits (kb >= 110: finishers, kicks, dashes, throws, specials) launch it.
  - **Rolling props:** a fast-moving prop plows patients down (it uses the kicker's score, combo and meter), shoves other props, and bounces off the screen edges and floor walls.
  - **Breaking:** a break makes debris (`chunk` fx), a drop roll (ZYNN capped at one per level), points, hit-stop and shake.
  - **Patients:** a knocked or thrown patient that hits a prop launches it, and Tilly's charge smashes props.
  - **Rules:** props are never solid, never hurt heroes, and never touch the camera or zone logic, so don't add any of that or progress could softlock.
- **Gurney ride (v0.4):** the `gurney` prop (`ride:true`).
  - **Mount:** GRAB or ATK+JUMP next to one (pad B or X+A). The touch GRAB button becomes RIDE (`#b_grab.ctx`).
  - **Ride:** `hero.js` `mount`/`s_ride`/`dismount`. It's about 2.6s, plows patients and bumps props, then crashes (`smashProp`) at the timeout, the screen edge or the boss. JUMP bails.
  - **Rules:** `updateProp` skips a prop that has a `rider`. Keep 'ride' non-hittable.
- **Charge Nurse team-up (v0.4, 2P only):** both nurses within 110x/40y hold SP with a meter of at least 50.
  - **Flow:** `teamwait`, then `startTeam`, then `s_teamup`. The blast at 0.75s does 70 forced damage to on-screen foes, 15% to the boss, and hits props. It costs 50 meter each.
  - **Fallback:** a release, a 1.2s timeout or no partner gives the normal special or Code Blue.
  - **FX:** `drawTeamBack`/`drawTeamFront`.
- **Cutscenes (v0.4, `src/cutscene.js`):** 3-panel comic pages (`start`, `boss`, `lunch`, `next`; v0.5 `mri`, `night`, `ending`), 8.6s each, skipped by any input after 0.6s.
  - Test URLs (`autostart`/`zone`/`bot`/`nocut`) skip them unless `&cuts=1`.
  - The boss one runs through `W.onBossCut`.
- **Breakroom Bonus (v0.4, `src/bonus.js`, `BONUS` in data.js):** a 45s round where thieves raid the fridge, vending machine and counter.
  - **Scoring:** 500 per stop, 150 per snack saved, and a 3000 perfect bonus. The tally (`btally`) adds it to the score.
  - **Flow:** tally → lunch cut → bonus → btally → next cut → Floor 4 (v0.5; the old teaser scene is unused).
  - **Debug:** `?scene=bonus`, `__nbd.bonus()`, `__nbd.B`.
- **Input:** presses that land during hit-stop are buffered (`h.pend`) and merged into the next live input.
- **Boss: Turbo Tilly** in an electric wheelchair.
  - Phase 1: horn honk shock ring (dizzies), rev and charge. After a charge her battery panel opens as the weak point; she takes only 30% damage otherwise.
  - Phase 2 (turbo): faster charges, drops puddles and yarn, and calls patients for backup.
- **Flow:** title, 1P/2P select, stage intro, waves, boss, tally, then the next floor (`afterTally()`), and THE END (`ending` scene) after the
  night shift. The tally total becomes the hero's score (ON TIME bonus = 2 game-hours from the floor's start clock). High scores are recorded at the end
  of the run or on game over. A KO'd 2P partner gets a fresh continue countdown on the next floor. Continues (3 / 5 / free play), lives,
  top-5 high scores, and settings saved in localStorage (`nbd2.save`, `nbd2.display`, `nbd2.input`). `save.best` = floors cleared (max 3).
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
- `?level=2` / `?level=3` starts on Radiology / the night shift (combine with `&zone=N`: Radiology 2 = Lou, 5 = MRI; night 3 = the last zone).
- `?god=1` keeps P1 at full HP.
- `?bot=1` lets a simple bot drive P1 (used for tests and GIFs).
- `?nocut=1` skips the cutscenes, and `&cuts=1` forces them back on for autostart/zone URLs.
- `?autostart=1&scene=bonus` jumps straight to the Breakroom Bonus.

Tests (Playwright + Chromium; the server must be running):
```bash
python3 tests/smoke.py      # desktop keyboard: title, select, first fight
python3 tests/moves.py      # every hero: jump, kick, special cost, super, run/dash, weapon pickup + swing
python3 tests/pad.py        # mocked gamepad: menus, select, move, attack, pause; 2P keyboard + pad
python3 tests/touch.py      # emulated Pixel phone landscape: taps, floating joystick, buttons, pause, rotate prompt
python3 tests/flow.py       # boss defeat -> tally -> bonus round -> bonus tally -> Radiology -> Night -> ending -> scores -> title; continue; game over
python3 tests/will.py       # Will's look on title, select, in-game HUD, tally
python3 tests/patients.py   # all patient types + random looks, elite syringe/urinal throws, splash + puddle, KO drops, new pickups
python3 tests/props.py      # v0.3 breakables: roll/plow/bounce/break, every kind, patients into props, loot odds, 2P pad, touch, bot to boss
python3 tests/v04.py        # v0.4: new patients, gurney (keys/pad/touch), 2P team-up + fallbacks, cutscenes + skips, bonus round + tally + flow
python3 tests/v05.py        # v0.5: Radiology, Lou, MRI (pull/yank/vent/waves/table/phase 2), night shift lights, full flow + cutscenes, 2P carry/continue, pad, touch, bot playthroughs
python3 tests/v05.py C D    # sections: A radiology, B Lou, C MRI, D night, E flow, F 2P/pad/touch, G bot playthrough (~4 min)
python3 tests/props_video.py   # webm for docs/props.gif (ffmpeg converts)
python3 tests/before_after.py <old art dir> docs/art_before_after.png   # art comparison sheet
python3 tests/shots.py "autostart=1&bot=1&god=1" 240 full 1280 720 6   # whole level with the bot
python3 tests/video.py      # webm clips for the GIF (ffmpeg converts)
```
Screenshots go to `tests/out/`, which is git-ignored. `docs/screenshots.png`, `docs/gameplay.gif`, `docs/props.gif`, `docs/v04_patients.gif`, `docs/v04_gurney_teamup.gif`, `docs/v05_radiology.gif`, `docs/v05_mri.gif` and `docs/v05_night.png` are committed copies.

## Rebuilding art and audio
- Patient looks: `tools/chars.py` has `GOWN`, `GOWN_OLIVE`, `SOCK`, `SOCK_ELITE` and `HAIRS`. `make_art.py` writes them to `atlas.json`
  (`chars.<patient>.pal` and `palettes`), and the game swaps those exact colors per spawn (a pool of 6 looks per type).
  If you add a patient, give it `**gown` and `**socks`, and add it to `PATIENTS` in `make_art.py`.
- `python3 tools/make_art.py` rewrites `art/*.png`, `art/atlas.json`, the font and the icons.
  - `tools/rig.py` is the side-view pixel puppet rig. `tools/chars.py` holds the heroes and patients (v0.5: `barium`, `apron`, `lou`), `tools/boss.py` Tilly, `tools/props.py` the hospital art, `tools/breakables.py` the v0.3 kickable props (3 states each) and debris bits, and `tools/radiology.py` the v0.5 art (radiology tiles, lightboxes, warning lamps, signs, night windows/call lamps/monitors, radiology props, MRI sheet `art/mri.png`, waves/table/cup/film, words).
  - It uses vendored copies of Master Builder's Gravewake `sprite_writer`/`pixel_writer` and brileta-sprites (plants, via node).
  - Never edit `/workspace/gravewake` itself. It belongs to another bot.
- `python3 tools/prop_sfx.py` rewrites only the prop sounds (crash, rattle, thunk, shatter), and `tools/v04_sfx.py` the v0.4 ones (beep, hiss, splat, fling, charge shout, fanfare, raid). `make_audio.py` calls both. `tools/v05_audio.py` writes the v0.5 music (`radiology`, `mri`, `night`) and SFX (hum, bang, quench, table, powerdown, click, lightsout, film, stomp, clunk, mri_voice, lou, scared).
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
| `src/data.js` | heroes, attacks, weapons, items, enemies, difficulty, `LEVEL1`/`LEVEL2`/`LEVEL3` layouts + zones/waves, `LEVELS` |
| `src/world.js` | world state `W`, background pre-render (per-level tiles), doors/elevators, props/items/shots/fx, camera (no scrolling back), v0.5 lights + `drawLighting()` |
| `src/actor.js`, `src/hero.js`, `src/enemy.js`, `src/boss.js` | actor base + `strike()` hit logic, hero state machine, patient AI, Turbo Tilly |
| `src/mri.js` | v0.5 Floor 4 bosses: `MRI` (MAGNA-SCAN 3000) and `Lou` (mini-boss) |
| `src/stage.js` | Director: zone triggers, camera locks, wave queue with cap, GO arrow, boss start/backup, projectiles |
| `src/hud.js` | portraits, HP/meter (half-meter team tick), lives, score, combo, last-hit foe bar, boss bar, toasts, continue prompts |
| `src/cutscene.js` | v0.4 shift-change comic cutscenes (`makeCut`/`updateCut`/`drawCut`, scripts start/boss/lunch/next) |
| `src/bonus.js` | v0.4 Breakroom Bonus round: `buildBreakroom`, `startBonus`, thief AI, `updateBonus`, bonus HUD, `bonusRows` for the tally |
| `sw.js`, `app.webmanifest`, `icons/` | PWA (cache name `nbd2-app-vN`, now v8: **bump N on every release**) |

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
- Three floors exist (Med-Surg, Radiology, Night Shift) plus the Breakroom Bonus. The ending says "SEE YOU NEXT SHIFT...".
- Turbo Tilly (Level 1 boss, from before Bill's size rule) is about 1.6x a nurse's height (3.3x area); she was not resized in v0.5.
- The MRI meets the 5x rule by area/width, not height (the screen is only 224 px tall). Lou is 2.2x height.
- Balance is first-pass: Tilly has 420 HP, the MRI 560, Lou 300 (x1.35 in 2P) and patient damage scales by difficulty in `DIFF`. The elite waves make zones 2–4 noticeably harder.
- The gown check pattern is drawn on a fixed pixel grid, so it doesn't move with the body. It shimmers very slightly during animation.
- Online co-op is not implemented. That was optional in the spec.

## Next steps
1. Bill plays on his phone and gives feedback on feel, difficulty and hero looks.
2. **Size rule from Bill:** bosses **at least 5x the player's size**, mini-bosses **2–3x** (applied to the v0.5 MRI and Lou).
   Turbo Tilly could be scaled up to match.
3. Character voice barks, plus an attract-mode demo on the title screen using the bot.
4. More stages per the spec: lobby/ER, ICU, cafeteria, roof helipad.
