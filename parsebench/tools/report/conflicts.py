"""The conflicts, each with the evidence needed to settle it, in one file.

`reports/pages/<page>.md` is the adjudication surface for one page: it puts the three
models beside the page and shows everything they said about it. That is the right
shape when the question is "what happened on this page", and the wrong shape when the
question is "settle every conflict in this run" -- a conflict over one figure's type
is decided by three cells, not by three page reports.

So this prints one block per conflict, in the order the summary lists them: what each
model said, the fields that bear on that particular disagreement, and the verdict
already on file if there is one. Nothing here is a judgement; it is the same data the
page reports carry, cut to the unit being judged.

Which fields bear on which unit is the only thing this file knows, and it is written
down once in `EVIDENCE`.

Usage:
    python parsebench/tools/report/conflicts.py                 # every open conflict
    python parsebench/tools/report/conflicts.py --unit type     # only figure types
    python parsebench/tools/report/conflicts.py --all           # settled ones too
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "parsebench" / "tools")]

ANALYSIS = ROOT / "parsebench/data/analysis"
STATS = ROOT / "parsebench/data/stats"

#: Per conflict kind, the figure-level fields worth printing beside the disputed
#: value. A type conflict is usually a naming difference over the same reading, and
#: the mark count and the mark shapes are what show that; a density conflict is
#: decided by the mark count alone.
EVIDENCE: dict[str, tuple[str, ...]] = {
    "type": ("type", "type_other", "marks", "series", "panels", "worked_example"),
    "printed": ("values_printed", "marks", "type"),
    "density": ("marks", "series", "panels", "type"),
    "heading": ("heading", "type"),
    "value_axes": ("axes", "type"),
    "key_roles": ("key_parts", "panels", "series"),
}

#: The figure schema has no field for mark shape, so a type conflict is settled from
#: the page's component list instead: these are the entries that name a shape or a
#: composition. Printed per model beside a type conflict, and nowhere else.
SHAPE_COMPONENTS = (
    "mixed_marks", "dual_axis", "stacked_bar", "grouped_bar", "pct_stacked",
    "stacked_area", "stacked_and_grouped", "data_table_as_figure", "horizontal_bars",
    "range_connector_line", "tick_marker_as_series", "step_line_series",
    "reference_line", "no_value_axis",
)


def unit_kind(unit: str) -> str:
    """`type#f2` -> `type`; a page-level unit is its own kind."""
    return unit.split("#", 1)[0]


def answers(model: str) -> dict[str, dict]:
    out = {}
    for path in sorted((ANALYSIS / model).glob("*.json")):
        if path.name in ("overview.json", "failures.json"):
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        out[record["stem"]] = record["answer"]
    return out


def figure(answer: dict, unit: str) -> dict | None:
    """The figure a `<kind>#f<n>` unit points at.

    The units are aligned across models by reading order over the *readable* figures,
    so the same filter has to be applied here: a model that opened its list with an
    `unreadable` block would otherwise have every figure shifted by one, and the
    evidence printed under a conflict would be about a different figure than the
    conflict is.
    """
    if "#f" not in unit:
        return None
    index = int(unit.split("#f", 1)[1]) - 1
    figures = [f for f in (answer.get("figures") or ()) if f.get("type") != "unreadable"]
    return figures[index] if 0 <= index < len(figures) else None


def brief(value) -> str:
    """One line, short enough to scan a hundred of them."""
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return text if len(text) <= 300 else text[:297] + "..."


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--unit", default="", help="only conflicts of this kind (type, density, ...)")
    ap.add_argument("--all", action="store_true", help="include conflicts already adjudicated")
    args = ap.parse_args()

    summary = json.loads((STATS / "analysis_summary.json").read_text(encoding="utf-8"))
    verdicts = json.loads((ANALYSIS / "verdicts.json").read_text(encoding="utf-8"))["verdicts"]
    models = summary["models"]
    read = {model: answers(model) for model in models}
    steps = {row["page"]: row["said"] for row in summary["hardest_step_reasons"]}

    shown = 0
    for item in summary["disagreements"]:
        key = f'{item["page"]}/{item["unit"]}'
        kind = unit_kind(item["unit"])
        if args.unit and kind != args.unit:
            continue
        if key in verdicts and not args.all:
            continue
        shown += 1
        print(f"\n### {key}   [{kind}]")
        for model in models:
            said = item["values"].get(model)
            print(f"  {model:<24} {'—' if said is None else brief(said)}")
        for model in models:
            answer = read[model].get(item["page"])
            if not answer:
                continue
            if kind == "hardest_step":
                why = (steps.get(item["page"], {}).get(model) or {}).get("why", "")
                print(f"    {model:<22} why: {brief(why)}")
                continue
            fig = figure(answer, item["unit"])
            if not fig:
                continue
            fields = {name: fig.get(name) for name in EVIDENCE.get(kind, ())
                      if fig.get(name) not in (None, "", [], {})}
            print(f"    {model:<22} {brief(fields)}")
            if kind == "type":
                said = [c for c in (answer.get("components") or ())
                        if str(c.get("key")) in SHAPE_COMPONENTS]
                print(f"      {'':<20} shapes: "
                      + (", ".join(str(c.get("key")) for c in said) or "—"))
        if key in verdicts:
            print(f"    VERDICT  {brief(verdicts[key])}")

    print(f"\n{shown} conflicts printed "
          f"({len(summary['disagreements'])} in the run, {len(verdicts)} already settled)")


if __name__ == "__main__":
    main()
