// Game data: heroes, patients, weapons, pickups, breakables and the Level 1 script (Floor 3, Med-Surg).
export const Y_MIN = 136, Y_MAX = 212, GRAV = 760;

export const HEROES = {
  nick: { name: 'NICK', role: 'Balanced', blurb: 'Tall, glasses, orange shoes. Steady hands.', hp: 100, walk: 72, depth: 50, run: 150, jump: 250, power: 1.0, reach: 1.0,
    combo: ['atk1', 'atk2', 'atk1', 'atk3'], special: 'CRASH CART', stats: [3, 3, 3, 3], color: '#ff8a1e' },
  kim: { name: 'KIM', role: 'Fast', blurb: 'Quick combos, lighter hits.', hp: 90, walk: 88, depth: 60, run: 170, jump: 255, power: 0.78, reach: 0.95,
    combo: ['atk1', 'atk2', 'atk1', 'atk2', 'atk4'], special: 'WHIRLWIND KICK', stats: [2, 5, 2, 2], color: '#ff5a3a', comboGap: 0.85 },
  will: { name: 'WILL', role: 'Power', blurb: 'Slow, hits hard, big throws.', hp: 120, walk: 58, depth: 42, run: 128, jump: 225, power: 1.38, reach: 1.0,
    combo: ['atk1', 'atk2', 'atk4'], special: 'BODY SLAM', stats: [5, 2, 3, 5], color: '#ff7a18', throwK: 1.45, grabR: 1.3 },
  jackie: { name: 'JACKIE', role: 'Reach', blurb: 'Long reach, big jumps, strong dash.', hp: 100, walk: 74, depth: 50, run: 160, jump: 290, power: 1.0, reach: 1.3,
    combo: ['atk1', 'atk2', 'atk3'], special: 'CLIPBOARD SPIN', stats: [3, 3, 5, 3], color: '#9a5ae0', dashK: 1.4 },
};
export const HERO_ORDER = ['nick', 'kim', 'will', 'jackie'];

// hit = which frame lands; box = [x0, x1] forward reach, z band [z0, z1]
export const ATTACKS = {
  atk1: { t: [0.06, 0.1], dur: 0.2, dmg: 6, box: [6, 30], z: [26, 46], kb: 30, stun: 0.32, sfx: 'punch0' },
  atk2: { t: [0.07, 0.11], dur: 0.22, dmg: 7, box: [6, 32], z: [26, 46], kb: 34, stun: 0.34, sfx: 'punch1' },
  atk3: { t: [0.1, 0.2, 0.08], dur: 0.38, dmg: 12, box: [6, 40], z: [18, 50], kb: 140, stun: 0.5, down: true, sfx: 'punch2', word: 1 },
  atk4: { t: [0.14, 0.2], dur: 0.36, dmg: 13, box: [6, 38], z: [10, 52], kb: 150, stun: 0.5, down: true, sfx: 'heavy', word: 1 },
  jkick: { dmg: 12, box: [4, 36], z: [6, 40], kb: 150, stun: 0.5, down: true, sfx: 'punch2' },
  dash: { dur: 0.42, dmg: 14, box: [0, 34], z: [10, 46], kb: 170, stun: 0.5, down: true, sfx: 'heavy', word: 1 },
  back: { t: [0.14], dur: 0.32, dmg: 9, box: [-34, -2], z: [18, 48], kb: 120, stun: 0.45, down: true, sfx: 'punch1' },
  knee: { t: [0.12], dur: 0.24, dmg: 6, sfx: 'punch0' },
};

export const WEAPONS = {
  clipboard: { name: 'CLIPBOARD', spr: 'w_clipboard', dmg: 10, reach: 32, uses: 12, rate: 0.3, sfx: 'punch1', grip: [6, 14], word: 'w_smack' },
  bedpan: { name: 'BEDPAN', spr: 'w_bedpan', dmg: 14, reach: 30, uses: 8, rate: 0.38, sfx: 'clang', grip: [17, 6], dizzy: true, word: 'w_clang' },
  mop: { name: 'MOP', spr: 'w_mop', dmg: 11, reach: 54, uses: 10, rate: 0.42, sfx: 'whoosh', grip: [3, 5], down: true, word: 'w_wham' },
  ivpole: { name: 'IV POLE', spr: 'w_ivpole', dmg: 13, reach: 58, uses: 10, rate: 0.46, sfx: 'clang', grip: [3, 6], down: true, word: 'w_bonk' },
  crutch: { name: 'CRUTCH', spr: 'w_crutch', dmg: 12, reach: 50, uses: 10, rate: 0.4, sfx: 'clang', grip: [20, 5], down: true, word: 'w_poke' },
  callbell: { name: 'CALL BELL', spr: 'w_callbell', dmg: 8, reach: 62, uses: 12, rate: 0.36, sfx: 'ding', grip: [1, 6], dizzy: true, word: 'w_ding' },
  cane: { name: 'CANE', spr: 'w_cane', dmg: 11, reach: 40, uses: 10, rate: 0.34, sfx: 'punch1', grip: [3, 7], word: 'w_smack' },
  extinguisher: { name: 'EXTINGUISHER', spr: 'w_extinguisher', spray: true, ammo: 3.2, reach: 74, sfx: 'spray', grip: [6, 18] },
};

export const ITEMS = {
  energy: { spr: 'energy', heal: 25, score: 100, msg: 'ENERGY DRINK!' },
  snacks: { spr: 'snacks', heal: 70, score: 300, msg: 'FRUIT SNACKS!' },
  candy: { spr: 'candy', speed: 8, score: 200, msg: 'SUGAR RUSH!' },
  donut: { spr: 'donut', heal: 12, score: 500, msg: 'DONUT!' },
  star: { spr: 'star', score: 1000, msg: 'GOLD STAR!' },
  zynn: { spr: 'zynn', life: 1, score: 500, msg: 'ZYNN! +1 LIFE' },
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
  visitor: { name: 'BELLIGERENT VISITOR', sheet: 'visitor', hp: 110, speed: 44, depth: 26, reach: 34, score: 800, atk: 'punch', cd: [1.4, 2.2], armor: 3, ko: ['I want the manager... zzz', 'Visiting hours are over.'], voice: 'voice3', big: true },
};
export const VARIANTS = {};  // v0.2: looks are randomized at runtime instead (src/enemy.js lookFor)

export const BREAKABLES = {
  medcart: { spr: 'medcart', hp: 3, w: 24 }, linen: { spr: 'linen', hp: 3, w: 20 }, vending: { spr: 'vending', hp: 6, w: 30, big: true }, ivstand: { spr: 'ivstand', hp: 2, w: 12, states: 2 },
};

// ---- Level 1: Floor 3 West, Med-Surg. x in world pixels. Doors / elevators are wall features enemies can come out of.
export const LEVEL1 = {
  id: 1, name: 'FLOOR 3: MED-SURG', sub: '7:00 AM. SHIFT CHANGE.', width: 3560, music: 'stage',
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
  props: [ // breakables on the floor: [x, y, kind, drops[]]
    [470, 150, 'medcart', ['energy']], [880, 146, 'ivstand', ['w:ivpole']], [1012, 196, 'linen', ['w:bedpan', 'star']],
    [1500, 148, 'medcart', ['energy', 'donut']], [1730, 200, 'linen', ['w:mop']], [2110, 142, 'vending', ['candy', 'snacks', 'energy']],
    [2330, 196, 'medcart', ['w:clipboard']], [2600, 148, 'ivstand', ['w:extinguisher']], [2680, 200, 'linen', ['zynn']],
  ],
  floorItems: [[700, 200, 'w:clipboard']],
  // zones: when the lead player passes `at`, the camera locks at [lock, lock + view width] until every wave is cleared
  zones: [
    { at: 120, lock: 0, waves: [
      [['wanderer', 'R', 0.6], ['escape', 'L', 1.8]],
      [['wanderer', 'D301', 0.2], ['spammer', 'R', 1.2]],
    ] },
    { at: 560, lock: 480, waves: [
      [['escape', 'D302', 0.2], ['wanderer', 'R', 1.0], ['ivswing', 'L', 2.2]],
      [['spammer', 'D303', 0.3], ['crutch', 'R', 1.0], ['wanderer', 'L', 1.6], ['bell', 'D304', 2.4]],
    ] },
    { at: 1150, lock: 1060, title: 'ELEVATOR BANK', waves: [
      [['wanderer', 'EB', 0.8], ['sundowner', 'EB', 1.1], ['escape', 'EB', 1.4]],
      [['elite', 'EC', 0.8], ['spammer', 'EC', 1.2], ['crutch', 'R', 2.4]],
      [['visitor', 'EB', 0.6], ['bell', 'EB', 1.0], ['sundowner', 'L', 2.0]],
    ] },
    { at: 1700, lock: 1600, waves: [
      [['ivswing', 'D306', 0.3], ['escape', 'L', 0.9], ['sundowner', 'R', 1.6]],
      [['wanderer', 'D307', 0.2], ['bell', 'D308', 1.0], ['ivswing', 'R', 1.8], ['escape', 'L', 2.4]],
      [['elite', 'R', 0.4], ['crutch', 'L', 1.0]],
    ] },
    { at: 2300, lock: 2200, waves: [
      [['visitor', 'R', 0.4], ['wanderer', 'D310', 1.0], ['escape', 'L', 1.6]],
      [['sundowner', 'D311', 0.3], ['elite', 'R', 0.9], ['ivswing', 'L', 1.5], ['visitor', 'D309', 2.6], ['bell', 'L', 3.2]],
    ] },
    { at: 3080, lock: 3060, boss: 'tilly', waves: [] },
  ],
  bossArena: 3060,
};
export const DIFF = { easy: { dmg: 0.65, hp: 0.85, cap: 3 }, normal: { dmg: 1, hp: 1, cap: 4 }, hard: { dmg: 1.35, hp: 1.2, cap: 5 } };
