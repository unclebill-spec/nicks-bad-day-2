# Changelog

All notable changes to Nick's Very Bad, Terrible Bad Day Part II. Dates are America/New_York.

## 2026-10-06: v0.10.3 "Flat Front" (Bill: "it looks like he's got a blob at the belly because of how the lines are done on the sweater.")
- **No more belly blob on Wonderful Will:** his sweater front is now straight from chest to hem, like Nick, Nate and Heather's tops
  but a bit broader for his stocky build. The old belly bulge (a curved outline and curved shading around the stomach) is gone; the
  only shading is one flat darker strip down the far side.
- **Arm fix:** his long sleeves used to run past the elbow and bunch into a round red lump in front of his stomach. The sleeve now
  stops at the elbow and is a little slimmer, and his idle, walk and punch wind-up use a high boxer's guard (elbow up at chest
  height), so there's a clear gap over the stomach.
- Same red and green sweater: red body, green collar, cuffs and hip band, the green zigzag band with snowflakes on the chest and
  shoulders only, a plain red belly, belt and navy pants with a visible waist. Checked in game at real size and 2x.
- Regenerated every Will frame (including the scooter rider and Body Slam); his HUD faces get the slimmer sleeve too. Other
  characters are unchanged. Service worker cache `nbd2-app-v19`. Docs: `docs/v10_3_will_belly.png` (v0.10.2 vs v0.10.3 at 3x:
  idle, walk, punch, scooter, plus in-game crops at real size and 2x).

## 2026-10-06: v0.10.2 "Red and Green" (Bill: "Just do a red and green sweater, the belly looks weird.")
- **Wonderful Will's sweater is now a classic red and green Christmas sweater:** a red knit body and long sleeves, a green Fair Isle
  band across the chest and shoulders (two solid green rows with a green zigzag between them and a white snowflake pixel in each
  gap), a few white snowflakes on the shoulders, a green crew collar and green cuffs.
- **Clean belly:** the little tree, the star and the all-over snowflake dots are gone. The stomach is one solid red area, and the
  sweater ends in a plain straight green hem band at the hips over his belt and navy pants, so there's a clear waist and no
  bulge, diaper or onesie look. Same stocky build and front silhouette as his old plain shirt.
- His brighter, cooler Christmas red (#d81e34) plus the green trim keep him apart from the red buffalo-plaid Visitor (#c03a30,
  jeans, beard). His select-card / HUD colour stays blue.
- Regenerated every Will frame (walk, attacks, Body Slam, scooter rider and the rest), his HUD face and hurt face; the select card,
  title line-up, cutscenes, tallies and THE END all draw from these. The HUD portrait shows the chest band (it only shows the shoulders).
- Service worker cache `nbd2-app-v18`. tests/v10_1.py checks the red + green sweater, a pattern-free stomach and the portrait.
  Docs: `docs/v10_2_will_sweater.png` (v0.10.1 vs v0.10.2: HUD face + hurt face, idle, walk, punch, scooter).

## 2026-10-06: v0.10.1 "Nicknames" (Bill: ginger Nick, then a nickname + personality for four nurses, and Will's Christmas sweater)
All six nurses now have a nickname and a personality on the select card: **Nervous Nick** (Pessimist), **Killer Kim** (Cheerful),
**Wonderful Will** (Top Dog), **Charge Jackie** (Helpful), **Nasty Nate** (Lazy) and **Heather** (Tough). Stats and moves are unchanged.
- **Nick is a ginger:** warm copper-orange hair (#e8842e, shade #b0581c) with light freckles. It is clearly more orange / copper
  than Kim's red (#d8462a), and Kim keeps her ponytail, so the two still read apart at a glance. Glasses, spiky cut, tall average
  build, navy scrubs and orange shoes are unchanged.
- **Wonderful Will's ugly Christmas sweater:** a bright blue knit (his colour, and it keeps him apart from the red-flannel visitor)
  with long sleeves and red ribbed cuffs, a red chest band with a white zigzag, white snowflake dots, a little tree with a star, and
  a red rib hem that ends at the hips over his belt and navy pants (visible waist, no onesie). Christmas, not Halloween, no pumpkins.
  So "Do you like my festive shirt?" lands.
- **About 30-40 speech bubbles each** for Nick, Kim, Will and Jackie on the same triggers as Nate and Heather: spawn, idle, grabs,
  lifting, food, coffee, weapons, hurt, KO, revive, the Ativan jab, Code Blue, special, zone clear, floor clear (the tally card),
  the Scooter Run (start, crash, snack, sedating a rider) and their own take on every cutscene line. Each also has a personal
  Ativan shout. New triggers: **throw** (a throw or slam lands) and **drop** (you just knocked a patient down).
  - **Nervous Nick (Pessimist):** anxious and sure the worst is coming. Bill's lines: "Did you see what the emergency room looks
    like right now?", "I know we're just going to get that admit.", "How come we always get screwed?", plus the full moon, the Q
    word, short two nurses, nine hours without peeing, the Pyxis, floated to the ICU, "This is fine. Nothing is fine." and more.
  - **Killer Kim (Cheerful):** relentlessly sweet while she flattens people. Extra lines on knockdowns, grabs, throws and her
    special, said to the patient she just dropped: "Can I help you back to bed?" (Bill), "Oopsie! Let's get you tucked in!",
    "Nap time, sweetie!", "I'll chart that as a mechanical fall!", "You're doing amazing! Stay on the floor!" and more.
  - **Wonderful Will (Top Dog):** cheerfully egotistical. Bill's lines: "I make nursing look easy.", "Lucky you, you got the best
    nurse on the unit.", "I make nursing look good!", "Do you like my festive shirt?", "Someone call for help?", "Normally this
    would be a two-nurse job, but I'm here.", plus "Hold your applause.", "One stick. Every time.", "Watch and learn, rookies." and more.
  - **Charge Jackie (Helpful):** the take-charge charge nurse who always pitches in. Bill's lines: "Who needs help?", "What can I do
    for you?", "Do you guys need anything?", "I'll get vitals!", "No, finish your charting, I'll get the patient!", plus "Go eat
    lunch, I've got your patients.", "I'll take the rapid response.", "Teamwork makes the dream work!" and more. She also has a line
    for the 2P **Charge Nurse** team-up (that move keeps its name; she's "Charge Jackie", the team-up is still "CHARGE NURSE").
- All lines are PG-13 and at most 57 characters, so the bubbles wrap to 2-3 rows and fit on a phone (tests/v10_1.py checks them).
- **Names everywhere:** select cards (two-line nickname + personality; 3x2 grid on 4:3), HUD (full nickname beside the score; the
  HUD slot grew from 170 to 180 px and long names / the score squeeze their letter spacing; very narrow screens fall back to the
  short name). New **narrow font** (a condensed copy of the 8 px font built at runtime) so 9-letter words like WONDERFUL and
  PESSIMIST fit the 62 px select cards cleanly, floor / bonus / Scooter Run tallies, high scores, THE END ("NERVOUS NICK AND THE CREW SURVIVED THE SHIFT.") and
  join / continue toasts. New `heroName(d, room)` in gfx.js picks the full or short name for the space.
- Regenerated: Nick's and Will's sheets (every frame, incl. the scooter rider poses), their HUD / hurt faces, the app icons.
- Service worker cache `nbd2-app-v17`. Tests: new `tests/v10_1.py`. Docs: `docs/v10_1_nick_ginger.png` (old vs new Nick next to Kim),
  `docs/v10_1_select_nick.png` (select, Nervous Nick picked), `docs/v10_1_select_phone.png`, `docs/v10_1_will_sweater.png`, `docs/v10_1_bubbles.png` (in-game bubbles), `docs/v10_1_crew.gif`.

## 2026-10-06: v0.10 "Heather" (Bill: a sixth playable nurse with a running clothesline and a sharp tongue)
- **HEATHER, the 6th playable nurse.** Blonde, long hair worn down, **royal blue scrubs**: a V-neck top with a hem over deeper royal
  blue drawstring pants, so the top, waistband and pants read separately (Bill's style rule: no onesie, diaper, padded or armor
  look). Stethoscope, badge, white sneakers. Normal staff size (56 px, the nurse average is ~57).
- **Stats: fast and tough, mid power.** 115 HP (only Will has more), walk 84 / run 166 (only Kim is quicker), power 1.0, reach 0.95.
  Select card: POW 3, SPD 4, RCH 2, TUF 4, in royal blue.
- **Her own 3-hit combo:** a quick jab, a swinging elbow, then a turn-and-bump **HIP CHECK** that knocks the patient over.
- **Special: RUNNING CLOTHESLINE** (her special slot, like Nate's Rolling Chair). She cocks her arm, sprints forward ~145 px with it
  held straight out at neck height (speed streaks, dust, a rising whoosh), flattens every patient in her lane (16 x power, forced
  knockdown, +150 each), then skids to a stop. She can't be interrupted mid-dash. Costs 8 HP like every special; the Ativan jab
  and Code Blue tiers work as usual.
- **Snarky speech bubbles** (same system as Nate's): spawn, idle (with an annoyed huff), grabs, lifting, food, coffee, weapons,
  taking damage, KO, revive / continue, after the Ativan jab, Code Blue, her special, zone clear and floor clear (also on the
  tally card). **Bill's lines, verbatim:**
  - "Your hands aren't broke, you can wipe your own ass."
  - "You don't like being wet? Shouldn't have pissed in your gown."
  - "Here's a rag, you can clean it up yourself."
  - "This isn't a restaurant. I have sick patients to take care of, your sandwich can wait."
  - Plus more in the same spirit: "Call bell's for emergencies, not ice chips.", "I'm your nurse, not your waitress.", "No, you
    can't have more Dilaudid.", "Hospital food isn't room service.", "The remote is right next to you.", "No, the TV doesn't get
    HBO.", "You're NPO. That means no cheeseburger.", "Yes, the gown opens in the back. That is how gowns work.", and others.
  - **Ativan jab:** her own shout bubble, "NO MORE DILAUDID. / HERE'S YOUR ATIVAN!", with a brisk voice clip, then a follow-up
    line once the jab lands ("Sweet dreams, sunshine.").
  - Long lines get wider bubbles (up to 27 characters a row) and stay up longer so they can be read.
- **Everywhere the other nurses are:** select card, HUD portrait (and hurt face), the title line-up (now six: three either side
  of the menu), tally, THE END screen, and her own takes in the cutscenes ("A RUNNER? I'm your nurse, not your track coach.",
  "Grab a scooter! I'm your nurse, not your chauffeur, Marv!", "NOPE! Here's a rag. See you tomorrow!", and more).
- **Scooter Run:** she rides a scooter sitting up straight, one hand on the tiller and the other on her hip, with her own lines
  ("Beep beep. Move it, Marv.", "Ow! Incident report!"). Tip banners now wait while a rider is talking so they don't cover the bubble.
- **Six-card select that fits phones:** 62 px cards on a 398 px (16:9) phone, up to 75 px on wide phones; tight names squeeze to a
  7 px letter spacing. Narrow 4:3 / retro views switch to a 3 x 2 grid of shorter cards. Keyboard, d-pad, touch and 2P all wrap
  across the six cards.
- **Tally card:** a long floor-clear quote is printed full width under the card instead of being cut off.
- **Controls:** keyboard (1P / 2P), gamepad and touch all work for her, including the touch joystick and the SP button.
- **Tests:** new `tests/v10.py` (A art / data / Bill's lines, B desktop select + title + HUD, C phones + 4:3 grid + touch,
  D gamepad, E combo + stats, F clothesline, G speech bubbles + Ativan + Code Blue + tally, H 2P keyboard, I Scooter Run 1P / 2P,
  J cutscenes + ending, K moves). `moves.py` covers Heather; `v08.py` and `v09.py` updated for six nurses.
- **Assets:** `art/heather.png` and the portraits (tools/chars.py `B["heather"]`, `long_hair()`, `hero_anims("heather")`);
  `tools/v10_audio.py` makes `ativan_heather`, `huff` and `clothesline`. Service worker cache `nbd2-app-v16`.
- Docs: `docs/v10_select.png`, `docs/v10_select_phone.png`, `docs/v10_heather.gif`.

## 2026-10-05: v0.9 "Scooter Run" (Bill: a TMNT sewer-surf style driving level on mobility scooters)
- **New level between Radiology and the Night Shift: the SCOOTER RUN.** After the Radiology tally, a comic cutscene: a patient,
  **MOTORCART MARV**, busts out of Radiology on a souped-up mobility scooter ("OUTTA MY WAY, NURSES!"), the lead nurse wonders
  about the flames (Nate: "Flames? Ugh. Can someone else chase him?"), and the team grabs scooters from the charging station
  (Nate: "Wait. I get to SIT? ...I'm in."). Then the chase down the long Floor 4 hallway at 6:30 PM.
- **How it plays (TMNT hover / sewer-surf style):**
  - The screen auto-scrolls quickly (172 px/s). UP / DOWN steers across the lanes. RIGHT speeds up and LEFT eases off, about 25%
    either way; the scooter also edges forward or back on screen.
  - **JUMP** hops the scooter over junk lying on the floor (knocked-over trash cans, mop buckets, green jello spills), with air
    time and a shadow under it. **Dodge** the things you can't jump: wet-floor signs, gurneys, supply and med carts, IV poles and
    patients.
  - **ATTACK fires Ativan syringes forward** (tap, or hold for auto-fire). A sedated patient tumbles to the side of the hall and naps
    there ("Nice scooter... zzz"), so the nurses can ride past.
  - **Patients:** wanderers drift across the lanes, chargers run straight at you ("RACE YA!"), food-tray throwers lob jello, cups
    and trays from the wall, and wheelchair patients roll at you ("WHEELCHAIR DERBY!"). Wheelchairs and throwers take two syringes;
    the empty wheelchair rolls off on its own.
  - **Crashing** costs health (difficulty-scaled), with a spin-out and ~1.6 s of invincible blinking. Losing all health costs a life;
    on the last life you get the usual CONTINUE countdown, and with no continues left it's GAME OVER.
  - **Pickups:** health snacks along the route (fruit snacks, donut, jerky, energy drink) and one ZYNN tin (+1 life).
  - **Set pieces:** a Wheelchair Derby at ~45% and a Gurney Slalom at ~70%, with tips at the top of the screen for the first jump,
    shot and dodge.
- **Mini-boss: MOTORCART MARV.** He roars up from behind ("EAT MY EXHAUST, NURSES!") in a candy-red hot-rod mobility scooter with
  flame decals, chrome twin exhausts, a spoiler, bull-horn handlebars, a bike horn and a checkered whip flag. Marv wears the normal
  checked gown, grip socks and orange racing goggles. Following Bill's size override, he is only modestly bigger than a nurse:
  about 1.22x a standing nurse with his cart.
  - **Attacks:** he weaves across the lanes, throws bedpans and urinals, drops trash cans and spills behind him, and reverses straight
    back at you ("BEEP BEEP!").
  - **NITRO** kicks in at half health and makes him faster.
  - **Defeat:** his cart sputters, smokes and coasts back while he falls asleep ("TUCKED IN! ...zzz", +5000). If nobody beats him
    within ~24 s, he runs out of battery.
- **Length:** about 60 s of hallway, then the Marv chase, for 60-90 s in total (the test bot takes ~82 s).
- **Scooter tally,** then on to the night shift. The tally adds:
  - SEDATED x150
  - SNACKS x100
  - NO CRASHES! 3000
  - MARV PARKED! 2000
- **Score, lives, continues and 2P carry over** both ways, because the nurses are the same Hero objects.
- **Look:**
  - Same pixel rig. All five nurses visibly sit on the scooters in their normal scrubs (separate top and pants with the waist;
    nothing padded): hands on the tiller, knees forward, feet on the footboard. Nate leans back with one hand behind his head.
  - New poses `scoot` / `scootf` (flicking a syringe) / `scooth` (crash), plus `wheel` for patients in wheelchairs.
  - Scooters come in red (P1) and blue (P2), with a basket holding a sharps box of Ativan and the classic orange safety flag.
- **Parallax:** a looping hallway at dusk. The ceiling and wall scroll at 0.72x, the floor at 1x, and dark support posts sweep past
  in front at 1.45x. Floor seams whip by, light pools sit under the ceiling lights, there is an evening tint, and speed lines and
  dust trail the wheels.
- **Controls:**
  - Keyboard: WASD / J / K, and P2 arrows / , / .
  - Gamepad: stick or d-pad, X shoots, A jumps.
  - Touch: the floating joystick steers, HIT reads SHOOT, JUMP jumps, and GRAB / SP hide during the level.
  - Pause (Esc / Start / the pause button) works.
  - 2P = two scooters.
- **New music and sounds:** a fast "scooter" chiptune (176 bpm), plus syringe "pew", tyre skid, motor rev, reversing beeper and
  Marv's voice lines (`tools/v09_audio.py`).
- **New code and art:**
  - New: `src/scooter.js`, `tools/v09_art.py`, `chars.marv_body()` / `marv_anims()` and the new poses.
  - Changed: main.js (`goScooter` / `scootPlay` / `toScootTally` / `goNight`, scenes `scoot` + `stally`), the `scoot` cutscene with
    vehicle support for cutscene actors, HUD (no SP hints on a scooter), CSS for the touch layout, and the world.js `door0` wall
    layer.
  - Debug: `?autostart=1&scene=scooter`, `__nbd.scooter()`, `__nbd.SC`, `__nbd.SCOOT`, `__nbd.scootSpawn(kind, dx, dy, who)`.
    The `?bot=1` test bot rides the level (dodges, hops, shoots, fights Marv).
- **Tests:**
  - New `tests/v09.py`, sections A-N:
    - A: art and sizes
    - B: flow and carry-over
    - C: keyboard
    - D: crashes and jumps
    - E: patients
    - F: pickups and course mix
    - G: continue and game over
    - H: Marv
    - I: 2P
    - J: pad
    - K: touch
    - L: cutscene
    - M: pause
    - N: timed bot ride
  - `tests/flow.py` now plays the whole Scooter Run with the bot between Radiology and the night shift. `tests/v05.py` follows the
    new Radiology -> scooter -> night flow.
- Service worker cache `nbd2-app-v15`. Screens: `docs/v09_scooter.gif`, `docs/v09_scooter.png`, `docs/v09_boss.png`,
  `docs/v09_cutscene.png`, `docs/v09_2p.png`.

## 2026-10-04: v0.8.1 "Waistline" (Bill: the nurses looked like they had a onesie or a diaper on, with no waist)
- **All five nurses redrawn with a separate scrub top and scrub pants.** The torso used to be one capsule whose round bottom
  swallowed the hips in the shirt colour, and the pants were the same colour as the top, so everyone read as a onesie / diaper.
  Now the shared rig (`figure()` in tools/rig.py) draws:
  - a shaped top (Will: his blue shirt) that goes shoulders -> narrower waist -> a slight flare at the hips and **ends at the hips
    with a visible hem** (ink edge plus a darker stitch row), keeping the slight V-neck, stethoscope and badge;
  - a **waistband** just below the hem (darker band, white drawstring ends; Will keeps his brown belt with a buckle);
  - **pants in a deeper shade than the top** (navy scrubs: top `#283a7a`, pants `#1d2a5e`; Nate: teal top, deeper teal pants),
    with slimmer thighs hung from hip joints set further apart, so the **legs part right under the seat** and there's a gap
    between them instead of a bulky crotch;
  - natural hips and a less boxy, more human torso.
- Every animation frame of every nurse is regenerated from the rig, so the select cards, HUD portraits, title line-up, cutscenes,
  tally card and ending all pick it up. The night-shift nurse in the cutscenes gets matching maroon pants.
- **Patients checked the same way:** gowns still hang like gowns with legs showing below (they just get a very slight waist);
  the Visitor's flannel / belt / jeans, the Lab-Coat Hugger's coat over slacks and Lou's gown + lead apron all read as separate
  top and bottom. Elites use the gown look.
- Sizes and hitboxes unchanged (every sprite keeps its height; widths within 1 px). Before/after: `docs/v081_before_after.png`
  (the nurses) and `docs/v081_patients_before_after.png`; in-game `docs/v081_ingame.png`, select `docs/v081_select.png`.
  Service worker cache `nbd2-app-v14`.

## 2026-10-04: v0.8 "Nasty Nate" (Bill: a fifth, playable, extremely lazy nurse)
- **NASTY NATE joins the shift.** A tall brunette guy with glasses and a low ponytail in plain teal scrubs (scrub top with V-neck,
  stethoscope and badge, matching pants, dark clogs). Slim, normal build: nothing padded or armored. He is the tallest nurse
  (~63 px vs the nurses' 56 px average, 61 px for Jackie) but still staff-sized (1.12x the average). Heavy-lidded "can I sit down"
  eyes and a faint five-o'clock shadow. Same pixel rig and style as Nick, Kim, Will and Jackie.
- **Lazy stats:** longest reach (1.45x), slowest walk and run, slower wind-ups (attacks take 1.18x as long), 105 HP, solid power.
  Card stats POW 3 / SPD 1 / RCH 5 / TUF 3, role LAZY.
- **His own moves:** a long-armed backhand, a palm shove, then a stretched-out push-kick finisher (`lz1`-`lz3`). Idle, he's on his
  phone. Win pose: hands behind his head.
- **Special: ROLLING CHAIR** (8 HP like the others). He plops into a black mesh office chair, leans back on his phone and coasts
  forward ~130 px, plowing over every patient in the way (knockdown). He can't be hit while rolling.
- **Speech bubbles with a lazy personality**, at spawn, idle (after ~6 s), grabbing a patient, picking up food / coffee / a weapon / a prop,
  taking damage, getting knocked out, being revived or continuing, Code Blue, his special, clearing a zone and clearing the floor
  (he signs off on the tally card too). Bill's exact lines are all in: "You made me get up from my chair." (every spawn),
  "I was playing a game on my phone." (idle) and "Oh btw, your IVs are all blown." (grabs and floor clear). Plus "Is it time for my
  break yet?", "I'm not charting that.", "Ugh, call bells.", "Ow. Rude.", "Five more minutes...", "Fine. CODE BLUE. Happy?",
  "Rolling chair. Best invention.", "Can I go home now?" and more.
- **His Ativan call:** the shout bubble reads "UGH. IT'S TIME FOR / SOME ATIVAN... *YAWN*" with a slower, lower voice clip.
- **Everywhere the nurses show up:** select card, HUD portrait (normal + hurt), title screen line-up (now five nurses), tally card,
  ending, and the cutscenes (he gets lazy versions of the lead nurse's lines when he's P1, e.g. "Double shift? You made me get up from
  my chair.").
- **Select screen fits five cards** on desktop and phones (tested 915x412, 844x390 and 667x375): narrower cards, NASTY NATE wraps to two
  lines, 1P / 2P markers moved to the card's top corners, "OK!" when locked. Keyboard, d-pad, touch (double-tap) and 2P all wrap
  across five cards. 2P works with Nate on either side.
- **MRI fix:** the open vent's frost plume is no longer cut off at the top of the machine's sprite (7 px of headroom added to the cell;
  the anchor moved with it, so the machine and its LCD face sit exactly where they did).
- New art: `tools/v08_art.py` (office chair), `low_ponytail()` + phone holder in tools/chars.py, heavy-lid eyes in tools/rig.py `face()`.
  New sounds: `tools/v08_audio.py` (ativan_nate, yawn). New test: `tests/v08.py`; `tests/moves.py` now covers Nate.
  Service worker cache `nbd2-app-v13`. Screens: `docs/v08_select.png`, `docs/v08_select_phone.png`, `docs/v08_nate.gif`.

## 2026-10-04: v0.7.1 "Dress Code" (Bill's art fixes: Lou, the apron patient, the Visitor)
- **Lead-Apron Lou redrawn** (Bill: the puffy blue body "looked weird"). Same height (~78-80 px, ~1.4x a nurse) and still broad, but now a
  natural patient build in the standard checked gown (random green/olive like everyone else) and yellow grip socks, with visible arms,
  hands and legs. Over the front of the gown he wears a FITTED radiology lead apron: a flat slate panel with a clean ink outline and edge
  highlight, a thyroid collar, a shoulder strap, a waist strap and a little dosimeter badge. Every frame (idle, walk, charge, stomp, throw,
  winded, hurt, falls) plus his HUD portrait, which now shows Lou himself instead of reusing the apron patient's face. (Lou has no
  cutscene panel; the HUD portrait is his only other art.)
- **The Radiology "apron" patient is now the LAB-COAT HUGGER:** an open white lab coat (lapels, chest pocket with a pen, hip pocket,
  long sleeves, tails hanging below the waist) over a pale-yellow shirt, red tie, charcoal slacks and brown shoes. No blue gown. His
  jab-absorbing gimmick now comes from the starchy coat; new lines ("I'm a doctor now!", "Doctor's orders: HUG!").
- **The Belligerent Visitor's top and bottom are clearly separate:** a red buffalo-plaid flannel that stops at the hips with a visible
  hem, a brown belt with a buckle, then denim jeans (different colour, shading and a fly seam) and white sneakers. No onesie look.
- Hitboxes, stats and the Lou fight are unchanged. Before/after: `docs/v071_before_after.png`; `docs/v07_sizes.png` refreshed.
  Service worker cache `nbd2-app-v12`.

## 2026-10-04: v0.7 "Body Slam" (Bill's v0.7 list: a real GRAB, smaller bosses, staff-sized patients, BEEF JERKY)
- **Dedicated GRAB (touch, gamepad, keyboard; P1 and P2).** Walking into a patient no longer grabs him; press GRAB (H / M, pad B, touch GRAB).
  - Holding a patient: direction toward where you FACE (alone, or with ATK) **tosses him forward**, bowling over and damaging anyone he hits.
  - Direction AWAY from where you face (alone, or with ATK) is an **over-the-shoulder BODY SLAM** behind you: big damage, a forced knockdown,
    screen shake, and a shockwave that knocks down and damages patients near the landing spot (and dents bosses).
  - ATK alone still knees (the third knee tosses). GRAB again tosses, or slams if you're pushing away. You let go after 2 s.
  - Context priority for the one button: throw a carried prop > toss a held patient > grab a patient > ride a gurney > pick up a weapon or prop.
    The touch button relabels itself GRAB / TOSS / RIDE / PICK UP / THROW, and a small <SLAM TOSS> hint shows on your first grabs each floor.
  - New sounds: toss whoosh and slam thud.
- **Patients are the same size as the staff** (Bill: unlike most games). Every patient type, elite and variant now uses the nurses'
  build (`NURSE_BUILD` in tools/chars.py): bodies stand ~57 px like the nurses (56 px average). Only hair, hats, props and a little belly
  differ; the elite's beehive was lowered. The Belligerent Visitor matches Nick's height with slightly broader shoulders. Hitboxes match
  too (patients h 52, visitor 56, nurses 48-54).
- **Smaller bosses (Bill overrides the old 5x boss rule for this game):** bosses are now only modestly bigger than the nurses,
  ~1.4-1.5x a nurse's height (see `docs/v07_sizes.png`).
  - **Turbo Tilly** redrawn at 0.86x her v0.5 layout (82 px with the flag, 1.46x; was 168 px). Hitbox 48x70, chair solidity, charge box,
    honk ring (80), wall stop, telegraph lane, FX and text heights all scaled to match; the lane lock and battery weak point are unchanged.
  - **MAGNA-SCAN 3000** drawn at 0.56x (83 px, 1.48x; was 149 px) with a crisp-rim scaled raster; the name plate moved to the plinth and
    the live LCD face was redrawn for the smaller screen. Hitbox 82x80, front face 41 px from centre, and the machine now sits nearer the
    right edge so the arena is roomier. Pull, waves, tables and the hot-coil weak point keep their timings.
  - **Lead-Apron Lou** rebuilt at 80 px (1.43x; was 133 px), still twice as broad as a nurse. Hitbox 30x78, charge box/speed trimmed
    (240 / 290), stomp ring 80 (104 in phase 2), solidity and FX scaled.
  - Cutscenes, the title-screen Tilly and the MRI's HUD icon use the new sizes. The test bot now walks round a boss pinned at the screen edge.
- **How to play** is now two pages (CONTROLS and MOVES) that fit on a phone screen above the pause button; flip with PAGE or left/right.
- **SNAP STIX is now BEEF JERKY** everywhere: a made-up kraft-bag wrapper with a red BEEF JERKY label (no real brand), "BEEF JERKY!"
  pickup text, its own crunchy-chew sound, docs and tests.
- Tests: new `tests/v07.py` (grab/toss/slam on keyboard, pad, touch and 2P; touch layout; jerky; sizes; bot wins all three boss fights);
  v05/v06 boss-size checks now follow the 1.2-1.5x rule. Service worker cache `nbd2-app-v11`.

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
