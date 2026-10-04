"""v0.8 sprites: Nasty Nate's rolling office chair (side view, facing right: backrest on the left, behind him)."""
from __future__ import annotations

from rig import INK, Raster


def office_chair(spin=0):
    """Black mesh office chair on a five-star base. spin 0/1 swaps the caster highlights so the wheels look like they roll.
    Anchor (13, 33) = floor under the gas cylinder; the seat top sits 17 px above the floor."""
    S = Raster(28, 35)
    mesh, mesh_s, frame, chrome = "#34363f", "#22232a", "#5a5e6a", "#b4bcc8"
    S.rect(2, 1, 6, 16, INK); S.rect(3, 2, 4, 14, mesh); S.rect(3, 2, 1, 14, "#4a4c58")          # backrest
    S.rect(6, 15, 3, 3, frame)                                                                    # back post
    S.rect(4, 15, 21, 4, INK); S.rect(5, 16, 19, 2, mesh); S.rect(5, 16, 19, 1, "#4a4c58")      # seat cushion
    S.rect(8, 19, 12, 1, mesh_s)
    S.rect(18, 11, 6, 2, INK); S.rect(19, 11, 4, 1, frame); S.rect(20, 13, 2, 3, frame)          # armrest
    S.rect(13, 20, 3, 7, INK); S.rect(14, 20, 1, 7, chrome)                                       # gas cylinder
    S.rect(3, 27, 23, 2, INK); S.rect(4, 27, 21, 1, frame)                                        # five-star base (side)
    for i, x in enumerate((3, 13, 23)):                                                           # casters
        S.ellipse((x + 1, 31), 2.2, 2.2, "#1c1c22", None, rim=False)
        S.set(x + (1 if (i + spin) % 2 else 0), 30 + spin, "#6a6e7a")
    return S
