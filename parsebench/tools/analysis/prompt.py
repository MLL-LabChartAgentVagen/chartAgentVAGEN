"""What is sent with the page image, and with a batch of answers.

Kept apart from the schema because this text is half of the response cache key:
editing a word here re-bills every page and every model, so the file holding it
should be the one you open on purpose.

A page prompt carries the page's spot-check **values** and withholds its
**labels**. The values force the answer to be about this page -- each one has to be
put on a mark -- while the labels stay back as independent evidence, so the keys
the model predicts can be graded against the ones the benchmark uses.

Three prompts, matching the three calls each model makes: one page, the overview of
its own sampled pages, and the failure batch. The overview and failure prompts hand
the model the program's counts for its own answers, so its prose argues against
real numbers rather than against what it remembers reporting.

`page_user_free` is the no-vocabulary control: the same page, the same fields, no
list of 65 keys. Its component names are free text, mapped back afterwards, and the
overlap with the vocabulary run says how much of the agreement between models is
the list rather than the page.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1])]

from contract import format as contract          # noqa: E402
from contract.vocabulary import prompt_block     # noqa: E402

SYSTEM = (
    "You read one page of a corporate or institutional report and describe, exactly, "
    "the chart constructions on it.\n\n"
    "You are not extracting data. The values this page is scored on are given to you; "
    "guessing numbers adds nothing. What is unknown is how the page is built -- how the "
    "heading is split, where it sits, what carries the unit, which construction each "
    "value has to be read out of -- because that decides what a chart generator has to "
    "be able to draw.\n\n"
    "Two habits decide whether this answer is usable. Quote the page rather than "
    "paraphrase it: headings and tick labels go in verbatim, and every component you "
    "report carries the words or the drawing that show it. And report only what is on "
    "this page -- an absent component is a finding, a guessed one costs a wrong build "
    "order."
)

_PAGE_BODY = """Here is one page, rendered whole at 150 dpi. It is a real report page: body
text, headers and footers, a figure number, source and note lines, and one to
three figures.

Work through it in this order. Each step is a field.

## 1 · Every figure, read closely

For each figure, in reading order:

**The heading, split five ways.** The figure number (`Figure 15`), the title line,
any further heading lines as `subtitle`, and separately the phrase that fixes the
scale of the numbers -- `USD billion (2022 prices)`, `% of GDP`, `2011 = 100` --
wherever on the figure it sits. All verbatim. Then `placement`: the heading block
sits `above` the plot, `below` it, `inside` it, or `beside` it -- `beside` meaning
a side column level with the plot rather than stacked over it. Leave a field empty
rather than inventing one; an unnumbered figure has an empty `figure_number`.

**The shape of it.** Type; when nothing in the list fits, use `other` and name the
form in `type_other` (`dumbbell`, `bullet chart`, `population pyramid`) -- an
unnamed `other` is a hole in the answer. An entry that is not a figure at all -- a
decorative panel, a block of body text, a placeholder -- is `unreadable`, with the
reason in `type_other`.

**How dense it is.** `categories` is per panel, `marks` is the whole figure across
all panels: a bar with 4 stacked segments is 4 marks, a line with 20 plotted points
is 20 marks. Estimate when they are too dense to count. `values_printed` says
whether the numbers are written on the marks.

**Every axis it draws.** One entry per axis: which side it is on, whether it carries
a quantity, categories or time, the scale phrase written on it, its first and last
tick as printed, and `serves` -- which marks are measured against it. A panel with a
left and a right value axis gives **two** entries with role `value`, and then
`serves` is the field that matters: one pixel height on that panel means two
different numbers, and a recorded value that does not say which axis it was read
against cannot be checked. A pie or a treemap draws no axis and gives an empty list.

**What it takes to address one value.** `key_parts`, one entry per part of the
address, each with the place its label is drawn and one label verbatim. A plain bar
chart needs one part; a grouped bar in small multiples needs three or four. Use
`colour_group` only when the colour carries something the legend's series names do
not -- a performance band, a significance flag, a region -- and `colour_only` when
nothing but the colour names it.

**One value, written out in full.** `worked_example`: pick a value on this figure,
give its whole key in the order of the parts above, what it reads, whether that
number is printed or has to be read off an axis, and in `why_hard` what would make
it hard to address or to read to 5%. Pick the one that is hard rather than the one
that is easy.

{components}

## 3 · The values this page is scored on

{values}

For each, in the order given: which figure carries it, which mark it is (`the 1992
Weather-related segment`), whether that number is printed on the figure or has to
be read off the mark against the axis, and `addressing_keys` -- the labels a table
row would need to address that one value and no other, verbatim from the page. A
value you cannot place gets `not_found` and a reason; that is a real answer.

Then two more, per value rather than per page. `keys_verbatim`: whether every label
you just wrote is printed on the page exactly that way -- false when one had to be
shortened, expanded out of an abbreviation, or named after its colour, because a
table can then hold the right cell and still not be found. And `blocked_step`: the
step of the four below that this one value would block on, `0` when you expect it
to pass.

## 4 · hardest_step

The page is scored by searching a parser's markdown output for each of those values
together with the labels that address it. Four things can go wrong; say which blocks
hardest on this page.

{steps}

`hardest_step_why` is at most 30 Chinese words and has to argue from this page's own
numbers -- the tick spacing against the 5% tolerance, how many labels a value needs,
which of the values above you have in mind. A reason that would fit any page is not
a reason.

## 5 · examples

Two to five things on this page that a chart generator would have to be **rebuilt**
to produce. Each is filed under one of the changes below, names the figure, and
carries a `quote`: at most 25 words of English, the words on the page verbatim or
exactly what is drawn and where, checkable against the image on its own. `why` is at
most 30 Chinese words -- what the pipeline cannot produce today that this page shows.

{gaps}

Use `new` when none of them covers it, and then say in `why` what the change would
be. A page with nothing worth quoting returns an empty list; that is a real answer,
and padding this list is worse than leaving it short.

## 6 · report_md

Chinese markdown, at most 250 words, in three labelled parts, printed beside the
other models' as written:

- **画出来要什么** — what a chart generator would have to be able to draw to produce
  this page.
- **定位一个值难在哪** — argued from one named value on this page, not in general.
- **不确定的** — what you could not see, or had to guess.

No suggestions for the pipeline -- those belong to the report written after every
sampled page.

## Language

`report_md` is Chinese. `evidence`, `mark`, `type_other` and the component names are
English. Headings, tick labels and addressing keys stay exactly as they are on the
page."""

_WITH_VOCABULARY = """## 2 · Components, each with its evidence

Which of these appear anywhere on the page:

{vocabulary}

Use these keys and no others. Every entry names the figure it is on (or `page`) and
carries `evidence`: at most 20 words of English, either the words on the page or
what is drawn and where. `the y axis reads 0, 25 ... 200 and no unit appears on it`
is evidence. `the unit is in the title` only restates the key, and an entry that
cannot be evidenced should not be reported.

A construction that is on the page but has no key goes into `new_components`, with
the same evidence and with `affects`. That list is the most valuable thing you
produce, so do not force a near-miss into an existing key to avoid it."""

_WITHOUT_VOCABULARY = """## 2 · Components, each with its evidence

Name every construction on this page that a chart generator would have to be able to
draw: how the axes, ticks, legend, labels, annotations and layout are built. There is
no list to choose from -- give each one a `lower_snake_case` English name of your own.

Every entry names the figure it is on (or `page`) and carries `evidence`: at most 20
words of English, either the words on the page or what is drawn and where. `the y axis
reads 0, 25 ... 200 and no unit appears on it` is evidence; `the unit is in the title`
only restates the name. Also give `affects`, which of the four judgement steps in
section 4 the construction can change -- an empty array is a normal answer."""


def _values_block(values: tuple[str, ...]) -> str:
    return ("  " + "  ·  ".join(values) if values
            else "  (none recorded for this page -- leave `spot_checks` empty)")


def _steps_block() -> str:
    return "\n".join(f"{n}. {text}" for n, text in contract.STEPS.items())


def _gaps_block() -> str:
    return "\n".join(f"  {key} = {text}" for key, text in contract.GAP_ITEMS.items())


def page_user(values: tuple[str, ...]) -> str:
    """The page prompt with the fixed vocabulary in it."""
    return _PAGE_BODY.format(
        components=_WITH_VOCABULARY.format(vocabulary=prompt_block()),
        values=_values_block(values), steps=_steps_block(), gaps=_gaps_block())


def page_user_free(values: tuple[str, ...]) -> str:
    """The no-vocabulary control: same page, same fields, no list of keys."""
    return _PAGE_BODY.format(components=_WITHOUT_VOCABULARY,
                             values=_values_block(values), steps=_steps_block(),
                             gaps=_gaps_block())


def free_page_schema() -> dict:
    """`PAGE_SCHEMA` with its component enum opened up, for the control run.

    The same six fields answered the same way; only the domain of
    `components[].key` changes, because a run whose point is that no list was given
    cannot draw its names from one. `affects` comes back with each name -- with no
    vocabulary there is nothing that already fixed it.
    """
    schema = copy.deepcopy(contract.PAGE_SCHEMA)
    item = schema["properties"]["components"]["items"]
    item["properties"]["key"] = {
        "type": "string",
        "description": "a lower_snake_case English name you choose for the construction",
    }
    item["properties"]["affects"] = copy.deepcopy(
        contract.PAGE_SCHEMA["properties"]["new_components"]["items"]["properties"]["affects"])
    item["required"] = ["key", "figure_id", "evidence", "affects"]
    return schema


# --------------------------------------------------------------------------- #
# The two reports a model writes: its own pages, and its failure batch          #
# --------------------------------------------------------------------------- #

OVERVIEW_SYSTEM = (
    "You are reporting on a benchmark of published report pages, to decide what a "
    "chart-generation pipeline has to be able to draw.\n\n"
    "You have just answered a sample of those pages, and you are handed the program's "
    "counts over your own answers. Argue from those counts; do not recall your "
    "answers from memory. Every number your report uses comes back in "
    "`numbers_cited`, and the program holds each one against its own table.\n\n"
    "Two things are being asked at once and they are not on one scale: what a change "
    "does to the benchmark score, and what capability it adds to the pipeline. They "
    "get two fields. A change that only removes an ability -- generating fewer chart "
    "types, dropping a dimension -- is not a capability: rewrite it as a configurable "
    "dimension whose default is the current behaviour."
)

OVERVIEW_USER = """You answered these {n_pages} pages. Below are the program's counts over your own
answers, and the parts of the benchmark's own annotation that are checkable
without a model.

{tables}

Your own report on each page, as you wrote it:

{reports}

Write the report of the {n_pages}.

`ranked_items` is what matters, most first, and it is the only place opinions
belong. Name each item with a vocabulary key or a chart type where one fits. For
each: why it is at that position, argued from the tables above; the pages it rests
on, by name; `affects`, which of the four judgement steps it can change --

{steps}

-- an empty array being a normal answer, meaning the metric never looks at it. Then
the two effects in their own fields, `score_effect` and `capability_effect`, and
`new_ablation_row`: the row this change adds to the ablation table. A change with no
ablation row only chases the benchmark. File each under one of:

{gaps}

`headline` is the one claim the report makes, at most 40 Chinese words. If it needs
a `但是`, it is two claims and you should pick.

`report_md` is at most 600 Chinese words. Every number in it comes back as a
`numbers_cited` entry, with the table you took it from, or `自己数的`.

`limits` is at most 60 Chinese words: what {n_pages} pages cannot support, what you
could not see, where you guessed."""

FAILURE_SYSTEM = (
    "You are reading the failures of one document parser on the chart split of a "
    "benchmark, to decide what a chart-generation pipeline has to be able to draw.\n\n"
    "The division of labour is fixed. Whether a point passed comes from the official "
    "evaluation report and is never re-judged. Which *form* the failure took is "
    "computed by the program from the parser's own output tables. You supply the "
    "*mechanism*: what about the way the figure was drawn produced that form. The "
    "mechanism list is closed and each entry names the judgement step it belongs to, "
    "so the program derives the rest.\n\n"
    "Evidence is quoted from the parser's output or named on the page -- the cell, the "
    "column header, the legend entry. A restatement of the mechanism is not evidence."
)

FAILURE_USER = """A parser ran the whole chart split: 568 pages, 4,864 spot-check points, scored by
the official rule. Below are the program's counts over **every** failure in that
run, then a sample of the failures themselves.

{tables}

The sample is **equal-sized per form**, not proportional: the rare forms are where
an unknown mechanism would hide. So a mechanism count over this sample is a count
*within a form*; the program weights it back by the full-run form counts above.

Each case gives the rule (the value and the labels that must address it), the form
the program computed, and the parser's output for that page cut down to what
matters.

{cases}

Attribute every case, in the order given, one entry each. The mechanisms:

{mechanisms}

`other` is a real answer when none of them fits, and it must carry
`mechanism_note`; a mechanism that maps to none of the four judgement steps cannot
be acted on, so `other` is the only way to say so.

Then write the report over them, the same five fields as the sample report:
`headline` (≤40 Chinese words, one claim), `ranked_items` (most first, each with
`affects`, `score_effect`, `capability_effect`, `new_ablation_row`, `maps_to`),
`numbers_cited` (every number your report uses), `report_md` (≤600 Chinese words),
`limits` (≤60 Chinese words). File each ranked item under one of:

{gaps}"""


def _enum_block(table: dict) -> str:
    return "\n".join(f"  {key} = {value}" for key, value in table.items())


def overview_user(tables: str, reports: str, n_pages: int) -> str:
    """The sample overview prompt: the program's tables, and the model's own pages."""
    return OVERVIEW_USER.format(tables=tables, reports=reports, n_pages=n_pages,
                                steps=_steps_block(),
                                gaps=_enum_block(contract.GAP_ITEMS))


def failure_user(tables: str, cases: str) -> str:
    """The failure batch prompt: the full-run counts, and the sampled cases."""
    mechanisms = "\n".join(f"  {key} = {text} (step {step})"
                           for key, (step, text) in contract.MECHANISMS.items())
    return FAILURE_USER.format(tables=tables, cases=cases, mechanisms=mechanisms,
                               gaps=_enum_block(contract.GAP_ITEMS))
