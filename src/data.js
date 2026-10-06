// Game data: heroes, patients, weapons, pickups, breakables and the Level 1 script (Floor 3, Med-Surg).
export const Y_MIN = 136, Y_MAX = 212, GRAV = 760;

export const HEROES = {
  nick: { name: 'NICK', role: 'Balanced', blurb: 'Tall, glasses, orange shoes. Steady hands.', hp: 100, walk: 72, depth: 50, run: 150, jump: 250, power: 1.0, reach: 1.0,
    combo: ['atk1', 'atk2', 'atk1', 'atk3'], special: 'CRASH CART', stats: [3, 3, 3, 3], color: '#ff8a1e' },
  kim: { name: 'KIM', role: 'Fast', blurb: 'Quick combos, lighter hits.', hp: 90, walk: 88, depth: 60, run: 170, jump: 255, power: 0.78, reach: 0.95,
    combo: ['atk1', 'atk2', 'atk1', 'atk2', 'atk4'], special: 'WHIRLWIND KICK', stats: [2, 5, 2, 2], color: '#ff5a3a', comboGap: 0.85, atkK: 0.85 },
  will: { name: 'WILL', role: 'Power', blurb: 'Slow, hits hard, big throws.', hp: 120, walk: 58, depth: 42, run: 128, jump: 225, power: 1.38, reach: 1.0,
    combo: ['atk1', 'atk2', 'atk4'], special: 'BODY SLAM', stats: [5, 2, 3, 5], color: '#3a92ff', throwK: 1.45, grabR: 1.3, atkK: 1.12 },
  jackie: { name: 'JACKIE', role: 'Reach', blurb: 'Long reach, big jumps, strong dash.', hp: 100, walk: 74, depth: 50, run: 160, jump: 290, power: 1.0, reach: 1.3,
    combo: ['atk1', 'atk2', 'atk3'], special: 'CLIPBOARD SPIN', stats: [3, 3, 5, 3], color: '#9a5ae0', dashK: 1.4 },
  // v0.8 NASTY NATE: tall, glasses, ponytail, teal scrubs, extremely lazy. Longest reach, slowest feet and wind-ups.
  // lines = his speech bubbles (Hero.say), shout = his take on the Ativan call, ativanSfx = his slower voice clip.
  nate: { name: 'NASTY NATE', short: 'NATE', role: 'Lazy', blurb: 'Longest reach, slowest walk. Would rather be sitting.', hp: 105, walk: 56, depth: 40, run: 124, jump: 230,
    power: 1.08, reach: 1.45, combo: ['lz1', 'lz2', 'lz3'], special: 'ROLLING CHAIR', stats: [3, 1, 5, 3], color: '#2ad0b8', atkK: 1.18, comboGap: 0.75,
    shout: ["UGH. IT'S TIME FOR", 'SOME ATIVAN... *YAWN*'], ativanSfx: 'ativan_nate',
    lines: {
      spawn: ['You made me get up from my chair.'],
      idle: ['I was playing a game on my phone.', 'Is it time for my break yet?', 'Ugh, call bells.'],
      grab: ['Oh btw, your IVs are all blown.', "Hold still. I'm on break."],
      lift: ["Ugh. Fine. I'll carry it."],
      food: ['Is it time for my break yet?', 'Snack break. Finally.'],
      coffee: ["Coffee. Now we're talking."],
      weapon: ["I'm not charting that.", "Ugh, fine. I'll hold it."],
      hurt: ['Ow. Rude.', "I'm not charting that.", 'Ugh, call bells.'],
      ko: ["Wake me when it's over."],
      revive: ['You made me get up from my chair.', 'Five more minutes...'],
      codeblue: ['Fine. CODE BLUE. Happy?', "Ugh. Code Blue. I'm up."],
      special: ["Don't make me get up.", 'Rolling chair. Best invention.'],
      zone: ['Ugh, call bells.', 'Is it time for my break yet?', "I'm not charting that."],
      clear: ['Is it time for my break yet?', 'Oh btw, your IVs are all blown.', 'Can I go home now?'],
    },
    scoot: { start: ['Finally. A job I can do sitting down.'], crash: ['Ow. Rude.', "I'm not charting that."], snack: ['Snack break. Finally.'] } },
  // v0.10 HEATHER: blonde, royal blue scrubs, fast and tough, mid power, zero patience for ridiculous demands.
  // RUNNING CLOTHESLINE special (hero.js), combo hc1-hc3 (jab, elbow, hip check). Bill's four lines are verbatim (BILL_LINES).
  heather: { name: 'HEATHER', role: 'Tough', blurb: "Fast, tough, and done with your nonsense.", hp: 115, walk: 84, depth: 56, run: 166, jump: 255,
    power: 1.0, reach: 0.95, combo: ['hc1', 'hc2', 'hc3'], special: 'CLOTHESLINE', stats: [3, 4, 2, 4], color: '#4a6cff', comboGap: 0.85,
    shout: ['NO MORE DILAUDID.', "HERE'S YOUR ATIVAN!"], ativanSfx: 'ativan_heather', idleSfx: 'huff',
    lines: {
      spawn: ["I'm your nurse, not your waitress.", 'Who keeps hitting the call bell?', 'Alright. Who wants their meds?'],
      idle: ["This isn't a restaurant. I have sick patients to take care of, your sandwich can wait.", "Call bell's for emergencies, not ice chips.",
        "Hospital food isn't room service.", 'The remote is right next to you.', 'Pressing it forty times will not make me faster.',
        "No, the TV doesn't get HBO.", 'Yes, the gown opens in the back. That is how gowns work.'],
      grab: ["Your hands aren't broke, you can wipe your own ass.", "You don't like being wet? Shouldn't have pissed in your gown.",
        "Here's a rag, you can clean it up yourself.", "No, you can't have more Dilaudid.", 'Back to bed. Now.'],
      lift: ['Lift with your legs, people.'],
      food: ['Finally, a snack. Nobody tell 304.', 'Mine. Get your own.'],
      coffee: ['Coffee. The only thing keeping this floor alive.'],
      weapon: ["Don't make me use this.", 'Oh, this will do.'],
      hurt: ["Really? That's going in my incident report.", 'Ow! Rude!', "I'm your nurse, not your punching bag."],
      ko: ['Somebody call a rapid... on me.'],
      revive: ["Break's over. Who rang?", "I'm back. Nobody touch the call bell."],
      ativan: ["No, you can't have more Dilaudid.", 'Sweet dreams, sunshine.'],
      codeblue: ['CODE BLUE! Everybody back in bed!', 'Clear! And stop pressing that call bell!'],
      special: ["Here's a rag, you can clean it up yourself.", 'Visiting hours are OVER.', 'You want ice chips? Get in line.'],
      zone: ["Call bell's for emergencies, not ice chips.", 'Next hall. More call lights.', "I'm your nurse, not your waitress.", "You're NPO. That means no cheeseburger."],
      clear: ["This isn't a restaurant. I have sick patients to take care of, your sandwich can wait.", "Hospital food isn't room service.",
        "Your hands aren't broke, you can wipe your own ass.", 'Floor done. Somebody bring me coffee.'],
    },
    scoot: { start: ['Beep beep. Move it, Marv.', "I'm your nurse, not your chauffeur."], crash: ["Who left that there? I'm charting it.", 'Ow! Incident report!'],
      snack: ['Finally, a snack.'], hit: ['Sweet dreams, sunshine.', 'Back to bed!'] } },
};
export const HERO_ORDER = ['nick', 'kim', 'will', 'jackie', 'nate', 'heather'];
// v0.10: Bill's exact lines for Heather. They must stay verbatim (tests/v10.py checks HEROES.heather.lines against these).
export const BILL_LINES = ["Your hands aren't broke, you can wipe your own ass.", "You don't like being wet? Shouldn't have pissed in your gown.",
  "Here's a rag, you can clean it up yourself.", "This isn't a restaurant. I have sick patients to take care of, your sandwich can wait."];

// hit = which frame lands; box = [x0, x1] forward reach, z band [z0, z1]
export const ATTACKS = {
  atk1: { t: [0.06, 0.1], dur: 0.2, dmg: 6, box: [6, 30], z: [26, 46], kb: 30, stun: 0.32, sfx: 'punch0' },
  atk2: { t: [0.07, 0.11], dur: 0.22, dmg: 7, box: [6, 32], z: [26, 46], kb: 34, stun: 0.34, sfx: 'punch1' },
  atk3: { t: [0.1, 0.2, 0.08], dur: 0.38, dmg: 12, box: [6, 40], z: [18, 50], kb: 140, stun: 0.5, down: true, sfx: 'punch2', word: 1 },
  // v0.8 Nate's lazy combo: a long backhand, a palm shove, then a stretched-out push-kick (long boxes, slow wind-ups via atkK)
  lz1: { t: [0.08, 0.12], dur: 0.24, dmg: 6, box: [6, 34], z: [24, 48], kb: 34, stun: 0.34, sfx: 'punch0' },
  lz2: { t: [0.09, 0.13], dur: 0.26, dmg: 8, box: [6, 36], z: [22, 48], kb: 40, stun: 0.36, sfx: 'punch1' },
  lz3: { t: [0.12, 0.2, 0.1], dur: 0.42, dmg: 13, box: [6, 42], z: [12, 46], kb: 150, stun: 0.5, down: true, sfx: 'heavy', word: 1 },
  // v0.10 Heather's combo: a quick jab, a swinging elbow, then a turn-and-bump HIP CHECK that knocks them over
  hc1: { t: [0.05, 0.09], dur: 0.19, dmg: 6, box: [6, 30], z: [26, 46], kb: 32, stun: 0.32, sfx: 'punch0' },
  hc2: { t: [0.06, 0.1], dur: 0.22, dmg: 8, box: [6, 31], z: [24, 48], kb: 40, stun: 0.36, sfx: 'punch1' },
  hc3: { t: [0.1, 0.18, 0.1], dur: 0.38, dmg: 13, box: [2, 34], z: [6, 40], kb: 175, stun: 0.5, down: true, sfx: 'heavy', word: 1 },
  atk4: { t: [0.14, 0.2], dur: 0.36, dmg: 13, box: [6, 38], z: [10, 52], kb: 150, stun: 0.5, down: true, sfx: 'heavy', word: 1 },
  jkick: { dmg: 12, box: [4, 36], z: [6, 40], kb: 150, stun: 0.5, down: true, sfx: 'punch2' },
  dash: { dur: 0.42, dmg: 14, box: [0, 34], z: [10, 46], kb: 170, stun: 0.5, down: true, sfx: 'heavy', word: 1 },
  back: { t: [0.14], dur: 0.32, dmg: 9, box: [-34, -2], z: [18, 48], kb: 120, stun: 0.45, down: true, sfx: 'punch1' },
  knee: { t: [0.12], dur: 0.24, dmg: 6, sfx: 'punch0' },
};

export const WEAPONS = {
  clipboard: { name: 'CLIPBOARD', spr: 'w_clipboard', dmg: 10, reach: 32, uses: 12, rate: 0.3, sfx: 'punch1', grip: [6, 14], word: 'w_smack' },
  bedpan: { metal: true, name: 'BEDPAN', spr: 'w_bedpan', dmg: 14, reach: 30, uses: 8, rate: 0.38, sfx: 'clang', grip: [17, 6], dizzy: true, word: 'w_clang' },
  mop: { name: 'MOP', spr: 'w_mop', dmg: 11, reach: 54, uses: 10, rate: 0.42, sfx: 'whoosh', grip: [3, 5], down: true, word: 'w_wham' },
  ivpole: { metal: true, name: 'IV POLE', spr: 'w_ivpole', dmg: 13, reach: 58, uses: 10, rate: 0.46, sfx: 'clang', grip: [3, 6], down: true, word: 'w_bonk' },
  crutch: { metal: true, name: 'CRUTCH', spr: 'w_crutch', dmg: 12, reach: 50, uses: 10, rate: 0.4, sfx: 'clang', grip: [20, 5], down: true, word: 'w_poke' },
  callbell: { metal: true, name: 'CALL BELL', spr: 'w_callbell', dmg: 8, reach: 62, uses: 12, rate: 0.36, sfx: 'ding', grip: [1, 6], dizzy: true, word: 'w_ding' },
  cane: { metal: true, name: 'CANE', spr: 'w_cane', dmg: 11, reach: 40, uses: 10, rate: 0.34, sfx: 'punch1', grip: [3, 7], word: 'w_smack' },
  extinguisher: { metal: true, name: 'EXTINGUISHER', spr: 'w_extinguisher', spray: true, ammo: 3.2, reach: 74, sfx: 'spray', grip: [6, 18] },
};

export const ITEMS = {
  energy: { spr: 'energy', heal: 25, score: 100, msg: 'ENERGY DRINK!' },
  snacks: { spr: 'snacks', heal: 70, score: 300, msg: 'FRUIT SNACKS!' },
  candy: { spr: 'candy', speed: 8, score: 200, msg: 'SUGAR RUSH!' },
  donut: { spr: 'donut', heal: 12, score: 500, msg: 'DONUT!' },
  star: { spr: 'star', score: 1000, msg: 'GOLD STAR!' },
  zynn: { spr: 'zynn', life: 1, score: 500, msg: 'ZYNN! +1 LIFE' },
  // v0.6 food: a slightly green three-day-old pizza slice (mid heal) and a bag of BEEF JERKY (v0.7 rename of the meat stick; plain made-up label, small-mid heal)
  pizza: { spr: 'pizza', heal: 45, score: 250, msg: '3-DAY-OLD PIZZA!', sfx: 'stink', stink: true },
  jerky: { spr: 'jerky', heal: 30, score: 200, msg: 'BEEF JERKY!', sfx: 'jerky' },
};

// Patients. Every one is a person having a rough day; their defeat is a nap, never a mean joke.
export const ENEMIES = {
  wanderer: { name: 'WANDERER', sheet: 'wanderer', hp: 38, speed: 30, depth: 22, reach: 24, score: 300, atk: 'hug', cd: [1.6, 2.6], ko: ['Zzz...', 'Is it lunch?', 'Sweet dreams!'], voice: 'voice0' },
  spammer: { name: 'CALL-LIGHT SPAMMER', sheet: 'spammer', hp: 34, speed: 40, depth: 26, reach: 140, score: 300, atk: 'throw', cd: [1.8, 2.8], keep: 110, ko: ['*click* ...zzz', 'Nurse? ...zzz'], voice: 'voice1' },
  escape: { name: 'ESCAPE ARTIST', sheet: 'escape', hp: 30, speed: 112, depth: 60, reach: 22, score: 350, atk: 'slap', cd: [1.2, 2.0], ko: ['Okay, back to bed!', 'Fine, fine...'], voice: 'voice5' },
  ivswing: { name: 'IV-POLE SWINGER', sheet: 'ivswing', hp: 50, speed: 36, depth: 24, reach: 52, score: 400, atk: 'sweep', cd: [1.6, 2.4], ko: ['My drip!', 'Zzz...'], voice: 'voice2' },
  sundowner: { name: 'SUNDOWNER', sheet: 'sundowner', hp: 44, speed: 34, depth: 26, reach: 24, score: 400, atk: 'charge', cd: [2.0, 3.0], ko: ['Is it morning?', 'Goodnight, nurse.'], voice: 'voice4' },
  crutch: { name: 'CRUTCH CRUSADER', sheet: 'crutch', hp: 42, speed: 30, depth: 22, reach: 44, score: 400, atk: 'poke', cd: [1.5, 2.4], drop: ['w:crutch', 0.5], ko: ['My good leg!', 'Physical therapy... zzz'], voice: 'voice2' },
  bell: { name: 'BELL RINGER', sheet: 'bell', hp: 40, speed: 36, depth: 24, reach: 60, score: 400, atk: 'whip', cd: [1.5, 2.3], drop: ['w:callbell', 0.5], ko: ['*ding* ...zzz', 'Ring me later...'], voice: 'voice1' },
  elite: { name: 'FREQUENT FLYER', sheet: 'elite', hp: 74, speed: 38, depth: 26, reach: 36, score: 900, atk: 'cane', cd: [1.3, 2.1], keep: 100, armor: 1, elite: true, drop: ['w:cane', 0.35],
    ko: ['I know the way out... zzz', 'See you next week!', 'Put it on my tab.'], voice: 'voice3' },
  // v0.4: the Bed-Alarm Runner never fights, it just runs (beeping) and gets away if you don't catch it; the Food-Tray
  // Thrower keeps its distance and hurls trays / lobs jello; the O2 Wanderer swings its tank cart until a hard hit knocks it loose.
  runner: { name: 'BED-ALARM RUNNER', sheet: 'runner', hp: 26, speed: 92, depth: 58, reach: 0, score: 700, atk: 'none', cd: [9, 9], runner: true, escape: 13,
    drop: ['snacks', 1], ko: ["Fine, I'll go back to bed!", '*beep* ...zzz', 'You caught me fair and square.'], voice: 'voice5' },
  tray: { name: 'FOOD-TRAY THROWER', sheet: 'tray', hp: 36, speed: 34, depth: 26, reach: 150, score: 450, atk: 'throw', cd: [1.7, 2.7], keep: 118, drop: ['donut', 0.3],
    ko: ['Compliments to the chef... zzz', 'Is it dessert time?', 'Fine. I will eat the peas.'], voice: 'voice1' },
  o2: { name: 'O2 WANDERER', sheet: 'o2', hp: 50, speed: 26, depth: 22, reach: 48, score: 450, atk: 'swing', cd: [1.8, 2.7], drop: ['energy', 0.4],
    ko: ['Just need a little air... zzz', 'Deep breaths... zzz'], voice: 'voice4' },
  // v0.4 breakroom bonus: snack thieves never attack, they raid the fridge / vending machine / counter and run for it
  thief: { name: 'SNACK THIEF', sheet: 'wanderer', hp: 14, speed: 62, depth: 40, reach: 0, score: 0, atk: 'none', cd: [9, 9],
    ko: ['I was just LOOKING!', "Okay, okay, back to bed!", 'Midnight snack... zzz', 'It had no NAME on it!'], voice: 'voice5' },
  // v0.5 Radiology patients. ai = which patient brain they borrow (src/enemy.js); lines = their own chatter.
  barium: { name: 'CONTRAST CHUGGER', sheet: 'barium', ai: 'tray', proj: 'barium', hp: 34, speed: 34, depth: 26, reach: 150, score: 450, atk: 'throw', cd: [1.6, 2.6], keep: 118, drop: ['energy', 0.3],
    ko: ['Tastes like... chalk... zzz', 'Banana flavor, my foot... zzz'], voice: 'voice1', lines: ['BANANA FLAVOR?!', 'Drink it ALL, they said!', 'Bottoms up!'] },
  // v0.7.1: wears a borrowed white lab coat now (Bill); the starchy coat soaks up two jabs (armor)
  apron: { name: 'LAB-COAT HUGGER', sheet: 'apron', ai: 'wanderer', hp: 56, speed: 26, depth: 22, reach: 24, score: 450, atk: 'hug', cd: [1.8, 2.8], armor: 2,
    ko: ['Paging... Dr. Nap... zzz', 'Is the scan over? ...zzz'], voice: 'voice0', lines: ['I\'m a doctor now!', 'Doctor\'s orders: HUG!'] },
  // v0.6 Fire Alarm Yeller (any floor, src/alarm.js): sprints for a pull station; knock him down before he pulls it
  yeller: { name: 'FIRE ALARM YELLER', sheet: 'yeller', ai: 'yeller', hp: 30, speed: 72, depth: 40, reach: 22, score: 600, atk: 'slap', cd: [1.3, 2.1],
    ko: ['Was it... not a fire? ...zzz', 'I smelled TOAST! ...zzz', 'False alarm... zzz'], voice: 'voice5', lines: ['FIRE! FIIIRE!', 'I SMELL SMOKE!'] },
  visitor: { name: 'BELLIGERENT VISITOR', sheet: 'visitor', hp: 110, speed: 44, depth: 26, reach: 34, score: 800, atk: 'punch', cd: [1.4, 2.2], armor: 3, ko: ['I want the manager... zzz', 'Visiting hours are over.'], voice: 'voice3', big: true },
};
export const VARIANTS = {};  // v0.2: looks are randomized at runtime instead (src/enemy.js lookFor)

// v0.3 breakables: every floor prop can be smashed; most can be kicked. v0.6: carry = a nurse can lift it overhead and
// throw it (crash carts, supply carts, gurneys and the vending machine are too big: kick-only).
// v0.3 breakables: every floor prop can be smashed; most can be kicked. move: 'roll' (casters, glides far) or 'slide'
// (scoots and stops), fr = friction per second, push = launch speed factor, dmg = damage to patients it plows into,
// mass = how hard it is to shove (other props / falling patients), bits = debris sprites, deb = debris chunk colours.
export const BREAKABLES = {
  crashcart: { metal: true, name: 'CRASH CART', spr: 'crashcart', hp: 5, w: 28, h: 40, move: 'roll', fr: 0.55, push: 1.0, dmg: 14, mass: 2.2, loot: 'cart', zap: true,
    bits: ['deb_drawer', 'deb_gauze', 'deb_pill', 'deb_syringe', 'deb_wheel', 'deb_gauze'], deb: ['#d8303c', '#a01c28', '#b8c0cc', '#3aa860'], hit: 'clang', brk: 'crash' },
  supplycart: { metal: true, name: 'SUPPLY CART', spr: 'supplycart', hp: 4, w: 28, h: 36, move: 'roll', fr: 0.6, push: 0.95, dmg: 12, mass: 2, loot: 'cart',
    bits: ['deb_box', 'deb_gauze', 'deb_glove', 'deb_rod', 'deb_wheel'], deb: ['#b8c0cc', '#c8a070', '#4a8ad8'], hit: 'clang', brk: 'crash' },
  medcart: { carry: true, metal: true, name: 'MED CART', spr: 'medcart', hp: 3, w: 24, h: 30, move: 'roll', fr: 0.6, push: 1.0, dmg: 12, mass: 1.8, loot: 'cart',
    bits: ['deb_pill', 'deb_gauze', 'deb_wheel'], deb: ['#e84a5a', '#a82838', '#b8c0cc'], hit: 'clang', brk: 'crash' },
  wheelchair: { carry: true, metal: true, name: 'WHEELCHAIR', spr: 'wheelchair', hp: 3, w: 24, h: 30, move: 'roll', fr: 0.5, push: 1.1, dmg: 12, mass: 1.4, loot: 'small',
    bits: ['deb_wheel', 'deb_rod', 'deb_seat'], deb: ['#2a5aa8', '#2a2e3a', '#9aa4b4'], hit: 'clang', brk: 'crash' },
  linen: { carry: true, name: 'LINEN HAMPER', spr: 'linen', hp: 3, w: 20, h: 30, move: 'roll', fr: 0.85, push: 0.9, dmg: 10, mass: 1.2, loot: 'linen',
    bits: ['deb_linen', 'deb_linen', 'deb_rod'], deb: ['#4a7ac8', '#f4f4f8'], hit: 'thunk', brk: 'crash' },
  ivstand: { carry: true, metal: true, name: 'IV STAND', spr: 'ivstand', hp: 2, w: 12, h: 54, states: 2, move: 'roll', fr: 0.9, push: 1.1, dmg: 8, mass: 0.7, loot: 'small',
    bits: ['deb_rod', 'deb_glass'], deb: ['#b8c0cc', '#cfe8ff'], hit: 'clang', brk: 'smash' },
  chair: { carry: true, name: 'CHAIR', spr: 'chair', hp: 2, w: 18, h: 26, move: 'slide', fr: 3.2, push: 0.85, dmg: 8, mass: 1, loot: 'small',
    bits: ['deb_seat', 'deb_rod'], deb: ['#5a8ad8', '#7c8696'], hit: 'thunk', brk: 'crash' },
  trash: { carry: true, name: 'TRASH CAN', spr: 'trash', hp: 2, w: 14, h: 24, move: 'slide', fr: 2.4, push: 1.05, dmg: 7, mass: 0.6, loot: 'trash',
    bits: ['deb_paper', 'deb_can', 'deb_paper', 'deb_box'], deb: ['#8a94a4', '#5c6676'], hit: 'clang', brk: 'crash' },
  plant: { carry: true, name: 'PLANT', spr: 'potplant', hp: 2, w: 16, h: 34, move: 'slide', fr: 4, push: 0.7, dmg: 6, mass: 1, loot: 'small',
    bits: ['deb_shard', 'deb_leaf', 'deb_shard', 'deb_leaf'], deb: ['#c86a3a', '#5a3a24', '#3a8a3a'], hit: 'thunk', brk: 'shatter' },
  wetfloor: { carry: true, name: 'WET FLOOR SIGN', spr: 'wetfloor', hp: 2, w: 14, h: 26, states: 2, move: 'slide', fr: 2.6, push: 1.2, dmg: 5, mass: 0.4, loot: 'small',
    bits: ['deb_sign', 'deb_sign'], deb: ['#ffd84a', '#d8a820'], hit: 'thunk', brk: 'thunk' },
  // v0.4: a rideable gurney (GRAB / ATK+JUMP / the RIDE touch button) and the O2 tank an O2 Wanderer drops
  gurney: { metal: true, name: 'GURNEY', spr: 'gurneyp', hp: 6, w: 52, h: 26, move: 'roll', fr: 0.5, push: 0.85, dmg: 14, mass: 2.4, loot: 'cart', ride: true,
    bits: ['deb_wheel', 'deb_linen', 'deb_rod', 'deb_linen'], deb: ['#f4f6fa', '#7ab0e8', '#b8c0cc'], hit: 'clang', brk: 'crash' },
  o2tank: { carry: true, metal: true, name: 'O2 TANK', spr: 'o2tank', hp: 4, w: 14, h: 30, move: 'roll', fr: 0.7, push: 1.15, dmg: 12, mass: 1.0, loot: 'small', hiss: true,
    bits: ['deb_rod', 'deb_wheel'], deb: ['#3aa860', '#267a44', '#b8c0cc'], hit: 'clang', brk: 'hiss' },
  // v0.5 Radiology props (metal ones get yanked by the MRI magnet; glow = it lights the dark floor around it)
  apronrack: { carry: true, metal: true, name: 'LEAD APRON RACK', spr: 'apronrack', hp: 4, w: 30, h: 44, move: 'roll', fr: 0.6, push: 0.9, dmg: 13, mass: 2, loot: 'cart',
    bits: ['deb_apron', 'deb_rod', 'deb_wheel', 'deb_apron'], deb: ['#3a6ad8', '#8a4ad8', '#2aa8a0', '#b8c0cc'], hit: 'clang', brk: 'crash' },
  contrastcart: { carry: true, metal: true, name: 'CONTRAST CART', spr: 'contrastcart', hp: 3, w: 28, h: 42, move: 'roll', fr: 0.6, push: 1.0, dmg: 12, mass: 1.8, loot: 'cart', zap: true, glow: '#ffb03a',
    bits: ['deb_bottle', 'deb_gauze', 'deb_wheel', 'deb_bottle'], deb: ['#b8c0cc', '#f4f6fa', '#3a6ad8'], hit: 'clang', brk: 'crash' },
  viewer: { carry: true, metal: true, name: 'FILM VIEWER', spr: 'viewer', hp: 2, w: 24, h: 44, move: 'roll', fr: 0.9, push: 1.0, dmg: 9, mass: 0.9, loot: 'small', glow: '#3aa8ff',
    bits: ['deb_film', 'deb_glass', 'deb_rod', 'deb_film'], deb: ['#bfeaff', '#1c3a66', '#8a94a4'], hit: 'clang', brk: 'smash' },
  // v0.6: a loose meal tray (the Tray Thrower's trays land as these): light, carryable, shatters in one hit
  mealtray: { carry: true, single: true, name: 'MEAL TRAY', spr: 'p_tray', hp: 1, w: 14, h: 8, move: 'slide', fr: 4, push: 1.2, dmg: 5, mass: 0.3, loot: 'none',
    deb: ['#c8ccd6', '#8a94a4', '#e8a040'], hit: 'clang', brk: 'clang' },
  vending: { name: 'VENDING MACHINE', spr: 'vending', hp: 6, w: 30, h: 64, big: true, mass: 99, loot: 'vending',
    bits: ['deb_glass', 'deb_can', 'deb_glass', 'deb_box'], deb: ['#d83a4a', '#1a2a3a', '#cfe8ff'], hit: 'clang', brk: 'smash' },
};
// what a smashed prop coughs up (one roll per break, on top of any authored drops). Odds are per break.
export const LOOT = {
  patient: [['jerky', 0.06], ['pizza', 0.04]],  // v0.6: rolled when a patient (with no drop of their own) naps
  cart: [['pizza', 0.05], ['jerky', 0.05], ['energy', 0.22], ['snacks', 0.12], ['donut', 0.14], ['star', 0.1], ['w:mop', 0.05], ['w:bedpan', 0.05], ['w:clipboard', 0.04], ['w:extinguisher', 0.02], ['zynn', 0.025]],
  linen: [['pizza', 0.05], ['jerky', 0.06], ['energy', 0.16], ['snacks', 0.06], ['donut', 0.08], ['star', 0.06], ['w:bedpan', 0.08], ['w:mop', 0.03], ['zynn', 0.015]],
  trash: [['pizza', 0.1], ['jerky', 0.05], ['energy', 0.12], ['snacks', 0.05], ['donut', 0.12], ['star', 0.05], ['w:bedpan', 0.04], ['w:clipboard', 0.03], ['zynn', 0.01]],
  small: [['pizza', 0.04], ['jerky', 0.06], ['energy', 0.14], ['snacks', 0.05], ['donut', 0.09], ['star', 0.06], ['w:mop', 0.03], ['w:bedpan', 0.02], ['zynn', 0.01]],
  vending: [['snacks', 0.35], ['energy', 0.3], ['jerky', 0.15], ['star', 0.15], ['zynn', 0.03]],
};

// ---- Level 1: Floor 3 West, Med-Surg. x in world pixels. Doors / elevators are wall features enemies can come out of.
export const LEVEL1 = {
  id: 1, name: 'FLOOR 3: MED-SURG', sub: '7:00 AM. SHIFT CHANGE.', width: 3560, music: 'stage', clock: 7 * 60, floorNum: '3', cutBoss: 'boss',
  // wall layout: [x, kind, extra]
  wall: [
    [24, 'elev', 'A'], [118, 'callpanel'], [132, 'floornum3'], [170, 'poster_hands'], [200, 'sign_medsurg'], [244, 'chairs'], [306, 'plant0'],
    [340, 'door', 301], [400, 'poster_clock'], [430, 'window0'], [510, 'door', 302], [566, 'poster_sanitizer'], [600, 'poster_board'],
    [640, 'station'], [790, 'door', 303], [846, 'poster_quiet'], [880, 'window1'], [960, 'door', 304], [1016, 'poster_alarm'], [1040, 'sign_elev'],
    [1100, 'plant1'], [1140, 'elev', 'B'], [1222, 'callpanel'], [1240, 'elev', 'C'], [1322, 'callpanel'], [1344, 'chairs'], [1410, 'fountain'], [1440, 'poster_duck'],
    [1480, 'door', 305], [1540, 'window2'], [1620, 'door', 306], [1676, 'poster_hands'], [1710, 'gurney'], [1780, 'door', 307], [1840, 'poster_board'],
    [1880, 'window0'], [1960, 'door', 308], [2016, 'sign_lounge'], [2080, 'chairs'], [2150, 'plant2'], [2190, 'poster_duck'], [2240, 'door', 309],
    [2300, 'window1'], [2380, 'door', 310], [2440, 'poster_sanitizer'], [2470, 'wheelchair'], [2520, 'door', 311], [2580, 'sign_dayroom'], [2650, 'window2'],
    [2730, 'door', 312], [2800, 'poster_bingo'], [2840, 'poster_tv'], [2880, 'window0'], [2960, 'poster_bingo'], [3000, 'chairs'], [3070, 'window1'],
    [3150, 'poster_tv'], [3190, 'plant0'], [3230, 'door', 314], [3290, 'window2'], [3370, 'poster_duck'], [3410, 'sign_exit'], [3460, 'plant1'],
  ],
  props: [ // breakables on the floor: [x, y, kind, guaranteed drops[]] (plus one random LOOT roll each)
    // zone 1 (camera 0..)
    [150, 182, 'wetfloor', []], [236, 150, 'crashcart', ['energy']], [300, 204, 'trash', []], [334, 146, 'plant', []],
    [470, 150, 'medcart', []], [392, 196, 'gurney', []], [262, 194, 'mealtray', []],
    // zone 2 (camera 480..)
    [556, 198, 'chair', []], [612, 148, 'trash', []], [700, 164, 'crashcart', []], [804, 202, 'wetfloor', []], [880, 146, 'ivstand', ['w:ivpole']],
    [1012, 196, 'linen', ['w:bedpan']], [640, 186, 'gurney', []], [760, 150, 'mealtray', []],
    // zone 3: elevator bank (camera 1060..)
    [1118, 202, 'wheelchair', []], [1196, 146, 'trash', []], [1296, 190, 'crashcart', ['snacks']], [1366, 148, 'chair', []], [1388, 150, 'chair', []],
    [1500, 148, 'supplycart', []], [1190, 176, 'gurney', []],
    // zone 4 (camera 1600..)
    [1652, 148, 'plant', []], [1730, 200, 'linen', ['w:mop']], [1808, 162, 'crashcart', []], [1902, 202, 'wetfloor', []], [1958, 148, 'trash', []],
    [2090, 198, 'chair', []], [2110, 142, 'vending', ['candy', 'snacks', 'energy']], [2150, 200, 'chair', []],
    // zone 5 (camera 2200..)
    [2262, 150, 'wheelchair', []], [2330, 196, 'supplycart', ['w:clipboard']], [2424, 162, 'crashcart', []], [2504, 202, 'trash', []], [2562, 148, 'plant', []],
    [2600, 148, 'ivstand', ['w:extinguisher']], [2680, 200, 'linen', ['zynn']], [2290, 182, 'gurney', []], [1690, 184, 'gurney', []],
    // dayroom (boss): Tilly plows through these
    [3130, 150, 'chair', []], [3156, 152, 'chair', []], [3300, 200, 'crashcart', []], [3470, 148, 'plant', []],
    [3236, 198, 'mealtray', []], [3410, 196, 'trash', []],  // v0.6: ammo to throw at Tilly
  ],
  floorItems: [[700, 200, 'w:clipboard']],
  // zones: when the lead player passes `at`, the camera locks at [lock, lock + view width] until every wave is cleared
  zones: [
    { at: 120, lock: 0, waves: [
      [['wanderer', 'R', 0.6], ['escape', 'L', 1.8]],
      [['wanderer', 'D301', 0.2], ['spammer', 'R', 1.2], ['runner', 'D302', 2.4]],
    ] },
    { at: 560, lock: 480, waves: [
      [['escape', 'D302', 0.2], ['wanderer', 'R', 1.0], ['ivswing', 'L', 2.2], ['o2', 'R', 3.0]],
      [['spammer', 'D303', 0.3], ['tray', 'R', 1.0], ['wanderer', 'L', 1.6], ['bell', 'D304', 2.4], ['crutch', 'R', 3.2]],
    ] },
    { at: 1150, lock: 1060, title: 'ELEVATOR BANK', waves: [
      [['wanderer', 'EB', 0.8], ['sundowner', 'EB', 1.1], ['escape', 'EB', 1.4]],
      [['elite', 'EC', 0.8], ['tray', 'EC', 1.2], ['crutch', 'R', 2.4], ['runner', 'EB', 3.0]],
      [['visitor', 'EB', 0.6], ['bell', 'EB', 1.0], ['sundowner', 'L', 2.0]],
    ] },
    { at: 1700, lock: 1600, waves: [
      [['ivswing', 'D306', 0.3], ['o2', 'L', 0.9], ['sundowner', 'R', 1.6], ['escape', 'L', 2.6]],
      [['wanderer', 'D307', 0.2], ['bell', 'D308', 1.0], ['ivswing', 'R', 1.8], ['escape', 'L', 2.4]],
      [['elite', 'R', 0.4], ['crutch', 'L', 1.0], ['runner', 'D308', 1.8], ['tray', 'R', 2.4]],
    ] },
    { at: 2300, lock: 2200, waves: [
      [['visitor', 'R', 0.4], ['wanderer', 'D310', 1.0], ['tray', 'L', 1.6], ['o2', 'R', 2.6]],
      [['sundowner', 'D311', 0.3], ['elite', 'R', 0.9], ['ivswing', 'L', 1.5], ['visitor', 'D309', 2.6], ['bell', 'L', 3.2]],
    ] },
    { at: 3080, lock: 3060, boss: 'tilly', waves: [] },
  ],
  bossArena: 3060,
};
// ---- v0.5 Level 2: Floor 4 Radiology. Dark slate halls lit by neon-blue X-ray lightboxes; a mini-boss (Lead-Apron Lou) in
// the imaging waiting room and the MRI magnet boss in the MRI suite. dark = how dark the floor is (src/world.js lighting).
export const LEVEL2 = {
  id: 2, name: 'FLOOR 4: RADIOLOGY', sub: '3:00 PM. HOLD STILL, PLEASE.', width: 3500, music: 'radiology', bossMusic: 'mri', clock: 15 * 60, floorNum: '4', cutBoss: 'mri',
  dark: 0.5, tiles: { wall: 'rwall', ceil: 'rceil', floor: 'rfloor' },
  wall: [
    [24, 'elev', 'A'], [118, 'callpanel'], [132, 'floornum4'], [168, 'sign_radiology'], [236, 'lightbox0'], [296, 'chairs'], [370, 'door', 401], [364, 'warnlamp'],
    [430, 'lightbox1'], [496, 'poster_nometal'], [540, 'door', 402], [534, 'warnlamp'], [596, 'sign_xray'], [640, 'station'], [790, 'door', 403], [784, 'warnlamp'],
    [846, 'lightbox2'], [906, 'trefoil'], [960, 'door', 404], [954, 'warnlamp'], [1016, 'lightbox3'], [1080, 'sign_imaging'], [1100, 'chairs'], [1166, 'chairs'],
    [1240, 'lightbox0'], [1300, 'plant1'], [1344, 'chairs'], [1410, 'lightbox1'], [1480, 'door', 405], [1474, 'warnlamp'], [1540, 'lightbox2'], [1620, 'door', 406],
    [1614, 'warnlamp'], [1676, 'poster_nometal'], [1720, 'lightbox3'], [1780, 'door', 407], [1774, 'warnlamp'], [1840, 'lightbox0'], [1910, 'trefoil'], [1960, 'door', 408],
    [2030, 'lightbox1'], [2100, 'chairs'], [2180, 'lightbox2'], [2240, 'door', 409], [2234, 'warnlamp'], [2300, 'lightbox3'], [2380, 'door', 410], [2374, 'warnlamp'],
    [2440, 'poster_nometal'], [2470, 'wheelchair'], [2520, 'door', 411], [2514, 'warnlamp'], [2600, 'lightbox0'], [2680, 'sign_mri'], [2800, 'poster_nometal'],
    [2850, 'trefoil'], [2900, 'lightbox1'], [2990, 'sign_mri'], [3080, 'poster_nometal'], [3140, 'lightbox2'], [3420, 'sign_exit'],
  ],
  props: [
    [150, 182, 'wetfloor', []], [236, 150, 'contrastcart', ['energy']], [300, 204, 'trash', []], [392, 190, 'gurney', []], [452, 150, 'viewer', []],
    [556, 198, 'wheelchair', []], [640, 150, 'apronrack', []], [720, 186, 'gurney', []], [804, 202, 'viewer', []], [880, 146, 'ivstand', ['w:ivpole']], [1012, 196, 'contrastcart', ['w:bedpan']],
    [1118, 200, 'chair', []], [1150, 198, 'chair', []], [1296, 190, 'apronrack', ['snacks']], [1366, 148, 'chair', []], [1388, 150, 'chair', []], [1500, 148, 'wheelchair', []], [1440, 202, 'trash', []],
    [1652, 148, 'viewer', []], [1730, 200, 'linen', ['w:mop']], [1808, 162, 'contrastcart', []], [1902, 202, 'wetfloor', []], [1958, 148, 'apronrack', []], [2090, 190, 'gurney', []], [2150, 200, 'chair', []],
    [2262, 150, 'wheelchair', []], [2330, 196, 'supplycart', ['w:clipboard']], [2424, 162, 'apronrack', []], [2504, 202, 'trash', []], [2562, 148, 'viewer', []], [2600, 148, 'ivstand', ['w:extinguisher']], [2680, 200, 'linen', ['zynn']],
    // MRI suite: metal things for the magnet to yank
    [3036, 150, 'wheelchair', []], [3060, 200, 'crashcart', ['energy']], [3116, 172, 'ivstand', []], [3090, 140, 'contrastcart', []], [3150, 206, 'apronrack', []],
  ],
  floorItems: [[700, 200, 'w:clipboard'], [3100, 184, 'w:crutch'], [3140, 160, 'w:ivpole']],
  zones: [
    { at: 120, lock: 0, waves: [
      [['barium', 'R', 0.6], ['wanderer', 'D401', 1.4]],
      [['apron', 'R', 0.3], ['escape', 'L', 1.2], ['barium', 'D402', 2.0], ['runner', 'R', 2.8]],
    ] },
    { at: 560, lock: 480, title: 'X-RAY', waves: [
      [['spammer', 'D402', 0.2], ['barium', 'R', 1.0], ['crutch', 'L', 1.8], ['apron', 'R', 2.6]],
      [['tray', 'D403', 0.3], ['o2', 'R', 1.1], ['bell', 'L', 1.9], ['barium', 'D404', 2.6]],
    ] },
    { at: 1150, lock: 1060, title: 'IMAGING WAITING', boss: 'lou', mini: true, waves: [] },
    { at: 1700, lock: 1600, waves: [
      [['elite', 'D406', 0.3], ['barium', 'R', 0.9], ['apron', 'L', 1.6]],
      [['visitor', 'R', 0.4], ['sundowner', 'D407', 1.0], ['barium', 'L', 1.8], ['runner', 'D408', 2.4]],
    ] },
    { at: 2300, lock: 2200, waves: [
      [['o2', 'D409', 0.3], ['apron', 'R', 0.9], ['tray', 'L', 1.6], ['barium', 'D410', 2.4]],
      [['elite', 'R', 0.3], ['ivswing', 'L', 1.0], ['apron', 'D411', 1.8], ['bell', 'R', 2.5]],
    ] },
    { at: 3020, lock: 3000, boss: 'mri', title: 'MRI SUITE', waves: [] },
  ],
  bossArena: 3000, backup: ['barium', 'apron', 'wanderer', 'escape'],
};
// ---- v0.5 Level 3: the night shift, back on Floor 3. The lights go out: only exit signs, call lights, monitors, the
// windows, blue night-lights and the nurses' flashlights glow. The last zone ends the shift (the power comes back on).
export const LEVEL3 = {
  id: 3, name: 'FLOOR 3: NIGHT SHIFT', sub: '11:00 PM. WHO TURNED OFF THE LIGHTS?', width: 2100, music: 'night', clock: 23 * 60, floorNum: '3',
  dark: 0.9, flashlight: true, lightsOut: true, tiles: { ceilLit: false },
  wall: [
    [24, 'elev', 'A'], [118, 'callpanel'], [132, 'floornum3'], [200, 'sign_medsurg'], [244, 'chairs'], [306, 'plant0'], [340, 'door', 301], [356, 'calllamp'],
    [430, 'nwindow0'], [510, 'door', 302], [526, 'calllamp'], [596, 'sign_exit'], [640, 'station'], [664, 'monitor'], [706, 'monitor'], [748, 'monitor'],
    [790, 'door', 303], [806, 'calllamp'], [880, 'nwindow1'], [960, 'door', 304], [976, 'calllamp'], [1040, 'sign_elev'], [1100, 'plant1'], [1140, 'elev', 'B'],
    [1222, 'callpanel'], [1240, 'elev', 'C'], [1322, 'callpanel'], [1344, 'chairs'], [1440, 'poster_duck'], [1480, 'door', 305], [1496, 'calllamp'],
    [1540, 'nwindow2'], [1620, 'door', 306], [1636, 'calllamp'], [1700, 'sign_exit'], [1780, 'door', 307], [1796, 'calllamp'], [1880, 'nwindow0'],
    [1960, 'door', 308], [1976, 'calllamp'], [2050, 'sign_exit'],
    [90, 'nlight'], [470, 'nlight'], [900, 'nlight'], [1300, 'nlight'], [1580, 'nlight'], [1900, 'nlight'],
  ],
  props: [
    [150, 182, 'wetfloor', []], [236, 150, 'crashcart', ['energy']], [392, 196, 'gurney', []], [470, 150, 'medcart', []], [556, 198, 'chair', []], [700, 164, 'crashcart', []],
    [804, 202, 'wetfloor', []], [880, 146, 'ivstand', ['w:ivpole']], [1012, 196, 'linen', ['w:bedpan']], [1118, 202, 'wheelchair', []], [1296, 190, 'crashcart', ['snacks']],
    [1366, 148, 'chair', []], [1500, 148, 'supplycart', []], [1652, 148, 'plant', []], [1730, 200, 'linen', ['w:mop']], [1808, 162, 'crashcart', []], [1902, 202, 'gurney', []],
    [1958, 148, 'trash', ['zynn']], [1700, 186, 'viewer', []],
  ],
  floorItems: [[700, 200, 'w:clipboard'], [1200, 170, 'w:extinguisher']],
  zones: [
    { at: 120, lock: 0, waves: [
      [['wanderer', 'D301', 0.5], ['sundowner', 'R', 1.4]],
      [['escape', 'L', 0.3], ['runner', 'D302', 1.2], ['spammer', 'R', 2.0]],
    ] },
    { at: 560, lock: 480, title: 'NURSES STATION', waves: [
      [['bell', 'D303', 0.3], ['crutch', 'R', 1.0], ['sundowner', 'L', 1.8]],
      [['elite', 'D304', 0.3], ['tray', 'R', 1.2], ['wanderer', 'L', 2.0]],
    ] },
    { at: 1150, lock: 1060, title: 'ELEVATOR BANK', waves: [
      [['sundowner', 'EB', 0.6], ['o2', 'EC', 1.0], ['escape', 'EB', 1.6]],
      [['visitor', 'EC', 0.5], ['apron', 'EB', 1.0], ['barium', 'R', 2.0]],
    ] },
    { at: 1700, lock: 1600, title: 'LAST CALL', final: true, waves: [
      [['elite', 'D306', 0.3], ['sundowner', 'R', 0.8], ['runner', 'D307', 1.6], ['ivswing', 'L', 2.2]],
      [['visitor', 'D308', 0.3], ['bell', 'R', 0.9], ['tray', 'L', 1.5], ['wanderer', 'D307', 2.2], ['elite', 'R', 2.8]],
    ] },
  ],
};
export const LEVELS = [LEVEL1, LEVEL2, LEVEL3];
// ---- v0.4 Breakroom bonus round (between Floor 3 and Floor 4): one screen, built to the current view width at start.
// Thieves come out of the staff door and both screen edges, raid a snack spot for a couple of seconds, then run.
export const BONUS = { time: 45, every: [1.3, 2.3], cap: 4, raid: 2.3, stop: 500, saved: 150, perfect: 3000,
  loot: { fridge: ['donut', 'snacks', 'energy'], vending: ['candy', 'snacks', 'energy'], counter: ['donut', 'candy'] },
  looks: ['wanderer', 'spammer', 'escape', 'runner', 'tray', 'sundowner', 'crutch', 'bell'] };
export const DIFF = { easy: { dmg: 0.65, hp: 0.85, cap: 3 }, normal: { dmg: 1, hp: 1, cap: 4 }, hard: { dmg: 1.35, hp: 1.2, cap: 5 } };
