"""The style vector: everything about how a figure looks, and nothing about what it says.

Each dimension is sampled independently from a seed and stored with the record, so
an ablation can group results by any single dimension.

`STYLE_DOMAINS` is the declarative half: every dimension states the values it may
take, its default, the function that realises it, and whether it can change which
values are readable. Two meta-tests read that table -- one checks that every
declared value has a drawing branch, so a record can never claim something that
never happened; the other renders each value of every dimension marked
`readable=False` and requires the key-to-value mapping to come back bit-identical.

"Which values are readable" is the one thing style is allowed to change: whether an
axis starts at zero changes how values map to pixels, and a value written on the
chart is exact rather than estimated. Neither changes what any value is worth.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Literal

ValueLabels = Literal["none", "all", "some", "outside", "outside_leader"]
LegendPlacement = Literal["outside", "per_panel", "inside"]
PanelTypes = Literal["same", "mixed"]
PanelBackground = Literal["white", "tint", "grid_band"]
NumberFormat = Literal["plain", "thousands", "currency", "percent", "si", "paren_neg"]
Palette = Literal["corporate_low", "monochrome", "gradient", "grayscale"]
Orientation = Literal["vertical", "horizontal"]
UnitPlacement = Literal["axis_title", "subtitle", "tick_labels", "value_labels"]
TimeTickFormat = Literal["iso", "short", "compact"]
TitlePlacement = Literal["above", "below"]
TickDensity = Literal["sparse", "normal", "dense"]
Margins = Literal["normal", "tight", "wide"]

#: What a point series is drawn as. This changes the marker, never the mark shape:
#: a diamond and a dot are both a point, and both stay measurable. Swapping in a
#: sector or a cell would change whether the value can be read at all, which is
#: what makes it a different chart type rather than a different style.
Marker = Literal["line", "circle", "diamond", "triangle", "tick", "square"]

DegradationKind = Literal["none", "jpeg", "noise", "blur", "downscale", "rotate", "perspective"]


@dataclass(frozen=True)
class Degradation:
    """One image degradation. Only degradations whose geometry has a closed form
    are allowed, so recorded boxes can be mapped through the same transform."""

    kind: DegradationKind = "none"
    amount: float = 0.0     # jpeg quality, noise sigma, blur radius, scale, angle, strength


@dataclass(frozen=True)
class StyleDim:
    """One sampleable visual decision.

    `draws` names the function that realises it, as `path::function`. A dimension
    whose values have no drawing branch would let the record state something that
    did not happen, so a meta-test resolves every one of these strings.

    `readable` says whether changing this dimension can change which values are
    measurable off the image. The dimensions marked False must leave the recorded
    answers bit-identical, and the style self-check is what proves it.
    """

    domain: tuple[Any, ...]
    default: Any
    draws: str
    readable: bool = False
    group: str = ""
    #: How often each value comes up, when they are not meant to come up equally.
    #: A log axis and a pseudo-three-dimensional bar are real and rare; sampling
    #: them as often as a linear axis would make the corpus that of no real report.
    weights: tuple[float, ...] | None = None


def _d(domain, default, draws, *, readable: bool = False, group: str = "",
       weights: tuple[float, ...] | None = None) -> StyleDim:
    domain = tuple(domain)
    if weights is not None and len(weights) != len(domain):
        raise ValueError(f"{draws}: {len(weights)} weights for {len(domain)} values")
    return StyleDim(domain, default, draws, readable, group, weights)


#: Every dimension of the style vector, by field name. A meta-test requires this
#: table and the fields of `StyleVector` to name exactly the same set, apart from
#: `degradation`, which is a nested object with its own sampler.
STYLE_DOMAINS: dict[str, StyleDim] = {
    # ---- 1 value labels
    "value_labels": _d(("none", "all", "some", "outside", "outside_leader"), "none",
                       "s03_render/draw/labels.py::write_value_labels",
                       readable=True, group="labels", weights=(0.40, 0.25, 0.15, 0.10, 0.10)),
    "value_label_rotation": _d((0.0, 45.0, 90.0), 0.0,
                               "s03_render/draw/labels.py::write_value_labels",
                               group="labels", weights=(0.80, 0.12, 0.08)),
    "unit_placement": _d(("axis_title", "subtitle", "tick_labels", "value_labels"),
                         "axis_title", "s03_render/draw/canvas.py::axis_title",
                         group="labels"),
    "footnote_marker": _d((False, True), False,
                          "s03_render/draw/canvas.py::write_text", group="labels", weights=(0.85, 0.15)),

    # ---- 2 layout detail
    "legend_placement": _d(("outside", "per_panel", "inside"), "outside",
                           "s03_render/draw/canvas.py::draw_legend", group="layout"),
    # Which edge an outside legend takes. A side legend is cut out of the width, so
    # the plotting area is narrower and a pixel of the value axis is worth the same
    # but a pixel of the category axis covers more -- which is why it is declared as
    # affecting readability. Measured on a hundred ParseBench pages: nine carry a
    # legend down the side, and all three models agree on them.
    "legend_edge": _d(("bottom", "right", "left"), "bottom",
                      "s03_render/draw/canvas.py::_compose", readable=True,
                      group="layout", weights=(0.89, 0.09, 0.02)),
    "panel_gap": _d((0.06, 0.10, 0.14, 0.18), 0.10,
                    "s03_render/render.py::panel_rects", group="layout"),
    "repeat_shared_ticks": _d((False, True), False,
                              "s03_render/render.py::_hide_repeated_ticks", group="layout"),
    "series_name_beside_line": _d((False, True), False,
                                  "s03_render/draw/point.py::name_beside_line",
                                  group="layout", weights=(0.80, 0.20)),
    "note_box": _d((False, True), False,
                   "s03_render/render.py::draw_texts", group="layout", weights=(0.80, 0.20)),
    "panel_bg": _d(("white", "tint", "grid_band"), "white",
                   "s03_render/draw/canvas.py::_style_axes", group="layout", weights=(0.70, 0.20, 0.10)),
    "title_placement": _d(("above", "below"), "above",
                          "s03_render/render.py::draw_texts", group="layout", weights=(0.85, 0.15)),

    # ---- 3 panel types
    "panel_types": _d(("same", "mixed"), "same",
                      "s03_render/render.py::panel_chart_type",
                      readable=True, group="panel_types"),

    # ---- 4 number format
    "number_format": _d(("plain", "thousands", "currency", "percent", "si", "paren_neg"),
                        "plain", "s03_render/draw/frame.py::_format_ticks", group="numbers"),
    "decimals": _d((0, 1, 2), 1, "s03_render/style.py::format_number", group="numbers"),
    "time_tick_format": _d(("iso", "short", "compact"), "iso",
                           "s03_render/draw/canvas.py::category_axis", group="numbers"),

    # ---- 5 palette
    "palette": _d(("corporate_low", "monochrome", "gradient", "grayscale"),
                  "corporate_low", "s03_render/style.py::colors", group="palette"),
    "highlight_single": _d((False, True), False,
                           "s03_render/style.py::colors", group="palette", weights=(0.80, 0.20)),

    # ---- 6 shape detail
    "edge_width": _d((0.0, 0.8, 1.6), 0.8,
                     "s03_render/draw/context.py::shape_kwargs", group="shape"),
    "shadow": _d((False, True), False,
                 "s03_render/draw/context.py::shape_kwargs", group="shape", weights=(0.80, 0.20)),
    "pseudo_3d": _d((False, True), False,
                    "s03_render/draw/context.py::shape_kwargs", group="shape", weights=(0.85, 0.15)),
    "hatch": _d((None, "//", "..", "xx"), None,
                "s03_render/draw/context.py::shape_kwargs", group="shape", weights=(0.70, 0.10, 0.10, 0.10)),
    "gridlines": _d((False, True), True,
                    "s03_render/draw/canvas.py::_style_axes", group="shape"),
    "font_family": _d(("auto",), "auto",
                      "s03_render/draw/canvas.py::Canvas", group="shape"),
    "font_size": _d((9.0, 10.0, 11.0, 12.0, 14.0), 11.0,
                    "s03_render/draw/canvas.py::_style_axes", group="shape"),
    "bar_width": _d((0.35, 0.432, 0.6, 0.8), 0.432,
                    "s03_render/draw/rect.py::draw_bar", group="shape"),
    "donut": _d((False, True), False,
                "s03_render/draw/sector.py::draw_pie", group="shape"),
    "orientation": _d(("vertical", "horizontal"), "vertical",
                      "s03_render/draw/rect.py::draw_bar", readable=True, group="shape", weights=(0.75, 0.25)),
    "series_marks": _d((None, ("circle",), ("diamond",), ("triangle",), ("tick",),
                        ("line", "circle")), None,
                       "s03_render/draw/point.py::marker_of", group="shape", weights=(0.50, 0.10, 0.10, 0.10, 0.10, 0.10)),

    # ---- 7 axes
    "zero_baseline": _d((False, True), True,
                        "s03_render/style.py::nice_range", readable=True, group="axes"),
    "zero_line": _d((False, True), False,
                    "s03_render/draw/canvas.py::_style_axes", group="axes", weights=(0.70, 0.30)),
    "tick_density": _d(("sparse", "normal", "dense"), "normal",
                       "s03_render/style.py::nice_range", group="axes"),
    # The angle a batch asks for, which the fitting may raise but never lower. Set on
    # its side reads poorly, so ninety degrees is rare and never arrived at by fitting.
    "label_rotation": _d((0.0, 30.0, 45.0, 90.0), 0.0,
                         "s03_render/draw/canvas.py::category_axis", group="axes",
                         weights=(0.55, 0.20, 0.20, 0.05)),
    "log_scale": _d((False, True), False,
                    "s03_render/style.py::nice_range", readable=True, group="axes", weights=(0.92, 0.08)),
    "dual_axis": _d((False, True), False,
                    "s03_render/draw/canvas.py::add_twin", readable=True, group="axes"),
    "axis_title_above": _d((False, True), False,
                           "s03_render/draw/canvas.py::axis_title", group="axes", weights=(0.80, 0.20)),
    "two_level_x_labels": _d((False, True), False,
                             "s03_render/draw/canvas.py::category_axis", group="axes", weights=(0.85, 0.15)),
    "category_label_wrap": _d((False, True), False,
                              "s03_render/draw/canvas.py::category_axis", group="axes", weights=(0.80, 0.20)),

    # ---- canvas: frozen for one rendering, because auto-layout must never move a
    # recorded box. All three change how many pixels a value gets and therefore what
    # can be measured back out, so all three are marked as affecting readability.
    "image_size": _d(((900, 600), (1000, 640), (800, 560), (1200, 720),
                      (680, 680), (720, 900)), (900, 600),
                     "s03_render/draw/canvas.py::Canvas", readable=True, group="canvas",
                     weights=(0.28, 0.20, 0.16, 0.16, 0.10, 0.10)),
    "dpi": _d((72, 100, 150), 100, "s03_render/draw/canvas.py::Canvas",
              readable=True, group="canvas", weights=(0.20, 0.60, 0.20)),
    "margins": _d(("normal", "tight", "wide"), "normal",
                  "s03_render/draw/canvas.py::Canvas", readable=True, group="canvas",
                  weights=(0.60, 0.20, 0.20)),
}


@dataclass(frozen=True)
class StyleVector:
    """Every visual decision for one rendering. The field set matches `STYLE_DOMAINS`."""

    # 1 value labels
    value_labels: ValueLabels = "none"
    value_label_rotation: float = 0.0
    unit_placement: UnitPlacement = "axis_title"
    footnote_marker: bool = False

    # 2 layout detail
    legend_placement: LegendPlacement = "outside"
    legend_edge: str = "bottom"
    panel_gap: float = 0.10
    repeat_shared_ticks: bool = False
    series_name_beside_line: bool = False
    note_box: bool = False
    panel_bg: PanelBackground = "white"
    title_placement: TitlePlacement = "above"

    # 3 panel types
    panel_types: PanelTypes = "same"

    # 4 number format
    number_format: NumberFormat = "plain"
    decimals: int = 1
    time_tick_format: TimeTickFormat = "iso"

    # 5 palette
    palette: Palette = "corporate_low"
    highlight_single: bool = False

    # 6 shape detail
    edge_width: float = 0.8
    shadow: bool = False
    pseudo_3d: bool = False
    hatch: str | None = None
    gridlines: bool = True
    font_family: str = "auto"          # "auto" resolves to a font available on this machine
    font_size: float = 11.0
    bar_width: float = 0.432           # three bars across a 764 pixel plot area are 110 wide
    donut: bool = False
    orientation: Orientation = "vertical"
    series_marks: tuple[Marker, ...] | None = None

    # 7 axes
    zero_baseline: bool = True
    zero_line: bool = False
    tick_density: TickDensity = "normal"
    label_rotation: float = 0.0
    log_scale: bool = False
    dual_axis: bool = False
    axis_title_above: bool = False
    two_level_x_labels: bool = False
    category_label_wrap: bool = False

    # canvas: frozen, because auto-layout must never move a recorded box
    image_size: tuple[int, int] = (900, 600)
    dpi: int = 100
    margins: Margins = "normal"

    degradation: Degradation = Degradation()


#: Dimensions whose value cannot change any recorded answer. The style self-check
#: renders each of their values and requires the key-to-value mapping to match.
NEUTRAL_DIMS: tuple[str, ...] = tuple(
    name for name, dim in STYLE_DOMAINS.items() if not dim.readable)


def style_fields() -> tuple[str, ...]:
    """Field names of `StyleVector` other than the nested degradation object."""
    return tuple(f.name for f in fields(StyleVector) if f.name != "degradation")
