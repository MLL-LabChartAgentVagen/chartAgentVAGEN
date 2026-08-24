"""Cutting the image into blocks, and leaving the plotting area what is left.

The layout used to be two fixed strips of the top margin and one of the bottom, with
the plotting rectangle computed from four margin numbers. That fixed the answer to a
question real reports answer differently from page to page: a legend runs down the
right of one and across the bottom of the next, and the strip a title sits in is
above the plot on most pages and below it on some.

So the margins are no longer the input. Each block states which edge it wants and how
thick it is, the blocks on an edge stack outward from the plotting area, and the
plotting rectangle is whatever the four edges leave. With every block in its default
place the numbers come out identical to the old margins -- that is the test this had
to pass -- and moving one is now a table edit rather than a new branch.

Two rules survive, and they are why this is a fold and not a search:

* **It is composed before anything is drawn.** Nothing here measures an artist. The
  one thing that has to be measured, how wide a side legend needs to be, is asked of
  the canvas by the caller and passed in as a thickness, before the first panel.
* **A block keeps its room whether or not it holds anything.** `occupied` says
  whether anything will be written in it, and that decides only what the fitting
  passes treat as a limit; it never changes a box. A block that shrank when empty
  would move the plotting area and invalidate every box recorded against it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence

from ...common.geometry import Box, axes_rect
from ...interfaces.record import Layout, LayoutBlock

Edge = Literal["top", "bottom", "left", "right"]

#: The four edges, in the order they are cut. Sides first: a top block spans the
#: plotting area's width, so the width has to be settled before it can be placed.
EDGES: tuple[Edge, ...] = ("left", "right", "top", "bottom")

SIDES: tuple[str, ...] = ("left", "right")


@dataclass(frozen=True)
class Block:
    """A request for room on one edge, before anything has been placed.

    `lead` is clear space on the plot side and `trail` clear space on the far side.
    Both are part of what the block costs its edge, which keeps the arithmetic a sum:
    an edge's total is its gutter plus every block's lead, thickness and trail.
    """

    name: str
    edge: str
    lead: float
    thickness: float
    trail: float
    occupied: bool = True

    @property
    def cost(self) -> float:
        return self.lead + self.thickness + self.trail


def compose(image_size: tuple[int, int], gutters: dict[str, float],
            blocks: Sequence[Block]) -> Layout:
    """The plotting rectangle and every block's box, in image pixels.

    A gutter is the room an edge keeps for what the axis itself draws -- tick labels
    and an axis title -- and is what is left of the old margin once the blocks that
    used to live inside it are taken out.
    """
    total = {edge: gutters.get(edge, 0.0)
             + sum(b.cost for b in blocks if b.edge == edge) for edge in EDGES}
    plot = axes_rect(image_size, left=total["left"], top=total["top"],
                     right=total["right"], bottom=total["bottom"])

    placed: list[LayoutBlock] = []
    for edge in EDGES:
        offset = gutters.get(edge, 0.0)
        for block in [b for b in blocks if b.edge == edge]:
            near, far = offset + block.lead, offset + block.lead + block.thickness
            if edge == "top":
                box = Box(plot.x0, plot.y0 - far, plot.x1, plot.y0 - near)
            elif edge == "bottom":
                box = Box(plot.x0, plot.y1 + near, plot.x1, plot.y1 + far)
            elif edge == "left":
                box = Box(plot.x0 - far, plot.y0, plot.x0 - near, plot.y1)
            else:
                box = Box(plot.x1 + near, plot.y0, plot.x1 + far, plot.y1)
            placed.append(LayoutBlock(block.name, edge, box, block.occupied))
            offset += block.cost
    return Layout(plot, tuple(placed), image_size=tuple(image_size))
