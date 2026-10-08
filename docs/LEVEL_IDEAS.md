# Level ideas backlog

Bill liked all five of these pitches (2026-10-06). Build them one at a time; each one keeps the house rules:
comedic, never mean to patients (they nap or get tucked in), staff-sized enemies, bosses ~1.2-1.5x a nurse's height,
separate top + bottom with a visible waist (no onesie / diaper / padded / armor look), and "gloom and glow" neon
(blue, violet, red) wherever it fits. Every level must keep 2P, touch, gamepad, keyboard, the phone layout, Ativan,
Code Blue, grabs/throws, specials and the drops (pizza, BEEF JERKY, energy drink, fruit snacks, ZYNN).

| # | Level | Status |
|---|---|---|
| 1 | Parking Garage at Shift Change | **DONE (v0.11)**: Level P3, after the Night Shift, before the ending |
| 2 | Psych Ward | **DONE (v0.13)**: Floor 5, after the Scooter Run, before the Night Shift |
| 3 | Cafeteria Lunch Rush | idea |
| 4 | Labor & Delivery | idea |
| 5 | Rooftop Helipad at Night | idea |

## 1. Parking Garage at Shift Change (DONE, v0.11)
1990s TMNT-style street level. Concrete parking levels with stall lines, pillars, ramps, EXIT signs, a pay booth and a
gate arm; dawn light, sodium + fluorescent tubes and blue / violet / red neon. Cars back out of stalls and drive the lane
(horn, headlights, lane-flash warning) and flatten nurses *and* enemies, so you can bait foes into traffic; hit a parked car
and its alarm goes off. Parody cars only (ZIPPY HATCH, COMMUTER LX, FAMILY HAULER, WOODY WAGON). Angry visitors (road-rage
visitor with a parking ticket, minivan mom with a diaper bag, coffee guy, the "Do you know who I am?" big shot) plus escaped
patients. Boss: **Vinnie the Valet** in a golf cart (charge passes, honks, hops out to fight, climbs back in).
See `src/garage.js`, `src/valet.js`, `LEVEL4` in `src/data.js`.

## 2. Psych Ward (DONE, v0.13)
Built as FLOOR 5: THE PSYCH WARD with GREG and boss "Dr." Phil-in. See `src/ward.js`, `src/philin.js`, `LEVEL5` in `src/data.js`.

- **Look:** padded walls (quilted panels), flickering fluorescent lights (use the night-shift flicker + `W.dark`), a
  locked nurses' station behind glass, a dayroom with a TV on a bracket.
- **Enemies:** patients loose from their restraints (loose straps flapping from their sleeves, not a straitjacket
  costume; gown or sweats with a visible waist). Keep it kind and silly: they want snacks, the TV remote, to go home.
- **Hazards:** the lights flicker off for a beat (only eyes glow), a med-cart that rolls on its own.
- **Boss:** a patient who thinks he's the doctor, in a stolen white coat (stethoscope, clipboard, "I'll be doing
  rounds now"). He "prescribes" things: tongue-depressor throws, a reflex-hammer bonk, a "STAT!" rush. Naps on the
  exam table when beaten.

## 3. Cafeteria Lunch Rush
- **Look:** serving line with sneeze guards, steam trays, a salad bar, round tables and plastic chairs, a soda fountain.
- **Hazards:** slippery Jell-O puddles (reuse the jello puddle / slip), stacked trays that topple.
- **Enemies:** tray throwers (flat trays + lobbed Jell-O), line cutters, the guy who wants his order "on the side".
- **Boss:** **the Lunch Lady** with a giant ladle (hairnet, apron over a top + slacks). Ladle swing, soup splash wave
  down a lane, "NEXT!" shout that stuns, flings mystery meat. Phase 2: "WE'RE OUT OF PUDDING!"

## 4. Labor & Delivery
- **Look:** a pastel floor (mint, peach, baby blue tiles), a nursery window, balloons and "IT'S A ...!" banners.
- **Enemies:** screaming dads with camcorders (the camcorder light is a flash that dizzies), grandmas who won't leave
  (slow, tough, purse swing, "I'm not going anywhere!"), siblings with juice boxes.
- **Boss:** **a giant stork** (still only ~1.5x a nurse's height): bundle drops, wing gusts that push lanes, beak
  peck charge. Comedic, never scary; it flies off with a "baby" (a sack of laundry) at the end.

## 5. Rooftop Helipad at Night
- **Look:** a windy rooftop, the H pad with neon blue, violet and red landing lights, a windsock, the city skyline,
  HVAC units and vents.
- **Hazards:** wind gusts that push everyone across the lanes, the rotor wash when the chopper lands.
- **Boss:** **a rogue Life Flight crew** (flight-suit look must still be a separate jacket + cargo pants with a belt):
  a pilot who buzzes the pad and a flight medic pair who fight on foot. Defeated, they "go off shift" and nap on the
  stretcher. A good finale for the whole game.
