"""The three checks a record has to pass before it is kept.

    is there anything inside the box     the box is read back off the image
    does the geometry match the value    the box is converted back into a value
    does restyling change the answer     two style versions are compared key by key

They run on every figure produced, not in the test suite. Drawing and recording in
the same statement leans on the plotting library's own coordinate transform, and
when that goes wrong nothing is raised -- what comes out is a record full of boxes
that are quietly in the wrong place. Only real data exercises it.

The first two need the image and the claimed `(value, box)` and nothing else. That
is why the same code is the reward signal during training: swap the renderer's
record for a model's answer and every line of it still applies.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Sequence

import numpy as np

from ..common.readback import (
    Verification, background_coverage, check_mark, load_image,
)
from ..interfaces.record import Record, SelfCheck

#: Steps a recorded value may sit on before it is treated as quantised. The fact
#: table rounds to whole numbers or to one decimal, and half a step of that is
#: larger than one percent on a score near four.
QUANTA: tuple[float, ...] = (1.0, 0.5, 0.1, 0.01)

#: How many marks of a figure may fail before the figure is discarded. One mark
#: clipped at the edge of the plotting area is not a reason to lose the figure; a
#: systematic offset shows up on all of them.
FAILURE_ALLOWANCE = 0.05


def quantum_of(values: Sequence[float]) -> float:
    """The step these numbers appear to be recorded on, or zero if they are not.

    Read off the record rather than carried down from the declarations: an average
    is not quantised at all while a median, a maximum and a five-number summary are
    row values and inherit the column's rounding.
    """
    finite = [v for v in values if np.isfinite(v)]
    if not finite:
        return 0.0
    for step in QUANTA:
        if all(abs(v / step - round(v / step)) < 1e-6 for v in finite):
            return step
    return 0.0


def check_figure(record: Record) -> tuple[bool, bool, tuple[str, ...]]:
    """The first two checks, mark by mark. Neither needs ground truth."""
    img = load_image(record.image_path)
    panels = {p.panel_id: p for p in record.panels}
    grounds = {pid: background_coverage(img, p.box) for pid, p in panels.items()}
    quantum = quantum_of([v for m in record.marks for v in m.values.values()])

    empty: list[str] = []
    wrong: list[str] = []
    measured = 0
    for mark in record.marks:
        panel = panels[mark.panel_id]
        background, coverage = grounds[mark.panel_id]
        result: Verification = check_mark(
            img, mark, panel, quantum=quantum,
            background=background, coverage=coverage)
        if not result.has_content:
            empty.append(f"{mark.mark_id} {mark.key}: box holds "
                         f"{result.content_fraction:.0%} ink")
        if result.value_agrees is not None:
            measured += 1
            if not result.value_agrees:
                wrong.append(f"{mark.mark_id} {mark.key}: measured {result.measured}, "
                             f"recorded {mark.values}")

    allowed = max(1, int(len(record.marks) * FAILURE_ALLOWANCE))
    reasons = tuple(empty[:5] + wrong[:5])
    return (len(empty) <= allowed, len(wrong) <= allowed if measured else True, reasons)


def answers(record: Record) -> dict[tuple[str, tuple[str, ...]], tuple[float, ...]]:
    """The key-to-value mapping a restyled rendering has to reproduce exactly."""
    return {(m.panel_id, m.key): tuple(round(v, 9) for _, v in sorted(m.values.items()))
            for m in record.marks}


def style_invariant(a: Record, b: Record) -> tuple[bool, str]:
    """Whether two style versions of one figure say the same thing.

    It needs no extra rendering: two style versions are a product in their own
    right -- a paired sample -- so the second one is already there.
    """
    left, right = answers(a), answers(b)
    if left == right:
        return (True, "")
    missing = sorted(set(left) ^ set(right))[:3]
    moved = [k for k in set(left) & set(right) if left[k] != right[k]][:3]
    return (False, f"restyling changed the answers: keys only on one side {missing}, "
                   f"values that moved {moved}")


def run(record: Record, *, variant: Record | None = None) -> Record:
    """Run every check that can be run and attach the verdict."""
    content, values, reasons = check_figure(record)
    invariant: bool | None = None
    if variant is not None:
        invariant, why = style_invariant(record, variant)
        if why:
            reasons = reasons + (why,)
    return replace(record, selfcheck=SelfCheck(content, values, invariant, reasons))


def finish(rendered, spec, *, variant: Record | None = None, provenance: bool = True,
           page_elements: bool = True, encoding: bool = True,
           tolerance: float | None = None) -> Record:
    """The whole stage: join the layers, decide readability, run the checks."""
    from ..registry.channels import RELATIVE_TOLERANCE
    from . import readable
    from .merge import merge

    record = merge(rendered, spec, provenance=provenance,
                   page_elements=page_elements, encoding=encoding)
    record = readable.apply(record, tolerance=tolerance or RELATIVE_TOLERANCE)
    return run(record, variant=variant)
