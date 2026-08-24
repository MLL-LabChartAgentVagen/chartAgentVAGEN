"""What a figure is for, in a sentence.

The caption is a training target and is never drawn on the image, which is exactly
where its value is: a sentence that only repeats the axis names teaches nothing,
because a model looking at the figure can already write it.

    a figure built from an intent   why the data was collected, and what it was to answer
    any other figure               what the view shows, from the view itself

Only the first kind carries something unreadable off the image. That is the whole
reason the intents are written in the same call as the columns, and the reason this
split exists at all -- it is a split about captions, not about titles. Every figure
gets a title, and a title is drawn.
"""

from __future__ import annotations

from ..interfaces.figure import FigureSpec
from ..interfaces.table import TableSchema, aggregate_phrase

#: How each relation reads in a caption.
RELATION_PHRASE: dict[str, str] = {
    "small_multiples": "one panel per category, on a shared scale",
    "facet": "the same measure cut by different categories",
    "drilldown": "the same measure, then one level deeper",
    "time_split": "the same view over two consecutive windows",
    "dual_metric": "two measures over the same grouping",
    "part_whole": "the same amounts read as a comparison and as shares",
    "overlay_metric": "two measures in one plotting area",
    "overlay_slice": "one measure over two slices in one plotting area",
    "overlay_range": "a value drawn with the spread it summarises",
}


def describe(spec: FigureSpec, schema: TableSchema) -> str:
    """What the views show, said once."""
    parts: list[str] = []
    for view in spec.views:
        b = view.binding
        by = " and ".join(spec.label_of(c) for c in b.group_columns)
        if len(b.measures) == 2:
            parts.append(f"{spec.label_of(b.measures[0])} against "
                         f"{spec.label_of(b.measures[1])}"
                         + (f", by {by}" if by else ""))
            continue
        measure = spec.label_of(b.measures[0]) if b.measures else ""
        how = aggregate_phrase(b.aggregate, measure)
        parts.append(how + (f" by {by}" if by else ""))
    sentence = "; ".join(dict.fromkeys(parts))
    if spec.relation in RELATION_PHRASE:
        sentence += f", {RELATION_PHRASE[spec.relation]}"
    return sentence[:1].upper() + sentence[1:] + "."


def build(spec: FigureSpec, schema: TableSchema) -> str:
    """The caption for one figure."""
    if spec.source.kind == "intent" and spec.source.intent_index is not None:
        intent = schema.intents[spec.source.intent_index]
        return (f"{describe(spec, schema)[:-1]}, shown to answer "
                f"{intent.sentence[:1].lower() + intent.sentence[1:]}. "
                f"{schema.data_context}")
    return describe(spec, schema)


def attach(specs, schema: TableSchema):
    """Give every figure in a batch its caption."""
    from dataclasses import replace

    return [replace(s, caption=build(s, schema)) for s in specs]
