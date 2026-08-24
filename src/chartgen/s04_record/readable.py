"""Deciding, per mark, whether its value can be read off the image.

The rule itself lives with the chart table, because it is a property of how a value
was drawn. This applies it to what actually came out: the axis the mark says it was
measured against, and the pixel geometry that axis ended up with.

Two ways a mark loses its value target and keeps its localisation target:

    the encoding cannot reach the    a colour scale is quantised and non-linear; a
    tolerance being asked for        wedge too narrow for its radius to pin
    the key cannot be recovered      no part of the page names it

The second is why the key's sources are recorded per segment. A scatter point is
addressed by a row identifier that appears nowhere on the page: the point is still
somewhere to be found, but there is no question whose answer is its value.

Which number a mark is asked about is decided here too, beside whether it can be
read, because the two are one decision. A wedge holds a value and the share of the
whole that value is, and the angle gives the share alone -- so a wedge asked about
its value would be readable and wrong at the same time.

A pie or a heatmap can end up with no value targets at all. That is the rule
working, not a defect -- those figures still carry every localisation target they
would otherwise have.
"""

from __future__ import annotations

from dataclasses import replace

from ..common.readback import SPANNING_KEYS, axis_of, axis_pair
from ..interfaces.record import Mark, Panel, Record
from ..registry.channels import RELATIVE_TOLERANCE, readable

#: The scalar a mark is asked about when its value dictionary holds one.
VALUE_KEYS: tuple[str, ...] = ("value", "count", "y")


def target_key(mark: Mark) -> str:
    """Which entry of a mark's value dictionary a value target asks about.

    Two shapes answer this with something other than the first entry.

    A wedge holds a value and the share of the whole that value is, and only the share
    is on the page: the angle gives the share, and turning that into the value needs
    the total, which a pie writes nowhere. A wedge with its value printed on it is the
    exception -- there the number is written out and the number is the answer.

    A mark summarising a group holds five numbers and none of them is "the" value. The
    two its box runs between are the two a reader can take off the value axis, so the
    question is about the far one; the pair comes from the same table the readback
    measures against, so what is asked and what can be checked cannot drift apart.
    Asked about the median instead -- which is where this started -- the answer sits
    somewhere inside the box with nothing on the page fixing it, and every one of the
    38 such marks in a batch went out as a value target the reward path could not
    check.
    """
    if mark.mark_shape == "sector" and "share" in mark.values and not mark.labeled:
        return "share"
    for key in VALUE_KEYS:
        if key in mark.values:
            return key
    for small, large in SPANNING_KEYS.get(mark.mark_shape, ()):
        if small in mark.values and large in mark.values:
            return large
    return next(iter(mark.values), "")


def value_of(mark: Mark) -> float:
    key = target_key(mark)
    return float(mark.values[key]) if key in mark.values else 0.0


def addressable(mark: Mark) -> bool:
    """Whether every segment of this mark's key is written somewhere on the page."""
    return "not_shown" not in mark.key_src


def decide(mark: Mark, panel: Panel, *, tolerance: float = RELATIVE_TOLERANCE) -> bool:
    """Whether this mark's value is worth asking for."""
    if not addressable(mark):
        return False
    axis = axis_of(panel, mark)
    return readable(mark.channel, labeled=mark.labeled, value=value_of(mark),
                    axis=axis_pair(axis) if axis else None, tolerance=tolerance,
                    radius=panel.radius)


def apply(record: Record, *, tolerance: float = RELATIVE_TOLERANCE) -> Record:
    """Write `readable` onto every mark.

    The tolerance is the caller's. The spot-check target passes the benchmark's own
    terms; the self-check and the reward pass what the pixels can resolve, which is
    a different question with a different answer.
    """
    panels = {p.panel_id: p for p in record.panels}
    return replace(record, marks=tuple(
        replace(m, readable=decide(m, panels[m.panel_id], tolerance=tolerance),
                value_key=target_key(m))
        for m in record.marks))


def rate(record: Record) -> float:
    """Share of marks that keep a value target. Reported per chart type, because a
    dense figure or an angle-encoded one is expected to be low."""
    return (sum(1 for m in record.marks if m.readable) / len(record.marks)
            if record.marks else 0.0)
