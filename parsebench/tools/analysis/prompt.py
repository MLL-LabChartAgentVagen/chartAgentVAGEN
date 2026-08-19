"""What is sent with the page image.

Kept apart from the schema because this text is half of the response cache key:
editing a word here re-bills every page, so the file that holds it should be the
one you open on purpose.

The page's spot-check *values* go in, its *labels* do not. The values force the
answer to be about this page -- every one has to be placed on a mark -- while the
labels stay back as independent evidence, so `checks.crosscheck` can still grade
the addressing keys the model predicts against the ones the benchmark uses.
"""

from __future__ import annotations

from schema import GAP_ITEMS, GENERALITY
from vocabulary import prompt_block

SYSTEM = (
    "You read one page of a corporate or institutional report and describe, exactly, "
    "the chart constructions on it.\n\n"
    "You are not extracting data. The values this page is scored on are given to you; "
    "guessing numbers adds nothing. What is unknown is how the page is built -- how the "
    "heading is split, where it sits, what the axis ticks are, what carries the unit, "
    "which construction each value has to be read out of -- because that decides what a "
    "chart generator has to be able to draw.\n\n"
    "Two habits decide whether this answer is usable. Quote the page rather than "
    "paraphrase it: names, headings and tick labels go in verbatim, and every component "
    "you report carries the words or the drawing that show it. And report only what is "
    "on this page -- an absent component is a finding, a guessed one costs a wrong "
    "build order."
)

USER = """Here is one page, rendered whole at 150 dpi. It is a real report page: body
text, headers and footers, a figure number, source and note lines, and one to
three figures.

Work through it in this order. Each step is a field.

## 1 · Every figure, read closely

For each figure, in reading order:

**The heading, split five ways.** Report the figure number (`Figure 15`), the
title line, any further heading lines as `subtitle`, and separately the phrase
that fixes the scale of the numbers -- `USD billion (2022 prices)`, `% of GDP`,
`2011 = 100` -- wherever on the figure it sits. All verbatim. Then `placement`:
the heading block is `above` the plot, `below` it, `inside` it, or `beside` it --
`beside` meaning a side column level with the plot rather than stacked over it.
Leave a field empty rather than inventing one; an unnumbered figure has an empty
`figure_number`.

**The shape of it.** Type; when nothing in the list fits, use `other` and name the
form in `type_other` (`dumbbell`, `bullet chart`, `population pyramid`) -- an
unnamed `other` is a hole in the answer. Orientation. Panel, series and category
counts with their printed names.

**How the values are read.** `value_axis_ticks` is the tick labels as printed,
comma separated -- `0, 25, 50, 75, 100, 125, 150, 175, 200`. Empty when the
figure draws no value axis. `values_printed` says whether the numbers are written
on the marks. `source_line` is the `Source:` line verbatim.

`categories` is per panel, `marks` is the whole figure across all panels. A bar
with 4 stacked segments is 4 marks; a line with 20 plotted points is 20 marks.
Estimate when they are too dense to count, and say so in `difficulty_notes`.
`category_names` is up to 12 of them in axis order.

## 2 · Components, each with its evidence

Which of these appear anywhere on the page:

{vocabulary}

Use these keys and no others. Every entry names the figure it is on (or `page`)
and carries `evidence`: at most 20 words of English, either the words on the page
or what is drawn and where. `the y axis reads 0, 25 ... 200 and no unit appears on
it` is evidence. `the unit is in the title` only restates the key, and an entry
that cannot be evidenced should not be reported.

A construction that is on the page but has no key goes into `new_components`, with
the same evidence. That list is the most valuable thing you produce, so do not
force a near-miss into an existing key to avoid it.

## 3 · The values this page is scored on

{values}

For each, in the order given: which figure carries it, which mark it is (`the 1992
Weather-related segment`), whether that number is printed on the figure or has to
be read off the mark against the axis, and `addressing_keys` -- the labels a table
row would need to address that one value and no other, verbatim from the page.
A value you cannot place gets `not_found` and a reason; that is a real answer.

## 4 · hardest_step

The page is scored by searching a parser's markdown output for each of those
values together with the labels that address it. Four things can go wrong; say
which blocks hardest here, and argue from this page's own numbers -- the tick
spacing against the tolerance, how many keys a value needs -- not in general terms.

1. no table -- the figure gets skipped entirely, or has nothing that names its rows
2. the value -- reading it off the pixels to within 5% is out of reach
3. the labels -- how many keys it takes to address one value, and whether a table
   can carry them
4. the context -- the figure title or panel name lives outside the table, and only
   counts if it is written as bold text or a heading

## 5 · suggestions

Each names four things: what to add, where it changes, which row it adds to the
ablation table, and how general the construction is:

{generality}

The ablation row is the constraint that separates adding a capability from chasing
a benchmark -- if a change adds no ablation row, drop it. File each under one of:

{gaps}

This list exists to route a finding you already made in section 2. It is not a
checklist to find things against: do not report a component because it appears
here.

## Language

`page_note`, `difficulty_notes`, `why_it_matters` and the suggestion fields are
Chinese prose. `evidence`, `mark` and `type_other` are English. Captions, panel /
series / category names, tick labels, addressing keys, component keys and every
enum stay exactly as they are on the page.

Zero figures, an empty component list, or no suggestions are all legitimate
answers for a page that warrants them. If a figure cannot be judged from this
rendering, put it in `unreadable` rather than guessing."""


#: Appended for the one exception the design allows: a reply that describes nothing.
#: Every page in this split carries spot-check points, so it carries a figure, and an
#: empty answer is a degenerate reply rather than a finding about the page.
RETRY_NOTE = """

---

This page carries spot-check points, so it holds at least one figure. An empty
`figures` list is not an answer for it, and neither is a placeholder. Look again
and describe every figure on the page."""


def user_prompt(values: tuple[str, ...] = ()) -> str:
    """The page prompt. `values` are the page's spot-check values, labels withheld."""
    gaps = "\n".join(f"  {k} = {v}" for k, v in GAP_ITEMS.items())
    generality = "\n".join(f"  {k} = {v}" for k, v in GENERALITY.items())
    listed = ("  " + "  ·  ".join(values) if values else
              "  (none recorded for this page -- skip `spot_checks`)")
    return USER.format(vocabulary=prompt_block(), values=listed,
                       generality=generality, gaps=gaps)
