"""One worked example of every chart type, drawn without calling a model.

The seventeen types are what the pipeline can draw at all, so they need a place
where each of them is produced from a known table under a known style: the test
suite reads this table to check that no declared type is left undrawn, and the
review pages read it to show what each one comes out as.

Nothing here calls a model. The scenarios are the hand-written payloads in
`tests/samples/`, so a gallery run is reproducible from the repository alone.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Iterator

from chartgen.config import Config
from chartgen.interfaces.figure import Binding, FigureSpec, PanelSpec, TextBlock
from chartgen.interfaces.record import Record
from chartgen.interfaces.style import StyleVector
from chartgen.interfaces.table import FactTable, TableSchema
from chartgen.s01_data.author import compose as compose_data
from chartgen.s02_figure.keys import key_sources
from chartgen.s02_figure.project import project
from chartgen.s03_render.render import render
from chartgen.s03_render.style import default, sample
from chartgen.s04_record.selfcheck import finish

SAMPLES = Path(__file__).resolve().parents[1] / "tests" / "samples"

#: One binding per chart type, over whichever of the worked scenarios can draw it.
CASES: dict[str, tuple[str, dict]] = {
    "bar": ("er", dict(dims=("hospital",), measures=("wait_minutes",), aggregate="AVG")),
    "grouped_bar": ("er", dict(dims=("hospital", "severity"),
                               measures=("wait_minutes",), aggregate="AVG")),
    "stacked_bar": ("er", dict(dims=("hospital", "severity"),
                               measures=("cost",), aggregate="SUM")),
    "histogram": ("er", dict(measures=("wait_minutes",), aggregate="BIN_COUNT")),
    "waterfall": ("funnel", dict(dims=("stage",), measures=("basket_value",),
                                 aggregate="SUM")),
    "funnel": ("funnel", dict(dims=("stage",), aggregate="COUNT")),
    "line": ("er", dict(time="visit_date", measures=("wait_minutes",),
                        aggregate="AVG", resample="monthly")),
    "category_line": ("er", dict(dims=("department",), measures=("wait_minutes",),
                                 aggregate="AVG")),
    "area": ("er", dict(dims=("severity",), time="visit_date", measures=("cost",),
                        aggregate="SUM", resample="monthly")),
    "scatter": ("er", dict(measures=("wait_minutes", "satisfaction"), aggregate="NONE")),
    "pie": ("er", dict(dims=("department",), measures=("cost",), aggregate="SUM")),
    "range_bar": ("er", dict(dims=("hospital",), measures=("wait_minutes",),
                             aggregate="FIVE_NUM")),
    "error_bar": ("er", dict(dims=("hospital",), measures=("wait_minutes",),
                             aggregate="FIVE_NUM")),
    "table_chart": ("er", dict(dims=("hospital", "severity"), measures=("wait_minutes",),
                               aggregate="AVG")),
    "heatmap": ("er", dict(dims=("hospital", "department"), measures=("wait_minutes",),
                           aggregate="AVG")),
    "box": ("er", dict(dims=("department",), measures=("wait_minutes",),
                       aggregate="FIVE_NUM")),
    "windsock": ("er", dict(time="visit_date", measures=("wait_minutes",),
                            aggregate="FIVE_NUM", resample="monthly")),
}

#: The styles each type is drawn under. The first is the neutral one every test
#: compares against; the others are there because a type that only holds together at
#: the default style holds together nowhere.
STYLES: tuple[tuple[str, dict], ...] = (
    ("Default style", {}),
    ("Values printed · greyscale",
     {"value_labels": "all", "palette": "grayscale", "decimals": 0}),
    ("Gridlines · larger type · no frame", {"gridlines": True, "font_size": 13.0,
                                  "edge_width": 0.0, "zero_line": True}),
)

#: Seed for the sampled style variant shown beside the fixed ones.
SEED = 20260822


def tables(config: Config | None = None) -> dict[str, tuple[FactTable, TableSchema]]:
    """The scenarios the gallery draws from, built from the hand-written payloads."""
    config = config or Config.load()
    out = {}
    for name, path in (("er", "er_scenario.json"), ("funnel", "funnel_scenario.json")):
        payload = json.loads((SAMPLES / path).read_text(encoding="utf-8"))
        out[name] = compose_data(payload, scenario_id=name, seed=SEED, config=config)
    return out


def spec_for(name: str, table: FactTable, schema: TableSchema) -> FigureSpec:
    """The one-panel figure that shows this chart type, with its text written out."""
    binding = Binding(name, **CASES[name][1])
    binding = replace(binding, key_sources=key_sources(binding))
    view = project(table.df, binding, schema, seed=5)
    names = {c.name: c.name.replace("_", " ").title() for c in schema.columns}
    return FigureSpec(
        name, schema.scenario_id, (PanelSpec("p0", (view,)),),
        column_units={c.name: c.unit for c in schema.measures},
        column_names=names,
        # "Figure 1", not the type name. The block is the figure number, and a figure
        # on a real page is numbered; the type name is the heading of the page this
        # example sits on, so writing it here puts a word on the image that no figure
        # in the corpus carries.
        texts=(TextBlock("figure_number", "Figure 1", "figure", "above"),
               TextBlock("title", _title(binding, names), "figure", "above"),
               TextBlock("source", f"Source: {schema.scenario_title}", "figure", "below")))


def _title(binding: Binding, names: dict[str, str]) -> str:
    """A plain title. The words call is not involved: a gallery calls no model."""
    from chartgen.interfaces.table import aggregate_phrase

    measure = names.get(binding.measures[0], "") if binding.measures else ""
    by = " and ".join(names.get(c, c) for c in binding.group_columns)
    phrase = aggregate_phrase(binding.aggregate, measure)
    return f"{phrase[:1].upper()}{phrase[1:]}" + (f" by {by}" if by else "")


def styles() -> Iterator[tuple[str, StyleVector]]:
    """The styles every type is drawn under, in order, each with a readable name."""
    for label, overrides in STYLES:
        yield label, replace(default(), **overrides)
    yield "A sampled style vector", sample(SEED, "gallery", "f01")


def draw(out_dir: Path, config: Config | None = None
         ) -> dict[str, list[tuple[str, FigureSpec, Record]]]:
    """Every chart type under every gallery style, recorded and self-checked."""
    built = tables(config)
    out: dict[str, list[tuple[str, FigureSpec, Record]]] = {}
    for name in CASES:
        table, schema = built[CASES[name][0]]
        spec = spec_for(name, table, schema)
        made = []
        for index, (label, style) in enumerate(styles()):
            rendered = render(spec, style, out_dir / name / f"v{index}", index)
            made.append((label, spec, finish(rendered, spec)))
        out[name] = made
    return out
