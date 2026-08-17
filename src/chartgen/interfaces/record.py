"""The annotation record: an image plus everything known about what is drawn on it.

Three layers, each written by the component that already knows it, and joined on
`(figure_id, panel_id, key)` without inference:

    page elements   written by the page composer: boxes and their categories
    encoding        written by the renderer: for every mark, its box, key and value,
                    and for every panel, its axis value and pixel ranges
    provenance      written by the projection: how many source rows a mark covers

`Mark` uses one value dictionary rather than a class per shape. A bar fills one
key, a box plot fills five, and everything downstream does the same thing with
both -- take the box, take the values -- so there is nothing for polymorphism to do.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from ..common.geometry import Box
from .style import Degradation, StyleVector

ElementCategory = Literal["Text", "Table", "Picture", "Page-Header", "Page-Footer"]
AxisRole = Literal["x", "y", "y_right"]

#: How a mark encodes its value. Length and position can be measured off the
#: pixels; angle and colour cannot be measured to useful precision.
Channel = Literal["length", "position", "angle", "color"]


@dataclass(frozen=True)
class Element:
    """A box on the page and what kind of thing it is. Pixels only, no data meaning."""

    box: Box
    category: ElementCategory


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


@dataclass(frozen=True)
class Panel:
    panel_id: str
    box: Box                        # the plotting area
    axes: tuple[Axis, ...] = ()
    chart_type: str = ""


@dataclass(frozen=True)
class Mark:
    """One separately identifiable shape: a box, a key, a value dictionary.

    `rows` and `readable` are filled in after rendering; the renderer writes None.
    """

    mark_id: str
    panel_id: str
    key: tuple[str, ...]
    values: dict[str, float]
    box: Box
    channel: Channel
    labeled: bool = False
    label_box: Box | None = None
    rows: int | None = None
    readable: bool | None = None


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
class RenderOutput:
    """What the renderer produces: the image and its geometry. Marks do not yet
    carry their row counts or readability."""

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

    def panel(self, panel_id: str) -> Panel:
        for p in self.panels:
            if p.panel_id == panel_id:
                return p
        raise KeyError(f"no such panel: {panel_id}")

    def marks_of(self, panel_id: str) -> tuple[Mark, ...]:
        return tuple(m for m in self.marks if m.panel_id == panel_id)
