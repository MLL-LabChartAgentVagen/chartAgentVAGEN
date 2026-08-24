"""Where each segment of a mark's key is read from.

A key is an ordered tuple of strings, and its segments do not share a source. On a
two-panel figure the hospital name is read off a panel title while the department
is read off an axis tick; draw the same numbers as one panel and the hospital moves
into the legend; put it on a page as two figures and it moves into the heading. The
key does not change. Where a reader finds each part of it does.

Recording one source per figure would answer none of those questions, which is why
it is recorded per segment. It is a property of the figure rather than of the style:
style decides what a legend looks like, not whether a name is in one.
"""

from __future__ import annotations

from dataclasses import replace

import pandas as pd

from ..interfaces.figure import Binding
from ..interfaces.record import KeySource
from ..interfaces.table import TableSchema
from ..registry.charts import CHARTS


def key_sources(binding: Binding) -> tuple[KeySource, ...]:
    """Where each segment of this view's key will be drawn.

    A panel's own name is not among them. It is not part of a mark's key -- the panel
    is one of the three things a record is joined on -- and it reaches an exported key
    through the export scope instead, where it is read off the panel's drawn title.
    """
    spec = CHARTS[binding.chart_type]
    columns = binding.group_columns

    if spec.shape == "per_row":
        # The row identifier is not written anywhere: nothing on the page names it,
        # so that segment of the key cannot be recovered from the image at all.
        return ("legend",) * len(binding.dims) + ("not_shown",)

    out: list[KeySource] = []
    for i, column in enumerate(columns):
        if spec.primary_mark == "sector":
            # A pie has no category axis and no legend: the name is printed beside
            # its own wedge, and that is the only place it can be read.
            out.append("inline_label")
        elif spec.primary_channel == "printed":
            # A table prints its own row and column names inside itself.
            out.append("inline_label")
        elif spec.primary_mark == "cell":
            # A grid names both of its dimensions on ticks, one down each side. A
            # legend here would assert a colour for a name, and the cells are
            # coloured by their value.
            out.append("axis_tick")
        elif i == len(columns) - 1 and len(columns) >= 2:
            out.append("legend")
        else:
            out.append("axis_tick")
    if binding.colour_group and binding.colour_group not in columns:
        out.append("colour_only")
    return tuple(out)


def with_colour_group(binding: Binding, df: pd.DataFrame, schema: TableSchema) -> Binding:
    """Colour a view by the column its grouping column belongs to, where there is one.

    A site reports to exactly one region, so the region is not another way of
    grouping the rows -- it is a second name every bar already has. Reports carry it
    as colour with the names in the legend and nothing on the axis, and a reader who
    cannot recover it cannot say which of two identically named bars they are
    looking at.

    Nothing is added when one grouping value maps to several parent values: then the
    parent really is another grouping, and adding it would change what a mark covers.
    """
    from .project import colour_map

    if binding.colour_group or binding.key_sources or not binding.dims:
        return binding
    parent = schema.column(binding.dims[-1]).parent
    if not parent or parent in binding.group_columns:
        return binding
    candidate = replace(binding, colour_group=parent)
    if colour_map(df, candidate) is None:
        return binding
    return replace(candidate, key_sources=key_sources(candidate))
