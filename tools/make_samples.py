"""Writing the minimal sample of every interface into tests/samples/.

The samples share one worked example end to end, so the numbers in a schema, a
figure spec, a render output and a record all line up. Changing an interface means
editing this file and running it again.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from chartgen.common.geometry import Box  # noqa: E402
from chartgen.common import serde  # noqa: E402
from chartgen.interfaces.figure import (  # noqa: E402
    Binding, Datum, FigureSpec, PanelSpec, Sharing, Source, ViewSpec,
)
from chartgen.interfaces.record import (  # noqa: E402
    Axis, Element, Mark, Panel, Record, RenderOutput, SelfCheck,
)
from chartgen.interfaces.style import Degradation, StyleVector  # noqa: E402
from chartgen.interfaces.table import Column, DimGroup, IntentBinding, TableSchema  # noqa: E402
from chartgen.s01_data.author import EXAMPLE_OUTPUT  # noqa: E402

SCENARIO = "er_wait"
IMAGE_SIZE = (900, 600)
PLOT_RECT = Box(96, 60, 860, 520)
Y_AXIS = Axis("y", (0.0, 60.0), (520.0, 60.0), column="wait_minutes")

BARS = (
    (("Mercy General",), 42.3, Box(168, 196, 278, 520), 372),
    (("St. Luke's",), 35.8, Box(423, 245, 533, 520), 315),
    (("Riverside",), 28.1, Box(678, 305, 788, 520), 213),
)


def table_schema() -> TableSchema:
    return TableSchema(
        scenario_id=SCENARIO,
        scenario_title="Emergency department visits and wait times at three metro hospitals, Jan–Jun 2024",
        data_context=(
            "The county health department compiled per-visit records from three "
            "hospitals for January through June 2024 to assess a new triage "
            "diversion policy."
        ),
        columns=(
            Column("hospital", "category", 3, group="entity",
                   values=("Mercy General", "St. Luke's", "Riverside")),
            Column("department", "category", 4, group="entity", parent="hospital",
                   values=("Internal Medicine", "Surgery", "Pediatrics", "Trauma")),
            Column("severity", "category", 3, group="triage", ordered="ordinal",
                   values=("Minor", "Moderate", "Severe")),
            Column("visit_date", "time", 182, group="calendar",
                   freq="daily", start="2024-01-01", end="2024-06-30"),
            Column("day_of_week", "category", 7, group="calendar", derived_from="visit_date",
                   ordered="ordinal",
                   values=("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")),
            Column("month", "category", 6, group="calendar", derived_from="visit_date",
                   ordered="ordinal",
                   values=("2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06")),
            Column("wait_minutes", "measure", 900, unit="minutes", additive=True),
            Column("cost", "measure", 900, unit="USD", additive=True),
            Column("satisfaction", "measure", 900, unit="points", additive=False),
        ),
        groups=(
            DimGroup("entity", ("hospital", "department")),
            DimGroup("triage", ("severity",)),
            DimGroup("calendar", ("visit_date", "day_of_week", "month")),
        ),
        dependencies=(("wait_minutes", "cost"), ("wait_minutes", "satisfaction")),
        intents=(
            IntentBinding(0, "Which hospital and department waits longest",
                          ("hospital", "wait_minutes"), "AVG", "comparison"),
            IntentBinding(1, "How wait time moved over the half year",
                          ("visit_date", "wait_minutes"), "AVG", "trend"),
            IntentBinding(2, "Do longer waits go with lower satisfaction",
                          ("wait_minutes", "satisfaction"), "NONE", "relation"),
        ),
        n_rows=900,
        script=EXAMPLE_OUTPUT["script"],
    )


def figure_spec() -> FigureSpec:
    view = ViewSpec(
        binding=Binding("bar", dims=("hospital",), measures=("wait_minutes",), aggregate="AVG"),
        data=tuple(Datum(key, {"value": v}, rows) for key, v, _, rows in BARS),
    )
    return FigureSpec(
        figure_id="f01",
        scenario_id=SCENARIO,
        panels=(PanelSpec("p0", view),),
        layout="single",
        sharing=Sharing(),
        relation=None,
        source=Source("intent", intent_index=0),
        column_units={"wait_minutes": "minutes", "cost": "USD", "satisfaction": "points"},
    )


def style_vector() -> StyleVector:
    """One fixed style: no written values, a corporate blue, an axis from zero."""
    return StyleVector(
        value_labels="none",
        palette="corporate_low",
        zero_baseline=True,
        image_size=IMAGE_SIZE,
        degradation=Degradation("jpeg", 75),
    )


def render_output() -> RenderOutput:
    return RenderOutput(
        figure_id="f01",
        scenario_id=SCENARIO,
        image_path="out/er_wait/f01.png",
        image_size=IMAGE_SIZE,
        style=style_vector(),
        panels=(Panel("p0", PLOT_RECT, (Y_AXIS,), "bar"),),
        marks=tuple(
            Mark(f"m{i}", "p0", key, {"value": v}, box, "length", labeled=False)
            for i, (key, v, box, _) in enumerate(BARS)
        ),
        legend=(),
        elements=(Element(Box(0, 0, *IMAGE_SIZE), "Picture"),),
        degradations=(Degradation("jpeg", 75),),
    )


def record() -> Record:
    r = render_output()
    return Record(
        figure_id=r.figure_id, scenario_id=r.scenario_id, image_path=r.image_path,
        image_size=r.image_size, style=r.style, panels=r.panels,
        marks=tuple(
            Mark(f"m{i}", "p0", key, {"value": v}, box, "length",
                 labeled=False, rows=rows, readable=True)
            for i, (key, v, box, rows) in enumerate(BARS)
        ),
        legend=r.legend, elements=r.elements, degradations=r.degradations,
        selfcheck=SelfCheck(box_content=True, value_readback=True, style_invariant=True),
    )


BUILDERS = {
    "TableSchema": table_schema,
    "FigureSpec": figure_spec,
    "StyleVector": style_vector,
    "RenderOutput": render_output,
    "Record": record,
}


SCENARIO_PATH = serde.SAMPLES["TableSchema"][1].parent / "er_scenario.json"


def main() -> None:
    for name, build in BUILDERS.items():
        path = serde.SAMPLES[name][1]
        serde.save(build(), path)
        print(f"wrote {path.relative_to(Path.cwd())}")
    # The hand-written answer for the data stage. It is the same object the prompt
    # carries as its worked example, so the two cannot drift apart.
    SCENARIO_PATH.write_text(
        json.dumps(EXAMPLE_OUTPUT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {SCENARIO_PATH.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
