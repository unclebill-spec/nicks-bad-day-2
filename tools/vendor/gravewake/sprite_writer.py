"""Sprite writer.

Earmarked for Gravewake and for later games.
It draws 16×32 people and creatures as real pixels: one color per pixel,
a 1px outline, no blending. You pass the colors. It does not invent hues.

A later game can call `human` and `creature` with its own palette.
"""

from __future__ import annotations

from PIL import Image


def _rgba(color: str) -> tuple[int, int, int, int]:
    h = color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


class Sprite:
    def __init__(self, w: int = 16, h: int = 32):
        self.w = w
        self.h = h
        self.p: list[list[str | None]] = [[None] * w for _ in range(h)]

    def set(self, x: int, y: int, color: str | None) -> None:
        if color and 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = color

    def rect(self, x: int, y: int, w: int, h: int, color: str) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def outline(self, ink: str = "#140c10") -> None:
        src = [row[:] for row in self.p]
        for y in range(self.h):
            for x in range(self.w):
                if src[y][x]:
                    continue
                if any(
                    0 <= y + dy < self.h and 0 <= x + dx < self.w and src[y + dy][x + dx]
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                ):
                    self.p[y][x] = ink

    def image(self) -> Image.Image:
        im = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        px = im.load()
        for y in range(self.h):
            for x in range(self.w):
                c = self.p[y][x]
                if c:
                    px[x, y] = _rgba(c)
        return im


def strip(sprites: list[Sprite]) -> Image.Image:
    w = sprites[0].w
    h = sprites[0].h
    out = Image.new("RGBA", (w * len(sprites), h), (0, 0, 0, 0))
    for i, sprite in enumerate(sprites):
        out.paste(sprite.image(), (i * w, 0))
    return out


INK = "#140c10"
SKIN = "#e8b898"
PALE = "#ecd8cc"
BOOT = "#2a241c"
GOLD = "#e0c060"
BONE = "#f4ecdc"

PEOPLE = {
    "warrior": {"cloth": "#2a4568", "trim": "#c4b48a", "skin": SKIN, "hat": "helm", "hatc": "#8a9098", "metal": "#8a9098", "weapon": "sword"},
    "wizard": {"cloth": "#4a2870", "trim": "#c4b4e0", "skin": SKIN, "hat": "point", "hatc": "#2a1848", "metal": "#c4b4e0", "weapon": "wand"},
    "assassin": {"cloth": "#243828", "trim": "#1a1a1a", "skin": SKIN, "hat": "hood", "hatc": "#1a2818", "metal": "#8a9090", "weapon": "dagger"},
    "vampire": {"cloth": "#6a2030", "trim": "#1a1014", "skin": PALE, "hat": "widow", "hatc": "#1a1014", "metal": "#e0c060", "weapon": "none"},
    "priest": {"cloth": "#e6e0d4", "trim": "#c4b48a", "skin": SKIN, "hat": "hood", "hatc": "#f4f0e8", "metal": "#c4b48a", "weapon": "none"},
    "witch": {"cloth": "#4a1848", "trim": "#c44868", "skin": "#f0c8b0", "hat": "point", "hatc": "#2a1028", "metal": "#c44868", "weapon": "wand"},
    "shade": {"cloth": "#1a2438", "trim": "#8aa0c0", "skin": "#9eb0c8", "hat": "hood", "hatc": "#101820", "metal": "#8aa0c0", "weapon": "none"},
    "mystic": {"cloth": "#241848", "trim": "#e0c868", "skin": SKIN, "hat": "point", "hatc": "#140c28", "metal": "#e0c868", "weapon": "wand"},
    "guard": {"cloth": "#2a3140", "trim": "#c4b48a", "skin": SKIN, "hat": "helm", "hatc": "#8a9098", "metal": "#8a9098", "weapon": "sword"},
    "hunter": {"cloth": "#3a3228", "trim": "#6a2030", "skin": SKIN, "hat": "hood", "hatc": "#2a241c", "metal": "#c4b48a", "weapon": "dagger"},
    "undertaker": {"cloth": "#1a1a1c", "trim": "#4a4a50", "skin": "#c8b8a8", "hat": "hood", "hatc": "#101014", "metal": "#4a4a50", "weapon": "none"},
    "zeppelin": {"cloth": "#4a4038", "trim": "#c4b48a", "skin": SKIN, "hat": "helm", "hatc": "#6a5a40", "metal": "#c4b48a", "weapon": "none"},
    "inn": {"cloth": "#6a3a28", "trim": "#e6dcc8", "skin": SKIN, "hat": "hood", "hatc": "#e6dcc8", "metal": "#c4b48a", "weapon": "none"},
    "shop": {"cloth": "#2a4a38", "trim": "#c4b48a", "skin": SKIN, "hat": "hood", "hatc": "#1a3028", "metal": "#c4b48a", "weapon": "none"},
    "guild": {"cloth": "#2a3a6a", "trim": "#e0c060", "skin": SKIN, "hat": "hood", "hatc": "#1a2848", "metal": "#e0c060", "weapon": "sword"},
    "bank": {"cloth": "#1e3a32", "trim": "#d8c878", "skin": SKIN, "hat": "hood", "hatc": "#142820", "metal": "#d8c878", "weapon": "none"},
    "casino": {"cloth": "#8a2030", "trim": "#f0e2c8", "skin": SKIN, "hat": "hood", "hatc": "#2a1018", "metal": "#f0e2c8", "weapon": "none"},
    "patron": {"cloth": "#3a1830", "trim": "#c4a050", "skin": SKIN, "hat": "hood", "hatc": "#1a1218", "metal": "#c4a050", "weapon": "none"},
    "smith": {"cloth": "#5a4030", "trim": "#2a2a2e", "skin": "#c08060", "hat": "hood", "hatc": "#3a2a22", "metal": "#8a9098", "weapon": "sword"},
    "tailor": {"cloth": "#6a4060", "trim": "#e6dcc8", "skin": SKIN, "hat": "hood", "hatc": "#3a2038", "metal": "#e6dcc8", "weapon": "none"},
    "fisher": {"cloth": "#1c3040", "trim": "#6a8a48", "skin": "#d2c0b4", "hat": "hood", "hatc": "#101820", "metal": "#6a5030", "weapon": "wand"},
    "merchant": {"cloth": "#6a5040", "trim": "#c4a15a", "skin": SKIN, "hat": "hood", "hatc": "#3a2818", "metal": "#c4a15a", "weapon": "none"},
    "alchemist": {"cloth": "#4a1848", "trim": "#6a8a32", "skin": "#f0c8b0", "hat": "point", "hatc": "#2a1028", "metal": "#6a8a32", "weapon": "wand"},
    "portal": {"cloth": "#4a2a78", "trim": "#c4b4e0", "skin": SKIN, "hat": "point", "hatc": "#2a1848", "metal": "#c4b4e0", "weapon": "wand"},
}

POSES = ("stand", "idle", "walk0", "walk1", "walk2", "swing0", "swing1", "swing2", "cast0", "cast1", "cast2")


def _legs(s: Sprite, frame: int, boot: str) -> None:
    if frame == 1:
        s.rect(3, 23, 3, 6, boot)
        s.rect(10, 21, 3, 8, boot)
    elif frame == 2:
        s.rect(4, 21, 3, 8, boot)
        s.rect(10, 23, 3, 6, boot)
    else:
        s.rect(4, 22, 3, 7, boot)
        s.rect(9, 22, 3, 7, boot)


def _rank(s: Sprite, rank: str) -> None:
    if rank == "boss":
        s.rect(5, 2, 6, 1, GOLD)
        s.set(4, 3, GOLD)
        s.set(11, 3, GOLD)
    elif rank == "rare":
        s.set(6, 16, GOLD)
        s.set(10, 17, GOLD)
    elif rank == "mini":
        s.rect(6, 4, 4, 1, "#6a5848")


def human(role: str, pose: str | int = "stand", rank: str = "mob", sash: str | None = None) -> Sprite:
    """A 3/4 person. Poses: stand, idle, walk0, walk1, swing, cast."""
    if isinstance(pose, int):
        pose = "walk0" if pose else "stand"
    spec = PEOPLE[role]
    frame = 1 if pose in ("walk0", "swing1") else 2 if pose in ("walk2", "swing2") else 0
    s = Sprite()
    _legs(s, frame, BOOT)
    s.rect(3, 13, 10, 10, spec["cloth"])
    s.rect(3, 13, 10, 2, spec["trim"])
    if sash:
        s.rect(4, 18, 8, 2, sash)
    if pose == "swing0":
        s.rect(1, 11, 2, 5, spec["cloth"])
        s.rect(0, 12, 2, 2, spec["metal"])
        s.rect(13, 15, 2, 5, spec["cloth"])
        s.set(1, 10, spec["skin"])
    elif pose in ("swing", "swing1"):
        s.rect(1, 14, 2, 5, spec["cloth"])
        s.rect(13, 10, 3, 2, "#e8dcc8")
        s.rect(14, 8, 2, 2, spec["metal"])
        s.set(1, 18, spec["skin"])
    elif pose == "swing2":
        s.rect(1, 16, 2, 4, spec["cloth"])
        s.rect(12, 16, 3, 2, spec["metal"])
        s.set(14, 18, spec["skin"])
    elif pose == "cast0":
        s.rect(5, 12, 2, 3, spec["skin"])
        s.rect(9, 12, 2, 3, spec["skin"])
        s.set(7, 11, spec["metal"])
    elif pose in ("cast", "cast1"):
        s.rect(1, 10, 2, 5, spec["cloth"])
        s.rect(13, 8, 2, 5, spec["skin"])
        s.set(1, 9, spec["skin"])
        s.set(14, 6, GOLD)
        s.set(13, 5, "#fff8e0")
    elif pose == "cast2":
        s.rect(13, 9, 2, 5, spec["skin"])
        s.set(12, 3, GOLD)
        s.set(15, 4, "#fff8e0")
        s.set(11, 6, spec["metal"])
    elif pose == "idle":
        s.rect(1, 14, 2, 6, spec["cloth"])
        s.rect(13, 11, 2, 4, spec["cloth"])
        s.set(1, 19, spec["skin"])
        s.set(14, 10, spec["skin"])
    else:
        s.rect(1, 14, 2, 6, spec["cloth"])
        s.rect(13, 14, 2, 6, spec["cloth"])
        s.set(1, 19, spec["skin"])
        s.set(14, 19, spec["skin"])
    s.rect(4, 7, 8, 6, spec["skin"])
    if pose == "idle":
        s.rect(5, 9, 2, 1, spec["skin"])
        s.rect(8, 9, 2, 1, spec["skin"])
    else:
        s.set(5, 9, INK)
        s.set(9, 9, INK)
    s.rect(6, 11, 3, 1, "#6a2030" if role == "vampire" else "#a06050")
    hat = spec["hat"]
    if rank != "mini":
        if hat == "helm":
            s.rect(4, 5, 8, 3, spec["metal"])
            s.rect(6, 4, 4, 1, spec["metal"])
        elif hat == "point":
            s.rect(7, 2, 2, 3, spec["hatc"])
            s.rect(3, 5, 10, 3, spec["hatc"])
        elif hat == "hood":
            s.rect(3, 5, 10, 3, spec["hatc"])
            s.rect(4, 4, 8, 2, spec["hatc"])
        elif hat == "widow":
            s.rect(4, 4, 8, 3, spec["hatc"])
            s.set(6, 6, spec["hatc"])
            s.set(9, 6, spec["hatc"])
    weapon = spec["weapon"]
    if pose not in ("swing0", "swing1", "swing2", "swing", "cast0", "cast1", "cast2", "cast"):
        if weapon == "sword":
            s.rect(14, 8, 1, 8, "#c4b48a")
            s.rect(13, 16, 3, 1, "#5a4030")
        elif weapon == "wand":
            s.rect(14, 7, 1, 7, "#5a4030")
            s.set(14, 6, GOLD)
        elif weapon == "dagger":
            s.rect(14, 13, 1, 4, "#c8c8d0")
    elif pose == "swing2" and weapon == "none":
        s.rect(12, 16, 3, 2, spec["trim"])
        s.rect(13, 10, 3, 2, spec["trim"])
    _rank(s, rank)
    s.outline()
    return s


def _eyes(s: Sprite, x: int, y: int) -> None:
    s.set(x, y, INK)
    s.set(x + 3, y, INK)


def creature(kind: str, pose: str | int = "stand", rank: str = "mob") -> Sprite:
    """One family. Poses match a person: stand, idle, walk0, walk1, swing, cast."""
    if isinstance(pose, int):
        pose = "walk0" if pose else "stand"
    if kind == "witch":
        return human("witch", pose, rank)
    if kind == "vampire":
        return human("vampire", pose, rank)
    frame = 1 if pose in ("walk0", "swing1") else 2 if pose in ("walk2", "swing2") else 0
    step = 1 if pose in ("walk0", "swing1") else 0
    s = Sprite()
    if kind == "zombie":
        _legs(s, frame, "#3a4a28")
        s.rect(3, 13, 10, 9, "#6a7a48")
        s.rect(3, 13, 10, 3, "#4a3828")
        s.rect(0, 14, 3, 6, "#5a6a38")
        s.rect(13, 14, 3, 6, "#5a6a38")
        s.rect(4, 6, 8, 7, "#7a8a58")
        _eyes(s, 5, 8)
        s.rect(6, 11, 4, 1, "#6a2030")
    elif kind == "skeleton":
        _legs(s, frame, BONE)
        s.rect(5, 13, 6, 8, BONE)
        s.rect(5, 15, 6, 1, "#d8cfc0")
        s.rect(5, 18, 6, 1, "#d8cfc0")
        s.rect(2, 14, 3, 5, BONE)
        s.rect(11, 14, 3, 5, BONE)
        s.rect(4, 4, 8, 7, BONE)
        _eyes(s, 6, 6)
        s.rect(6, 9, 4, 1, "#c8b8a8")
    elif kind == "ghost":
        s.rect(4, 6, 8, 4, "#e8eef8")
        s.rect(3, 10, 10, 12, "#c5d4e8")
        s.rect(4, 22, 2, 5, "#9aa8c0")
        s.rect(7, 23, 2, 4, "#c5d4e8")
        s.rect(10, 22, 2, 5, "#9aa8c0")
        _eyes(s, 5, 12)
        s.rect(6, 15, 4, 1, "#8aa0c0")
    elif kind == "bat":
        wing = 1 if step else 0
        s.rect(1, 10 + wing, 5, 4, "#3a2a44")
        s.rect(10, 10 + wing, 5, 4, "#3a2a44")
        s.rect(0, 9 + wing, 4, 2, "#5a4060")
        s.rect(12, 9 + wing, 4, 2, "#5a4060")
        s.rect(5, 12, 6, 6, "#2a1c30")
        _eyes(s, 6, 14)
        s.rect(7, 16, 2, 1, "#e07a2f")
    elif kind == "ghoul":
        _legs(s, frame, "#4a3424")
        s.rect(3, 14, 10, 8, "#7a5a3a")
        s.rect(2, 12, 12, 4, "#6a4a30")
        s.rect(0, 13, 3, 7, "#5a4030")
        s.rect(13, 13, 3, 7, "#5a4030")
        s.rect(4, 5, 8, 7, "#8a6a4a")
        _eyes(s, 5, 7)
        s.rect(6, 10, 4, 1, "#6a2030")
    elif kind == "witch":
        return human("witch", frame, rank)
    elif kind == "lantern":
        _legs(s, frame, "#3a2818")
        s.rect(3, 12, 10, 10, "#6a5038")
        s.rect(4, 6, 8, 7, "#e07a2f")
        s.rect(6, 4, 4, 2, "#2a4a20")
        _eyes(s, 5, 8)
        s.rect(6, 11, 4, 1, INK)
        s.set(7, 7, "#f4e27a")
    elif kind == "scarecrow":
        s.rect(7, 8, 2, 16, "#6a5030")
        s.rect(2, 12, 12, 2, "#6a5030")
        s.rect(4, 16, 3, 6, "#c4a15a")
        s.rect(9, 16, 3, 6, "#8a6840")
        s.rect(4, 4, 8, 6, "#c4a15a")
        _eyes(s, 5, 6)
        s.rect(6, 9, 4, 1, INK)
        s.rect(4, 24 + step, 2, 3, "#5a4030")
        s.rect(10, 23 - step, 2, 4, "#5a4030")
    elif kind == "wolf":
        s.rect(3, 14, 10, 8, "#5a4030")
        s.rect(2, 8, 4, 6, "#4a3428")
        s.rect(10, 8, 4, 6, "#4a3428")
        s.set(3, 9, "#f0e0b0")
        s.set(12, 9, "#f0e0b0")
        _eyes(s, 5, 16)
        s.rect(6, 18, 4, 2, "#3a2818")
        s.rect(3, 22 + step, 3, 4, "#3a2818")
        s.rect(10, 21 - step, 3, 5, "#3a2818")
    elif kind == "mummy":
        _legs(s, frame, "#e6d2a2")
        s.rect(4, 6, 8, 16, "#f0e2c0")
        s.rect(3, 9, 10, 2, "#c4b48a")
        s.rect(3, 14, 10, 2, "#c4b48a")
        s.rect(3, 19, 10, 2, "#c4b48a")
        _eyes(s, 6, 8)
    elif kind == "vampire":
        return human("vampire", frame, rank)
    elif kind == "tree":
        s.rect(7, 16, 3, 12, "#4a3020")
        s.rect(3, 6, 10, 12, "#3d4a28")
        s.rect(5, 4, 6, 4, "#4a5a30")
        _eyes(s, 5, 8)
        s.rect(6, 12, 4, 2, "#1a1008")
        s.rect(1, 10, 3, 3, "#2a3820")
        s.rect(12, 9, 3, 3, "#2a3820")
    elif kind == "lich":
        s.rect(4, 22, 3, 6, BONE)
        s.rect(9, 22, 3, 6, BONE)
        s.rect(3, 12, 10, 10, "#8eb4d8")
        s.rect(4, 4, 8, 8, BONE)
        _eyes(s, 6, 7)
        s.rect(5, 2, 6, 2, GOLD)
        s.rect(3, 18, 10, 2, "#d8c8a0")
    elif kind == "horse":
        s.rect(3, 14, 8, 8, "#2a2428")
        s.rect(9, 8, 5, 8, "#3a3030")
        s.rect(12, 4, 3, 6, "#2a2428")
        s.set(13, 6, "#f0e2c8")
        s.rect(8, 6, 3, 4, "#1a1418")
        s.rect(2, 22 + step, 2, 5, "#1a1418")
        s.rect(6, 21 - step, 2, 6, "#1a1418")
        s.rect(10, 22 + step, 2, 5, "#1a1418")
        s.rect(13, 23 - step, 2, 4, "#1a1418")
    elif kind == "goblin":
        _legs(s, frame, "#3a4a20")
        s.rect(4, 14, 8, 8, "#6a8a32")
        s.rect(3, 8, 10, 6, "#5a7a28")
        s.rect(3, 6, 2, 3, "#3a4a20")
        s.rect(11, 6, 2, 3, "#3a4a20")
        _eyes(s, 5, 10)
        s.rect(11, 16, 4, 5, "#c4a050")
    elif kind == "cat":
        s.rect(4, 16, 8, 6, "#2a2a2e")
        s.rect(10, 14, 4, 4, "#2a2a2e")
        s.rect(3, 14, 2, 3, "#2a2a2e")
        s.rect(6, 14, 2, 3, "#2a2a2e")
        s.set(12, 15, "#e07a2f")
        s.rect(2, 20, 8, 1, "#2a2a2e")
        s.rect(4, 22 + step, 2, 2, "#1a1a1c")
        s.rect(9, 21 - step, 2, 3, "#1a1a1c")
    elif kind == "rat":
        s.rect(4, 16, 8, 5, "#8a7060")
        s.rect(11, 15, 3, 3, "#8a7060")
        s.rect(2, 18, 6, 1, "#c4a090")
        s.set(12, 16, INK)
        s.rect(4, 21 + step, 2, 2, "#5a4038")
        s.rect(9, 20 - step, 2, 3, "#5a4038")
    else:
        return human("warrior", pose, rank)
    if pose in ("swing", "swing1"):
        s.rect(13, 9, 3, 2, "#e8dcc8")
        s.rect(14, 7, 2, 2, "#f4e27a")
    elif pose == "swing0":
        s.rect(1, 10, 3, 2, "#e8dcc8")
        s.set(0, 9, "#f4e27a")
    elif pose == "swing2":
        s.rect(12, 16, 3, 2, "#e8dcc8")
        s.set(15, 18, "#f4e27a")
    elif pose in ("cast", "cast1"):
        s.rect(6, 2, 4, 2, "#f4e27a")
        s.set(7, 1, "#fff8e0")
        s.set(10, 1, "#fff8e0")
    elif pose == "cast0":
        s.rect(6, 8, 4, 2, "#f4e27a")
    elif pose == "cast2":
        s.set(4, 0, "#fff8e0")
        s.set(11, 1, "#f4e27a")
        s.set(8, 3, "#fff8e0")
    elif pose == "idle":
        s.set(14, 11, "#f4ecdc")
    _rank(s, rank)
    s.outline()
    return s
