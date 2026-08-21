"""The output contract: what the analyses return, and how three models are compared.

One file, because a contract split across four is a contract nobody re-reads. The
prose version, with the reasoning behind each field, is
`parsebench/review/06_output_contract.md`; the two say the same thing and the
field names are the join. The one thing not here is the component vocabulary --
65 keys with a criterion and an `affects` each, in `vocabulary.py`, which is a
data table rather than a contract.

Fixed before any model runs. A field only becomes comparable across models once
its domain is closed: a free-text component name cannot be summed, and two models
naming the same construction differently would read as a disagreement about the
page.

Five parts:

    1  domains     the closed vocabularies every schema field draws on
    2  page        what one page call returns -- a report on the page, and its facts
    3  failure     what one failure call returns -- every case attributed, and a report
    4  written     which files get written, by whom, and what each table's rows are
    5  compare     how three models' answers are put side by side

Three kinds of call per model, no more: every sampled page, one overview of them,
one failure
batch. Opinions live only in the overviews, where the model has seen its own
batch and the counts over it; a page answer carries description and evidence.

Two rules from `parsebench/TODO.md` §T0 are built into the fields rather than
left to a renderer. Every observation a model proposes carries `affects` -- which
of the four judgement steps it can change, empty meaning the metric never looks
at it. Every ranked item answers two questions that are not on one scale, in two
fields: what it does to the ParseBench score, and what capability it adds to the
generation pipeline. Nothing downstream can sort them into one column.
"""

from __future__ import annotations

from dataclasses import dataclass

from .vocabulary import KEYS

# --------------------------------------------------------------------------- #
# 1 · Domains                                                                   #
# --------------------------------------------------------------------------- #

#: What the four-step judgement of ParseBench's `ChartDataPointRule` can fail on.
#: `review/02_chart_metric.md` walks one rule through them.
STEPS = {
    1: "there is no table at all",
    2: "the value cannot be read to the tolerance",
    3: "the labels cannot be associated with the cell",
    4: "the context outside the table is not bold or a heading",
}

#: Chart types worth telling apart when counting what the benchmark contains.
#: `other` is the residue and carries `type_other`: an unnamed `other` is a hole
#: in the type mix that the family weight vector would be read off.
CHART_TYPES = (
    "bar", "grouped_bar", "stacked_bar", "line", "area", "pie", "donut", "scatter",
    "heatmap", "box", "histogram", "waterfall", "funnel", "compound", "map",
    "radar", "treemap", "gauge", "other", "unreadable",
)

#: How widely a construction is used, as the model reads it off this one page.
#: The program computes the same thing independently, from how many distinct
#: documents a component appears in, so the two can be compared.
GENERALITY = {
    "general": "most published charts of this kind do it, whoever drew them",
    "common": "a whole class of publisher does it, not all of them",
    "house_style": "this document's own convention",
}

#: The pipeline changes a suggestion can be filed under. P1-P7 are kept in sync with
#: `parsebench/review/04_pipeline_gap.md`; P8 and P9 were added after the first round
#: and did not come from an opinion -- P8 out of the `new` names three models proposed
#: independently, P9 out of the program's own component counts. `new` is for what none
#: of them covers; it is the field that keeps the review list open rather than closed.
#:
#: Nine, not thirty: one entry per thing the pipeline would have to be rebuilt around.
#: What a change decomposes into is `GAP_PARTS`, which is a reading aid and is never
#: a field a model fills.
GAP_ITEMS = {
    "P1": "readable becomes a per-mark attainable precision instead of a boolean gate",
    "P2": "the panel dimension enters the key (panel_key)",
    "P3": "a whole-page markdown export, and where a title or panel name sits "
          "relative to the table",
    "P4": "how often each chart family is generated, a weight vector -- not what a family looks like",
    "P5": "raise the density cap, making density a controlled variable",
    "P6": "three more style dimensions: value-label placement, tick format and unit "
          "position, negative values and the zero line",
    "P7": "the figure title becomes a field of its own: number, title, subtitle, unit, "
          "and where the heading block sits",
    "P8": "colour or highlight encodes an attribute the legend does not carry, and that "
          "attribute has to enter the key",
    "P9": "two value axes in one panel and bar+line mixed marks: a value has to record "
          "which axis and which mark shape it was read from",
    "new": "none of the nine covers it",
}

#: What each change decomposes into, two or three parts each. A reading aid for the
#: report -- never a schema field: a model files an example under `P9`, and the parts
#: are how the report explains what P9 would take.
GAP_PARTS = {
    "P1": ("每个 mark 记下它能被读到的精度，不再只有能读/不能读",
           "读不出的 mark 留在定位目标里，只退出数值目标"),
    "P2": ("面板名进入键，成为 panel_key",
           "面板标题的位置（面板内 / 面板上方 / 共享）成为可控维"),
    "P3": ("整页 markdown 导出：图之外还有正文、页眉、source/note",
           "标题与面板名相对表格的位置可配"),
    "P4": ("族采样从等概率改为权重向量",
           "权重向量本身是消融的一个自变量"),
    "P5": ("稠密度上限抬高，稠密度成为受控自变量",
           "稠密时的标签策略（抽稀 / 旋转 / 换行）跟着成为一维"),
    "P6": ("值标签位置：条内 / 条外 / 不画",
           "刻度格式与单位位置：轴标题 / 刻度后缀 / 系列名里",
           "负值与零线：零线居中的分叉条"),
    "P7": ("图号、标题、副标题、单位短语四个字段分开生成",
           "标题块的位置（上 / 下 / 内 / 侧）成为可控维"),
    "P8": ("颜色分组作为第三个键分量进入 key",
           "高亮（单条变色 / 加粗标签）与颜色分组分开表示"),
    "P9": ("同面板两条值轴，每条轴各自的单位与量程",
           "每个 mark 记下它对着哪条轴、是什么图元形状",
           "混合图元（bar + line 同面板）成为一个族，而不是多面板关系"),
}

assert set(GAP_PARTS) == set(GAP_ITEMS) - {"new"}


# --------------------------------------------------------------------------- #
# 2 · One page analysis                                                         #
# --------------------------------------------------------------------------- #
#
# Two fields carry most of the weight. `components[].evidence` makes every count
# checkable -- a key without the words that show it is a claim, and a frequency
# table built out of claims cannot be read. `figures[].heading` splits the caption
# into number, title, subtitle, unit and placement, because those five are
# separate generation problems and a single caption string hides all of them.

#: Which of the four steps an observation can change. Empty means the metric never
#: looks at it, which makes the observation a question about how honest the
#: generated data is rather than about the score.
_AFFECTS = {
    "type": "array",
    "items": {"type": "integer", "enum": [1, 2, 3, 4]},
    "description": "which of the four judgement steps this can change: 1 there is a "
                   "table, 2 the value is within tolerance, 3 the labels associate "
                   "with the cell, 4 the context outside the table. Empty array when "
                   "the metric never looks at it -- that is a normal answer",
}

#: The caption, split into the five things a generator would have to produce.
_HEADING = {
    "type": "object",
    "additionalProperties": False,
    "required": ["figure_number", "title", "subtitle", "unit_text", "placement"],
    "properties": {
        "figure_number": {"type": "string",
                          "description": "`Figure 15`, `Exhibit 3` as printed; empty when "
                                         "the figure is unnumbered"},
        "title": {"type": "string", "description": "the main title line, verbatim"},
        "subtitle": {"type": "string",
                     "description": "further heading lines, verbatim; empty when one line"},
        "unit_text": {"type": "string",
                      "description": "the phrase that fixes the scale -- `USD billion`, "
                                     "`% of GDP`, `2011 = 100`; empty when there is none"},
        "placement": {"type": "string", "enum": ["above", "beside", "below", "inside", "none"],
                      "description": "where the heading block sits. `beside` means a side "
                                     "column level with the plot, not stacked over it"},
    },
}

#: One axis as drawn. Two value axes in one panel are why this is a list rather than
#: a pair of fields: under two axes one pixel height means two different numbers, so a
#: recorded value that does not say which axis it was measured against is ambiguous --
#: and the pipeline's output unit is exactly a recorded value.
_AXIS = {
    "type": "object",
    "additionalProperties": False,
    "required": ["side", "role", "unit_text", "low", "high", "serves"],
    "properties": {
        "side": {"type": "string", "enum": ["left", "right", "bottom", "top", "radial", "none"]},
        "role": {"type": "string", "enum": ["value", "category", "time"],
                 "description": "what the axis carries: a quantity, named categories, "
                                "or points in time"},
        "unit_text": {"type": "string",
                      "description": "the scale phrase written on or beside this axis, "
                                     "verbatim; empty when the axis carries none"},
        "low": {"type": "string", "description": "the first tick label as printed; empty "
                                                 "when the axis has no ticks"},
        "high": {"type": "string", "description": "the last tick label as printed"},
        "serves": {"type": "string",
                   "description": "English, at most 12 words: which marks or series are "
                                  "measured against this axis. `all bars`, `only the "
                                  "orange line`. This is the whole point of the field "
                                  "when a panel has two value axes"},
    },
}

#: One component of the address of a single value on this figure -- what the pipeline
#: calls a key part. `colour_group` and `panel` are the two the current key does not
#: carry, so they are named rather than folded into `series`.
_KEY_PART = {
    "type": "object",
    "additionalProperties": False,
    "required": ["role", "label_source", "example"],
    "properties": {
        "role": {"type": "string",
                 "enum": ["category", "series", "panel", "colour_group", "time"],
                 "description": "`colour_group` only when the colour carries an attribute "
                                "the legend's series names do not -- a performance band, "
                                "a significance flag, a region"},
        "label_source": {"type": "string",
                         "enum": ["axis_tick", "legend", "panel_title", "inline_label",
                                  "heading", "colour_only", "not_shown"],
                         "description": "where the label that names this part is drawn. "
                                        "`colour_only` means the reader has to name it by "
                                        "its colour, because no text gives it"},
        "example": {"type": "string",
                    "description": "one label of this part, verbatim from the page"},
    },
}

#: One value on this figure, fully addressed. The single most useful thing a page
#: answer carries: it is the pipeline's own output unit, written out by hand for a
#: real published figure, so it can be held against what the pipeline emits.
_WORKED = {
    "type": "object",
    "additionalProperties": False,
    "required": ["key", "value", "value_source", "why_hard"],
    "properties": {
        "key": {"type": "array", "items": {"type": "string"},
                "description": "the full address of one value on this figure, one entry "
                               "per key part above, in that order, verbatim from the page"},
        "value": {"type": "string", "description": "what that mark reads, as printed or as "
                                                   "read off the axis"},
        "value_source": {"type": "string", "enum": ["printed", "axis_read", "not_readable"]},
        "why_hard": {"type": "string",
                     "description": "English, at most 20 words: what makes this one hard "
                                    "to address or to read to 5%. Empty when nothing does"},
    },
}

_FIGURE = {
    "type": "object",
    "additionalProperties": False,
    "required": ["id", "heading", "type", "type_other", "panels", "series", "categories",
                 "marks", "values_printed", "axes", "key_parts", "worked_example"],
    "properties": {
        "id": {"type": "string", "description": "f1, f2, ... in reading order"},
        "heading": _HEADING,
        "type": {"type": "string", "enum": list(CHART_TYPES),
                 "description": "`unreadable` for an entry that is not a figure at all -- "
                                "a placeholder, a block of body text, a decorative panel"},
        "type_other": {"type": "string",
                       "description": "when type is `other`, name the form in two or three "
                                      "English words (`dumbbell`, `bullet chart`); empty "
                                      "otherwise. When type is `unreadable`, say why"},
        "panels": {"type": "integer", "description": "1 for a single-panel figure"},
        "series": {"type": "integer",
                   "description": "distinct legend entries, 1 when there is no legend"},
        "categories": {"type": "integer",
                       "description": "distinct slots on the category or time axis, per panel"},
        "marks": {"type": "integer",
                  "description": "individually drawn marks across all panels: bars, stacked "
                                 "segments, points, slices, cells"},
        "values_printed": {"type": "string", "enum": ["all", "some", "none"],
                           "description": "whether the numbers are written on the figure"},
        "axes": {"type": "array", "items": _AXIS,
                 "description": "every axis drawn on this figure. A panel with a left and "
                                "a right value axis gives two entries with role `value`; "
                                "a pie or a treemap gives none"},
        "key_parts": {"type": "array", "items": _KEY_PART,
                      "description": "what it takes to address one value on this figure, "
                                     "one entry per part. A plain bar chart has one; a "
                                     "small-multiples grouped bar has three or four"},
        "worked_example": _WORKED,
    },
}

#: One vocabulary key, with the thing on the page that shows it. No `affects` here:
#: the vocabulary fixes it for these 65 keys before any page is seen.
_COMPONENT = {
    "type": "object",
    "additionalProperties": False,
    "required": ["key", "figure_id", "evidence"],
    "properties": {
        "key": {"type": "string", "enum": list(KEYS)},
        "figure_id": {"type": "string",
                      "description": "the figure it appears on, or `page` when it is a "
                                     "property of the page rather than of one figure"},
        "evidence": {"type": "string",
                     "description": "English, at most 20 words: the words on the page that "
                                    "show it, quoted, or what is drawn and where. `the y "
                                    "axis reads 0, 25, ... 200 with no unit` is evidence; "
                                    "`the unit is in the title` is a restatement of the key"},
    },
}

#: One quotable thing on the page, filed under the change it argues for. The report
#: is built out of these: a claim about a page that carries no quote off that page
#: cannot be checked, and a change with no example under it is a change nobody has
#: seen the need for.
_EXAMPLE = {
    "type": "object",
    "additionalProperties": False,
    "required": ["gap", "figure_id", "quote", "why"],
    "properties": {
        "gap": {"type": "string", "enum": list(GAP_ITEMS),
                "description": "the change this argues for; `new` when none of them covers "
                               "it, and then `why` has to name what would"},
        "figure_id": {"type": "string", "description": "the figure, or `page`"},
        "quote": {"type": "string",
                  "description": "English, at most 25 words: the words on the page, "
                                 "verbatim, or exactly what is drawn and where. Has to be "
                                 "checkable against the image on its own"},
        "why": {"type": "string",
                "description": "Chinese, at most 30 words: what the pipeline cannot produce "
                               "today that this page shows"},
    },
}

#: One page, one call. Eight fields: a report, what is on the page, and the one
#: prediction the annotation can score. Opinions are not here -- they belong to the
#: overview, where the model has seen its own sampled pages and the counts over them.
PAGE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["report_md", "figures", "components", "new_components", "spot_checks",
                 "hardest_step", "hardest_step_why", "examples"],
    "properties": {
        "report_md": {"type": "string",
                      "description": "Chinese markdown, at most 250 words, in three "
                                     "labelled parts: `画出来要什么` -- what a chart "
                                     "generator would have to be able to draw to produce "
                                     "this page; `定位一个值难在哪` -- argued from one "
                                     "named value on it; `不确定的` -- what you could not "
                                     "see or had to guess. Printed as written, beside the "
                                     "other models'"},
        "figures": {"type": "array", "items": _FIGURE},
        "components": {"type": "array", "items": _COMPONENT,
                       "description": "every vocabulary key present anywhere on the page, "
                                      "each with the evidence for it"},
        "new_components": {
            "type": "array",
            "description": "constructions the vocabulary has no key for. A name repeated "
                           "across enough pages earns a key of its own in the next round",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "figure_id", "evidence", "affects"],
                "properties": {
                    "name": {"type": "string",
                             "description": "a lower_snake_case key you propose, English"},
                    "figure_id": {"type": "string", "description": "the figure, or `page`"},
                    "evidence": {"type": "string",
                                 "description": "English, at most 20 words: what on the page "
                                                "shows it"},
                    "affects": _AFFECTS,
                },
            },
        },
        "spot_checks": {
            "type": "array",
            "description": "one entry per value listed in the prompt, in the order given",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["value", "figure_id", "mark", "printed_on_figure",
                             "addressing_keys", "keys_verbatim", "blocked_step"],
                "properties": {
                    "value": {"type": "string", "description": "the value, copied back"},
                    "figure_id": {"type": "string",
                                  "description": "the figure carrying it, or `not_found`"},
                    "mark": {"type": "string",
                             "description": "English: which mark it is, e.g. `the 1992 "
                                            "Weather-related segment`, or why it cannot "
                                            "be placed"},
                    "printed_on_figure": {"type": "boolean",
                                          "description": "whether that number is written on "
                                                         "the figure, rather than read off "
                                                         "the mark against the axis"},
                    "addressing_keys": {
                        "type": "array", "items": {"type": "string"},
                        "description": "the labels a table row would need to address this "
                                       "one value and no other, verbatim from the page"},
                    "keys_verbatim": {
                        "type": "boolean",
                        "description": "whether every one of those labels is printed on the "
                                       "page exactly as you wrote it. False when one had to "
                                       "be shortened, expanded from an abbreviation, or "
                                       "named after a colour -- a table can then hold the "
                                       "right cell and still not be found"},
                    "blocked_step": {
                        "type": "integer", "enum": [0, 1, 2, 3, 4],
                        "description": "the step this one value would block on, 0 when you "
                                       "expect it to pass. Per value, not per page"},
                },
            },
        },
        "hardest_step": {"type": "integer", "enum": [1, 2, 3, 4],
                         "description": "the step of the four this page blocks on"},
        "hardest_step_why": {
            "type": "string",
            "description": "Chinese, at most 30 words: argued from this page's own "
                           "numbers -- the tick spacing against the 5% tolerance, how many "
                           "labels a value needs, which spot-check value you have in mind. "
                           "Without this a disagreement between models cannot be settled"},
        "examples": {
            "type": "array", "items": _EXAMPLE,
            "description": "two to five things on this page that a generator would have to "
                           "be rebuilt to produce, each filed under one change. This is "
                           "what the report quotes; a page with nothing worth quoting "
                           "returns an empty list, which is a real answer"},
    },
}


# --------------------------------------------------------------------------- #
# 3 · The failure run, and the overview each model writes                       #
# --------------------------------------------------------------------------- #
#
# The division of labour is fixed and does not move: the program says *what*
# happened, the model says *why*. Whether a spot check passed comes from the run's
# own `_evaluation_report.json` and is never re-judged; which form the failure took
# is computed from the parser's output tables; the model is handed both and asked
# only for the mechanism.
#
# One call per model, not one per case. The per-case answer has to stay -- three
# models can only be compared case by case -- but a call per case buys nothing:
# the cases are text, they fit in one context, and the model that has just read all
# fifty is the one that should write the overview of them. So the failure call
# returns the attributions and the overview together.
#
# Mechanisms are a closed list for the same reason component keys are, and each
# names the step of the four it belongs to, so the program derives `affects` and
# does not ask for it.

#: The forms the program computes from the run output, and hands the model as input.
#: `series_swap` and `stack_confusion` were candidate forms the last round could not
#: separate from an ordinary misread; they come back as mechanisms instead, where
#: they are a claim about the drawing rather than a count.
FORMS = {
    "no_table": "the page produced no table at all",
    "label_unlinked": "the value is in a table, but a label will not associate with its cell",
    "row_missing": "one of the addressing labels is nowhere in the output",
    "value_off": "the addressed cell holds a different number",
    "unit_mismatch": "the addressed cell holds the same number at another scale",
    "value_absent": "the labels are all there, but that value was never written",
}

#: Where a label the metric could not associate turned out to live. Also computed
#: by the program.
LABEL_HOMES = (
    "in_a_table_but_not_addressing",
    "in_another_table_only",
    "emphasised_before_a_table",
    "emphasised_after_the_table",
    "plain_text_only",
    "absent_from_the_output",
)

#: What about the drawing produced that form, and which step it belongs to.
MECHANISMS = {
    "key_off_the_value_row": (3, "the key is in the table but on another row, column or header"),
    "key_only_in_another_table": (3, "the figure was split into several tables and the key stayed in one of the others"),
    "key_only_in_prose": (3, "the key was written as running text, not into any table"),
    "series_identified_by_colour": (3, "the series name is only in the legend, and the column was named after its colour"),
    "panel_name_dropped": (3, "a multi-panel figure lost the panel name, so the remaining keys address several cells"),
    "value_read_off_wrong_mark": (2, "the number belongs to a neighbouring mark or series"),
    "value_interpolated_off_axis": (2, "no number is printed and the tick spacing leaves the reading short of the tolerance"),
    "stacked_total_vs_segment": (2, "a segment was read as the cumulative total, or the total as a segment"),
    "scale_word_ignored": (2, "the scale stated in the title, axis or label was not applied"),
    "value_domain_ignored": (2, "the quantity can only take certain values (a count, a rank) and the reading is between them"),
    "non_data_mark_read_as_data": (2, "a reference line, callout or shaded band was transcribed as a series"),
    "figure_not_transcribed": (1, "the figure produced no table, only surrounding text"),
    "other": (0, "none of the above; say what it was in `mechanism_note`"),
}

#: The step each mechanism belongs to. The program derives an attribution's
#: `affects` from this rather than asking for it. `other` maps to no step and must
#: carry a note.
MECHANISM_STEP = {key: step for key, (step, _) in MECHANISMS.items()}

assert set(MECHANISM_STEP.values()) <= set(STEPS) | {0}

_ATTRIBUTION = {
    "type": "object",
    "additionalProperties": False,
    "required": ["case_id", "mechanism", "mechanism_note", "evidence"],
    "properties": {
        "case_id": {"type": "string", "description": "the identifier given in the prompt"},
        "mechanism": {"type": "string", "enum": list(MECHANISMS),
                      "description": "what about the way the figure was drawn produced "
                                     "the form the program computed"},
        "mechanism_note": {"type": "string",
                           "description": "Chinese, at most 30 words. Required when the "
                                          "mechanism is `other`; empty otherwise"},
        "evidence": {"type": "string",
                     "description": "English, at most 25 words: quoted from the parser's "
                                    "output or named on the page -- the cell, the column "
                                    "header, the legend entry. Not a restatement of the "
                                    "mechanism"},
    },
}

#: The five fields of a report a model writes about its own batch. It is handed the
#: program's tables for that batch, so the prose is written against real counts
#: instead of against what it remembers reporting.
#:
#: `numbers_cited` is why the prose is worth putting in a schema: every number the
#: report uses comes back as a field, so the program can hold each one against its
#: own table. That check -- 模型自报 vs 程序实测 -- does not exist unless the models
#: write reports.
_OVERVIEW_FIELDS = {
    "headline": {"type": "string",
                 "description": "Chinese, at most 40 words: the one claim this report "
                                "makes. If it needs a `但是`, it is two claims"},
    "ranked_items": {
        "type": "array",
        "description": "your own ordering of what matters, most first. This is the part "
                       "three models are compared on, and the only place opinions belong",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "required": ["what", "why", "evidence", "affects", "score_effect",
                         "capability_effect", "new_ablation_row", "maps_to"],
            "properties": {
                "what": {"type": "string",
                         "description": "Chinese: the gap or the mechanism, named with a "
                                        "vocabulary key or a mechanism name where one fits"},
                "why": {"type": "string",
                        "description": "Chinese, at most 40 words: why it is at this "
                                       "position. Argue from the tables you were given"},
                "evidence": {"type": "array", "items": {"type": "string"},
                             "description": "the pages or case ids this rests on, by name"},
                "affects": _AFFECTS,
                "score_effect": {"type": "string",
                                 "description": "Chinese, at most 30 words; write "
                                                "`度量看不见它` when `affects` is empty"},
                "capability_effect": {"type": "string",
                                      "description": "Chinese, at most 30 words: what the "
                                                     "generation pipeline can do afterwards "
                                                     "that it cannot do now. A change that "
                                                     "only removes an ability does not "
                                                     "belong here -- rewrite it as a "
                                                     "configurable dimension whose default "
                                                     "is the current behaviour"},
                "new_ablation_row": {"type": "string",
                                     "description": "Chinese: the row this adds to the "
                                                    "ablation table; without one the change "
                                                    "only chases the benchmark"},
                "maps_to": {"type": "string", "enum": list(GAP_ITEMS)},
            },
        },
    },
    "numbers_cited": {
        "type": "array",
        "description": "every number your report_md uses, one entry each. The program "
                       "checks each against its own table; a mismatch is recorded, not "
                       "corrected",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "required": ["claim", "value", "source"],
            "properties": {
                "claim": {"type": "string", "description": "Chinese: what the number counts"},
                "value": {"type": "string", "description": "the number as you wrote it"},
                "source": {"type": "string",
                           "description": "which table you took it from, or `自己数的`"},
            },
        },
    },
    "report_md": {"type": "string",
                  "description": "Chinese markdown, at most 600 words: your report. "
                                 "Printed as written, beside the other two models'"},
    "limits": {"type": "string",
               "description": "Chinese, at most 60 words: what this report cannot support "
                              "-- sample size, what you could not see, where you guessed"},
}

_OVERVIEW_REQUIRED = ["headline", "ranked_items", "numbers_cited", "report_md", "limits"]

#: One call per model, after its sampled pages are answered and counted.
OVERVIEW_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": _OVERVIEW_REQUIRED,
    "properties": dict(_OVERVIEW_FIELDS),
}

#: One call per model for the whole failure batch: every case attributed, and the
#: report over them, written by the model that just read them.
FAILURE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["attributions", *_OVERVIEW_REQUIRED],
    "properties": {
        "attributions": {"type": "array", "items": _ATTRIBUTION,
                         "description": "one entry per case given in the prompt, in the "
                                        "order given"},
        **_OVERVIEW_FIELDS,
    },
}


# --------------------------------------------------------------------------- #
# 4 · What gets written                                                         #
# --------------------------------------------------------------------------- #
#
# Five kinds of file. A page gets one file holding all three reports of it rather
# than one file per model per page: the three are read against each other and
# against the same image, and splitting them by model would mean opening three
# files to compare one page.
#
# Every table says what one row is and which columns it carries, because that is
# what fixes the analysis: three models can only be compared per column.

PROVENANCE = ("rule_checkable", "program_measured", "model_claim")

#: Who writes what. All three write; only one of them may state a number.
AUTHORSHIP = {
    "模型": "报告正文与它自己的排序：每页一段 `report_md`，加上两份 overview"
            "（样例一份、失败一份），都随结构化字段在同一次回答里出",
    "程序": "全部数字：计数、一致率、判分、失败统计、模型自报与实测的对账；"
            "并把三家的答案渲染成下面的文件。**唯一的数字来源**，随时可重跑",
    "agent": "裁决三家的冲突（写进 `verdicts.json`），以及读完全部之后的 `INDEX.md` "
             "与它的 `view.html`。**不产生任何数字**",
}

#: How many calls each model makes. A page is one call; the whole failure batch is
#: one call; the sample overview is one call after the pages are counted.
WORKLOAD = {
    "页面分析": "每家 × 100 页 = 300 次，`PAGE_SCHEMA`。每次的 `report_md` 就是这一页的报告",
    "样例 overview": "每家 1 次 = 3 次，`OVERVIEW_SCHEMA`。输入是它自己那 100 份答案 + "
                     "程序为它算好的表",
    "失败批次": "每家 1 次 = 3 次，`FAILURE_SCHEMA`。抽样的 case 一次全给，返回逐条归因 "
                "加这一家的失败 overview",
    "无词表对照": "三家取一家 × 100 页 = 100 次，`PAGE_SCHEMA`，prompt 里不给词表",
}

#: Which failure cases the models are asked about. Equal size per form rather than
#: proportional: the rare forms are where an unknown mechanism would hide, and
#: `label_unlinked` at two thirds of the run would otherwise take the whole sample.
#: A mechanism count over this sample is therefore a count *within a form*; a
#: run-level number is that distribution weighted by the program's full-run form
#: counts, which are computed over every failure and not sampled at all.
CASE_SAMPLE = "每形态 10 条（不足 10 的全取，约 50 条），按种子抽；形态计数仍在全部失败上算"

#: The agent's verdicts on conflicting items, as data rather than as hand-edited
#: markdown: the files stay regenerable and a verdict survives a re-render.
VERDICTS = "parsebench/data/analysis/verdicts.json"

#: Where the raw answers live. Every file below is rendered from these.
RAW_ANSWERS = "parsebench/data/analysis/<model>/<page>.json"


@dataclass(frozen=True)
class Table:
    """One table in a report: what a row is, and what the columns say about it."""

    title: str
    row: str
    columns: tuple[str, ...]
    provenance: str


@dataclass(frozen=True)
class Section:
    """One section of a report: the question it answers, and its tables."""

    id: str
    title: str
    question: str
    tables: tuple[Table, ...]


@dataclass(frozen=True)
class Report:
    """One file that gets written, who writes it, and what it is for."""

    path: str
    by: str                      # keys of `AUTHORSHIP`, joined by ` + `
    what: str
    sections: tuple[Section, ...]


PAGE_FILE = Report(
    "parsebench/reports/pages/<page>.md", "模型 + 程序",
    "一页一份：三家对这一页的报告并排，加上判分与冲突。裁决面",
    (
        Section("1", "三家怎么读这一页", "同一张图，三份报告", (
            Table("页面", "这一页",
                  ("页名", "文档", "文档级 tags", "抽查点数", "页面图像路径"),
                  "program_measured"),
            Table("报告", "一家模型", ("模型", "report_md（≤150 词，原样印出）"), "model_claim"),
            Table("图表分解", "(模型, 图序号)",
                  ("模型", "图序号", "类型", "图元数", "图号", "标题位置", "数值印不印"),
                  "model_claim"),
            Table("组件命中", "一个 key",
                  ("key", "三家各自报没报", "每家的证据原文"), "model_claim"),
            Table("词表外的自拟名字", "一个名字",
                  ("名字", "哪家报的", "affects", "证据原文"), "model_claim"),
        )),
        Section("2", "抽查点", "值给了模型、标签没给，所以这一节是判分", (
            Table("定位键", "一个抽查点",
                  ("值", "规则的真实标签", "三家各自预测的键", "三家各自对错",
                   "这个点在失败运行里过没过"), "rule_checkable"),
        )),
        Section("3", "分歧与裁决", "这一页上三家说法不同的地方", (
            Table("冲突", "一个冲突项",
                  ("量", "三家各自的取值", "人工裁决", "裁决理由"), "model_claim"),
        )),
    ),
)

MODEL_REPORT = Report(
    "parsebench/reports/<model>.md", "模型",
    "这一家自己的两份 overview：读完那 100 页之后一份，读完自己的归因之后一份",
    (
        Section("1", "样例 overview", "它读完自己那 100 页之后写的", (
            Table("结论", "一句话", ("headline（≤40 词）",), "model_claim"),
            Table("它的排序", "一条",
                  ("what", "why", "证据页", "affects", "对分数", "对能力", "归入哪条 P"),
                  "model_claim"),
            Table("正文", "一段散文", ("report_md（≤600 词）", "limits（≤60 词）"),
                  "model_claim"),
        )),
        Section("2", "失败 overview", "它读完自己那批 case 之后写的，结构相同", (
            Table("结论与排序", "一条", ("headline", "ranked_items 同上"), "model_claim"),
        )),
        Section("3", "它引用的数字", "逐条与程序的表对账", (
            Table("对账", "一个数字",
                  ("claim", "模型自报的值", "它说的来源", "程序实测的值", "一致否"),
                  "program_measured"),
        )),
    ),
)

COMPARE_REPORT = Report(
    "parsebench/reports/compare.md", "程序",
    "全部数字：样例与失败两批的汇总表、三家的一致率、判分与对账。没有结论",
    (
        Section("1", "缺口表", "基准里有、而 storyline 没有定义的东西", (
            Table("组件缺口", "一个词表 key",
                  ("key", "三家各自的页数", "一致性", "affects", "文档分布",
                   "我们画不画得出", "归入哪条 P", "一页实例（链到逐页文件）"),
                  "model_claim"),
            Table("类型缺口", "一个图表类型",
                  ("类型", "三家各自的图数", "一致性", "条件表有没有这一族"), "model_claim"),
        )),
        Section("2", "基准长什么样", "描述，没有待办；每一格三家并列，不合并", (
            Table("配比", "一个取值",
                  ("维度（类型 / 数值印不印 / 稠密度档 / 标题）", "取值", "三家各自的数"),
                  "model_claim"),
            Table("卡在哪一步", "四步之一",
                  ("步", "三家各自的页数", "同一批页在失败运行里实际卡住的步"), "model_claim"),
        )),
        Section("3", "失败", "形态由程序算，机制由三家归因", (
            Table("失败形态", "一种形态", ("形态", "个数", "占失败", "失联键的去向"),
                  "program_measured"),
            Table("单变量", "一个自变量的一档",
                  ("自变量", "档", "通过率", "n", "95% 区间"), "rule_checkable"),
            Table("机制", "一个机制",
                  ("机制", "归入哪一步", "三家各自的条数", "一致率", "冲突数",
                   "一个实例（case_id + 页名）"), "model_claim"),
        )),
        Section("4", "能不能信", "这些数字是怎么来的", (
            Table("调用口径", "一家模型",
                  ("模型", "effort", "图像 dpi", "调用次数", "输入 / 输出 token", "用时"),
                  "program_measured"),
            Table("判分", "一家模型", ("模型", "落位的值数", "对的数", "命中率"),
                  "rule_checkable"),
            Table("一致率", "一个对齐量",
                  ("量", "三家一致", "两家", "一家", "冲突", "一致率"), "program_measured"),
            Table("自报 vs 实测", "(模型, 一个被引用的数字)",
                  ("模型", "claim", "模型自报", "程序实测", "一致否"), "program_measured"),
            Table("词表控制", "一个模型的两次跑法",
                  ("模型", "有词表报出的 key 数", "无词表映回后重合的 key 数", "重合率"),
                  "program_measured"),
        )),
    ),
)

INDEX_REPORT = Report(
    "parsebench/reports/INDEX.md", "agent",
    "读完上面全部之后的那一份：裁决分歧、得出要加什么能力、每条标可信度。"
    "**唯一有结论的报告**",
    (
        Section("1", "要改什么", "缺口里哪些进改造清单，依据是哪一行", (
            Table("改造清单", "一条要加的能力",
                  ("能力", "证据来自哪一张表", "三家一致性", "可信度层", "affects",
                   "对分数", "对能力", "新增的消融行", "归入哪条 P",
                   "一页实例（链到逐页文件）"), "model_claim"),
        )),
        Section("2", "失败说明什么", "机制翻成能力，以及每条的价", (
            Table("机制 → 能力", "一个机制",
                  ("机制", "归入哪一步", "占失败", "三家一致性", "要加的能力",
                   "一个实例（case_id + 页名）"), "model_claim"),
        )),
        Section("3", "与 P1–P7 的对齐", "扩哪一条、加哪一条新的、删哪一条", (
            Table("P 对齐", "一条 P", ("P", "扩 / 加 / 删", "依据"), "model_claim"),
        )),
        Section("4", "没进清单的与还没裁决的", "报了但不做的，以及为什么", (
            Table("不做", "一条被排除的意见",
                  ("意见", "排除理由（只有一家 / 不加能力 / 证据不足）"), "model_claim"),
            Table("待裁决", "一个还没裁决的冲突",
                  ("量", "页", "三家各自的取值", "为什么还没定"), "model_claim"),
        )),
        Section("5", "能不能信", "这一份的结论建立在什么上", (
            Table("折价", "一条口径",
                  ("口径", "内容（三层可信度的分布 · 词表控制的重合率 · "
                   "定位键预测的命中率 · 自报与实测对不上的条数 · 分母）"),
                  "program_measured"),
        )),
    ),
)

VIEW = Report(
    "parsebench/reports/view.html", "agent",
    "`INDEX.md` 的图示版，三个分区一一对应；每一项配一页实例与证据原文，自足",
    (
        Section("1", "要改什么", "`INDEX.md` §1 的分区", (
            Table("组件缺口卡片", "一个词表 key",
                  ("key", "三家各自的页数", "一致性", "affects", "对分数", "对能力",
                   "实例页图像", "证据原文"), "model_claim"),
        )),
        Section("2", "失败长什么样", "`INDEX.md` §2 的分区", (
            Table("失败卡片", "一个机制",
                  ("机制", "归入哪一步", "条数", "一致率", "实例页图像", "证据原文"),
                  "model_claim"),
        )),
        Section("3", "要加的能力", "`INDEX.md` §3 的分区", (
            Table("能力卡片", "一条能力",
                  ("能力", "证据来自哪一份", "可信度层", "对分数", "对能力", "新增的消融行"),
                  "model_claim"),
        )),
    ),
)

REPORTS = (PAGE_FILE, MODEL_REPORT, COMPARE_REPORT, INDEX_REPORT, VIEW)

#: Numbers a model must never be the source of. Each is computable without a model.
PROGRAM_ONLY = {
    "每个组件出现在几页、几份文档": "对模型回答里的 key 计数，不问模型频次",
    "通过率与 95% 区间": "取自官方 _evaluation_report.json，不重判分",
    "失败形态的计数": "由解析器输出的表算出，模型只归因不计数",
    "规则实际用了几个标签": "chart.jsonl 的 labels 长度",
    "定位键预测的对错": "规则标签与模型预测的双向子串匹配，与基准自己的匹配方式一致",
    "页面文字量": "PDF 文字层实测",
    "三家的一致性与一致率": "对齐后按下面的判据算，不问模型",
    "模型自报的数字对不对": "拿 numbers_cited 逐条与程序的表比，对不上记录不改写",
}


# --------------------------------------------------------------------------- #
# 5 · How three models' answers are compared                                    #
# --------------------------------------------------------------------------- #
#
# The comparison is per page and per quantity, never per report: two reports that
# agree on totals can disagree on every page and cancel out.
#
# A quantity is on this list only because a decision consumes it. That is the same
# test the change list is held to, applied to the analysis itself -- a column that
# nothing reads is a column that gets argued about for free.

@dataclass(frozen=True)
class Quantity:
    """One thing three answers are aligned on."""

    name: str
    unit: str            # what one comparable item is
    equal_when: str      # when two models are counted as saying the same thing
    provenance: str
    consumer: str        # the decision that reads it; without one it is not here


SAMPLE_QUANTITIES = (
    Quantity("组件命中集合", "(页, key)",
             "同一页同一个 key 都被报出",
             "model_claim", "改造清单第 1 节的每一行"),
    Quantity("图表类型判定", "(页, 图序号)",
             "type 相同；`other` 还要 type_other 归一化后相同",
             "model_claim", "类型配比 → P4 的族权重向量"),
    Quantity("数值印不印", "(页, 图序号)", "values_printed 三值相同",
             "model_claim", "P6 的标注形态；也是失败分析里最大的控制变量"),
    Quantity("稠密度档", "(页, 图序号)",
             "marks 落在同一档（≤20 / 21–60 / 61–150 / 151–400 / >400）",
             "model_claim", "P5 的稠密度上限"),
    Quantity("标题", "(页, 图序号)",
             "figure_number 有无相同，且 placement 四值相同。标题正文不比",
             "model_claim", "P7 的图号与位置两维"),
    Quantity("卡在哪一步", "页", "hardest_step 相同",
             "model_claim", "与失败运行实测的步对照，校准模型的判断"),
    Quantity("同向两条值轴", "(页, 图序号)",
             "同一张图上承载数值的轴占了同一对边（左右 / 上下）的一边还是两边。"
             "数的是边不是轴：小面板图每个面板各画一条左轴，那仍然只是一边",
             "model_claim", "P9 的双轴：两条平行值轴时一个像素高度对应两个值。"
             "散点的 x/y 两个量纲互相垂直，不算这一项"),
    Quantity("键分量", "(页, 图序号)",
             "key_parts 的 role 集合相同（类目 / 系列 / 面板 / 颜色分组 / 时间）",
             "model_claim", "P2 的面板维与 P8 的颜色分组——键要几段才够"),
    Quantity("模型自报 vs 程序实测", "(模型, 一个被引用的数字)",
             "模型 overview 里 `numbers_cited` 的值与程序同一张表里的值相等",
             "program_measured",
             "报告可不可信的直接检验；只有模型写了 overview 才存在这一项"),
    Quantity("排序", "(模型, 排在前三的项)",
             "三家的 `ranked_items` 前三名按 `what` 归一化后的集合相同",
             "model_claim", "改造清单的次序——上一轮的次序只有一个观察者"),
    Quantity("定位键预测", "(页, 抽查点)",
             "与规则的真实标签逐条判对错，三家各自得一个分——这一项问「谁对」，"
             "不问「谁和谁一致」",
             "rule_checkable", "唯一可核的量，用来校准上面五条的可信度；同时是 P2 的证据"),
)

FAILURE_QUANTITIES = (
    Quantity("失败机制", "case_id", "mechanism 相同；affects 不同记为冲突",
             "model_claim", "`compare.md` §3 与 `INDEX.md` §2"),
)

#: Dropped on purpose, so the next round does not re-add them by reflex.
NOT_ALIGNED = {
    "抽查点落到哪张图": "与定位键预测是同一条链，并入那一项",
    "标题正文": "比的是抄写差异不是读图差异；只比图号有无与位置",
    "系列名 / 类目名": "同上",
}

#: 三家一致 / 两家 / 一家，以及冲突的定义。差异表按这四类分栏。
AGREEMENT = {
    "unanimous": "三家都报了这一项，且按 `equal_when` 相等",
    "majority": "两家相同，第三家沉默（没报，不是报了别的）",
    "single": "只有一家报了这一项",
    "conflict": "两家以上报了，但取值不同——包括 affects 不同、类型不同、步骤不同",
}

#: 结论怎么用这四类。这条规则先于任何数字。
DECISION = {
    "unanimous": "直接进改造清单",
    "majority": "进清单，标注为两家",
    "single": "单列，不进清单",
    "conflict": "单列，需要人工看页面裁决；裁决结果写进报告，不改模型的原答案",
}

#: 一致率怎么算：分母是至少一家报过的项，分子是 unanimous 的项。按页算再平均，
#: 与基准自己的按页平均口径一致。
AGREEMENT_RATE = "unanimous / (unanimous + majority + single + conflict)，按页平均"

#: Two controls on the vocabulary itself. It was grown by one model over the last
#: round's 192 pages, so handing the same 65 keys to three models makes some of
#: their agreement an artefact of the list rather than of the pages. Neither
#: control is optional: without them the agreement rate cannot be read.
CONTROLS = {
    "词表外残差": "每家 new_components 的条数与占全部观察的比例。词表覆盖不了的部分越大，"
                  "词表越该扩",
    "无词表对照": "三家里取一家，同一批页再跑一次、prompt 不给词表；程序把自由名字映回词表，"
                  "与有词表那次比重合率。重合率低说明这份枚举在造一致，一致率要按此折价",
    "自身重跑": "三家里取一家，同一批页原样再跑一次（换缓存键，不换 prompt）。同一家两次的"
                "一致率就是本底噪声——跨家的分歧要减掉它才是真的分歧。实测同一页同一模型两次"
                "跑出的 hardest_step 与 marks 都会变，所以这条不是可选项",
}
