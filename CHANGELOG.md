# Changelog

All notable changes to Nick's Very Bad, Terrible Bad Day Part II. Dates are America/New_York.

## 2026-10-04: v0.7 "Body Slam" (Bill's v0.7 list: a real GRAB, smaller bosses, staff-sized patients, BEEF JERKY)
- **Dedicated GRAB (touch, gamepad, keyboard; P1 and P2).** Walking into a patient no longer grabs him; press GRAB (H / M, pad B, touch GRAB).
  - Holding a patient: direction toward where you FACE (alone, or with ATK) **tosses him forward**, bowling over and damaging anyone he hits.
  - Direction AWAY from where you face (alone, or with ATK) is an **over-the-shoulder BODY SLAM** behind you: big damage, a forced knockdown,
    screen shake, and a shockwave that knocks down and damages patients near the landing spot (and dents bosses).
  - ATK alone still knees (the third knee tosses). GRAB again tosses, or slams if you're pushing away. You let go after 2 s.
  - Context priority for the one button: throw a carried prop > toss a held patient > grab a patient > ride a gurney > pick up a weapon or prop.
    The touch button relabels itself GRAB / TOSS / RIDE / PICK UP / THROW, and a small <SLAM TOSS> hint shows on your first grabs each floor.
  - New sounds: toss whoosh and slam thud.
- **How to play** is now two pages (CONTROLS and MOVES) that fit on a phone screen above the pause button; flip with PAGE or left/right.
- **SNAP STIX is now BEEF JERKY** everywhere: a made-up kraft-bag wrapper with a red BEEF JERKY label (no real brand), "BEEF JERKY!"
  pickup text, its own crunchy-chew sound, docs and tests.

## 2026-10-03: v0.6 "Hands Full" (Bill's v0.6 list: throwable props, a bigger Tilly, meter tiers, new food, the Fire Alarm Yeller)
- **Pick up and throw props (Golden Axe / TMNT style).**
  - GRAB (or ATK when no patient is in reach) lifts small and medium props overhead: chairs, trash cans, plants, IV stands, wheelchairs, O2 tanks, linen and med carts, apron racks, film viewers, wet-floor signs and new loose meal trays.
  - Carrying is slower (0.74x, no running). ATK throws forward, up/down + ATK throws on a diagonal, ATK+JUMP throws backward, and you can jump-throw.
  - A thrown prop bowls over every patient in its path and breaks on impact. Getting hit makes you drop it, and the MRI magnet yanks carried metal props away.
  - Crash carts, supply carts, gurneys and vending machines stay kick-only.
  - The touch GRAB button relabels itself: GRAB / RIDE / PICK UP / THROW. Works on keyboard, gamepad and 2P.
- **Turbo Tilly is now a real boss (Bill's 5x rule):** redrawn at 1.8x (6x a nurse's width, about 10x her area, 2.8x her height).
  - Bigger, readable charge lane (flashes, then goes solid 0.4 s before she goes; red in phase 2), scaled hitboxes and honk ring, and a "HIT THE BATTERY!" hint.
- **Code Blue meter tiers** (notches at 1/3 and 2/3 on the HUD meter; the touch SP button reads SP / ATIVAN / CODE BLUE):
  - **1/3 meter: "IT'S TIME FOR SOME ATIVAN!"** Speech bubble, voice and a syringe jab on the nearest patient in front. Heavy damage, and the patient falls asleep (zzz), then wakes up woozy. Bosses and mini-bosses take damage plus a short stagger ("WOOZY...").
  - **Full meter: defib paddles.** CLEAR!, then crackling lightning bolts down the hall in the direction you face only. Patients get the electrified skeleton-flash knockdown; bosses take a chunk of damage plus a stagger.
  - Under 1/3 meter SP is still the regular special (costs a little health). The 2P Charge Nurse team-up is unchanged.
- **New food:**
  - **Three-day-old pizza:** a slightly green slice with stink lines. Mid heal (45).
  - **SNAP STIX meat stick** (renamed **BEEF JERKY** in v0.7): a parody wrapper (like the ZYNN tin). Small-to-mid heal (30), with a "snap" pickup sound.
  - Both are in the prop drop tables (carts, linen, trash, small props; the meat stick in vending) and the new patient KO drop table.
- **Fire Alarm Yeller (any floor: Med-Surg, Radiology, Night Shift and future floors).**
  - Red pull stations hang on the walls. Now and then a yelling patient ("FIRE! FIRE!") sprints to one and reaches up for 1.6 s with a big flashing "!" and a progress bar. Knock him down to stop it; knocked down, he has to start over.
  - **If he pulls it:** the alarm blares, the screen strobes red/white (2.5 flashes/s), the sprinklers rain on everything, the floor gets a wet sheen and slippery puddles, every patient on screen gets ENRAGED (red tint, steam, faster, 1.35x harder hits) for 14 s, and an extra wave of 4 pours out of the doors and elevators.
  - Afterwards the sprinklers stop and the floor stays wet for about 12 s.
  - **Limits:** at most 2 alarms per floor, at least 60 s apart, never in boss or mini-boss zones (it shuts off if a boss starts), and the zone can't clear until the extra wave is in, so camera locks can't softlock.
  - **Settings > FLASHING: FULL / REDUCED** (photosensitivity). REDUCED swaps the strobe for a soft red edge pulse and also tones down the other screen flashes.
- How-to-play page updated (lifting, meter tiers, the Yeller). New SFX: ativan, snap, defib, crackle, clear, alarm, yell, sprinkler, stink.
- Tests: new `tests/v06.py` (A carry/throw, B priorities, C directions/trays/magnet, D touch/pad/2P, E Tilly, F meter tiers, G food, H fire alarm). Every suite passes with no console errors.
- PWA cache bumped to `nbd2-app-v9`.

## 2026-10-03: v0.5 "Hold Still, Please" (Bill's last suggestions: Radiology, the MRI boss, the night shift)
- **A whole shift is now playable from start to finish.** Floor 3 Med-Surg (Turbo Tilly) → Breakroom Bonus → comic cutscene → **Floor 4: Radiology** → cutscene → **Night Shift** → ending cutscene → **THE END** → high scores.
  - Score, lives, meter, continues used and 2P all carry from floor to floor. Each floor's tally total becomes your score, and the ON TIME bonus is now measured from that floor's own clock.
  - High scores are recorded at THE END or on game over. "Floors cleared" now goes up to 3.
  - A 2P partner who was knocked out gets a fresh continue countdown on the next floor.
- **Level 2 "Floor 4: Radiology"** (3500 px, 6 zones), with Bill's gloom-and-glow look.
  - **Look:** dark slate halls lit by neon-blue X-ray lightboxes (chest, hand, skull and a rubber duck), blinking red IN USE lamps, radiation signs, a "NO METAL" poster and a violet MRI sign.
  - **New lighting system:** a darkness layer with retro, stepped pools of light, plus a soft coloured glow (neon blue first, then violet, then red). Lights come from wall pieces, glowing props, sparks and projectiles.
  - **Kickable radiology props** on the existing kick/break system: lead-apron racks, contrast carts (amber glow, sparks), film viewers (blue glow), and more wheelchairs. Each has its own debris (aprons, barium bottles, X-ray film).
  - **New patients:**
    - **Contrast Chugger:** lobs cups of barium ("BOTTOMS UP!") that leave a slippery white puddle ("CHALKY!", "BANANA FLAVOR?!").
    - **Lead-Apron Hugger:** his lead apron shrugs off two jabs before a real hit gets through.
  - Its own music (Radiology theme, plus an MRI boss theme) and new sounds: hum, KNOCK, quench hiss, table slam, power-down, film whoosh, stomp, clunk, the MRI's voice.
- **Mini-boss: LEAD-APRON LOU,** a gentle-giant ex-linebacker in three lead aprons, about **2.2x a nurse's height** (Bill's 2–3x rule).
  - **Charge:** he drops into a three-point stance (his lane flashes), then charges across the screen and ends up winded. That's his weak point: full damage. Otherwise he's armored (half damage, no flinch).
  - **Other attacks:** a stomp shock ring and X-ray film frisbees.
  - **Phase 2:** at half health he yells "FOURTH QUARTER! HIKE!" and calls two helpers.
  - **Defeat:** he naps where he fell ("Good game, nurses... zzz"), dropping fruit snacks and a gold star.
- **Boss: MAGNA-SCAN 3000, the MRI magnet,** with a live LCD face: eyes track you, angry while pulling, X-eyes while venting, asleep when beaten.
  - **Size:** 2.5x a nurse's height, 6.6x her width and 23x her area. A boss 5x as tall (about 280 px) can't fit on the 224 px screen, so it meets Bill's 5x rule by area and width, and is as tall as the screen allows.
  - **MAGNET ON:**
    - It drags the nurses toward it, and walking away resists.
    - It yanks metal weapons right out of their hands ("IT TOOK MY IV POLE!").
    - Metal on the floor (IV poles, crutches, bedpans, canes) and metal props (carts, wheelchairs, IV stands, apron racks) fly in and smash on it, hurting any nurse in the way. Touching its face zaps you.
  - **QUENCH:** after each pull it vents helium and its coil glows red. That's the weak point (full damage, otherwise 20% and CLANK!).
  - **KNOCK:** sound waves roll along the floor lanes. Jump them or change lanes.
  - **TABLE:** the patient table shoots out along your lane after the lane flashes red. Jump it.
  - **Phase 2 (SUPERCONDUCTING!, violet):** a stronger pull that ends in a REPEL blast, double tables, more waves, and "NEXT PATIENT, PLEASE!" backup.
  - **Defeat:** it powers down ("SCAN COMPLETE. HAVE A NICE DAY.") and every patient it paged takes a nap.
- **Level 3 "Night Shift":** back on Floor 3 at 11 PM.
  - **Lights out:** the lights flicker and die during the intro (KA-CHUNK! LIGHTS OUT!).
  - **What still glows:** red EXIT signs, blinking call lights over every door, the station monitors, moonlit windows and little night-lights, each casting its own pool of light.
  - **Flashlights:** every nurse carries one, which throws a cone and a pool of light ahead of her.
  - **Patients:** they shuffle out of the dark with glowing eyes and their own night music.
  - **Finale:** clear LAST CALL and the power comes back ("POWER'S BACK!") before the tally.
- **New cutscenes:**
  - Before the MRI: "PLEASE HOLD STILL. SCANNING... EVERYTHING!" / "Why is my badge clip FLOATING?"
  - Into the night shift: "Quiet night, right?" / KA-CHUNK / "WHO SAID THE Q-WORD?!"
  - The 7 AM ending: "NOPE! See you tomorrow!"
  - The "next floor" cutscene glow is now neon blue.
- **New THE END screen** with each nurse's final score and NEW HIGH SCORE.
- **Tests:**
  - New `tests/v05.py`, in 7 sections:
    - Radiology patients and props, Lou, and the MRI (pull, yank, floor metal, props, vent, far-lane hits, waves, table jump and hit, phase 2, repel, backup, defeat).
    - The night lights (lights-out ramp, glow sources, flashlight brightness, power back on).
    - The full flow with every cutscene.
    - 2P carry-over and continues, gamepad, and touch.
    - A bot playing Radiology and the Night Shift start to finish.
  - `flow.py` and `v04.py` now follow the new flow instead of the teaser.
- **Debug:** `?level=2` / `?level=3` (with `&zone=N`). `__nbd.loadLevel(i)`. Service worker cache bumped to `nbd2-app-v8`.

## 2026-10-03: v0.4 "Shift Change" (Bill's request: add all five suggestions)
- **Three new Level 1 patients.** They wear the same checked gown and yellow grip socks as the others, with their own hair, and get random looks per spawn.
  - **Bed-Alarm Runner** (blonde spikes, blinking red bed alarm): beeps and runs away from the nearest nurse, juking up and down. Catch him in time and he drops fruit snacks (35% chance of a gold star too, and a one-time 15% chance of a ZYNN tin) plus a +1000 CAUGHT! bonus. If you don't catch him in about 13 seconds he runs off screen. That never blocks a zone.
  - **Food-Tray Thrower** (grey hair, glasses): hurls meal trays flat across the lane and lobs jello that splats into a slippery green puddle (SPLAT!).
  - **O2 Wanderer** (elderly, bald ring of hair): drags an oxygen tank on a little cart and swings it. A hard hit (knockdown, kick, throw, special) knocks the tank loose. It becomes a rolling prop you can kick into the crowd, and it breaks with a PSSSHHH! and a puff of smoke. Without the tank he shuffles along with his own poses.
  - All three appear in every wave zone. The tray thrower and O2 wanderer also show up as Tilly's backup.
- **Rideable gurneys.** There are 5 on the floor.
  - **Hop on:** Grab, or Attack+Jump, next to one. On a pad that's B or X+A. On touch, the GRAB button changes to a pulsing **RIDE** button, and a RIDE! hint shows over the gurney.
  - **Ride:** the nurse shoves it forward for about 2.6 seconds, speeding up (you can steer up and down). It plows patients over and bumps props out of the way.
  - **End:** it crashes and breaks (CRASH!) at the end, against the screen edge, or into Tilly, and the nurse hops off with a kick. Press Jump to bail early, and the empty gurney keeps rolling into patients.
- **Charge Nurse team-up (2 players only).** When both nurses stand close together and both hold Special with at least half a meter, they launch a combined move.
  - **Look and sound:** a rotating starburst, rings, confetti and a cut-in band with both portraits. The shout is "CHARGE NURSE!" with a brass hit.
  - **Effect:** it knocks out every patient on screen, does 15% to Tilly, and smashes props. It costs half a meter each.
  - **Fallbacks:** a quick tap, or a partner who's too far away, still gives the normal special or Code Blue. The HUD shows a half-meter tick and a "TEAM UP: SP+SP!" hint in 2P.
- **Shift-change cutscenes** (`src/cutscene.js`), in the style of the Simpsons arcade game: 3-panel comic pages with captions, typewriter speech bubbles and a halftone background.
  - **Start of the game:** the night nurse's handoff ("Did you say... RUNNER?") as Turbo Tilly zooms past.
  - **Before Turbo Tilly.**
  - **After the level:** a lunch break ("HEY! That's MY yogurt!").
  - **After the bonus round:** the elevator up to Floor 4 Radiology.
  - Any key, pad button, click or tap skips one.
- **Breakroom Bonus round** (`src/bonus.js`) between the Level 1 tally and the next floor.
  - **Setup:** 45 seconds in a new breakroom (fridge, vending machine, counter, cabinets, table, notes on the fridge). Patients sneak in from the door and edges and raid the snack spots, then try to get away with the loot.
  - **Scoring:** 500 per thief stopped and 150 per snack saved (a thief you stop drops what he took), plus a 3000 NOTHING STOLEN! bonus.
  - **End:** a results tally is added to your score before the elevator cutscene and the teaser. It works in 1P and 2P, pause works, and the test bot plays it too.
- **Input:** button presses during hit-stop are now buffered, so no grab or jump gets dropped mid-impact.
- **New art and sounds:**
  - Art: 3 patient sheets, ride and team poses on every hero sheet, gurney, O2 tank, tray and jello, green puddle, breakroom pieces, and the CHARGE NURSE! / BONUS / STOPPED / CRASH / BEEP / TIME UP / SPLAT / CAUGHT words.
  - Sounds (`tools/v04_sfx.py`): beep, hiss, splat, fling, the charge shout, fanfare and raid.
- **New test `tests/v04.py`** covers every feature on keys, pad and touch, plus 2P, skips and the full flow. `smoke`, `pad`, `touch` and `will` now skip the start cutscene. `flow` now runs through the bonus round. Debug: `?nocut=1`, `?cuts=1`, `?scene=bonus`. Service worker cache bumped to `nbd2-app-v6`.
- **Follow-up fix (same day):** the bonus-round timer panel is wider, so "STOPPED n" no longer runs into "LOST n" (checked at 16:9 and Retro 4:3). Service worker cache bumped to `nbd2-app-v7`.

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
