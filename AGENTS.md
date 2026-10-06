# AGENTS.md: Nick's Very Bad, Terrible Bad Day Part II

Handoff notes for any builder (Cursor reads this file automatically, and so do Bill's bots). Keep this file and
`CHANGELOG.md` current before every commit and push. **Pull first** when you resume work.

## What it is
A 1990s arcade beat 'em up in the spirit of Golden Axe and the TMNT and Simpsons arcade games. Six nurses fight
their way through hospital floors full of comedic patients. Plain HTML5 Canvas 2D plus ES modules. No build step
and no dependencies at runtime. Live on GitHub Pages: https://unclebill-spec.github.io/nicks-bad-day-2/

## Current state (2026-10-06, v0.10)
- **v0.10 HEATHER (6th playable nurse, `HEROES.heather`, last in `HERO_ORDER`):**
  - **Look:** `B["heather"]` in tools/chars.py: blonde (`HEATHER_HAIR`), long hair worn down (`long_hair()` hair_back), royal blue
    scrubs: top `HEATHER_BLUE` #2448d8 over deeper pants `HEATHER_BLUE_P` #1c38b0 with a waistband + drawstring (Bill's style rule).
    Staff-sized (56 px). `hero_anims("heather")`: hand-on-hip idle, `hc1` jab / `hc2` elbow / `hc3` turn-and-bump hip check
    (`flip=True` frames), 4-frame `special` (cock, dash A/B with the arm straight out, skid), `win`, seated `scoot` (hand on hip).
  - **Stats:** hp 115, walk 84, run 166, power 1.0, reach 0.95, `stats` [3, 4, 2, 4], colour #4a6cff. Attacks `hc1`-`hc3` in `ATTACKS`.
  - **RUNNING CLOTHESLINE** (`s_special` heather branch in hero.js): t 0.12-0.8 dashes at up to 255 px/s, `strike` once per target
    (box [-4, 28], z [8, 52], depth 15, 16 x power, kb 200, forced knockdown, +150 each, `W.stats.clotheslined`), skid at 0.8, idle +
    `say('special', true)` at 1.0. Not hittable mid-dash (`hittable()`), no inv blink. Speed streaks drawn in `draw()`. SFX `charge`
    (wind-up), `clothesline`, `skid`.
  - **Lines:** `d.lines` (spawn, idle, grab, lift, food, coffee, weapon, hurt, ko, revive, **ativan** (new event: said when the jab lands,
    shown after the shout), codeblue, special, zone, clear), `d.shout` = her Ativan bubble, `ativanSfx` 'ativan_heather', `idleSfx`
    'huff' (sayTick uses `d.idleSfx || 'yawn'`). **Bill's four lines must stay verbatim**: they are also in `BILL_LINES` (data.js),
    which tests/v10.py checks. `say()` now keeps long lines up longer (2.6 s + 0.045 s per char over 34) and starts the timer after
    an Ativan shout; `drawSay()` wraps at 18 / 22 / 27 chars by length.
  - **Scooter lines** moved to data: `HEROES[id].scoot` {start, crash, snack, hit} for Nate and Heather (`line()` in scooter.js).
    `SC.talk`: tip banners wait/pause while a rider bubble is up.
  - **Cutscenes:** `lz(id, normal, lazy, snark)`: 4th arg = Heather's line (start, boss, lunch x2, next, scoot x2, night, ending).
  - **Select (`drawSelect`):** 6 cards, gap 3, `cw = min(84, floor((VW - 8) / n) - gap)` (62 px at VW 398, 75 at 480); `fit()` squeezes
    a name / role to a 7 px advance (`text(..., { adv })` in gfx.js) when 8 px doesn't fit. If cards would be < 56 px (4:3 / retro,
    VW 300-320) it switches to a 3 x 2 grid (face + P/S/R/T bars, name, role; no full-body sprite). Title line-up: `xs` 3 left + 3 right.
  - **Tally:** a quote that needs more than 2 rows beside the face is printed under the card (full width in 1P, 7 px advance if needed)
    and PRESS ATTACK moves to the bottom row.
  - Tests: `tests/v10.py` A-K (see below). Docs: docs/v10_select.png, docs/v10_select_phone.png, docs/v10_heather.gif.
- **v0.9 SCOOTER RUN (`src/scooter.js`), between Radiology and the night shift:** a TMNT sewer-surf style driving level on mobility scooters.
  - **Flow:** `afterTally()` on lv 2 → `goScooter()` → cutscene `scoot` → `enterScooter()` (scene `scoot`, `scootUI(true)`: touch HIT reads SHOOT,
    `html[data-mode=scoot]` hides GRAB/SP) → `scootPlay()` each step (pause, continues, `updateScooter(dt, inputs)`) → `toScootTally()` (scene
    `stally`, `scootRows(h)` added to the score) → `goNight()` → cutscene `night` → `loadLevel(2)`. `loadLevel`/`toTitle` reset `W.scoot`.
  - **Model:** hallway things have a world x (`SC.d` = distance scrolled; screen x = `o.x - SC.d`); riders (`h.sc` on each Hero: x/y/z/vz/inv/crash/cd/fire/col)
    and Marv (`SC.boss`) live in screen x. `W.camX` stays 0 so `floatText`/`word`/`addFx` work in screen x. `syncHero()` copies the rider onto h.x/y/z
    so `drawSay()` and the HUD follow. Score/lives/continues are the Hero's own, so they carry both ways.
  - **Tuning** in `SCOOT` (len 10600 px ≈ 60 s at base 172 px/s, ±25% with left/right, jumpV 236 / grav 760, steer 96, dmg 14, inv 1.6, shot cd 0.22,
    boss HP 30 / 42 in 2P, `bossMax` 24 s before Marv runs out of battery). Hazards in `KIND` (`jump` = hop it with z > 0.7·h, `tall` = dodge only,
    `stop` = blocks syringes, `skid` = spill), patients in `FOE` (wander / charge / thrower / wheel). `buildCourse()` scripts tips, a Wheelchair Derby
    (~45%) and a Gurney Slalom (~70%), and exactly one ZYNN.
  - **Marv:** acts cycle `weave, throw, weave, drop, ram` (ram = BEEP BEEP reverse), phase 2 NITRO at half HP; `W.boss` is a plain HUD object
    (name/hp/maxHp/shown/phase/drawIcon/hint) only for the boss bar. Defeat → `SC.phase='finish'` → done after 3.2 s.
  - **Draw:** `drawHall()` parallax (wall 0.72x, floor 1x from the looping 1536 px `W.scootBg` built by `buildLevel`), `drawFront()` posts at 1.45x,
    y-sorted list of hazards / patients / riders / Marv / lobs / syringes. Rider = `scoot_red|blue0/1` sprite (ax 22, ay 43) + hero frame at (−4, −4);
    Marv = `marvcart0/1/2` (ax 34, ay 49) + `marv` frame at (−1, −8).
  - **Art:** `tools/v09_art.py` (scooters, `tipcan`, `mopbucket`, `marvcart*`), `hero_anims` `scoot`/`scootf`/`scooth` (all five; Nate leans back),
    `enemy_anims` `wheel`, `chars.marv_body()`/`marv_anims()` (sheet `marv`, cell 96x88). Marv + cart ≈ 1.22x a standing nurse (Bill's boss-size rule).
  - **Audio:** `tools/v09_audio.py` → music `scooter`, sfx pew, skid, scoot, beepbeep, marv, marv_ko.
  - **Debug / tests:** `?autostart=1&scene=scooter`, `__nbd.scooter()`, `__nbd.goScooter()`, `__nbd.SC`, `__nbd.SCOOT`, `__nbd.scootSpawn(kind, dx, dy, who)`;
    `?bot=1` uses `scootBot()` (dodge / hop / shoot / dodge the ram). `tests/v09.py` A-N; flow.py rides the whole level with the bot.
- **v0.8.1 waistline (Bill):** the torso in tools/rig.py `figure()` is a shaped top polygon (shoulders -> waist inset `waist`
  (default 2.0) -> hip flare `hip_flare` (0.9) -> hem at `hem` (-1.2, just below the hip joint) + a `hem_c` stitch row), drawn over a pants
  "seat" polygon with a waistband (`band` colour, or `belt` + `buckle`) and drawstring ends (`drawstring`, `drawstring_c`). Legs hang
  from hip joints `hip_sep` (1.9) apart with thighs `leg_w + thigh_add` (0.4). Gown bodies (`gown_len`) skip the seat, use waist 0.4 and
  keep the skirt. Hero pants default to `NAVY_P`/`NAVY_PS` (a deeper navy than the top; Nate `NATE_TEAL_P`). The cutscene night nurse
  (`nightNurse()` in cutscene.js) maps those pants colours to maroon; if you change them, update that tint list too.
  Before/after: docs/v081_before_after.png, docs/v081_patients_before_after.png.
- **v0.8 NASTY NATE (5th playable nurse):**
  - Data: `HEROES.nate` in data.js (`name` 'NASTY NATE', `short` 'NATE' for the HUD / ending, `reach` 1.45, `walk` 56, `atkK` 1.18,
    combo `lz1`-`lz3` in `ATTACKS`, `shout` = his Ativan bubble, `ativanSfx` 'ativan_nate', `lines` = his speech bubbles). `HERO_ORDER` has 5 ids.
    `atkK` (attack duration multiplier) replaced the old kim/will id checks in hero.js (kim 0.85, will 1.12); 3-frame attacks are any with 3 `t` entries.
  - **Speech bubbles:** `Hero.say(ev, force)` picks from `d.lines[ev]` (no immediate repeats), shows 2.6 s, 4.5 s cooldown unless `force`.
    `sayTick()` does the once-per-floor spawn line (`hiLv`) and the idle line (~6 s of no input, plays `yawn`). `drawSay()` is a wrapped
    white bubble drawn by main.js after everything else (on top of the dark). Events: spawn, idle, grab, lift, food, coffee, weapon,
    hurt, ko, revive (respawn + continue), codeblue, special, zone (stage.js zone clear), clear (toTally; also shown on the tally card
    as `T.quote`). Any hero can get lines by adding `lines` to its HEROES entry. Debug: `W.said` lists every line said, `W.stats.says`.
    **Bill's exact lines must stay verbatim:** "You made me get up from my chair." / "I was playing a game on my phone." / "Oh btw, your IVs are all blown."
  - **ROLLING CHAIR** special (`s_special` nate branch): t 0.16-0.98 coasts up to 190 px/s, `strike` once per target (knockdown);
    not hittable while rolling (`hittable()`), no inv blink. The chair sprite (`chair0/1`, tools/v08_art.py) is drawn under him in `draw()`.
  - Art: `B["nate"]` in tools/chars.py (teal `NATE_TEAL` scrubs, `NATE_HAIR`, `hair_cap(top=-0.28, back=0.12, grow=0.6, fringe=0)`,
    `low_ponytail`, `heavy_lids` in rig.py `face()`, light `beard` stubble, glasses). `hero_anims("nate")`: phone idle (`holder("phone")`),
    lz1-3, chair special (phone in hand), hands-behind-head win. Height ~63 px (taller than Jackie's 61, <= 1.15x the 56 px average).
    Plain scrubs only: Bill dislikes bulky / padded / armor-looking outfits.
  - Select (`drawSelect`, v0.8 layout; v0.10 changed it, see above): `cw = min(84, floor((VW-12)/n)-4)`, `ch` 176, names longer than the card wrap at the space, 1P/2P in the top
    corners, OK! at the bottom. Title line-up `xs` has five slots. Cutscenes use `lz(a, normal, lazy)` for Nate's versions of hero-a lines.
  - MRI sheet: `MOY` = 12.5 base units of headroom in tools/radiology.py (cell 104x96, anchor 52,93) so the vent plume isn't clipped.
  - Tests: `tests/v08.py` (A desktop select + title, B phones + touch, C pad, D size/art/stats, E combo/reach/chair, F bubbles + Ativan +
    Code Blue + tally line, G 2P keyboard with Nate as P2, H cutscene + MRI headroom).
- **v0.7 additions:**
  - **Dedicated GRAB:** walking into a patient no longer grabs (`autoGrab()` in hero.js is kept but unused). GRAB (H / M, pad B, touch `#b_grab`)
    calls `grab()`. While holding (`s_grab`): direction toward facing (|stick| > 0.55, alone once re-armed by a neutral stick or held 0.4 s,
    or with ATK) = `throwHeld(face)`; away from facing = `slam()` → `s_slam` (0.4 s over-the-shoulder arc, `e.rot` drives the sprite
    rotation via `frame(..., {rot})` in gfx.js) → `slamLand()` (26x power to the victim, forced knockdown, area hit 34 px / 14 depth).
    `grabContext()` in main.js: THROW (carrying) > TOSS (holding) > GRAB (patient in reach, no weapon) > RIDE > PICK UP. Stats: `W.stats.grabs/tosses/slams`.
  - **How to play:** `drawHelp()` in main.js is two pages (CONTROLS / MOVES), max 44 chars a line, panel height `min(VH - 34, 190)` so it clears the phone pause row.
  - **BEEF JERKY** replaces SNAP STIX (`jerky` item, `V6.jerky()` art in tools/v06_art.py, sounds in tools/v07_audio.py: jerky, toss, slam).
  - **Patients = staff size (Bill's v0.7 rule for this game):** `NURSE_BUILD` is applied to every kind in `PATIENT_KINDS` at the end of
    `bodies()` in tools/chars.py (visitor: Nick height, broader). Runtime hitbox in enemy.js: h 52 / w 14 (visitor h 56 / w 16).
    Don't make patients bigger or smaller than the nurses again.
  - **BOSS-SIZE OVERRIDE (Bill, v0.7, this game only):** bosses are only modestly bigger than the nurses, **~1.2-1.5x a nurse's height**
    (Tilly 82 px, MRI 83 px, Lou 78 px vs the nurses' 56 px average). This replaces the older "bosses >= 5x, mini-bosses 2-3x" rule for
    Nick's Very Bad, Terrible Bad Day Part II. Knobs: `SC` in tools/boss.py, `MS` in tools/radiology.py (mirrored by `BORE`/drawFace in
    src/mri.js), `B["lou"]` in tools/chars.py; hitboxes/FX in src/boss.js (`SOLID`, `LANE`, `TOP`) and src/mri.js. `docs/v07_sizes.png` shows the lineup.
  - **v0.7.1 outfits (Bill):** Lou = gown + fitted lead apron painted by `lou_apron()` (body `pattern` hook in tools/rig.py `figure()`,
    drawn over the torso, under the head and front arm; colours `LEAD`). Apron patient = Lab-Coat Hugger, `lab_coat()` (`COAT`, `COAT_SHIRT`);
    his runtime palette skips gown/sock recolouring (make_art.py). Visitor = red flannel + hem + belt + jeans via `flannel_and_jeans()` (`JEANS`).
    Lou's HUD face is `portrait(B["lou"], k=1.4)`. Never go back to the puffy blue Lou or the one-piece Visitor. Before/after: docs/v071_before_after.png.
  - Tests: `tests/v07.py` (A keyboard grab/toss/slam/knee + help pages, B priority/pad/2P/touch layout, C jerky, D sizes).
- **v0.6 additions:**
  - **Carry/throw props:** `carry: true` in `BREAKABLES` (data.js). Hero `lift`/`carry`/`toss` states in hero.js, flight physics `flyProp`/`landProp` and `THROW` in world.js. Priority: patient grab > gurney > weapon > lift > throw weapon.
  - **Turbo Tilly** was drawn at 1.8x in v0.6; v0.7 shrank her to 0.86x (`SC` in tools/boss.py, constants at the top of src/boss.js).
  - **Meter tiers:** `TIER = 100/3` in hero.js. `soloSpecial()`: full = `codeBlue()` (defib, shot kind `'defib'` in stage.js `shots()`), >= TIER = `ativan()`, else the special. Enemy `sleepT`, `'zapped'` state and skeleton flash in enemy.js; bosses use `stagT` (frozen while > 0).
  - **Food:** `pizza` and `jerky` (BEEF JERKY bag; v0.6's SNAP STIX meat stick, renamed in v0.7) in `ITEMS`/`LOOT` (plus `LOOT.patient` for KO drops).
  - **Fire Alarm Yeller (`src/alarm.js`):** `ALARM` tuning, wall stations, `maybeYeller()` on wave start, `pullAlarm()`, `updateAlarm()` (rain, wet floor, extra wave, `alarmPending()` blocks zone clear), drawing. Enemy kind `yeller` (ai `yeller`). `?yeller=1` forces one every wave (still capped), `?noalarm=1` turns it off. Settings `flash: 'full'|'reduced'` (`W.reducedFlash`).
- **A full shift is playable, start to finish:** Level 1 "Floor 3: Med-Surg" (Turbo Tilly) → Breakroom Bonus → comic cutscene →
  Level 2 "Floor 4: Radiology" (Lead-Apron Lou mini-boss, MAGNA-SCAN 3000 MRI boss) → cutscene → Level 3 "Night Shift" → ending
  cutscene → THE END screen → high scores. Score, lives, meter, continues used and 2P carry from floor to floor (`loadLevel(idx)` in main.js).
  Level 1 is 3560 px wide with 6 camera-lock zones: 5 wave zones, then the boss dayroom.
- **Level 2 "Floor 4: Radiology" (v0.5, `LEVEL2` in data.js):** 3500 px, 6 zones (waves, X-RAY, IMAGING WAITING = Lou, waves, waves, MRI SUITE).
  - **Look:** dark slate tiles (`rwall`/`rceil`/`rfloor`), `W.dark = 0.5`, lit by neon-blue X-ray lightboxes (chest, hand, skull, rubber duck),
    blinking red "IN USE" warning lamps, violet MRI sign. The lights come from wall pieces (`GLOW` table in world.js) plus glowing props and the MRI bore.
  - **Props:** lead-apron racks (`apronrack`), contrast carts (`contrastcart`, glow amber, zap), film viewers (`viewer`, glow blue), wheelchairs, gurneys,
    IV stands, crash carts. All use the v0.3 kick/break system. `metal: true` marks what the MRI magnet pulls (props and weapons).
  - **Patients:** Contrast Chugger (`barium`, `ai:'tray'`, lobs barium cups `p_cup` → white chalky puddle `puddle_w`), Lead-Apron Hugger (v0.7.1: Lab-Coat Hugger, white lab coat)
    (`apron`, `ai:'wanderer'`, armor 2: shrugs off two jabs). `d.ai` lets a new patient reuse an AI; `e.kind` is the AI, `e.type` the patient id.
  - **Mini-boss: LEAD-APRON LOU** (`Lou` in `src/mri.js`), ~78 px tall = **1.4x a nurse** (v0.7; was 133 px; v0.7.1 gown + fitted lead apron). Telegraphed three-point stance → linebacker charge →
    winded (`tired`, the weak point: full damage; 40% otherwise, no flinch). Stomp shock ring, X-ray film frisbees (`p_film`). Phase 2 at half HP
    ("FOURTH QUARTER! HIKE!") calls 2 helpers. Zone has `mini:true` (no cutscene); when beaten he is moved to `W.decor` (naps as scenery) and the zone opens.
  - **Boss: MAGNA-SCAN 3000** (`MRI` in `src/mri.js`), a front-view MRI machine with a live LCD face. **Size (v0.7): 83 px = 1.48x a nurse's height,
    ~3.7x her width** (drawn at `MS = 0.56` of the old 184x158 layout).
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
- **6 heroes:**
  - Nick: balanced, Crash Cart special.
  - Kim: fast, Whirlwind Kick.
  - Will: power, Body Slam, big throws. He is bald (skin-tone head with a shine) in a normal fitted short-sleeve bright blue top, with skin forearms, a belt, dark pants and shoes. His stat color is blue. There's no orange/Halloween look and no padded suit/armor look.
  - Jackie: reach, Clipboard Spin, strong jump and dash.
  - Nasty Nate (v0.8): lazy; longest reach, slowest, Rolling Chair special, speech bubbles. Tall, glasses, ponytail, teal scrubs.
  - Heather (v0.10): fast and tough, mid power; Running Clothesline special, snarky speech bubbles. Blonde, long hair, royal blue scrubs.
- **Moves:** combos with a finisher, jump and jump kick, run (double-tap or Shift/RB) and dash attack, back attack (Attack+Jump),
  GRAB a patient, then knee, toss forward or body slam behind (both hit other patients), a special that costs 8 HP, and the Code Blue super when the meter is full.
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
- **Cutscenes (v0.4, `src/cutscene.js`):** 3-panel comic pages (`start`, `boss`, `lunch`, `next`; v0.5 `mri`, `night`, `ending`; v0.9 `scoot`), 8.6s each, skipped by any input after 0.6s.
  - v0.9: an act with `ride: 'scoot_red' | 'scoot_blue' | 'marvcart'` is drawn sitting on that vehicle.
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
- **Flow:** title, 1P/2P select, stage intro, waves, boss, tally, then the next floor (`afterTally()`; v0.9: Radiology → Scooter Run → night), and THE END (`ending` scene) after the
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
- `?autostart=1&scene=bonus` jumps straight to the Breakroom Bonus; `?autostart=1&scene=scooter` to the v0.9 Scooter Run.
- `?yeller=1` forces a Fire Alarm Yeller into every wave (still capped at 2 per floor); `?noalarm=1` disables the event.

Tests (Playwright + Chromium; the server must be running):
```bash
python3 tests/smoke.py      # desktop keyboard: title, select, first fight
python3 tests/moves.py      # every hero: jump, kick, special cost, super, run/dash, weapon pickup + swing
python3 tests/pad.py        # mocked gamepad: menus, select, move, attack, pause; 2P keyboard + pad
python3 tests/touch.py      # emulated Pixel phone landscape: taps, floating joystick, buttons, pause, rotate prompt
python3 tests/flow.py       # boss defeat -> tally -> bonus round -> bonus tally -> Radiology -> Scooter Run (bot) -> Night -> ending -> scores -> title; continue; game over
python3 tests/will.py       # Will's look on title, select, in-game HUD, tally
python3 tests/patients.py   # all patient types + random looks, elite syringe/urinal throws, splash + puddle, KO drops, new pickups
python3 tests/props.py      # v0.3 breakables: roll/plow/bounce/break, every kind, patients into props, loot odds, 2P pad, touch, bot to boss
python3 tests/v04.py        # v0.4: new patients, gurney (keys/pad/touch), 2P team-up + fallbacks, cutscenes + skips, bonus round + tally + flow
python3 tests/v05.py        # v0.5: Radiology, Lou, MRI (pull/yank/vent/waves/table/phase 2), night shift lights, full flow + cutscenes, 2P carry/continue, pad, touch, bot playthroughs
python3 tests/v05.py C D    # sections: A radiology, B Lou, C MRI, D night, E flow, F 2P/pad/touch, G bot playthrough (~4 min)
python3 tests/v06.py        # v0.6: A carry/throw, B priorities, C directions/trays/magnet, D touch/pad/2P, E Tilly, F meter tiers, G food, H fire alarm
python3 tests/v07.py        # v0.7: A grab/toss/slam + help pages, B priority/pad/2P/touch layout, C beef jerky, D boss + patient sizes
python3 tests/v08.py        # v0.8: Nasty Nate: A select/title, B phones/touch, C pad, D size/art, E combo/chair, F speech bubbles, G 2P, H cutscene + MRI headroom
python3 tests/v10.py        # v0.10: Heather: A art/data/Bill's lines, B select+title+HUD, C phones+4:3 grid+touch, D pad, E combo, F clothesline, G bubbles, H 2P, I scooter, J cutscenes+ending, K moves
python3 tests/v09.py        # v0.9: Scooter Run: A art/sizes, B flow+carry, C keys, D crash/jump, E patients, F pickups, G continue, H Marv, I 2P, J pad, K touch, L cutscene, M pause, N timed bot ride (~85 s)
python3 tests/props_video.py   # webm for docs/props.gif (ffmpeg converts)
python3 tests/before_after.py <old art dir> docs/art_before_after.png   # art comparison sheet
python3 tests/shots.py "autostart=1&bot=1&god=1" 240 full 1280 720 6   # whole level with the bot
python3 tests/video.py      # webm clips for the GIF (ffmpeg converts)
```
Screenshots go to `tests/out/`, which is git-ignored. `docs/screenshots.png`, `docs/gameplay.gif`, `docs/props.gif`, `docs/v04_patients.gif`, `docs/v04_gurney_teamup.gif`, `docs/v05_radiology.gif`, `docs/v05_mri.gif`, `docs/v05_night.png` and the `docs/v06_*` GIFs and food images are committed copies.

## Rebuilding art and audio
- Patient looks: `tools/chars.py` has `GOWN`, `GOWN_OLIVE`, `SOCK`, `SOCK_ELITE` and `HAIRS`. `make_art.py` writes them to `atlas.json`
  (`chars.<patient>.pal` and `palettes`), and the game swaps those exact colors per spawn (a pool of 6 looks per type).
  If you add a patient, give it `**gown` and `**socks`, and add it to `PATIENTS` in `make_art.py`.
- `python3 tools/make_art.py` rewrites `art/*.png`, `art/atlas.json`, the font and the icons.
  - `tools/rig.py` is the side-view pixel puppet rig. `tools/chars.py` holds the heroes and patients (v0.5: `barium`, `apron`, `lou`), `tools/boss.py` Tilly, `tools/props.py` the hospital art, `tools/breakables.py` the v0.3 kickable props (3 states each) and debris bits, and `tools/radiology.py` the v0.5 art, `tools/v08_art.py` Nate's office chair, `tools/v09_art.py` the Scooter Run vehicles + floor junk, and `tools/v06_art.py` the v0.6 art (pizza, BEEF JERKY bag, Ativan syringe, skeleton, fire-alarm station; the `yeller` patient is in chars.py) (radiology tiles, lightboxes, warning lamps, signs, night windows/call lamps/monitors, radiology props, MRI sheet `art/mri.png`, waves/table/cup/film, words).
  - It uses vendored copies of Master Builder's Gravewake `sprite_writer`/`pixel_writer` and brileta-sprites (plants, via node).
  - Never edit `/workspace/gravewake` itself. It belongs to another bot.
- `python3 tools/prop_sfx.py` rewrites only the prop sounds (crash, rattle, thunk, shatter), and `tools/v04_sfx.py` the v0.4 ones (beep, hiss, splat, fling, charge shout, fanfare, raid). `make_audio.py` calls both. `tools/v05_audio.py` writes the v0.5 music (`radiology`, `mri`, `night`) and SFX (hum, bang, quench, table, powerdown, click, lightsout, film, stomp, clunk, mri_voice, lou, scared). `tools/v06_audio.py` writes the v0.6 SFX (ativan, defib, crackle, clear, alarm, yell, sprinkler, stink); `tools/v07_audio.py` the v0.7 ones (jerky, slam, toss); `tools/v08_audio.py` the v0.8 ones (ativan_nate, yawn); `tools/v10_audio.py` the v0.10 ones (ativan_heather, huff, clothesline); `tools/v09_audio.py` the v0.9 `scooter` music + pew, skid, scoot, beepbeep, marv, marv_ko.
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
| `src/alarm.js` | v0.6 Fire Alarm Yeller event: stations, caps, pull, sprinklers/wet floor, enrage, extra wave, strobe / reduced pulse |
| `src/mri.js` | v0.5 Floor 4 bosses: `MRI` (MAGNA-SCAN 3000) and `Lou` (mini-boss) |
| `src/stage.js` | Director: zone triggers, camera locks, wave queue with cap, GO arrow, boss start/backup, projectiles |
| `src/hud.js` | portraits, HP/meter (half-meter team tick), lives, score, combo, last-hit foe bar, boss bar, toasts, continue prompts |
| `src/cutscene.js` | v0.4 shift-change comic cutscenes (`makeCut`/`updateCut`/`drawCut`, scripts start/boss/lunch/next) |
| `src/bonus.js` | v0.4 Breakroom Bonus round: `buildBreakroom`, `startBonus`, thief AI, `updateBonus`, bonus HUD, `bonusRows` for the tally |
| `src/scooter.js` | v0.9 Scooter Run driving level: course, riders, hazards, patients, Motorcart Marv, parallax drawing, HUD, tally rows, test bot |
| `sw.js`, `app.webmanifest`, `icons/` | PWA (cache name `nbd2-app-vN`, now v16: **bump N on every release**) |

## Bill's standing preferences
- **Outfit style rule (Bill, v0.8.1):** every character's clothes read as a **separate top and bottom with a visible waist**
  (hem line, waistband / drawstring or belt, pants a different shade, legs visibly separate). **Never** a onesie, diaper,
  padded or armor look. Gowns hang like gowns with legs visible below.
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
- Three floors exist (Med-Surg, Radiology, Night Shift) plus the Breakroom Bonus and (v0.9) the Scooter Run driving level. The ending says "SEE YOU NEXT SHIFT...".
- Boss sizes follow Bill's v0.7 override (1.2-1.5x a nurse's height): Tilly 1.46x, MRI 1.48x, Lou 1.43x, Motorcart Marv (with his cart) 1.22x.
- Balance is first-pass: Tilly has 420 HP, the MRI 560, Lou 300 (x1.35 in 2P) and patient damage scales by difficulty in `DIFF`. The elite waves make zones 2–4 noticeably harder.
- The gown check pattern is drawn on a fixed pixel grid, so it doesn't move with the body. It shimmers very slightly during animation.
- Online co-op is not implemented. That was optional in the spec.

## Next steps
1. Bill plays on his phone and gives feedback on feel, difficulty and hero looks.
2. **Size rule from Bill (v0.7 override for this game):** bosses only **~1.2-1.5x a nurse's height**; patients **the same size as the nurses**.
3. More voice barks (Nate and Heather have speech bubbles via `say()`; the others could get lines too), plus an attract-mode demo on the title screen using the bot.
4. More stages per the spec: lobby/ER, ICU, cafeteria, roof helipad.
