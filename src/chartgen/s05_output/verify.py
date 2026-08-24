"""Checking a model's answer against the image it was read from, with no ground truth.

An answer of the form `(key, value, box)` has a property no plain `(key, value)`
answer has: it can be shown to be wrong without anyone knowing the right answer.

    is there anything in the box       an invented region is empty
    does the box match the value       convert the region back and compare

That is the same pair of checks the render self-check runs. The only thing that
changes is who wrote the claim, so this module calls the same implementation rather
than repeating it -- an equality a test in the suite asserts, because two copies of
this arithmetic would eventually disagree and the disagreement would be silent.

    while generating   the claim is the renderer's, and a failure discards the figure
    while training     the claim is the model's, and this is a verifiable reward
    while evaluating   the claim is the model's, and this is a consistency metric
                       computable on a test set with no box annotations at all

One kind of chart has no value axis: a table-shaped one prints its numbers, so the
second check has nothing to measure and returns nothing rather than a verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

from ..common.geometry import Box
from ..common.readback import (
    Verification, background_coverage, check_mark, load_image,
)
from ..interfaces.record import Mark, Panel, Record
from ..s04_record.selfcheck import quantum_of


@dataclass(frozen=True)
class Claim:
    """What a model said about one mark: where it read it and what it read.

    `values` rather than one number, because a mark's value is not always one number
    and the geometry it is measured on depends on which numbers it holds: a stacked
    segment is read between its two running totals, a box between its quartiles. A
    claim reduced to a single value is measured against the wrong edge and marked
    wrong for being right.
    """

    key: tuple[str, ...]
    values: dict[str, float]
    box: Box
    panel_id: str = "p0"
    value_axis: str = "y"
    mark_shape: str = "rect"
    channel: str = "length"


@dataclass(frozen=True)
class Judgement:
    """What the pixels say about one claim."""

    key: tuple[str, ...]
    has_content: bool
    value_agrees: bool | None
    measured: dict[str, float]
    content_fraction: float

    @property
    def ok(self) -> bool:
        return self.has_content and self.value_agrees is not False


def as_mark(claim: Claim) -> Mark:
    """A claim in the shape the geometric checks read.

    The checks take a mark, and a model's answer is a mark with a different author.
    Building one here is what lets both sides run the identical code -- and it has to
    carry every number the claim made, or the shape's own rule about which pair of
    numbers spans its box cannot fire.
    """
    return Mark("claim", claim.panel_id, tuple(claim.key),
                {k: float(v) for k, v in claim.values.items()}, claim.box, claim.channel,
                value_axis=claim.value_axis, mark_shape=claim.mark_shape)


def judge(img: np.ndarray, claims: Sequence[Claim], panels: Sequence[Panel],
          quantum: float = 0.0) -> list[Judgement]:
    """Every claim against the pixels.

    The rounding the values were recorded at is given, not inferred from the claims:
    inferred, a claim's verdict would depend on the other claims in the batch, and an
    answer rounded to whole numbers would buy itself a wider tolerance.
    """
    by_id = {p.panel_id: p for p in panels}
    grounds = {p.panel_id: background_coverage(img, p.box) for p in panels}

    out: list[Judgement] = []
    for claim in claims:
        panel = by_id.get(claim.panel_id) or panels[0]
        background, coverage = grounds[panel.panel_id]
        result: Verification = check_mark(
            img, as_mark(claim), panel, quantum=quantum,
            background=background, coverage=coverage)
        out.append(Judgement(tuple(claim.key), result.has_content, result.value_agrees,
                             result.measured, result.content_fraction))
    return out


def verify(image_path: str | Path, claims: Sequence[Claim], panels: Sequence[Panel],
           quantum: float = 0.0) -> list[Judgement]:
    """The reward: an image, a model's answers, and the geometry the image was drawn in."""
    return judge(load_image(image_path), claims, panels, quantum)


def consistency(judgements: Sequence[Judgement]) -> dict[str, float]:
    """One number per check, over a batch of answers.

    Computable on any test set, because nothing here reads a ground-truth value.
    """
    if not judgements:
        return {"grounded": 0.0, "consistent": 0.0, "measured": 0.0}
    measured = [j for j in judgements if j.value_agrees is not None]
    return {
        "grounded": sum(j.has_content for j in judgements) / len(judgements),
        "consistent": (sum(bool(j.value_agrees) for j in measured) / len(measured)
                       if measured else 0.0),
        "measured": len(measured) / len(judgements),
    }


def claims_of(record: Record) -> list[Claim]:
    """The record's own marks as claims. What a perfect answer would look like, and
    what the generation-side self-check is really checking."""
    return [Claim(m.key, dict(m.values), m.box, m.panel_id, m.value_axis,
                  m.mark_shape, m.channel) for m in record.marks]


def quantum_of_record(record: Record) -> float:
    """The step this record's values were rounded at, read off the record itself."""
    return quantum_of([v for m in record.marks for v in m.values.values()])
