# Changelog

All notable changes to Nick's Very Bad, Terrible Bad Day Part II. Dates are America/New_York.

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
