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
    2  page        what one page analysis returns
    3  failure     what one failure attribution returns
    4  report      which sections a report has, and who computed each number
    5  compare     how three models' answers are put side by side

Two rules from `parsebench/TODO.md` §T0 are built into the fields rather than
left to a renderer. Every observation a model proposes carries `affects` -- which
of the four judgement steps it can change, empty meaning the metric never looks
at it. Every suggestion answers two questions that are not on one scale, in two
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
    "radar", "treemap", "gauge", "other",
)

#: How widely a construction is used, as the model reads it off this one page.
#: The program computes the same thing independently, from how many distinct
#: documents a component appears in, so the two can be compared.
GENERALITY = {
    "general": "most published charts of this kind do it, whoever drew them",
    "common": "a whole class of publisher does it, not all of them",
    "house_style": "this document's own convention",
}

#: The seven pipeline changes a suggestion can be filed under, kept in sync with
#: `parsebench/review/04_pipeline_gap.md`. `new` is for what none of them covers;
#: it is the field that keeps the review list open rather than closed.
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
    "new": "none of the seven covers it",
}


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
                   "the metric never looks at it -- that is a normal answer, not a "
                   "missing one",
}

#: The caption, split into the five things a generator would have to produce.
_HEADING = {
    "type": "object",
    "additionalProperties": False,
    "required": ["figure_number", "title", "subtitle", "unit_text", "placement"],
    "properties": {
        "figure_number": {"type": "string",
                          "description": "`Figure 15`, `Exhibit 3`, `Chart 2.1` as printed; "
                                         "empty string when the figure is unnumbered"},
        "title": {"type": "string",
                  "description": "the main title line, verbatim, without the number"},
        "subtitle": {"type": "string",
                     "description": "further heading lines under the title, verbatim; "
                                    "empty when the heading is one line"},
        "unit_text": {"type": "string",
                      "description": "the phrase that fixes the scale of the numbers, "
                                     "wherever it sits -- `USD billion (2022 prices)`, "
                                     "`% of GDP`, `2011 = 100`; empty when there is none"},
        "placement": {"type": "string",
                      "enum": ["above", "beside", "below", "inside", "none"],
                      "description": "where the heading block sits relative to the plot "
                                     "area. `beside` means a side column level with the "
                                     "plot, not stacked over it"},
    },
}

_FIGURE = {
    "type": "object",
    "additionalProperties": False,
    "required": ["id", "heading", "type", "type_other", "orientation", "panels",
                 "panel_names", "series", "series_names", "categories", "category_names",
                 "marks", "values_printed", "value_axis_ticks", "source_line"],
    "properties": {
        "id": {"type": "string", "description": "f1, f2, ... in reading order"},
        "heading": _HEADING,
        "type": {"type": "string", "enum": list(CHART_TYPES)},
        "type_other": {"type": "string",
                       "description": "when type is `other`, name the form in two or three "
                                      "English words (`dumbbell`, `bullet chart`, "
                                      "`population pyramid`); empty otherwise"},
        "orientation": {"type": "string", "enum": ["vertical", "horizontal", "na"]},
        "panels": {"type": "integer", "description": "1 for a single-panel figure"},
        "panel_names": {"type": "array", "items": {"type": "string"},
                        "description": "one per panel, verbatim; empty when panels is 1"},
        "series": {"type": "integer",
                   "description": "distinct legend entries, 1 when there is no legend"},
        "series_names": {"type": "array", "items": {"type": "string"}},
        "categories": {"type": "integer",
                       "description": "distinct slots on the category or time axis, per panel"},
        "category_names": {"type": "array", "items": {"type": "string"},
                           "description": "up to 12 of them, verbatim, in axis order"},
        "marks": {"type": "integer",
                  "description": "individually drawn marks in the whole figure across all "
                                 "panels: bars, stacked segments, points, slices, cells"},
        "values_printed": {"type": "string", "enum": ["all", "some", "none"],
                           "description": "whether the numbers are written on the figure"},
        "value_axis_ticks": {"type": "string",
                             "description": "the value-axis tick labels as printed, comma "
                                            "separated (`0, 25, 50, 75, 100`); empty string "
                                            "when the figure draws no value axis"},
        "source_line": {"type": "string",
                        "description": "the `Source:` line under the figure, verbatim; "
                                       "empty when there is none"},
    },
}

#: One vocabulary key, with the thing on the page that shows it. No `affects`
#: here: the vocabulary already fixes it for these 65 keys, before any page is seen.
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
                                    "show it, quoted, or what is drawn and where. `the "
                                    "y axis reads 0, 25, ... 200 with no unit` is evidence; "
                                    "`the unit is in the title` is a restatement of the key"},
    },
}

PAGE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["page_note", "figures", "components", "new_components", "spot_checks",
                 "hardest_step", "difficulty_notes", "unreadable", "suggestions"],
    "properties": {
        "page_note": {"type": "string",
                      "description": "one sentence in Chinese: what is on this page"},
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
                "required": ["name", "figure_id", "evidence", "affects", "why_it_matters"],
                "properties": {
                    "name": {"type": "string",
                             "description": "a lower_snake_case key you propose, English"},
                    "figure_id": {"type": "string", "description": "the figure, or `page`"},
                    "evidence": {"type": "string",
                                 "description": "English, at most 20 words: what on the page "
                                                "shows it"},
                    "affects": _AFFECTS,
                    "why_it_matters": {"type": "string",
                                       "description": "Chinese, at most 30 words: what it "
                                                      "changes for reading a value out of "
                                                      "this page"},
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
                             "addressing_keys"],
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
                },
            },
        },
        "hardest_step": {"type": "integer", "enum": [1, 2, 3, 4],
                         "description": "the step of the four this page blocks on"},
        "difficulty_notes": {"type": "string",
                             "description": "Chinese, at most 60 words: why that step is the "
                                            "one that blocks. Argue from this page's numbers "
                                            "-- tick spacing against the tolerance, how many "
                                            "keys a value needs -- not in general terms"},
        "unreadable": {
            "type": "array",
            "description": "entries that are not figures at all, or figures nothing can be "
                           "read off",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["figure_id", "reason"],
                "properties": {
                    "figure_id": {"type": "string"},
                    "reason": {"type": "string", "description": "Chinese, at most 20 words"},
                },
            },
        },
        "suggestions": {
            "type": "array",
            "description": "what this page says the generation pipeline should be able to "
                           "do. Two effects, never one: the score and the capability",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["what_to_add", "where_to_change", "affects", "score_effect",
                             "capability_effect", "new_ablation_row", "generality", "maps_to"],
                "properties": {
                    "what_to_add": {"type": "string",
                                    "description": "Chinese: which vocabulary key or new component"},
                    "where_to_change": {"type": "string",
                                        "description": "Chinese: which condition row, style field "
                                                       "or record field"},
                    "affects": _AFFECTS,
                    "score_effect": {"type": "string",
                                     "description": "Chinese, at most 30 words: what it does to "
                                                    "the ParseBench score, argued through the "
                                                    "step named in `affects`. Write `度量看不见它` "
                                                    "when `affects` is empty -- that is an answer, "
                                                    "not a gap"},
                    "capability_effect": {"type": "string",
                                          "description": "Chinese, at most 30 words: what the "
                                                         "generation pipeline can do afterwards "
                                                         "that it cannot do now. A change that "
                                                         "only removes an existing ability does "
                                                         "not belong here -- rewrite it as a "
                                                         "configurable dimension with the "
                                                         "current behaviour as its default"},
                    "new_ablation_row": {"type": "string",
                                         "description": "Chinese: the row this adds to the ablation "
                                                        "table; without one the change only chases "
                                                        "the benchmark"},
                    "generality": {"type": "string", "enum": list(GENERALITY),
                                   "description": "how widely charts outside this document "
                                                  "use the construction"},
                    "maps_to": {"type": "string", "enum": list(GAP_ITEMS)},
                },
            },
        },
    },
}


# --------------------------------------------------------------------------- #
# 3 · One failure attribution                                                   #
# --------------------------------------------------------------------------- #
#
# The division of labour is fixed and does not move: the program says *what*
# happened, the model says *why*. Whether a spot check passed comes from the run's
# own `_evaluation_report.json` and is never re-judged; which form the failure
# took is computed from the parser's output tables; the model is handed both and
# asked only for the mechanism. Mechanisms are a closed list for the same reason
# component keys are, and each names the step of the four it belongs to, so an
# attribution that cannot be mapped back onto the metric cannot be written down.

#: The forms the program computes, from the run output. Given to the model as
#: input, never asked of it. `series_swap` and `stack_confusion` were candidate
#: forms that the last round could not separate from an ordinary misread; they
#: stay out of the form list and come back as mechanisms, where they are a claim
#: about the drawing rather than a count.
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

#: What about the drawing produced that form, and which step of the judgement it
#: belongs to. This is the one field the model decides.
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

FAILURE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["case_id", "mechanism", "mechanism_note", "evidence", "affects",
                 "drawn_differently", "maps_to", "confidence"],
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
        "affects": {"type": "array", "items": {"type": "integer", "enum": [1, 2, 3, 4]},
                    "description": "the judgement step this failure belongs to, normally "
                                   "the one the mechanism names"},
        "drawn_differently": {"type": "string",
                              "description": "Chinese, at most 30 words: what a generator "
                                             "would have to record or draw for this failure "
                                             "not to be possible. A capability, not a fix "
                                             "to this one page"},
        "maps_to": {"type": "string", "enum": list(GAP_ITEMS)},
        "confidence": {"type": "string", "enum": ["certain", "likely", "guess"],
                       "description": "`certain` only when the evidence shows the mechanism "
                                      "rather than being consistent with it"},
    },
}

#: The step each mechanism belongs to, for the check that an attribution maps back
#: onto the metric. `other` maps to no step and must carry a note.
MECHANISM_STEP = {key: step for key, (step, _) in MECHANISMS.items()}

assert set(MECHANISM_STEP.values()) <= set(STEPS) | {0}


# --------------------------------------------------------------------------- #
# 4 · The three reports                                                         #
# --------------------------------------------------------------------------- #
#
# Three summary reports and one file per sampled page. The page file is where the
# three answers sit side by side against the same image, so it is where a conflict
# is adjudicated and where a row in the summary can be checked back to what was
# actually on the page. Twenty pages, twenty files.
#
# The failure analysis has no per-case file, and the asymmetry is a matter of
# scale rather than of principle: a run holds some 900 failures, so a case is a
# row with its evidence in the report, and the conflicting ones are listed
# together in the adjudication table.
#
# The raw answers stay on disk as JSON, machine-readable, one file per
# (model, page); every table below is computed from them.
#
# Three hands touch a report, and the split is what keeps the numbers honest:
# the models write only the raw answers, the program computes every count, rate
# and score into the tables, and the agent writes the prose around those tables,
# adjudicates the conflicts and renders the HTML view. `AUTHORSHIP` states it;
# the one rule is that the agent never produces a number of its own.
#
# Every table below says what one row is and which columns it carries, because
# that is what fixes the analysis: three models can only be compared per column.

PROVENANCE = ("rule_checkable", "program_measured", "model_claim")

#: Who writes what. A report is a program-computed table set with prose around it,
#: not a document someone writes while reading JSON.
AUTHORSHIP = {
    "模型": "只产出 `data/analysis/<model>/<page>.json`，此外什么都不写",
    "程序": "全部计数、一致率、判分、失败统计，写成下面每一张表。这些数字进报告时原样引用",
    "agent": "表之外的东西：逐页报告的裁决列与理由 · 三份汇总报告的结论散文 · `view.html`。"
             "**不产生任何数字**——每一句结论都要指回一张程序算出的表或一份逐页报告",
}


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
    """One file that gets written, and what it is for."""

    path: str
    what: str
    sections: tuple[Section, ...]


#: Where the raw answers live: one JSON per (model, page), the schema above.
#: The reports are built from these, never by hand.
RAW_ANSWERS = "parsebench/data/analysis/<model>/<page>.json"

#: One file per sampled page, three models against the same image. `<page>` is the
#: page stem; the rows of `SAMPLE_REPORT` link here, and adjudication happens here.
PAGE_FILE = Report(
    "parsebench/reports/pages/<page>.md",
    "一页一份：三家的答案与同一张图并排，供核对与裁决",
    (
        Section("1", "这一页", "看的是什么", (
            Table("页面", "这一页",
                  ("页名", "文档", "文档级 tags", "抽查点数", "页面图像路径"),
                  "program_measured"),
        )),
        Section("2", "三家怎么读这一页", "同一张图，三份分解", (
            Table("图表分解", "(模型, 图序号)",
                  ("模型", "图序号", "类型", "图元数", "图号", "标题位置", "数值印不印"),
                  "model_claim"),
            Table("组件命中", "一个 key",
                  ("key", "三家各自报没报", "每家的证据原文"), "model_claim"),
            Table("词表外的自拟名字", "一个名字",
                  ("名字", "哪家报的", "affects", "证据原文"), "model_claim"),
        )),
        Section("3", "抽查点", "值给了模型、标签没给，所以这一节是判分", (
            Table("定位键", "一个抽查点",
                  ("值", "规则的真实标签", "三家各自预测的键", "三家各自对错",
                   "这个点在失败运行里过没过"),
                  "rule_checkable"),
        )),
        Section("4", "分歧与裁决", "这一页上三家说法不同的地方", (
            Table("冲突", "一个冲突项",
                  ("量", "三家各自的取值", "人工裁决", "裁决理由"), "model_claim"),
        )),
        Section("5", "原始答案", "报告的每一行都能回到这里", (
            Table("原始答案", "一家模型", ("模型", "JSON 路径"), "program_measured"),
        )),
    ),
)

SAMPLE_REPORT = Report(
    "parsebench/reports/sample.md",
    "20 页 × 三家模型：基准里有、而 storyline 没有定义的东西",
    (
        Section("1", "要改什么", "哪些缺口进改造清单，哪些不进", (
            Table("组件缺口", "一个词表 key",
                  ("key", "三家各自的页数", "一致性", "affects", "文档分布",
                   "我们画不画得出", "归入哪条 P", "对分数", "对能力",
                   "一页实例（链到该页的页报告）与证据原文"),
                  "model_claim"),
            Table("词表外的观察", "一个自拟名字，归并后",
                  ("名字", "哪几家报了", "页数", "affects", "证据原文"),
                  "model_claim"),
            Table("类型缺口", "一个图表类型",
                  ("类型", "三家各自的图数", "一致性", "条件表有没有这一族"),
                  "model_claim"),
        )),
        Section("2", "基准长什么样", "这批页面实际是什么样。描述，没有待办", (
            Table("类型配比", "一个图表类型", ("类型", "三家各自的图数", "一致性"), "model_claim"),
            Table("数值印不印", "all / some / none 三档", ("档", "三家各自的图数"), "model_claim"),
            Table("稠密度", "五档图元数", ("档", "三家各自的图数"), "model_claim"),
            Table("标题", "图号有无 · 位置四值", ("取值", "三家各自的图数"), "model_claim"),
            Table("卡在哪一步", "四步之一",
                  ("步", "三家各自的页数", "同一批页在失败运行里实际卡住的步"),
                  "model_claim"),
        )),
        Section("3", "能不能信", "这些数字是怎么来的", (
            Table("调用口径", "一家模型",
                  ("模型", "effort", "图像 dpi", "调用次数", "输入 / 输出 token", "用时"),
                  "program_measured"),
            Table("定位键预测的判分", "一家模型",
                  ("模型", "落位的值数", "对的数", "命中率"), "rule_checkable"),
            Table("一致率", "一个对齐量",
                  ("量", "三家一致", "两家", "一家", "冲突", "一致率"), "program_measured"),
            Table("词表控制", "一个模型的两次跑法",
                  ("模型", "有词表报出的 key 数", "无词表那次映回词表后重合的 key 数", "重合率"),
                  "program_measured"),
            Table("交叉核对", "一类矛盾", ("矛盾", "三家各自的页数"), "program_measured"),
        )),
    ),
)

FAILURE_REPORT = Report(
    "parsebench/reports/failures.md",
    "一次解析器运行的全部失败：形态由程序算，机制由三家模型归因。一份总报告，"
    "没有逐 case 文件——实例是报告里的一列，指回 case_id 与页名",
    (
        Section("1", "失败长什么样", "失败各是什么形态，失联的键在哪", (
            Table("失败形态", "一种形态", ("形态", "个数", "占失败"), "program_measured"),
            Table("失联键的去向", "一个去向", ("去向", "个数", "占 label_unlinked"),
                  "program_measured"),
        )),
        Section("2", "什么样的图更容易失败", "哪些自变量与通过率相关", (
            Table("单变量", "一个自变量的一档",
                  ("自变量", "档", "通过率", "n", "95% 区间"), "rule_checkable"),
            Table("控制组内的组件差值", "一个组件",
                  ("组件", "页", "文档", "有", "无", "差"), "rule_checkable"),
        )),
        Section("3", "机制", "什么样的画法产生了这种失败", (
            Table("机制", "一个机制",
                  ("机制", "归入哪一步", "三家各自的条数", "一致率", "冲突数",
                   "一个实例（case_id + 页名）", "要加什么能力"), "model_claim"),
        )),
        Section("4", "能不能信", "口径与没有测到的东西", (
            Table("口径", "一条声明",
                  ("声明", "内容"), "program_measured"),
        )),
    ),
)

OVERVIEW_REPORT = Report(
    "parsebench/reports/overview.md",
    "两份报告合并成一份对流水线的总结：要加什么能力，证据来自哪一份",
    (
        Section("1", "要加的能力", "每条改动加了什么，证据是哪一行", (
            Table("能力轴", "一条要加的能力",
                  ("能力", "证据来自哪一份", "可信度层", "对分数", "对能力",
                   "新增的消融行", "归入哪条 P"), "model_claim"),
        )),
        Section("2", "与 P1–P7 的对齐", "扩哪一条、加哪一条新的、删哪一条", (
            Table("P 对齐", "一条 P",
                  ("P", "扩 / 加 / 删", "依据"), "model_claim"),
        )),
        Section("3", "没进清单的", "报了但不做的，以及为什么", (
            Table("不做", "一条被排除的意见",
                  ("意见", "排除理由（只有一家 / 冲突未裁决 / 不加能力）"), "model_claim"),
        )),
    ),
)

#: The illustrated version of the three summaries, written by the agent from the
#: same tables:
#: three panels matching the three reports, each row carrying the page it came
#: from and the model's own evidence line. Self-contained -- readable without
#: opening the markdown.
VIEW = Report(
    "parsebench/reports/view.html",
    "三份汇总报告的图示版，三个分区一一对应；每一项配一页实例与证据原文，自足",
    (
        Section("1", "要改什么", "报告 A §1 的分区", (
            Table("组件缺口卡片", "一个词表 key",
                  ("key", "三家各自的页数", "一致性", "affects", "对分数", "对能力",
                   "实例页图像", "证据原文"), "model_claim"),
        )),
        Section("2", "失败长什么样", "报告 B §1–§3 的分区", (
            Table("失败卡片", "一个机制",
                  ("机制", "归入哪一步", "条数", "一致率", "实例页图像", "证据原文"),
                  "model_claim"),
        )),
        Section("3", "要加的能力", "报告 C §1 的分区", (
            Table("能力卡片", "一条能力",
                  ("能力", "证据来自哪一份", "可信度层", "对分数", "对能力", "新增的消融行"),
                  "model_claim"),
        )),
    ),
)

REPORTS = (PAGE_FILE, SAMPLE_REPORT, FAILURE_REPORT, OVERVIEW_REPORT, VIEW)

#: Numbers a model must never be the source of. Each is computable without a model,
#: and each was a place the last round could have drifted had it not been.
PROGRAM_ONLY = {
    "每个组件出现在几页、几份文档": "对模型回答里的 key 计数，不问模型频次",
    "通过率与 95% 区间": "取自官方 _evaluation_report.json，不重判分",
    "失败形态的计数": "由解析器输出的表算出，模型只归因不计数",
    "规则实际用了几个标签": "chart.jsonl 的 labels 长度",
    "定位键预测的对错": "规则标签与模型预测的双向子串匹配，与基准自己的匹配方式一致",
    "页面文字量": "PDF 文字层实测",
    "三家的一致性与一致率": "对齐后按下面的判据算，不问模型",
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
    Quantity("定位键预测", "(页, 抽查点)",
             "与规则的真实标签逐条判对错，三家各自得一个分——这一项问「谁对」，"
             "不问「谁和谁一致」",
             "rule_checkable", "唯一可核的量，用来校准上面五条的可信度；同时是 P2 的证据"),
)

FAILURE_QUANTITIES = (
    Quantity("失败机制", "case_id", "mechanism 相同；affects 不同记为冲突",
             "model_claim", "失败报告第 3 节，以及 overview 里的能力轴"),
)

#: Dropped on purpose, so the next round does not re-add them by reflex.
NOT_ALIGNED = {
    "改进意见": "由组件命中派生，对齐它等于把同一件事数两遍。三家的意见原样附在报告里给人读",
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
}
