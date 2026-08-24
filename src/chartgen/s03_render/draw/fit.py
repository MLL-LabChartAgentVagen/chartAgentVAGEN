"""Where the page's own text ends up when the room runs out.

The bands are frozen, so nothing here moves a plotting area: what gives is the type
size, and after that the position of a title inside the band it already has. Two
things this decides, both of which the record then describes:

    tick labels and axis titles   shrunk until they stay inside their band and out
                                  of each other
    value labels                  the ones a reader could not tell apart are not
                                  drawn, and their marks keep no printed value

Kept apart from the canvas because the canvas is about what is drawn and written
down; this is about what to do when two things want the same pixels.
"""

from __future__ import annotations

from typing import Sequence

from ...common.geometry import Box
from .canvas import (
    LABEL_GAP, LEFT_EDGE, PANEL_TITLE_HEIGHT, TICK_GAP, Canvas, PanelCanvas,
)


def everything(canvas: Canvas) -> None:
    """Every fitting pass, in the order they depend on each other."""
    axis_labels(canvas)
    label_overlaps(canvas)


def axis_labels(canvas: Canvas) -> None:
    """Keep everything an axis draws inside the room the frozen bands leave it.

    An axis title is placed after the tick labels, so tall rotated labels push it
    down the page -- into the legend, into the foot line, or off the image
    altogether, where the record would carry a box for text nobody can see. Two
    things give, in this order: the tick type size, because a tick label is only
    ever shortened as a last resort -- its string is what a key is read off -- and
    then the title's own position, which is pinned to the row the ticks end at.
    """
    floor = canvas.layout.limit("bottom") - 2
    # The second row of tick labels is hung under the first, so where it lands is
    # known only once the first has been measured -- and it is part of what has to
    # fit above the band below. It is therefore pinned inside the shrinking loop
    # rather than after it: pinned once at the end, a shrink that had already been
    # judged sufficient would be undone by the row moving down.
    for _ in range(4):
        canvas.fig.canvas.draw()
        for panel in canvas.panels:
            pin_second_level(canvas, panel)
        canvas.fig.canvas.draw()
        over = max((overrun(canvas, panel, floor_for(canvas, panel, floor))
                    for panel in canvas.panels), default=1.0)
        if over <= 1.0:
            break
        # The tick labels give first; the axis titles give after them. A tick label is
        # read for a key and is only ever made smaller, never shorter; an axis title
        # names the quantity and is already cut to the edge it runs along.
        if (not canvas.shrink_ticks(over) and not canvas.flatten_ticks()
                and not canvas.shrink_axis_titles(over)):
            break
    ceiling = canvas.layout.limit("top") + 2
    for _ in range(2):
        canvas.fig.canvas.draw()
        if not any(pin_title_above(canvas, panel, ceiling) for panel in canvas.panels):
            break
    canvas.fig.canvas.draw()
    for panel in canvas.panels:
        pin_second_level(canvas, panel)
    canvas.fig.canvas.draw()
    for panel in canvas.panels:
        pin_titles(canvas, panel, floor_for(canvas, panel, floor))
    # Measured, then corrected: a rotated label is anchored at its baseline rather
    # than at the middle of the box it comes out as, so where it lands is known
    # only after it is drawn.
    for _ in range(2):
        canvas.fig.canvas.draw()
        if not any(nudge(canvas, panel, floor_for(canvas, panel, floor))
                   for panel in canvas.panels):
            break


def tick_extent(canvas: Canvas, panel: PanelCanvas, below: bool = True) -> tuple[float, float]:
    """How far this panel's tick labels reach: down the page, and to the left."""
    bottom, left = panel.rect.y1, panel.rect.x0
    for label in panel.ax.get_xticklabels():
        if label.get_text():
            bottom = max(bottom, canvas.text_box(label).y1)
    for label in panel.ax.get_yticklabels():
        if label.get_text():
            left = min(left, canvas.text_box(label).x0)
    if below:
        for artist in panel.below:
            bottom = max(bottom, canvas.text_box(artist).y1)
    return bottom, left


def pin_second_level(canvas: Canvas, panel: PanelCanvas) -> None:
    """Put the second row of tick labels directly under the first.

    Hung at a fixed distance from the axis it would sit either on top of the row
    above it or a long way below it, depending on how tall that row came out --
    and either way it decides where the axis title can go.
    """
    if not panel.below:
        return
    bottom, _ = tick_extent(canvas, panel, below=False)
    offset = (bottom + 3.0 - panel.rect.y1) * 72.0 / canvas.style.dpi
    for artist in panel.below:
        artist.set_position((0.0, -offset))


def floor_for(canvas: Canvas, panel: PanelCanvas, floor: float) -> float:
    """How far down the page this panel's tick labels may reach.

    On a grid the band below the axis is not the first thing in the way: the panel on
    the next row has a strip above it holding its own title, and a slanted tick label
    from the row above reaches into it. Written over, that title is a key segment
    nobody can read -- on small multiples it is the segment that says which panel the
    marks belong to.
    """
    below = [p.rect.y0 for p in canvas.panels if p.rect.y0 > panel.rect.y1]
    return min(floor, min(below) - PANEL_TITLE_HEIGHT - 2.0) if below else floor


def overrun(canvas: Canvas, panel: PanelCanvas, floor: float) -> float:
    """By what factor this panel's tick labels exceed the room they have.

    Two ways they can: past the band below or beside the plotting area, and into
    each other. The second matters as much as the first -- two tick labels run
    together name neither of the two keys they were drawn for.
    """
    bottom, left = tick_extent(canvas, panel)
    title_h = canvas.text_box(panel.ax.xaxis.label).height
    title_w = canvas.text_box(panel.ax.yaxis.label).width
    down = max(floor - title_h - 6.0 - panel.rect.y1, 1.0)
    across = max(panel.rect.x0 - canvas.layout.limit('left') - title_w - 6.0, 1.0)
    return max((bottom - panel.rect.y1) / down, (panel.rect.x0 - left) / across,
               panel_crowding(canvas, panel), 1.0)


def pin_title_above(canvas: Canvas, panel: PanelCanvas, ceiling: float) -> bool:
    """Keep a value-axis title written above the plotting area out of the text band.

    It is the one axis title placed by an offset rather than by the pass below, and
    the room it has is the gap between the text band and the plotting area -- which
    the margins decide, so the narrowest margins are where it runs into the figure's
    own title. True when it had to be moved, so the caller measures again.
    """
    artist = panel.above_title
    if artist is None:
        return False
    box = canvas.text_box(artist)
    if box.y0 >= ceiling:
        return False
    x, y = artist.get_position()
    # The offset is in points and grows upwards; the box is in pixels from the top.
    artist.set_position((x, y - (ceiling - box.y0) * 72.0 / canvas.style.dpi))
    return True


def panel_crowding(canvas: Canvas, panel: PanelCanvas) -> float:
    """By what factor this panel's category tick labels run into each other."""
    return crowding([canvas.text_box(label) for label in panel.ax.get_xticklabels()
                     if label.get_text()])


def pin_titles(canvas: Canvas, panel: PanelCanvas, floor: float) -> None:
    """Put each axis title just past its own tick labels, and no further."""
    w, h = canvas.style.image_size
    bottom, left = tick_extent(canvas, panel)
    label = panel.ax.xaxis.label
    if label.get_text() and "x" not in panel.placed_titles:
        height = canvas.text_box(label).height
        # Below the tick labels or not at all. Slanted names reach far enough down
        # that on a shallow bottom margin there is no row left, and pulled up into
        # the room they leave the title is written across them -- costing a key,
        # which is what a tick label is there to give. An axis title is the text
        # that gives way: nothing is read off it that is not also on the axis.
        if bottom + 4.0 + height > floor:
            canvas.drop(label)
        else:
            panel.ax.xaxis.set_label_coords(
                (panel.rect.x0 + panel.rect.x1) / 2 / w, 1.0 - (bottom + 4.0) / h,
                transform=canvas.fig.transFigure)
    side = panel.ax.yaxis.label
    if side.get_text() and "y" not in panel.placed_titles:
        column = max(left - 6.0 - canvas.text_box(side).width / 2,
                     canvas.layout.limit('left') + canvas.text_box(side).width / 2)
        panel.ax.yaxis.set_label_coords(
            column / w, 1.0 - (panel.rect.y0 + panel.rect.y1) / 2 / h,
            transform=canvas.fig.transFigure)


def nudge(canvas: Canvas, panel: PanelCanvas, floor: float) -> bool:
    """Shift a title that still ends up outside its room. True when one moved."""
    w, h = canvas.style.image_size
    moved = False
    for role, axis, label in (("x", panel.ax.xaxis, panel.ax.xaxis.label),
                              ("y", panel.ax.yaxis, panel.ax.yaxis.label)):
        if not label.get_text() or role in panel.placed_titles:
            continue
        box = canvas.text_box(label)
        dx = (max(0.0, canvas.layout.limit('left') - box.x0)
              - max(0.0, box.x1 - canvas.layout.limit('right')))
        dy = -max(0.0, box.y1 - floor) + max(0.0, LEFT_EDGE - box.y0)
        if abs(dx) < 0.5 and abs(dy) < 0.5:
            continue
        x, y = label.get_position()
        axis.set_label_coords(x + dx / w, y + dy / h, transform=canvas.fig.transFigure)
        moved = True
    return moved


def label_overlaps(canvas: Canvas, gap: float = LABEL_GAP) -> None:
    """Keep only the value labels a reader can tell apart.

    A printed value is matched exactly and the mark it belongs to is found by the
    box its label came out in, so a label a reader cannot separate from its
    neighbour leaves two marks with an answer neither can be shown to carry. The
    later one is dropped: it is not drawn at all, and its mark keeps no printed
    value -- which puts it back among the marks whose value is estimated off the
    geometry, where the readability rule can judge it.

    Two things count as not separable, and the second is why a share of overlap is
    not the test:

        it touches another label      `2 USD million2 USD millions` is two answers
                                      and reads as one string, and the two boxes
                                      overlap by nothing at all
        it touches a tick label       a tick label is where a key is read from, so a
                                      number written across one costs a key as well
                                      as a value

    So the test is clear space: a label is kept when its box, grown by a couple of
    pixels, meets nothing already on the page.
    """
    if not canvas.labels:
        return
    canvas.fig.canvas.draw()
    taken: dict[str, list[Box]] = {}
    for artist, panel, then in canvas.labels:
        others = taken.setdefault(panel.panel_id, None)  # type: ignore[arg-type]
        if others is None:
            others = [canvas.text_box(t) for t in
                      (*panel.ax.get_xticklabels(), *panel.ax.get_yticklabels(),
                       *panel.below) if t.get_text()]
            taken[panel.panel_id] = others
        box = canvas.text_box(artist).grow(gap)
        if any(box.clip_to(other).area > 0 for other in others):
            artist.set_visible(False)
            continue
        others.append(box)
        canvas.keep(artist, then)
    canvas.labels.clear()


def crowding(boxes: Sequence[Box]) -> float:
    """How much smaller these labels have to be written before they stop touching.

    1.0 when they already stand apart. Two tick labels run together name neither of
    the two keys they were drawn for, and shrinking is the only remedy allowed:
    shortening one would stop it naming its key at all.
    """
    ordered = sorted(boxes, key=lambda b: (b.x0 + b.x1) / 2)
    worst = 1.0
    for a, b in zip(ordered, ordered[1:]):
        apart = (b.x0 + b.x1) / 2 - (a.x0 + a.x1) / 2
        if apart > 0.5:
            worst = max(worst, ((a.width + b.width) / 2 + TICK_GAP) / apart)
    return worst
