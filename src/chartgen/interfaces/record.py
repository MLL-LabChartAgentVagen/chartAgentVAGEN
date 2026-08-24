"""The annotation record: an image plus everything known about what is drawn on it.

Three layers, each written by the component that already knows it, and joined on
`(figure_id, panel_id, key)` without inference:

    page elements   written by the page composer: boxes, their categories, and the
                    string of text that was actually drawn inside them
    encoding        written by the renderer: for every mark, its box, key, value,
                    which axis the value was measured against and which shape it
                    was measured as; for every panel, its axis value and pixel ranges
    provenance      written by the projection: how many source rows a mark covers

`Mark` uses one value dictionary rather than a class per shape. A bar fills one
key, a box plot fills five, and everything downstream does the same thing with
both -- take the box, take the values -- so there is nothing for polymorphism to do.

The four vocabularies below (`Channel`, `MarkShape`, `KeySource`, `TextRole`) are
defined here rather than beside the code that produces them, because the exporter
reads nothing but this module: a record that cannot be interpreted without also
loading the chart table or the figure specification would not be self-sufficient.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from ..common.geometry import Box
from .style import Degradation, StyleVector

AxisRole = Literal["x", "y", "y_right"]

#: How a mark encodes its value. Length and position can be measured off the
#: pixels; angle and colour cannot be measured to useful precision; a printed
#: value is read as text and needs no geometry at all.
Channel = Literal["length", "position", "angle", "color", "printed"]

#: The shape of one mark. Drawing code is split by shape, not by chart type:
#: seventeen types share six shapes.
MarkShape = Literal["rect", "point", "sector", "cell", "boxlike", "band"]

#: Where one segment of a key was read from. A key is an ordered tuple of strings
#: and its segments do not share a source: on a two-panel figure the hospital name
#: is read off the panel title while the department is read off an axis tick, so a
#: single source per figure would answer neither question.
KeySource = Literal[
    "axis_tick",      # a tick label on the category or time axis
    "legend",         # a legend entry
    "panel_title",    # the title above the panel this mark belongs to
    "inline_label",   # printed next to the mark itself
    "heading",        # only in the figure title
    "colour_only",    # carried by colour with no text anywhere
    "mark_shape",     # carried by the marker shape
    "hatch",          # carried by the fill pattern
    "not_shown",      # not on the page at all; this key cannot be recovered
]

#: The eight kinds of text that sit outside the plotting area.
TextRole = Literal[
    "figure_number", "title", "subtitle", "unit",
    "source", "note", "axis_title", "legend_title",
]

#: The five page-level categories, then the eight text roles, then the tick label.
#: A page-element box therefore carries the role of the text it holds, not just a
#: coarse `Text` label.
#:
#: `axis_tick` is the one category that is not page furniture: it is where a key is
#: read from. A mark already records that its key came off an axis tick; the box says
#: which tick, which is the same claim about a key that `(value, box)` is about a
#: value. It is kept out of the page-element target, whose vocabulary is fixed by the
#: benchmark it is written for.
ElementCategory = Literal[
    "Text", "Table", "Picture", "Page-Header", "Page-Footer",
    "figure_number", "title", "subtitle", "unit",
    "source", "note", "axis_title", "legend_title", "axis_tick",
]

TEXT_ROLES: tuple[str, ...] = (
    "figure_number", "title", "subtitle", "unit",
    "source", "note", "axis_title", "legend_title",
)

KEY_SOURCES: tuple[str, ...] = (
    "axis_tick", "legend", "panel_title", "inline_label",
    "heading", "colour_only", "mark_shape", "hatch", "not_shown",
)


@dataclass(frozen=True)
class Element:
    """A box on the page, what kind of thing it is, and the text drawn in it.

    `text` holds the string as it came out on the page, which is not always the
    string the figure specification asked for: it may have been wrapped, cut short
    or given a footnote marker. What is on the page is the ground truth.
    """

    box: Box
    category: ElementCategory
    text: str = ""
    panel_id: str = ""      # set when the element belongs to one panel, as a panel title does


@dataclass(frozen=True)
class Axis:
    """An axis as drawn. The value range and the pixel range are the whole input to
    deciding whether a value can be read off the image and to converting a box
    back into a value."""

    role: AxisRole
    value_range: tuple[float, float]
    pixel_range: tuple[float, float]
    scale: Literal["linear", "log"] = "linear"
    column: str | None = None      # which column this axis carries
    #: The title drawn beside it. The column name identifies the column; this is what
    #: a reader of the page sees, and a question phrased in the raw column name is a
    #: question about something that is not written anywhere on the image.
    label: str = ""
    #: The angle the tick labels were written at. Recorded rather than read off the
    #: style vector, because the style states the angle a batch asked for while the
    #: fitting raises it when the names do not fit side by side -- and what a record
    #: says was drawn has to be what was drawn.
    tick_rotation: float = 0.0


@dataclass(frozen=True)
class Panel:
    """One plotting area. `chart_types` is a tuple because a single plotting area
    may hold more than one view -- a bar chart with a line drawn over it."""

    panel_id: str
    box: Box                        # the plotting area
    axes: tuple[Axis, ...] = ()
    chart_types: tuple[str, ...] = ()
    #: The circle a sector panel's wedges are cut from, in pixels: centre, inner
    #: radius, outer radius. A wedge's value is an angle, and an angle needs a centre
    #: to be measured from -- the plotting rectangle alone does not give one. It sits
    #: on the panel rather than on each mark because every wedge of one pie shares
    #: it, exactly as every bar of one panel shares its value axis.
    circle: tuple[float, float, float, float] | None = None

    def axis(self, role: AxisRole) -> Axis | None:
        return next((a for a in self.axes if a.role == role), None)

    @property
    def radius(self) -> float | None:
        """The radius wedges are drawn at, which is what an angle is pinned by."""
        return self.circle[3] if self.circle else None


@dataclass(frozen=True)
class Mark:
    """One separately identifiable shape: a box, a key, a value dictionary.

    `value_axis` and `mark_shape` are how the value was read: which of the panel's
    axes it was measured against and which geometry it was measured as. On a panel
    holding one view both could be inferred from the chart type, but a panel may
    hold two views with two value axes and two mark shapes, and the exporter is not
    allowed to go back to the figure specification to find out which.

    `key_src` runs parallel to `key`: one source per segment. `rows` and `readable`
    are filled in after rendering; the renderer writes None.
    """

    mark_id: str
    panel_id: str
    key: tuple[str, ...]
    values: dict[str, float]
    box: Box
    channel: Channel
    labeled: bool = False
    label_box: Box | None = None
    #: The string printed beside the mark. A printed value is matched exactly, so
    #: what was printed is the answer -- and storing it is what lets anyone check
    #: that it is the number recorded for this mark and not some other one.
    label_text: str = ""
    value_axis: AxisRole = "y"
    mark_shape: MarkShape = "rect"
    key_src: tuple[KeySource, ...] = ()
    rows: int | None = None
    readable: bool | None = None
    #: Which entry of `values` a value target asks about. Written by the record stage
    #: together with `readable`, because the two are one decision: what a reader can
    #: recover from a wedge is the share it holds, while what a bar's height gives is
    #: the value itself -- so a mark that answers about the wrong entry is readable
    #: and wrong at the same time. Empty until the record stage fills it in.
    value_key: str = ""


@dataclass(frozen=True)
class LegendEntry:
    """A legend item and the panels it governs.

    On a single-panel figure `applies_to_panels` always has one element and says
    nothing. It carries information only when several panels share one legend,
    which is where the legend-binding training target comes from.
    """

    box: Box
    maps_to_category: str
    applies_to_panels: tuple[str, ...] = ()


@dataclass(frozen=True)
class LayoutBlock:
    """One strip of the image held for something other than the plotting area.

    Recorded because where it is settles what a reader can be asked. A legend down
    the right edge and a legend across the bottom put the same names in different
    places, and a key read off a legend is a key whose position is part of the
    answer.
    """

    name: str            # text | legend | foot
    edge: str            # top | bottom | left | right
    box: Box = field(default_factory=lambda: Box(0.0, 0.0, 0.0, 0.0))
    occupied: bool = True


@dataclass(frozen=True)
class Layout:
    """The plotting rectangle and the blocks cut out around it.

    The blocks are settled before anything is drawn and keep their room whether or
    not they hold anything: a strip that appeared only when something needed it would
    move the plotting area and invalidate every box already recorded against it.
    """

    plot: Box = field(default_factory=lambda: Box(0.0, 0.0, 0.0, 0.0))
    blocks: tuple[LayoutBlock, ...] = ()
    image_size: tuple[int, int] = (0, 0)

    def block(self, name: str) -> LayoutBlock | None:
        return next((b for b in self.blocks if b.name == name), None)

    def edge_of(self, name: str) -> str:
        found = self.block(name)
        return found.edge if found else ""

    def limit(self, edge: str) -> float:
        """How far a fitting pass may reach on this edge before it hits a block.

        Only an occupied block bounds anything: an empty one holds its room so the
        plotting area does not move, but nothing is written in it to run into.
        """
        held = [b for b in self.blocks if b.edge == edge and b.occupied]
        if edge == "top":
            return max((b.box.y1 for b in held), default=0.0)
        if edge == "bottom":
            return min((b.box.y0 for b in held), default=float(self.image_size[1]))
        if edge == "left":
            return max((b.box.x1 for b in held), default=0.0)
        return min((b.box.x0 for b in held), default=float(self.image_size[0]))


@dataclass(frozen=True)
class RenderOutput:
    """What the renderer produces: the image and its geometry. Marks do not yet
    carry their row counts or readability.

    `page_id` groups figures that were composed onto the same page. Page-element
    targets are merged by it, because two figures on one page each know only their
    own text blocks and would otherwise leave the other's unlabelled.
    """

    figure_id: str
    scenario_id: str
    image_path: str
    image_size: tuple[int, int]
    style: StyleVector
    panels: tuple[Panel, ...] = ()
    marks: tuple[Mark, ...] = ()
    legend: tuple[LegendEntry, ...] = ()
    elements: tuple[Element, ...] = ()
    degradations: tuple[Degradation, ...] = ()
    #: How the image was cut into blocks, and which edge each one took. A legend down
    #: the right and a legend across the bottom put the same names in different
    #: places, and a key read off a legend is a key whose position is part of the
    #: answer -- so what was actually drawn is recorded, not just what was asked for.
    layout: Layout = field(default_factory=Layout)
    page_id: str = ""
    #: Which style version of this figure this is. The same specification is drawn
    #: more than once on purpose: the pair is a training sample of its own, and it is
    #: what the restyling self-check compares. So it is part of a record's identity,
    #: not a detail of where its image happened to be written.
    variant: int = 0
    #: What the figure is for, in a sentence. It comes from upstream rather than
    #: from the pixels -- an intent figure's caption says why the data was collected,
    #: which is the one thing about a figure that cannot be read off it.
    caption: str = ""

    def panel(self, panel_id: str) -> Panel:
        for p in self.panels:
            if p.panel_id == panel_id:
                return p
        raise KeyError(f"no such panel: {panel_id}")

    def marks_of(self, panel_id: str) -> tuple[Mark, ...]:
        return tuple(m for m in self.marks if m.panel_id == panel_id)


@dataclass(frozen=True)
class SelfCheck:
    """The three checks a figure must pass before its record is kept.

    Is there anything inside the box; does the value read back off the pixels match
    the recorded one; does a differently styled rendering give the same answers.
    The third is run on a sample of figures, so it is None when it did not run.
    """

    box_content: bool | None = None
    value_readback: bool | None = None
    style_invariant: bool | None = None
    reasons: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return all(v is not False for v in
                   (self.box_content, self.value_readback, self.style_invariant))


@dataclass(frozen=True)
class Record(RenderOutput):
    """A finished record: the render output plus row counts, per-mark readability
    and the self-check verdict. The exporter reads only this -- it needs to know
    nothing about the fact table or the renderer."""

    selfcheck: SelfCheck = field(default_factory=SelfCheck)
