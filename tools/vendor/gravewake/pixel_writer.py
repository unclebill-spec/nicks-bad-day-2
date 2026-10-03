"""Pixel writer.

Earmarked for Gravewake and for later games.
It draws real pixels: one color per pixel, no blending, no anti-alias, no new hues
beyond the colors you pass in. A tile is 16×16 unless you ask for another size.

Use it when a zone needs ground and a downloaded sheet does not fit.
Do not scale a photo down and call it a tile. Draw the pixels.
"""

from __future__ import annotations

import random
from PIL import Image


def _rgba(hex_color: str) -> tuple[int, int, int, int]:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


class Tile:
    """One tile. Empty pixels stay transparent."""

    def __init__(self, n: int = 16):
        self.n = n
        self.p: list[list[str | None]] = [[None] * n for _ in range(n)]

    def set(self, x: int, y: int, color: str | None) -> None:
        if color and 0 <= x < self.n and 0 <= y < self.n:
            self.p[y][x] = color

    def rect(self, x: int, y: int, w: int, h: int, color: str) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def fill(self, color: str) -> None:
        self.rect(0, 0, self.n, self.n, color)

    def image(self) -> Image.Image:
        im = Image.new("RGBA", (self.n, self.n), (0, 0, 0, 0))
        px = im.load()
        for y in range(self.n):
            for x in range(self.n):
                c = self.p[y][x]
                if c:
                    px[x, y] = _rgba(c)
        return im


def strip(tiles: list[Tile]) -> Image.Image:
    """Lay tiles in a row. The game reads them as columns of 16."""
    n = tiles[0].n
    out = Image.new("RGBA", (n * len(tiles), n), (0, 0, 0, 0))
    for i, tile in enumerate(tiles):
        out.paste(tile.image(), (i * n, 0))
    return out


def preview(tiles: list[Tile], scale: int = 4) -> Image.Image:
    """Nearest-neighbor contact sheet, so the pixels stay countable."""
    row = strip(tiles)
    return row.resize((row.width * scale, row.height * scale), Image.NEAREST)


def _inset(tile: Tile, color: str, pad: int = 1) -> None:
    """Keep a solid border so neighboring tiles of the same ground do not seam."""
    n = tile.n
    tile.rect(0, 0, n, pad, color)
    tile.rect(0, n - pad, n, pad, color)
    tile.rect(0, 0, pad, n, color)
    tile.rect(n - pad, 0, pad, n, color)


def grass(seed: int, base: str, dark: str, tip: str, spot: str, kind: int) -> Tile:
    """Meadow tile. Blades are 1px stems in clumps. The border stays the base color."""
    t = Tile()
    t.fill(base)
    rng = random.Random(seed)
    # Two clumps, so the tile is grass and not a flat square with three dots.
    for clump in range(2):
        cx = 3 + clump * 5 + (kind % 2)
        cy = 4 + (clump * 3 + kind) % 5
        for i in range(3):
            x = cx + (i - 1)
            h = 3 + ((seed + i + clump) % 3)
            y = cy
            t.rect(x, y, 1, h, dark)
            t.set(x, y, tip)
        t.rect(cx - 1, cy + 3, 3, 1, dark)
    if kind == 2:
        t.rect(6, 8, 3, 2, spot)
        t.set(7, 7, tip)
    elif kind == 3:
        t.rect(9, 9, 2, 2, dark)
        t.set(9, 8, spot)
    elif kind == 5:
        t.rect(4, 10, 3, 2, spot)
        t.set(5, 9, tip)
    elif kind == 7:
        t.set(8, 7, spot)
        t.set(9, 7, tip)
        t.set(8, 8, dark)
    elif kind % 2 == 0:
        t.set(5, 6, tip)
        t.set(11, 9, dark)
    _inset(t, base)
    if rng.randrange(2) == 0:
        t.set(4 + (seed % 7), 5 + (kind % 6), dark)
        _inset(t, base)
    return t


def soil(seed: int, base: str, dark: str, light: str, speck: str, kind: int) -> Tile:
    """Packed earth. Clods are 2×2, not single-pixel noise."""
    t = Tile()
    t.fill(base)
    rng = random.Random(seed)
    for i in range(3):
        x = 2 + rng.randrange(10)
        y = 2 + rng.randrange(10)
        t.rect(x, y, 2, 2, dark if i % 2 == 0 else light)
    if kind % 3 == 0:
        t.rect(6, 7, 4, 1, dark)
    elif kind % 3 == 1:
        t.rect(4, 5, 2, 2, speck)
    else:
        t.set(10, 4, light)
        t.set(11, 4, speck)
        t.set(10, 5, dark)
    _inset(t, base)
    return t


def brick(seed: int, fill: str, mortar: str, hi: str, shade: str) -> Tile:
    """Two brick courses. Joints stay on the same pixels so the floor tiles."""
    t = Tile()
    t.fill(mortar)
    # Top course, joint at x = 7. Bottom course, joints at x = 3 and x = 11.
    t.rect(0, 0, 7, 7, fill)
    t.rect(8, 0, 8, 7, fill)
    t.rect(0, 8, 3, 7, fill)
    t.rect(4, 8, 7, 7, fill)
    t.rect(12, 8, 4, 7, fill)
    for x, y, w, h in ((0, 0, 7, 7), (8, 0, 8, 7), (0, 8, 3, 7), (4, 8, 7, 7), (12, 8, 4, 7)):
        t.rect(x, y, w, 1, hi)
        t.rect(x, y + h - 1, w, 1, shade)
    rng = random.Random(seed)
    for _ in range(rng.randrange(1, 3)):
        t.set(rng.randrange(1, 15), rng.randrange(1, 14), shade if rng.randrange(2) else hi)
    # Put the mortar joints back. A chip must not erase the seam.
    t.rect(7, 0, 1, 7, mortar)
    t.rect(3, 8, 1, 7, mortar)
    t.rect(11, 8, 1, 7, mortar)
    t.rect(0, 7, 16, 1, mortar)
    t.rect(0, 15, 16, 1, mortar)
    return t


def pit(floor: str, hole: str, rim: str) -> Tile:
    """A square hole. The outer pixels stay the floor color."""
    t = Tile()
    t.fill(floor)
    t.rect(3, 3, 10, 10, rim)
    t.rect(4, 4, 8, 8, hole)
    t.rect(5, 5, 4, 2, rim)
    t.set(6, 6, floor)
    return t


def water(deep: str, mid: str, light: str, frame: int) -> Tile:
    """One frame of a pond. The ripple moves. The border stays deep so it tiles."""
    t = Tile()
    t.fill(deep)
    t.rect(0, 8, 16, 8, mid)
    y = 3 + (frame % 4)
    t.rect(2, y, 6, 1, light)
    t.rect(9, (y + 5) % 12 + 2, 5, 1, light)
    _inset(t, deep)
    return t


def field(seed: int, base: str, dark: str, light: str, kind: int) -> Tile:
    """Snow, sand, ash, or swamp. Same rule: clumps, then a solid border."""
    t = Tile()
    t.fill(base)
    rng = random.Random(seed + kind * 17)
    for i in range(2 + kind % 2):
        x = 2 + rng.randrange(10)
        y = 2 + rng.randrange(10)
        t.rect(x, y, 2 + (i % 2), 1 + (kind % 2), light if i == 0 else dark)
    if kind == 1:
        t.rect(7, 8, 1, 3, dark)
        t.rect(10, 8, 1, 3, dark)
    _inset(t, base)
    return t
