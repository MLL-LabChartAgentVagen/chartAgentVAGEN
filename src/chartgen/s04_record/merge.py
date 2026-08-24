"""Joining the three layers into one record.

Each layer was written by the component that already knew it, so joining is a
lookup and never an inference:

    page elements   the page composer wrote the boxes and their categories
    encoding        the renderer wrote each mark's box, key, value and reading
    provenance      the projection returned how many rows every group covered

They meet on `(figure_id, panel_id, key)`. A layer that is switched off leaves its
column empty rather than making the others unusable, which is what lets the
provenance layer be ablated away and the run repeated.
"""

from __future__ import annotations

from dataclasses import replace

from ..interfaces.figure import FigureSpec
from ..interfaces.record import Mark, Record, RenderOutput


def row_counts(spec: FigureSpec) -> dict[tuple[str, tuple[str, ...]], int]:
    """How many source rows sit behind every mark, by panel and key."""
    out: dict[tuple[str, tuple[str, ...]], int] = {}
    for panel in spec.panels:
        for view in panel.views:
            for datum in view.data:
                out[(panel.panel_id, view.full_key(datum))] = datum.rows
    return out


def merge(rendered: RenderOutput, spec: FigureSpec, *, provenance: bool = True,
          page_elements: bool = True, encoding: bool = True) -> Record:
    """The three layers as one record, with any of them switched off.

    Row counts are stored rather than rows. The rows themselves are recoverable by
    filtering the fact table with the key, and storing them would make the record an
    order of magnitude larger for something already reproducible.

    A layer switched off leaves its column empty rather than making the others
    unusable, which is what lets a run be repeated without one and compared.
    """
    rows = row_counts(spec) if provenance else {}
    marks = tuple(replace(m, rows=rows.get((m.panel_id, m.key))) for m in rendered.marks)
    if not encoding:
        marks = ()
    return Record(
        figure_id=rendered.figure_id,
        scenario_id=rendered.scenario_id,
        image_path=rendered.image_path,
        image_size=rendered.image_size,
        style=rendered.style,
        panels=rendered.panels if encoding else (),
        marks=marks,
        legend=rendered.legend if encoding else (),
        elements=rendered.elements if page_elements else (),
        degradations=rendered.degradations,
        layout=rendered.layout,
        page_id=rendered.page_id,
        variant=rendered.variant,
        caption=rendered.caption,
    )


def unmatched(record: Record) -> tuple[Mark, ...]:
    """Marks the provenance layer had nothing for. A non-empty result means the
    renderer and the projection disagree about what was drawn."""
    return tuple(m for m in record.marks if m.rows is None)
