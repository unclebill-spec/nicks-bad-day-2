# Changelog

All notable changes to Nick's Very Bad, Terrible Bad Day Part II. Dates are America/New_York.

## 2026-10-03: v0.3 "Smash the Furniture" (Bill's request: kick and break things)
- **Every floor prop in Level 1 can now be kicked and smashed, arcade style.** There are 36 props across the 6 zones, and the dayroom gets a few for Tilly to plow through.
- **Crash carts:**
  - A kick, finisher, dash, throw or special sends one rolling across the floor. It knocks down and hurts every patient in its path (a WHAM! per hit), and the hits count toward your combo and meter.
  - It bounces off the screen edges and the floor's front and back walls, and shoves other props along with it.
  - Jabs only nudge it, so one full ground combo smashes it. Each hit pops the drawers open and scatters gauze, pills and syringes, with defib sparks and zaps.
  - When it breaks it flies apart into chunky debris and leaves a wreck on the floor.
- **New breakables:** supply cart, wheelchair, waiting-room chair, trash can, potted plant, and a CAUTION wet-floor sign. The med cart, linen hamper and IV stand now roll too, and the vending machine stays put but still smashes.
  - Carts, wheelchairs, hampers and IV stands roll far.
  - Chairs, trash cans, plants and signs scoot a short way.
  - Everything breaks after 1–6 hits.
- **Feel:** chunky pixel debris made from each prop's own parts (drawers, wheels, pot shards, leaves, paper, linen) plus color chunks that bounce and skid. You also get hit-stop, screen shake, sparks, and new sounds: crash, caster rattle, plastic thunk and ceramic shatter (`tools/prop_sfx.py`). Each smash is worth 150 points, 300 for a rolling prop and 500 for the vending machine.
- **Drops:** one random roll per break (`LOOT` in `src/data.js`), on top of any guaranteed drops placed in the level.
  - Carts drop something about 82% of the time.
  - Hampers about 50%, trash cans about 44%, and small props about 42%.
  - Drops can be an energy drink, fruit snacks, a donut or gold star (points), or sometimes a weapon (mop, bedpan, clipboard, rarely the extinguisher).
  - The ZYNN tin is rare (1–2.5%), and props can give only one per level.
- **Patients and props interact:**
  - A patient knocked down or thrown into a prop sends it flying and takes a little extra damage.
  - Tilly's charge smashes anything in her lane.
  - Props never block anyone, never hurt the nurses, and never affect the camera or zone locks.
- Works the same on keyboard, gamepad, touch and in 2-player, since props respond to every nurse's attacks.
- **New art** in `tools/breakables.py`, registered in `tools/make_art.py`. Character sheets are unchanged.
- **New test** `tests/props.py`: rolling, plowing, bouncing, breaking, debris, every prop kind, knocking and throwing patients into props, no blocking, loot odds, 2P keyboard + pad, touch, and the bot reaching the boss.
- `tests/props_video.py` records the clip for `docs/props.gif`. `tests/moves.py` now clears patients before the weapon-pickup check, so a hug can no longer make it flaky. Service worker cache bumped to `nbd2-app-v5`.

## 2026-10-03: v0.2.2 "Normal Clothes" (Bill's feedback)
- **Will and the Belligerent Visitor now wear normal clothes** instead of looking like they're in padded red-man suits or armor. Bulk, outlines and sizes were trimmed to match Nick, Kim, Jackie and the patients.
- **Will:** still bald and in bright blue, but now in a fitted short-sleeve blue top. You can see his skin-tone forearms and hands, plus a brown belt, regular dark pants and brown shoes. The puffy torso and long arm "plates" are gone.
- **Belligerent Visitor:** the purple tracksuit and red cap are gone. He now wears a green/navy plaid flannel shirt open at the neck, blue jeans, a belt and white sneakers, with short brown hair and a beard. He keeps the yellow visitor badge. The plaid comes from a new `plaid` body option in `tools/make_art.py`.
- Same pixel style, sheet size, animation frames and hitboxes. Updated everywhere they appear: all frames (`art/will.png`, `art/visitor.png`), the select card, the HUD/tally portraits and the title.
- **Before/after:** `docs/will_visitor_before_after.png`. Service worker cache bumped to `nbd2-app-v4`.

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
