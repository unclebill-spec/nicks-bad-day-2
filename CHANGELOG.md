# Changelog

All notable changes to Nick's Very Bad, Terrible Bad Day Part II. Dates are America/New_York.

## 2026-10-03: v0.2.1 "Will's new look" (Bill's feedback)
- **Will is now bald.** He has a clean skin-tone head with a small shine highlight on the crown, and his plain bright blue shirt (`WILL_BLUE` in `tools/chars.py`) replaces the orange Halloween shirt.
- **The whole orange/pumpkin look is gone:** the `halloween` pattern is deleted from `tools/chars.py`, and Will's hero-select stat-bar and role color is now blue (`#3a92ff`).
- **Updated everywhere Will appears:** every animation frame (`art/will.png`), the hero-select card, the HUD and tally portraits (`face_will` / `face_will_hurt`), and the title screen.
- Nothing else in the game changed.
- **Before/after:** `docs/will_before_after.png`. New test `tests/will.py` covers title, select, in-game and tally with Will. Service worker cache bumped to `nbd2-app-v3`.

## 2026-10-03: v0.2 "Gown Check" (Bill's art + gameplay notes)
- **Patients:**
  - Every patient now wears a traditional checked hospital gown, in pale green or faded olive, with yellow grip socks.
  - Standard patients get random hair colors and skin tones. Sheets are recolored at runtime by `tintSheet` in `src/gfx.js` and `lookFor` in `src/enemy.js`.
  - The old palette-swap sheets `wanderer2` and `escape2` are removed.
- **New weapon patients:**
  - **Crutch Crusader** pokes with a crutch.
  - **Bell Ringer** whips a call bell on its cord, which dizzies. IV-pole Swingers stay.
  - Both drop their weapon 50% of the time, and nurses can pick it up and use it: new weapons **crutch**, **call bell** and **cane**.
- **Elite "Frequent Flyer":**
  - Beehive hairdo with curlers, red or blue grip socks, and 1 armor.
  - Canes you up close. From range it throws syringe darts, or lobs full urinals that splash ("SPLOOSH!") and leave a slippery yellow puddle.
  - It's cartoonish, with no gore.
- **Nurse drops:**
  - The **energy drink** (small heal) and **fruit snacks** (big heal) replace coffee and pizza.
  - A round **ZYNN** tin replaces the Double Shift token for +1 life. It's a parody label with no real logo.
- **Level 1 waves** now mix in crutch, bell and elite patients, and add an extra wave in the elevator bank and in zone 4. Tilly's backup calls bring crutch and bell patients.
- **New sprites:** splash FX, comic words SPLOOSH!, DING! and POKE!, syringe, urinal, and the new weapon pickups. Service worker cache bumped to `nbd2-app-v2`.
- **Tests:** new `tests/patients.py` (random looks, elite throws, splash and puddle, KO drops, new pickups) and `tests/before_after.py` (the art comparison in `docs/art_before_after.png`).

## 2026-10-03: v0.1 "First Shift" (Level 1 playable)
- **Published** to GitHub Pages at https://unclebill-spec.github.io/nicks-bad-day-2/
- **Game runtime** (`src/`):
  - Fixed 60 Hz loop with hit-stop and screen shake.
  - Title, 1P/2P hero select, stage intro ("CLOCK IN!"), waves, boss, tally, teaser, game over, and a high score table ("Employees of the Month").
  - Pause, settings and how-to-play menus, drawn in the canvas and usable with keyboard, pad, mouse or touch.
- **Heroes:** Nick, Kim, Will and Jackie, each with their own stats, combos and special.
  - Shared moves: jump kick, run and dash attack, back attack, grab with knee or throw, weapons, and the Code Blue super.
- **Patients:** six types with AI, attack tokens, KO lines and sleepy defeats. They spawn from room doors, elevators and both screen edges.
- **Turbo Tilly** boss, in 2 phases (horn shock, charges, battery weak point, then turbo with puddles, yarn and backup calls).
- **Items and props:** pickups, weapons, breakables and score items.
- **Systems:** continues, lives, difficulty, saves in localStorage, and local 2P co-op (split keyboard, pads, and drop-in).
- **Bill's standard features:** fullscreen button, display presets (Retro forces 4:3), Install app, rotate prompt, PWA service worker, and music and SFX volume.
- **Tests:** Playwright tests for desktop keyboard, every hero's moves, mocked gamepad (1P and 2P), phone-landscape touch, full flow, and a bot run of the whole level.
- **Fixes during testing:**
  - Hero death no longer gets stuck before the continue prompt.
  - Heroes stay on screen during knockdowns.
  - A newly created input device can't fire a phantom press on its first frame.
  - Tally rows line up.
  - Floating text stays on screen.
- **Docs:** README, AGENTS.md, and third-party license notes.

## 2026-10-03: scaffold
- Project started: folder layout, vendored tools (Gravewake sprite and pixel writers, brileta-sprites), and fonts (Press Start 2P OFL, Luckiest Guy Apache-2.0).
- Art pipeline `tools/make_art.py`: a side-view pixel puppet rig (`tools/rig.py`) built on the Gravewake `Sprite`.
  - Characters: 4 heroes (Nick, Kim, Will, Jackie), 6 patient types plus 2 palette swaps, and Turbo Tilly in her power chair.
  - Hospital props, breakables, pickups, weapons, FX and comic words.
  - Logo, HUD portraits, bitmap font and app icons.
- Audio pipeline `tools/make_audio.py`: chiptune music (title, select, stage, boss, clear) and SFX made with the N64 suite generators.
