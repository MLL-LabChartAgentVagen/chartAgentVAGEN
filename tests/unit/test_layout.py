"""Cutting the image into blocks, and what the plotting rectangle is left with.

The geometry this replaced was four margin numbers with two horizontal strips cut
out of them. The first thing a block layout has to prove is that it did not move
anything: with every block in its default place, the plotting rectangle and the three
strips have to come out where they always were, at every image size and every margin
set. After that, moving one block is a table edit rather than a new branch.
"""

import pytest

from chartgen.common.geometry import axes_rect
from chartgen.interfaces.style import STYLE_DOMAINS
from chartgen.s03_render.draw.layout import Block, EDGES, compose
from chartgen.s03_render.style import (
    MARGIN_SETS, block_spans, default, gutters,
)

SIZES = STYLE_DOMAINS["image_size"].domain
SETS = tuple(MARGIN_SETS)


def default_blocks(setting: str) -> list[Block]:
    """The three blocks where they sit when nothing asks for anything else."""
    spans = block_spans(MARGIN_SETS[setting])
    home = {"text": "top", "legend": "bottom", "foot": "bottom"}
    return [Block(name, home[name], *spans[name]) for name in ("text", "legend", "foot")]


@pytest.mark.parametrize("size", SIZES)
@pytest.mark.parametrize("setting", SETS)
class TestTheDefaultLayoutIsTheOldOne:
    def test_the_plotting_rectangle_has_not_moved(self, size, setting):
        made = compose(size, gutters(MARGIN_SETS[setting]), default_blocks(setting))
        assert made.plot.as_tuple() == axes_rect(size, **MARGIN_SETS[setting]).as_tuple()

    def test_the_three_strips_are_where_they_were(self, size, setting):
        """The text band took 14-96 of the top margin, the legend 44-68 of the
        bottom and the foot line 76-110 of it."""
        margins = MARGIN_SETS[setting]
        made = compose(size, gutters(margins), default_blocks(setting))
        w, _ = size
        top, bottom = margins["top"], margins["bottom"]
        floor = size[1] - bottom
        want = {
            "text": (margins["left"], 14.0 / 132.0 * top,
                     w - margins["right"], 96.0 / 132.0 * top),
            "legend": (margins["left"], floor + 44.0 / 120.0 * bottom,
                       w - margins["right"], floor + 68.0 / 120.0 * bottom),
            "foot": (margins["left"], floor + 76.0 / 120.0 * bottom,
                     w - margins["right"], floor + 110.0 / 120.0 * bottom),
        }
        for name, expected in want.items():
            got = made.block(name).box.as_tuple()
            assert got == pytest.approx(expected, abs=0.01), name

    def test_every_block_spans_the_plotting_area(self, size, setting):
        made = compose(size, gutters(MARGIN_SETS[setting]), default_blocks(setting))
        for block in made.blocks:
            assert (block.box.x0, block.box.x1) == (made.plot.x0, made.plot.x1)


class TestMovingABlock:
    def blocks(self, setting: str, name: str, edge: str, thickness: float = 0.0):
        out = []
        for block in default_blocks(setting):
            if block.name == name:
                block = Block(name, edge, 8.0, thickness or block.thickness, 8.0)
            out.append(block)
        return out

    def test_a_block_on_a_side_narrows_the_plotting_area_by_what_it_costs(self):
        margins = MARGIN_SETS["normal"]
        before = compose((900, 600), gutters(margins), default_blocks("normal"))
        after = compose((900, 600), gutters(margins),
                        self.blocks("normal", "legend", "right", 120.0))
        assert after.plot.x1 == before.plot.x1 - (120.0 + 16.0)
        assert after.plot.y1 > before.plot.y1, "the bottom gets its room back"

    def test_a_side_block_spans_the_plotting_area_the_other_way(self):
        made = compose((900, 600), gutters(MARGIN_SETS["normal"]),
                       self.blocks("normal", "legend", "right", 120.0))
        legend = made.block("legend").box
        assert (legend.y0, legend.y1) == (made.plot.y0, made.plot.y1)

    def test_two_blocks_on_one_edge_stack_outward_and_do_not_meet(self):
        made = compose((900, 600), gutters(MARGIN_SETS["normal"]),
                       self.blocks("normal", "text", "bottom"))
        boxes = sorted((made.block(n).box for n in ("text", "legend", "foot")),
                       key=lambda b: b.y0)
        for near, far in zip(boxes, boxes[1:]):
            assert near.y1 <= far.y0 + 0.01

    def test_the_edges_are_cut_in_an_order_that_settles_the_width_first(self):
        """A top block spans the plotting area's width, so a side block has to be
        taken out before the width is known."""
        assert EDGES[:2] == ("left", "right")


class TestRoomIsKeptWhetherOrNotItIsUsed:
    """A block that shrank when empty would move the plotting area, and every box
    already recorded against it would be wrong."""

    def test_an_empty_block_costs_its_edge_the_same(self):
        margins = MARGIN_SETS["normal"]
        full = compose((900, 600), gutters(margins), default_blocks("normal"))
        empty = compose((900, 600), gutters(margins),
                        [Block(b.name, b.edge, b.lead, b.thickness, b.trail,
                               occupied=False) for b in default_blocks("normal")])
        assert empty.plot.as_tuple() == full.plot.as_tuple()

    def test_only_an_occupied_block_bounds_what_may_be_written(self):
        margins = MARGIN_SETS["normal"]
        blocks = default_blocks("normal")
        full = compose((900, 600), gutters(margins), blocks)
        empty = compose((900, 600), gutters(margins),
                        [Block(b.name, b.edge, b.lead, b.thickness, b.trail,
                               occupied=b.edge != "bottom") for b in blocks])
        assert empty.limit("bottom") > full.limit("bottom")
        assert empty.plot.as_tuple() == full.plot.as_tuple(), "and nothing moved"


def test_the_canvas_composes_before_it_draws():
    """Nothing here measures a drawn artist. That is the whole difference from
    auto-layout, which measures artists and then moves the axes."""
    from chartgen.s03_render.draw.canvas import Canvas

    canvas = Canvas(default())
    assert canvas.panels == []
    assert canvas.full_rect().as_tuple() == axes_rect(
        default().image_size, **MARGIN_SETS[default().margins]).as_tuple()
